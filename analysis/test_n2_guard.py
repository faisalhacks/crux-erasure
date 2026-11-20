"""Unit test for n2_grid.assert_scoring_allowed() after the D56 R5 edit.  Temp files only; the real
analysis/GATE1_PASSED.json and scorer_manifest.json are never written.   python -I test_n2_guard.py"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import n2_grid as N  # noqa: E402

FAILS, CNT = [], [0]


def chk(name, cond):
    CNT[0] += 1
    if not cond:
        FAILS.append(name)
    print(("PASS " if cond else "FAIL ") + name)


def run(gate, manifest_bytes=b'{"scorer":"x"}', write_gate=True, write_manifest=True):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        gp, mp = td / "GATE1_PASSED.json", td / "scorer_manifest.json"
        if write_manifest:
            mp.write_bytes(manifest_bytes)
        if write_gate:
            g = dict(gate)
            if g.get("scorer_manifest_sha256") == "MATCH":
                g["scorer_manifest_sha256"] = N.sha256_file(mp)
            gp.write_text(json.dumps(g), encoding="utf-8")
        old = N.GATE1_PASSED, N.SCORER_MANIFEST
        N.GATE1_PASSED, N.SCORER_MANIFEST = gp, mp
        try:
            N.assert_scoring_allowed()
            return "OK"
        except SystemExit as e:
            return "REFUSED: " + str(e)
        finally:
            N.GATE1_PASSED, N.SCORER_MANIFEST = old


for st in ("VALIDATED_BOTH", "VALIDATED_PRESENCE", "VALIDATED_HIDE_EVIDENCE", "EXPLORATORY_UNVALIDATED"):
    chk(f"R5 {st} + matching manifest accepted", run(dict(rules="R5", status=st, scorer_manifest_sha256="MATCH")) == "OK")
    chk(f"R5 {st} + wrong manifest hash refused",
        run(dict(rules="R5", status=st, scorer_manifest_sha256="0" * 64)).startswith("REFUSED"))
    chk(f"R5 {st} + missing manifest hash refused", run(dict(rules="R5", status=st)).startswith("REFUSED"))
for st in ("FAIL", "NOT_EVALUATED", "PENDING", "PASS", "validated_presence", "", None):
    chk(f"R5 status {st!r} refused", run(dict(rules="R5", status=st, scorer_manifest_sha256="MATCH")).startswith("REFUSED"))
chk("R5 with no status refused", run(dict(rules="R5", scorer_manifest_sha256="MATCH")).startswith("REFUSED"))
chk("non-R5 VALIDATED_PRESENCE refused",
    run(dict(status="VALIDATED_PRESENCE", scorer_manifest_sha256="MATCH")).startswith("REFUSED"))
chk("rules R4 + VALIDATED_PRESENCE refused",
    run(dict(rules="R4", status="VALIDATED_PRESENCE", scorer_manifest_sha256="MATCH")).startswith("REFUSED"))
chk("legacy PASS still accepted (unchanged behaviour)", run(dict(status="PASS", scorer_manifest_sha256="MATCH")) == "OK")
chk("legacy FAIL refused", run(dict(status="FAIL", scorer_manifest_sha256="MATCH")).startswith("REFUSED"))
chk("missing GATE1_PASSED.json refused", run({}, write_gate=False).startswith("REFUSED"))
chk("missing scorer manifest refused",
    run(dict(rules="R5", status="VALIDATED_PRESENCE", scorer_manifest_sha256="0" * 64), write_manifest=False).startswith("REFUSED"))
chk("allowed set is exactly the four D56 statuses",
    N.R5_SCORING_STATUSES == {"VALIDATED_BOTH", "VALIDATED_PRESENCE", "VALIDATED_HIDE_EVIDENCE", "EXPLORATORY_UNVALIDATED"})
# the real project files pass (read-only check)
try:
    N.assert_scoring_allowed()
    real = "OK"
except SystemExit as e:
    real = str(e)
chk("real analysis/GATE1_PASSED.json (R5 VALIDATED_PRESENCE) accepted", real == "OK")

print(f"test_n2_guard: {CNT[0] - len(FAILS)}/{CNT[0]} PASS")
sys.exit(1 if FAILS else 0)
