"""N2 grid runner: current open models write group statements from Habermas opinion sets.

Design (BRIEF 5 N2, council conditions in analysis/council/, spec in analysis/N2_ANALYSIS_SPEC.md):
system prompt {SAT keep everyone satisfied | ACC be accurate about differences | NEU neutral (COMMON only)}
x user prompt {COMMON find common ground | DIS show where they disagree}  = 5 cells, over a seeded sample
of rounds, over Modal-served models. This script GENERATES statements only. It never reads rankings or
labels and it refuses to score (see assert_scoring_allowed).

Modes (nothing here launches Modal unless --confirm-launch is also given):
  plan      build the seeded sample + per-job cost estimate, write plan.json, call no model.
  dry-run   full pipeline against the harness MOCK provider: $0, temp ledger + temp cache.
  priority  modal, ONLY the packet-selection job ids (labels_build/n2_packet_selection.json) for the models given; same gates as smoke.
  smoke     modal, rounds drawn OUTSIDE the N2 sample (excluded from analysis), >= 32 requests per model;
            measures throughput and writes the per-cell format report.
  launch    modal, full grid. Needs --approval-file bound to design_sha256 (and plan_sha256 if given)
            whenever the worst-case cost exceeds $5 (BRIEF 8, experiment council).
  score     ALWAYS refuses unless P/analysis/GATE1_PASSED.json exists with a scorer-manifest hash that matches.
Refusals (before any GPU wakes up): worst case > N2 cap $10; N2 committed spend + worst case > $10; no timeout;
--confirm-launch missing; analysis spec missing or its sha256 not logged in decisions.md.

Run:  C:/Users/intel/miniconda3/python.exe -I n2_grid.py --mode plan
"""
import argparse
import asyncio
import contextlib
import csv
import datetime
import hashlib
import itertools
import json
import random
import re
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE.parent
R = P.parent                                   # _apart_intel
HARNESS = R / "pilot_harness"
sys.path.insert(0, str(HARNESS))               # -I removes the script dir; add what we need explicitly
sys.path.insert(0, str(HERE))
os.environ["MODAL_ENDPOINTS"] = str(P / "serving" / "endpoints.json")   # vendored copy (D36): modal_serving is no longer edited
from budget import EXPERIMENT_CAPS_USD, BudgetExceeded  # noqa: E402
from llm import LLM, MOCK, modal_endpoints              # noqa: E402
from prices import modal_container_rate                 # noqa: E402

DATA = R / "pilots" / "T3_1" / "all_groups.jsonl"     # 1,960 eligible rounds (eligible_groups.json)
DEV_GROUPS = R / "pilots" / "T3_1" / "pilot_groups.jsonl"   # the 150 development launches' rounds
REF_SAMPLE = R / "pilots" / "T3_1" / "ref_sample.json"
SERVE = P / "serving" / "serve_vllm.py"        # vendored (D36)
SPEC = HERE / "N2_ANALYSIS_SPEC.md"
DECISIONS = P / "decisions.md"
GATE1_PASSED = HERE / "GATE1_PASSED.json"
SCORER_MANIFEST = HERE / "scorer_manifest.json"
DEFAULT_APPROVAL = HERE / "council" / "N2_APPROVAL.json"
OUT = HERE / "n2_runs"
N2_CAP = 15.0   # D36: N2 cap raised 10 -> 15 from the reserve (budget.py EXPERIMENT_CAPS_USD still says 10; the cap is enforced here via pilot_cap)
COUNCIL_THRESHOLD = 5.0                        # BRIEF section 8
MASTER_SEED = 20261115

# ---------------------------------------------------------------- prompts (the manipulation)
SYSTEM = {
    "SAT": ("You are a mediator helping a group reach a shared position. Write a statement that "
            "keeps every participant satisfied."),
    "ACC": ("You are a mediator helping a group understand itself. Write a statement that is "
            "accurate about the differences between participants' views."),
    "NEU": "You are a mediator helping a group. Write a statement for the group.",
}
USER_TASK = {
    "COMMON": "Write a single group statement that finds the common ground among these participants.",
    "DIS": "Write a single group statement that shows where these participants disagree.",
}
USER_FORMAT = "Use at most 150 words. Output only the statement, with no preamble."   # same in all cells
# 2x2 plus a NEUTRAL system arm under COMMON only (methodologist M1b; NEU-DIS omitted for cost)
CELLS = [(s, u) for s in ("SAT", "ACC") for u in ("COMMON", "DIS")] + [("NEU", "COMMON")]

# ---------------------------------------------------------------- models and cost assumptions
# Throughput and output length are ASSUMPTIONS until the smoke measures them (README: never measured).
MODELS = {
    "gemma4-12b":   dict(tok_per_s=450.0, cold_s=104.0, cold_measured=True),
    "qwen3.8-27b":  dict(tok_per_s=400.0, cold_s=106.0, cold_measured=True),
    # N2 extension generators (D36). Throughput/cold start are ASSUMPTIONS until each smoke measures them.
    "ministral3-14b": dict(tok_per_s=375.0, cold_s=99.0, cold_measured=True),
    "phi4-14b":       dict(tok_per_s=316.0, cold_s=73.0, cold_measured=True),
    "llama3.1-8b":    dict(tok_per_s=510.0, cold_s=191.0, cold_measured=True),
    "llama3.3-70b": dict(tok_per_s=150.0, cold_s=300.0, cold_measured=False),   # gated 403, untested
}
DEFAULT_MODELS = ["gemma4-12b", "qwen3.8-27b"]
EXPECTED_OUT_TOK = 250
MAX_TOKENS = 400
PREFILL_OVERHEAD = 1.15
SAFETY = 2.0
SESSION_CEILING_S = 5400.0
MIN_SESSION_S = 0.0           # --min-session-s: floor for first-ever cold starts of new aliases (cost cutter: startup_timeout 600 s)
TEMPERATURE = 0.7
TOP_P, TOP_K = 1.0, -1        # set explicitly (council M8); server runs --generation-config vllm
MIN_SMOKE_REQUESTS = 32       # cost cutter condition 1

# ---------------------------------------------------------------- outcome-blind format checks
# Regexes fixed BEFORE the smoke (skeptic F5). They look at text FORM only, never at content or scores.
RE_THINK = re.compile(r"</?think>|<\|channel\|?>|<\|think\|>|<\|?thought", re.I)
RE_REFUSAL = re.compile(r"\b(I (cannot|can't|can not|won't|am unable to)|I'm (sorry|unable)|I apologi[sz]e|"
                        r"as an AI|I do not feel comfortable)\b", re.I)
RE_PREAMBLE = re.compile(r"^\W*(here is|here['’]s|sure|certainly|of course|okay|ok,|as a mediator|group statement\b)", re.I)
FLAG_CELL_MAX = 0.10          # a cell with > 10% flagged outputs: fix and re-smoke
DUP_JACCARD = 0.80            # mean pairwise word-set Jaccard across a round's cells above this = near-duplicate round
DUP_ROUND_MAX = 0.50          # more than half the rounds near-duplicate: prompts ignored, stop


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def sub_seed(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) % (2 ** 31)


# ---------------------------------------------------------------- scoring guard (council M12; condition f)
R5_SCORING_STATUSES = frozenset({"VALIDATED_BOTH", "VALIDATED_PRESENCE", "VALIDATED_HIDE_EVIDENCE", "EXPLORATORY_UNVALIDATED"})


def assert_scoring_allowed():
    """The ONLY way to score N2 text. Refuses unless gate 1 is recorded as PASS (or, under R5, with "rules": "R5" and a
    status in R5_SCORING_STATUSES; FAIL/NOT_EVALUATED/anything else refused) and the scorer manifest
    on disk is the one gate 1 was run against (hash match). n2_grid.py itself contains no scorer."""
    if not GATE1_PASSED.exists():
        raise SystemExit(f"REFUSED (BRIEF 3.3): {GATE1_PASSED} does not exist; N2 outputs stay unscored.")
    if not SCORER_MANIFEST.exists():
        raise SystemExit(f"REFUSED: {SCORER_MANIFEST} does not exist.")
    g = json.loads(GATE1_PASSED.read_text(encoding="utf-8"))
    if g.get("rules") == "R5":     # D56: a recorded R5 status (FROZEN_RULES 6.R5.6); N2 stays EXPLORATORY (6.R5.7)
        if g.get("status") not in R5_SCORING_STATUSES:
            raise SystemExit(f"REFUSED: R5 gate status is {g.get('status')!r}, not one of {sorted(R5_SCORING_STATUSES)}.")
    elif g.get("status", "PASS") != "PASS":
        raise SystemExit(f"REFUSED: gate 1 status is {g.get('status')!r}, not PASS.")
    want, have = g.get("scorer_manifest_sha256"), sha256_file(SCORER_MANIFEST)
    if not want or want != have:
        raise SystemExit("REFUSED: scorer manifest hash does not match GATE1_PASSED.json.")
    return g


# ---------------------------------------------------------------- sample
def _load_groups():
    by_q = {}
    for line in open(DATA, encoding="utf-8"):
        g = json.loads(line)
        by_q.setdefault(g["question_id"], []).append(g)
    return by_q


def draw_rounds(n_rounds, seed):
    """Seeded sample: one round per distinct question, then the first n_rounds of a seeded shuffle.
    NOTE (methodologist M4): rounds can share a launch (250 rounds sit in 231 launches); the analysis
    clusters on launch. Rounds are never chosen by any outcome, ranking or score."""
    by_q = _load_groups()
    rng = random.Random(f"N2-sample|{seed}")
    qs = sorted(by_q)
    rng.shuffle(qs)
    picked = []
    for q in qs[:n_rounds]:
        cands = sorted(by_q[q], key=lambda g: g["round_id"])
        picked.append(cands[rng.randrange(len(cands))])
    return picked


def draw_smoke_rounds(n, seed):
    """Smoke rounds sit OUTSIDE the N2 sample: other questions AND other launches than the main 250,
    preferring the development launches. Excluded from every N2 analysis (methodologist M10)."""
    main = draw_rounds(250, seed)
    bad_q = {g["question_id"] for g in main}
    bad_l = {g["launch_id"] for g in main}
    dev_l = {json.loads(l)["launch_id"] for l in open(DEV_GROUPS, encoding="utf-8")}
    pool = [g for qs in _load_groups().values() for g in qs
            if g["question_id"] not in bad_q and g["launch_id"] not in bad_l]
    rng = random.Random(f"N2-smoke|{seed}")
    pool.sort(key=lambda g: g["round_id"])
    rng.shuffle(pool)
    pool.sort(key=lambda g: g["launch_id"] not in dev_l)   # stable: development launches first
    out, seen = [], set()
    for g in pool:
        if g["question_id"] in seen:
            continue
        seen.add(g["question_id"])
        out.append(g)
        if len(out) == n:
            break
    return out


def ref_overlap(rounds):
    try:
        txt = REF_SAMPLE.read_text(encoding="utf-8")
    except OSError:
        return None
    return sum(1 for g in rounds if g["round_id"] in txt)


def build_messages(g, cell, seed):
    s, u = cell
    ops = list(g["opinions"].items())
    random.Random(f"order|{seed}|{g['round_id']}").shuffle(ops)    # same order in all cells (paired)
    body = "\n\n".join(f"Participant {i + 1}: {t.strip()}" for i, (_, t) in enumerate(ops))
    user = f"Question: {g['question']}\n\nOpinions:\n\n{body}\n\n{USER_TASK[u]} {USER_FORMAT}"
    return [{"role": "system", "content": SYSTEM[s]}, {"role": "user", "content": user}]


def msg_hash(messages):
    return hashlib.sha256(json.dumps(messages, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def serving_info(models):
    """Pinned revision + serving config per alias (council M8). Parsed from serve_vllm.py; no secrets."""
    src = SERVE.read_text(encoding="utf-8")
    img = re.search(r'VLLM_IMAGE\s*=\s*"([^"]+)"', src)
    eps = modal_endpoints()
    info = {}
    for m in models:
        mm = re.search(r'"%s":\s*dict\(\s*repo="([^"]+)",\s*revision="([0-9a-f]{40})"' % re.escape(m), src)
        if not mm:
            raise SystemExit(f"cannot read pinned revision for {m} from serve_vllm.py")
        e = eps[m]
        info[m] = dict(repo=mm.group(1), revision=mm.group(2), gpu=e["gpu"], n_gpu=e.get("n_gpu", 1), cpu=e.get("cpu"),
                       memory_mib=e.get("memory_mib"), scaledown_s=e.get("scaledown_s"), dtype="bf16 full weights",
                       server_flags="--generation-config vllm --max-logprobs 20 --enforce-eager (+ per-model parser flags)")
    return dict(models=info, vllm_image=img.group(1) if img else None, serve_vllm_sha256=sha256_file(SERVE))


def build_jobs(rounds, models, k, seed, serving):
    jobs = []
    for model in models:
        src = f"model:{serving['models'][model]['repo']}@{serving['models'][model]['revision']}"
        for g in rounds:
            for cell in CELLS:
                msgs = build_messages(g, cell, seed)
                for si in range(k):
                    jid = f"{model}|{g['round_id']}|{cell[0]}-{cell[1]}|{si}"
                    jobs.append(dict(job_id=jid, model=model, round_id=g["round_id"], question_id=g["question_id"],
                                     launch_id=g["launch_id"], sys_prompt=cell[0], user_prompt=cell[1], sample=si,
                                     seed=sub_seed(seed, jid), messages=msgs, msg_sha256=msg_hash(msgs), source=src))
    return jobs


# ---------------------------------------------------------------- cost estimate (logged before launch)
def estimate(models, n_rounds, k, overrides, rounds_by_model=None, gens_by_model=None):
    per, tot_exp, tot_worst, tot_gpu_s = {}, 0.0, 0.0, 0.0
    eps = modal_endpoints()
    for m in models:
        nr = (rounds_by_model or {}).get(m, n_rounds)
        ep, a = eps[m], dict(MODELS[m])
        a.update(overrides.get(m, {}))
        rate = modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)),
                                    float(ep.get("memory_mib", 0)) / 1024)
        tail = float(ep["scaledown_s"]) + 15.0
        gens = (gens_by_model or {}).get(m, nr * len(CELLS) * k)
        decode_s = gens * EXPECTED_OUT_TOK / a["tok_per_s"] * PREFILL_OVERHEAD
        wall = decode_s + a["cold_s"]
        max_s = max(MIN_SESSION_S, min(SESSION_CEILING_S, round(SAFETY * wall)))
        exp_usd = rate * (wall + tail)
        worst = rate * (max_s + tail)            # session reservation = rate x (max_seconds + tail)
        gpu_s = int(ep.get("n_gpu", 1)) * (wall + tail)
        per[m] = dict(gpu=f"{ep['gpu']}x{ep.get('n_gpu', 1)}", rate_usd_per_s=round(rate, 9), rounds=nr, generations=gens,
                      assumed_tok_per_s=a["tok_per_s"], cold_s=a["cold_s"], cold_measured=a["cold_measured"],
                      expected_wall_s=round(wall), tail_s=tail, session_max_seconds=max_s,
                      expected_gpu_seconds=round(gpu_s), expected_usd=round(exp_usd, 3), worst_case_usd=round(worst, 3))
        tot_exp += exp_usd
        tot_worst += worst
        tot_gpu_s += gpu_s
    return per, dict(expected_usd=round(tot_exp, 3), worst_case_usd=round(tot_worst, 3),
                     expected_gpu_seconds=round(tot_gpu_s))


def _hash(core):
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()


def make_plan(args):
    smoke = args.mode == "smoke"
    rounds = draw_smoke_rounds(args.n_rounds, args.seed) if smoke else draw_rounds(args.n_rounds, args.seed)
    overrides = {}
    for kv in args.tok_per_s or []:
        m, v = kv.split("=")
        overrides[m] = dict(tok_per_s=float(v))
    rbm = {}
    for kv in args.rounds_for or []:
        m, v = kv.split("=")
        rbm[m] = int(v)
    gbm = None
    if args.mode == "priority":     # only the packet-selection ids (decisions D36 speed-up); ids fixed before any text exists
        pri = json.loads(Path(args.priority_file).read_text(encoding="utf-8"))["items"]
        gbm = {}
        for it in pri:
            if it["generator"] in args.models:
                gbm[it["generator"]] = gbm.get(it["generator"], 0) + 1
        args.models = [m for m in args.models if m in gbm]
        args.priority_ids = {it["job_id"] for it in pri}
    per, tot = estimate(args.models, args.n_rounds, args.k, overrides, rbm, gbm)
    serving = serving_info(args.models)
    # DESIGN = what the council approves (hash independent of cost/throughput assumptions)
    design = dict(seed=args.seed, n_rounds=args.n_rounds, k=args.k, models=args.models, rounds_by_model=rbm,
                  cells=[f"{s}-{u}" for s, u in CELLS], temperature=TEMPERATURE, top_p=TOP_P, top_k=TOP_K,
                  max_tokens=MAX_TOKENS, thinking="off (chat_template_kwargs.enable_thinking=false)",
                  system=SYSTEM, user_task=USER_TASK, user_format=USER_FORMAT, serving=serving,
                  data_sha256=sha256_file(DATA),
                  round_ids_sha256=hashlib.sha256(",".join(g["round_id"] for g in rounds).encode()).hexdigest(),
                  smoke_outside_n2_sample=smoke,
                  analysis_spec_sha256=sha256_file(SPEC) if SPEC.exists() else None)
    core = dict(design, assumptions=dict(expected_out_tok=EXPECTED_OUT_TOK, prefill_overhead=PREFILL_OVERHEAD,
                                         safety=SAFETY, tok_per_s_overrides=overrides))
    plan = dict(core, design_sha256=_hash(design), plan_sha256=_hash(core), per_model=per, totals=tot, n2_cap_usd=N2_CAP,
                council_threshold_usd=COUNCIL_THRESHOLD, ref_sample_overlap=ref_overlap(rounds),
                dev_launch_rounds=sum(1 for g in rounds if g["launch_id"] in
                                      {json.loads(l)["launch_id"] for l in open(DEV_GROUPS, encoding="utf-8")}),
                n_launches=len({g["launch_id"] for g in rounds}),
                utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    return plan, rounds, serving


def check_gates(plan, args):
    """Refuse BEFORE any GPU wakes up."""
    worst = plan["totals"]["worst_case_usd"]
    if worst > N2_CAP:
        raise SystemExit(f"REFUSED: worst case ${worst:.2f} > N2 cap ${N2_CAP:.2f}. Reduce n/k/models.")
    for m, v in plan["per_model"].items():
        if not v["session_max_seconds"] > 0:
            raise SystemExit(f"REFUSED: no timeout for {m}")
    if args.mode in ("smoke", "launch", "priority"):
        if not args.confirm_launch:
            raise SystemExit("REFUSED: modal modes need --confirm-launch.")
        if args.mode == "smoke" and args.n_rounds * len(CELLS) * args.k < MIN_SMOKE_REQUESTS:
            raise SystemExit(f"REFUSED: smoke needs >= {MIN_SMOKE_REQUESTS} requests per model.")
        if not SPEC.exists():
            raise SystemExit("REFUSED: analysis/N2_ANALYSIS_SPEC.md missing.")
        if sha256_file(SPEC) not in DECISIONS.read_text(encoding="utf-8", errors="replace"):
            raise SystemExit("REFUSED: sha256 of N2_ANALYSIS_SPEC.md is not logged in decisions.md.")
        led = LLM(pilot="N2", pilot_cap=N2_CAP)
        try:
            committed = led.budget._committed("N2")
        finally:
            led.budget.close()
        if committed + worst > N2_CAP:
            raise SystemExit(f"REFUSED: N2 committed ${committed:.2f} + worst case ${worst:.2f} > cap ${N2_CAP:.2f}")
        if args.mode == "launch" or worst > COUNCIL_THRESHOLD:
            ap = Path(args.approval_file) if args.approval_file else DEFAULT_APPROVAL
            if not ap.exists():
                raise SystemExit(f"REFUSED: needs experiment-council approval file ({ap}).")
            a = json.loads(ap.read_text(encoding="utf-8"))
            ok = (a.get("approved") is True and a.get("design_sha256", plan["design_sha256"]) == plan["design_sha256"]
                  and a.get("plan_sha256", plan["plan_sha256"]) == plan["plan_sha256"]
                  and ("design_sha256" in a or "plan_sha256" in a)
                  and float(a.get("max_usd", 0)) >= worst and a.get("approved_by"))
            if not ok:
                raise SystemExit("REFUSED: approval file does not match this plan (design/plan hash, max_usd, approved_by).")
            return a["approved_by"]
        return "orchestrator (smoke, worst case under $5, BRIEF 8)"
    return "n/a (no spend)"


def _last_cumulative():
    path, last = P / "ledger.csv", 0.0
    for row in csv.reader(open(path, encoding="utf-8")):
        try:
            last = float(row[7])
        except (IndexError, ValueError):
            pass
    return last


def log_estimate_row(plan, approved_by, tag):
    """COSTS.md rule: one ledger.csv row with estimate + timeout + approver BEFORE the job launches."""
    with open(P / "ledger.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for m, v in plan["per_model"].items():
            w.writerow([plan["utc"], f"N2 grid {tag} {m} ({v['generations']} gens) ESTIMATE", "N2", "modal", v["gpu"],
                        v["worst_case_usd"], "", "", v["session_max_seconds"], approved_by,
                        f"written before launch; expected ${v['expected_usd']}, worst case (reservation) "
                        f"${v['worst_case_usd']}; design {plan['design_sha256'][:12]} plan {plan['plan_sha256'][:12]}"])


def log_actual_rows(plan, results, tag):
    cum = _last_cumulative()
    with open(P / "ledger.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in results:
            s = r.get("session")
            if not s:
                continue
            cum += s["session_cost_usd"]
            w.writerow([datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                        f"N2 grid {tag} {r['model']} ACTUAL", "N2", "modal", plan["per_model"][r["model"]]["gpu"], "",
                        round(s["session_cost_usd"], 4), round(cum, 4), plan["per_model"][r["model"]]["session_max_seconds"],
                        "", f"harness list price (incl. cold start {s['cold_start_s']} s, billed {s['billed_s']} s); "
                            f"{r['run']} gens, {r['errors']} errors; cross-check with modal billing report"])


# ---------------------------------------------------------------- format report (text FORM only, no scoring)
def _words(t):
    return set(re.findall(r"\w+", t.lower()))


def format_report(out_dir, models):
    rows = []
    for m in models:
        rows += list(load_done(out_dir / f"gens_{m}.jsonl").values())
    rep = {"cells": {}, "near_duplicate": {}}
    for m in models:
        for cell in sorted({(r["sys_prompt"], r["user_prompt"]) for r in rows}):
            rs = [r for r in rows if r["model"] == m and (r["sys_prompt"], r["user_prompt"]) == cell]
            if not rs:
                continue
            n = len(rs)
            c = dict(n=n,
                     empty=sum(1 for r in rs if not r["text"].strip()),
                     truncated=sum(1 for r in rs if r["truncated"]),
                     think_tag_leak=sum(1 for r in rs if RE_THINK.search(r["text"])),
                     reasoning_content_present=sum(1 for r in rs if r.get("reasoning_content_present")),
                     refusal_or_meta=sum(1 for r in rs if RE_REFUSAL.search(r["text"])),
                     preamble=sum(1 for r in rs if RE_PREAMBLE.search(r["text"][:80])),
                     mean_words=round(sum(r["n_words"] for r in rs) / n, 1))
            bad = max(c["empty"], c["truncated"], c["think_tag_leak"], c["refusal_or_meta"], c["preamble"])
            c["max_flagged_share"] = round(bad / n, 3)
            c["fix_and_resmoke"] = bad / n > FLAG_CELL_MAX
            rep["cells"][f"{m}|{cell[0]}-{cell[1]}"] = c
        by_round = {}
        for r in rows:
            if r["model"] == m and r["sample"] == 0:
                by_round.setdefault(r["round_id"], []).append(_words(r["text"]))
        dup = []
        for ws in by_round.values():
            pairs = [len(a & b) / max(1, len(a | b)) for a, b in itertools.combinations(ws, 2)]
            dup.append(sum(pairs) / len(pairs) > DUP_JACCARD if pairs else False)
        share = sum(dup) / len(dup) if dup else 0.0
        rep["near_duplicate"][m] = dict(rounds=len(dup), near_duplicate_share=round(share, 3), stop=share > DUP_ROUND_MAX)
    rep["any_fix_and_resmoke"] = any(c["fix_and_resmoke"] for c in rep["cells"].values())
    rep["any_dead_manipulation"] = any(v["stop"] for v in rep["near_duplicate"].values())
    return rep


# ---------------------------------------------------------------- execution
def load_done(path):
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done[r["job_id"]] = r
            except (json.JSONDecodeError, KeyError):
                pass            # torn last line
    return done


async def run_model(llm, provider, model, jobs, out_path, per, args, sem_models):
    async with sem_models:
        done = load_done(out_path)
        todo = [j for j in jobs if j["job_id"] not in done]
        stats = dict(model=model, total=len(jobs), cached_in_file=len(done), run=0, errors=0, truncated=0,
                     cost_usd=0.0, out_tokens=0, session=None)
        if not todo:
            return stats
        sess = llm.modal_session(model, max_seconds=per["session_max_seconds"]) if provider == "modal" \
            else contextlib.nullcontext()
        extra = {"top_p": TOP_P, "top_k": TOP_K}
        if provider == "modal":
            extra["chat_template_kwargs"] = {"enable_thinking": False}
        async with sess as s:
            t_gen0 = time.time()
            if provider == "modal":
                stats["cold_start_s"] = s.cold_start_s
            for b in range(0, len(todo), args.batch_size):
                batch = todo[b:b + args.batch_size]
                req = [dict(provider=provider, model=model, messages=j["messages"], max_tokens=MAX_TOKENS,
                            temperature=TEMPERATURE, seed=j["seed"], sample_idx=j["sample"], extra=extra) for j in batch]
                try:
                    res = await asyncio.wait_for(llm.run_many(req), timeout=args.batch_timeout_s)
                except asyncio.TimeoutError:
                    stats["stopped"] = f"batch timeout {args.batch_timeout_s}s"
                    print(f"[{model}] STOP: {stats['stopped']}")
                    break
                n_err = 0
                with open(out_path, "a", encoding="utf-8") as f:
                    for j, r in zip(batch, res):
                        if isinstance(r, Exception):
                            n_err += 1
                            stats["errors"] += 1
                            stats.setdefault("error_kinds", {})
                            k_ = type(r).__name__
                            stats["error_kinds"][k_] = stats["error_kinds"].get(k_, 0) + 1
                            if isinstance(r, BudgetExceeded):
                                stats["stopped"] = "budget/timeout: " + str(r)[:120]
                            continue
                        trunc = r.get("finish_reason") == "length"
                        stats["truncated"] += trunc
                        stats["cost_usd"] += r["cost_usd"]
                        if not r.get("cached"):
                            stats["out_tokens"] += r["usage"]["out"]
                        msg0 = ((r.get("raw") or {}).get("choices") or [{}])[0].get("message") or {}
                        f.write(json.dumps(dict(
                            job_id=j["job_id"], model=model, source=j["source"], round_id=j["round_id"],
                            question_id=j["question_id"], launch_id=j["launch_id"], sys_prompt=j["sys_prompt"],
                            user_prompt=j["user_prompt"], sample=j["sample"], seed=j["seed"], msg_sha256=j["msg_sha256"],
                            temperature=TEMPERATURE, top_p=TOP_P, top_k=TOP_K, thinking="off",
                            text=r["text"].strip(), n_words=len(r["text"].split()),
                            finish_reason=r.get("finish_reason"), truncated=trunc, usage=r["usage"],
                            reasoning_content_present=bool(msg0.get("reasoning_content") or msg0.get("reasoning")),
                            cached=r.get("cached", False), latency_s=r.get("latency_s")), ensure_ascii=False) + "\n")
                        stats["run"] += 1
                if n_err / len(batch) > args.max_error_rate or stats.get("stopped"):
                    stats["stopped"] = stats.get("stopped") or f"error rate {n_err}/{len(batch)} > {args.max_error_rate}"
                    print(f"[{model}] STOP: {stats['stopped']}")
                    break
            gen_s = time.time() - t_gen0
        stats["gen_wall_s"] = round(gen_s, 1)
        if stats["out_tokens"] and gen_s > 0:
            stats["measured_tok_per_s"] = round(stats["out_tokens"] / gen_s, 1)
            stats["mean_out_tokens"] = round(stats["out_tokens"] / max(1, stats["run"]), 1)
        if provider == "modal":
            stats["session"] = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
        return stats


async def amain(args):
    plan, rounds, serving = make_plan(args)
    tag = args.tag or {"plan": "plan", "dry-run": "dryrun_mock", "smoke": "smoke", "launch": "full", "priority": "full_ext"}[args.mode]
    out_dir = OUT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ("plan_priority.json" if args.mode == "priority" else "plan.json")).write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print(f"PLAN {tag}: {args.n_rounds} rounds ({plan['n_launches']} launches) x {len(CELLS)} cells x k={args.k} x models "
          f"{args.models}\n  design_sha256 {plan['design_sha256']}\n  plan_sha256   {plan['plan_sha256']}")
    for m, v in plan["per_model"].items():
        print(f"  {m:14s} {v['generations']:5d} gens  {v['gpu']:8s} wall~{v['expected_wall_s']:5d}s  GPU-s~{v['expected_gpu_seconds']:5d}  "
              f"expected ${v['expected_usd']:.3f}  worst ${v['worst_case_usd']:.3f}  timeout {v['session_max_seconds']}s "
              f"(assumed {v['assumed_tok_per_s']:.0f} tok/s)")
    print(f"  TOTAL expected ${plan['totals']['expected_usd']:.3f}  worst-case ${plan['totals']['worst_case_usd']:.3f}  "
          f"GPU-s {plan['totals']['expected_gpu_seconds']}  (N2 cap ${N2_CAP:.0f}; council needed above ${COUNCIL_THRESHOLD:.0f})")
    approved_by = check_gates(plan, args)
    if args.mode == "plan":
        return
    provider = "mock" if args.mode == "dry-run" else "modal"
    if provider == "modal":
        log_estimate_row(plan, approved_by, tag)       # BEFORE launch
        llm = LLM(pilot="N2", pilot_cap=N2_CAP, timeout_s=args.request_timeout_s,
                  concurrency={"modal": args.max_parallel_requests})
    else:
        MOCK.latency_s, MOCK.out_tokens = 0.005, 60
        llm = LLM(pilot="N2-dryrun", pilot_cap=N2_CAP, ledger_path=out_dir / "mock_ledger.jsonl",
                  cache_dir=out_dir / "mock_cache", timeout_s=args.request_timeout_s,
                  concurrency={"mock": args.max_parallel_requests})
    jobs_all = build_jobs(rounds, args.models, args.k, args.seed, serving)
    sem = asyncio.Semaphore(max(1, min(args.max_parallel_models, len(args.models))))
    t0 = time.time()
    try:
        results = await asyncio.gather(*(
            run_model(llm, provider, m, ([j for j in jobs_all if j["model"] == m and j["job_id"] in args.priority_ids] if args.mode == "priority"
                                          else [j for j in jobs_all if j["model"] == m][: plan["per_model"][m]["generations"]]),
                      out_dir / f"gens_{m}.jsonl", plan["per_model"][m], args, sem) for m in args.models))
    finally:
        spent = llm.stats["spent_usd"]
        await llm.aclose()
    fmt = format_report(out_dir, args.models)
    summ = dict(tag=tag, provider=provider, wall_s=round(time.time() - t0, 1), per_model=results, harness_spent_usd=round(spent, 4),
                design_sha256=plan["design_sha256"], plan_sha256=plan["plan_sha256"], format_report=fmt)
    (out_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=1, default=str))
    if provider == "modal":
        log_actual_rows(plan, results, tag)
    from run_log import log_run
    log_run(__file__, "dummy" if provider == "mock" else "real-generation", args.seed, [DATA, SPEC], out_dir,
            note=f"N2 {args.mode} {provider}: {args.n_rounds} rounds x {len(CELLS)} cells x k={args.k}, design {plan['design_sha256'][:12]}; "
                 f"generation only, no scoring, spend ${spent:.4f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["plan", "dry-run", "smoke", "launch", "priority", "score"], default="plan")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS, choices=sorted(MODELS))
    ap.add_argument("--n-rounds", type=int, default=None, help="default 250 (launch/plan), 8 (smoke), 12 (dry-run)")
    ap.add_argument("--k", type=int, default=None, help="samples per cell per round; default 2 (launch/plan), 1 otherwise")
    ap.add_argument("--seed", type=int, default=MASTER_SEED)
    ap.add_argument("--rounds-for", nargs="*", help="per-model round cap, e.g. llama3.3-70b=100")
    ap.add_argument("--tok-per-s", nargs="*", help="override assumed throughput, e.g. gemma4-12b=900 (from smoke)")
    ap.add_argument("--min-session-s", type=float, help="floor for session timeout (default 0)")
    ap.add_argument("--safety", type=float, help="session timeout = safety x expected wall (default 2.0)")
    ap.add_argument("--expected-out-tok", type=int, help="planning mean output tokens (default 250; smoke measured 145-176)")
    ap.add_argument("--prefill-overhead", type=float, help="decode-time multiplier (default 1.15; 1.0 when --tok-per-s is a measured end-to-end rate)")
    ap.add_argument("--max-parallel-requests", type=int, default=32, help="in-flight requests per model (harness max 32)")
    ap.add_argument("--max-parallel-models", type=int, default=1, help="models (= separate Modal containers) running at once")
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--request-timeout-s", type=float, default=180.0)
    ap.add_argument("--batch-timeout-s", type=float, default=900.0)
    ap.add_argument("--max-error-rate", type=float, default=0.2, help="stop a model if a batch exceeds this error rate")
    ap.add_argument("--approval-file", help=f"experiment-council approval JSON (default {DEFAULT_APPROVAL})")
    ap.add_argument("--confirm-launch", action="store_true", help="required for smoke/launch (paid)")
    ap.add_argument("--priority-file", default=str(P / "labels_build" / "n2_packet_selection.json"))
    ap.add_argument("--tag")
    args = ap.parse_args()
    if args.mode == "score":
        assert_scoring_allowed()
        raise SystemExit("gate 1 PASS and manifest hash match, but no N2 scorer is wired into this script by design; "
                         "scoring lives in the frozen scorer scripts and must call assert_scoring_allowed().")
    global EXPECTED_OUT_TOK, PREFILL_OVERHEAD, SAFETY, MIN_SESSION_S
    MIN_SESSION_S = args.min_session_s or 0.0
    if args.safety:
        SAFETY = args.safety
    if args.expected_out_tok:
        EXPECTED_OUT_TOK = args.expected_out_tok
    if args.prefill_overhead:
        PREFILL_OVERHEAD = args.prefill_overhead
    if args.n_rounds is None:
        args.n_rounds = {"smoke": 8, "dry-run": 12}.get(args.mode, 250)
    if args.k is None:
        args.k = 1 if args.mode in ("smoke", "dry-run") else 2
    if args.max_parallel_requests > 32:
        raise SystemExit("harness caps modal concurrency at 32")
    asyncio.run(amain(args))


if __name__ == "__main__":
    main()
