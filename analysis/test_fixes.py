"""Tests for the METHODS_EVAL fixes G1, A1, A3, L3, N1a.  SYNTHETIC / DUMMY data only; no real rank is read.
Each run writes into its own fresh directory under analysis/testout/runs/.  See analysis/eval/FIXES.md."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import gate1 as G1  # noqa: E402
import make_dummy_labels as MD  # noqa: E402
import n1_length_coverage as COV  # noqa: E402
import run_log  # noqa: E402

TD = C.A / "testdata"
R = C.A / "testout" / "runs" / ("fixes_" + C.utc_stamp())
R.mkdir(parents=True)
ok = True


def chk(n, c, d=""):
    global ok
    ok &= bool(c)
    print(("PASS " if c else "FAIL ") + n + " :: " + str(d), flush=True)


def exits(fn, *a, **k):
    try:
        fn(*a, **k)
    except SystemExit as e:
        return True, str(e)
    return False, ""


# ------------------------------------------------------------------ G1 (R4 schema: author_pass1/2, optional volunteer)
G1.B = 1000    # speed only; test_r4.py runs the full B = 10,000 scenario


def g1args(root, step):
    return ["--step", step, "--kind", "dummy", "--labels-dir", str(root / "labels"), "--gate-dir", str(root / "gate")]


def fresh(name, **kw):
    src = MD.build(name, **kw)
    dst = R / src.name
    shutil.copytree(src, dst)
    return dst


g = fresh("fx_single", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7)
k = G1.main(g1args(g, "kappa"))
kj = json.loads((g / "gate" / "KAPPA.json").read_text(encoding="utf-8"))
chk("G1 kappa stores sha256 of the label files and rows it used", set(kj["row_hashes"]) >= {"author_pass1_all", "author_pass2_all"} and len(kj["hashes"]["author_pass2"]) == 64, "row_hashes present")
chk("G1 KAPPA.json has sha256 sidecar", (g / "gate" / "KAPPA.json.sha256").read_text().split()[0] == C.sha256_file(g / "gate" / "KAPPA.json"), "sidecar ok")
before = C.sha256_file(g / "gate" / "KAPPA.json")
e, msg = exits(G1.main, g1args(g, "kappa"))
chk("G1 second kappa run refused (write-once)", e and "write-once" in msg and C.sha256_file(g / "gate" / "KAPPA.json") == before, msg[:60])
v1 = G1.main(g1args(g, "validity"))
v2 = G1.main(g1args(g, "validity"))
chk("G1 validity with unchanged labels computes", v1["status"] == "PASS", v1["status"])
chk("L3 gate1_computed versioned, two runs -> two files + sidecars",
    v1["output_path"] != v2["output_path"] and all(Path(x + ".sha256").exists() for x in (v1["output_path"], v2["output_path"])), Path(v2["output_path"]).name)

# pass 2 edited after kappa -> validity INCOMPLETE
gt = fresh("fx_tamper", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7)
G1.main(g1args(gt, "kappa"))
p2 = gt / "labels" / "author_pass2.csv"
d = pd.read_csv(p2, dtype=str, keep_default_na=False)
d.loc[0, "label"] = "SHOWS" if d.loc[0, "label"] != "SHOWS" else "HIDES"
d.to_csv(p2, index=False)
v = G1.main(g1args(gt, "validity"))
chk("G1 pass 2 edited after kappa -> validity INCOMPLETE, hash mismatch named",
    v["status"] == "INCOMPLETE" and any("G1 hash mismatch: author_pass2" in p for p in v["problems"]) and "balanced_accuracy" not in v, str(v["problems"][:1])[:90])

# KAPPA.json edited -> sidecar mismatch
gk = fresh("fx_kedit", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7)
G1.main(g1args(gk, "kappa"))
kt = json.loads((gk / "gate" / "KAPPA.json").read_text(encoding="utf-8"))
kt["kappa"]["pass"] = not kt["kappa"]["pass"]
(gk / "gate" / "KAPPA.json").write_text(json.dumps(kt, indent=1), encoding="utf-8")
v = G1.main(g1args(gk, "validity"))
chk("G1 KAPPA.json edited -> validity INCOMPLETE (sidecar)", v["status"] == "INCOMPLETE" and any("sidecar" in p for p in v["problems"]), str(v["problems"][:1])[:90])

# INCOMPLETE kappa (pass 2 with a blank label) is archived, not overwritten, and does not lock
gi = fresh("fx_inc", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7)
good2 = (gi / "labels" / "author_pass2.csv").read_bytes()
d = pd.read_csv(gi / "labels" / "author_pass2.csv", dtype=str, keep_default_na=False)
d.loc[0, "label"] = ""
d.to_csv(gi / "labels" / "author_pass2.csv", index=False)
import os  # noqa: E402
t2 = (MD.T1.timestamp() + 150 * 60)
os.utime(gi / "labels" / "author_pass2.csv", (t2, t2))
r0 = G1.main(g1args(gi, "kappa"))
(gi / "labels" / "author_pass2.csv").write_bytes(good2)
os.utime(gi / "labels" / "author_pass2.csv", (t2, t2))
r1 = G1.main(g1args(gi, "kappa"))
chk("G1 INCOMPLETE kappa archived (not lost); a later complete kappa is accepted",
    r0["status"] == "INCOMPLETE" and r1["status"] == "COMPUTED" and len(list((gi / "gate").glob("KAPPA.INCOMPLETE__*.json"))) == 1, "archived 1")

# ------------------------------------------------------------------ A1
syn = C.make_synth(n_launches=20, seed=5)
tab = R / "table.csv"
syn.to_csv(tab, index=False)


def manifest(**over):
    m = {"source_parquet_sha256": C.FROZEN_SRC_SHA, "table_sha256": C.sha256_file(tab),
         "build_analysis_set_counts": dict(C.FROZEN_COUNTS), "table_counts": C.table_counts(syn)}
    m.update(over)
    Path(str(tab) + ".manifest.json").write_text(json.dumps(m), encoding="utf-8")


mp = Path(str(tab) + ".manifest.json")
e, msg = exits(C.read_long, str(tab), "real")
chk("A1 real run without manifest refused", e and "manifest" in msg, msg[:70])
manifest(source_parquet_sha256="0" * 64)
e, msg = exits(C.read_long, str(tab), "real")
chk("A1 manifest source hash != FROZEN refused", e and "FROZEN" in msg, msg[:70])
manifest(build_analysis_set_counts={"n_rounds": 1, "n_launches": 1, "n_rater_rows": 1})
e, msg = exits(C.read_long, str(tab), "real")
chk("A1 build_analysis_set counts != FROZEN refused", e and "counts" in msg, msg[:70])
manifest(table_sha256="0" * 64)
e, msg = exits(C.read_long, str(tab), "real")
chk("A1 table hash != manifest refused", e and "table" in msg, msg[:70])
manifest()
saved = C.SRC_PARQUET
fake = R / "fake.parquet"
fake.write_bytes(b"not the source")
C.SRC_PARQUET = fake
e, msg = exits(C.read_long, str(tab), "real")
C.SRC_PARQUET = saved
chk("A1 source parquet on disk with wrong SHA-256 refused", e and "on disk" in msg, msg[:70])
e, msg = exits(C.read_long, "HABERMAS_SHUFFLED", "real")
chk("A1 real with HABERMAS_SHUFFLED refused", e, msg[:70])
df, _ = C.read_long(str(tab), "real")
chk("A1 matching manifest + parquet hash (real file re-hashed) accepted", len(df) == len(syn), f"{len(df)} rows")
df, _ = C.read_long(str(tab), "synthetic")
chk("A1 non-real kinds are not blocked", len(df) == len(syn), "ok")

# ------------------------------------------------------------------ A3
gl = R / "lock"
gl.mkdir()
(gl / "A2_TIER.json").write_text("{}", encoding="utf-8")   # the pre-R4 all-launch tier is NOT the tier of record
e, msg = exits(C.check_kind, "real", gl)
chk("R4 lock: only the pre-R4 A2_TIER.json present -> refused (tier of record is A2_TIER_R4.json)", e and "A2_TIER_R4" in msg, msg[:70])
(gl / C.TIER_FILE).write_text("{}", encoding="utf-8")
e, msg = exits(C.check_kind, "real", gl)
chk("A3 GATE1_RESULT.json absent -> refused", e, msg[:60])
(gl / "GATE1_RESULT.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
e, msg = exits(C.check_kind, "real", gl)
chk("R4 lock: DESIGN.json missing -> refused", e and "DESIGN.json" in msg, msg[:70])
(gl / "DESIGN.json").write_bytes(b'{"design": "two_human"}')
C.write_sidecar(gl / "DESIGN.json")
(gl / "DESIGN.json").write_bytes(b'{"design": "single_labeler"}')
e, msg = exits(C.check_kind, "real", gl)
chk("R4 lock: DESIGN.json altered (sidecar mismatch) -> refused", e and "altered" in msg, msg[:70])
(gl / "DESIGN.json").write_bytes(b'{"design": "single_labeler"}')
C.write_sidecar(gl / "DESIGN.json")
for st, want in (("PASS", "VALIDATED"), ("FAIL", "EXPLORATORY_UNVALIDATED"), ("NOT_YET_MEASURABLE", "EXPLORATORY_UNVALIDATED"),
                 ("PROVISIONAL_PASS", "PROVISIONAL")):
    (gl / "GATE1_RESULT.json").write_text(json.dumps({"status": st}), encoding="utf-8")
    chk(f"A3 status {st} -> tag {want}", C.check_kind("real", gl) == want, C.GATE_TAG["tag"])
(gl / "DESIGN.json").write_bytes(b'{"design": "two_human"}')
C.write_sidecar(gl / "DESIGN.json")
(gl / "GATE1_RESULT.json").write_text(json.dumps({"status": "PROVISIONAL_PASS"}), encoding="utf-8")
e, msg = exits(C.check_kind, "real", gl)
chk("R4 lock: PROVISIONAL_PASS in the two-human design -> refused (no PROVISIONAL state there)", e and "single-labeler" in msg, msg[:70])
(gl / "DESIGN.json").write_bytes(b'{"design": "single_labeler"}')
C.write_sidecar(gl / "DESIGN.json")
for st in ("INCOMPLETE", "NOT EVALUATED", "", "pass-ish", None):
    (gl / "GATE1_RESULT.json").write_text(json.dumps({"status": st} if st is not None else {"x": 1}), encoding="utf-8")
    e, msg = exits(C.check_kind, "real", gl)
    chk(f"A3 status {st!r} -> refused", e, msg[:70])
(gl / "GATE1_RESULT.json").write_text("{broken", encoding="utf-8")
e, msg = exits(C.check_kind, "real", gl)
chk("A3 unparsable GATE1_RESULT.json -> refused", e, msg[:60])
# tag is stamped on the output and the RUNS row (tested against a scratch RUNS file)
(gl / "GATE1_RESULT.json").write_text(json.dumps({"status": "FAIL"}), encoding="utf-8")
C.check_kind("real", gl)
real_runs = run_log.RUNS
run_log.RUNS = R / "RUNS_scratch.md"
p = C.write_result(R / "tagged.json", {"x": 1}, __file__, "real", 0, [], "tag test")
run_log.RUNS = real_runs
C.GATE_TAG["tag"] = ""
chk("A3 output JSON and RUNS row carry EXPLORATORY_UNVALIDATED",
    json.loads(Path(p).read_text())["gate_tag"] == "EXPLORATORY_UNVALIDATED" and "EXPLORATORY_UNVALIDATED" in (R / "RUNS_scratch.md").read_text(), Path(p).name)

# ------------------------------------------------------------------ L3
p1 = C.write_result(R / "same.json", {"v": 1}, __file__, "synthetic", 0, [], "L3 test")
p2 = C.write_result(R / "same.json", {"v": 2}, __file__, "synthetic", 0, [], "L3 test")
chk("L3 same --out twice -> two distinct files, first intact", p1 != p2 and json.loads(Path(p1).read_text())["v"] == 1, f"{Path(p1).name} / {Path(p2).name}")
chk("L3 sidecar sha256 equals file hash", Path(p1 + ".sha256").read_text().split()[0] == C.sha256_file(p1), "ok")
try:
    C.write_new(Path(p1), "x")
    chk("L3 write_new refuses existing path", False, "overwrote")
except FileExistsError:
    chk("L3 write_new refuses existing path", True, "FileExistsError")
last = [l for l in run_log.RUNS.read_text(encoding="utf-8").splitlines() if "L3 test" in l][-1]
chk("L3 RUNS.md row carries the output sha256", "sha256:" + C.sha256_file(p2) in last, "ok")

# ------------------------------------------------------------------ N1a (small version; the >=200 check is n1_length_coverage.py)
cv = COV.run_check(R=40, B=300)
chk("N1a [R3] adjusted alpha covers 0 in >= 85% (40 datasets, B=300) under the length confound",
    cv["coverage"]["alpha"] >= 0.85, f"alpha {cv['covers_0']['alpha']}/40 N1u {cv['covers_0']['N1u']}/40 N1h {cv['covers_0']['N1h']}/40")
chk("N1a unadjusted N1u rejects more often than adjusted alpha", cv["false_positive_rate"]["N1u"] > cv["false_positive_rate"]["alpha"],
    f"FP N1u {cv['false_positive_rate']['N1u']:.3f} alpha {cv['false_positive_rate']['alpha']:.3f}")
C.write_result(R / "fixes_results.json", {"all_pass": bool(ok), "n1a_small": cv}, __file__, "synthetic", "n/a", [], "test_fixes results")
print("FIX TESTS PASS" if ok else "FIX TESTS FAILED")
sys.exit(0 if ok else 1)
