"""FR 7.1 [R1][R4] A2 informativeness tier, computed from scorer output and SHUFFLED ranks only.
Input: long table (schema in common.py) holding scorer-1 E.  The real rank column is never used:
every null fit permutes each rater's ranks with random.Random(430000 + i) (common.shuffle_ranks,
i = 0..399) before anything is computed.
  R_inf = informative rounds (>= 2 distinct E among the round's candidates, E present)
  K_inf = launches with >= 1 informative round
  MDE80 = 2.80 * SD of beta_E point estimates over the 400 null fits (A2 primary model, 0-1 y scale)
  tier: INFORMATIVE  K_inf >= 100 and MDE80 <= 0.10 ; LOW-POWER K_inf >= 50 ; else NOT MEASURABLE
[R4] The tier of record is computed on the CONFIRMATORY set (the 150 development launches excluded, FR 7.1 / s2):
R_inf, K_inf, the null fits and MDE80 all use that set, z-scoring constants included (fit_models restricts it).
Side figures, never the tier: the same counts including the development launches (and for E_pos / E2).
Thresholds 50/100/0.10 are fixed (FR 7.1).  kind=real additionally requires the table to hold 871 launches and the
confirmatory set to hold 721 (FR s2), else it refuses.
Writes P/gate1/A2_TIER_R4.json (kind real; write-once; the pre-R4 all-launch A2_TIER.json is kept and not read);
for tests use --kind dummy --out elsewhere.  --include-dev computes the all-launch version (sensitivity, labelled).
The one-way downgrade after unblinding (2.80 x real-rank SE > 0.10) is applied by the A2 run, not here."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402
import run_log  # noqa: E402

NFIT = 400
SEED0 = 430000
K_INFO, K_LOW, MDE_MAX = 100, 50, 0.10


def counts(df, col):
    d = df.drop_duplicates(["round_id", "cand"]).dropna(subset=[col])
    ok = d.groupby("round_id")[col].transform("size") == d.groupby("round_id")["cand"].transform("nunique")
    d = d[ok]
    inf = d.groupby("round_id")[col].nunique() >= 2
    rounds = d.drop_duplicates("round_id").set_index("round_id")["launch_id"]
    ir = inf[inf].index
    return {"rounds_in_set": int(d["round_id"].nunique()), "R_inf": int(len(ir)),
            "K_inf": int(rounds.loc[ir].nunique()) if len(ir) else 0}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--kind", required=True, choices=("dummy", "real"))
    ap.add_argument("--out", default=str(C.GATE / C.TIER_FILE))
    ap.add_argument("--nfit", type=int, default=NFIT)
    ap.add_argument("--include-dev", dest="include_dev", action="store_true",
                    help="sensitivity: all launches (labelled; may not write the file of record)")
    a = ap.parse_args(argv)
    rec = (C.GATE / C.TIER_FILE).resolve()
    if a.kind == "real" and a.input in ("HABERMAS_SHUFFLED",):
        sys.exit("kind=real needs a scorer-1 E table, not the dummy-E loader")
    if a.kind == "dummy" and Path(a.out).resolve() == rec:
        sys.exit(f"dummy runs may not write P/gate1/{C.TIER_FILE}")
    if a.include_dev and Path(a.out).resolve() == rec:
        sys.exit("--include-dev (all launches) is a sensitivity figure and may not write the tier of record")
    if a.kind == "real" and Path(a.out).exists():
        sys.exit(f"REFUSED (L3): {Path(a.out).name} is write-once for kind=real; it exists.")
    df_all, srcs = C.read_long(a.input, a.kind)
    p = C.load_params(json.dumps({"B": 10, "include_dev": bool(a.include_dev), "_kind": a.kind}))
    df, aset = C.restrict_confirmatory(df_all, p, a.kind)
    if a.kind == "real" and not a.include_dev:
        if (aset["n_launches_in"], aset["n_launches_out"]) != (C.N_ALL_LAUNCHES, C.N_CONFIRMATORY_LAUNCHES):
            sys.exit(f"REFUSED (FR s2 R4): table has {aset['n_launches_in']} launches, confirmatory set "
                     f"{aset['n_launches_out']}; expected {C.N_ALL_LAUNCHES} and {C.N_CONFIRMATORY_LAUNCHES}.")
    pg = C.PILOT / "pilot_groups.jsonl"
    if pg.exists():
        srcs = list(srcs) + [pg]
    out = {"kind": a.kind, "analysis_set": aset,
           "tier_of_record_set": "all launches (SENSITIVITY, not the tier of record)" if a.include_dev else "confirmatory set (development launches excluded)",
           "counts": counts(df, "E"),
           "counts_including_development_launches": counts(df_all, "E"),
           "counts_other": {c: counts(df, c) for c in ("E_pos", "E2") if c in df},
           "counts_other_including_development_launches": {c: counts(df_all, c) for c in ("E_pos", "E2") if c in df_all}}
    ests = []
    for i in range(a.nfit if out["counts"]["R_inf"] > 0 else 0):
        d = C.shuffle_ranks(df, SEED0 + i)
        X, y, codes, nc = A2.fit_models(d, p, design_only=True)
        ests.append(np.linalg.solve(X.T @ X, X.T @ y)[0])
    sd = float(np.std(ests, ddof=1)) if len(ests) > 1 else float("nan")
    mde = 2.80 * sd
    K = out["counts"]["K_inf"]
    tier = "INFORMATIVE" if (K >= K_INFO and mde <= MDE_MAX and mde == mde) else "LOW-POWER" if K >= K_LOW else "NOT MEASURABLE"
    out.update({"R_inf": out["counts"]["R_inf"], "K_inf": K, "SD_null_beta_E": sd, "MDE80": mde, "n_null_fits": a.nfit,
                "null_beta_E_mean": float(np.mean(ests)) if ests else None, "shuffle_seeds": f"random.Random({SEED0}+i), i=0..{a.nfit - 1}",
                "thresholds": {"K_informative": K_INFO, "K_low_power": K_LOW, "MDE80_max": MDE_MAX}, "tier": tier,
                "disclosure": "The all-launch tier of D35 (K_inf=168, MDE80=0.0509, INFORMATIVE; 144 informative launches outside the "
                              "development set) was logged before this row was written; thresholds were fixed in R1 and are unchanged "
                              "(FR 7.1).",
                "note": "computed from shuffled ranks only; one-way downgrade after unblinding is applied by the A2 run (FR 7.1)"})
    note = f"A2 tier={tier} K_inf={K} R_inf={out['R_inf']} MDE80={mde:.4f} set={aset['set']}"
    seeds = f"{SEED0}..{SEED0 + a.nfit - 1}"
    if a.kind == "real":   # fixed name read by the lock: exclusive create + sidecar, never overwritten
        out["gate_tag"] = "NOT_REAL_RANKS(shuffled)"
        C.write_new(a.out, json.dumps(out, indent=1, default=float))
        run_log.log_run(__file__, "shuffled", seeds, srcs, a.out, note)
    else:
        C.write_result(a.out, out, __file__, "dummy", seeds, srcs, note)
    print(json.dumps({k: out[k] for k in ("R_inf", "K_inf", "SD_null_beta_E", "MDE80", "tier")}))
    return out


if __name__ == "__main__":
    main()
