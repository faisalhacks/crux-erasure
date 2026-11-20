"""Red-team: Monte Carlo (seed) sensitivity of the wild-cluster bootstrap-t bounds for A2, A2b, A2h, A2g.
Uses the project's own design builder (a2_within_round.fit_models, design_only) and interval code (common.ols_cluster_ci),
read-only; nothing is written outside analysis/redteam/.  The record uses seed 20261119; here 40 other seeds, B = 10,000.
Usage: python -I rt_seed_sensitivity.py"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402

df = C.read_long(str(HERE.parent / "scores" / "a2_long_real.parquet"))[0]   # kind=None: no writes, no gate stamp
specs = {"A2": {}, "A2b": {"controls": ["log_len", "flesch", "own_sim"],
                           "control_labels": {"log_len": "length", "flesch": "clarity", "own_sim": "own_sim"}},
         "A2h": {"controls": ["log_len"], "control_labels": {"log_len": "length"}},
         "A2g": {"predictor": "E_w"}}
seeds = [20261119] + list(range(1, 41))
res = {}
for name, extra in specs.items():
    p = C.load_params(json.dumps(extra))
    p["_kind"] = None
    X, y, codes, nc = A2.fit_models(df, p, design_only=True)
    los, his, ps = [], [], []
    for s in seeds:
        r = C.ols_cluster_ci(X, y, codes, nc, 10000, s, 0.05, "wild")[0]
        los.append(r["lo"]); his.append(r["hi"]); ps.append(r["p_boot"])
    los, his, ps = map(np.array, (los, his, ps))
    res[name] = {"est": r["est"], "lo_record_seed": float(los[0]), "lo_min": float(los[1:].min()), "lo_max": float(los[1:].max()),
                 "lo_sd": float(los[1:].std(ddof=1)), "share_other_seeds_lo_le_0": float((los[1:] <= 0).mean()),
                 "p_min": float(ps[1:].min()), "p_max": float(ps[1:].max()), "n_other_seeds": len(seeds) - 1}
    print(name, json.dumps(res[name]))
(HERE / "rt_seed_sensitivity.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
