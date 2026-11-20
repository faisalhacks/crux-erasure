"""Methodologist eval: STRUCTURE ONLY of the pilot long table (no rank-vs-covariate relation).
Reports: candidates per round, raters per round, whether each rater ranks every candidate,
tie structure of ranks (counts only), rounds per launch, raters spanning >1 launch.
Uses the SHUFFLED loader so real rank order never leaves memory unpermuted; tie/count
structure is invariant to the within-rater permutation."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402

df = C.load_habermas_shuffled()
raw = pd.read_parquet(C.PILOT / "features.parquet")
out = {"columns_raw": list(raw.columns), "n_rows_after_dropna": int(len(df)), "n_rows_raw": int(len(raw))}
k_round = df.groupby("round_id")["cand"].nunique()
out["cands_per_round"] = k_round.value_counts().sort_index().to_dict()
rr = df.groupby(["round_id", "rater_id"])["cand"].nunique()
kr = rr.reset_index().merge(k_round.rename("k").reset_index(), on="round_id")
out["rater_rounds"] = int(len(rr))
out["rater_rounds_ranking_subset_of_round"] = int((kr["cand"] < kr["k"]).sum())
out["raters_per_round"] = df.groupby("round_id")["rater_id"].nunique().describe().round(2).to_dict()


def tie_info(r):
    v = np.sort(r.to_numpy())
    return pd.Series({"has_tie": len(np.unique(v)) < len(v), "min": v.min(), "max": v.max(), "k": len(v)})


ti = df.groupby(["round_id", "rater_id"])["rank"].apply(lambda s: tie_info(s)).unstack()
out["rater_rounds_with_ties"] = int(ti["has_tie"].astype(bool).sum())
out["rank_min_values"] = ti["min"].value_counts().to_dict()
out["rank_max_minus_k"] = (ti["max"] - ti["k"]).value_counts().to_dict()
out["rank_dtype"] = str(df["rank"].dtype)
out["rank_unique_values_sample"] = sorted(map(float, pd.unique(df["rank"])))[:20]
rpl = df.groupby("group_id")["round_id"].nunique()
out["rounds_per_launch"] = rpl.value_counts().sort_index().to_dict()
out["n_launch_clusters"] = int(df["group_id"].nunique())
lpr = df.groupby("rater_id")["group_id"].nunique()
out["raters_in_more_than_one_launch"] = int((lpr > 1).sum())
out["n_raters"] = int(len(lpr))
rows_per_cluster = df.groupby("cluster").size()
out["rows_per_cluster"] = rows_per_cluster.describe().round(1).to_dict()
# within-round variance share of the covariates (how much signal A2 can use)
for v in ("erasure", "length", "clarity"):
    cand = df.drop_duplicates(["round_id", "cand"])
    tot = cand[v].var(ddof=0)
    within = (cand[v] - cand.groupby("round_id")[v].transform("mean")).var(ddof=0)
    out[f"{v}_within_round_var_share"] = round(float(within / tot), 3)
cand = df.drop_duplicates(["round_id", "cand"]).copy()
for v in ("erasure", "length", "clarity"):
    cand[v + "_w"] = cand[v] - cand.groupby("round_id")[v].transform("mean")
out["within_round_corr_proxies"] = cand[["erasure_w", "length_w", "clarity_w"]].corr().round(3).to_dict()
def _k(o):
    if isinstance(o, dict):
        return {str(k): _k(v) for k, v in o.items()}
    return o
out = _k(out)
print(json.dumps(out, indent=1, default=str))
(HERE / "structure.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
