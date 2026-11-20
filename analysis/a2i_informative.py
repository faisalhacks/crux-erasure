"""A2i (FR s7.2 / s7 sensitivity table [R1]): A2 fitted on informative rounds only (FR 7.1: a round of the A2 analysis
set, >= 1 crux and no missing E, whose 4 candidates take >= 2 distinct values of E); control slopes are then estimated
inside those rounds.  Thin wrapper: reads the table with common.read_long (source/manifest checks), keeps the
informative rounds, and calls a2_within_round.fit_models unchanged (confirmatory set by default; seed 20261119;
interval of record).  Usage as a2_within_round.py: --input --kind real --out [--params]."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402


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
    df, srcs = C.read_long(a.input, a.kind)
    pred = p["predictor"]
    st = df.drop_duplicates(["round_id", "cand"])
    ok = st.groupby("round_id")[pred].apply(lambda s: s.notna().all() and s.nunique() >= 2)
    keep = set(ok[ok].index)
    n_before = df["round_id"].nunique()
    df = df[df["round_id"].isin(keep)]
    res = A2.fit_models(df, p)
    res["kind"] = a.kind
    res["A2i_informative_rounds_kept_before_set_restriction"] = len(keep)
    res["A2i_rounds_in_table"] = int(n_before)
    C.write_result(a.out, res, __file__, a.kind, p["seed"], srcs,
                   f"A2i informative rounds only, unit={p['unit']} B={p['B']} interval={p['interval']} pred={pred}")
    e = res["controlled"]["erasure"]
    print(f"A2i[{a.kind}] beta_E {e['est']:+.4f} [{e['lo']:+.4f}, {e['hi']:+.4f}] p={e['p_boot']:.3f} rounds={res['n_rounds']} clusters={res['n_clusters']}")
    return res


if __name__ == "__main__":
    main()
