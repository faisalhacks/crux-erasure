"""Methodologist eval: FAST reshuffle coverage for A2 (controlled, A2h, uncontrolled) and N1, current code.

Under a within-(round, rater) reshuffle only the outcome moves: E, controls, fixed effects, clusters,
all-tied-rater drops are invariant.  So the author's design is built ONCE (C.add_y, C.zscore,
C.fe_demean exactly as A2.fit_models does), and each replicate permutes the rank column within
rater-round, recomputes y/midranks, and calls the author's C.ols_cluster_boot / C.ratio_cluster_boot
/ C.summarize.  --verify runs both paths on the same permutation and asserts identical results
against A2.fit_models and N1.run (unchanged author code).
Also computes CR1 and BCa for A2 controlled beta_E from the same bootstrap draws.
Usage: python -I coverage_fast.py --R 200 --B 2000 --out cov_reshuffle_fast.json [--verify]
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

CODE = [HERE / "coverage_fast.py", HERE.parent / "common.py", HERE.parent / "a2_within_round.py",
        HERE.parent / "n1_winner_vs_mean.py"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


CODE_SHA = {p.name: sha(p) for p in CODE}


class Fast:
    def __init__(self, base, p):
        self.p = p
        d = base.reset_index(drop=True).copy()
        d["_g"] = pd.factorize(pd.Series(list(zip(d.round_id, d.rater_id))))[0]
        self.d = d
        self.g = d["_g"].to_numpy()
        self.idx_sorted = np.argsort(self.g, kind="stable")
        self.rank0 = d["rank"].to_numpy()

    def permute(self, seed):
        rng = np.random.default_rng(seed)
        order = np.lexsort((rng.random(len(self.g)), self.g))
        new = np.empty_like(self.rank0)
        new[self.idx_sorted] = self.rank0[order]
        return new

    def a2(self, rank, seed, verify_df=None):
        p = self.p
        d = self.d.copy()
        d["rank"] = rank
        dd, _ = C.add_y(d, "rater")
        ctr = list(p["controls"])
        for c in ctr:
            dd["z_" + c] = C.zscore(dd, c)
        codes, nc = C.cluster_codes(dd["launch_id"])
        y = C.fe_demean(dd, ["y"])["y"]
        res = {}
        for name, cols in {"controlled": ["E"] + ["z_" + c for c in ctr], "uncontrolled": ["E"],
                           "A2h": ["E", "z_" + ctr[0]]}.items():
            Xd = C.fe_demean(dd, cols)
            X = np.column_stack([Xd[c] for c in cols])
            est, bs = C.ols_cluster_boot(X, y, codes, nc, p["B"], seed)
            res[name] = C.summarize(est[0], bs[:, 0], p["alpha"])
            if name == "controlled":
                XtX, Xty = C.cluster_sums(X, y, codes, nc)
                A_ = XtX.sum(0)
                b = np.linalg.solve(A_, Xty.sum(0))
                sc = Xty - np.einsum("cij,j->ci", XtX, b)
                Ai = np.linalg.inv(A_)
                n, k = X.shape
                V = nc / (nc - 1) * (n - 1) / (n - k) * Ai @ (sc.T @ sc) @ Ai
                se = np.sqrt(V[0, 0])
                tq = stats.t.ppf(0.975, nc - 1)
                res["cr1"] = (b[0] - tq * se, b[0] + tq * se)
                jk = np.linalg.solve(A_[None] - XtX, (Xty.sum(0)[None] - Xty)[..., None])[..., 0][:, 0]
                jm = jk.mean()
                acc = ((jm - jk) ** 3).sum() / (6 * (((jm - jk) ** 2).sum()) ** 1.5)
                z0 = stats.norm.ppf(np.clip((bs[:, 0] < b[0]).mean(), 1e-6, 1 - 1e-6))
                q = [stats.norm.cdf(z0 + (z0 + z) / (1 - acc * (z0 + z))) for z in stats.norm.ppf([0.025, 0.975])]
                res["bca"] = tuple(np.percentile(bs[:, 0], [100 * q[0], 100 * q[1]]))
                res["bootSE_over_CR1"] = float(bs[:, 0].std(ddof=1) / se)
                if hasattr(C, "wild_cluster_t"):  # author's method of record since D19
                    _, _, wlo, whi, _ = C.wild_cluster_t(XtX, Xty, p["B"], seed, 0.05)
                    res["wild"] = (float(wlo[0]), float(whi[0]))
        return res, nc

    def n1(self, rank, seed):
        d = self.d.copy()
        d["rank"] = rank
        D, nm, nt = N1.round_deltas(d, self.p)
        codes, nc = C.cluster_codes(D["launch_id"])
        den = np.bincount(codes, minlength=nc).astype(float)
        num = np.bincount(codes, weights=D["E"].to_numpy(float), minlength=nc)
        est, bs = C.ratio_cluster_boot(num, den, self.p["B"], seed)
        return C.summarize(est, bs, self.p["alpha"]), nt, len(D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=200)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--no_n1", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    base = C.load_habermas_shuffled()
    p = C.load_params(json.dumps({"B": a.B, "unit": "rater"}))
    F = Fast(base, p)
    if a.verify:
        for s in (1, 2):
            rk = F.permute(80000 + s)
            df = F.d.drop(columns="_g").copy()
            df["rank"] = rk
            ref = A2.fit_models(df, dict(p, seed=s, interval="percentile"))
            mine, _ = F.a2(rk, s)
            for m in ("controlled", "uncontrolled", "A2h"):
                for key in ("est", "lo", "hi", "p_boot"):
                    assert abs(ref[m]["erasure"][key] - mine[m][key]) < 1e-12, (m, key, ref[m]["erasure"][key], mine[m][key])
            refn = N1.run(df, dict(p, seed=s, interval="percentile"))
            myn, _, _ = F.n1(rk, s)
            for key in ("est", "lo", "hi"):
                assert abs(refn["erasure"][key] - myn[key]) < 1e-12, (key, refn["erasure"][key], myn[key])
        print("VERIFY OK: fast path == A2.fit_models and N1.run on 2 permutations", flush=True)
    recs = []
    for s in range(a.start, a.start + a.R):
        rk = F.permute(90000 + s)
        r, nc = F.a2(rk, s)
        rec = {"rep": s}
        for m in ("controlled", "uncontrolled", "A2h"):
            rec[f"A2_{m}"] = bool(r[m]["lo"] <= 0 <= r[m]["hi"])
            rec[f"A2_{m}_p_lt_05"] = bool(r[m]["p_boot"] < 0.05)
            rec[f"A2_{m}_est"] = r[m]["est"]
        for k in ("cr1", "bca", "wild"):
            if k in r:
                rec[f"A2_controlled_{k}"] = bool(r[k][0] <= 0 <= r[k][1])
        rec["bootSE_over_CR1"] = r["bootSE_over_CR1"]
        if not a.no_n1:
            n, nt, nr = F.n1(rk, s)
            rec["N1"] = bool(n["lo"] <= 0 <= n["hi"])
            rec["N1_est"] = n["est"]
            rec["N1_tied_excluded"] = nt
            rec["N1_rounds_used"] = nr
        recs.append(rec)
        if (s - a.start) % 20 == 0:
            print(f"rep {s} {time.time() - t0:.0f}s", flush=True)
    D = pd.DataFrame(recs)
    summ = {}
    for c in D.columns:
        if D[c].dtype == bool:
            x, n_ = int(D[c].sum()), len(D)
            ci = stats.binomtest(x, n_).proportion_ci(confidence_level=0.95, method="exact")
            summ[c] = {"k": x, "n": n_, "rate": x / n_, "clopper_pearson_95": [ci.low, ci.high]}
        elif c != "rep":
            summ[c] = {"mean": float(D[c].mean()), "sd": float(D[c].std())}
    meta = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "R": a.R, "B": a.B, "perm_seeds": f"numpy default_rng {90000 + a.start}..{90000 + a.start + a.R - 1}",
            "boot_seeds": f"{a.start}..{a.start + a.R - 1}", "verified_against_author_code": a.verify,
            "code_sha256_16": CODE_SHA, "code_changed_during_run": {p_.name: sha(p_) for p_ in CODE} != CODE_SHA,
            "input_sha256_16": {Path(x).name: sha(x) for x in C.HAB_SOURCES},
            "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                         "scipy": scipy.__version__}, "seconds": round(time.time() - t0, 1)}
    Path(a.out).write_text(json.dumps({"meta": meta, "summary": summ, "reps": recs}, indent=1, default=float), encoding="utf-8")
    with open(HERE / "EVAL_RUNS.md", "a", encoding="utf-8", newline="\n") as f:
        f.write(f"| {meta['utc']} | coverage_fast.py | shuffled | {meta['perm_seeds']}; boot {meta['boot_seeds']} | "
                f"{json.dumps(CODE_SHA)} changed={meta['code_changed_during_run']} | {json.dumps(meta['input_sha256_16'])} | "
                f"{a.out} | R={a.R} B={a.B} verify={a.verify} {meta['versions']} |\n")
    for c, v in summ.items():
        print(c, json.dumps(v))


if __name__ == "__main__":
    main()
