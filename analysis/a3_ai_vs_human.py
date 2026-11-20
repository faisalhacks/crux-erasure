"""A3 (FR s8): mean within-round difference E(AI-written) - E(human-written), launch-cluster
bootstrap (B=10000, default_rng(20261122)).  Input is STATEMENT-level (no ranks needed):
  launch_id, round_id, cand, prov (MODEL_MEDIATOR / HUMAN_MEDIATOR), E
Round difference = mean E of its MODEL_MEDIATOR candidates - mean E of its HUMAN_MEDIATOR candidates;
only rounds with both kinds count.  Runs only if >= 30 launches contribute (FR s8, J); otherwise the
JSON records status NOT_RUN with the count.  Output {n_clusters, erasure:{est,lo,hi,se,p_boot}}.
N3 reuses diff_run(): n3_draft_vs_revised.py.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402


def diff_run(df, grp_col, plus, minus, p, floor_key="min_launches_a3_n3"):
    """mean over rounds of mean(E | grp==plus) - mean(E | grp==minus)."""
    df, aset = C.restrict_confirmatory(df, p, p.get("_kind"))   # FR s2 [R4]: confirmatory set (A3 and N3)
    d = df.dropna(subset=["E"])
    m = d.groupby(["launch_id", "round_id", grp_col])["E"].mean().unstack(grp_col)
    m = m.dropna(subset=[plus, minus])
    m["d"] = m[plus] - m[minus]
    m = m.reset_index()
    nl = int(m["launch_id"].nunique())
    out = {"analysis_set": aset, "B": p["B"], "seed": p["seed"], "n_rounds": int(len(m)), "n_clusters": nl}
    if nl < p[floor_key]:
        out["status"] = "NOT_RUN"
        out["reason"] = f"{nl} launches < floor {p[floor_key]} (FR s8)"
        return out
    codes, nc = C.cluster_codes(m["launch_id"])
    out["status"] = "RUN"
    out["erasure"] = C.mean_ci(m["d"].to_numpy(float), codes, nc, p["B"], p["seed"], p["alpha"], p["interval"])
    return out


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
        p["seed"] = 20261122
    C.verify_source(a.kind, a.input)
    df = pd.read_csv(a.input)
    res = diff_run(df, "prov", "MODEL_MEDIATOR", "HUMAN_MEDIATOR", p)
    res["kind"] = a.kind
    C.write_result(a.out, res, __file__, a.kind, p["seed"], [a.input], f"A3 status={res['status']} B={p['B']}")
    print("A3", a.kind, res["status"], res.get("erasure"))
    return res


if __name__ == "__main__":
    main()
