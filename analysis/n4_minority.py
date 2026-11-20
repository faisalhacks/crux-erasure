"""N4 (FR s8): A2 plus E x minority.  Per-rater ranks only (skipped under the FR s11 fallback).
Long-table schema of common.py plus 'minority' (1 = rater on the side with fewer members of the
first-listed crux, 0 = majority side; blank/NaN = rater on neither side or equal sides -> excluded
and counted; the side assignment comes from the extractor's member lists, not from this script).
Model: y = FE(rater x round) + b_E*E + b_int*E*minority + controls (minority itself is absorbed by
the rater-round fixed effect).  Test = interaction b_int, launch bootstrap (B=10000,
default_rng(20261124)).  Output (figure schema): minority = b_E + b_int, majority = b_E, plus interaction.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402


def run(df, p):
    if p["unit"] == "group":
        sys.exit("N4 is skipped under the per-group fallback (FR s11, BRIEF 14).")
    pred = p["predictor"]
    df, aset = C.restrict_confirmatory(df, p, p.get("_kind"))   # FR s2 [R4]
    miss = df.groupby("round_id")[pred].transform(lambda s: s.isna().any())
    d = df[~miss].copy()
    n_no_side = int(d.loc[d["minority"].isna()].groupby(["round_id", "rater_id"]).ngroups)
    d = d[d["minority"].notna()].copy()
    d, n_tied = C.add_y(d, "rater")
    ctr = list(p["controls"])
    for c in ctr:
        d["z_" + c] = C.zscore(d, c)
    d["Exm"] = d[pred] * d["minority"]
    cols = [pred, "Exm"] + ["z_" + c for c in ctr]
    codes, nc = C.cluster_codes(d["launch_id"])
    y = C.fe_demean(d, ["y"])["y"]
    Xd = C.fe_demean(d, cols)
    X = np.column_stack([Xd[c] for c in cols])
    r1 = C.ols_cluster_ci(X, y, codes, nc, p["B"], p["seed"], p["alpha"], p["interval"])
    ci_ = list(range(len(cols)))
    Xd2 = dict(Xd); Xd2[pred] = d[pred].to_numpy(float) * (1 - d["minority"].to_numpy(float))
    Xd2[pred] = C.fe_demean(d.assign(_em=d[pred] * (1 - d["minority"])), ["_em"])["_em"]
    X2 = np.column_stack([Xd2[pred], Xd["Exm"]] + [Xd[c] for c in cols[2:]])
    r2 = C.ols_cluster_ci(X2, y, codes, nc, p["B"], p["seed"], p["alpha"], p["interval"])
    return {"analysis_set": aset, "B": p["B"], "seed": p["seed"], "n_clusters": int(nc), "n_rows": int(len(d)),
            "raters_excluded_no_side": n_no_side, "rater_rounds_dropped_all_tied": n_tied,
            "n_minority_raters": int(d.loc[d.minority == 1].groupby(["round_id", "rater_id"]).ngroups),
            "n_majority_raters": int(d.loc[d.minority == 0].groupby(["round_id", "rater_id"]).ngroups),
            "majority": r1[0],
            "minority": r2[1],
            "interaction": r1[1]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--kind", required=True, choices=C.KINDS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--params", default=None)
    a = ap.parse_args(argv)
    C.check_kind(a.kind)
    p = C.load_params(a.params)
    p["_kind"] = a.kind
    if not a.params or "seed" not in a.params:
        p["seed"] = 20261124
    df, srcs = C.read_long(a.input, a.kind)
    res = run(df, p)
    res["kind"] = a.kind
    C.write_result(a.out, res, __file__, a.kind, p["seed"], srcs, f"N4 B={p['B']}")
    i = res["interaction"]
    print(f"N4[{a.kind}] interaction {i['est']:+.3f} [{i['lo']:+.3f},{i['hi']:+.3f}] p={i['p_boot']:.3f}")
    return res


if __name__ == "__main__":
    main()
