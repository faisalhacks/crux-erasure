"""FR s7 interval-method check: coverage of three interval methods for the A2 primary coefficient
(beta_E, controlled model) over within-rater reshuffles of real Habermas rankings (FR 6.5
shuffle, seeds 800000+i) with DUMMY E proxy (no AI score exists).  Methods: percentile (current),
bca (cluster BCa), wild (Rademacher wild cluster bootstrap-t).  Every method sees the same design
and the same reshuffle.  Usage: coverage_interval.py --R 400 --B 2000 --out FILE.json
Selection rule (orchestrator): choose coverage >= 93% closest to 95%; if none reaches 93%, most
conservative (highest coverage) and log as a limitation."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402
import run_log  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--R", type=int, default=400)
ap.add_argument("--B", type=int, default=2000)
ap.add_argument("--start", type=int, default=800000)
ap.add_argument("--out", required=True)
a = ap.parse_args()
METHODS = ("percentile", "bca", "wild")
base = C.load_habermas_shuffled(424242)
hits = {m: 0 for m in METHODS}
below = {m: 0 for m in METHODS}   # CI entirely above 0 -> truth below
above = {m: 0 for m in METHODS}
width = {m: [] for m in METHODS}
t0 = time.time()
for i in range(a.R):
    d = C.shuffle_ranks(base, a.start + i)
    p = C.load_params(json.dumps({"B": a.B, "seed": i}))
    X, y, codes, nc = A2.fit_models(d, p, design_only=True)
    for m in METHODS:
        r = C.ols_cluster_ci(X, y, codes, nc, a.B, i, 0.05, m)[0]
        hits[m] += r["lo"] <= 0 <= r["hi"]
        below[m] += r["lo"] > 0
        above[m] += r["hi"] < 0
        width[m].append(r["hi"] - r["lo"])
    if (i + 1) % 20 == 0:
        print(i + 1, {m: f"{hits[m]}/{i + 1}" for m in METHODS}, f"{time.time() - t0:.0f}s", flush=True)
res = {"R": a.R, "B": a.B, "shuffle_seeds": f"{a.start}..{a.start + a.R - 1}", "E": "DUMMY proxy 1/(1+markers/100w)",
       "methods": {m: {"coverage": hits[m] / a.R, "covered": hits[m], "ci_all_above_0": below[m], "ci_all_below_0": above[m],
                       "mean_width": float(np.mean(width[m]))} for m in METHODS}}
Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8")
run_log.log_run(__file__, "shuffled", f"{a.start}..{a.start + a.R - 1}", C.HAB_SOURCES, a.out,
                "FR7 interval check " + "; ".join(f"{m} {hits[m]}/{a.R}" for m in METHODS) + f" B={a.B}")
print(json.dumps(res, indent=1))
