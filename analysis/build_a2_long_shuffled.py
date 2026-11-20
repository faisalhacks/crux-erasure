"""Build the A2 long table (schema in common.py) for a2_informativeness.py with ranks SHUFFLED at build time.
Inputs: pilots/T3_1/all_groups.jsonl (statements, raters, ranks), scores/a2_scores_v2.jsonl (scorer-1 E).
Each rater's 4 ranks are permuted in memory (random.Random(777000) via common.shuffle_ranks) before anything
is written; real ranks are never summarised, joined to E, or persisted.  Output: <out>.parquet + .manifest.json."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402

out = Path(sys.argv[1])
sc = {}
for l in open(C.A / "scores" / "a2_scores_v2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    sc[(r["round_id"], int(r["cand"]))] = np.nan if r["E"] is None else float(r["E"])
rows = []
for l in open(C.PILOT / "all_groups.jsonl", encoding="utf-8"):
    g = json.loads(l)
    tx = [(C.n_words(c), C.flesch(c)) for c in g["candidates"]]
    for r in g["raters"]:
        for j in range(4):
            nw, fl = tx[j]
            rows.append(dict(launch_id=g["launch_id"], round_id=g["round_id"], rater_id=r["pid"], cand=j,
                             rank=r["ranks"][j], E=sc.get((g["round_id"], j), np.nan),
                             log_len=float(np.log(nw)) if nw > 0 else np.nan, flesch=fl))
d = pd.DataFrame(rows)
d = C.shuffle_ranks(d, 777000)
d.to_parquet(out, index=False)
man = {"source_parquet_sha256": C.FROZEN_SRC_SHA, "table_sha256": C.sha256_file(out),
       "build_analysis_set_counts": C.FROZEN_COUNTS, "table_counts": C.table_counts(pd.read_parquet(out)),
       "ranks": "shuffled at build (random.Random(777000)); real ranks not persisted",
       "inputs": {"a2_scores_v2.jsonl": C.sha256_file(C.A / "scores" / "a2_scores_v2.jsonl"),
                  "all_groups.jsonl": C.sha256_file(C.PILOT / "all_groups.jsonl")}}
Path(str(out) + ".manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
print(json.dumps(man["table_counts"]), len(d), int(d.E.isna().sum()))
