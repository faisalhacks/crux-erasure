"""Reviewer check: which SD / missing-row convention reproduces the reported Spearman (reported-no-rule, appendix)."""
import csv
import json
import statistics
import pyarrow.parquet as pq
from scipy.stats import spearmanr

P = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1"
rows = list(csv.DictReader(open(P + r"\analysis\review\rederive_step2_rounds.csv", encoding="utf-8")))
# recompute member values is not stored; rebuild sample sd from pstdev: sd_s = sd_p * sqrt(n/(n-1))
res = {}
for miss in ("exclude", "zero"):
    for sdk in ("pop", "sample"):
        x, y = [], []
        for r in rows:
            n = int(r["n_rated"]); sdp = float(r["sd"])
            sd = sdp if sdk == "pop" else sdp * (n / (n - 1)) ** 0.5
            if r["missing"] == "True":
                if miss == "exclude":
                    continue
                c = 0
            else:
                c = int(r["n_cruxes"])
            x.append(c); y.append(sd)
        res[f"{miss}_{sdk}"] = spearmanr(x, y).correlation
print(json.dumps(res, indent=1))
