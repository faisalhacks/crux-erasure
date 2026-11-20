"""FR 6.R5.4 format-bar items for the LLM annotator panel (supplementary; not human): development launches ONLY.

Builds items "exactly like packet items" (question, quote A, quote B, statement) on development-launch rounds:
- dev round keys from pilots/T3_1/pilot_groups.jsonl (scorer.load_rounds: `raters` dropped; only the keys are used);
- round text loaded with labels_build/v5/extract.py load_rounds (same parquet, same column whitelist, same opinion
  order, same human_only rule); eligible = human_only, >= 2 opinions, >= 1 candidate;
- order: sorted keys shuffled with random.Random(20261146); the statement is candidate random.Random(20261146 stream)
  .randrange(n_cands) of the round (an original statement, as the 19 originals of the packet);
- quotes: gpt-oss-120b with prompt X1 (labels_build/v5/X1_prompt.md, sha256 cb25581a...), temperature 0, seed 0, one
  retry seed 1, max_tokens 6000, validated by extract.validate (exact substrings of two different participants);
- the first 20 valid items in draw order are the format-bar items. Items invalid after seed 1 are dropped (counted).
No packet item, no labels\\ access, no score, rank or rating. Ledger ESTIMATE before launch, ACTUAL after; bounded
poll of this app's own containers only (stdin closed, UTF-8 decoding).
Usage (from P): C:/Users/intel/miniconda3/python.exe -I analysis/panel_dev_items.py [--confirm-launch]
Output: analysis/panel/dev_items.json, analysis/panel/dev_extraction_attempts.jsonl, analysis/panel/dev_container_check.json
"""
import argparse
import asyncio
import importlib.util
import json
import random
import re
import sys
import time
from pathlib import Path

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
OUT = P / "analysis" / "panel"
spec = importlib.util.spec_from_file_location("v5_extract", P / "labels_build" / "v5" / "extract.py")
X = importlib.util.module_from_spec(spec)
spec.loader.exec_module(X)          # sets MODAL_ENDPOINTS, imports scorer as X.S; defines nothing that runs
S = X.S

SEED = 20261146
N_DRAW = 24
N_BAR = 20
MAX_S = 600
PILOT, PILOT_CAP = "T3-1-panel-P1", 5.0


async def run(a):
    tmpl = X.X1.read_text(encoding="utf-8")
    assert X.sha256_file(X.X1) == "cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2"
    if X.sha256_file(X.DATA) != X.EXPECT_SHA:
        raise SystemExit("STOP: data hash mismatch")
    dev_keys = sorted(S.load_rounds(S.DEV_GROUPS))
    rounds = X.load_rounds(set(dev_keys))
    rng = random.Random(SEED)
    ks = list(dev_keys)
    rng.shuffle(ks)
    items = []
    for k in ks:
        r = rounds.get(k)
        if r is None or not r["human_only"] or len(r["opinions"]) < 2 or not r["cands"]:
            continue
        c = rng.randrange(len(r["cands"]))
        items.append(dict(draw_index=len(items), launch_id=k[0], round_id=k[1], cand=c, question=r["question"],
                          statement=r["cands"][c], prompt=X.build_prompt(tmpl, r)))
        if len(items) == N_DRAW:
            break
    print("dev keys", len(dev_keys), "loaded", len(rounds), "drawn", len(items))
    if not a.confirm_launch:
        print("dry run; no launch")
        return
    ep = S.modal_endpoints()[X.ALIAS]
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    worst = round(rate * (MAX_S + ep["scaledown_s"] + 15), 3)
    rc, rows, _ = X.container_rows()
    if rc != 0:
        raise SystemExit("STOP: modal container list failed before launch")
    baseline = {re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows}
    S.ledger_row(f"LLM annotator panel (supplementary; not human) P1 format-bar dev items: quote extraction {X.ALIAS} "
                 f"({len(items)} dev rounds, <=2 attempts) ESTIMATE", "r5-panel-p1", "H100x1", worst, "", MAX_S,
                 "panel runner (FR 6.R5.4; total cap $5)",
                 f"ESTIMATE row before launch; worst-case ${worst} ({MAX_S} s session cap + scaledown); dev launches only; "
                 f"baseline containers {len(baseline)}")
    llm = S.LLM(pilot=PILOT, pilot_cap=PILOT_CAP, timeout_s=600.0, concurrency={"modal": 12})
    log, res, sess, t0 = [], {}, None, time.time()
    try:
        async with llm.modal_session(X.ALIAS, max_seconds=MAX_S) as s:
            todo = list(range(len(items)))
            for seed in (0, 1):
                if not todo:
                    break
                jobs = [dict(provider="modal", model=X.ALIAS, messages=[{"role": "user", "content": items[i]["prompt"]}],
                             max_tokens=X.MAX_TOK, temperature=0.0, seed=seed, extra={}) for i in todo]
                out = await llm.run_many(jobs, stop_on_budget=True)
                nxt = []
                for i, r in zip(todo, out):
                    rec = dict(draw_index=i, seed=seed)
                    if isinstance(r, Exception):
                        rec.update(error=str(r)[:300])
                        nxt.append(i)
                    else:
                        v, why = X.validate(r["text"], rounds[(items[i]["launch_id"], items[i]["round_id"])])
                        rec.update(text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"),
                                   valid=v is not None, why=why)
                        if v:
                            res[i] = dict(v, attempt_seed=seed)
                        else:
                            nxt.append(i)
                    log.append(rec)
                todo = nxt
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    finally:
        await llm.aclose()
        cc = X.wait_and_stop(baseline)
        (OUT / "dev_container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        with open(OUT / "dev_extraction_attempts.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in log:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    valid = [dict({k: v for k, v in items[i].items() if k != "prompt"}, quote_a=res[i]["quote_a"], quote_b=res[i]["quote_b"],
                  extraction=res[i]) for i in range(len(items)) if i in res]
    bar = valid[:N_BAR]
    summ = dict(utc=S.utc(), seed=SEED, n_drawn=len(items), n_valid=len(valid), n_invalid_dropped=len(items) - len(valid),
                n_bar_items=len(bar), calls=len(log), truncated=sum(1 for r in log if r.get("finish_reason") == "length"),
                conflict_found_false=sum(1 for x in bar if x["extraction"]["conflict_found"] is False),
                session=sess, wall_s=round(time.time() - t0, 1), container_check={k: v for k, v in cc.items() if k != "polls"},
                x1_sha256=X.sha256_file(X.X1), script_sha256=X.sha256_file(Path(__file__)), data_sha256=X.EXPECT_SHA,
                dev_groups_sha256=X.sha256_file(S.DEV_GROUPS))
    (OUT / "dev_items.json").write_text(json.dumps(dict(summary=summ, items=bar), indent=1, ensure_ascii=False),
                                        encoding="utf-8", newline="\n")
    if sess:
        S.ledger_row(f"LLM annotator panel (supplementary; not human) P1 format-bar dev items: quote extraction {X.ALIAS} ACTUAL",
                     "r5-panel-p1", "H100x1", "", sess["session_cost_usd"], MAX_S, "panel runner (FR 6.R5.4; total cap $5)",
                     f"ACTUAL list-price session cost; {len(log)} calls; wall {summ['wall_s']} s; cold start {sess['cold_start_s']} s; "
                     f"own containers after: {len(cc['own_final'])}; stops {[(x['id'], x['returncode']) for x in cc['stops']]}")
    print(json.dumps(summ, indent=1, default=str))
    if len(bar) < N_BAR:
        raise SystemExit(f"STOP: only {len(bar)} valid dev items (< {N_BAR})")


if __name__ == "__main__":
    import os
    os.chdir(P)
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-launch", action="store_true")
    asyncio.run(run(ap.parse_args()))
