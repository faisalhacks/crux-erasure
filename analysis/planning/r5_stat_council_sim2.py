"""Statistician council check, part 2. SYNTHETIC ONLY. Extreme class imbalance:
Hsplit=0 in only k rounds (k = 30, 50, 100) of 1,622; launch-cluster bootstrap of BA2;
P(PASS) under the R5 rule (LB > 0.5 and point >= 0.60) and P(LB > 0.5)."""
import json
import numpy as np

rng = np.random.default_rng(4243)
N_LAUNCH, N_ROUNDS, B, SIMS = 721, 1622, 400, 150


def ba(s, h):
    if h.min() == h.max():
        return 0.5
    return 0.5 * (s[h == 1].mean() + (1 - s[h == 0]).mean())


out = []
for k in (30, 50, 100):
    for name, p1, p0 in [("null", 0.95, 0.95), ("ba0.60", 0.95, 0.75), ("ba0.65", 0.95, 0.65)]:
        npass = nlb = 0
        widths = []
        for _ in range(SIMS):
            launch = np.sort(rng.integers(0, N_LAUNCH, N_ROUNDS))
            h = np.ones(N_ROUNDS, int)
            h[rng.choice(N_ROUNDS, k, replace=False)] = 0
            s = (rng.random(N_ROUNDS) < np.where(h == 1, p1, p0)).astype(int)
            ul = np.unique(launch)
            idx = {l: np.where(launch == l)[0] for l in ul}
            bs = np.empty(B)
            for b in range(B):
                ii = np.concatenate([idx[l] for l in rng.choice(ul, len(ul))])
                bs[b] = ba(s[ii], h[ii])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            pt = ba(s, h)
            widths.append(hi - lo)
            nlb += lo > 0.5
            npass += (lo > 0.5) and (pt >= 0.60)
        out.append({"k_hsplit0": k, "scorer": name, "true_BA": round(0.5 * (p1 + 1 - p0), 3),
                    "p_LB_gt_0.5": round(nlb / SIMS, 3), "p_PASS": round(npass / SIMS, 3),
                    "mean_ci_width": round(float(np.mean(widths)), 3)})
        print(out[-1], flush=True)

with open(__file__.replace(".py", ".json"), "w", encoding="utf-8") as f:
    json.dump({"note": "synthetic only", "sims": SIMS, "B": B, "cells": out}, f, indent=1)
