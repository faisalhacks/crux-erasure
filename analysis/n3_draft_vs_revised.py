"""N3 (FR s8): mean within-round difference mean E(iteration 1) - mean E(iteration 0), cruxes fixed
from the opinions; launch-cluster bootstrap (B=10000, default_rng(20261123)).  Statement-level input:
  launch_id, round_id, cand, iteration (0/1), E
Only rounds with both iterations count; runs only if >= 30 launches qualify (FR s8, J).
Output {n_clusters, erasure:{est,lo,hi,se,p_boot}} (figure schema).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402
from a3_ai_vs_human import diff_run  # noqa: E402


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
        p["seed"] = 20261123
    C.verify_source(a.kind, a.input)
    df = pd.read_csv(a.input)
    res = diff_run(df, "iteration", 1, 0, p)
    res["kind"] = a.kind
    C.write_result(a.out, res, __file__, a.kind, p["seed"], [a.input], f"N3 status={res['status']} B={p['B']}")
    print("N3", a.kind, res["status"], res.get("erasure"))
    return res


if __name__ == "__main__":
    main()
