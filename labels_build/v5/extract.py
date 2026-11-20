"""V5 step-3 evidence extraction (decisions.md D49b, D49c).  gpt-oss-120b on Modal, prompt X1 (X1_prompt.md).

Input to the model per item: the round's question + the round's participant opinions ONLY (iteration 0, numbered in
sorted participant-id order, as r4_build.py).  Never the statement, scores, ranks or ratings: the parquet is read
with opinion/question/candidate columns only (candidate text is read for the original statement, never sent).
Decoding: temperature 0, seed 0; one retry with seed 1; max_tokens 6000; reasoning at the served default (as the
D41 format smoke).  Validity (checked by code): JSON with quote_a, quote_b (non-empty after stripping outer
whitespace, not equal), conflict_found a bool, and the two quotes exact substrings of two DIFFERENT participants'
opinions (the model's opinion numbers are used if they hold; otherwise any distinct-participant assignment found
by exact search is accepted and recorded as located_by=search).  An item still invalid after seed 1 is replaced
from the ordered reserve (selection.json, rule in select.py) and the replacement is logged.
Guards: labels\\ must be empty (listing only) before launch; ESTIMATE ledger row before launch, ACTUAL after;
own bounded container poll after the session (UTF-8 decoding), stopping only containers of this app that were not
alive before launch, recording each stop's return code.
Usage:  C:/Users/intel/miniconda3/python.exe -I extract.py --confirm-launch
Output: labels_build/v5/extraction.json, extraction_attempts.jsonl, container_check.json
"""
import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pyarrow.parquet as pq

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
V5 = P / "labels_build" / "v5"
LABELS = P / "labels"
DATA = P.parent / "data" / "habermas_gcs" / "hm_all_candidate_comparisons.parquet"
EXPECT_SHA = "7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4"
X1 = V5 / "X1_prompt.md"
GEN_FILES = sorted((P / "analysis" / "n2_runs" / "full_k1").glob("gens_*.jsonl")) + \
            sorted((P / "analysis" / "n2_runs" / "full_ext").glob("gens_*.jsonl"))
sys.path.insert(0, str(P / "analysis"))
os.environ["MODAL_ENDPOINTS"] = str(P / "serving" / "endpoints.json")
import scorer as S  # noqa: E402

ALIAS = "gptoss-120b"
APP_FULL = "pilot-vllm-gptoss-120b"   # matched in the untruncated --json rows
MAX_TOK = 6000
MAX_S = 1200
CAP = 3.0
MODAL_PY = "C:/Users/intel/miniconda3/python.exe"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ------------------------------------------------------------------ data
def load_rounds(keys):
    """(launch_id, round_id) -> question, opinions {pid: text}, cands, human_only. No rank/rating columns."""
    cols = ["launch_id", "round_id", "iteration_index", "own_opinion.text", "own_opinion.metadata.provenance",
            "own_opinion.metadata.participant_id", "other_opinions.metadata.provenance",
            "other_opinions.metadata.participant_id", "other_opinions.text", "critique.metadata.provenance",
            "candidates.text", "question.text"]
    rids = sorted({k[1] for k in keys})
    df = pq.read_table(DATA, columns=cols, filters=[("round_id", "in", rids)]).to_pandas()
    bot_rounds = set(map(tuple, df.loc[df["critique.metadata.provenance"] == "BOT_CITIZEN", ["launch_id", "round_id"]].values))
    out = {}
    for (lid, rid), g in df[df.iteration_index == 0].groupby(["launch_id", "round_id"], sort=True):
        ops, human = {}, (lid, rid) not in bot_rounds
        for _, r in g.iterrows():
            human &= r["own_opinion.metadata.provenance"] == "HUMAN_CITIZEN"
            ops[r["own_opinion.metadata.participant_id"]] = r["own_opinion.text"]
            for pid, pv, t in zip(r["other_opinions.metadata.participant_id"], r["other_opinions.metadata.provenance"],
                                  r["other_opinions.text"]):
                human &= pv == "HUMAN_CITIZEN"
                ops.setdefault(pid, t)
        r0 = g.iloc[0]
        out[(lid, rid)] = dict(question=r0["question.text"], opinions=dict(sorted(ops.items())),
                               cands=list(r0["candidates.text"]), human_only=bool(human))
    return out


def n2_texts():
    t = {}
    for f in GEN_FILES:
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                t.setdefault(d["job_id"], set()).add(d["text"])
    return t


def build_prompt(tmpl, rnd):
    ops = "\n".join(f"{i}. {t}" for i, t in enumerate(rnd["opinions"].values(), 1))
    return tmpl.replace("{question}", rnd["question"]).replace("{numbered_opinions}", ops)


# ------------------------------------------------------------------ validation
def validate(text, rnd):
    js = S.parse_json_obj(text)
    if js is None:
        return None, "no JSON object"
    qa, qb, cf = js.get("quote_a"), js.get("quote_b"), js.get("conflict_found")
    if not isinstance(qa, str) or not isinstance(qb, str) or not qa.strip() or not qb.strip():
        return None, "missing/empty quote"
    if not isinstance(cf, bool):
        return None, "conflict_found not bool"
    qa, qb = qa.strip(), qb.strip()
    if qa == qb:
        return None, "identical quotes"
    pids = list(rnd["opinions"])
    texts = list(rnd["opinions"].values())
    ia = [i for i, t in enumerate(texts) if qa in t]
    ib = [i for i, t in enumerate(texts) if qb in t]
    if not ia or not ib:
        return None, f"not exact substring (a found {bool(ia)}, b found {bool(ib)})"
    na, nb = js.get("opinion_a"), js.get("opinion_b")
    ok_idx = (isinstance(na, int) and isinstance(nb, int) and not isinstance(na, bool) and not isinstance(nb, bool)
              and (na - 1) in ia and (nb - 1) in ib and na != nb)
    if ok_idx:
        a, b, how = na - 1, nb - 1, "model_index"
    else:
        pair = next(((x, y) for x in ia for y in ib if x != y), None)
        if pair is None:
            return None, "quotes only found in the same participant's opinion"
        a, b, how = pair[0], pair[1], "search"
    return dict(quote_a=qa, quote_b=qb, pid_a=pids[a], pid_b=pids[b], opinion_no_a=a + 1, opinion_no_b=b + 1,
                conflict_found=cf, located_by=how), None


# ------------------------------------------------------------------ containers (own bounded poll)
def container_rows():
    """`modal container list --json` (stdin closed: an inherited stdin made the plain list hang in a background
    shell). Each row is serialised to one JSON string so ids/app names are matched untruncated."""
    r = subprocess.run([MODAL_PY, "-I", "-m", "modal", "container", "list", "--json"], capture_output=True,
                       stdin=subprocess.DEVNULL, timeout=120)
    out = (r.stdout or b"").decode("utf-8", errors="replace")
    err = (r.stderr or b"").decode("utf-8", errors="replace")
    try:
        rows = [json.dumps(x, ensure_ascii=False) for x in json.loads(out or "[]")]
    except json.JSONDecodeError:
        return 99, [], ("unparseable list output: " + out[-200:] + err)[-300:]
    rows = [ln for ln in rows if re.search(r"\bta-[0-9A-Za-z]+", ln)]
    return r.returncode, rows, err[-300:]


def own_ids(rows, baseline):
    ids = [re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows if APP_FULL in ln]
    return [i for i in ids if i not in baseline]


def wait_and_stop(baseline, max_wait_s=300, every_s=15):
    t0, polls, stops = time.time(), [], []
    while True:
        rc, rows, err = container_rows()
        mine = own_ids(rows, baseline)
        polls.append(dict(t=round(time.time() - t0), rc=rc, all_rows=len(rows), own=mine, err=err if rc else ""))
        if rc != 0 or not mine or time.time() - t0 >= max_wait_s:
            break
        time.sleep(every_s)
    if rc == 0 and mine:
        for cid in mine:
            r = subprocess.run([MODAL_PY, "-I", "-m", "modal", "container", "stop", "-y", cid], capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=120)
            stops.append(dict(id=cid, returncode=r.returncode,
                              stderr=(r.stderr or b"").decode("utf-8", errors="replace")[-300:]))
        time.sleep(10)
        rc, rows, err = container_rows()
        mine = own_ids(rows, baseline)
        polls.append(dict(t=round(time.time() - t0), rc=rc, all_rows=len(rows), own=mine, err=err if rc else ""))
    return dict(waited_s=round(time.time() - t0), polls=polls, stops=stops, own_final=mine, baseline=sorted(baseline),
                other_rows_final=len(rows) - len(mine))


# ------------------------------------------------------------------ main
async def run(a):
    sel = json.loads((V5 / "selection.json").read_text(encoding="utf-8"))
    tmpl = X1.read_text(encoding="utf-8")
    x1_sha = sha256_file(X1)
    if sha256_file(DATA) != EXPECT_SHA:
        raise SystemExit("STOP: data hash mismatch")
    every = sel["selected"] + sel["reserve_original"] + sel["reserve_n2"] + sel["reserve_ministral"]
    rounds = load_rounds({(x["launch_id"], x["round_id"]) for x in every})
    texts = n2_texts()

    def materialise(x):
        rnd = rounds.get((x["launch_id"], x["round_id"]))
        if rnd is None or not rnd["human_only"] or len(rnd["opinions"]) < 2:
            return None
        if x["kind"] == "original":
            st = rnd["cands"][x["cand"]]
        else:
            ts = texts[x["job_id"]]
            assert len(ts) == 1
            st = next(iter(ts))
        return dict(x, statement=st, prompt=build_prompt(tmpl, rnd))

    slots = []
    for x in sel["selected"]:
        m = materialise(x)
        assert m is not None, ("selected item not loadable", x)
        slots.append(dict(slot=x["slot"], item=m, history=[]))
    reserves = {"original": list(sel["reserve_original"]), "n2": list(sel["reserve_n2"]),
                "ministral": list(sel["reserve_ministral"])}

    def next_reserve(slot):
        if slot == "original":
            q, pred = reserves["original"], (lambda r: True)
        elif slot == "gen:ministral3-14b":
            q, pred = reserves["ministral"], (lambda r: True)
        elif slot.startswith("gen:"):
            g = slot[4:]
            q, pred = reserves["n2"], (lambda r: r["generator"] == g)
        else:
            q, pred = reserves["n2"], (lambda r: True)
        for i, r in enumerate(q):
            if pred(r):
                q.pop(i)
                m = materialise(r)
                if m is not None:
                    return m
                return next_reserve(slot)
        return None

    (V5 / "extract_plan.json").write_text(json.dumps(dict(x1_sha256=x1_sha, alias=ALIAS, max_tokens=MAX_TOK, temperature=0.0,
                                                           seeds=[0, 1], n_items=len(slots), max_s=MAX_S),
                                                      indent=1), encoding="utf-8")
    if not a.confirm_launch:
        print("dry: prompts built for", len(slots), "items; first prompt chars", len(slots[0]["item"]["prompt"]))
        print("x1 sha256", x1_sha)
        return
    # ---- guards before launch
    listing = os.listdir(LABELS)
    if listing:
        raise SystemExit(f"STOP: labels\\ is not empty ({len(listing)} entries)")
    ep = S.modal_endpoints()[ALIAS]
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    worst = round(rate * (MAX_S + ep["scaledown_s"] + 15), 3)
    assert worst < CAP, worst
    rc, rows, _ = container_rows()
    if rc != 0:
        raise SystemExit("STOP: modal container list failed before launch")
    baseline = {re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows}
    S.ledger_row(f"V5 verification-packet extraction {ALIAS} (25 items + reserves, <=2 attempts each) ESTIMATE",
                 "labels-v5-extraction", "H100x1", worst, "", MAX_S, "packet builder (orchestrator D49b/D49c, cap $3)",
                 f"ESTIMATE row before launch; worst-case reservation ${worst} ({MAX_S} s session cap + scaledown); "
                 f"expected ~$0.6 incl. cold start (D41 smoke: $0.49 for 10 items); baseline containers {len(baseline)}")
    llm = S.LLM(pilot="T3-1-v5-extract", pilot_cap=CAP, timeout_s=600.0, concurrency={"modal": 10})
    attempts_log, replacements, sess, t0 = [], [], None, time.time()
    try:
        async with llm.modal_session(ALIAS, max_seconds=MAX_S) as s:
            pending = list(range(len(slots)))
            while pending:
                failed_final = []
                todo = pending
                for seed in (0, 1):
                    if not todo:
                        break
                    jobs = [dict(provider="modal", model=ALIAS, messages=[{"role": "user", "content": slots[i]["item"]["prompt"]}],
                                 max_tokens=MAX_TOK, temperature=0.0, seed=seed, extra={}) for i in todo]
                    out = await llm.run_many(jobs, stop_on_budget=True)
                    nxt = []
                    for i, r in zip(todo, out):
                        it = slots[i]["item"]
                        rec = dict(slot_index=i, slot=slots[i]["slot"], src=it.get("job_id") or f"r4uid:{it['uid']}", seed=seed)
                        if isinstance(r, Exception):
                            rec.update(error=str(r)[:300])
                            nxt.append(i)
                        else:
                            v, why = validate(r["text"], rounds[(it["launch_id"], it["round_id"])])
                            rec.update(text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"),
                                       valid=v is not None, why=why)
                            if v:
                                slots[i]["result"] = dict(v, attempt_seed=seed)
                            else:
                                nxt.append(i)
                        attempts_log.append(rec)
                        slots[i]["history"].append({k: rec.get(k) for k in ("seed", "valid", "why", "error")})
                    todo = nxt
                failed_final = todo
                pending = []
                for i in failed_final:
                    old = slots[i]["item"]
                    new = next_reserve(slots[i]["slot"])
                    replacements.append(dict(slot_index=i, slot=slots[i]["slot"],
                                             replaced=old.get("job_id") or f"r4uid:{old['uid']}",
                                             by=(new.get("job_id") or f"r4uid:{new['uid']}") if new else None,
                                             reasons=slots[i]["history"]))
                    if new is None:
                        continue
                    slots[i] = dict(slot=slots[i]["slot"], item=new, history=[])
                    pending.append(i)
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    finally:
        await llm.aclose()
        cc = wait_and_stop(baseline)
        (V5 / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
        with open(V5 / "extraction_attempts.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in attempts_log:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    items = []
    for i, s_ in enumerate(slots):
        it = s_["item"]
        items.append(dict(slot_index=i, slot=s_["slot"], source=it["source"], kind=it["kind"], uid=it["uid"],
                          r4_item_id=it["r4_item_id"], job_id=it.get("job_id", ""), launch_id=it["launch_id"],
                          round_id=it["round_id"], cand=it["cand"], generator=it["generator"], cell=it["cell"],
                          question=rounds[(it["launch_id"], it["round_id"])]["question"], statement=it["statement"],
                          result=s_.get("result"), history=s_["history"]))
    summ = dict(utc=utc(), x1_sha256=x1_sha, alias=ALIAS, n_items=len(items), n_valid=sum(1 for x in items if x["result"]),
                n_replacements=len(replacements), replacements=replacements,
                conflict_found_false=sum(1 for x in items if x["result"] and x["result"]["conflict_found"] is False),
                located_by_search=sum(1 for x in items if x["result"] and x["result"]["located_by"] == "search"),
                calls=len(attempts_log), truncated=sum(1 for r in attempts_log if r.get("finish_reason") == "length"),
                session=sess, wall_s=round(time.time() - t0, 1),
                container_check={k: v for k, v in cc.items() if k != "polls"},
                selection_sha256=sha256_file(V5 / "selection.json"), extract_py_sha256=sha256_file(Path(__file__)),
                data_sha256=EXPECT_SHA)
    (V5 / "extraction.json").write_text(json.dumps(dict(summary=summ, items=items), indent=1, ensure_ascii=False),
                                        encoding="utf-8", newline="\n")
    if sess:
        S.ledger_row(f"V5 verification-packet extraction {ALIAS} ACTUAL", "labels-v5-extraction", "H100x1", "",
                     sess["session_cost_usd"], MAX_S, "packet builder (orchestrator D49b/D49c, cap $3)",
                     f"ACTUAL list-price session cost; {len(attempts_log)} calls; wall {summ['wall_s']} s; cold start "
                     f"{sess['cold_start_s']} s; own containers after: {len(cc['own_final'])}; stops {[(x['id'], x['returncode']) for x in cc['stops']]}")
    print(json.dumps({k: v for k, v in summ.items() if k != "replacements"}, indent=1, default=str))
    print("replacements:", json.dumps(replacements, default=str)[:3000])


if __name__ == "__main__":
    # v5/select.py (renamed select_items.py under D49e) shadowed the stdlib `select` for any child `python -m ...`
    # started with cwd=v5 (that hung `modal container list`); children still run with -I from P as a safeguard.
    os.chdir(P)
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-launch", action="store_true")
    asyncio.run(run(ap.parse_args()))
