"""D49e packet fix (decisions.md D49e).  Re-applies the stricter markdown filter (select_items.MD_STRICT) to all six
N2 slots of extraction.json, then redraws the ministral3-14b slot by walking the EXISTING ordered ministral reserve
(selection.json, seed 20261116) to the first item that passes the strict filter, and extracts quotes for that item
only with the same X1 prompt and decoding as extract.py (temperature 0, seed 0, retry seed 1; an item that still
fails is replaced by the next passing reserve item, logged).  Model input: question + the round's opinions only.
Guards: labels\\ empty (listing only); ESTIMATE ledger row before launch, ACTUAL after; cap $1.5; own bounded container
poll (extract.wait_and_stop).  The pre-fix extraction.json is kept as extraction_pre_d49e.json.
Usage:  C:/Users/intel/miniconda3/python.exe -I redraw_d49e.py [--confirm-launch]
"""
import argparse
import asyncio
import importlib.util
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
V5 = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\v5")
CAP = 1.5
MAX_S = 900
SLOT = "gen:ministral3-14b"


def load(name):
    spec = importlib.util.spec_from_file_location("v5_" + name, V5 / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SI = load("select_items")
EX = load("extract")
S = EX.S


async def run(a):
    sel = json.loads((V5 / "selection.json").read_text(encoding="utf-8"))
    ext = json.loads((V5 / "extraction.json").read_text(encoding="utf-8"))
    tmpl = EX.X1.read_text(encoding="utf-8")
    x1_sha = EX.sha256_file(EX.X1)
    assert x1_sha == ext["summary"]["x1_sha256"]
    texts = EX.n2_texts()

    def stmt(it):
        ts = texts[it["job_id"]]
        assert len(ts) == 1
        return next(iter(ts))

    # 1. strict filter on all six N2 slots
    n2_slots = [x for x in ext["items"] if x["kind"] == "n2"]
    check = {x["slot"]: SI.has_markdown_strict(stmt(x)) for x in n2_slots}
    print("strict filter on the 6 N2 slots (True = markdown):", check)
    fail_slots = [s for s, v in check.items() if v]
    assert fail_slots == [SLOT], f"STOP: unexpected strict-filter failures {fail_slots} (D49e expects only the ministral slot)"
    # corrected count
    mrows = [json.loads(l) for l in open(SI.MINI_FILE, encoding="utf-8") if l.strip()]
    n_strict = sum(SI.has_markdown_strict(r["text"]) for r in mrows)
    print("ministral full_ext outputs with markdown (strict):", n_strict, "of", len(mrows))
    # 2. walk the existing ordered ministral reserve
    queue = []
    skipped = 0
    for r in sel["reserve_ministral"]:
        if SI.has_markdown_strict(stmt(r)):
            skipped += 1
            continue
        queue.append(r)
    print("ministral reserve:", len(sel["reserve_ministral"]), "| failing strict:", skipped, "| passing:", len(queue))
    rounds = EX.load_rounds({(r["launch_id"], r["round_id"]) for r in queue[:20]})
    queue = [r for r in queue[:20] if rounds.get((r["launch_id"], r["round_id"]), {}).get("human_only")
             and len(rounds[(r["launch_id"], r["round_id"])]["opinions"]) >= 2]
    first_passing = queue[0]
    print("first passing reserve item:", first_passing["job_id"],
          "(reserve position", sel["reserve_ministral"].index(first_passing) + 1, ")")
    if not a.confirm_launch:
        return
    listing = os.listdir(EX.LABELS)
    if listing:
        raise SystemExit(f"STOP: labels\\ is not empty ({len(listing)} entries)")
    ep = S.modal_endpoints()[EX.ALIAS]
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    worst = round(rate * (MAX_S + ep["scaledown_s"] + 15), 3)
    assert worst < CAP, worst
    rc, rows, _ = EX.container_rows()
    if rc != 0:
        raise SystemExit("STOP: modal container list failed before launch")
    baseline = {re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows}
    S.ledger_row(f"V5 D49e ministral re-extraction {EX.ALIAS} (1 item, <=2 attempts, reserve walk on failure) ESTIMATE",
                 "labels-v5-extraction", "H100x1", worst, "", MAX_S, "packet builder (orchestrator D49e, cap $1.5)",
                 f"ESTIMATE row before launch; worst-case reservation ${worst} ({MAX_S} s session cap + scaledown); "
                 f"expected ~$0.3 (cold start ~100 s + 1-2 calls); baseline containers {len(baseline)}")
    llm = S.LLM(pilot="T3-1-v5-d49e", pilot_cap=CAP, timeout_s=600.0, concurrency={"modal": 2})
    attempts, replacements, result, chosen, sess, t0 = [], [], None, None, None, time.time()
    try:
        async with llm.modal_session(EX.ALIAS, max_seconds=MAX_S) as s:
            for cand in queue:
                rnd = rounds[(cand["launch_id"], cand["round_id"])]
                prompt = EX.build_prompt(tmpl, rnd)
                hist = []
                for seed in (0, 1):
                    out = await llm.run_many([dict(provider="modal", model=EX.ALIAS, messages=[{"role": "user", "content": prompt}],
                                                   max_tokens=EX.MAX_TOK, temperature=0.0, seed=seed, extra={})], stop_on_budget=True)
                    r = out[0]
                    rec = dict(slot=SLOT, src=cand["job_id"], seed=seed, phase="D49e")
                    if isinstance(r, Exception):
                        rec.update(error=str(r)[:300])
                        v = None
                    else:
                        v, why = EX.validate(r["text"], rnd)
                        rec.update(text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"), valid=v is not None, why=why)
                    attempts.append(rec)
                    hist.append({k: rec.get(k) for k in ("seed", "valid", "why", "error")})
                    if v:
                        result, chosen = dict(v, attempt_seed=seed), (cand, hist, rnd)
                        break
                if result:
                    break
                replacements.append(dict(slot=SLOT, replaced=cand["job_id"], reasons=hist))
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    finally:
        await llm.aclose()
        cc = EX.wait_and_stop(baseline)
        (V5 / "container_check_d49e.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        with open(V5 / "extraction_attempts.jsonl", "a", encoding="utf-8", newline="\n") as f:
            for r in attempts:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if sess:
        S.ledger_row(f"V5 D49e ministral re-extraction {EX.ALIAS} ACTUAL", "labels-v5-extraction", "H100x1", "",
                     sess["session_cost_usd"], MAX_S, "packet builder (orchestrator D49e, cap $1.5)",
                     f"ACTUAL list-price session cost; {len(attempts)} calls; wall {round(time.time() - t0, 1)} s; cold start "
                     f"{sess['cold_start_s']} s; own containers after: {len(cc['own_final'])}; stops {[(x['id'], x['returncode']) for x in cc['stops']]}")
    if not result:
        raise SystemExit("STOP: no reserve item yielded a valid extraction")
    cand, hist, rnd = chosen
    shutil.copyfile(V5 / "extraction.json", V5 / "extraction_pre_d49e.json")
    for i, x in enumerate(ext["items"]):
        if x["slot"] == SLOT:
            old = x
            ext["items"][i] = dict(slot_index=x["slot_index"], slot=SLOT, source=cand["source"], kind="n2", uid=None, r4_item_id="",
                                   job_id=cand["job_id"], launch_id=cand["launch_id"], round_id=cand["round_id"], cand=-1,
                                   generator=cand["generator"], cell=cand["cell"], question=rnd["question"], statement=stmt(cand),
                                   result=result, history=hist)
    s_ = ext["summary"]
    s_["replacements"].append(dict(slot=SLOT, replaced=old["job_id"], by=cand["job_id"],
                                   reasons=[{"why": "D49e: statement fails the stricter markdown filter (single-asterisk italics)"}]))
    s_["replacements"].extend(replacements)
    s_["n_replacements"] = len(s_["replacements"])
    s_["conflict_found_false"] = sum(1 for x in ext["items"] if x["result"]["conflict_found"] is False)
    s_["located_by_search"] = sum(1 for x in ext["items"] if x["result"]["located_by"] == "search")
    s_["calls"] += len(attempts)
    s_["d49e"] = dict(utc=EX.utc(), strict_filter=SI.MD_STRICT.pattern, slot_check=check, ministral_strict_markdown=n_strict,
                      ministral_outputs=len(mrows), reserve_position_1based=sel["reserve_ministral"].index(cand) + 1, new_item=cand["job_id"], replaced=old["job_id"], extra_failures=replacements,
                      session=sess, container_check={k: v for k, v in cc.items() if k != "polls"},
                      redraw_py_sha256=EX.sha256_file(Path(__file__)), select_items_py_sha256=EX.sha256_file(V5 / "select_items.py"))
    s_["n_valid"] = sum(1 for x in ext["items"] if x["result"])
    (V5 / "extraction.json").write_text(json.dumps(ext, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps(s_["d49e"], indent=1, default=str))
    print("conflict_found_false now", s_["conflict_found_false"], "| replacements total", s_["n_replacements"])


if __name__ == "__main__":
    os.chdir(EX.P)
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-launch", action="store_true")
    asyncio.run(run(ap.parse_args()))
