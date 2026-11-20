"""FR s2 second half: confirm the rank direction from the sign of the within-rater association between
numerical_ranks and the rater's own ratings.agreement (1-7).  Uses NO erasure score and no statement
text.  If 0 = best, a statement ranked better (smaller rank) should get HIGHER agreement, so the
within-(rater, round) slope of agreement on rank is NEGATIVE.
Source: pilots/T3_1/features.parquet (columns rank, agree built by s05 from the eligible groups of
FR s2; hash logged).  Estimate: pooled OLS slope after demeaning within (rater, round); also the
count of rater-rounds with Spearman < 0 / > 0.  Launch-cluster bootstrap B=2000, default_rng(20261126).
Output JSON; kind label 'exp0-rank-vs-rating' (not an erasure analysis; no GATE1 lock applies)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402

f = pd.read_parquet(C.PILOT / "features.parquet", columns=["round_id", "launch_id", "rater", "cand", "rank", "agree"])
f = f.dropna(subset=["agree"])
g = f.groupby(["round_id", "rater"], sort=False)
f["nr"] = g["rank"].transform("nunique")
f["na"] = g["agree"].transform("nunique")
f = f[(f.nr > 1) & (f.na > 1)].copy()
g = f.groupby(["round_id", "rater"], sort=False)
f["xr"] = f["rank"] - g["rank"].transform("mean")
f["ya"] = f["agree"] - g["agree"].transform("mean")
codes, nc = C.cluster_codes(f["launch_id"])
X = f[["xr"]].to_numpy(float)
est, bs = C.ols_cluster_boot(X, f["ya"].to_numpy(float), codes, nc, 2000, 20261126)
s = C.summarize(est[0], bs[:, 0])
sp = f.groupby(["round_id", "rater"], sort=False).apply(
    lambda d: d["rank"].rank().corr(d["agree"].rank()), include_groups=False).dropna()
res = {"n_rater_rounds": int(f.groupby(["round_id", "rater"]).ngroups), "n_launches": int(nc),
       "slope_agreement_on_rank": s, "rater_rounds_spearman_negative": int((sp < 0).sum()),
       "rater_rounds_spearman_positive": int((sp > 0).sum()), "rater_rounds_spearman_zero_or_nan": int(len(sp) - (sp < 0).sum() - (sp > 0).sum()),
       "reading": ("NEGATIVE slope (CI below 0) => lower rank number = higher agreement => 0 = best CONFIRMED"
                   if s["hi"] < 0 else "POSITIVE slope => 0 = worst" if s["lo"] > 0 else "UNRESOLVED (CI includes 0)")}
out = C.A / "exp0_rank_direction.json"
out.write_text(json.dumps(res, indent=1), encoding="utf-8")
run_log.log_run(__file__, "exp0-rank-vs-rating", 20261126, [C.PILOT / "features.parquet"], str(out), res["reading"])
print(json.dumps(res, indent=1))
