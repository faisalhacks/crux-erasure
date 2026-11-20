"""step2_reference.py -- FROZEN_RULES 6.R5 step 2 (R5; decisions.md D49, D50).

PRESENCE CHECK ONLY.  Human reference Hsplit_r (round level) from participants' PRE-deliberation position ratings
(hm_all_position_statement_ratings, rating_index 0) against scorer 1's call Sdis_r = "E1 found >= 1 crux".
It says nothing about whether a statement hides the disagreement.

Primary statistic (the ONLY one that decides the outcome): BA2 = balanced accuracy of Sdis against Hsplit over the
usable rounds, with a launch-cluster percentile bootstrap (B = 10,000, default_rng(20261141)) and, if any question
id occurs in more than one launch, a question-cluster bootstrap (same B, seed 20261142); the SMALLER lower bound is used.
Outcome codes: PASS (LB > 0.5 and BA2 >= 0.60), WEAK (LB > 0.5, BA2 < 0.60), FAIL (LB <= 0.5), UNUSABLE.
UNUSABLE if: < 200 usable rounds or < 100 launches; any Hsplit class < 50 rounds or < 25 launches; or > 1% of the
resamples of a deciding bootstrap contain a single Hsplit class.

Real data (--kind real):
  1. If P/gate1/FREEZE.json does not exist, freeze.run(trigger='step2') writes it (FROZEN_RULES read-only) BEFORE any
     rating value is read.  Then the script refuses unless FREEZE.json exists and FROZEN_RULES.md and this script hash
     to the values recorded in it.
  2. Refuses if any P/gate1/STEP2_computed__*.json exists (a completed run is never repeated).
  3. Reads ONLY the whitelisted columns below (unit-tested: no rank, candidate rating, E, label, critique, survey,
     top_candidate column).
  4. Writes P/gate1/STEP2_computed__<utc>.json (never overwritten).  Per-round calls go to
     P/gate1/step2_private/rounds__<utc>.csv, which must not be shown to the author before author_verification.csv
     is complete (FR 6.R5).
Dummy data (--kind dummy): synthetic table, output to --out-dir only.  python -I step2_reference.py --kind dummy --out-dir X
"""
import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P_DEFAULT = HERE.parent

SEED_LAUNCH = 20261141
SEED_QUESTION = 20261142
B_DEFAULT = 10000
BAR_POINT = 0.60
MIN_ROUNDS, MIN_LAUNCHES = 200, 100
MIN_CLASS_ROUNDS, MIN_CLASS_LAUNCHES = 50, 25
MAX_ONE_CLASS_SHARE = 0.01
EXPECTED_CONF_ROUNDS = 1622      # r5_feasibility.json (analysis set minus development launches)
CONTEXT_DROP_SHARE = 0.05

TOKENS = {"STRONGLY_DISAGREE": -3, "DISAGREE": -2, "SOMEWHAT_DISAGREE": -1, "NEUTRAL": 0,
          "SOMEWHAT_AGREE": 1, "AGREE": 2, "STRONGLY_AGREE": 3}

# Column whitelists (FR 6.R5 step 2 "Not read").  test_r5.py asserts none of FORBIDDEN_SUBSTR is in any of them.
COLS_A2 = ["launch_id", "round_id"]
COLS_CC = ["launch_id", "round_id", "iteration_index", "question.id", "own_opinion.metadata.participant_id",
           "metadata.provenance"]
COLS_PS = ["launch_id", "question.id", "metadata.participant_id", "metadata.provenance", "metadata.status",
           "rating_index", "ratings.agreement", "monotonic_timestamp"]
EXTRACT_KEYS = ["launch_id", "round_id", "ok", "n_cruxes", "dropped_too_long"]
FORBIDDEN_SUBSTR = ["rank", "ratings.quality", "candidates.", "critique", "top_candidate", "explanation",
                    "label", "best_expression", "own_influence", "welfare", "reward"]
FORBIDDEN_EXACT = ["E", "E_pos", "y", "ratings.agreement@cc"]   # 'ratings.agreement' is allowed only from position ratings


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ reference
def member_value(tokens):
    """ratings.agreement array -> value in -3..3, or None (unrated) unless exactly one known token."""
    if tokens is None:
        return None
    t = list(tokens)
    if len(t) != 1:
        return None
    return TOKENS.get(str(t[0]).strip().upper())


def hsplit(values, strong=False):
    """1 if >= 1 member at +1 or above and >= 1 at -1 or below (strong: +2 / -2); NEUTRAL counts to neither side."""
    k = 2 if strong else 1
    return int(any(v >= k for v in values) and any(v <= -k for v in values))


# ------------------------------------------------------------------ statistics
def ba_counts(tp, fn, tn, fp):
    """Balanced accuracy; None if a reference class is empty."""
    if tp + fn == 0 or tn + fp == 0:
        return None
    return 0.5 * (tp / (tp + fn) + tn / (tn + fp))


def confusion(y, yhat):
    y = np.asarray(y, int)
    yhat = np.asarray(yhat, int)
    return (int(((y == 1) & (yhat == 1)).sum()), int(((y == 1) & (yhat == 0)).sum()),
            int(((y == 0) & (yhat == 0)).sum()), int(((y == 0) & (yhat == 1)).sum()))


def cluster_boot_ba(y, yhat, clusters, B, seed):
    """Percentile cluster bootstrap of BA.  One-class resamples score 0.5 and are counted.
    Returns (lb, ub, n_one_class, B)."""
    y = np.asarray(y, int)
    yhat = np.asarray(yhat, int)
    codes, uniq = pd.factorize(pd.Series(list(clusters)), sort=True)
    K = len(uniq)
    M = np.zeros((K, 4))
    np.add.at(M, (codes, 0), (y == 1) & (yhat == 1))
    np.add.at(M, (codes, 1), (y == 1) & (yhat == 0))
    np.add.at(M, (codes, 2), (y == 0) & (yhat == 0))
    np.add.at(M, (codes, 3), (y == 0) & (yhat == 1))
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    one = 0
    for b in range(B):
        w = np.bincount(rng.integers(0, K, K), minlength=K)
        tp, fn, tn, fp = w @ M
        v = ba_counts(tp, fn, tn, fp)
        if v is None:
            one += 1
            v = 0.5
        out[b] = v
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)), int(one), int(B)


def decide(ba2, boots, usable_counts):
    """THE outcome rule.  Inputs: primary BA2 point, the deciding bootstraps [(lb, ub, n_one, B), ...] and the
    usability verdict from usable_counts().  Nothing else can reach this function (FR 6.R5, statistician cond. 5)."""
    ok, reasons = usable_counts
    reasons = list(reasons)
    for lb, ub, n_one, B in boots:
        if n_one > MAX_ONE_CLASS_SHARE * B:
            ok = False
            reasons.append(f"{n_one}/{B} single-class resamples > 1%")
    if not ok or ba2 is None:
        return "UNUSABLE", None, reasons
    lb = min(b[0] for b in boots)
    if lb <= 0.5:
        return "FAIL", lb, reasons
    return ("PASS" if ba2 >= BAR_POINT else "WEAK"), lb, reasons


def usable_counts(df):
    """df: usable rounds with columns launch_id, hsplit."""
    reasons = []
    n, k = len(df), df["launch_id"].nunique()
    if n < MIN_ROUNDS or k < MIN_LAUNCHES:
        reasons.append(f"usable rounds {n} (min {MIN_ROUNDS}) / launches {k} (min {MIN_LAUNCHES})")
    for c in (0, 1):
        s = df[df["hsplit"] == c]
        if len(s) < MIN_CLASS_ROUNDS or s["launch_id"].nunique() < MIN_CLASS_LAUNCHES:
            reasons.append(f"Hsplit={c}: {len(s)} rounds (min {MIN_CLASS_ROUNDS}) from {s['launch_id'].nunique()} "
                           f"launches (min {MIN_CLASS_LAUNCHES})")
    return (not reasons), reasons


def evaluate(t, B=B_DEFAULT, seed_launch=SEED_LAUNCH, seed_question=SEED_QUESTION):
    """t: one row per confirmatory round with columns
         launch_id, round_id, question_id, n_members, n_rated, hsplit (0/1 or NaN if unusable), hsplit_strong,
         sd_values, ext_ok (bool), n_cruxes (int or NaN), dropped_too_long (bool)
    Returns the result dict; result['outcome'] is set by decide() from the primary BA2 only."""
    t = t.copy()
    res = {"n_rounds_in": int(len(t)), "B": B, "seed_launch": seed_launch, "seed_question": seed_question}
    drop_ctx = t["dropped_too_long"].fillna(False).astype(bool)
    res["n_dropped_context_length"] = int(drop_ctx.sum())
    usable = (t["n_rated"] >= 3) & ((t["n_members"] - t["n_rated"]) <= 1)
    res["n_unusable_rating_coverage"] = int((~usable).sum())
    u = t[usable & ~drop_ctx].copy()
    u["hsplit"] = u["hsplit"].astype(int)
    # scorer call; extraction missing after retry -> counted as the wrong call
    miss = ~u["ext_ok"].fillna(False).astype(bool)
    sd = (u["n_cruxes"].fillna(0) >= 1).astype(int)
    u["sdis"] = np.where(miss, 1 - u["hsplit"], sd)
    res["n_extraction_missing_counted_wrong"] = int(miss.sum())
    res["n_usable_rounds"] = int(len(u))
    res["n_usable_launches"] = int(u["launch_id"].nunique())
    res["hsplit_class_counts"] = {str(c): {"rounds": int((u["hsplit"] == c).sum()),
                                           "launches": int(u.loc[u["hsplit"] == c, "launch_id"].nunique())}
                                  for c in (0, 1)}
    tp, fn, tn, fp = confusion(u["hsplit"], u["sdis"])
    ba2 = ba_counts(tp, fn, tn, fp)
    res["confusion"] = {"tp": tp, "fn": fn, "tn": tn, "fp": fp}
    res["BA2"] = ba2
    res["sens"] = tp / (tp + fn) if tp + fn else None
    res["spec"] = tn / (tn + fp) if tn + fp else None
    uc = usable_counts(u)
    boots = []
    if len(u) and u["hsplit"].nunique() == 2:
        bl = cluster_boot_ba(u["hsplit"], u["sdis"], u["launch_id"], B, seed_launch)
        res["launch_boot"] = {"lb": bl[0], "ub": bl[1], "n_one_class": bl[2]}
        boots.append(bl)
        q_multi = bool((u.groupby("question_id")["launch_id"].nunique() > 1).any())
        res["question_in_more_than_one_launch"] = q_multi
        if q_multi:
            bq = cluster_boot_ba(u["hsplit"], u["sdis"], u["question_id"], B, seed_question)
            res["question_boot"] = {"lb": bq[0], "ub": bq[1], "n_one_class": bq[2]}
            boots.append(bq)
    outcome, lb_used, reasons = decide(ba2, boots, uc) if boots else ("UNUSABLE", None, list(uc[1]) + ["one Hsplit class"])
    res["outcome"] = outcome
    res["lb_used"] = lb_used
    res["unusable_reasons"] = reasons
    res["reported_no_rule"] = reported(u, t, drop_ctx, B, seed_launch)
    return res


def reported(u, t, drop_ctx, B, seed):
    """Statistician condition 4 and the R5 'also reported' list.  NEVER read by decide()."""
    r = {"prevalence_hsplit": float(u["hsplit"].mean()) if len(u) else None,
         "prevalence_sdis": float(u["sdis"].mean()) if len(u) else None}
    s5 = u[u["n_rated"] == 5]
    r["BA2_n_rated_5"] = ba_counts(*confusion(s5["hsplit"], s5["sdis"])) if len(s5) else None
    r["n_rated_5_rounds"] = int(len(s5))
    al = u[u["n_members"] == u["n_rated"]]
    r["BA2_all_rated"] = ba_counts(*confusion(al["hsplit"], al["sdis"])) if len(al) else None
    if "hsplit_strong" in u:
        r["BA2_strong_split"] = ba_counts(*confusion(u["hsplit_strong"].astype(int), u["sdis"])) if len(u) else None
    if "sd_values" in u and len(u) > 2:
        from scipy.stats import spearmanr
        nc = u["n_cruxes"].fillna(0)
        rho = spearmanr(nc, u["sd_values"]).statistic
        r["spearman_ncruxes_sd"] = None if rho != rho else float(rho)
    n_elig = len(t)
    r["context_drop_share"] = (int(drop_ctx.sum()) / n_elig) if n_elig else None
    if n_elig and drop_ctx.sum() / n_elig > CONTEXT_DROP_SHARE:
        usable = (t["n_rated"] >= 3) & ((t["n_members"] - t["n_rated"]) <= 1)
        d = t[usable].copy()
        d["hsplit"] = d["hsplit"].astype(int)
        sd = (d["n_cruxes"].fillna(0) >= 1).astype(int)
        wrong = drop_ctx[usable] | ~d["ext_ok"].fillna(False).astype(bool)
        d["sdis"] = np.where(wrong, 1 - d["hsplit"], sd)
        r["BA2_context_drops_as_wrong"] = ba_counts(*confusion(d["hsplit"], d["sdis"]))
    return r


# ------------------------------------------------------------------ real-data table
def build_table(round_ids, cc, ps, ext):
    """round_ids: DataFrame(launch_id, round_id) of the confirmatory set.  cc, ps: projected frames.  ext: list of dicts.
    Returns the per-round table for evaluate()."""
    cc0 = cc[(cc["iteration_index"] == 0) & (cc["metadata.provenance"] == "HUMAN_CITIZEN")]
    cc0 = cc0[cc0["round_id"].isin(set(round_ids["round_id"]))]
    pre = ps[(ps["rating_index"] == 0) & (ps["metadata.provenance"] == "HUMAN_CITIZEN")
             & (ps["metadata.status"] == "COMPLETED")].copy()
    pre["v"] = [member_value(a) for a in pre["ratings.agreement"]]
    pre = pre[pre["v"].notna()].sort_values("monotonic_timestamp")
    pre = pre.drop_duplicates(["launch_id", "question.id", "metadata.participant_id"], keep="first")
    val = {(a, q, m): v for a, q, m, v in zip(pre["launch_id"], pre["question.id"], pre["metadata.participant_id"], pre["v"])}
    exd = {e["round_id"]: e for e in ext}
    rows = []
    for rid, g in cc0.groupby("round_id", sort=True):
        L = g["launch_id"].iloc[0]
        qs = g["question.id"].dropna().unique()
        members = set(g["own_opinion.metadata.participant_id"].dropna())
        e = exd.get(rid, {})
        base = dict(launch_id=L, round_id=rid, question_id=qs[0] if len(qs) == 1 else None, n_members=len(members),
                    ext_ok=bool(e.get("ok", False)), n_cruxes=e.get("n_cruxes"),
                    dropped_too_long=bool(e.get("dropped_too_long", False)))
        if len(qs) != 1:
            rows.append({**base, "n_rated": 0, "hsplit": np.nan, "hsplit_strong": np.nan, "sd_values": np.nan})
            continue
        vals = [val[(L, qs[0], m)] for m in members if (L, qs[0], m) in val]
        rows.append({**base, "n_rated": len(vals), "hsplit": hsplit(vals) if vals else np.nan,
                     "hsplit_strong": hsplit(vals, strong=True) if vals else np.nan,
                     "sd_values": float(np.std(vals)) if vals else np.nan})
    return pd.DataFrame(rows)


def load_real(root, data_dir, dev_file):
    a2 = pd.read_parquet(Path(root) / "analysis" / "scores" / "a2_long_shuffled.parquet", columns=COLS_A2).drop_duplicates()
    dev = {json.loads(l)["launch_id"] for l in open(dev_file, encoding="utf-8") if l.strip()}
    conf = a2[~a2["launch_id"].isin(dev)]
    cc = pd.read_parquet(Path(data_dir) / "hm_all_candidate_comparisons.parquet", columns=COLS_CC)
    ps = pd.read_parquet(Path(data_dir) / "hm_all_position_statement_ratings.parquet", columns=COLS_PS)
    ext = []
    for l in open(Path(root) / "analysis" / "scores" / "a2_extractions_v2.jsonl", encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            ext.append({k: r.get(k) for k in EXTRACT_KEYS})
    return conf, cc, ps, ext


def ensure_freeze(root):
    """FR 6.R5: FREEZE.json before the reference is computed.  Returns the FREEZE record or exits."""
    sys.path.insert(0, str(HERE))
    import freeze
    gate = Path(root) / "gate1"
    fz = gate / "FREEZE.json"
    if not fz.exists():
        code, msg = freeze.run(root, fz, trigger="step2")
        print("freeze:", msg)
        if code != 0:
            sys.exit(f"REFUSED (FR 6.R5): freeze failed ({msg}).")
    if not fz.exists():
        sys.exit("REFUSED (FR 6.R5): gate1/FREEZE.json absent.")
    rec = json.loads(fz.read_text(encoding="utf-8"))
    files = rec.get("files", {})
    if files.get("FROZEN_RULES.md", {}).get("sha256") != sha(Path(root) / "FROZEN_RULES.md"):
        sys.exit("REFUSED (FR 6.R5): FROZEN_RULES.md differs from FREEZE.json.")
    me = Path(root) / "analysis" / "step2_reference.py"
    if files.get("step2_reference.py", {}).get("sha256") != sha(me):
        sys.exit("REFUSED (FR 6.R5): step2_reference.py differs from the hash in FREEZE.json (or was not hashed).")
    return rec


def run_real(root, data_dir, dev_file, expected_rounds=EXPECTED_CONF_ROUNDS, B=B_DEFAULT):
    root = Path(root)
    gate = root / "gate1"
    if glob.glob(str(gate / "STEP2_computed__*.json")):
        sys.exit("REFUSED (FR 6.R5): a completed step-2 run exists; it is never repeated.")
    rec = ensure_freeze(root)          # BEFORE any rating value is read
    conf, cc, ps, ext = load_real(root, data_dir, dev_file)
    if conf["round_id"].nunique() != expected_rounds:
        sys.exit(f"REFUSED (FR 6.R5): {conf['round_id'].nunique()} confirmatory rounds, expected {expected_rounds}.")
    t = build_table(conf, cc, ps, ext)
    res = evaluate(t, B=B)
    from datetime import datetime, timezone
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    res.update(rules="R5", step=2, kind="real", freeze_utc=rec.get("frozen_utc"),
               script_sha256=sha(root / "analysis" / "step2_reference.py"),
               scope="presence of disagreement only; says nothing about whether a statement hides it")
    priv = gate / "step2_private"
    priv.mkdir(parents=True, exist_ok=True)
    t.to_csv(priv / f"rounds__{stamp}.csv", index=False)
    out = gate / f"STEP2_computed__{stamp}.json"
    with open(out, "x", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return out, res


# ------------------------------------------------------------------ synthetic
def synth_table(n_launch=400, rounds_per=3, p_split=0.6, sens=0.85, spec=0.6, seed=1, q_pool=None):
    rng = np.random.default_rng(seed)
    rows = []
    for L in range(n_launch):
        for r in range(rounds_per):
            h = int(rng.random() < p_split)
            s = int(rng.random() < (sens if h else 1 - spec))
            nm = int(rng.choice([4, 5], p=[0.12, 0.88]))
            rows.append(dict(launch_id=f"L{L}", round_id=f"L{L}r{r}",
                             question_id=f"q{rng.integers(q_pool)}" if q_pool else f"L{L}q{r}",
                             n_members=nm, n_rated=nm, hsplit=h, hsplit_strong=h, sd_values=float(h) + rng.random(),
                             ext_ok=True, n_cruxes=int(s) * int(rng.integers(1, 5)), dropped_too_long=False))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=("dummy", "real"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--B", type=int, default=B_DEFAULT)
    a = ap.parse_args(argv)
    if a.kind == "dummy":
        if not a.out_dir:
            sys.exit("--out-dir required for dummy")
        res = evaluate(synth_table(), B=a.B)
        res.update(rules="R5", step=2, kind="DUMMY / NOT RESULTS")
        Path(a.out_dir).mkdir(parents=True, exist_ok=True)
        (Path(a.out_dir) / "STEP2_dummy.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        print(res["outcome"], res["BA2"])
        return 0
    if a.B != B_DEFAULT:
        sys.exit("REFUSED: B is fixed at 10,000 for real data.")
    out, res = run_real(P_DEFAULT, P_DEFAULT.parent / "data" / "habermas_gcs",
                        P_DEFAULT.parent / "pilots" / "T3_1" / "pilot_groups.jsonl")
    print(out, res["outcome"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
