"""Planning room R4 (decisions.md D34): design calculations on SYNTHETIC labels only.
No human label, ranking, rating or score file is read. Nothing is written outside analysis/planning/.

(a) Self-consistency kappa (FROZEN_RULES 6.2 [R4]): one labeler, two passes over n = 20 repeated items,
    cut-off 0.60. Model, the same form as analysis/eval/gate1_sim.py part (b): each item has a stable
    own reading (HIDES with probability prev); each pass reproduces the own reading with probability r
    (repeatability), independently between passes; each pass label is replaced by UNSURE (-1) with
    probability 0.05; UNSURE kept as a category; gate1.kappa unchanged; 2000 simulations; seed 777.
    With prev = 0.5 this is exactly the METHODS_EVAL G2 design with r in the place of "accuracy".
    The model assumes no memory of the first pass; memory would raise the pass rate.
(b) Balanced-accuracy rule at n = 38 gate items (FROZEN_RULES 6.4 [R4]): P(bootstrap 2.5th percentile of
    BA > 0.5) for a scorer with sensitivity = specificity = s, human HIDES prevalence prev.
    One-class resample scored 0.5 as in gate1.ba (vectorised here; checked equal to gate1.ba).
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

SEED, SIMS = 777, 2000
out = {"seed": SEED, "sims": SIMS, "utc_start": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "versions": {"python": platform.python_version(), "numpy": np.__version__},
       "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__).resolve(), HERE.parent / "gate1.py")},
       "selfkappa": {}, "ba38": {}}

N = 20
for prev in (0.5, 0.75):
    for r in (0.80, 0.85, 0.90, 0.95, 0.975, 0.99):
        rng = np.random.default_rng([SEED, 2000, int(round(prev * 100)), int(round(r * 1000))])
        ks = []
        for s in range(SIMS):
            t = (rng.random(N) < prev).astype(int)
            lab = []
            for _ in range(2):
                v = np.where(rng.random(N) < r, t, 1 - t)
                v = np.where(rng.random(N) < 0.05, -1, v)
                lab.append(v)
            ks.append(G.kappa(*lab))
        ks = np.array(ks)
        # population kappa without unsure: po = r^2+(1-r)^2 ; marginal q = prev*r + (1-prev)*(1-r)
        po = r * r + (1 - r) * (1 - r)
        q = prev * r + (1 - prev) * (1 - r)
        pe = q * q + (1 - q) * (1 - q)
        cell = {"pop_kappa_no_unsure": (po - pe) / (1 - pe), "kappa_mean": float(np.nanmean(ks)),
                "kappa_sd": float(np.nanstd(ks)), "undefined": int(np.isnan(ks).sum()),
                "P(kappa>=0.60)": float(np.mean(ks >= 0.60))}
        out["selfkappa"][f"n{N}_prev{prev}_r{r}"] = cell
        print(f"selfkappa n={N} prev={prev} r={r}: pop={cell['pop_kappa_no_unsure']:.3f} "
              f"sd={cell['kappa_sd']:.3f} undefined={cell['undefined']} P(>=.60)={cell['P(kappa>=0.60)']:.4f}",
              flush=True)

BB, NB, NG = 2000, 1000, 38


def ba_vec(y, yh):
    """rows = resamples; one-class row -> 0.5 (FR 6.4)."""
    pos, neg = (y == 1), (y == 0)
    npos, nneg = pos.sum(1), neg.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sens = ((yh == 1) & pos).sum(1) / npos
        spec = ((yh == 0) & neg).sum(1) / nneg
    v = 0.5 * (sens + spec)
    v[(npos == 0) | (nneg == 0)] = 0.5
    return v


chk = np.random.default_rng(1)
for _ in range(200):
    y = (chk.random((1, 9)) < 0.7).astype(int)
    yh = (chk.random((1, 9)) < 0.5).astype(int)
    assert abs(ba_vec(y, yh)[0] - G.ba(y[0], yh[0])) < 1e-12

for prev in (0.5, 0.25, 0.75):
    for s_ in (0.5, 0.6, 0.65, 0.7, 0.8, 0.9):
        rng = np.random.default_rng([SEED, 3000, int(round(prev * 100)), int(round(s_ * 100))])
        passes = oneclass = 0
        for s in range(NB):
            y = (rng.random(NG) < prev).astype(int)
            yh = np.where(rng.random(NG) < s_, y, 1 - y)
            if y.sum() in (0, NG):
                oneclass += 1
            idx = rng.integers(0, NG, size=(BB, NG))
            passes += np.percentile(ba_vec(y[idx], yh[idx]), 2.5) > 0.5
        cell = {"P(pass)": passes / NB, "sims": NB, "B": BB, "one_class_samples": oneclass}
        out["ba38"][f"n{NG}_prev{prev}_acc{s_}"] = cell
        print(f"BA n={NG} prev={prev} acc={s_}: P(pass)={cell['P(pass)']:.3f}", flush=True)

out["utc_end"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "r4_selfconsistency.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
