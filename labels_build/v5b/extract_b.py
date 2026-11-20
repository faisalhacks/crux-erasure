"""Part 2 (v5b) quote extraction, decisions.md D62.  Same as labels_build/v5/extract.py (imported: same X1 prompt and
hash, same model gptoss-120b, temperature 0, seed 0 + retry seed 1, same validator: verbatim substrings of two
different participants' opinions; same own bounded container poll with UTF-8 decoding and recorded stop codes).
Model input: question + the round's opinions only.  Replacement: original and R4-N2 slots have no reserve left
(slot left empty and logged); ministral and extra(ministral) slots take the next item of the ministral queue.
Guards: labels\\ listing only: only author_verification.csv may be present (never opened), author_verification_b.csv
must not exist; ESTIMATE ledger row before launch, ACTUAL after; cap $1.5; serve timeout: session wrapped in a
900 s wall limit (the app must serve well inside 15 min).
Usage: C:/Users/intel/miniconda3/python.exe -I extract_b.py [--confirm-launch]
Output: labels_build/v5b/extraction_b.json, extraction_attempts_b.jsonl, container_check_b.json
"""
import argparse
import asyncio
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
V5 = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\v5")
V5B = V5.parent / "v5b"
CAP = 1.5
MAX_S = 900
X1_SHA = "cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2"


def load(name):
    spec = importlib.util.spec_from_file_location("v5_" + name, V5 / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


EX = load("extract")
S = EX.S


def src_id(it):
    return it.get("job_id") or f"r4uid:{it['uid']}"


async def run(a):
    sel = json.loads((V5B / "selection_b.json").read_text(encoding="utf-8"))
    tmpl = EX.X1.read_text(encoding="utf-8")
    assert EX.sha256_file(EX.X1) == X1_SHA
    if EX.sha256_file(EX.DATA) != EX.EXPECT_SHA:
        raise SystemExit("STOP: data hash mismatch")
    every = sel["selected"] + sel["replacement_queue_ministral"]
    rounds = EX.load_rounds({(x["launch_id"], x["round_id"]) for x in every})
    texts = EX.n2_texts()
    ext5 = json.loads((V5 / "extraction.json").read_text(encoding="utf-8"))
    used_l = {x["launch_id"] for x in ext5["items"]}

    def materialise(x):
        rnd = rounds.get((x["launch_id"], x["round_id"]))
        if rnd is None or not rnd["human_only"] or len(rnd["opinions"]) < 2:
            return None
        st = rnd["cands"][x["cand"]] if x["kind"] == "original" else next(iter(texts[x["job_id"]]))
        return dict(x, statement=st, prompt=EX.build_prompt(tmpl, rnd))

    slots = []
    for x in sel["selected"]:
        m = materialise(x)
        assert m is not None, x
        slots.append(dict(slot=x["slot"], item=m, history=[]))
    mq = list(sel["replacement_queue_ministral"])
    taken_l = used_l | {s["item"]["launch_id"] for s in slots if s["item"]["kind"] == "n2"}

    def next_reserve(slot, old):
        if slot == "gen:ministral3-14b" or (slot == "extra" and old.get("generator") == "ministral3-14b"):
            while mq:
                r = mq.pop(0)
                if r["launch_id"] in taken_l:
                    continue
                m = materialise(r)
                if m is not None:
                    taken_l.add(r["launch_id"])
                    return m
        return None

    if not a.confirm_launch:
        print("dry: prompts built for", len(slots), "items; ministral queue", len(mq))
        return
    present = os.listdir(EX.LABELS)
    if "author_verification_b.csv" in present or any(n != "author_verification.csv" for n in present):
        raise SystemExit(f"STOP: labels\\ holds unexpected files {present}")
    ep = S.modal_endpoints()[EX.ALIAS]
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    worst = round(rate * (MAX_S + ep["scaledown_s"] + 15), 3)
    assert worst < CAP, worst
    rc, rows, _ = EX.container_rows()
    if rc != 0:
        raise SystemExit("STOP: modal container list failed before launch")
    baseline = {re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows}
    approved = "packet builder (orchestrator D62, cap $1.5)"
    S.ledger_row(f"V5b verification-packet part 2 extraction {EX.ALIAS} (25 items, <=2 attempts each) ESTIMATE",
                 "labels-v5b-extraction", "H100x1", worst, "", MAX_S, approved,
                 f"ESTIMATE row before launch; worst-case reservation ${worst} ({MAX_S} s session cap + scaledown); "
                 f"expected ~$0.65 (v5 part 1: $0.6543); baseline containers {len(baseline)}")
    llm = S.LLM(pilot="T3-1-v5b-extract", pilot_cap=CAP, timeout_s=600.0, concurrency={"modal": 10})
    attempts, replacements, sess, t0, timed_out = [], [], None, time.time(), False

    async def body():
        async with llm.modal_session(EX.ALIAS, max_seconds=MAX_S) as s:
            pending = list(range(len(slots)))
            while pending:
                todo = pending
                for seed in (0, 1):
                    if not todo:
                        break
                    jobs = [dict(provider="modal", model=EX.ALIAS, messages=[{"role": "user", "content": slots[i]["item"]["prompt"]}],
                                 max_tokens=EX.MAX_TOK, temperature=0.0, seed=seed, extra={}) for i in todo]
                    out = await llm.run_many(jobs, stop_on_budget=True)
                    nxt = []
                    for i, r in zip(todo, out):
                        it = slots[i]["item"]
                        rec = dict(slot_index=i, slot=slots[i]["slot"], src=src_id(it), seed=seed)
                        if isinstance(r, Exception):
                            rec.update(error=str(r)[:300])
                            nxt.append(i)
                        else:
                            v, why = EX.validate(r["text"], rounds[(it["launch_id"], it["round_id"])])
                            rec.update(text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"), valid=v is not None, why=why)
                            if v:
                                slots[i]["result"] = dict(v, attempt_seed=seed)
                            else:
                                nxt.append(i)
                        attempts.append(rec)
                        slots[i]["history"].append({k: rec.get(k) for k in ("seed", "valid", "why", "error")})
                    todo = nxt
                pending = []
                for i in todo:
                    old = slots[i]["item"]
                    new = next_reserve(slots[i]["slot"], old)
                    replacements.append(dict(slot_index=i, slot=slots[i]["slot"], replaced=src_id(old),
                                             by=src_id(new) if new else None, reasons=slots[i]["history"]))
                    if new is None:
                        slots[i]["dropped"] = True
                        continue
                    slots[i] = dict(slot=slots[i]["slot"], item=new, history=[])
                    pending.append(i)
        return dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    try:
        sess = await asyncio.wait_for(body(), timeout=MAX_S - 10)
    except asyncio.TimeoutError:
        timed_out = True
    finally:
        await llm.aclose()
        cc = EX.wait_and_stop(baseline)
        (V5B / "container_check_b.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        with open(V5B / "extraction_attempts_b.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in attempts:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    spent = sess["session_cost_usd"] if sess else round(llm.stats.get("spent_usd", 0.0) or 0.0, 4)
    S.ledger_row(f"V5b verification-packet part 2 extraction {EX.ALIAS} ACTUAL", "labels-v5b-extraction", "H100x1", "",
                 spent, MAX_S, approved,
                 f"ACTUAL list-price session cost; {len(attempts)} calls; wall {round(time.time() - t0, 1)} s; timed_out {timed_out}; "
                 f"cold start {sess['cold_start_s'] if sess else None} s; own containers after: {len(cc['own_final'])}; "
                 f"stops {[(x['id'], x['returncode']) for x in cc['stops']]}")
    if timed_out:
        raise SystemExit("STOP: session did not finish within the wall limit (serve timeout); see container_check_b.json")
    items = []
    for i, s_ in enumerate(slots):
        it = s_["item"]
        items.append(dict(slot_index=i, slot=s_["slot"], source=it["source"], kind=it["kind"], uid=it["uid"],
                          r4_item_id=it["r4_item_id"], job_id=it.get("job_id", ""), launch_id=it["launch_id"],
                          round_id=it["round_id"], cand=it["cand"], generator=it["generator"], cell=it["cell"],
                          question=rounds[(it["launch_id"], it["round_id"])]["question"], statement=it["statement"],
                          result=None if s_.get("dropped") else s_.get("result"), history=s_["history"]))
    summ = dict(utc=EX.utc(), x1_sha256=X1_SHA, alias=EX.ALIAS, n_items=len(items), n_valid=sum(1 for x in items if x["result"]),
                n_replacements=len(replacements), replacements=replacements,
                conflict_found_false=sum(1 for x in items if x["result"] and x["result"]["conflict_found"] is False),
                located_by_search=sum(1 for x in items if x["result"] and x["result"]["located_by"] == "search"),
                calls=len(attempts), truncated=sum(1 for r in attempts if r.get("finish_reason") == "length"),
                session=sess, wall_s=round(time.time() - t0, 1), container_check={k: v for k, v in cc.items() if k != "polls"},
                selection_sha256=EX.sha256_file(V5B / "selection_b.json"), extract_b_py_sha256=EX.sha256_file(Path(__file__)),
                extract_py_sha256=EX.sha256_file(V5 / "extract.py"), data_sha256=EX.EXPECT_SHA)
    (V5B / "extraction_b.json").write_text(json.dumps(dict(summary=summ, items=items), indent=1, ensure_ascii=False),
                                           encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "replacements"}, indent=1, default=str))
    print("replacements:", json.dumps(replacements, default=str)[:3000])


if __name__ == "__main__":
    os.chdir(EX.P)
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-launch", action="store_true")
    asyncio.run(run(ap.parse_args()))
