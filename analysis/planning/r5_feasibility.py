"""R5 proposal, step 2: FEASIBILITY COUNTS ONLY (planning room, 2026-11-16).

What this reads (column projection; nothing else is decoded):
  - analysis/scores/a2_long_shuffled.parquet: columns launch_id, round_id ONLY (no rank, no E, no length/flesch)
  - pilots/T3_1/pilot_groups.jsonl via common.dev_launch_ids(): development launch ids
  - hm_all_candidate_comparisons.parquet: launch_id, round_id, iteration_index, question.id,
        own_opinion.metadata.participant_id, metadata.provenance (no rankings, ratings, top_candidate, critique)
  - hm_all_position_statement_ratings.parquet: launch_id, question.id, metadata.participant_id,
        metadata.provenance, metadata.status, rating_index (NOT ratings.agreement: no rating value is read)
What it computes: how many confirmatory rounds have enough members with a COMPLETED pre-deliberation
position-rating row. It does NOT compute the reference (no split / no-split class), no score, no rank.
Output: analysis/planning/r5_feasibility.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402

D = common.P.parent / "data" / "habermas_gcs"
out = {"script": "analysis/planning/r5_feasibility.py", "utc": common.utc_stamp() if hasattr(common, "utc_stamp") else None}

a2 = pd.read_parquet(common.A / "scores" / "a2_long_shuffled.parquet", columns=["launch_id", "round_id"]).drop_duplicates()
dev = common.dev_launch_ids()
out["a2_rounds_all"] = int(a2["round_id"].nunique())
out["a2_launches_all"] = int(a2["launch_id"].nunique())
conf = a2[~a2["launch_id"].isin(dev)] if dev is not None else a2
out["dev_file_found"] = dev is not None
out["conf_rounds"] = int(conf["round_id"].nunique())
out["conf_launches"] = int(conf["launch_id"].nunique())

cc = pd.read_parquet(D / "hm_all_candidate_comparisons.parquet",
                     columns=["launch_id", "round_id", "iteration_index", "question.id",
                              "own_opinion.metadata.participant_id", "metadata.provenance"])
cc0 = cc[(cc["iteration_index"] == 0) & (cc["metadata.provenance"] == "HUMAN_CITIZEN")]
cc0 = cc0[cc0["round_id"].isin(set(conf["round_id"]))]
qn = cc0.groupby("round_id")["question.id"].nunique()
out["conf_rounds_found_in_cc"] = int(qn.size)
out["conf_rounds_unique_question"] = int((qn == 1).sum())
mem = cc0.groupby("round_id")["own_opinion.metadata.participant_id"].apply(lambda s: set(s.dropna()))
qid = cc0.groupby("round_id")["question.id"].first()
lid = cc0.groupby("round_id")["launch_id"].first()
out["members_per_round"] = {str(k): int(v) for k, v in sorted(Counter(len(m) for m in mem).items())}

ps = pd.read_parquet(D / "hm_all_position_statement_ratings.parquet",
                     columns=["launch_id", "question.id", "metadata.participant_id", "metadata.provenance",
                              "metadata.status", "rating_index"])
pre = ps[(ps["rating_index"] == 0) & (ps["metadata.provenance"] == "HUMAN_CITIZEN") & (ps["metadata.status"] == "COMPLETED")]
have = set(zip(pre["launch_id"], pre["question.id"], pre["metadata.participant_id"]))
dup = pre.groupby(["launch_id", "question.id", "metadata.participant_id"]).size()
out["pre_rows_completed_human"] = int(len(pre))
out["pre_keys_with_more_than_one_row"] = int((dup > 1).sum())

rows = []
for r, m in mem.items():
    if qn.get(r, 0) != 1:
        continue
    n_rated = sum((lid[r], qid[r], p) in have for p in m)
    rows.append((r, lid[r], len(m), n_rated))
t = pd.DataFrame(rows, columns=["round_id", "launch_id", "n_members", "n_rated"])
t["n_missing"] = t["n_members"] - t["n_rated"]
out["n_rated_dist"] = {str(k): int(v) for k, v in sorted(Counter(t["n_rated"]).items())}
out["n_missing_dist"] = {str(k): int(v) for k, v in sorted(Counter(t["n_missing"]).items())}
u = t[(t["n_rated"] >= 3) & (t["n_missing"] <= 1)]
out["usable_rule"] = "n_rated >= 3 and n_missing <= 1 (rated = has >= 1 COMPLETED HUMAN_CITIZEN rating_index 0 row; values unread)"
out["usable_rounds"] = int(len(u))
out["usable_launches"] = int(u["launch_id"].nunique())
a = t[(t["n_rated"] >= 3) & (t["n_missing"] == 0)]
out["all_rated_rounds"] = int(len(a))
out["all_rated_launches"] = int(a["launch_id"].nunique())
out["caveat"] = ("Upper bound: a COMPLETED row may still carry an empty or invalid agreement token; values were not read. "
                 "Confirmatory rounds taken from the A2 analysis table (1,960 eligible rounds) minus development launches.")
(HERE / "r5_feasibility.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
