"""Methodologist eval: empirical 95% CI coverage of A2 and N1 (CURRENT code, FR-aligned) under known nulls.

Modes
  reshuffle  : pilot Habermas statements/raters, ranks re-shuffled with the AUTHOR'S C.shuffle_ranks
               (random.Random(seed), within rater) using a fresh seed per replicate. E is the author's
               DUMMY text proxy. No real rank order is related to anything.
  synth      : author's C.make_synth null (300 launches x 2 rounds, launch shock), fresh seed per replicate.
  synth_hard : own generator. Null on average for E but harder: G launches, 1-3 rounds per launch,
               3-5 raters per round, k=4, DISCRETE E (share of 1-4 cruxes, so many rounds have no E
               variation), launch-level random slope on E (mean 0, sd tau), launch-level taste on
               length/clarity, dense-coded ties as in the real data. len_eff = fixed length effect,
               with E correlated with length (0.3) -> N1 (no controls) is biased when len_eff != 0.
For each replicate the AUTHOR'S A2.fit_models / N1.run are called unchanged (percentile launch
bootstrap, B, seed = replicate index).  For A2 'controlled' beta_E we also compute, from the same
design, CR1 cluster-robust t interval, normal interval from bootstrap SE, and BCa.
Usage: python -I coverage.py --mode reshuffle --R 100 --start 0 --B 10000 --out cov.json
"""
import argparse
import datetime
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy  # noqa: E402
from scipy import stats  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402
import n1_winner_vs_mean as N1  # noqa: E402

CODE = [HERE / "coverage.py", HERE.parent / "common.py", HERE.parent / "a2_within_round.py",
        HERE.parent / "n1_winner_vs_mean.py"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


CODE_SHA_AT_START = {p.name: sha(p) for p in CODE}


def synth_hard(seed, G=60, tau=0.3, k=4, len_eff=0.0):
    rng = np.random.default_rng(seed)
    rows = []
    for g in range(G):
        slope = rng.normal(0, tau)
        t_len, t_cl = rng.normal(0, 0.5, size=2)
        for r in range(rng.integers(1, 4)):
            rid = f"L{g}R{r}"
            ln = rng.normal(size=k)
            fl = rng.normal(size=k)
            nc = rng.integers(1, 5)
            z = 0.3 * ln + np.sqrt(1 - 0.09) * rng.normal(size=k)
            e = np.clip(np.round((0.5 + 0.3 * z) * nc) / nc, 0, 1)
            for q in range(rng.integers(3, 6)):
                u = slope * (e - 0.5) * 2 + (len_eff + t_len) * ln + t_cl * fl + rng.normal(size=k)
                u = np.round(u * 1.2) / 1.2
                uniq = np.unique(-u)
                rank = np.searchsorted(uniq, -u)  # dense, 0 = best
                for j in range(k):
                    rows.append((f"L{g}", rid, f"{rid}q{q}", j, int(rank[j]), e[j], 5 + 0.3 * ln[j], 60 + 10 * fl[j]))
    return pd.DataFrame(rows, columns=["launch_id", "round_id", "rater_id", "cand", "rank", "E", "log_len", "flesch"])


def a2_alt(df, p, alpha=0.05):
    """Re-builds the A2 'controlled' design exactly as A2.fit_models does, then alt intervals."""
    pred = p["predictor"]
    miss = df.groupby("round_id")[pred].transform(lambda s: s.isna().any())
    d = df[~miss].copy()
    d, _ = C.add_y(d, p["unit"])
    ctr = list(p["controls"])
    for c in ctr:
        d["z_" + c] = C.zscore(d, c)
    codes, nc = C.cluster_codes(d["launch_id"])
    cols = [pred] + ["z_" + c for c in ctr]
    y = C.fe_demean(d, ["y"])["y"]
    Xd = C.fe_demean(d, cols)
    X = np.column_stack([Xd[c] for c in cols])
    XtX, Xty = C.cluster_sums(X, y, codes, nc)
    A_ = XtX.sum(0)
    b = np.linalg.solve(A_, Xty.sum(0))
    score = Xty - np.einsum("cij,j->ci", XtX, b)
    Ainv = np.linalg.inv(A_)
    n, kx = X.shape
    V = nc / (nc - 1) * (n - 1) / (n - kx) * Ainv @ (score.T @ score) @ Ainv
    se = np.sqrt(np.diag(V))
    tq = stats.t.ppf(1 - alpha / 2, nc - 1)
    est, bs = C.ols_cluster_boot(X, y, codes, nc, p["B"], p["seed"])  # identical draws to the author's
    bse = bs.std(0, ddof=1)
    zq = stats.norm.ppf(1 - alpha / 2)
    jk = np.linalg.solve(A_[None] - XtX, (Xty.sum(0)[None] - Xty)[..., None])[..., 0]
    jm = jk.mean(0)
    acc = ((jm - jk) ** 3).sum(0) / (6 * (((jm - jk) ** 2).sum(0)) ** 1.5)
    z0 = stats.norm.ppf(np.clip((bs < b).mean(0), 1e-6, 1 - 1e-6))
    i = 0
    zl, zh = stats.norm.ppf(alpha / 2), stats.norm.ppf(1 - alpha / 2)
    pl = stats.norm.cdf(z0[i] + (z0[i] + zl) / (1 - acc[i] * (z0[i] + zl)))
    ph = stats.norm.cdf(z0[i] + (z0[i] + zh) / (1 - acc[i] * (z0[i] + zh)))
    return {"cr1": (b[i] - tq * se[i], b[i] + tq * se[i]),
            "boot_se_normal": (b[i] - zq * bse[i], b[i] + zq * bse[i]),
            "bca": (np.percentile(bs[:, i], 100 * pl), np.percentile(bs[:, i], 100 * ph)),
            "ratio_bootSE_to_CR1": float(bse[i] / se[i])}


def cov(d):
    return bool(d["lo"] <= 0 <= d["hi"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("reshuffle", "synth", "synth_hard"))
    ap.add_argument("--R", type=int, default=200)
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--len", type=float, default=0.0)
    ap.add_argument("--units", default="rater,group")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    base = C.load_habermas_shuffled() if a.mode == "reshuffle" else None
    recs = []
    for s in range(a.start, a.start + a.R):
        data_seed = 90000 + s
        if a.mode == "reshuffle":
            df = C.shuffle_ranks(base, data_seed)
        elif a.mode == "synth":
            df = C.make_synth(seed=data_seed)
        else:
            df = synth_hard(data_seed, G=a.G, len_eff=a.len)
        rec = {"rep": s, "data_seed": data_seed}
        for unit in a.units.split(","):
            p = C.load_params(json.dumps({"B": a.B, "seed": s, "unit": unit}))
            r = A2.fit_models(df, p)
            rec["n_clusters"] = r["n_clusters"]
            rec["launches_with_E_variation"] = r["launches_with_E_variation"]
            for m in ("controlled", "uncontrolled", "A2h"):
                rec[f"A2_{unit}_{m}"] = cov(r[m]["erasure"])
                rec[f"A2_{unit}_{m}_est"] = r[m]["erasure"]["est"]
                rec[f"A2_{unit}_{m}_p"] = r[m]["erasure"]["p_boot"]
            if a.mode == "reshuffle" or (a.mode == "synth"):
                for v in ("length", "clarity"):
                    rec[f"A2_{unit}_controlled_{v}"] = cov(r["controlled"][v])
            alt = a2_alt(df, p)
            for k_ in ("cr1", "boot_se_normal", "bca"):
                lo, hi = alt[k_]
                rec[f"A2_{unit}_controlled_{k_}"] = bool(lo <= 0 <= hi)
            rec[f"A2_{unit}_ratio_bootSE_to_CR1"] = alt["ratio_bootSE_to_CR1"]
        pn = C.load_params(json.dumps({"B": a.B, "seed": s}))
        n = N1.run(df, pn)
        rec["N1"] = cov(n["erasure"])
        rec["N1_est"] = n["erasure"]["est"]
        rec["N1_tied_excluded"] = n["rounds_tied_winner_excluded"]
        rec["N1_rounds"] = n["n_rounds"]
        recs.append(rec)
        if (s - a.start) % 10 == 0:
            print(f"rep {s} done {time.time() - t0:.0f}s", flush=True)
    D = pd.DataFrame(recs)
    summ = {}
    for c in D.columns:
        if D[c].dtype == bool:
            x, n_ = int(D[c].sum()), len(D)
            ci = stats.binomtest(x, n_).proportion_ci(confidence_level=0.95, method="exact")
            summ[c] = {"covered": x, "n": n_, "rate": x / n_, "clopper_pearson_95": [ci.low, ci.high]}
    for c in D.columns:
        if c.endswith("_est") or c.endswith("ratio_bootSE_to_CR1") or c in ("N1_tied_excluded", "N1_rounds", "launches_with_E_variation"):
            summ[c] = {"mean": float(D[c].mean()), "sd": float(D[c].std())}
    code_now = {p.name: sha(p) for p in CODE}
    meta = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": a.mode, "R": a.R, "B": a.B, "start": a.start,
            "G": a.G if a.mode == "synth_hard" else None, "len_eff": a.len if a.mode == "synth_hard" else None,
            "data_seeds": f"{90000 + a.start}..{90000 + a.start + a.R - 1}",
            "boot_seeds": f"{a.start}..{a.start + a.R - 1}",
            "code_sha256_16_at_start": CODE_SHA_AT_START, "code_changed_during_run": code_now != CODE_SHA_AT_START,
            "input_sha256_16": {Path(p).name: sha(p) for p in (C.HAB_SOURCES if a.mode == "reshuffle" else [])},
            "versions": {"python": platform.python_version(), "numpy": np.__version__,
                         "pandas": pd.__version__, "scipy": scipy.__version__},
            "seconds": round(time.time() - t0, 1)}
    Path(a.out).write_text(json.dumps({"meta": meta, "summary": summ, "reps": recs}, indent=1, default=float),
                           encoding="utf-8")
    with open(HERE / "EVAL_RUNS.md", "a", encoding="utf-8", newline="\n") as f:
        f.write(f"| {meta['utc']} | coverage.py | {a.mode} | data {meta['data_seeds']}; boot {meta['boot_seeds']} | "
                f"{json.dumps(CODE_SHA_AT_START)} changed={meta['code_changed_during_run']} | "
                f"{json.dumps(meta['input_sha256_16'])} | {a.out} | R={a.R} B={a.B} G={meta['G']} len={meta['len_eff']} {meta['versions']} |\n")
    for c, v in summ.items():
        if "covered" in v:
            print(f"{c:42s} {v['covered']}/{v['n']} = {v['rate']:.3f}  CP95 [{v['clopper_pearson_95'][0]:.3f}, {v['clopper_pearson_95'][1]:.3f}]")
        else:
            print(f"{c:42s} mean {v['mean']:.4f} sd {v['sd']:.4f}")


if __name__ == "__main__":
    main()
