"""Reviewer check: does np.std split mathematically equal SDs into distinct floats (tie-breaking in Spearman)?"""
import csv
from scipy.stats import spearmanr

P = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1"
rows = list(csv.DictReader(open(P + r"\analysis\review\rederive_step2_rounds.csv", encoding="utf-8")))
print("distinct exact pstdev:", len({round(float(r["sd"]), 9) for r in rows}),
      "distinct raw pstdev floats:", len({r["sd"] for r in rows}),
      "distinct np.std floats:", len({r["sd_np"] for r in rows}))
nc = [0 if r["missing"] == "True" else int(r["n_cruxes"]) for r in rows]
print("missing->0, np.std rounded to 9 dp:", spearmanr(nc, [round(float(r["sd_np"]), 9) for r in rows]).correlation)
