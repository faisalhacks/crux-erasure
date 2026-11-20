"""gate1_r5.py -- FROZEN_RULES 6.R5: combine step 2 and step 3 into the R5 gate status (R5; decisions.md D50, D51).

Writes P/gate1/gate1_r5_computed__<utc>.json (never overwritten).  It never writes GATE1_RESULT.json: an Opus reviewer
re-derives the record and the planning room writes GATE1_RESULT.json with "rules": "R5" and the computed status only.

D51 time-out.  T_ready = ISO UTC in P/gate1/T_READY.txt (written by the orchestrator when READY.md is published);
T_cut = T_ready + 30 min.  Author file labels/author_verification.csv:
  ON_TIME   exists and its modification time <= T_cut          -> step 3 is the author's (verification_eval.py)
  LATE      exists, modification time > T_cut                   -> step 3 = NOT_DONE; file = labelled post-gate check
  NOT_DONE  absent and now >= T_cut                             -> step 3 = NOT_DONE (no author file by T_cut)
  PENDING   absent and now < T_cut, or T_READY.txt missing      -> nothing can be recorded yet
With step 3 NOT_DONE the gate is recorded from step 2 alone (at most VALIDATED_PRESENCE).  The LLM panel's answers to
the packet questions are "LLM verification of LLM-extracted evidence (supplementary; not human)" and never enter here.
"""
import argparse
import glob
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
P_DEFAULT = HERE.parent
CUT_MIN = 30
STEP2_CODES = ("PASS", "WEAK", "FAIL", "UNUSABLE")
STEP3_CODES = ("SUPPORTED", "INCONCLUSIVE", "CONTRADICTED", "UNUSABLE", "INCOMPLETE")
STATUSES = ("VALIDATED_BOTH", "VALIDATED_PRESENCE", "VALIDATED_HIDE_EVIDENCE", "FAIL", "EXPLORATORY_UNVALIDATED",
            "NOT_EVALUATED")


def parse_iso(s):
    s = s.strip().replace("Z", "+00:00")
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        raise ValueError("T_READY must carry a UTC designator (Z)")
    return d.astimezone(timezone.utc)


def author_timing(labels_file, t_ready, now):
    """-> (state, info).  t_ready None -> PENDING."""
    lf = Path(labels_file)
    info = {"t_ready": t_ready.isoformat() if t_ready else None}
    if t_ready is None:
        return "PENDING", {**info, "why": "gate1/T_READY.txt missing"}
    t_cut = t_ready + timedelta(minutes=CUT_MIN)
    info["t_cut"] = t_cut.isoformat()
    if lf.exists():
        mt = datetime.fromtimestamp(lf.stat().st_mtime, timezone.utc)
        info["author_file_mtime"] = mt.isoformat()
        return ("ON_TIME" if mt <= t_cut else "LATE"), info
    return ("NOT_DONE" if now >= t_cut else "PENDING"), info


def combine(step2, step3, timing):
    """THE R5 status rule.  step2 in STEP2_CODES or None; step3 in STEP3_CODES or None; timing from author_timing.
    Returns (status, notes).  'PENDING' means nothing may be recorded yet."""
    notes = []
    if step2 is None:
        return "PENDING", ["step 2 not computed"]
    if step2 not in STEP2_CODES:
        raise ValueError(step2)
    if timing == "PENDING":
        return "PENDING", ["author file not yet due (before T_cut) or T_READY missing"]
    if timing in ("NOT_DONE", "LATE"):            # D51: gate from step 2 alone, at most VALIDATED_PRESENCE
        notes.append("step 3 NOT DONE (no author file by T_cut)")
        if timing == "LATE":
            notes.append("author file arrived after T_cut: reported as a labelled post-gate check, not used for the gate")
        return {"PASS": "VALIDATED_PRESENCE", "FAIL": "FAIL"}.get(step2, "EXPLORATORY_UNVALIDATED"), notes
    # ON_TIME
    if step2 == "FAIL":
        return "FAIL", notes
    if step3 is None or step3 == "INCOMPLETE":
        return "PENDING", ["author file present but step 3 not computed / file incomplete: wait, never fill"]
    if step3 not in STEP3_CODES:
        raise ValueError(step3)
    if step3 == "CONTRADICTED":
        notes.append("step 3 CONTRADICTED: every E-based result EXPLORATORY_UNVALIDATED (D50 q6, skeptic 2)")
        if step2 == "PASS":
            notes.append("presence check passed (reported with its scoped wording)")
        return "EXPLORATORY_UNVALIDATED", notes
    if step2 == "PASS" and step3 == "SUPPORTED":
        return "VALIDATED_BOTH", notes
    if step2 == "PASS":
        return "VALIDATED_PRESENCE", notes
    if step3 == "SUPPORTED":
        return "VALIDATED_HIDE_EVIDENCE", notes
    return "EXPLORATORY_UNVALIDATED", notes


def latest(gd, pattern):
    f = sorted(glob.glob(str(Path(gd) / pattern)))
    return Path(f[-1]) if f else None


def run(root, now=None, step3_file=None):
    root = Path(root)
    gd = root / "gate1"
    now = now or datetime.now(timezone.utc)
    tr = gd / "T_READY.txt"
    t_ready = parse_iso(tr.read_text(encoding="utf-8")) if tr.exists() else None
    timing, tinfo = author_timing(root / "labels" / "author_verification.csv", t_ready, now)
    s2f = latest(gd, "STEP2_computed__*.json")
    s2 = json.loads(s2f.read_text(encoding="utf-8")) if s2f else None
    s3 = None
    s3f = Path(step3_file) if step3_file else latest(gd, "STEP3_computed__*.json")
    if timing == "ON_TIME" and s3f and s3f.exists():
        s3 = json.loads(s3f.read_text(encoding="utf-8"))
    pre_notes = []
    if timing == "ON_TIME" and s3 and s3.get("outcome") == "INCOMPLETE" and "t_cut" in tinfo \
            and now >= datetime.fromisoformat(tinfo["t_cut"]):
        # D51 reading: a file that is still incomplete at T_cut was not submitted; a completed version saved later is LATE
        timing = "NOT_DONE"
        pre_notes.append("author file present but incomplete at T_cut: treated as not submitted (D51)")
        s3 = None
    status, notes = combine(s2["outcome"] if s2 else None, s3["outcome"] if s3 else None, timing)
    notes = pre_notes + notes
    rec = {"rules": "R5", "computed_status": status, "notes": notes, "author_timing": timing, **tinfo,
           "step2_file": str(s2f) if s2f else None, "step2_outcome": s2["outcome"] if s2 else None,
           "step3_file": str(s3f) if (s3 and s3f) else None, "step3_outcome": s3["outcome"] if s3 else
           ("NOT_DONE" if timing in ("NOT_DONE", "LATE") else None),
           "computed_utc": now.isoformat(),
           "panel": "LLM verification of LLM-extracted evidence (supplementary; not human); never part of this status"}
    return status, rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(P_DEFAULT))
    ap.add_argument("--step3", default=None)
    a = ap.parse_args(argv)
    status, rec = run(a.root, step3_file=a.step3)
    print(json.dumps(rec, indent=1))
    if status == "PENDING":
        print("PENDING: nothing written")
        return 1
    out = Path(a.root) / "gate1" / f"gate1_r5_computed__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(out, "x", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    print("written", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
