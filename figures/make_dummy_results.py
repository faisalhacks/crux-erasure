"""Write DUMMY result JSONs for figure testing. Numbers are invented placeholders (kind="dummy").
Schemas mirror analysis/gate1.py, a2_within_round.py, n1_winner_vs_mean.py outputs; tier-2/N2 schemas are
defined in figures/README.md. Never use these numbers in any report."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent / "dummy"
D.mkdir(exist_ok=True)


def w(name, obj):
    obj["kind"] = "dummy"
    (D / name).write_text(json.dumps(obj, indent=1), encoding="utf-8")


def est(e, lo, hi):
    return {"est": e, "lo": lo, "hi": hi}


w("gate1.json", {
    "kappa": {"n_shared": 20, "primary": 0.62, "primary_ci_info_only": [0.30, 0.85], "unsure_L1": 1,
              "unsure_L2": 2, "cutoff": 0.6, "pass": True},
    "balanced_accuracy": {"n_used": 57, "n_unsure_excluded": 3, "ba": 0.72, "lo": 0.60, "hi": 0.83,
                          "must_exceed": 0.5, "pass": True},
    "verdict": "PASS"})
w("a2.json", {"n_clusters": 300, "unit": "rater", "B": 2000, "seed": 20261115,
              "controlled": {"erasure": {**est(0.20, 0.08, 0.32)}, "length": est(0.03, -0.08, 0.14),
                             "clarity": est(0.10, -0.01, 0.21)},
              "uncontrolled": {"erasure": est(0.22, 0.10, 0.34)}})
w("n1.json", {"unit": "rater", "n_clusters": 300, "B": 2000, "seed": 20261115,
              "erasure": {**est(0.30, 0.12, 0.48), "est_in_within_round_SD": 0.35},
              "length": est(0.02, -0.14, 0.18), "clarity": est(0.08, -0.08, 0.24)})
# Tier-2 generic effect files: est/lo/hi in the same units as A2 erasure coefficient
w("a4.json", {"n_clusters": 300, "controlled": {"erasure": est(0.17, 0.04, 0.30)}})  # a2-format, second scorer
w("a3.json", {"n_clusters": 80, "erasure": est(0.25, -0.05, 0.55)})
w("n3.json", {"n_clusters": 60, "erasure": est(0.05, -0.30, 0.40)})
w("n4.json", {"n_clusters": 150, "minority": est(0.28, 0.05, 0.51), "majority": est(0.10, -0.08, 0.28)})
cells = {}
for k, (m, s) in {"keep_all_satisfied|common_ground": (0.62, 0.05), "keep_all_satisfied|show_disagreement": (0.48, 0.05),
                  "accurate_differences|common_ground": (0.45, 0.05), "accurate_differences|show_disagreement": (0.25, 0.05)}.items():
    cells[k] = {"mean": m, "lo": m - 1.96 * s, "hi": m + 1.96 * s, "n_clusters": 40}
w("n2.json", {"measure": "mean erasure score of generated statement (0-1)", "cells": cells})
print("ok")
