"""N2 scoring with the frozen scorer v2 (qwen3.8-27b) through the sanctioned path (decisions.md D56).

Every mode first calls n2_grid.assert_scoring_allowed() (GATE1_PASSED.json, R5 status + scorer-manifest hash).
Scoring uses scorer.py functions UNCHANGED (E1/L1 prompts, temperature 0, seed 0 + one retry seed 1, parsers,
score_statements with order_check off, as the A2 `scorer.py all` run, D32). The statement is scored EXACTLY AS STORED in
the gens file (spec Amendment 3: nothing stripped). E1 sees question + opinions only.

Inputs : analysis/n2_runs/full_k1/gens_{qwen3.8-27b,gemma4-12b}.jsonl, full_ext/gens_{ministral3-14b,phi4-14b,llama3.1-8b}.jsonl
Outputs: analysis/scorer_runs/n2/{scores,extractions}.jsonl (chunked appends, resume from file + harness cache), summary.json,
         container_check.json; analysis/scores/n2_scores_v2.jsonl (+ .sha256) when complete.
Status : EXPLORATORY (FROZEN_RULES 6.R5.7), gate tag HIDE_NOT_HUMAN_VALIDATED.

  python -I n2_score.py plan                     # estimate only, no model call
  python -I n2_score.py mock [--n-rounds 6]      # $0 harness MOCK provider, temp cache/ledger
  python -I n2_score.py score --confirm-launch   # Modal; ESTIMATE ledger row before, ACTUAL after; cap from approval file
"""
import asyncio
import hashlib
import json
import random
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
import n2_grid as G  # noqa: E402  (sets MODAL_ENDPOINTS to the vendored copy; its qwen3.8-27b entry is identical)
import scorer as S   # noqa: E402

ALIAS = "qwen3.8-27b"
APPROVAL = HERE / "council" / "N2_SCORING_APPROVAL.json"
GENS = {
    "qwen3.8-27b": HERE / "n2_runs" / "full_k1" / "gens_qwen3.8-27b.jsonl",
    "gemma4-12b": HERE / "n2_runs" / "full_k1" / "gens_gemma4-12b.jsonl",
    "ministral3-14b": HERE / "n2_runs" / "full_ext" / "gens_ministral3-14b.jsonl",
    "phi4-14b": HERE / "n2_runs" / "full_ext" / "gens_phi4-14b.jsonl",
    "llama3.1-8b": HERE / "n2_runs" / "full_ext" / "gens_llama3.1-8b.jsonl",
}
OUT_DIR = S.RUNS / "n2"
FINAL = S.SCORES / "n2_scores_v2.jsonl"
CHUNK_ROUNDS = 50                # 5 chunks of whole rounds (~1,250 statements each); one append per chunk
SESSION_MAX_S = 2400             # measured A2 rate: 7,840 statements + 1,960 rounds in 1,695 s wall
TAG = "EXPLORATORY; HIDE_NOT_HUMAN_VALIDATED"


def load_gens():
    rows = []
    for gen, p in GENS.items():
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            assert r["model"] == gen, (p, r["model"])
            rows.append(r)
    ids = [r["job_id"] for r in rows]
    assert len(ids) == len(set(ids)) == 6250, (len(ids), len(set(ids)))
    return rows


def build(rows):
    keys = {(r["launch_id"], r["round_id"]) for r in rows}
    base = S.load_rounds(S.ALL_GROUPS, keys)
    assert len(base) == 250 == len(keys), len(base)
    rounds = {}
    for k, g in base.items():
        g = dict(g)
        g["candidates"] = {}          # the HM candidates are not scored here; only N2 text keyed by job_id
        rounds[k] = g
    for r in rows:
        rounds[(r["launch_id"], r["round_id"])]["candidates"][r["job_id"]] = r["text"]   # exactly as stored
    ls = sorted({k[0] for k in rounds})
    random.Random(S.RANDOM_PREFIX_SEED).shuffle(ls)        # same random-prefix rule as A2: any partial run is a random launch subset
    rank = {l: i for i, l in enumerate(ls)}
    meta = {r["job_id"]: r for r in rows}
    items = [dict(launch_id=k[0], round_id=k[1], cand=j) for k in sorted(rounds, key=lambda k: (rank[k[0]], k[1]))
             for j in sorted(rounds[k]["candidates"])]
    return rounds, items, meta


def plan_for(rounds, items):
    etm, ltm = S.load_prompt("E1"), S.load_prompt("L1")
    c = S.ASSUME["chars_per_tok"]
    et = S.mean(len(S.build_extract_prompt(dict(question=g["question"], opinions=g["opinions"]), etm)) / c for g in rounds.values())
    fake = [dict(issue="x" * 80, side_a="y" * 120, side_b="z" * 120)] * 3
    lt = S.mean(len(S.build_label_prompt(rounds[(i["launch_id"], i["round_id"])]["question"], fake,
                                         rounds[(i["launch_id"], i["round_id"])]["candidates"][i["cand"]], ltm)) / c
                for i in items)
    n_chunks = -(-len(rounds) // CHUNK_ROUNDS)
    pl = S.estimate(ALIAS, len(rounds), len(items), et, lt, 2 * n_chunks)
    ep = G.modal_endpoints()[ALIAS]
    rate = pl["rate_usd_per_s"]
    tail = float(ep["scaledown_s"]) + 15.0
    wall_meas = 106.0 + 0.89 * len(rounds) + 0.14 * len(items) * 0.85      # scorer.make_plans measured rule (A2 all_measured)
    pl.update(session_max_seconds=SESSION_MAX_S, worst_case_usd=round(rate * (SESSION_MAX_S + tail), 3),
              expected_wall_s_measured_rule=round(wall_meas), expected_usd_measured_rule=round(rate * (wall_meas + tail), 3),
              note="timeout fixed at %d s; worst case = rate x (timeout + scaledown tail); extraction calls may be harness-cache hits "
                   "from A2 (same E1 prompt, same seed) at $0" % SESSION_MAX_S)
    return pl


def annotate(recs, meta):
    for r in recs:
        m = meta[r["cand"]]
        r.update(job_id=r["cand"], generator=m["model"], sys_prompt=m["sys_prompt"], user_prompt=m["user_prompt"],
                 cell=f"{m['sys_prompt']}-{m['user_prompt']}", question_id=m["question_id"], msg_sha256=m["msg_sha256"],
                 n_words=m["n_words"], truncated=m["truncated"], scorer_version="v2", section="n2", stamp=TAG)
    return recs


async def run(mode, args):
    gate = G.assert_scoring_allowed()                       # the sanctioned path: refuses without a recorded gate
    rows = load_gens()
    rounds, items, meta = build(rows)
    S.verify_prompts()
    pl = plan_for(rounds, items)
    print("gate:", gate.get("rules"), gate.get("status"))
    print("plan:", json.dumps({k: v for k, v in pl.items() if k != "assumptions"}))
    if mode == "plan":
        return
    if mode == "mock":
        n = args.get("n_rounds", 6)
        keep = list(dict.fromkeys((i["launch_id"], i["round_id"]) for i in items))[:n]
        items = [i for i in items if (i["launch_id"], i["round_id"]) in set(keep)]
        out_dir = OUT_DIR.parent / "n2_mock"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        S.install_mock_responses()
        S.MOCK.latency_s = 0.002
        llm = S.LLM(pilot="scorer-mock", pilot_cap=1.0, ledger_path=out_dir / "mock_ledger.jsonl", cache_dir=out_dir / "mock_cache",
                    concurrency={"mock": 32})
        provider = "mock"
    else:
        if not args.get("confirm"):
            raise SystemExit("REFUSED: needs --confirm-launch")
        a = json.loads(APPROVAL.read_text(encoding="utf-8"))
        if not (a.get("approved") is True and a.get("approved_by") and float(a.get("max_usd", 0)) >= pl["worst_case_usd"]):
            raise SystemExit(f"REFUSED: approval file does not cover worst case ${pl['worst_case_usd']}")
        out_dir = OUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        approved = "N2 council + D56 (analysis/council/N2_SCORING_APPROVAL.json, max $%.2f)" % float(a["max_usd"])
        S.ledger_row(f"scorer N2 {ALIAS} v2 ({len(items)} statements, {len(rounds)} rounds; {pl['calls']} calls est.) ESTIMATE", "N2",
                     pl["gpu"], pl["worst_case_usd"], "", SESSION_MAX_S, approved,
                     f"ESTIMATE row before launch; expected ${pl['expected_usd_measured_rule']} (A2-measured rule; assumption-rule "
                     f"${pl['expected_usd']}), worst-case reservation ${pl['worst_case_usd']} at timeout {SESSION_MAX_S} s; cap ${a['max_usd']}; {TAG}")
        S.BASELINE_IDS.update(re.findall(r"ta-[0-9A-Za-z]+", S.container_check().get("stdout_tail", "") or ""))
        llm = S.LLM(pilot="N2", pilot_cap=G.N2_CAP, timeout_s=180.0, concurrency={"modal": 32})
        provider = "modal"
    sp, ep_ = out_dir / "scores.jsonl", out_dir / "extractions.jsonl"
    done = S.read_done(sp)
    todo = [i for i in items if (i["launch_id"], i["round_id"], i["cand"]) not in done]
    chunks = S.chunk_by_round(todo, CHUNK_ROUNDS)
    stats = S.new_stats()
    stats.update(chunks_total=len(chunks), chunks_done=0, resumed_statements=len(done))
    t0 = time.time()
    sess, cc = None, {}

    async def run_chunks(deadline):
        for ch in chunks:
            left = deadline - time.time()
            if left <= 0:
                stats["stopped"] = "timeout before chunk"
                return
            cs = S.new_stats()
            try:
                recs, ext = await asyncio.wait_for(S.score_statements(llm, provider, ALIAS, rounds, ch, False, cs), timeout=left)
            except asyncio.TimeoutError:
                stats["stopped"] = "timeout inside chunk (calls stay in the harness cache; resume rebuilds it)"
                return
            S.append_jsonl(sp, annotate(recs, meta))
            S.append_jsonl(ep_, ext)
            for k, v in cs.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    stats[k] = stats.get(k, 0) + v
                elif k == "stopped":
                    stats["stopped"] = v
            stats["chunks_done"] += 1
            print(f"chunk {stats['chunks_done']}/{len(chunks)} written ({len(recs)} statements), {round(time.time() - t0)} s", flush=True)
            if cs.get("stopped"):
                return
    try:
        if chunks and provider == "modal":
            async with llm.modal_session(ALIAS, max_seconds=SESSION_MAX_S) as s:
                await run_chunks(time.time() + SESSION_MAX_S - 5)
            sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
        elif chunks:
            await run_chunks(time.time() + 3600)
    finally:
        hs = dict(llm.stats)
        await llm.aclose()
        if provider == "modal" and chunks:
            cc = S.container_wait_empty(ALIAS)
            (out_dir / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
            print("modal container check:", json.dumps({k: v for k, v in cc.items() if k != "stdout_tail"}), flush=True)
    recs = list(S.read_done(sp).values())
    want = {(i["launch_id"], i["round_id"], i["cand"]) for i in items}
    summ = S.summarise(recs, stats)
    per_gen = {}
    for g in GENS:
        rg = [r for r in recs if r.get("generator") == g]
        per_gen[g] = dict(n=len(rg), extract_fail=sum(1 for r in rg if not r["extract_ok"]),
                          zero_crux=sum(1 for r in rg if r["n_cruxes"] == 0),
                          label_parse_fail=sum(1 for r in rg if r["extract_ok"] and r["n_cruxes"] and not r["label_ok"]),
                          with_E=sum(1 for r in rg if r["E"] is not None))
    summ.update(mode=mode, scorer=ALIAS, stamp=TAG, gate=dict(rules=gate.get("rules"), status=gate.get("status")),
                wall_s=round(time.time() - t0, 1), session=sess, plan=pl, harness_stats=hs, per_generator=per_gen,
                empty_side_cruxes_dropped_this_process=S.EMPTY_SIDE_DROPPED["n"], prompt_sha256=S.verify_prompts(),
                scorer_py_sha256=S.sha256_file(HERE / "scorer.py"), n2_grid_sha256=S.sha256_file(HERE / "n2_grid.py"),
                n2_score_sha256=S.sha256_file(Path(__file__)), scorer_manifest_sha256=S.sha256_file(G.SCORER_MANIFEST),
                gens_sha256={g: S.sha256_file(p) for g, p in GENS.items()},
                decoding=dict(temperature=S.TEMPERATURE, seed=S.SEED, retry_seed=S.RETRY_SEED,
                              max_tokens=dict(extract=S.MAX_TOK_EXTRACT, label=S.MAX_TOK_LABEL), response_format="json_object",
                              thinking="off"), order_check=False, container_check=cc, n_requested=len(items),
                complete=want <= set(S.read_done(sp)))
    (out_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if provider == "modal":
        if sess:
            S.ledger_row(f"scorer N2 {ALIAS} v2 ACTUAL", "N2", pl["gpu"], "", sess["session_cost_usd"], SESSION_MAX_S, approved,
                         f"ACTUAL list-price session cost; {stats['calls']} calls ({hs.get('cache_hits')} harness-cache hits), wall {summ['wall_s']} s, "
                         f"billed {sess['billed_s']} s, cold {sess['cold_start_s']} s; own container rows after {cc.get('own_rows_final')}, "
                         f"waited {cc.get('waited_s')} s (stopped by id: {cc.get('stopped_by_id')}); {TAG}")
        if summ["complete"]:
            S.SCORES.mkdir(exist_ok=True)
            ordered = sorted((r for r in recs if (r["launch_id"], r["round_id"], r["cand"]) in want), key=lambda r: r["job_id"])
            S.write_jsonl(FINAL, ordered)
            h = S.sha256_file(FINAL)
            Path(str(FINAL) + ".sha256").write_text(f"{h}  {FINAL.name}\n", encoding="utf-8")
            print("final", FINAL, h)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("plan", "container_check")}, indent=1, default=str))


if __name__ == "__main__":
    m = sys.argv[1]
    assert m in ("plan", "mock", "score"), m
    opts = dict(confirm="--confirm-launch" in sys.argv)
    if "--n-rounds" in sys.argv:
        opts["n_rounds"] = int(sys.argv[sys.argv.index("--n-rounds") + 1])
    asyncio.run(run(m, opts))
