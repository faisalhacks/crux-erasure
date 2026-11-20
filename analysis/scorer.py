"""Frozen crux-erasure scorer (FROZEN_RULES.md sections 3, 4, Appendix A).

Per round: ONE extraction call (prompt E1; inputs = question + opinions only) -> 0..4 cruxes.
Per statement: ONE labelling call (prompt L1) -> one of VISIBLE/SIDED/BLENDED/OMITTED per crux.
E(s) = hidden / n_cruxes, hidden = label != VISIBLE. Zero cruxes -> E undefined.
Decoding: temperature 0, seed 0 (retry seed 1), JSON output, max_tokens 700 / 300, thinking off.

This script reads ONLY: all_groups.jsonl / pilot_groups.jsonl fields question, opinions, candidates,
launch_id, round_id (the `raters` field is dropped at load), and key.json's sample ids. It reads no
ranking, rating, label or outcome. Scores must never be shown to labelers or joined to rankings
before GATE1_RESULT.json exists.

Modes (python -I scorer.py <mode>):
  prompts    write/verify analysis/prompts/{E1_extract,L1_label,C1_clarity}.txt from FROZEN_RULES Appendix A
  selftest   $0 unit checks
  mock       full pipeline on the harness MOCK provider ($0): dev-set rounds, order check on
  plan       cost estimates (probe / gate1 / all) -> scorer_runs/plan.json, no model called
  manifest   write scorer_manifest.json and SCORER_MANIFEST.md
  probe      Modal, dev set, 40 rounds (200 calls); needs --confirm-launch
  gate1      Modal, the 60 key.json sample statements -> scores/gate1_scores.jsonl; needs --confirm-launch
  all        Modal, all eligible rounds in random-prefix order; needs --confirm-launch AND --approval-file
Nothing launches Modal without --confirm-launch. A ledger.csv estimate+timeout row is written BEFORE
launch, an ACTUAL row after, and `modal container list` is run at the end.
"""
import argparse
import asyncio
import csv
import datetime
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE.parent
R = P.parent
HARNESS = R / "pilot_harness"
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HERE))
import llm as llm_mod                                   # noqa: E402
from budget import BudgetExceeded                       # noqa: E402
from llm import LLM, MOCK, modal_endpoints              # noqa: E402
from prices import modal_container_rate                 # noqa: E402

PILOT = R / "pilots" / "T3_1"
ALL_GROUPS = PILOT / "all_groups.jsonl"
DEV_GROUPS = PILOT / "pilot_groups.jsonl"
FROZEN = P / "FROZEN_RULES.md"
KEY = P / "labels_build" / "key.json"
PROMPTS = HERE / "prompts"
RUNS = HERE / "scorer_runs"
SCORES = HERE / "scores"
LEDGER = P / "ledger.csv"
MODAL_PY = "C:/Users/intel/miniconda3/python.exe"

# ---------------------------------------------------------------- frozen constants
SCORERS = {
    "qwen3.8-27b": dict(repo="Qwen/Qwen3.8-27B", revision="37561816e66b5b9153b1b64c10968c18c1e6f4a0"),
    "gemma4-12b": dict(repo="google/gemma-4-12B-it", revision="43c9d014b231474fa7212dbb48a762566c2b255d"),
    "granite4.2-30b": dict(repo="ibm-granite/granite-4.2-30b", revision="9e668ce1c538387ef24d3644e9b0606647762636"),
    "granite4.2-8b": dict(repo="ibm-granite/granite-4.2-8b", revision="a7042144125ce5ae64f89610e8289647fc000b9a"),
    "falcon-h1-34b": dict(repo="tiiuae/Falcon-H1-34B-Instruct", revision="6e6890e26cba1f58b1e6ee70d654ddf054f9fce8"),
    "command-r7b": dict(repo="CohereLabs/c4ai-command-r7b-12-2024", revision="4f3d0aa6856e322f2f4480fe65420d5d53d297b8"),   # FR 6.9 R4a candidate 2 (D48); registration only
}
TEMPERATURE = 0.0
SEED, RETRY_SEED = 0, 1
MAX_TOK_EXTRACT, MAX_TOK_LABEL = 700, 300
MAX_CRUXES = 4
LABELS = ("VISIBLE", "SIDED", "BLENDED", "OMITTED")
HIDE_THRESHOLD = 0.5                       # gate-1 AI binary: positive if E >= 0.5 (FR 6.4)
MAX_MODEL_LEN = 16384
EXTRACT_COLUMNS = ("question", "opinions")          # the ONLY inputs of crux extraction (FR 3)
RANDOM_PREFIX_SEED = 20261125               # EXPERIMENTS.md random-prefix rule
PROBE_ROUNDS, PROBE_SEED = 40, 20261126
COLD_START_S = None                         # override of the cold-start assumption in plans (first deploy of a big model)
PROMPT_FILES = {"E1": "E1_extract.txt", "L1": "L1_label.txt", "C1": "C1_clarity.txt"}

# cost assumptions: UNMEASURED, replaced by the probe's numbers (see SCORER_MANIFEST.md)
ASSUME = dict(decode_tok_per_s=400.0, prefill_tok_per_s=6000.0, overhead=1.15, phase_floor_s=30.0,
              extract_out_tok=300.0, label_out_tok=30.0, chars_per_tok=3.5, safety=2.0)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


# ---------------------------------------------------------------- prompts of record
def appendix_prompts():
    """Extract the three fenced prompts from FROZEN_RULES.md Appendix A, byte for byte."""
    txt = FROZEN.read_bytes().decode("utf-8")
    out = {}
    for name in PROMPT_FILES:
        m = re.search(r"^### " + name + r" [^\n]*\n\n```\n(.*?)\n```\n", txt, re.S | re.M)
        if not m:
            raise SystemExit(f"Appendix A prompt {name} not found in FROZEN_RULES.md")
        out[name] = m.group(1)
    return out


def write_prompts():
    PROMPTS.mkdir(exist_ok=True)
    for name, body in appendix_prompts().items():
        (PROMPTS / PROMPT_FILES[name]).write_bytes(body.encode("utf-8"))      # no trailing newline
    return verify_prompts()


def verify_prompts():
    ap = appendix_prompts()
    res = {}
    for name, fn in PROMPT_FILES.items():
        p = PROMPTS / fn
        if not p.exists():
            raise SystemExit(f"missing {p}; run: scorer.py prompts")
        b = p.read_bytes()
        if b != ap[name].encode("utf-8"):
            raise SystemExit(f"{p} is not byte-identical to FROZEN_RULES.md Appendix A ({name})")
        res[name] = hashlib.sha256(b).hexdigest()
    return res


def load_prompt(name):
    verify_prompts()
    return (PROMPTS / PROMPT_FILES[name]).read_bytes().decode("utf-8")


def _fill(template, mapping_re, fn):
    return re.sub(mapping_re, fn, template)            # single pass: inserted text is never re-scanned


def build_extract_prompt(row, template=None):
    """row holds EXACTLY the columns question + opinions (asserted: unit test + here)."""
    assert tuple(sorted(row.keys())) == tuple(sorted(EXTRACT_COLUMNS)), f"extraction input has columns {sorted(row)}"
    numbered = "\n".join(f"{i + 1}. {t}" for i, (_, t) in enumerate(sorted(row["opinions"].items())))
    vals = {"{question}": row["question"], "{numbered_opinions}": numbered}
    return _fill(template or load_prompt("E1"), r"\{question\}|\{numbered_opinions\}", lambda m: vals[m.group(0)])


def build_label_prompt(question, cruxes, statement, template=None):
    lines = "\n".join(f"{i + 1}. {c['issue']} (Side A: {c['side_a']} | Side B: {c['side_b']})" for i, c in enumerate(cruxes))
    vals = {"{question}": question, "{statement}": statement}

    def fn(m):
        s = m.group(0)
        return lines if s.startswith("{numbered_cruxes_as") else vals[s]
    return _fill(template or load_prompt("L1"), r"\{question\}|\{statement\}|\{numbered_cruxes_as:[^\n]*\}", fn)


# ---------------------------------------------------------------- parsing
def parse_json_obj(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        v = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None
    return v if isinstance(v, dict) else None


def _members(v, n):
    if not isinstance(v, list):
        return []
    return sorted({x for x in v if isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= n})


EMPTY_SIDE_DROPPED = {"n": 0}      # count of cruxes dropped for an empty side (per process; reported in summary.json)


def parse_cruxes(text, n_members):
    """None = parse failure. [] = valid, zero cruxes. Member lists are sanitised, never a failure."""
    js = parse_json_obj(text)
    if js is None or not isinstance(js.get("cruxes"), list) or len(js["cruxes"]) > MAX_CRUXES:
        return None
    out = []
    for c in js["cruxes"]:
        if not isinstance(c, dict):
            return None
        for k in ("issue", "side_a", "side_b"):
            if not isinstance(c.get(k), str) or not c[k].strip():
                return None
        cx = dict(issue=c["issue"].strip(), side_a=c["side_a"].strip(), side_b=c["side_b"].strip(),
                  members_a=_members(c.get("members_a"), n_members), members_b=_members(c.get("members_b"), n_members))
        if not cx["members_a"] or not cx["members_b"]:           # FR 3 [R1]: a crux needs members on BOTH sides
            EMPTY_SIDE_DROPPED["n"] += 1
            continue
        out.append(cx)
    return out


def parse_labels(text, n):
    js = parse_json_obj(text)
    if js is None or not isinstance(js.get("labels"), list) or len(js["labels"]) != n:
        return None
    labs = [str(x).strip().upper() for x in js["labels"]]
    return labs if all(x in LABELS for x in labs) else None


def erasure(labels):
    """E = hidden/total; None if no cruxes or labels missing."""
    if not labels:
        return None
    return sum(1 for x in labels if x != "VISIBLE") / len(labels)


def ai_binary(e, n_cruxes, parse_ok):
    """FR 6.4: positive if E >= 0.5; negative if E < 0.5 or zero cruxes; missing E (parse failure) = None (wrong)."""
    if not parse_ok:
        return None
    if n_cruxes == 0:
        return False
    return e >= HIDE_THRESHOLD


def swap_cruxes(cruxes):
    """Order-check variant: list reversed, sides A/B swapped."""
    return [dict(issue=c["issue"], side_a=c["side_b"], side_b=c["side_a"],
                 members_a=c["members_b"], members_b=c["members_a"]) for c in reversed(cruxes)]


# ---------------------------------------------------------------- data (outcome-free)
def load_rounds(path, only=None):
    """Keep ONLY launch_id, round_id, question, opinions, candidates. `raters` is dropped here."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            g = json.loads(line)
            k = (g["launch_id"], g["round_id"])
            if only is not None and k not in only:
                continue
            out[k] = dict(launch_id=g["launch_id"], round_id=g["round_id"], question=g["question"],
                          opinions=dict(sorted(g["opinions"].items())), candidates=list(g["candidates"]))
    return out


def est_tokens(s):
    return int(math.ceil(len(s) / 2.5))              # conservative, as the harness


# ---------------------------------------------------------------- model calls
def mk_job(provider, alias, prompt, max_tokens, seed):
    extra = {"response_format": {"type": "json_object"}}
    if provider == "modal":
        extra["chat_template_kwargs"] = {"enable_thinking": False}
    return dict(provider=provider, model=alias, messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens, temperature=TEMPERATURE, seed=seed, extra=extra)


async def call_all(llm, provider, alias, specs, parse_fn, stats, phase):
    """specs: list of (key, prompt, max_tokens, parse_arg). Seed 0, then ONE retry with seed 1 for any failure."""
    results = {}
    pending = list(specs)
    for attempt, seed in enumerate((SEED, RETRY_SEED)):
        if not pending:
            break
        jobs = [mk_job(provider, alias, pr, mt, seed) for _, pr, mt, _ in pending]
        res = await llm.run_many(jobs, stop_on_budget=True)
        nxt = []
        for (key, pr, mt, parg), r in zip(pending, res):
            rec = results.setdefault(key, dict(attempts=[], parsed=None, ok=False))
            if isinstance(r, Exception):
                rec["attempts"].append(dict(seed=seed, error=type(r).__name__ + ": " + str(r)[:160]))
                stats["errors"] += isinstance(r, BudgetExceeded) is False
                if isinstance(r, BudgetExceeded):
                    stats["stopped"] = str(r)[:160]
                nxt.append((key, pr, mt, parg))
                continue
            parsed = parse_fn(r["text"], parg)
            rec["attempts"].append(dict(seed=seed, text=r["text"], finish_reason=r.get("finish_reason"),
                                        usage=r.get("usage"), parse_ok=parsed is not None))
            stats["calls"] += 1
            stats["truncated"] += r.get("finish_reason") == "length"
            u = r.get("usage") or {}
            stats["prompt_tokens"] += u.get("prompt_tokens", 0) or 0
            stats["completion_tokens"] += u.get("completion_tokens", 0) or 0
            if parsed is not None:
                rec["parsed"], rec["ok"] = parsed, True
            else:
                nxt.append((key, pr, mt, parg))
        stats["parse_fail_first_" + phase] = len(pending) - sum(1 for k, *_ in pending if results[k]["ok"]) if attempt == 0 else stats.get("parse_fail_first_" + phase)
        pending = [x for x in nxt if not results[x[0]]["ok"]]
        if stats.get("stopped"):
            break
    stats["parse_fail_final_" + phase] = sum(1 for v in results.values() if not v["ok"])
    stats["n_" + phase] = len(results)
    return results


async def score_statements(llm, provider, alias, rounds, items, order_check, stats):
    """items: list of dicts with launch_id, round_id, cand. Returns (score_records, extraction_records)."""
    t0 = time.time()
    rkeys = sorted({(i["launch_id"], i["round_id"]) for i in items})
    dropped = []
    specs, tmpl = [], load_prompt("E1")
    for k in rkeys:
        g = rounds[k]
        pr = build_extract_prompt(dict(question=g["question"], opinions=g["opinions"]), tmpl)
        if est_tokens(pr) + MAX_TOK_EXTRACT > MAX_MODEL_LEN:
            dropped.append(k)
            continue
        specs.append((k, pr, MAX_TOK_EXTRACT, len(g["opinions"])))
    ex = await call_all(llm, provider, alias, specs, parse_cruxes, stats, "extract")
    stats["t_extract_s"] = round(time.time() - t0, 1)
    ext_recs = []
    for k in rkeys:
        r = ex.get(k)
        ext_recs.append(dict(launch_id=k[0], round_id=k[1], dropped_too_long=k in dropped,
                             ok=bool(r and r["ok"]), n_cruxes=len(r["parsed"]) if r and r["ok"] else None,
                             cruxes=r["parsed"] if r and r["ok"] else None,
                             attempts=r["attempts"] if r else []))
    ltm = load_prompt("L1")
    lspecs, lspecs_sw = [], []
    for it in items:
        k = (it["launch_id"], it["round_id"])
        r = ex.get(k)
        if not r or not r["ok"] or not r["parsed"]:
            continue
        g = rounds[k]
        key = (k[0], k[1], it["cand"])
        lspecs.append((key, build_label_prompt(g["question"], r["parsed"], g["candidates"][it["cand"]], ltm), MAX_TOK_LABEL, len(r["parsed"])))
        if order_check:
            lspecs_sw.append((key, build_label_prompt(g["question"], swap_cruxes(r["parsed"]), g["candidates"][it["cand"]], ltm),
                              MAX_TOK_LABEL, len(r["parsed"])))
    t1 = time.time()
    lb = await call_all(llm, provider, alias, lspecs, parse_labels, stats, "label")
    stats["t_label_s"] = round(time.time() - t1, 1)
    lbs = {}
    if order_check:
        t2 = time.time()
        lbs = await call_all(llm, provider, alias, lspecs_sw, parse_labels, stats, "label_swapped")
        stats["t_label_swapped_s"] = round(time.time() - t2, 1)
    recs = []
    for it in items:
        k = (it["launch_id"], it["round_id"])
        key = (k[0], k[1], it["cand"])
        r = ex.get(k)
        rec = dict(launch_id=k[0], round_id=k[1], cand=it["cand"], item_ids=it.get("item_ids"), scorer=alias,
                   extract_ok=bool(r and r["ok"]), n_cruxes=len(r["parsed"]) if r and r["ok"] else None,
                   labels=None, E=None, label_ok=None, ai_binary=None, labels_swapped=None, E_swapped=None,
                   binary_swapped=None, order_flip=None, dropped_too_long=k in dropped)
        if rec["extract_ok"]:
            if rec["n_cruxes"] == 0:
                rec.update(E=None, label_ok=True, ai_binary=False)          # zero cruxes: E undefined, AI binary negative
            else:
                lr = lb.get(key)
                rec["label_ok"] = bool(lr and lr["ok"])
                if rec["label_ok"]:
                    rec["labels"] = lr["parsed"]
                    rec["E"] = erasure(lr["parsed"])
                rec["ai_binary"] = ai_binary(rec["E"], rec["n_cruxes"], rec["label_ok"])
                if order_check:
                    sr = lbs.get(key)
                    if sr and sr["ok"]:
                        back = list(reversed(sr["parsed"]))                 # map back to the original crux order
                        rec["labels_swapped"], rec["E_swapped"] = back, erasure(back)
                        rec["binary_swapped"] = ai_binary(rec["E_swapped"], rec["n_cruxes"], True)
                        if rec["ai_binary"] is not None:
                            rec["order_flip"] = rec["binary_swapped"] != rec["ai_binary"]
        recs.append(rec)
    return recs, ext_recs


# ---------------------------------------------------------------- cost
def prompt_tokens_for(rounds, keys, which):
    et, lt = load_prompt("E1"), load_prompt("L1")
    c = ASSUME["chars_per_tok"]
    if which == "extract":
        return [len(build_extract_prompt(dict(question=rounds[k]["question"], opinions=rounds[k]["opinions"]), et)) / c for k in keys]
    fake = [dict(issue="x" * 80, side_a="y" * 120, side_b="z" * 120)] * 3
    return [len(build_label_prompt(rounds[k]["question"], fake, s, lt)) / c for k in keys for s in rounds[k]["candidates"]]


def estimate(alias, n_ext, n_lab, ext_prompt_tok, lab_prompt_tok, n_phases, a=ASSUME):
    ep = modal_endpoints()[alias]
    rate = modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    tail = float(ep["scaledown_s"]) + 15.0
    cold = COLD_START_S or (106.0 if alias == "qwen3.8-27b" else 104.0)
    dec = n_ext * a["extract_out_tok"] + n_lab * a["label_out_tok"]
    pre = n_ext * ext_prompt_tok + n_lab * lab_prompt_tok
    work = (dec / a["decode_tok_per_s"] + pre / a["prefill_tok_per_s"]) * a["overhead"] + n_phases * a["phase_floor_s"]
    wall = cold + work
    max_s = int(math.ceil(a["safety"] * wall / 100.0) * 100)
    return dict(scorer=alias, gpu=f"{ep['gpu']}x{ep.get('n_gpu', 1)}", rate_usd_per_s=round(rate, 9), calls=n_ext + n_lab,
                decode_tokens=int(dec), prefill_tokens=int(pre), expected_wall_s=round(wall), session_max_seconds=max_s,
                expected_usd=round(rate * (wall + tail), 3), worst_case_usd=round(rate * (max_s + tail), 3), assumptions=a)


def make_plans(alias="qwen3.8-27b"):
    allr = load_rounds(ALL_GROUPS)
    dev = load_rounds(DEV_GROUPS)
    plans = {}
    dkeys = sorted(dev)[:PROBE_ROUNDS]
    plans["probe"] = estimate(alias, len(dkeys), 4 * len(dkeys), mean(prompt_tokens_for(dev, dkeys, "extract")),
                              mean(prompt_tokens_for(dev, dkeys, "label")), 2)
    k = json.loads(KEY.read_text(encoding="utf-8")) if KEY.exists() else None
    if k:
        gk = sorted({(s["launch_id"], s["round_id"]) for v in k["sample"].values() for s in v})
        plans["gate1"] = estimate(alias, len(gk), 2 * 60, mean(prompt_tokens_for(allr, gk, "extract")),
                                  mean(prompt_tokens_for(allr, gk, "label")), 3)
    ak = sorted(allr)
    plans["all"] = estimate(alias, len(ak), 4 * len(ak), mean(prompt_tokens_for(allr, ak, "extract")),
                            mean(prompt_tokens_for(allr, ak, "label")), 2)
    # measured (probe 2026-11-15, gate1 run): extraction 0.73 s/round, labelling 0.14 s/call at 32-way; ~15% of rounds have 0 cruxes
    ep = modal_endpoints()[alias]
    rate = modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    wall = 106.0 + 0.89 * len(ak) + 0.14 * 4 * len(ak) * 0.85    # 0.89 s/round: dev probe (gate run 0.73), the larger is used
    plans["all_measured"] = dict(scorer=alias, calls=len(ak) + 4 * len(ak), expected_wall_s=round(wall), session_max_seconds=3700,
                                 expected_usd=round(rate * (wall + 135), 3), worst_case_usd=round(rate * (3700 + 135), 3),
                                 gpu=f"{ep['gpu']}x{ep.get('n_gpu', 1)}", rate_usd_per_s=round(rate, 9),
                                 note="extrapolated from 2 measured runs of ~180 calls; timeout 3700 s per EXPERIMENTS.md A2")
    plans["all_gemma4-12b_A4"] = estimate("gemma4-12b", len(ak), 4 * len(ak), plans["all"]["prefill_tokens"] / (len(ak) * 5),
                                          plans["all"]["prefill_tokens"] / (len(ak) * 5), 2)
    return plans


def mean(x):
    x = list(x)
    return sum(x) / len(x)


# ---------------------------------------------------------------- ledger + containers
def ledger_last_cum():
    cum = 0.0
    with open(LEDGER, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                cum = float(row["cumulative_usd"]) if row["cumulative_usd"] else cum
            except ValueError:
                pass
    return cum


def ledger_row(job, exp, gpu, est, actual, timeout, approved, notes):
    cum = ""
    if actual != "":
        cum = round(ledger_last_cum() + float(actual), 4)
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([utc(), job, exp, "modal", gpu, est, actual, cum, timeout, approved, notes])


def container_check():
    try:
        r = subprocess.run([MODAL_PY, "-m", "modal", "container", "list"], capture_output=True, text=True, timeout=120)
        out = (r.stdout or "").strip()
        rows = [ln for ln in out.splitlines() if re.search(r"\bta-[0-9A-Za-z]+", ln)]
        return dict(returncode=r.returncode, container_rows=len(rows), stdout_tail=out[-4000:], stderr_tail=(r.stderr or "")[-300:])
    except Exception as e:  # noqa: BLE001
        return dict(error=repr(e)[:200])


CHUNK_ROUNDS = 100


def read_done(path):
    d = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                d[(r["launch_id"], r["round_id"], r["cand"])] = r
            except (json.JSONDecodeError, KeyError):
                pass                                          # torn last line is ignored and redone
    return d


def append_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()


def chunk_by_round(items, n_rounds):
    """Chunks of whole rounds, in the given (random-prefix) order."""
    order, by = [], {}
    for i in items:
        k = (i["launch_id"], i["round_id"])
        if k not in by:
            by[k] = []
            order.append(k)
        by[k].append(i)
    return [[i for k in order[x:x + n_rounds] for i in by[k]] for x in range(0, len(order), n_rounds)]


BASELINE_IDS = set()          # container ids present before launch (other sessions' warm containers); set in execute()


def container_wait_empty(alias, max_wait_s=300, every_s=15):
    """After the session closes: poll `modal container list` until no container of THIS scorer's app remains
    (other apps' containers, e.g. N2 gemma, are counted separately and never touched). Bounded; if still alive
    at max_wait_s, stop our own container by id (-y) and re-check once."""
    prefix = "pilot-vllm-" + alias.split("-")[0][:4]            # list truncates app names; 'pilot-vllm-qwen' / 'pilot-vllm-gemm'
    t0 = time.time()
    last, stopped = {}, []

    def own():
        c = container_check()
        rows = [ln for ln in (c.get("stdout_tail", "") or "").splitlines() if re.search(r"\bta-[0-9A-Za-z]+", ln)]
        full = [ln for ln in rows if prefix in ln]
        ids = [m.group(0) for ln in full for m in [re.search(r"ta-[0-9A-Za-z]+", ln)] if m]
        mine = [i for i in ids if i not in BASELINE_IDS]        # containers alive before this run belong to other sessions: never stopped
        return c, mine, len(rows) - len(mine)
    while True:
        last, ids, other = own()
        if last.get("error") or last.get("returncode") not in (0, None):
            break
        if not ids or time.time() - t0 >= max_wait_s:
            break
        time.sleep(every_s)
    if ids and not last.get("error"):
        for cid in ids:
            subprocess.run([MODAL_PY, "-m", "modal", "container", "stop", "-y", cid], capture_output=True, text=True, timeout=120)
            stopped.append(cid)
        time.sleep(10)
        last, ids, other = own()
    return dict(waited_s=round(time.time() - t0), own_rows_final=len(ids), other_app_rows=other, stopped_by_id=stopped,
                returncode=last.get("returncode"), error=last.get("error"), stdout_tail=last.get("stdout_tail", "")[-400:])


# ---------------------------------------------------------------- mock provider (tests only)
def install_mock_responses():
    """Replace the harness mock's junk tokens with schema-valid JSON, deterministically; some failures on purpose.
    h%10==0: always unparsable (-> missing E). h%10==1: unparsable on the first call only (-> retry works)."""
    seen = {}

    async def fake(self, model, messages, max_tokens, logprobs, top_logprobs):
        MOCK.calls += 1
        await asyncio.sleep(MOCK.latency_s)
        prompt = " ".join(str(m.get("content")) for m in messages)
        h = int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16)
        seen[prompt] = seen.get(prompt, 0) + 1
        if h % 10 == 0 or (h % 10 == 1 and seen[prompt] == 1):
            text = "not json at all"
        elif "list the CRUXES" in prompt:
            n = h % 5                                           # 0..4 cruxes
            text = json.dumps({"cruxes": [dict(issue=f"issue {i}", side_a="a", members_a=[1], side_b="b", members_b=[2]) for i in range(n)]})
        else:
            n = len(re.findall(r"^\d+\. issue", prompt, re.M))
            text = json.dumps({"labels": [LABELS[(h >> (2 * i)) % 4] for i in range(n)]})
        return {"choices": [{"message": {"content": text}, "finish_reason": "stop", "logprobs": None}],
                "usage": {"prompt_tokens": len(prompt) // 4 + 5, "completion_tokens": len(text) // 4 + 1}}
    llm_mod.LLM._mock = fake


# ---------------------------------------------------------------- orchestration
def summarise(recs, stats):
    n = len(recs)
    good = [r for r in recs if r["E"] is not None]
    return dict(n_statements=n, n_with_E=len(good), n_zero_cruxes=sum(1 for r in recs if r["n_cruxes"] == 0),
                n_missing_E=sum(1 for r in recs if r["extract_ok"] and r["n_cruxes"] != 0 and r["E"] is None)
                + sum(1 for r in recs if not r["extract_ok"]),
                mean_E=round(mean(r["E"] for r in good), 4) if good else None,
                n_E_ge_half=sum(1 for r in good if r["E"] >= HIDE_THRESHOLD),
                order_flips=sum(1 for r in recs if r["order_flip"]), order_checked=sum(1 for r in recs if r["order_flip"] is not None),
                **{k: v for k, v in stats.items()})


def new_stats():
    return dict(calls=0, errors=0, truncated=0, prompt_tokens=0, completion_tokens=0)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def dev_items(n_rounds, rounds):
    ks = sorted(rounds)
    random.Random(PROBE_SEED).shuffle(ks)
    return [dict(launch_id=k[0], round_id=k[1], cand=c) for k in ks[:n_rounds] for c in range(4)]


def gate_items():
    k = json.loads(KEY.read_text(encoding="utf-8"))
    ids = {}
    for it in k["items"]:
        ids.setdefault((it["launch_id"], it["round_id"], it["cand"]), []).append(it["item_id"])
    out = []
    for sect in ("shared", "L1_unique", "L2_unique"):
        for s in k["sample"][sect]:
            key = (s["launch_id"], s["round_id"], s["cand"])
            out.append(dict(launch_id=key[0], round_id=key[1], cand=key[2], item_ids=sorted(set(ids.get(key, [s["item_id"]]))), section=sect))
    assert len({(i["launch_id"], i["round_id"], i["cand"]) for i in out}) == 60, "gate sample must be 60 distinct statements"
    return out, k


async def execute(mode, args):
    alias = args.scorer
    provider = "mock" if mode == "mock" else "modal"
    out_dir = (RUNS / mode) if mode != "gate1" else RUNS / "gate1"
    if alias != "qwen3.8-27b" and mode != "mock":
        out_dir = RUNS / f"{mode}_{alias}"                 # scorer 2 never writes into scorer 1 folders
    out_dir.mkdir(parents=True, exist_ok=True)
    if mode in ("mock", "probe"):
        rounds = load_rounds(DEV_GROUPS)
        items = dev_items(args.n_rounds if mode == "mock" else PROBE_ROUNDS, rounds)
        order_check = mode == "mock"
        exp, cap = ("A1/A2-probe" if mode == "probe" else "mock"), (4.9 if alias != "qwen3.8-27b" else 1.5)
        if alias != "qwen3.8-27b":
            exp = "A4-V1-smoke"
    elif mode == "gate1":
        items, key = gate_items()
        rounds = load_rounds(ALL_GROUPS, {(i["launch_id"], i["round_id"]) for i in items})
        order_check, exp, cap = True, "A1", 1.0
    else:
        rounds = load_rounds(ALL_GROUPS)
        ks = sorted({k[0] for k in rounds})
        random.Random(RANDOM_PREFIX_SEED).shuffle(ks)
        rank = {l: i for i, l in enumerate(ks)}
        items = [dict(launch_id=k[0], round_id=k[1], cand=c) for k in sorted(rounds, key=lambda k: (rank[k[0]], k[1])) for c in range(4)]
        order_check, exp, cap = False, "A2", 5.2
    plans = make_plans(alias) if mode != "mock" else {}
    plan = plans.get({"probe": "probe", "gate1": "gate1", "all": "all_measured"}.get(mode, ""), None)
    approved = "n/a (mock, $0)"
    if provider == "modal":
        if not args.confirm_launch:
            raise SystemExit("REFUSED: Modal modes need --confirm-launch.")
        if not (PROMPTS / PROMPT_FILES["E1"]).exists():
            raise SystemExit("REFUSED: prompts not written.")
        verify_prompts()
        if plan["worst_case_usd"] > cap:
            raise SystemExit(f"REFUSED: worst case ${plan['worst_case_usd']} > job cap ${cap}")
        if plan["worst_case_usd"] > 5.0:
            ap = Path(args.approval_file) if args.approval_file else None
            if not ap or not ap.exists():
                raise SystemExit("REFUSED: worst case > $5 needs experiment-council approval file (BRIEF 8).")
            a = json.loads(ap.read_text(encoding="utf-8"))
            if not (a.get("approved") is True and a.get("approved_by") and float(a.get("max_usd", 0)) >= plan["worst_case_usd"]):
                raise SystemExit("REFUSED: approval file does not cover this plan.")
            approved = a["approved_by"]
        else:
            approved = "scorer runner (under $5, BRIEF 8; gate-1 scoring pre-authorised in D10)"
        ledger_row(f"scorer {mode} {alias} ({plan['calls']} calls est.)", exp, plan["gpu"], plan["worst_case_usd"], "",
                   plan["session_max_seconds"], approved,
                   f"ESTIMATE row before launch; expected ${plan['expected_usd']}, worst-case reservation ${plan['worst_case_usd']}; "
                   f"throughput ASSUMED (unmeasured); job cap ${cap}")
        BASELINE_IDS.update(re.findall(r"ta-[0-9A-Za-z]+", container_check().get("stdout_tail", "") or ""))
        llm = LLM(pilot="T3-1-core-tier2" if alias == "qwen3.8-27b" else f"T3-1-A4-{alias}", pilot_cap=10.0 if alias == "qwen3.8-27b" else 5.0, timeout_s=180.0, concurrency={"modal": 32})
    else:
        install_mock_responses()
        MOCK.latency_s = 0.002
        llm = LLM(pilot="scorer-mock", pilot_cap=1.0, ledger_path=out_dir / "mock_ledger.jsonl", cache_dir=out_dir / "mock_cache",
                  concurrency={"mock": 32})
    stats = new_stats()
    t0 = time.time()
    sess_info, cc = None, {}
    if mode == "gate1":
        SCORES.mkdir(exist_ok=True)
        sp, ep = SCORES / "gate1_scores.jsonl", SCORES / "gate1_extractions.jsonl"
    else:
        sp, ep = out_dir / "scores.jsonl", out_dir / "extractions.jsonl"
    done = read_done(sp)                                      # resume: completed statements are never redone
    sect = {(i["launch_id"], i["round_id"], i["cand"]): i.get("section") for i in items}
    todo = [i for i in items if (i["launch_id"], i["round_id"], i["cand"]) not in done]
    chunks = chunk_by_round(todo, CHUNK_ROUNDS)
    stats["chunks_total"], stats["chunks_done"], stats["resumed_statements"] = len(chunks), 0, len(done)

    async def run_chunks(deadline):
        for ch in chunks:
            left = deadline - time.time()
            if left <= 0:
                stats["stopped"] = "timeout before chunk"
                return
            cs = new_stats()
            try:
                recs, ext = await asyncio.wait_for(score_statements(llm, provider, alias, rounds, ch, order_check, cs), timeout=left)
            except asyncio.TimeoutError:
                stats["stopped"] = "timeout inside chunk (its calls stay in the harness cache; resume rebuilds it)"
                return
            for r in recs:
                if mode == "gate1":
                    r["section"] = sect[(r["launch_id"], r["round_id"], r["cand"])]
            append_jsonl(sp, recs)                            # incremental: one append per completed chunk
            append_jsonl(ep, ext)
            for k, v in cs.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    stats[k] = stats.get(k, 0) + v
                elif k == "stopped":
                    stats["stopped"] = v
            stats["chunks_done"] += 1
            if cs.get("stopped"):
                return
    try:
        if not chunks:
            pass
        elif provider == "modal":
            max_s = plan["session_max_seconds"]
            async with llm.modal_session(alias, max_seconds=max_s) as s:
                await run_chunks(time.time() + max_s - 5)
            sess_info = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
        else:
            await run_chunks(time.time() + 3600)
    finally:
        await llm.aclose()
        if provider == "modal" and chunks:
            cc = container_wait_empty(alias)
            (out_dir / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
            print("modal container check:", json.dumps({k: v for k, v in cc.items() if k != "stdout_tail"}))
    recs = list(read_done(sp).values())
    ext = [json.loads(l) for l in open(ep, encoding="utf-8")] if ep.exists() else []
    summ = summarise(recs, stats)
    summ.update(empty_side_cruxes_dropped_this_process=EMPTY_SIDE_DROPPED["n"])
    summ.update(mode=mode, scorer=alias, wall_s=round(time.time() - t0, 1), session=sess_info, plan=plan,
                prompt_sha256=verify_prompts(), thinking="off (enable_thinking=False) on modal", decoding=dict(
                    temperature=TEMPERATURE, seed=SEED, retry_seed=RETRY_SEED, max_tokens=dict(extract=MAX_TOK_EXTRACT, label=MAX_TOK_LABEL),
                    response_format="json_object"), container_check=cc, n_requested=len(items), complete=len(recs) == len(items))
    (out_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if provider == "modal" and sess_info:
        ledger_row(f"scorer {mode} {alias} ACTUAL", exp, plan["gpu"], "", sess_info["session_cost_usd"], plan["session_max_seconds"], approved,
                   f"ACTUAL list-price session cost; {stats['calls']} calls, wall {summ['wall_s']} s, container rows after run "
                   f"{cc.get('own_rows_final')}, waited {cc.get('waited_s')} s (stopped by id: {cc.get('stopped_by_id')}); cross-check modal billing report")
    if provider == "mock":
        from run_log import log_run
        log_run(__file__, "dummy", SEED, [DEV_GROUPS], out_dir, note=f"scorer mock dry-run {len(recs)} statements, $0, no Modal")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("plan",)}, indent=1, default=str))
    return summ


# ---------------------------------------------------------------- manifest
def write_manifest(args):
    ph = verify_prompts()
    smoke = None
    sp = RUNS / "probe" / "summary.json"
    if sp.exists():
        smoke = json.loads(sp.read_text(encoding="utf-8"))
    plans = make_plans()
    man = dict(
        status="FINAL for scorer v2 (E1 silence fix + empty-side crux drop); freezes with FROZEN_RULES.md. v2 is the scorer of record; v1 archived.",
        scorer_version="v2",
        v1_archive=dict(E1_sha256="65450760176c7ad4e79c9329664c2074f08df5c23db6098613c580b77228c0aa", dir="analysis/v1_archive/",
                        gate1_scores="analysis/scores/gate1_scores_v1.jsonl", gate1_scores_sha256=sha256_file(SCORES / "gate1_scores_v1.jsonl")
                        if (SCORES / "gate1_scores_v1.jsonl").exists() else None, probe="analysis/scorer_runs/probe_v1/"),
        v2_changes=["E1: one inserted passage - a crux needs members who explicitly take opposing positions; silence is not opposition (decisions.md D18/D19)",
                    "scorer.py parse_cruxes: a crux with an empty members_a or members_b is dropped and counted (FR 3 [R1], decisions.md D21); no-op on dev and gate extractions (0 empty-side cruxes)",
                    "scorer.py container_wait_empty: never stops containers that existed before launch (other sessions)"],
        gate1_v2_summary=json.loads((RUNS / "gate1" / "summary.json").read_text(encoding="utf-8")) if (RUNS / "gate1" / "summary.json").exists() else None,
        written_utc=utc(), script=str(Path(__file__).name), script_sha256=sha256_file(__file__),
        scorer1=dict(alias="qwen3.8-27b", **SCORERS["qwen3.8-27b"]), scorer2=dict(alias="gemma4-12b", **SCORERS["gemma4-12b"]),
        served_by="modal_serving/serve_vllm.py (vLLM v0.32.0 image, --max-model-len 16384)",
        decoding=dict(temperature=TEMPERATURE, seed=SEED, retry_seed=RETRY_SEED, max_tokens=dict(extract=MAX_TOK_EXTRACT, label=MAX_TOK_LABEL),
                      output="JSON; request carries response_format={type: json_object}; runs parsed with 0 extraction failures (dev v2 40 rounds, gate v2 60 rounds), so the setting was accepted",
                      thinking="off: chat_template_kwargs enable_thinking=False (as used in every v1 and v2 run; summaries record 'off')"),
        prompts_sha256=ph, frozen_rules_sha256=sha256_file(FROZEN) if FROZEN.exists() else None,
        all_groups_sha256=sha256_file(ALL_GROUPS), pilot_groups_sha256=sha256_file(DEV_GROUPS),
        key_json_sha256=sha256_file(KEY) if KEY.exists() else None,
        parse_rule="seed-0 call; on failure one retry with seed 1; still failing -> E missing (wrong prediction in gate 1)",
        implementation_choices=[
            "crux member lists are sanitised (ints within 1..n); a bad member list is NOT a parse failure",
            "more than 4 cruxes, a crux missing issue/side_a/side_b, or a label list of the wrong length/with unknown token = parse failure",
            "labels are matched case-insensitively after strip; no synonym is mapped",
            "a round whose prompt estimate (chars/2.5 + max_tokens) exceeds 16384 tokens is dropped and counted (none expected)",
            "the order-check pass (reversed crux list, sides A/B swapped) runs on gate items only and never replaces the score of record",
        ],
        cost_plans=plans, dev_probe_summary=smoke,
    )
    (HERE / "scorer_manifest.json").write_text(json.dumps(man, indent=1, default=str), encoding="utf-8")
    print("wrote scorer_manifest.json")
    return man


def selftest():
    n = 0

    def ok(c, msg):
        nonlocal n
        assert c, msg
        n += 1
    ph = verify_prompts()
    ok(len(ph) == 3, "three prompts hashed")
    row = dict(question="Q?", opinions={"b": "second {question}", "a": "first"})
    pr = build_extract_prompt(row)
    ok("1. first\n2. second {question}" in pr, "opinions sorted by participant id, numbered, no re-substitution")
    ok(pr.count("Q?") == 1, "question inserted once")
    try:
        build_extract_prompt(dict(question="Q", opinions={}, candidates=["x"]))
        ok(False, "extra column must be refused")
    except AssertionError:
        n += 1
    g = next(iter(load_rounds(DEV_GROUPS).values()))
    ok(not any(c[:40] in build_extract_prompt(dict(question=g["question"], opinions=g["opinions"])) for c in g["candidates"]), "no candidate text in extraction prompt")
    ok("raters" not in g, "raters dropped at load")
    cr = [dict(issue="i1", side_a="A1", side_b="B1", members_a=[1], members_b=[2]), dict(issue="i2", side_a="A2", side_b="B2", members_a=[3], members_b=[1])]
    lp = build_label_prompt("Q", cr, "STATEMENT")
    ok("1. i1 (Side A: A1 | Side B: B1)\n2. i2 (Side A: A2 | Side B: B2)" in lp and '"""STATEMENT"""' in lp, "label prompt filled")
    ok("{" not in lp.replace('{"labels"', ""), "no unfilled placeholder in label prompt")
    sw = swap_cruxes(cr)
    ok(sw[0]["issue"] == "i2" and sw[0]["side_a"] == "B2" and sw[0]["members_a"] == [1], "swap reverses list and swaps sides")
    ok(swap_cruxes(sw) == cr, "swap is an involution")
    ok(parse_cruxes('{"cruxes": []}', 5) == [], "empty cruxes valid")
    ok(parse_cruxes("junk", 5) is None and parse_cruxes('{"cruxes": [1]}', 5) is None, "bad cruxes rejected")
    ok(parse_cruxes(json.dumps({"cruxes": [dict(issue="i", side_a="a", side_b="b")] * 5}), 5) is None, ">4 cruxes rejected")
    ok(parse_cruxes('{"cruxes":[{"issue":"i","side_a":"a","side_b":"b","members_a":[1],"members_b":[]}]}', 5) == [], "empty-side crux dropped")
    ok(len(parse_cruxes('{"cruxes":[{"issue":"i","side_a":"a","side_b":"b","members_a":[1],"members_b":[2]}]}', 5)) == 1, "two-sided crux kept")
    ok(parse_cruxes('```json\n{"cruxes":[{"issue":"i","side_a":"a","side_b":"b","members_a":[1,9,"x"],"members_b":[2,"no"]}]}\n```', 5)[0]["members_a"] == [1], "members sanitised")
    ok(parse_labels('{"labels": ["visible", "SIDED"]}', 2) == ["VISIBLE", "SIDED"], "labels parsed")
    ok(parse_labels('{"labels": ["VISIBLE", "GOOD"]}', 2) is None and parse_labels('{"labels": ["VISIBLE"]}', 2) is None, "bad labels rejected")
    ok(erasure(["VISIBLE", "SIDED", "BLENDED", "OMITTED"]) == 0.75 and erasure(["VISIBLE"]) == 0.0 and erasure([]) is None, "E arithmetic")
    ok(ai_binary(0.5, 2, True) is True and ai_binary(0.49, 3, True) is False and ai_binary(None, 0, True) is False and ai_binary(None, 2, False) is None, "binary rule")
    ok(RETRY_SEED == 1 and SEED == 0 and TEMPERATURE == 0.0, "decoding constants")
    # container polling with a faked `modal container list` (no Modal call)
    global container_check, time
    real_cc, real_sleep, real_run = container_check, time.sleep, subprocess.run
    seq = iter(["| ta-AAA | ap-1 | pilot-vllm-qwen… |\n| ta-BBB | ap-2 | pilot-vllm-gemm… |", "| ta-BBB | ap-2 | pilot-vllm-gemm… |"])
    try:
        container_check = lambda: dict(returncode=0, stdout_tail=next(seq))
        time.sleep = lambda s: None
        res = container_wait_empty("qwen3.8-27b", max_wait_s=300)
        ok(res["own_rows_final"] == 0 and res["other_app_rows"] == 1 and res["stopped_by_id"] == [], "polls until own app gone, ignores other apps")
        calls = []
        container_check = lambda: dict(returncode=0, stdout_tail="| ta-AAA | ap-1 | pilot-vllm-qwen… |")
        subprocess.run = lambda cmd, **k: calls.append(cmd)
        res = container_wait_empty("qwen3.8-27b", max_wait_s=0)
        ok(res["stopped_by_id"] == ["ta-AAA"] and "-y" in calls[0], "bounded wait then stop own container by id")
    finally:
        container_check, time.sleep, subprocess.run = real_cc, real_sleep, real_run
    ch = chunk_by_round([dict(launch_id="l", round_id=str(r), cand=c) for r in range(5) for c in range(4)], 2)
    ok([len(c) for c in ch] == [8, 8, 4], "chunks hold whole rounds")
    print(f"selftest: {n} checks passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["prompts", "selftest", "mock", "plan", "manifest", "probe", "gate1", "all"])
    ap.add_argument("--scorer", default="qwen3.8-27b", choices=list(SCORERS))
    ap.add_argument("--n-rounds", type=int, default=20)
    ap.add_argument("--confirm-launch", action="store_true")
    ap.add_argument("--probe-rounds", type=int, default=None)
    ap.add_argument("--cold-start-s", type=float, default=None)
    ap.add_argument("--approval-file")
    a = ap.parse_args()
    global PROBE_ROUNDS, COLD_START_S
    if a.probe_rounds:
        PROBE_ROUNDS = a.probe_rounds
    COLD_START_S = a.cold_start_s
    if a.scorer != "qwen3.8-27b":
        os.environ["MODAL_ENDPOINTS"] = str(P / "serving" / "endpoints.json")       # vendored, additive endpoints (D36)
    if a.mode == "prompts":
        print(json.dumps(write_prompts(), indent=1))
    elif a.mode == "selftest":
        selftest()
    elif a.mode == "plan":
        RUNS.mkdir(exist_ok=True)
        pl = make_plans(a.scorer)
        (RUNS / "plan.json").write_text(json.dumps(pl, indent=1), encoding="utf-8")
        for k, v in pl.items():
            print(f"{k:20s} calls {v['calls']:6d} wall~{v['expected_wall_s']:5d}s timeout {v['session_max_seconds']:5d}s "
                  f"expected ${v['expected_usd']:.3f} worst ${v['worst_case_usd']:.3f}")
    elif a.mode == "manifest":
        write_manifest(a)
    else:
        asyncio.run(execute(a.mode, a))


if __name__ == "__main__":
    main()
