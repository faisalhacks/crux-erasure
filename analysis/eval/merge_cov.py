"""Merge coverage chunk JSONs and print coverage with Clopper-Pearson 95% CI.
Usage: python -I merge_cov.py out.json in1.json in2.json ..."""
import json
import sys

import pandas as pd
from scipy import stats

out, ins = sys.argv[1], sys.argv[2:]
reps, metas = [], []
for f in ins:
    d = json.load(open(f, encoding="utf-8"))
    reps += d["reps"]
    metas.append(d["meta"])
D = pd.DataFrame(reps)
summ = {}
for c in D.columns:
    if D[c].dtype == bool:
        x, n = int(D[c].sum()), len(D)
        ci = stats.binomtest(x, n).proportion_ci(confidence_level=0.95, method="exact")
        summ[c] = {"k": x, "n": n, "rate": round(x / n, 4), "cp95": [round(ci.low, 4), round(ci.high, 4)]}
    elif c not in ("rep", "data_seed"):
        summ[c] = {"mean": float(D[c].mean()), "sd": float(D[c].std())}
json.dump({"inputs": ins, "metas": metas, "n_reps": len(D), "summary": summ}, open(out, "w", encoding="utf-8"), indent=1)
for c, v in summ.items():
    print(c, v)
