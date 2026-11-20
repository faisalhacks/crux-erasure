"""FR [R3] 'Check before real ranks': coverage of the length- and clarity-adjusted N1 (alpha) on the
evaluator's synthetic length-confound design: zero erasure effect, length effect 0.5 on rank,
corr(E, length) = 0.3, 60 launches (~58 informative), discrete E, launch random slope on E, dense ties.
SYNTHETIC DATA ONLY.  Generator copied from analysis/eval/coverage.py synth_hard (same seeds 90000+i).
Logs alpha, N1u and N1h coverage; the [R3] guard is alpha coverage >= 93% (else N1 leaves the Holm family).
  python -I n1_length_coverage.py --R 200 --B 2000 --out analysis/n1_length_coverage.json
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import n1_winner_vs_mean as N1  # noqa: E402


def synth_hard(seed, G=60, tau=0.3, k=4, len_eff=0.5):
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
            z = 0.3 * ln + np.sqrt(1 - 0.09) * rng.normal(size=k)       # corr(E, length) = 0.3
            e = np.clip(np.round((0.5 + 0.3 * z) * nc) / nc, 0, 1)
            for q in range(rng.integers(3, 6)):
                u = slope * (e - 0.5) * 2 + (len_eff + t_len) * ln + t_cl * fl + rng.normal(size=k)
                u = np.round(u * 1.2) / 1.2
                uniq = np.unique(-u)
                rank = np.searchsorted(uniq, -u)
                for j in range(k):
                    rows.append((f"L{g}", rid, f"{rid}q{q}", j, int(rank[j]), e[j], 5 + 0.3 * ln[j], 60 + 10 * fl[j]))
    return pd.DataFrame(rows, columns=["launch_id", "round_id", "rater_id", "cand", "rank", "E", "log_len", "flesch"])


def run_check(R, B, start=0, len_eff=0.5, verbose=False):
    hit = {"alpha": 0, "N1u": 0, "N1h": 0}
    means = {"alpha": [], "N1u": [], "N1h": []}
    t0 = time.time()
    for i in range(start, start + R):
        r = N1.run(synth_hard(90000 + i, len_eff=len_eff), C.load_params('{"B": %d, "seed": %d}' % (B, i)))
        for nm, d in (("alpha", r["erasure"]), ("N1u", r["N1u"]), ("N1h", r["N1h"])):
            hit[nm] += int(d["lo"] <= 0 <= d["hi"])
            means[nm].append(d["est"])
        if verbose and i % 20 == 0:
            print(f"rep {i} {time.time() - t0:.0f}s", flush=True)
    return {"R": R, "B": B, "len_eff": len_eff, "data_seeds": f"{90000 + start}..{90000 + start + R - 1}",
            "boot_seeds": f"{start}..{start + R - 1}",
            "covers_0": hit, "coverage": {k: v / R for k, v in hit.items()},
            "false_positive_rate": {k: 1 - v / R for k, v in hit.items()},
            "mean_estimate": {k: float(np.mean(v)) for k, v in means.items()},
            "guard_93pct_alpha": bool(hit["alpha"] / R >= 0.93)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=200)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--len", type=float, default=0.5, dest="len_eff")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = run_check(a.R, a.B, a.start, a.len_eff, verbose=True)
    res["design"] = "synthetic, erasure effect 0, corr(E,len)=0.3, 60 launches (eval/coverage.py synth_hard generator)"
    p = C.write_result(a.out, res, __file__, "synthetic", f"{a.start}..{a.start + a.R - 1}", [],
                       f"N1 [R3] length-confound coverage R={a.R} B={a.B} len={a.len_eff}: alpha {res['covers_0']['alpha']}/{a.R}, "
                       f"N1u {res['covers_0']['N1u']}/{a.R}, N1h {res['covers_0']['N1h']}/{a.R}; guard>=93% {res['guard_93pct_alpha']}")
    print(res["covers_0"], res["coverage"], "guard", res["guard_93pct_alpha"], p)
    return res


if __name__ == "__main__":
    main()
