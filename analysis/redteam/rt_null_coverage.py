"""Red-team: size of the A2 interval of record under the REAL, sparse E (150 informative rounds in 142 launches).
FR s7 [R2] checked coverage only with a dummy, densely varying E proxy.  Here: within-rater shuffles of the real ranks
(common.shuffle_ranks, random.Random(910000 + i)), real scorer-1 E and controls, A2 primary model, wild cluster
bootstrap-t (project code), B = 999.  Reports the share of 95% intervals covering 0 and of p < 0.05.
Read-only on project files; writes analysis/redteam/rt_null_coverage.json.  Usage: python -I -B rt_null_coverage.py [R]"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402

R = int(sys.argv[1]) if len(sys.argv) > 1 else 200
df = C.read_long(str(HERE.parent / "scores" / "a2_long_real.parquet"))[0]
p = C.load_params(None)
p["_kind"] = None
df, _ = C.restrict_confirmatory(df, p, None)
cover, rej, ests, ses = 0, 0, [], []
for i in range(R):
    d = C.shuffle_ranks(df, 910000 + i)
    X, y, codes, nc = A2.fit_models(d, {**p, "include_dev": True}, design_only=True)   # already restricted above
    r = C.ols_cluster_ci(X, y, codes, nc, 999, 5000 + i, 0.05, "wild")[0]
    cover += int(r["lo"] <= 0 <= r["hi"])
    rej += int(r["p_boot"] < 0.05)
    ests.append(r["est"]); ses.append(r["se"])
res = {"R": R, "B": 999, "coverage_of_0": cover / R, "share_p_lt_005": rej / R, "sd_null_est": float(np.std(ests, ddof=1)),
       "mean_cr1_se": float(np.mean(ses)), "mean_null_est": float(np.mean(ests))}
(HERE / "rt_null_coverage.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
