"""A2 (FR s7, s11): within-round rank vs crux erasure score E, controls log length and Flesch clarity.

y = (4 - midrank)/3 per rater-round (1 = ranked best); y = fixed effect(rater x round) + beta_E*E
+ beta_L*zLen + beta_C*zClar; OLS after demeaning within (rater, round); z-scores over all
statements in the analysis set; launch-cluster bootstrap (B=10000, default_rng(20261119)),
percentile 95% CI, bootstrap p = 2*min(#{b<=0}+1,#{b>=0}+1)/(B+1).
unit='group' = FR s11 fallback (y averaged over raters, round fixed effect).
Also reported beside the primary: 'uncontrolled' (E only) and 'A2h' (E + length, no clarity).
Other sensitivity models: pass --params with "controls" (extra columns, e.g. own_sim -> A2b) or
"predictor" (e.g. E_pos -> A2e, E_w -> A2g, E2 with seed 20261121 -> A4).
Positive beta_E = hiding statements ranked better.
[R4] Default analysis set = confirmatory set (development launches excluded, common.restrict_confirmatory);
"include_dev": true in --params = sensitivity model A2d (all launches), labelled in the output and the RUNS note.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402


def fit_models(df, p, design_only=False):
    pred = p["predictor"]
    df, aset = C.restrict_confirmatory(df, p, p.get("_kind"))   # FR s2 [R4]: confirmatory set by default; include_dev = A2d sensitivity
    n0_rounds = df["round_id"].nunique()
    miss = df.groupby("round_id")[pred].transform(lambda s: s.isna().any())
    dropped_missing = int(df.loc[miss, "round_id"].nunique())
    d = df[~miss].copy()
    d, n_tied = C.add_y(d, p["unit"])
    ctr = list(p["controls"])
    for c in ctr:
        d["z_" + c] = C.zscore(d, c)
    var_round = d.groupby("round_id")[pred].transform(lambda s: s.max() > s.min())
    inform = d.loc[var_round, "launch_id"].nunique()
    n_novar = int(d.loc[~var_round, "round_id"].nunique())
    codes, nc = C.cluster_codes(d["launch_id"])
    labels = {pred: "erasure", **p["control_labels"]}
    models = {"controlled": [pred] + ["z_" + c for c in ctr], "uncontrolled": [pred],
              "A2h": [pred] + ["z_" + c for c in ctr[:1]]}
    out = {"analysis_set": aset, "unit": p["unit"], "interval": p["interval"], "B": p["B"], "seed": p["seed"], "n_rows": int(len(d)), "n_clusters": int(nc),
           "n_rounds": int(d["round_id"].nunique()), "rounds_dropped_missing_E": dropped_missing,
           "rater_rounds_dropped_all_tied": n_tied, "rounds_no_E_variation": n_novar,
           "launches_with_E_variation": int(inform),
           "interpretability_floor_fires": bool(inform < p["min_informative_launches"])}
    y = C.fe_demean(d, ["y"])["y"]
    if design_only:
        Xd = C.fe_demean(d, models["controlled"])
        return np.column_stack([Xd[c] for c in models["controlled"]]), y, codes, nc
    if p.get("only_primary"):
        models = {"controlled": models["controlled"]}
    for name, cols in models.items():
        Xd = C.fe_demean(d, cols)
        X = np.column_stack([Xd[c] for c in cols])
        res_ = C.ols_cluster_ci(X, y, codes, nc, p["B"], p["seed"], p["alpha"], p["interval"])
        out[name] = {labels.get(c.replace("z_", ""), c): r_ for c, r_ in zip(cols, res_)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="long csv/parquet (schema in common.py) or HABERMAS_SHUFFLED")
    ap.add_argument("--kind", required=True, choices=C.KINDS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--params", default=None)
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    C.check_kind(a.kind)
    p = C.load_params(a.params)
    p["_kind"] = a.kind
    df, srcs = C.read_long(a.input, a.kind)
    res = fit_models(df, p)
    res["kind"] = a.kind
    if p["include_dev"]:
        a.note = (a.note + " ").lstrip() + "[A2d SENSITIVITY: including the development launches; not an estimate of record]"
    if a.kind == "real":
        tj = json.loads((C.GATE / C.TIER_FILE).read_text(encoding="utf-8"))
        se_ = res["controlled"]["erasure"]["se"]
        res["tier_blind"] = tj["tier"]
        res["tier_final"] = "LOW-POWER" if (tj["tier"] == "INFORMATIVE" and 2.80 * se_ > 0.10) else tj["tier"]   # FR 7.1 one-way downgrade, SE only
    C.write_result(a.out, res, __file__, a.kind, p["seed"], srcs,
                   f"A2 unit={p['unit']} B={p['B']} interval={p['interval']} pred={p['predictor']} {a.note}")
    e = res["controlled"]["erasure"]
    print(f"A2[{a.kind}] beta_E {e['est']:+.4f} [{e['lo']:+.4f}, {e['hi']:+.4f}] p={e['p_boot']:.3f} clusters={res['n_clusters']}")
    return res


if __name__ == "__main__":
    main()
