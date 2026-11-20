"""Tie encoding check (structure only; permutation-invariant): are tied ranks dense (0,0,1,2)
or competition/min style (0,0,2,3)?  Counts rater-rounds by sorted rank pattern."""
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C  # noqa: E402

df = C.load_habermas_shuffled()
pat = Counter(tuple(sorted(g.tolist())) for _, g in df.groupby(["round_id", "rater_id"])["rank"])
for k, v in sorted(pat.items(), key=lambda t: -t[1]):
    print(k, v)
