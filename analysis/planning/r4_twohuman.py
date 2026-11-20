"""Planning room R4 (decisions.md D37): design calculation on SYNTHETIC labels only.
Two-human design: Cohen's kappa (3 categories, UNSURE kept) on n = 50 shared items, cut-off 0.40.
Same data-generating form as analysis/eval/gate1_sim.py part (b): truth HIDES with probability prev;
two independent labelers each correct with probability acc; each label UNSURE (-1) with probability 0.05;
gate1.kappa unchanged; 2000 simulations per cell; seed 777. No label, ranking, rating or score file is read.
"""
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np  # noqa: E402
import gate1 as G  # noqa: E402

SEED, SIMS, N = 777, 2000, 50
out = {"seed": SEED, "sims": SIMS, "n": N, "utc_start": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "versions": {"python": platform.python_version(), "numpy": np.__version__},
       "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__).resolve(), HERE.parent / "gate1.py")},
       "kappa": {}}
for prev in (0.5, 0.75):
    for acc in (0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
        rng = np.random.default_rng([SEED, 4000, int(round(prev * 100)), int(round(acc * 100))])
        ks = []
        for s in range(SIMS):
            t = (rng.random(N) < prev).astype(int)
            lab = []
            for _ in range(2):
                v = np.where(rng.random(N) < acc, t, 1 - t)
                v = np.where(rng.random(N) < 0.05, -1, v)
                lab.append(v)
            ks.append(G.kappa(*lab))
        ks = np.array(ks)
        po = acc * acc + (1 - acc) * (1 - acc)
        q = prev * acc + (1 - prev) * (1 - acc)
        pe = q * q + (1 - q) * (1 - q)
        cell = {"pop_kappa_no_unsure": (po - pe) / (1 - pe), "kappa_mean": float(np.nanmean(ks)),
                "kappa_sd": float(np.nanstd(ks)), "undefined": int(np.isnan(ks).sum()),
                "P(kappa>=0.40)": float(np.mean(ks >= 0.40))}
        out["kappa"][f"n{N}_prev{prev}_acc{acc}"] = cell
        print(f"kappa n={N} prev={prev} acc={acc}: pop={cell['pop_kappa_no_unsure']:.3f} "
              f"sd={cell['kappa_sd']:.3f} P(>=.40)={cell['P(kappa>=0.40)']:.4f}", flush=True)
out["utc_end"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "r4_twohuman.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
