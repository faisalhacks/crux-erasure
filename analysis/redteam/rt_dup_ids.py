"""Red-team: rounds whose 4 candidate ids contain duplicates (found by rt_ranks_vs_source.py).
Are the texts duplicated too, and are those rounds in the A2 fit / informative set?  Usage: python -I -B rt_dup_ids.py"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2]
dev = {json.loads(l)["launch_id"] for l in open(P.parent / "pilots" / "T3_1" / "pilot_groups.jsonl", encoding="utf-8") if l.strip()}
sc = {}
for l in open(P / "analysis" / "scores" / "a2_scores_v2.jsonl", encoding="utf-8"):
    x = json.loads(l)
    sc.setdefault(x["round_id"], {})[int(x["cand"])] = x
out = {"rounds": 0, "texts_also_duplicated": 0, "nondev": 0, "in_A2_fit": 0, "informative": 0, "dup_pairs_E_differ": 0, "examples": []}
for l in open(P.parent / "pilots" / "T3_1" / "all_groups.jsonl", encoding="utf-8"):
    g = json.loads(l)
    ids = g["cand_ids"]
    if len(set(ids)) == len(ids):
        continue
    out["rounds"] += 1
    dupi = [i for i in range(4) if ids.count(ids[i]) > 1]
    same_text = len({g["candidates"][i] for i in dupi}) < len(dupi)
    out["texts_also_duplicated"] += int(same_text)
    if g["launch_id"] in dev:
        continue
    out["nondev"] += 1
    s = sc.get(g["round_id"], {})
    Es = [s.get(j, {}).get("E") for j in range(4)]
    if all(e is not None for e in Es) and s[0]["n_cruxes"]:
        out["in_A2_fit"] += 1
        out["informative"] += int(len(set(Es)) > 1)
        out["dup_pairs_E_differ"] += int(len({Es[i] for i in dupi}) > 1)
    if len(out["examples"]) < 3:
        out["examples"].append({"round": g["round_id"], "ids": ids, "dup_idx": dupi, "same_text": same_text, "E": Es})
Path(__file__).with_name("rt_dup_ids.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
