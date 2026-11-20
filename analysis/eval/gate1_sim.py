"""Methodologist eval: operating characteristics of gate1.py's decision rules on SYNTHETIC labels.
(No human labels are read, created or simulated into labels/; nothing here is written outside eval/.)
 (a) BA rule: P(bootstrap 95% lower bound > 0.5) when the AI is at chance (false pass) and at
     true BA 0.60/0.65/0.70/0.80 (power), for n_used = 20, 40, 60, prevalence 0.5 and 0.25.
     Uses gate1.balanced_acc and gate1.boot_stat unchanged.
 (b) Kappa rule: P(kappa >= 0.60) on n=20 shared items for two labelers of given accuracy vs truth,
     with 5% unsure treated as a category (gate1 primary) - uses gate1.kappa unchanged.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import gate1 as G  # noqa: E402

SEED = 777
rng = np.random.default_rng(SEED)
SIMS, B = 300, 1000
out = {"seed": SEED, "sims": SIMS, "B": B, "ba": {}, "kappa": {}}


def ai_with_ba(y, ba, rng):
    # symmetric errors: sensitivity = specificity = ba
    correct = rng.random(len(y)) < ba
    return np.where(correct, y, 1 - y)


for n in (20, 40, 60):
    for prev in (0.5, 0.25):
        for ba in (0.5, 0.6, 0.65, 0.7, 0.8):
            passes = 0
            for s in range(SIMS):
                y = (rng.random(n) < prev).astype(int)
                if y.sum() == 0 or y.sum() == n:
                    y[0] = 1 - y[0]
                yh = ai_with_ba(y, ba, rng)
                lo, hi, nb = G.boot_stat(G.balanced_acc, n, B, int(rng.integers(1 << 30)), 0.05, y, yh)
                passes += lo > 0.5
            out["ba"][f"n{n}_prev{prev}_trueBA{ba}"] = passes / SIMS
            print(f"BA n={n} prev={prev} trueBA={ba}: P(pass)={passes / SIMS:.3f}", flush=True)

for acc in (0.80, 0.85, 0.90, 0.95):
    hits, ks = 0, []
    for s in range(2000):
        t = (rng.random(20) < 0.5).astype(int)
        lab = []
        for _ in range(2):
            v = np.where(rng.random(20) < acc, t, 1 - t)
            v = np.where(rng.random(20) < 0.05, -1, v)
            lab.append(v)
        k = G.kappa(*lab)
        ks.append(k)
        hits += k >= 0.6
    # population kappa for two independent labelers of accuracy acc at prevalence .5 (no unsure)
    po = acc ** 2 + (1 - acc) ** 2
    out["kappa"][f"acc{acc}"] = {"P(kappa>=0.6)": hits / 2000, "pop_kappa_no_unsure": (po - 0.5) / 0.5,
                                 "kappa_sd_n20": float(np.nanstd(ks))}
    print(f"kappa acc={acc}: pop kappa={(po - .5) / .5:.3f} P(k>=.6 | n=20)={hits / 2000:.3f} sd={np.nanstd(ks):.3f}", flush=True)
(HERE / "gate1_sim.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
