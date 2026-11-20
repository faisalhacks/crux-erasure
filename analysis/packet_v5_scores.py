"""Scorer-1 (v2) outputs for the 25 R5 verification-packet items -> analysis/scores/packet_v5_scores.jsonl.

  score     score the 6 N2 packet items with the frozen scorer v2 (scorer.py functions, unchanged: E1/L1 prompts,
            temperature 0, seed 0 + one retry seed 1, parsers, order check as in gate1 mode). Gate measurement items
            (decisions.md D34 "The 12 N2 packet items are gate measurement items"; D50a OPEN item). No other N2 text.
            Needs --confirm-launch. Ledger ESTIMATE row before launch, ACTUAL row after; own containers polled.
  assemble  originals from v2 scores (gate1_scores.jsonl first, then a2_scores_v2.jsonl; never v1), N2 from the
            score run above -> packet_v5_scores.jsonl (+ .sha256).
Reads: key_verification.csv (item mapping), all_groups.jsonl (question/opinions only, via scorer.load_rounds),
N2 generation files (text of the 6 packet statements only). Reads no labels, ranks or author file.
"""
import asyncio
import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
import scorer as S  # noqa: E402

KEY = P / "labels_build" / "v5" / "key_verification.csv"
OUT_DIR = S.RUNS / "packet_v5_n2"
N2_SCORES = OUT_DIR / "scores.jsonl"
N2_EXT = OUT_DIR / "extractions.jsonl"
OUT = S.SCORES / "packet_v5_scores.jsonl"
GENS = [P / "analysis" / "n2_runs" / d / f for d in ("full_ext", "full_k1") for f in
        ("gens_llama3.1-8b.jsonl", "gens_ministral3-14b.jsonl", "gens_phi4-14b.jsonl", "gens_gemma4-12b.jsonl", "gens_qwen3.8-27b.jsonl")]
ALIAS = "qwen3.8-27b"
CAP = 2.0


def key_rows():
    with open(KEY, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n2_texts(ids):
    out = {}
    for g in GENS:
        if not g.exists():
            continue
        for line in open(g, encoding="utf-8"):
            r = json.loads(line)
            if r.get("job_id") in ids:
                if r["job_id"] in out and out[r["job_id"]][0] != r["text"]:
                    raise SystemExit(f"conflicting texts for {r['job_id']}")
                out[r["job_id"]] = (r["text"], str(g.relative_to(P)), r["launch_id"], r["round_id"])
    return out


async def score(confirm):
    rows = [r for r in key_rows() if r["kind"] == "n2"]
    assert len(rows) == 6, len(rows)
    tx = n2_texts({r["statement_id"] for r in rows})
    miss = [r["statement_id"] for r in rows if r["statement_id"] not in tx]
    if miss:
        raise SystemExit(f"STOP: N2 text not found for {miss}")
    for r in rows:
        t = tx[r["statement_id"]]
        assert (t[2], t[3]) == (r["launch_id"], r["round_id"]), r["item_id"]
    rounds = S.load_rounds(S.ALL_GROUPS, {(r["launch_id"], r["round_id"]) for r in rows})
    # candidates replaced by the packet statement only (keyed by statement_id); E1 sees question + opinions only.
    rr = {}
    for r in rows:
        k = (r["launch_id"], r["round_id"])
        g = dict(rounds[k])
        g["candidates"] = dict(rr.get(k, {}).get("candidates", {}), **{r["statement_id"]: tx[r["statement_id"]][0]})
        rr[k] = g
    items = [dict(launch_id=r["launch_id"], round_id=r["round_id"], cand=r["statement_id"], item_ids=[r["item_id"]]) for r in rows]
    S.verify_prompts()
    ext_tok = S.mean(S.est_tokens(S.build_extract_prompt(dict(question=g["question"], opinions=g["opinions"]), S.load_prompt("E1"))) for g in rr.values())
    plan = S.estimate(ALIAS, len(rr), 2 * len(items), ext_tok, ext_tok, 3)
    print("plan", json.dumps({k: v for k, v in plan.items() if k != "assumptions"}))
    if plan["worst_case_usd"] > CAP:
        raise SystemExit(f"REFUSED: worst case ${plan['worst_case_usd']} > cap ${CAP}")
    if not confirm:
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if N2_SCORES.exists():
        raise SystemExit("REFUSED: packet_v5_n2/scores.jsonl exists (no silent re-run)")
    labels_dir = P / "labels"
    present = [p.name for p in labels_dir.iterdir()] if labels_dir.exists() else []
    if any(n != "author_verification.csv" for n in present):
        raise SystemExit(f"REFUSED: labels/ holds unexpected files {present}")
    approved = "scorer runner (orchestrator brief: 6 N2 packet items = gate measurement items, D34/D50a; cap $2)"
    S.ledger_row(f"scorer packet_v5 N2 items {ALIAS} ({plan['calls']} calls est.)", "R5-step3-scores", plan["gpu"],
                 plan["worst_case_usd"], "", plan["session_max_seconds"], approved,
                 f"ESTIMATE row before launch; expected ${plan['expected_usd']}, worst-case reservation ${plan['worst_case_usd']}; "
                 f"6 N2 packet statements, 6 rounds, order check on (gate1 path); cap ${CAP}")
    S.BASELINE_IDS.update(re.findall(r"ta-[0-9A-Za-z]+", S.container_check().get("stdout_tail", "") or ""))
    llm = S.LLM(pilot="T3-1-core-tier2", pilot_cap=10.0, timeout_s=180.0, concurrency={"modal": 32})
    stats = S.new_stats()
    t0 = time.time()
    sess = None
    try:
        async with llm.modal_session(ALIAS, max_seconds=plan["session_max_seconds"]) as s:
            recs, ext = await asyncio.wait_for(S.score_statements(llm, "modal", ALIAS, rr, items, True, stats),
                                               timeout=plan["session_max_seconds"] - 5)
            for r in recs:
                r["section"] = "packet_v5_n2"
            S.write_jsonl(N2_SCORES, recs)
            S.write_jsonl(N2_EXT, ext)
            print("N2 scores written", N2_SCORES, flush=True)
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    finally:
        await llm.aclose()
        cc = S.container_wait_empty(ALIAS)
        (OUT_DIR / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        print("modal container check:", json.dumps({k: v for k, v in cc.items() if k != "stdout_tail"}), flush=True)
    summ = dict(mode="packet_v5_n2", scorer=ALIAS, stats=stats, session=sess, plan=plan, wall_s=round(time.time() - t0, 1),
                prompt_sha256=S.verify_prompts(), scorer_py_sha256=S.sha256_file(HERE / "scorer.py"),
                decoding=dict(temperature=S.TEMPERATURE, seed=S.SEED, retry_seed=S.RETRY_SEED,
                              max_tokens=dict(extract=S.MAX_TOK_EXTRACT, label=S.MAX_TOK_LABEL)),
                text_sources={r["statement_id"]: tx[r["statement_id"]][1] for r in rows}, container_check=cc)
    (OUT_DIR / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if sess:
        S.ledger_row(f"scorer packet_v5 N2 items {ALIAS} ACTUAL", "R5-step3-scores", plan["gpu"], "", sess["session_cost_usd"],
                     plan["session_max_seconds"], approved,
                     f"ACTUAL list-price session cost; {stats['calls']} calls, wall {summ['wall_s']} s, own container rows after "
                     f"{cc.get('own_rows_final')}, waited {cc.get('waited_s')} s (stopped by id: {cc.get('stopped_by_id')})")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("plan", "container_check")}, indent=1, default=str))


def assemble():
    rows = key_rows()
    g1 = [json.loads(l) for l in open(S.SCORES / "gate1_scores.jsonl", encoding="utf-8") if l.strip()]
    a2 = [json.loads(l) for l in open(S.SCORES / "a2_scores_v2.jsonl", encoding="utf-8") if l.strip()]
    n2 = {r["cand"]: r for r in (json.loads(l) for l in open(N2_SCORES, encoding="utf-8") if l.strip())} if N2_SCORES.exists() else {}
    out, report = [], []
    for k in rows:
        if k["kind"] == "original":
            key = (k["launch_id"], k["round_id"], int(k["cand"]))
            m = [r for r in g1 if (r["launch_id"], r["round_id"], r["cand"]) == key]
            src = "analysis/scores/gate1_scores.jsonl"
            if not m:
                m = [r for r in a2 if (r["launch_id"], r["round_id"], r["cand"]) == key]
                src = "analysis/scores/a2_scores_v2.jsonl"
            if len(m) > 1 and any(json.dumps(x, sort_keys=True) != json.dumps(m[0], sort_keys=True) for x in m):
                raise SystemExit(f"STOP: {len(m)} differing v2 rows for {k['item_id']} in {src}")
            r = m[0] if m else None
            how = "reused_v2" if r else "MISSING"
        else:
            r = n2.get(k["statement_id"])
            src = "analysis/scorer_runs/packet_v5_n2/scores.jsonl"
            how = "new_v2_run" if r else "MISSING"
        if r is None:
            raise SystemExit(f"STOP: no v2 score for {k['item_id']} ({k['kind']})")
        ok = bool(r["extract_ok"]) and (r["n_cruxes"] == 0 or bool(r["label_ok"]))
        out.append(dict(item_id=k["item_id"], kind=k["kind"], E=r["E"], n_cruxes=r["n_cruxes"], ok=ok,
                        statement_id=k["statement_id"], source=src, launch_id=k["launch_id"], round_id=k["round_id"],
                        packet_source=k["source"], scorer=r["scorer"], scorer_version="v2", labels=r["labels"],
                        provenance=how))
        report.append((k["item_id"], k["kind"], how, r["E"], r["n_cruxes"], ok))
    assert len(out) == 25 and len({o["item_id"] for o in out}) == 25
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for o in sorted(out, key=lambda o: o["item_id"]):
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    h = hashlib.sha256(OUT.read_bytes()).hexdigest()
    for x in report:
        print(*x)
    print("rows", len(out), "ok", sum(o["ok"] for o in out), "sha256", h)


if __name__ == "__main__":
    if sys.argv[1] == "score":
        asyncio.run(score("--confirm-launch" in sys.argv))
    elif sys.argv[1] == "assemble":
        assemble()
