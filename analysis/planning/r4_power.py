"""Planning room R4 (decisions.md D31): design calculations on SYNTHETIC labels only.
No human label, ranking, rating or score file is read. Nothing is written outside analysis/planning/.

(a) Kappa step. Same data-generating process as analysis/eval/gate1_sim.py part (b) (METHODS_EVAL G2):
    truth Bernoulli(0.5); two independent labelers, each correct with probability acc; each label
    replaced by UNSURE (-1) with probability 0.05; UNSURE kept as a category; gate1.kappa unchanged;
    2000 simulations per setting; seed 777. Here for n = 20 and n = 30 shared items and cut-offs
    0.40 and 0.60. (gate1_sim.py drew its kappa simulations after its BA simulations from one stream,
    so the n = 20 / 0.60 cell is a re-draw of the same design, not the same random numbers.)
(b) N2 scorer check on 12 items (FROZEN_RULES 6.6): P(pass) of candidate rules for a scorer with
    sensitivity = specificity = s against human labels with HIDES prevalence p.
    Rules: one-sided Fisher exact p <= 0.05; p <= 0.025; gate-1-style bootstrap 2.5th percentile of
    balanced accuracy > 0.5 (one-class resample scored 0.5, gate1.ba unchanged). Also n = 24 for reference.
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
import scipy  # noqa: E402
from scipy.stats import fisher_exact  # noqa: E402
import gate1 as G  # noqa: E402

SEED = 777
SIMS = 2000
out = {"seed": SEED, "sims": SIMS, "utc_start": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
       "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__).resolve(), HERE.parent / "gate1.py")},
       "kappa": {}, "n2check": {}}

# ---------- (a) kappa ----------
for n in (20, 30):
    for acc in (0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
        rng = np.random.default_rng([SEED, n, int(round(acc * 100))])
        ks = []
        for s in range(SIMS):
            t = (rng.random(n) < 0.5).astype(int)
            lab = []
            for _ in range(2):
                v = np.where(rng.random(n) < acc, t, 1 - t)
                v = np.where(rng.random(n) < 0.05, -1, v)
                lab.append(v)
            ks.append(G.kappa(*lab))
        ks = np.array(ks)
        po = acc ** 2 + (1 - acc) ** 2
        cell = {"pop_kappa_no_unsure": (po - 0.5) / 0.5, "kappa_mean": float(np.nanmean(ks)),
                "kappa_sd": float(np.nanstd(ks)), "undefined": int(np.isnan(ks).sum()),
                "P(kappa>=0.40)": float(np.mean(ks >= 0.40)), "P(kappa>=0.60)": float(np.mean(ks >= 0.60))}
        out["kappa"][f"n{n}_acc{acc}"] = cell
        print(f"kappa n={n} acc={acc}: pop={cell['pop_kappa_no_unsure']:.3f} sd={cell['kappa_sd']:.3f} "
              f"P(>=.40)={cell['P(kappa>=0.40)']:.4f} P(>=.60)={cell['P(kappa>=0.60)']:.4f}", flush=True)

# ---------- (b) N2 scorer check ----------
BB = 2000


def ba_vec(y, yh):
    """rows = resamples; one-class row -> 0.5 (FR 6.4). Checked equal to gate1.ba below."""
    pos, neg = (y == 1), (y == 0)
    npos, nneg = pos.sum(1), neg.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sens = ((yh == 1) & pos).sum(1) / npos
        spec = ((yh == 0) & neg).sum(1) / nneg
    v = 0.5 * (sens + spec)
    v[(npos == 0) | (nneg == 0)] = 0.5
    return v


_chk = np.random.default_rng(1)
for _ in range(200):
    _y = (_chk.random((1, 9)) < 0.7).astype(int)
    _yh = (_chk.random((1, 9)) < 0.5).astype(int)
    assert abs(ba_vec(_y, _yh)[0] - G.ba(_y[0], _yh[0])) < 1e-12


def boot_lb(y, yh, rng):
    n = len(y)
    idx = rng.integers(0, n, size=(BB, n))
    return float(np.percentile(ba_vec(y[idx], yh[idx]), 2.5))


for n in (12, 24):
    for prev in (0.5, 0.67, 0.75):
        for s_ in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
            rng = np.random.default_rng([SEED, 1000 + n, int(round(prev * 100)), int(round(s_ * 100))])
            f05 = f025 = bapass = oneclass = 0
            nb = 1000  # bootstrap rule is slower: first 1000 simulations only
            for s in range(SIMS):
                y = (rng.random(n) < prev).astype(int)
                yh = np.where(rng.random(n) < s_, y, 1 - y)
                tp = int(((y == 1) & (yh == 1)).sum()); fn = int(((y == 1) & (yh == 0)).sum())
                fp = int(((y == 0) & (yh == 1)).sum()); tn = int(((y == 0) & (yh == 0)).sum())
                if tp + fn == 0 or fp + tn == 0:
                    oneclass += 1
                    p = 1.0
                else:
                    p = float(fisher_exact([[tp, fn], [fp, tn]], alternative="greater")[1])
                f05 += p <= 0.05
                f025 += p <= 0.025
                if s < nb:
                    bapass += boot_lb(y, yh, rng) > 0.5
            cell = {"P(pass) Fisher<=0.05": f05 / SIMS, "P(pass) Fisher<=0.025": f025 / SIMS,
                    "P(pass) BA boot 2.5pct>0.5": bapass / nb, "ba_boot_sims": nb, "ba_boot_B": BB,
                    "P(one human class only)": oneclass / SIMS}
            out["n2check"][f"n{n}_prev{prev}_acc{s_}"] = cell
            print(f"n2check n={n} prev={prev} acc={s_}: F05={cell['P(pass) Fisher<=0.05']:.4f} "
                  f"F025={cell['P(pass) Fisher<=0.025']:.4f} BAboot={cell['P(pass) BA boot 2.5pct>0.5']:.3f} "
                  f"oneclass={cell['P(one human class only)']:.4f}", flush=True)

out["utc_end"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "r4_power.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
