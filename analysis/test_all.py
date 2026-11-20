"""Test harness aligned to FROZEN_RULES.md.  (i) synthetic planted effects, (ii) real Habermas
statements/raters with SHUFFLED ranks (FR 6.5: random.Random(424242)), (iii) pointer to test_r4.py (gate1 R4),
(iv) lock checks.  Real ranks are shuffled in memory and never summarised."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402
import n1_winner_vs_mean as N1  # noqa: E402
import n4_minority as N4  # noqa: E402
import a3_ai_vs_human as A3  # noqa: E402
import n3_draft_vs_revised as N3  # noqa: E402
import gate1 as G1  # noqa: E402
import make_dummy_labels as MD  # noqa: E402
import run_log  # noqa: E402

T = C.A / "testout"
T.mkdir(exist_ok=True)
R = T / "runs" / C.utc_stamp()   # L3: each test run writes into its own fresh dir; no output is overwritten
R.mkdir(parents=True)
TD = C.A / "testdata"
res, ok = {}, True


def chk(name, cond, detail, gating=True):
    global ok
    if gating:
        ok &= bool(cond)
    print(("PASS " if cond else ("FAIL " if gating else "INFO-MISS ")) + name + " :: " + detail)
    res[name] = {"pass": bool(cond), "gating": gating, "detail": detail}


def ci(d):
    return f"{d['est']:+.3f} [{d['lo']:+.3f},{d['hi']:+.3f}]"


def covers0(d):
    return d["lo"] <= 0 <= d["hi"]


def pj(**k):
    return json.dumps(k)


def save(df, nm):
    f = T / f"SYNTH_{nm}.csv"
    df.to_csv(f, index=False)
    return str(f)


# ---------------------------------------------------------------- (i) synthetic
planted = save(C.make_synth(beta_E=2.0, seed=11), "planted_E")
confound = save(C.make_synth(beta_len=0.8, E_len_corr=0.6, seed=12), "confound")
null = save(C.make_synth(seed=13), "null")
for unit in ("rater", "group"):
    a = A2.main(["--input", planted, "--kind", "synthetic", "--out", str(R / f"a2_planted_{unit}.json"),
                 "--params", pj(unit=unit), "--note", "synthetic planted beta_E=2"])
    chk(f"A2 planted effect recovered ({unit})", a["controlled"]["erasure"]["lo"] > 0, ci(a["controlled"]["erasure"]))
a = A2.main(["--input", confound, "--kind", "synthetic", "--out", str(R / "a2_confound.json"), "--note", "length confound, true E effect 0"])
chk("A2 confound: controlled CI covers 0", covers0(a["controlled"]["erasure"]), ci(a["controlled"]["erasure"]))
chk("A2 confound: uncontrolled biased (CI excludes 0)", not covers0(a["uncontrolled"]["erasure"]), ci(a["uncontrolled"]["erasure"]))
chk("A2 A2h (length only) covers 0 in confound", covers0(a["A2h"]["erasure"]), ci(a["A2h"]["erasure"]))
a = A2.main(["--input", null, "--kind", "synthetic", "--out", str(R / "a2_synth_null.json"), "--note", "synthetic null"])
chk("A2 synthetic null (single dataset) covers 0", covers0(a["controlled"]["erasure"]), ci(a["controlled"]["erasure"]), gating=False)
n = N1.main(["--input", planted, "--kind", "synthetic", "--out", str(R / "n1_planted.json"), "--note", "synthetic planted"])
chk("N1 planted effect recovered", n["erasure"]["lo"] > 0, ci(n["erasure"]))
n = N1.main(["--input", null, "--kind", "synthetic", "--out", str(R / "n1_null.json"), "--note", "synthetic null"])
chk("N1 synthetic null (single dataset) covers 0", covers0(n["erasure"]), ci(n["erasure"]), gating=False)

# synthetic null coverage, 60 datasets
hA = hN = 0
NSY = 60
for s in range(NSY):
    d0 = C.make_synth(seed=500 + s)
    pq = C.load_params(pj(B=500, seed=s))
    hA += covers0(A2.fit_models(d0, pq)["controlled"]["erasure"])
    hN += covers0(N1.run(d0, pq)["erasure"])
chk("A2 synthetic null coverage 60 datasets >= 88%", hA / NSY >= 0.88, f"{hA}/{NSY}")
chk("N1 synthetic null coverage 60 datasets >= 88%", hN / NSY >= 0.88, f"{hN}/{NSY}")
run_log.log_run(__file__, "synthetic", "500..559", [], str(R / "test_results.json"), f"null coverage A2 {hA}/{NSY} N1 {hN}/{NSY} B=500")

# N4 planted: majority 0, minority 3
n4d = save(C.make_synth(beta_E=0.0, minority_beta=3.0, seed=21), "n4_planted")
r = N4.main(["--input", n4d, "--kind", "synthetic", "--out", str(R / "n4_planted.json")])
chk("N4 planted interaction recovered", r["interaction"]["lo"] > 0 and covers0(r["majority"]), f"int {ci(r['interaction'])} maj {ci(r['majority'])} min {ci(r['minority'])}")
n4n = save(C.make_synth(beta_E=0.0, minority_beta=0.0, seed=22), "n4_null")
r = N4.main(["--input", n4n, "--kind", "synthetic", "--out", str(R / "n4_null.json")])
chk("N4 synthetic null interaction (single dataset) covers 0", covers0(r["interaction"]), ci(r["interaction"]), gating=False)

# A3 / N3 statement-level synthetic
def stmt(effect, col, seed, nl=120):
    rng = np.random.default_rng(seed)
    rows = []
    for g in range(nl):
        for r_ in range(2):
            for j in range(4):
                lab = (j < 2)
                e = float(np.clip(0.5 + rng.normal(0, 0.15) + (effect if lab else 0) + rng.normal(0, 0.05) * g / nl, 0, 1))
                if col == "prov":
                    rows.append((f"L{g}", f"L{g}R{r_}", j, "MODEL_MEDIATOR" if lab else "HUMAN_MEDIATOR", e))
                else:
                    rows.append((f"L{g}", f"L{g}R{r_}", j, 1 if lab else 0, e))
    return pd.DataFrame(rows, columns=["launch_id", "round_id", "cand", col, "E"])
for nm, mod, col, lab in (("A3", A3, "prov", "AI-human"), ("N3", N3, "iteration", "it1-it0")):
    f = T / f"SYNTH_{nm}_planted.csv"; stmt(0.15, col, 31).to_csv(f, index=False)
    r = mod.main(["--input", str(f), "--kind", "synthetic", "--out", str(R / f"{nm.lower()}_planted.json")])
    chk(f"{nm} planted effect recovered", r["status"] == "RUN" and r["erasure"]["lo"] > 0, ci(r["erasure"]))
    f = T / f"SYNTH_{nm}_null.csv"; stmt(0.0, col, 32).to_csv(f, index=False)
    r = mod.main(["--input", str(f), "--kind", "synthetic", "--out", str(R / f"{nm.lower()}_null.json")])
    chk(f"{nm} synthetic null (single dataset) covers 0", covers0(r["erasure"]), ci(r["erasure"]), gating=False)
    f = T / f"SYNTH_{nm}_small.csv"; stmt(0.15, col, 33, nl=10).to_csv(f, index=False)
    r = mod.main(["--input", str(f), "--kind", "synthetic", "--out", str(R / f"{nm.lower()}_small.json")])
    chk(f"{nm} floor: <30 launches -> NOT_RUN", r["status"] == "NOT_RUN", r["reason"])

# Holm
h = C.holm({"a": 0.01, "b": 0.04, "c": 0.03})
chk("Holm adjustment", abs(h["a"] - 0.03) < 1e-12 and abs(h["c"] - 0.06) < 1e-12 and abs(h["b"] - 0.06) < 1e-12, str(h))

# ---------------------------------------------------------------- (ii) Habermas covariates, shuffled ranks
H = "HABERMAS_SHUFFLED"
for unit in ("rater", "group"):
    a = A2.main(["--input", H, "--kind", "shuffled", "--out", str(R / f"a2_shuffled_{unit}.json"), "--params", pj(unit=unit, include_dev=True),
                 "--note", "Habermas, within-rater shuffled ranks (Random(424242)), E = DUMMY proxy (pilot rounds = development launches, so include_dev)"])
    chk(f"A2 shuffled null covers 0 ({unit})", covers0(a["controlled"]["erasure"]), ci(a["controlled"]["erasure"]) + f" clusters={a['n_clusters']} p={a['controlled']['erasure']['p_boot']:.3f}")
n = N1.main(["--input", H, "--kind", "shuffled", "--out", str(R / "n1_shuffled.json"), "--params", pj(include_dev=True), "--note", "Habermas shuffled, DUMMY E, include_dev (pilot rounds)"])
chk("N1 shuffled null covers 0", covers0(n["erasure"]), ci(n["erasure"]) + f" rounds={n['n_rounds']} ties_excl={n['rounds_tied_winner_excluded']}")

# FR 7 interval check: see coverage_interval.py / coverage_interval.json (400 reshuffles, B=2000, three methods)

# ---------------------------------------------------------------- (iii) gate1 [R4] on DUMMY fixtures: see test_r4.py (both labeler designs)
chk("gate1 [R4] tests live in test_r4.py (run it beside this file)", (C.A / "test_r4.py").exists(), "pointer")

# ---------------------------------------------------------------- (iv) lock
try:
    C.check_kind("real")
    locked = (C.GATE / "GATE1_RESULT.json").exists()
except SystemExit:
    locked = True
chk("real-rank analysis refused without GATE1_RESULT.json", locked, "SystemExit raised" if locked else "NOT refused")

C.write_result(R / "test_results.json", {"results": res, "all_gating_pass": bool(ok)}, __file__, "synthetic", "n/a", [], "test_all results")
print("ALL GATING TESTS PASS" if ok else "SOME GATING TESTS FAILED")
sys.exit(0 if ok else 1)
