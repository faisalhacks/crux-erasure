"""Red-team: do the ranks used by A2 (pilots/T3_1/all_groups.jsonl) equal the frozen source parquet's
rankings.numerical_ranks (FR s2 source, sha 7cf8d5ce...), mapped to the same candidate order?
Also: are statements with a missing E (label parse failure) different in length (missing-not-at-random check)?
Writes analysis/redteam/rt_ranks_vs_source.json.  Usage: python -I -B rt_ranks_vs_source.py"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parents[2]
SRC = P.parent / "data" / "habermas_gcs" / "hm_all_candidate_comparisons.parquet"
h = hashlib.sha256()
with open(SRC, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
res = {"source_sha256": h.hexdigest()}
cols = ["launch_id", "round_id", "iteration_index", "metadata.participant_id", "metadata.provenance",
        "rankings.numerical_ranks", "rankings.candidate_ids", "candidates.metadata.id"]
src = pd.read_parquet(SRC, columns=cols)
src = src[(src.iteration_index == 0) & (src["metadata.provenance"] == "HUMAN_CITIZEN")]
key = {}
for r in src.itertuples(index=False):
    key[(r.round_id, r[3])] = (list(r[5]) if r[5] is not None else None, list(r[6]) if r[6] is not None else None,
                               list(r[7]) if r[7] is not None else None)
groups = [json.loads(l) for l in open(P.parent / "pilots" / "T3_1" / "all_groups.jsonl", encoding="utf-8")]
n, match, missing, mism = 0, 0, 0, []
for g in groups:
    for r in g["raters"]:
        n += 1
        k = key.get((g["round_id"], r["pid"]))
        if k is None:
            missing += 1
            continue
        ranks, rc_ids, c_ids = k
        # map source ranks (ordered by rankings.candidate_ids) to all_groups cand order (g['cand_ids'])
        try:
            m = dict(zip(rc_ids, ranks))
            mapped = [m[c] for c in g["cand_ids"]]
        except Exception:  # noqa: BLE001
            mapped = None
        if mapped == list(r["ranks"]):
            match += 1
        else:
            if len(mism) < 5:
                mism.append({"round": g["round_id"], "pid": r["pid"], "all_groups": r["ranks"], "source_mapped": mapped,
                             "source_raw": ranks, "rc_ids_eq_cand_ids": rc_ids == g["cand_ids"], "cand_meta_eq": c_ids == g["cand_ids"]})
res.update({"rater_rows": n, "matched": match, "missing_in_source": missing, "mismatch_examples": mism})
# alternative: source ranks taken in their raw order (no candidate-id mapping)
raw_eq = sum(1 for g in groups for r in g["raters"] if key.get((g["round_id"], r["pid"])) and key[(g["round_id"], r["pid"])][0] == list(r["ranks"]))
res["raw_order_equal"] = raw_eq
res["rankings_candidate_ids_equal_cand_ids"] = sum(1 for g in groups for r in g["raters"]
                                                   if key.get((g["round_id"], r["pid"])) and key[(g["round_id"], r["pid"])][1] == g["cand_ids"])
res["rounds_with_duplicate_cand_ids"] = sum(1 for g in groups if len(set(g["cand_ids"])) < len(g["cand_ids"]))

# MNAR check: word counts of statements with E missing vs present, in rounds with >= 1 crux
WORD = re.compile(r"[A-Za-z0-9']+")
sc = {}
for l in open(P / "analysis" / "scores" / "a2_scores_v2.jsonl", encoding="utf-8"):
    x = json.loads(l)
    sc[(x["round_id"], int(x["cand"]))] = x
miss_w, ok_w = [], []
for g in groups:
    for j, c in enumerate(g["candidates"]):
        s = sc.get((g["round_id"], j))
        if s is None or not s["n_cruxes"]:
            continue
        (miss_w if s["E"] is None else ok_w).append(len(WORD.findall(c)))
res["words_E_missing"] = {"n": len(miss_w), "median": float(np.median(miss_w)), "mean": float(np.mean(miss_w))}
res["words_E_present"] = {"n": len(ok_w), "median": float(np.median(ok_w)), "mean": float(np.mean(ok_w))}
Path(__file__).with_name("rt_ranks_vs_source.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res, indent=1, default=str))
