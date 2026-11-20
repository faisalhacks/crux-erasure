"""R5 proposal, step 3: design calculation on SYNTHETIC labels only (no label, score or rank is read).
Pass rate of the step-3 SUPPORTED rule (one-sided Fisher exact p <= 0.05 on the Q1 = yes items) and of the
CONTRADICTED rule (balanced accuracy point estimate <= 0.5), for n Q1-yes items, share of author 'not
acknowledged', and a scorer that matches the author with probability acc on every item.
Output: analysis/planning/r5_step3_power.json. Seed 777, 4,000 simulations per cell.
"""
import json
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

import sys

# --usable (statistician condition 7, D50): apply the R5 usable rule (>= 3 items in each author class among the
# Q1-yes items); such samples count as UNUSABLE, never as SUPPORTED/CONTRADICTED. Output r5_step3_power_usable.json.
APPLY_USABLE = "--usable" in sys.argv
rng = np.random.default_rng(777)
SIMS = 4000
res = []
for n in (10, 12, 15, 20, 25):
    for share in (0.5, 0.75):
        for acc in (0.5, 0.7, 0.8, 0.9):
            sup = con = one = unus = 0
            for _ in range(SIMS):
                h = rng.random(n) < share
                s = np.where(rng.random(n) < acc, h, ~h)
                a, b = int((h & s).sum()), int((h & ~s).sum())
                c, d = int((~h & s).sum()), int((~h & ~s).sum())
                if APPLY_USABLE and ((a + b) < 3 or (c + d) < 3):   # R5 usable rule: >= 3 per author class
                    unus += 1
                    continue
                if (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
                    p = 1.0
                    one += 1
                else:
                    p = fisher_exact([[a, b], [c, d]], alternative="greater")[1]
                if (a + b) and (c + d):
                    ba = 0.5 * (a / (a + b) + d / (c + d))
                else:
                    ba = 0.5
                sup += p <= 0.05
                con += ba <= 0.5
            res.append({"n_q1_yes": n, "share_not_ack": share, "acc": acc,
                        "p_supported": round(sup / SIMS, 3), "p_contradicted": round(con / SIMS, 3),
                        "p_one_class": round(one / SIMS, 3), "p_unusable": round(unus / SIMS, 3)})
out = Path(__file__).resolve().parent / ("r5_step3_power_usable.json" if APPLY_USABLE else "r5_step3_power.json")
out.write_text(json.dumps({"seed": 777, "sims": SIMS, "usable_rule_applied": APPLY_USABLE,
                           "rule": "SUPPORTED: one-sided Fisher p<=0.05; CONTRADICTED: BA point <= 0.5",
                           "cells": res}, indent=1), encoding="utf-8")
for r in res:
    print(r)
