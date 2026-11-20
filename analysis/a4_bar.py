"""A4 scorer-2 validity bar, FROZEN_RULES.md 6.9 [R4] (decisions.md D36).  CODE ONLY until labels exist.

Subcommands (python -I a4_bar.py <cmd> ...):
  v1    technical bar on the DEVELOPMENT smoke: >= 200 calls, development launches only, statements left without E <= 5%.
        Reads only scorer output (scores.jsonl, summary.json) and pilot_groups.jsonl launch ids. Safe to run now.
  draw  the seeded V3 sample (FR 6.9 'Scope', rng = random.Random(20261133)): 250 non-development launches, one eligible
        round each, 4 candidates = 1,000 statements. Writes ids only (no scores read).
  v2    scorer 2's own balanced accuracy on the 38 original gate items against the labels of record: gate1.gate_frame +
        gate1.ba_block, i.e. the same binarisation (E >= 0.5; zero cruxes = negative; missing E = wrong), the same bootstrap
        (B = 10,000, default_rng(20261116)) and the same pass rule (2.5th-percentile bound > 0.5). NEEDS LABELS: refuses
        to run unless --labels-of-record is given; never reads a label file by default.
  v3    agreement with scorer 1 on the sample: Cohen's kappa of the binary calls and Spearman of E over statements where both
        found >= 1 crux, each with a launch-cluster percentile bootstrap interval (B = 10,000, default_rng(20261121)).
        Reference line kappa >= 0.40 changes WORDING only, never the membership of scorer 2.
Interpretation flagged for the planning room: FR 6.9 says "launch-cluster interval (section 7 method of record)". The method of
record (wild cluster bootstrap-t) is defined for a regression coefficient; kappa and Spearman have no regression form, so the
interval used here is the nonparametric launch-cluster percentile bootstrap with the stated seed. Logged, not hidden.

Outputs are written new-only (never overwritten). A4_BAR.json with the gate record is assembled from these by the planning room.
"""
import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
P = HERE.parent
DEV_FILE = P.parent / "pilots" / "T3_1" / "pilot_groups.jsonl"
HIDE = 0.5
B = 10000
SEED_V3 = 20261121
SEED_DRAW = 20261133
MIN_CALLS, MAX_MISSING = 200, 0.05
KAPPA_REF = 0.40


def rd(path):
    return [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]


def dev_ids():
    return {json.loads(x)["launch_id"] for x in open(DEV_FILE, encoding="utf-8") if x.strip()}


def write_new(path, obj):
    path = Path(path)
    if path.exists():
        sys.exit(f"REFUSED: {path} exists; outputs are write-once")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def is_missing(r):
    """After the one retry: no E although the round has (or may have) cruxes. Zero cruxes is a valid negative, not missing."""
    if not r["extract_ok"]:
        return True
    return r["n_cruxes"] != 0 and r["E"] is None


# ---------------------------------------------------------------- V1
def v1(a):
    sc = rd(Path(a.smoke_dir) / "scores.jsonl")
    sm = json.loads((Path(a.smoke_dir) / "summary.json").read_text(encoding="utf-8"))
    dev = dev_ids()
    n = len(sc)
    miss = sum(1 for r in sc if is_missing(r))
    non_dev = sorted({r["launch_id"] for r in sc} - dev)
    calls = int(sm.get("calls", 0))
    res = dict(bar="V1", scorer=sm.get("scorer"), calls=calls, calls_ok=calls >= MIN_CALLS, statements=n, missing_E=miss,
               missing_rate=round(miss / n, 4) if n else None, max_allowed=MAX_MISSING,
               extract_parse_fail_final=sm.get("parse_fail_final_extract"), label_parse_fail_final=sm.get("parse_fail_final_label"),
               zero_crux_statements=sum(1 for r in sc if r["n_cruxes"] == 0), non_development_launches_in_smoke=non_dev,
               development_only=not non_dev)
    res["V1_met"] = bool(res["calls_ok"] and res["development_only"] and n and miss / n <= MAX_MISSING)
    print(json.dumps(res, indent=1))
    if a.out:
        write_new(a.out, res)


# ---------------------------------------------------------------- draw (ids only)
def draw(a):
    sc = rd(a.scores1)                                   # scorer 1's file is used only for the id universe (launch, round)
    dev = dev_ids()
    rounds = {}
    for r in sc:
        if r["launch_id"] not in dev:
            rounds.setdefault(r["launch_id"], set()).add(r["round_id"])
    rng = random.Random(SEED_DRAW)
    S = rng.sample(sorted(rounds), 250)
    pick = [(l, rng.choice(sorted(rounds[l]))) for l in S]
    res = dict(seed=SEED_DRAW, confirmatory_launches=len(rounds), launches=len(pick),
               rounds=[dict(launch_id=l, round_id=r) for l, r in pick], statements=4 * len(pick))
    print(json.dumps({k: v for k, v in res.items() if k != "rounds"}))
    if a.out:
        write_new(a.out, res)


# ---------------------------------------------------------------- V2
def v2(a):
    import gate1
    import pandas as pd
    key = pd.read_csv(a.key, dtype=str, keep_default_na=False)
    k1 = key[key["pass"] == "1"]
    ids = list(k1.loc[k1.kind == "original", "item_id"])
    lab_df = pd.read_csv(a.labels_of_record, dtype=str, keep_default_na=False)
    lab = dict(zip(lab_df["item_id"], lab_df["label"]))
    sc = gate1.read_scores([a.scores2])
    miss = [i for i in ids if i not in sc]
    g, gs = gate1.gate_frame(ids, lab, sc)
    y, yh = gs.h.to_numpy(), gs.pred.to_numpy()
    blk = gate1.ba_block(y, yh)                           # seed = gate1.SEED = 20261116, B = 10,000
    res = dict(bar="V2", n_original_items=len(ids), items_without_scorer2_row=miss, n_unsure_excluded=int(g.unsure.sum()),
               n_scored=int(len(gs)), n_missing_E_counted_wrong=int(gs.ai_missing.sum()), balanced_accuracy=blk,
               seed=gate1.SEED, B=gate1.B, bar_rule="2.5th-percentile lower bound > 0.5")
    res["V2_met"] = bool(blk["lo"] is not None and blk["lo"] > 0.5 and not miss)
    res["wording"] = ("a second scorer validated against the same human labels" if res["V2_met"]
                      else "second scorer not validated; A4 leaves the Holm family")
    print(json.dumps(res, indent=1))
    if a.out:
        write_new(a.out, res)


# ---------------------------------------------------------------- V3
def binary(r):
    if r["n_cruxes"] == 0:
        return 0
    if r["E"] is None:
        return None
    return int(r["E"] >= HIDE)


def kappa_binary(x, y):
    from gate1 import kappa
    return kappa(x, y)


def spearman(e1, e2):
    from scipy.stats import spearmanr
    if len(e1) < 3 or np.ptp(e1) == 0 or np.ptp(e2) == 0:
        return float("nan")
    return float(spearmanr(e1, e2).statistic)


def v3(a):
    s1 = {(r["launch_id"], r["round_id"], r["cand"]): r for r in rd(a.scores1)}
    s2 = {(r["launch_id"], r["round_id"], r["cand"]): r for r in rd(a.scores2)}
    ids = json.loads(Path(a.sample).read_text(encoding="utf-8"))["rounds"]
    keys = [(d["launch_id"], d["round_id"], c) for d in ids for c in range(4)]
    byl = {}
    n_left_out = 0
    for k in keys:
        r1, r2 = s1.get(k), s2.get(k)
        if r1 is None or r2 is None:
            n_left_out += 1
            continue
        b1, b2 = binary(r1), binary(r2)
        if b1 is None or b2 is None:
            n_left_out += 1
            continue
        both = (r1["n_cruxes"] or 0) >= 1 and (r2["n_cruxes"] or 0) >= 1 and r1["E"] is not None and r2["E"] is not None
        byl.setdefault(k[0], []).append((b1, b2, r1["E"] if both else np.nan, r2["E"] if both else np.nan))
    L = sorted(byl)
    arr = {l: np.array(byl[l], dtype=float) for l in L}

    def stats(rows):
        k = kappa_binary(rows[:, 0], rows[:, 1])
        m = ~np.isnan(rows[:, 2])
        return k, spearman(rows[m, 2], rows[m, 3]), int(m.sum())
    allrows = np.vstack([arr[l] for l in L])
    k0, s0, nsp = stats(allrows)
    rng = np.random.default_rng(SEED_V3)
    ks, ss, und = [], [], 0
    for _ in range(B):
        pick = rng.integers(0, len(L), len(L))
        k, s, _ = stats(np.vstack([arr[L[i]] for i in pick]))
        if np.isnan(k):
            und += 1
        else:
            ks.append(k)
        if not np.isnan(s):
            ss.append(s)
    ci = lambda v: [float(x) for x in np.percentile(v, [2.5, 97.5])] if v else [float("nan")] * 2  # noqa: E731
    res = dict(bar="V3", launches=len(L), statements_used=int(len(allrows)), statements_left_out_missing_E=n_left_out,
               kappa_binary=k0, kappa_ci95=ci(ks), kappa_undefined_resamples=und, spearman_E=s0, spearman_n=nsp, spearman_ci95=ci(ss),
               B=B, seed=SEED_V3, interval="launch-cluster percentile bootstrap (see module docstring)", reference_kappa=KAPPA_REF,
               kappa_below_reference=bool(not np.isnan(k0) and k0 < KAPPA_REF))
    res["wording_if_V1_V2_met_and_below"] = ("two scorers that each agree with the human labels disagree with each other; "
                                              "results depend on the scorer" if res["kappa_below_reference"] else None)
    print(json.dumps(res, indent=1))
    if a.out:
        write_new(a.out, res)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("v1"); p.add_argument("--smoke-dir", required=True); p.add_argument("--out")  # noqa: E702
    p = sub.add_parser("draw"); p.add_argument("--scores1", required=True); p.add_argument("--out")  # noqa: E702
    p = sub.add_parser("v2")
    p.add_argument("--key", required=True); p.add_argument("--labels-of-record", required=True)  # noqa: E702
    p.add_argument("--scores2", required=True); p.add_argument("--out")  # noqa: E702
    p = sub.add_parser("v3")
    p.add_argument("--scores1", required=True); p.add_argument("--scores2", required=True)  # noqa: E702
    p.add_argument("--sample", required=True); p.add_argument("--out")  # noqa: E702
    a = ap.parse_args()
    {"v1": v1, "draw": draw, "v2": v2, "v3": v3}[a.cmd](a)


if __name__ == "__main__":
    main()
