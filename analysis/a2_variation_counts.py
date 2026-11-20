"""Counts only: within-round E variation on the full A2 scoring. Reads scores.jsonl only (no ranking/rating/label)."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

p = Path(sys.argv[1])
sc = [json.loads(x) for x in open(p, encoding="utf-8")]
rounds = defaultdict(list)
for r in sc:
    rounds[(r["launch_id"], r["round_id"])].append(r)
out = dict(statements=len(sc), rounds=len(rounds), launches=len({k[0] for k in rounds}))
out["zero_crux_rounds"] = sum(1 for v in rounds.values() if v[0]["n_cruxes"] == 0)
out["extract_failed_rounds"] = sum(1 for v in rounds.values() if not v[0]["extract_ok"])
out["rounds_with_any_missing_E"] = sum(1 for v in rounds.values() if v[0]["n_cruxes"] and any(x["E"] is None for x in v))
ev = {k: v for k, v in rounds.items() if v[0]["n_cruxes"] and all(x["E"] is not None for x in v)}
out["evaluable_rounds_all4_E"] = len(ev)
var = {k for k, v in ev.items() if len({x["E"] for x in v}) > 1}
out["rounds_E_varies"] = len(var)
out["launches_with_E_variation"] = len({k[0] for k in var})
epos = {}
for k, v in rounds.items():
    if v[0]["n_cruxes"] and all(x["labels"] for x in v):
        epos[k] = {round(sum(1 for l in x["labels"] if l not in ("VISIBLE", "SIDED")) / len(x["labels"]), 6) for x in v}
out["evaluable_rounds_Epos"] = len(epos)
out["rounds_Epos_varies"] = sum(1 for s in epos.values() if len(s) > 1)
out["launches_with_Epos_variation"] = len({k[0] for k, s in epos.items() if len(s) > 1})
out["label_counts"] = dict(Counter(l for r in sc for l in (r["labels"] or [])))
out["crux_count_dist"] = dict(sorted(Counter(v[0]["n_cruxes"] for v in rounds.values() if v[0]["extract_ok"]).items()))
out["statements_label_parse_failed"] = sum(1 for r in sc if r["label_ok"] is False)
out["dropped_too_long"] = sum(1 for v in rounds.values() if v[0]["dropped_too_long"])
print(json.dumps(out, indent=1))
