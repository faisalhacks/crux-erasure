"""EXP0 independent check: is the ranking unit per rater or per group?
Reads ONLY ranking/ID/provenance columns. No erasure score, no outcome analysis.
Seed: none needed (no randomness except nothing). Data: hm_all_candidate_comparisons.parquet.
Run: python -I exp0_check.py
"""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

PATH = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\data\habermas_gcs\hm_all_candidate_comparisons.parquet"
OUT = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\analysis\exp0_check.json")

h = hashlib.sha256()
with open(PATH, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)

cols = ["launch_id", "round_id", "iteration_index", "worker_id", "rankings.metadata.id",
        "rankings.metadata.participant_id", "own_opinion.metadata.participant_id",
        "metadata.participant_id", "rankings.metadata.provenance", "rankings.numerical_ranks",
        "rankings.candidate_ids", "candidates.metadata.id", "top_candidate.reward_data.welfare_or_rank",
        "candidates.reward_data.welfare_or_rank"]
df = pq.read_table(PATH, columns=cols).to_pandas()
res = {"sha256": h.hexdigest(), "n_rows": len(df)}
res["rank_prov"] = df["rankings.metadata.provenance"].value_counts(dropna=False).to_dict()
has = df["rankings.numerical_ranks"].map(lambda x: x is not None and len(x) > 0)
res["rows_with_ranks"] = int(has.sum())
d = df[has].copy()
d["rk"] = d["rankings.numerical_ranks"].map(lambda x: tuple(int(v) for v in x))
res["rank_pid_eq_own_pid"] = float((d["rankings.metadata.participant_id"] == d["own_opinion.metadata.participant_id"]).mean())
res["rank_id_unique_share"] = d["rankings.metadata.id"].nunique() / len(d)
res["rank_pid_nunique"] = int(d["rankings.metadata.participant_id"].nunique())
g = d.groupby(["launch_id", "round_id", "iteration_index"])
n_rows = g.size()
n_distinct_pid = g["rankings.metadata.participant_id"].nunique()
n_distinct_rk = g["rk"].nunique()
res["groups_with_rank_rows"] = int(len(n_rows))
res["rows_per_group_dist"] = {int(k): int(v) for k, v in n_rows.value_counts().sort_index().items()}
res["share_groups_rows_eq_distinct_pid"] = float((n_rows == n_distinct_pid).mean())
multi = n_rows >= 2
res["groups_ge2_raters"] = int(multi.sum())
res["groups_ge2_with_more_than_one_distinct_ranking"] = int((n_distinct_rk[multi] > 1).sum())
res["groups_ge2_all_identical"] = int((n_distinct_rk[multi] == 1).sum())
# candidate id sets: same across raters inside a group (shared candidates) ?
same_cands = 0
tot = 0
for key, sub in g:
    if len(sub) < 2:
        continue
    tot += 1
    s = {tuple(x) for x in sub["candidates.metadata.id"]}
    same_cands += (len(s) == 1)
res["multi_rater_groups_with_identical_candidate_id_list"] = [same_cands, tot]
# group-level aggregate field (social choice) is a separate column
res["group_level_fields"] = ["top_candidate.reward_data.welfare_or_rank", "candidates.reward_data.welfare_or_rank (list, per row)"]
# 3 example rows from the same group, truncated
ex = None
for key, sub in g:
    if len(sub) >= 3 and sub["rk"].nunique() >= 2:
        ex = (key, sub.head(3))
        break
rows = []
for _, r in ex[1].iterrows():
    rows.append({"launch_id": r["launch_id"][:8], "round_id": r["round_id"][:8], "iteration_index": int(r["iteration_index"]),
                 "worker_id": (r["worker_id"] or "")[:8] if r["worker_id"] else None,
                 "rankings.metadata.participant_id": r["rankings.metadata.participant_id"],
                 "own_opinion.metadata.participant_id": r["own_opinion.metadata.participant_id"],
                 "rankings.metadata.id": r["rankings.metadata.id"][:8],
                 "rankings.candidate_ids": [c[:6] for c in r["rankings.candidate_ids"]],
                 "rankings.numerical_ranks": list(r["rk"]),
                 "rankings.metadata.provenance": r["rankings.metadata.provenance"]})
res["example_rows"] = rows
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
