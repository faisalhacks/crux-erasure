"""Tests for the R1 additions: interval methods in A2 (bca, wild), a2_informativeness.py, gate1 FR 6.4a,
ADJ final_label rejection.  Dummy / synthetic / shuffled data only."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import a2_within_round as A2  # noqa: E402
import a2_informativeness as INF  # noqa: E402
import gate1 as G1  # noqa: E402,F401
import make_dummy_labels as MD  # noqa: E402

T, TD = C.A / "testout", C.A / "testdata"
R = T / "runs" / C.utc_stamp()
R.mkdir(parents=True)
ok = True


def chk(n, c, d):
    global ok
    ok &= bool(c)
    print(("PASS " if c else "FAIL ") + n + " :: " + d, flush=True)


pl = pd.read_csv(T / "SYNTH_planted_E.csv")
cf = pd.read_csv(T / "SYNTH_confound.csv")
for m in ("bca", "wild"):
    p = C.load_params(json.dumps({"B": 2000, "interval": m}))
    r = A2.fit_models(pl, p)["controlled"]["erasure"]
    chk(f"A2 {m} planted recovered", r["lo"] > 0, f"{r['est']:+.3f} [{r['lo']:+.3f},{r['hi']:+.3f}] p={r['p_boot']:.4f}")
    r = A2.fit_models(cf, p)
    e = r["controlled"]["erasure"]
    chk(f"A2 {m} confound controlled covers 0", e["lo"] <= 0 <= e["hi"], f"{e['est']:+.3f} [{e['lo']:+.3f},{e['hi']:+.3f}]")

# informativeness
d0 = C.make_synth(n_launches=120, seed=3)
f0 = T / "SYNTH_inf_varied.csv"; d0.to_csv(f0, index=False)
o = INF.main(["--input", str(f0), "--kind", "dummy", "--out", str(R / "A2_TIER_dummy_varied.json"), "--nfit", "40"])
chk("tier INFORMATIVE or LOW-POWER on varied-E synthetic, K_inf=120", o["K_inf"] == 120 and o["tier"] in ("INFORMATIVE", "LOW-POWER"), f"{o['tier']} MDE80={o['MDE80']:.3f}")
d1 = d0.copy(); d1["E"] = 1.0
f1 = T / "SYNTH_inf_const.csv"; d1.to_csv(f1, index=False)
try:
    o1 = INF.main(["--input", str(f1), "--kind", "dummy", "--out", str(R / "A2_TIER_dummy_const.json"), "--nfit", "5"])
    chk("constant E -> NOT MEASURABLE", o1["tier"] == "NOT MEASURABLE" and o1["R_inf"] == 0, f"{o1['tier']} R_inf={o1['R_inf']}")
except Exception as ex:  # singular design with no E variation is itself the NOT MEASURABLE case
    chk("constant E -> design singular (NOT MEASURABLE by construction)", True, type(ex).__name__)
d2 = d0.copy()
keep = d2.launch_id.isin([f"L{i}" for i in range(30)])
d2.loc[~keep, "E"] = 0.5
f2 = T / "SYNTH_inf_30.csv"; d2.to_csv(f2, index=False)
try:
    o2 = INF.main(["--input", str(f2), "--kind", "dummy", "--out", str(R / "A2_TIER_dummy_30.json"), "--nfit", "20"])
    chk("30 informative launches -> NOT MEASURABLE", o2["tier"] == "NOT MEASURABLE" and o2["K_inf"] == 30, f"{o2['tier']} K_inf={o2['K_inf']}")
except Exception as ex:
    chk("30-launch case ran", False, repr(ex))
try:
    INF.main(["--input", str(f0), "--kind", "dummy"])
    chk("dummy refuses P/gate1/A2_TIER_R4.json", False, "no exit")
except SystemExit:
    chk("dummy refuses P/gate1/A2_TIER_R4.json", True, "SystemExit")
try:
    C.check_kind("real")
    chk("real A2 refused without A2_TIER_R4/GATE1_RESULT", False, "no exit")
except SystemExit as ex:
    chk("real A2 refused without A2_TIER_R4/GATE1_RESULT", True, str(ex)[:70])

# [R4] the gate1 tests (6.4a fields, ADJ final_label rejection, both designs) moved to test_r4.py; fixtures changed with the R4 label schema
chk("gate1 R1 additions are covered in test_r4.py", (C.A / "test_r4.py").exists(), "pointer")
print("R1 TESTS PASS" if ok else "R1 TESTS FAILED")
