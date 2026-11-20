"""Methodologist eval: probe gate1.py behaviour on edge cases (synthetic tokens only, no labels).
1. Are the FROZEN_RULES §5 tokens accepted?  2. What does a missing (NaN) ai_score become?
3. One-class bootstrap resamples: dropped or scored 0.5?"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import gate1 as G  # noqa: E402

for t in ("HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE", " hides ", "yes", "erased", "1"):
    try:
        print(f"tok({t!r}) -> {G.tok(t)}")
    except ValueError as e:
        print(f"tok({t!r}) -> ValueError: {e}")

import io  # noqa: E402
aid = pd.read_csv(io.StringIO("item_id,ai_score\na,0.9\nb,\nc,0.1\n"), dtype=str)  # as gate1.main reads it
aid["ai_v"] = (aid["ai_score"].astype(float) >= 0.5).astype(float)
print("ai_score ['0.9','',  '0.1'] -> ai_v", aid["ai_v"].tolist(), "(NaN score becomes a NEGATIVE call, not missing)")

# one-class resamples at small n: how many bootstrap replicates are discarded
rng = np.random.default_rng(1)
y = np.array([1] * 3 + [0] * 17)
yh = y.copy()
lo, hi, nb = G.boot_stat(G.balanced_acc, len(y), 10000, 5, 0.05, y, yh)
print(f"n=20 with 3 positives, perfect AI: valid reps {nb}/10000 (discarded = one-class); lo={lo:.3f}")
