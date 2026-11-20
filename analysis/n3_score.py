"""N3 scoring (FR s8; decisions.md D57): label the ITERATION-1 candidates of the eligible non-development rounds with the
frozen scorer v2 (qwen3.8-27b), cap $3.

FR s8 N3: "cruxes stay those derived from the opinions; iteration-1 candidates are labelled with the same prompt".
So NO new extraction is made: each round's cruxes are the stored A2 extraction (analysis/scores/a2_extractions_v2.jsonl,
the scorer-v2 run of record, D32). Labelling uses scorer.py functions UNCHANGED: L1 prompt (verify_prompts), temperature 0,
seed 0 + one retry seed 1 (call_all), parse_labels, erasure(); order check off, as in the A2 `scorer.py all` run.
Rounds with zero cruxes or a failed extraction are not labelled (E undefined), as in A2.

  python -I n3_score.py plan                    # estimate only
  python -I n3_score.py score --confirm-launch  # Modal; ledger ESTIMATE before, ACTUAL after; own containers polled
  python -I n3_score.py assemble                # -> analysis/scores/n3_statements.csv (+ .manifest.json) for n3_draft_vs_revised.py
Reads no ranks, ratings or labels.  Gate tag HIDE_NOT_HUMAN_VALIDATED."""
import asyncio
import csv
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
import scorer as S  # noqa: E402
import common as C  # noqa: E402

ALIAS = "qwen3.8-27b"
CAP = 3.0
OUT_DIR = S.RUNS / "n3"
SC_OUT = OUT_DIR / "scores.jsonl"
TEXTS = OUT_DIR / "iter1_candidates.jsonl"
FINAL = S.SCORES / "n3_statements.csv"
APPROVED = "orchestrator D57 (N3 approved; cap $3; serial after N2 scoring)"


def iter1_candidates():
    """For every FR s2-eligible round of a non-development launch: the iteration-1 candidates (text + id) from the source
    parquet.  Returns {(launch_id, round_id): [(cand_id, text), ...]} (ordered by first appearance)."""
    import pyarrow.parquet as pq
    if C.sha256_file(C.SRC_PARQUET) != C.FROZEN_SRC_SHA:
        sys.exit("source parquet hash mismatch")
    dev = C.dev_launch_ids()
    elig = {(g["launch_id"], g["round_id"]) for g in (json.loads(l) for l in open(S.ALL_GROUPS, encoding="utf-8"))
            if g["launch_id"] not in dev}
    df = pq.read_table(C.SRC_PARQUET, columns=["launch_id", "round_id", "iteration_index", "candidates.text",
                                               "candidates.metadata.id"]).to_pandas()
    df = df[df.iteration_index == 1]
    out, conflicts = {}, 0
    for (lid, rid), g in df.groupby(["launch_id", "round_id"], sort=True):
        if (lid, rid) not in elig:
            continue
        seen = {}
        for txts, ids in zip(g["candidates.text"], g["candidates.metadata.id"]):
            if txts is None:
                continue
            for t, i in zip(list(txts), list(ids)):
                if i in seen and seen[i] != t:
                    conflicts += 1
                seen.setdefault(i, t)
        if seen:
            out[(lid, rid)] = list(seen.items())
    return out, conflicts


def build():
    cands, conflicts = iter1_candidates()
    rounds = S.load_rounds(S.ALL_GROUPS, set(cands))
    ex = {}
    for l in open(S.SCORES / "a2_extractions_v2.jsonl", encoding="utf-8"):
        r = json.loads(l)
        ex[(r["launch_id"], r["round_id"])] = r
    ltm = S.load_prompt("L1")
    specs, items = [], []
    for k in sorted(cands):
        x = ex.get(k)
        for j, (cid, txt) in enumerate(cands[k]):
            items.append(dict(launch_id=k[0], round_id=k[1], cand=j, cand_id=cid, extract_ok=bool(x and x["ok"]),
                              n_cruxes=x["n_cruxes"] if x and x["ok"] else None))
            if x and x["ok"] and x["n_cruxes"]:
                specs.append(((k[0], k[1], j), S.build_label_prompt(rounds[k]["question"], x["cruxes"], txt, ltm), S.MAX_TOK_LABEL, x["n_cruxes"]))
    return cands, conflicts, items, specs


def plan_for(specs):
    lt = S.mean(len(s[1]) / S.ASSUME["chars_per_tok"] for s in specs)
    pl = S.estimate(ALIAS, 0, len(specs), 0.0, lt, 1)
    # Timeout fixed at 2,000 s so the worst case fits the $3 cap: the assumption rule's 2x safety gives 2,400 s, while the
    # measured N2 run (ledger 02:16Z: 4,794 calls, billed 694 s) puts ~4,700 label calls well under 1,000 s.
    tail = (pl["worst_case_usd"] / pl["rate_usd_per_s"]) - pl["session_max_seconds"]
    pl["session_max_seconds"] = 2000
    pl["worst_case_usd"] = round(pl["rate_usd_per_s"] * (2000 + tail), 3)
    pl["timeout_note"] = "fixed 2000 s (measured N2 rate); assumption-rule timeout would be 2400 s"
    return pl


async def score(confirm):
    S.verify_prompts()
    if C.check_kind("real") != "HIDE_NOT_HUMAN_VALIDATED":
        sys.exit("unexpected gate tag")
    cands, conflicts, items, specs = build()
    pl = plan_for(specs)
    print(json.dumps({"rounds": len(cands), "statements": len(items), "label_calls": len(specs), "text_id_conflicts": conflicts,
                      **{k: v for k, v in pl.items() if k != "assumptions"}}))
    if pl["worst_case_usd"] > CAP:
        sys.exit(f"REFUSED: worst case ${pl['worst_case_usd']} > cap ${CAP}")
    if not confirm:
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if SC_OUT.exists():
        sys.exit("REFUSED: n3/scores.jsonl exists (no silent re-run)")
    with open(TEXTS, "w", encoding="utf-8", newline="\n") as f:
        for k in sorted(cands):
            f.write(json.dumps(dict(launch_id=k[0], round_id=k[1], candidates=[dict(cand=j, cand_id=c, text=t) for j, (c, t) in enumerate(cands[k])]),
                               ensure_ascii=False) + "\n")
    S.ledger_row(f"scorer N3 iteration-1 labels {ALIAS} v2 ({len(specs)} label calls, {len(cands)} rounds) ESTIMATE", "N3", pl["gpu"],
                 pl["worst_case_usd"], "", pl["session_max_seconds"], APPROVED,
                 f"ESTIMATE row before launch; expected ${pl['expected_usd']}, worst-case reservation ${pl['worst_case_usd']} at timeout "
                 f"{pl['session_max_seconds']} s; cap ${CAP}; cruxes reused from a2_extractions_v2 (no extraction calls); HIDE_NOT_HUMAN_VALIDATED")
    S.BASELINE_IDS.update(re.findall(r"ta-[0-9A-Za-z]+", S.container_check().get("stdout_tail", "") or ""))
    # own harness pilot with the D57 cap ($3): the shared T3-1-core-tier2 pilot ($10) had $7.21 committed (attempt 2 refused)
    llm = S.LLM(pilot="T3-1-N3", pilot_cap=CAP, timeout_s=180.0, concurrency={"modal": 32})
    stats = S.new_stats()
    t0 = time.time()
    sess, lb, err = None, {}, None
    try:
        async with llm.modal_session(ALIAS, max_seconds=pl["session_max_seconds"]) as s:
            lb = await asyncio.wait_for(S.call_all(llm, "modal", ALIAS, specs, S.parse_labels, stats, "label"),
                                        timeout=pl["session_max_seconds"] - 5)
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    except Exception as e:  # noqa: BLE001
        err = repr(e)[:300]
        try:
            sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
        except Exception:  # noqa: BLE001
            pass
    finally:
        await llm.aclose()
        cc = S.container_wait_empty(ALIAS)
        (OUT_DIR / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        print("modal container check:", json.dumps({k: v for k, v in cc.items() if k != "stdout_tail"}), flush=True)
    if not lb:   # nothing was labelled: write no scores file (attempt 2 wrote an all-missing file; moved to failed_attempt2/)
        if sess:
            S.ledger_row(f"scorer N3 iteration-1 labels {ALIAS} v2 ACTUAL (failed)", "N3", pl["gpu"], "", sess["session_cost_usd"],
                         pl["session_max_seconds"], APPROVED, f"ACTUAL list-price; no labels; error {err}")
        sys.exit(f"N3 scoring failed, no labels: {err}")
    recs = []
    for it in items:
        key = (it["launch_id"], it["round_id"], it["cand"])
        rec = dict(it, iteration=1, scorer=ALIAS, labels=None, E=None, label_ok=None)
        if it["extract_ok"] and it["n_cruxes"]:
            r = lb.get(key)
            rec["label_ok"] = bool(r and r["ok"])
            if rec["label_ok"]:
                rec["labels"], rec["E"] = r["parsed"], S.erasure(r["parsed"])
        elif it["extract_ok"]:
            rec["label_ok"] = True
        recs.append(rec)
    S.write_jsonl(SC_OUT, recs)
    summ = dict(mode="n3_iter1_labels", scorer=ALIAS, stats=stats, session=sess, error=err, plan=pl, wall_s=round(time.time() - t0, 1),
                prompt_sha256=S.verify_prompts(), scorer_py_sha256=S.sha256_file(HERE / "scorer.py"),
                extractions_sha256=S.sha256_file(S.SCORES / "a2_extractions_v2.jsonl"),
                decoding=dict(temperature=S.TEMPERATURE, seed=S.SEED, retry_seed=S.RETRY_SEED, max_tokens_label=S.MAX_TOK_LABEL),
                container_check=cc)
    (OUT_DIR / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if sess:
        S.ledger_row(f"scorer N3 iteration-1 labels {ALIAS} v2 ACTUAL", "N3", pl["gpu"], "", sess["session_cost_usd"],
                     pl["session_max_seconds"], APPROVED,
                     f"ACTUAL list-price session cost; {stats['calls']} calls, wall {summ['wall_s']} s, billed {sess['billed_s']} s; "
                     f"label parse failures final {stats.get('parse_fail_final_label')}; own container rows after {cc.get('own_rows_final')}, "
                     f"waited {cc.get('waited_s')} s (stopped by id: {cc.get('stopped_by_id')}); error {err}; HIDE_NOT_HUMAN_VALIDATED")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("plan", "container_check")}, indent=1, default=str))


def assemble():
    it1 = [json.loads(l) for l in open(SC_OUT, encoding="utf-8")]
    keys = {(r["launch_id"], r["round_id"]) for r in it1}
    rows = []
    for l in open(S.SCORES / "a2_scores_v2.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if (r["launch_id"], r["round_id"]) in keys:
            rows.append((r["launch_id"], r["round_id"], f"i0_{r['cand']}", 0, "" if r["E"] is None else r["E"]))
    for r in it1:
        rows.append((r["launch_id"], r["round_id"], f"i1_{r['cand']}", 1, "" if r["E"] is None else r["E"]))
    with open(FINAL, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["launch_id", "round_id", "cand", "iteration", "E"])
        w.writerows(rows)
    man = {"source_parquet_sha256": C.FROZEN_SRC_SHA, "table_sha256": C.sha256_file(FINAL),
           "build_analysis_set_counts": C.FROZEN_COUNTS,
           "note": "N3 statement table: iteration 0 from a2_scores_v2.jsonl, iteration 1 from analysis/scorer_runs/n3/scores.jsonl; "
                   "rounds = eligible rounds of non-development launches with iteration-1 candidates",
           "inputs": {"a2_scores_v2.jsonl": C.sha256_file(S.SCORES / "a2_scores_v2.jsonl"), "n3_scores.jsonl": C.sha256_file(SC_OUT)},
           "counts": {"rounds": len(keys), "statements_iter0": sum(1 for r in rows if r[3] == 0), "statements_iter1": len(it1),
                      "iter1_with_E": sum(1 for r in it1 if r["E"] is not None)}}
    Path(str(FINAL) + ".manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    import run_log
    run_log.log_run(__file__, "real (scorer output only)", "n/a", [S.SCORES / "a2_scores_v2.jsonl", SC_OUT], str(FINAL),
                    f"[HIDE_NOT_HUMAN_VALIDATED] N3 statement table {man['counts']}")
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "plan":
        asyncio.run(score(False))
    elif mode == "score":
        asyncio.run(score("--confirm-launch" in sys.argv))
    elif mode == "assemble":
        assemble()
