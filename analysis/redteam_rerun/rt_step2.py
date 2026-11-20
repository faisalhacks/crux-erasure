"""Red-team: recompute the step-2 confusion table from the per-round file, and what it implies for the A2 set.
Inputs: gate1/step2_private/rounds__20261116T015355Z.csv, analysis/scores/a2_scores_v2.jsonl, pilots/T3_1/pilot_groups.jsonl.
Writes analysis/redteam/rt_step2.json.  Usage: python -I rt_step2.py"""
import json
from pathlib import Path

import pandas as pd

P = Path(__file__).resolve().parents[2]
t = pd.read_csv(P / "gate1" / "step2_private" / "rounds__20261116T015355Z.csv")
res = {"n_rounds": int(len(t)), "n_launches": int(t.launch_id.nunique())}
sdis = ((t.ext_ok == True) & (t.n_cruxes.fillna(0) > 0)).astype(int)  # noqa: E712
miss = t.ext_ok != True  # noqa: E712
h = t.hsplit
tp = int(((h == 1) & (sdis == 1) & ~miss).sum())
fn = int(((h == 1) & ((sdis == 0) | miss)).sum())
tn = int(((h == 0) & (sdis == 0) & ~miss).sum())
fp = int(((h == 0) & ((sdis == 1) | miss)).sum())
res["confusion_missing_as_wrong"] = dict(tp=tp, fn=fn, tn=tn, fp=fp)
res["sens"], res["spec"] = tp / (tp + fn), tn / (tn + fp)
res["BA2"] = (res["sens"] + res["spec"]) / 2
res["PPV"] = tp / (tp + fp)
res["n_rated_distribution"] = t.n_rated.value_counts().sort_index().to_dict()
res["n_unrated_gt1"] = int(((t.n_members - t.n_rated) > 1).sum())
res["n_rated_lt3"] = int((t.n_rated < 3).sum())
# A2 set composition by Hsplit
sc = [json.loads(x) for x in open(P / "analysis" / "scores" / "a2_scores_v2.jsonl", encoding="utf-8")]
by = {}
for r in sc:
    by.setdefault(r["round_id"], []).append(r)
ev = {k for k, v in by.items() if v[0]["n_cruxes"] and all(x["E"] is not None for x in v) and len(v) == 4}
inf = {k for k in ev if len({x["E"] for x in by[k]}) > 1}
tt = t.set_index("round_id")
a2 = tt.loc[tt.index.isin(ev)]
res["A2_set_rounds_by_hsplit"] = a2.hsplit.value_counts().to_dict()
ai = tt.loc[tt.index.isin(inf)]
res["A2_informative_rounds_by_hsplit"] = ai.hsplit.value_counts().to_dict()
res["A2_informative_launches_by_hsplit"] = ai.groupby("hsplit").launch_id.nunique().to_dict()
# crux count vs hsplit
res["share_hsplit1_by_ncrux"] = t[t.ext_ok == True].groupby("n_cruxes").hsplit.agg(["mean", "size"]).round(4).to_dict(orient="index")  # noqa: E712
Path(__file__).with_name("rt_step2.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res, indent=1, default=str))
