"""Statistician council check for R5 step 2. SYNTHETIC ONLY: reads no project data.
Questions: (a) Hsplit prevalence under plausible synthetic rating models;
(b) BA2 interval width / PASS probability; (c) group-size confound: scorer with
NO tracking of Hsplit but crux prob rising with member count; (d) scorer that
almost always finds a crux."""
import json
import numpy as np

rng = np.random.default_rng(4242)
N_LAUNCH = 721
N_ROUNDS = 1622
SIZE_P = np.array([4, 196, 1422]) / 1622.0  # rated 3/4/5 (counts from r5_feasibility.json)


def make_data(polar_sd, mean_sd):
    launch = np.sort(rng.integers(0, N_LAUNCH, N_ROUNDS))
    n = rng.choice([3, 4, 5], size=N_ROUNDS, p=SIZE_P)
    hs = np.zeros(N_ROUNDS, int)
    sdv = np.zeros(N_ROUNDS)
    for r in range(N_ROUNDS):
        mu = rng.normal(0.8, mean_sd)          # question/round mean lean
        s = abs(rng.normal(0, polar_sd)) + 0.3  # round heterogeneity
        v = np.clip(np.rint(rng.normal(mu, s, n[r])), -3, 3)
        hs[r] = int((v >= 1).any() and (v <= -1).any())
        sdv[r] = v.std()
    return launch, n, hs, sdv


def ba(s, h):
    if h.min() == h.max():
        return 0.5
    return 0.5 * (s[h == 1].mean() + (1 - s[h == 0]).mean())


def boot(launch, s, h, B=1000):
    ul = np.unique(launch)
    idx = {l: np.where(launch == l)[0] for l in ul}
    out = np.empty(B)
    for b in range(B):
        pick = rng.choice(ul, size=len(ul), replace=True)
        ii = np.concatenate([idx[l] for l in pick])
        out[b] = ba(s[ii], h[ii])
    return np.percentile(out, [2.5, 97.5])


res = {"note": "synthetic only; no project data read", "cells": []}
for polar_sd, mean_sd in [(0.8, 1.0), (1.5, 1.2), (2.5, 1.5)]:
    launch, n, hs, sdv = make_data(polar_sd, mean_sd)
    prev = hs.mean()
    cell = {"polar_sd": polar_sd, "mean_sd": mean_sd, "hsplit_prev": round(prev, 3),
            "n_hsplit0": int((hs == 0).sum()), "scorers": []}
    # scorer types: (name, P(S=1|H=1), P(S=1|H=0)) plus size-confounded null
    for name, p1, p0 in [("null_high_crux", 0.95, 0.95), ("weak", 0.95, 0.85),
                         ("moderate", 0.90, 0.65), ("good", 0.85, 0.45)]:
        s = (rng.random(N_ROUNDS) < np.where(hs == 1, p1, p0)).astype(int)
        lo, hi = boot(launch, s, hs, B=500)
        cell["scorers"].append({"scorer": name, "BA2": round(ba(s, hs), 3),
                                "ci": [round(lo, 3), round(hi, 3)]})
    # size confound: no tracking, but P(S=1) = .70/.80/.95 for 3/4/5 rated
    ps = np.select([n == 3, n == 4, n == 5], [0.70, 0.80, 0.95])
    s = (rng.random(N_ROUNDS) < ps).astype(int)
    lo, hi = boot(launch, s, hs, B=500)
    cell["scorers"].append({"scorer": "null_size_confounded", "BA2": round(ba(s, hs), 3),
                            "ci": [round(lo, 3), round(hi, 3)]})
    res["cells"].append(cell)

with open(__file__.replace(".py", ".json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
