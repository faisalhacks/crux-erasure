"""LLM annotator panel (supplementary; not human), task P1 only: FROZEN_RULES.md section 6.R5.4, decisions.md D50, D51.

Members (FR 6.R5.4): falcon-h1-34b, command-r7b, granite4.2-30b.  gpt-oss-120b is excluded (it extracted the quotes).
Prompt: analysis/panel/P1_prompt.md (FR leaves the wording to the author's view: question, Quote A, Quote B, statement,
Q1 and Q2 in the packet wording, plus the one FR format line).  The same template, decoding and parser for every model.
Decoding: temperature 0, seed 0, one item per call, fresh context (one user message, no system message), retry once with
seed 1, still invalid -> missing (counted, never filled).  max_tokens and chat_template_kwargs as in the manifest.
Format bar (decides membership): the 20 development-launch items of analysis/panel/dev_items.json (built like packet
items); >= 20 calls; valid share after one retry >= 0.95.  Decided before any packet-item call, inside the same
session.  Format-line revisions: 0.  No re-runs, no substitute models.  A model that fails the bar makes no packet call.
Membership barrier: after its own bar, each process waits (bounded) for the other members' bar files; packet calls are
made only if this model passed and at least 2 models are known to have passed ("no panel" otherwise).
Validity: a JSON object (first '{' to last '}') with q1_quotes_disagree and q2_statement_acknowledges, each "yes" or
"no" (case and surrounding spaces ignored, as the author's rule).
Modes (run from P with python -I):
  manifest                 write gate1/llm_panel/panel_manifest.json (refuses to change an existing one)
  run --alias A --max-s N  [--confirm-launch]   one Modal session for one member
Never reads or writes labels\\.  Reads no score, rank, rating or scorer output.
"""
import argparse
import asyncio
import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
OUT = P / "analysis" / "panel"
GATE = P / "gate1" / "llm_panel"
V5 = P / "labels_build" / "v5"
sys.path.insert(0, str(P / "analysis"))
os.environ["MODAL_ENDPOINTS"] = str(P / "serving" / "endpoints.json")
import scorer as S  # noqa: E402

MEMBERS = ["falcon-h1-34b", "command-r7b", "granite4.2-30b"]
PROMPT = OUT / "P1_prompt.md"
FORMAT_LINE = 'Return JSON only: {"q1_quotes_disagree": "yes" or "no", "q2_statement_acknowledges": "yes" or "no"}'
MAX_TOK = 512
EXTRA = {"chat_template_kwargs": {"enable_thinking": False}}
SEEDS = (0, 1)
BAR_MIN_CALLS, BAR_MIN_VALID = 20, 0.95
PILOT, PILOT_CAP = "T3-1-panel-P1", 5.0
MODAL_PY = "C:/Users/intel/miniconda3/python.exe"
YN = {"yes", "no"}
WORDING = "LLM annotator panel (supplementary; not human)"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def fill(tmpl, it):
    return re.sub(r"\{(question|quote_a|quote_b|statement)\}", lambda m: it[m.group(1)], tmpl)


def parse(text):
    js = S.parse_json_obj(text)
    if js is None:
        return None, "no JSON object"
    out = {}
    for k in ("q1_quotes_disagree", "q2_statement_acknowledges"):
        v = js.get(k)
        if not isinstance(v, str) or v.strip().lower() not in YN:
            return None, f"{k} missing or not yes/no"
        out[k] = v.strip().lower()
    return out, None


def br(t):
    return html.escape(t or "").replace("\r\n", "\n").replace("\n", "<br>")


def packet_items():
    """The 25 packet items with exactly the inputs the author sees, cross-checked against the packet HTML."""
    ext = {x["slot_index"]: x for x in json.loads((V5 / "extraction.json").read_text(encoding="utf-8"))["items"]}
    page = (V5 / "packet_verification.html").read_text(encoding="utf-8")
    items = []
    with open(V5 / "key_verification.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            e = ext[int(row["slot_index"])]
            assert e["result"]["quote_a"] == row["quote_a"] and e["result"]["quote_b"] == row["quote_b"], row["item_id"]
            it = dict(item_id=row["item_id"], question=e["question"], quote_a=row["quote_a"], quote_b=row["quote_b"],
                      statement=e["statement"])
            m = re.search(r"<section id='" + re.escape(it["item_id"]) + r"'>(.*?)</section>", page, re.S)
            assert m, it["item_id"]
            sec = m.group(1)
            for k in ("question", "quote_a", "quote_b", "statement"):
                assert br(it[k]) in sec, (it["item_id"], k)
            items.append(it)
    items.sort(key=lambda x: x["item_id"])
    assert len(items) == 25 and len({x["item_id"] for x in items}) == 25
    return items


def dev_items():
    d = json.loads((OUT / "dev_items.json").read_text(encoding="utf-8"))
    its = [dict(item_id=f"dev-{i:02d}", launch_id=x["launch_id"], round_id=x["round_id"], question=x["question"],
                quote_a=x["quote_a"], quote_b=x["quote_b"], statement=x["statement"]) for i, x in enumerate(d["items"], 1)]
    assert len(its) >= BAR_MIN_CALLS
    return its


def write_manifest():
    tmpl = PROMPT.read_text(encoding="utf-8")
    assert tmpl.rstrip("\n").endswith(FORMAT_LINE)
    man = dict(
        wording=WORDING, task="P1 only (P2 dropped, D50 q4)", rules="FROZEN_RULES.md 6.R5.4; decisions.md D50, D51",
        frozen_rules_sha256=sha(P / "FROZEN_RULES.md"),
        members=MEMBERS, excluded={"gptoss-120b": "extracts the quotes (self-evaluation on Q1)"},
        prompt_file="analysis/panel/P1_prompt.md", prompt_sha256=sha(PROMPT),
        prompt_note="FR 6.R5.4 fixes the inputs, Q1/Q2 wording and the format line, not the full text; written neutrally "
                    "from INSTRUCTIONS_verification.md and the packet wording; identical for every model",
        format_line=FORMAT_LINE, format_line_revisions=0,
        decoding=dict(temperature=0.0, seed=SEEDS[0], retry_seed=SEEDS[1], max_tokens=MAX_TOK, extra=EXTRA,
                      one_item_per_call=True, fresh_context=True, system_prompt=None, response_format=None),
        validity="JSON object (first '{' to last '}') with q1_quotes_disagree and q2_statement_acknowledges each yes/no "
                 "(case and surrounding spaces ignored); invalid after the seed-1 retry -> missing, counted, never filled",
        format_bar=dict(items="analysis/panel/dev_items.json (development launches only)", dev_items_sha256=sha(OUT / "dev_items.json"),
                        min_calls=BAR_MIN_CALLS, min_valid_share_after_retry=BAR_MIN_VALID,
                        decided_before_any_packet_call=True, reruns=0, substitutes=0,
                        no_panel_rule="fewer than 2 models pass -> NO_PANEL, reported, nothing else"),
        packet_inputs={p: sha(V5 / p) for p in ("key_verification.csv", "extraction.json", "packet_verification.html")},
        majority="value given by >= 2 members; a member missing -> the other two must agree; else NO_MAJORITY; with exactly "
                 "2 members: unanimity",
        bootstrap=dict(B=10000, rng="numpy.random.default_rng(20261145)", unit="item"),
        outputs="analysis/panel/ (as instructed by the orchestrator) with identical copies in gate1/llm_panel/ (FR 6.R5.4); never labels\\",
        written_utc=S.utc(),
    )
    GATE.mkdir(parents=True, exist_ok=True)
    f = GATE / "panel_manifest.json"
    if f.exists():
        old = json.loads(f.read_text(encoding="utf-8"))
        old.pop("written_utc", None)
        new = dict(man)
        new.pop("written_utc")
        if old != new:
            raise SystemExit("REFUSED: panel_manifest.json exists with different settings")
        print("manifest unchanged", sha(f))
        return
    f.write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print("manifest written", sha(f))


def check_manifest():
    man = json.loads((GATE / "panel_manifest.json").read_text(encoding="utf-8"))
    assert man["prompt_sha256"] == sha(PROMPT), "prompt changed after manifest"
    assert man["format_bar"]["dev_items_sha256"] == sha(OUT / "dev_items.json"), "dev items changed"
    for p, h in man["packet_inputs"].items():
        assert sha(V5 / p) == h, p
    assert man["decoding"]["max_tokens"] == MAX_TOK and man["decoding"]["extra"] == EXTRA
    return man


# ------------------------------------------------------------------ own-app container poll (UTF-8, stdin closed)
def container_rows():
    r = subprocess.run([MODAL_PY, "-I", "-m", "modal", "container", "list", "--json"], capture_output=True,
                       stdin=subprocess.DEVNULL, timeout=120, cwd=str(P))
    out = (r.stdout or b"").decode("utf-8", errors="replace")
    err = (r.stderr or b"").decode("utf-8", errors="replace")
    try:
        rows = [json.dumps(x, ensure_ascii=False) for x in json.loads(out or "[]")]
    except json.JSONDecodeError:
        return 99, [], ("unparseable list output: " + out[-200:] + err)[-300:]
    rows = [ln for ln in rows if re.search(r"\bta-[0-9A-Za-z]+", ln)]
    return r.returncode, rows, err[-300:]


def own_ids(rows, app, baseline):
    pat = re.compile(re.escape(app) + r"(?![0-9A-Za-z.\-])")
    ids = [re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows if pat.search(ln)]
    return [i for i in ids if i not in baseline]


def wait_and_stop(app, baseline, max_wait_s=300, every_s=15):
    t0, polls, stops = time.time(), [], []
    while True:
        rc, rows, err = container_rows()
        mine = own_ids(rows, app, baseline)
        polls.append(dict(t=round(time.time() - t0), rc=rc, all_rows=len(rows), own=mine, err=err if rc else ""))
        if rc != 0 or not mine or time.time() - t0 >= max_wait_s:
            break
        time.sleep(every_s)
    if rc == 0 and mine:
        for cid in mine:
            r = subprocess.run([MODAL_PY, "-I", "-m", "modal", "container", "stop", "-y", cid], capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=120, cwd=str(P))
            stops.append(dict(id=cid, returncode=r.returncode, stderr=(r.stderr or b"").decode("utf-8", errors="replace")[-300:]))
        time.sleep(10)
        rc, rows, err = container_rows()
        mine = own_ids(rows, app, baseline)
        polls.append(dict(t=round(time.time() - t0), rc=rc, all_rows=len(rows), own=mine, err=err if rc else ""))
    return dict(app=app, waited_s=round(time.time() - t0), polls=polls, stops=stops, own_final=mine, baseline=sorted(baseline))


# ------------------------------------------------------------------ calls
async def answer(llm, alias, prompts):
    """prompts: {item_id: prompt}. Seed 0 for all, one retry with seed 1 for the invalid. Returns {item_id: record}."""
    rec = {k: dict(attempts=[], parsed=None) for k in prompts}
    todo = list(prompts)
    for seed in SEEDS:
        if not todo:
            break
        jobs = [dict(provider="modal", model=alias, messages=[{"role": "user", "content": prompts[k]}],
                     max_tokens=MAX_TOK, temperature=0.0, seed=seed, extra=EXTRA) for k in todo]
        out = await llm.run_many(jobs, stop_on_budget=True)
        nxt = []
        for k, r in zip(todo, out):
            if isinstance(r, Exception):
                rec[k]["attempts"].append(dict(seed=seed, error=str(r)[:300], valid=False))
                nxt.append(k)
                continue
            p, why = parse(r["text"])
            rec[k]["attempts"].append(dict(seed=seed, text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"),
                                           valid=p is not None, why=why))
            if p:
                rec[k]["parsed"] = p
            else:
                nxt.append(k)
        todo = nxt
    return rec


def bar_file(alias):
    return OUT / f"bar_p1_{alias}.json"


def wait_for_members(alias, deadline, every_s=5):
    while True:
        known = {}
        for m in MEMBERS:
            f = bar_file(m)
            if f.exists():
                try:
                    known[m] = json.loads(f.read_text(encoding="utf-8"))["bar_pass"]
                except (json.JSONDecodeError, KeyError):
                    pass
        if len(known) == len(MEMBERS) or time.time() >= deadline:
            return known
        time.sleep(every_s)


async def run(a):
    man = check_manifest()
    alias = a.alias
    assert alias in MEMBERS
    tmpl = PROMPT.read_text(encoding="utf-8")
    dev = dev_items()
    pk = packet_items()
    dev_prompts = {x["item_id"]: fill(tmpl, x) for x in dev}
    pk_prompts = {x["item_id"]: fill(tmpl, x) for x in pk}
    assert all(p.rstrip("\n").endswith(FORMAT_LINE) for p in list(dev_prompts.values()) + list(pk_prompts.values()))
    print(alias, "dev", len(dev_prompts), "packet", len(pk_prompts), "prompt sha", man["prompt_sha256"][:12])
    if not a.confirm_launch:
        print("dry run; example dev prompt:\n" + next(iter(dev_prompts.values()))[:1500])
        return
    if bar_file(alias).exists():
        raise SystemExit("REFUSED: a bar file for this model exists (no re-runs)")
    ep = S.modal_endpoints()[alias]
    app = ep["app"]
    gpu = f"{ep['gpu']}x{ep.get('n_gpu', 1)}"
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    worst = round(rate * (a.max_s + ep["scaledown_s"] + 15), 3)
    rc, rows, _ = container_rows()
    if rc != 0:
        raise SystemExit("STOP: modal container list failed before launch")
    baseline = {re.search(r"ta-[0-9A-Za-z]+", ln).group(0) for ln in rows}
    S.ledger_row(f"{WORDING} P1 {alias} (20 dev format-bar items, then 25 packet items if >=2 members pass; <=2 attempts) ESTIMATE",
                 "r5-panel-p1", gpu, worst, "", a.max_s, "panel runner (FR 6.R5.4; total cap $5)",
                 f"ESTIMATE row before launch; worst-case ${worst} ({a.max_s} s session cap + scaledown); baseline containers "
                 f"{len(baseline)}; prompt sha {man['prompt_sha256'][:16]}")
    llm = S.LLM(pilot=PILOT, pilot_cap=PILOT_CAP, timeout_s=300.0, concurrency={"modal": 13})
    bar, pk_rec, sess, members_known, t0, err = None, None, None, {}, time.time(), None
    try:
        async with llm.modal_session(alias, max_seconds=a.max_s) as s:
            dev_rec = await answer(llm, alias, dev_prompts)
            calls = sum(len(r["attempts"]) for r in dev_rec.values())
            nvalid = sum(1 for r in dev_rec.values() if r["parsed"])
            share = nvalid / len(dev_rec)
            bar = dict(alias=alias, items=len(dev_rec), calls=calls, first_attempt_valid=sum(1 for r in dev_rec.values() if r["attempts"][0]["valid"]),
                       valid_after_retry=nvalid, valid_share=share,
                       bar_pass=bool(calls >= BAR_MIN_CALLS and len(dev_rec) >= BAR_MIN_CALLS and share >= BAR_MIN_VALID),
                       truncated=sum(1 for r in dev_rec.values() for x in r["attempts"] if x.get("finish_reason") == "length"),
                       decided_utc=S.utc(), cold_start_s=s.cold_start_s)
            with open(OUT / f"bar_p1_{alias}.jsonl", "w", encoding="utf-8", newline="\n") as f:
                for k in dev_prompts:
                    f.write(json.dumps(dict(item_id=k, phase="format_bar_dev", **dev_rec[k]), ensure_ascii=False) + "\n")
            bar_file(alias).write_text(json.dumps(bar, indent=1), encoding="utf-8")
            print("BAR", json.dumps(bar))
            if bar["bar_pass"]:
                deadline = s.t0 + a.max_s - a.reserve_s
                members_known = wait_for_members(alias, deadline)
                n_pass = sum(1 for v in members_known.values() if v)
                print("members known", members_known)
                if n_pass >= 2:
                    pk_rec = await answer(llm, alias, pk_prompts)
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    except Exception as e:  # noqa: BLE001
        err = repr(e)[:500]
        print("ERROR", err)
        if bar is None:
            bar = dict(alias=alias, bar_pass=False, error=err, decided_utc=S.utc())
            bar_file(alias).write_text(json.dumps(bar, indent=1), encoding="utf-8")
    finally:
        await llm.aclose()
        cc = wait_and_stop(app, baseline)
        (OUT / f"container_check_p1_{alias}.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
    if pk_rec is not None:
        with open(OUT / f"panel_p1_{alias}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for k in sorted(pk_prompts):
                f.write(json.dumps(dict(item_id=k, phase="packet", model=alias, valid=pk_rec[k]["parsed"] is not None,
                                        parsed=pk_rec[k]["parsed"], attempts=pk_rec[k]["attempts"]), ensure_ascii=False) + "\n")
    run_rec = dict(alias=alias, app=app, utc=S.utc(), bar=bar, members_known_at_decision=members_known,
                   packet_called=pk_rec is not None,
                   packet_valid=(sum(1 for r in pk_rec.values() if r["parsed"]) if pk_rec else None),
                   packet_calls=(sum(len(r["attempts"]) for r in pk_rec.values()) if pk_rec else 0),
                   session=sess, error=err, wall_s=round(time.time() - t0, 1),
                   container_check={k: v for k, v in cc.items() if k != "polls"}, script_sha256=sha(Path(__file__)))
    (OUT / f"run_p1_{alias}.json").write_text(json.dumps(run_rec, indent=1, default=str), encoding="utf-8")
    cost = sess["session_cost_usd"] if sess else None
    if cost is None:
        # session left by an exception: the harness settled it on exit; read the settled figure if available
        cost = round(llm.stats.get("spent_usd", 0.0), 4)
    S.ledger_row(f"{WORDING} P1 {alias} ACTUAL", "r5-panel-p1", gpu, "", cost, a.max_s, "panel runner (FR 6.R5.4; total cap $5)",
                 f"ACTUAL list-price session cost; bar {bar.get('valid_after_retry')}/{bar.get('items')} valid "
                 f"({bar.get('calls')} calls) pass={bar.get('bar_pass')}; packet calls {run_rec['packet_calls']}; wall {run_rec['wall_s']} s; "
                 f"cold start {sess['cold_start_s'] if sess else None} s; own containers after: {len(cc['own_final'])}; "
                 f"stops {[(x['id'], x['returncode']) for x in cc['stops']]}; error {err}")
    print(json.dumps(run_rec, indent=1, default=str)[:3000])


if __name__ == "__main__":
    os.chdir(P)
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["manifest", "run"])
    ap.add_argument("--alias")
    ap.add_argument("--max-s", type=float, default=900)
    ap.add_argument("--reserve-s", type=float, default=240)
    ap.add_argument("--confirm-launch", action="store_true")
    a = ap.parse_args()
    if a.mode == "manifest":
        write_manifest()
    else:
        asyncio.run(run(a))
