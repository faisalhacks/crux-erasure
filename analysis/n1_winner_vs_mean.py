"""N1 (FR s8, [R3]): winner of a round = statement with the lowest mean mid-rank over the round's raters
(raters whose ranks are all equal dropped).  Rounds with a tie for winner are excluded and counted.

Per round:  d_r = E(winner) - mean E of the round's candidates;
            dLen_r = zLen(winner) - mean zLen;  dClar_r = zClar(winner) - mean zClar
            (zLen, zClar = A2's controls, z-scored over all statements of the analysis set, common.zscore).
Family test (FR [R3]) = alpha of  d_r = alpha + g_L*dLen_r + g_C*dClar_r + u_r  (OLS across rounds, equal
weight, launch clusters, interval method of record = wild cluster bootstrap-t, B=10000, seed 20261120).
Output key "erasure" = alpha (the family test).  Printed beside it, never family tests:
  N1u = unadjusted mean of d_r (brief's literal comparison); N1h = model with dLen_r only (A2h analogue);
  slopes g_L, g_C; mean dLen_r, mean dClar_r; number of rounds with d_r != 0.
Positive = winners hide more disagreement than the average candidate (of the same length and clarity for alpha).
Per-group fallback (FR s11): same rule on the group-level winner; with per-rater data it is the same mean-rank rule.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402


def round_deltas(df, p):
    pred = p["predictor"]
    d = df.copy()
    miss = d.groupby("round_id")[pred].transform(lambda s: s.isna().any())
    n_missing = int(d.loc[miss, "round_id"].nunique())
    d = d[~miss].copy()
    d["_mid"] = d.groupby(["round_id", "rater_id"], sort=False)["rank"].rank(method="average")
    d["_nu"] = d.groupby(["round_id", "rater_id"], sort=False)["rank"].transform("nunique")
    d = d[d["_nu"] > 1].copy()
    d["z_log_len"] = C.zscore(d, "log_len")    # same constants as A2 (statements of the analysis set)
    d["z_flesch"] = C.zscore(d, "flesch")
    recs, n_tie = [], 0
    for rid, g in d.groupby("round_id", sort=False):
        m = g.groupby("cand")["_mid"].mean()
        if (m == m.min()).sum() > 1:
            n_tie += 1
            continue
        st = g.drop_duplicates("cand").set_index("cand")
        w = m.idxmin()
        rec = {"launch_id": g["launch_id"].iat[0]}
        for v, nm in ((pred, "d"), ("z_log_len", "dLen"), ("z_flesch", "dClar")):
            rec[nm] = st.loc[w, v] - st[v].mean()
        recs.append(rec)
    return pd.DataFrame(recs), n_missing, n_tie


def _fit(D, cols, codes, nc, p):
    X = np.column_stack([np.ones(len(D))] + [D[c].to_numpy(float) for c in cols])
    return C.ols_cluster_ci(X, D["d"].to_numpy(float), codes, nc, p["B"], p["seed"], p["alpha"], p["interval"])


def run(df, p):
    df, aset = C.restrict_confirmatory(df, p, p.get("_kind"))   # FR s2 [R4]: confirmatory set; include_dev = sensitivity only
    D, n_missing, n_tie = round_deltas(df, p)
    codes, nc = C.cluster_codes(D["launch_id"])
    adj = _fit(D, ["dLen", "dClar"], codes, nc, p)
    h = _fit(D, ["dLen"], codes, nc, p)
    u = _fit(D, [], codes, nc, p)
    return {"analysis_set": aset, "B": p["B"], "seed": p["seed"], "interval": p["interval"], "n_rounds": int(len(D)), "n_clusters": int(nc),
            "rounds_tied_winner_excluded": n_tie, "rounds_dropped_missing_E": n_missing,
            "rounds_with_d_nonzero": int((D["d"] != 0).sum()),
            "erasure": adj[0], "g_L": adj[1], "g_C": adj[2],       # family test alpha + slopes
            "N1u": u[0], "N1h": h[0], "N1h_g_L": h[1],
            "mean_dLen": float(D["dLen"].mean()), "mean_dClar": float(D["dClar"].mean())}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--kind", required=True, choices=C.KINDS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--params", default=None)
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    C.check_kind(a.kind)
    p = C.load_params(a.params)
    p["_kind"] = a.kind
    if not a.params or "seed" not in json.loads(Path(a.params).read_text(encoding="utf-8") if Path(a.params).exists() else a.params):
        p["seed"] = 20261120
    df, srcs = C.read_long(a.input, a.kind)
    res = run(df, p)
    res["kind"] = a.kind
    e, u, h = res["erasure"], res["N1u"], res["N1h"]
    C.write_result(a.out, res, __file__, a.kind, p["seed"], srcs, f"N1 B={p['B']} {a.note}")
    print(f"N1[{a.kind}] alpha {e['est']:+.4f} [{e['lo']:+.4f}, {e['hi']:+.4f}] p={e['p_boot']:.3f} | "
          f"N1u {u['est']:+.4f} [{u['lo']:+.4f},{u['hi']:+.4f}] | N1h {h['est']:+.4f} [{h['lo']:+.4f},{h['hi']:+.4f}] "
          f"rounds={res['n_rounds']} ties_excl={res['rounds_tied_winner_excluded']}")
    return res


if __name__ == "__main__":
    main()
