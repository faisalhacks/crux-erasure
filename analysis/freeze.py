"""freeze.py [R4] (FR header "At freeze", FR s5, s6.0).  python -I freeze.py [--root P] [--out FREEZE.json]

If any file exists in <root>\\labels\\: write <root>\\FREEZE.json once (UTC time, sha256 of FROZEN_RULES.md, EXPERIMENTS.md,
analysis\\scorer_manifest.json, analysis\\N2_ANALYSIS_SPEC.md, every label file present, which label file arrived first by
modification time, name as tie-break), then mark FROZEN_RULES.md read-only (attrib +R).
Idempotent: if FREEZE.json exists it is NEVER rewritten; the read-only flag is re-applied and a changed FROZEN_RULES.md is
reported (exit 2).  Exit codes: 0 frozen / already frozen, 1 nothing to freeze (labels empty), 2 problem.
Stdlib only.  Tests pass --root <temp dir>; the real project is never touched by them."""
import argparse, hashlib, json, os, stat, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
TRACKED = {"FROZEN_RULES.md": "FROZEN_RULES.md", "EXPERIMENTS.md": "EXPERIMENTS.md",
           "scorer_manifest.json": "analysis/scorer_manifest.json", "N2_ANALYSIS_SPEC.md": "analysis/N2_ANALYSIS_SPEC.md",
           # [R5] code of the R5 gate, hashed at freeze (FR 6.R5)
           "step2_reference.py": "analysis/step2_reference.py", "verification_eval.py": "analysis/verification_eval.py",
           "gate1_r5.py": "analysis/gate1_r5.py"}
# [R5] optional list of further files to hash at freeze (25-item packet, key, quotes, scorer outputs of the 25 items),
# written by the packet builder: {"paths": ["rel/path", ...]} relative to the project root.
R5_MANIFEST = "gate1/R5_FREEZE_MANIFEST.json"
TRIGGERS = ("labels", "step2")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def utc(ts=None):
    d = datetime.now(timezone.utc) if ts is None else datetime.fromtimestamp(ts, timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def make_readonly(p):
    if os.name == "nt":
        subprocess.run(["attrib", "+R", str(p)], check=True, capture_output=True)
    else:
        os.chmod(p, os.stat(p).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    return not os.access(p, os.W_OK)


def is_readonly(p):
    return not (os.stat(p).st_mode & stat.S_IWRITE)


def label_files(ld):
    return sorted([p for p in Path(ld).iterdir() if p.is_file()], key=lambda p: p.name) if Path(ld).is_dir() else []


def run(root, out=None, trigger="labels"):
    """trigger='labels' (default): freeze only if a file exists in labels\\.  trigger='step2' [R5]: the first run of
    step2_reference.py freezes even with labels\\ empty (FR 6.R5: FREEZE.json before the step-2 reference is computed)."""
    if trigger not in TRIGGERS:
        return 2, f"unknown trigger {trigger!r}"
    root = Path(root)
    out = Path(out) if out else root / "FREEZE.json"
    fr = root / "FROZEN_RULES.md"
    if out.exists():
        rec = json.loads(out.read_text(encoding="utf-8"))
        msg = ["already frozen; FREEZE.json not rewritten"]
        code = 0
        if fr.exists():
            make_readonly(fr)
            if sha(fr) != rec.get("files", {}).get("FROZEN_RULES.md", {}).get("sha256"):
                msg.append("WARNING: FROZEN_RULES.md differs from the hash recorded in FREEZE.json")
                code = 2
        return code, "; ".join(msg)
    labs = label_files(root / "labels")
    if not labs and trigger == "labels":
        return 1, "no file in labels\\; nothing frozen"
    if not fr.exists():
        return 2, "FROZEN_RULES.md missing"
    st = {p: p.stat() for p in labs}
    first = min(labs, key=lambda p: (st[p].st_mtime_ns, p.name)) if labs else None
    rec = {"frozen_utc": utc(), "root": str(root), "files": {}, "label_files": {},
           "trigger": "first label file" if labs else "first run of step2_reference.py (labels\\ empty)",
           "first_label_file": first.name if first else None,
           "first_label_basis": "earliest modification time (ties: file name)",
           "missing_tracked": [], "r5_manifest_files": {}}
    for k, rel in TRACKED.items():
        p = root / rel
        if p.exists():
            rec["files"][k] = {"path": rel, "sha256": sha(p)}
        else:
            rec["missing_tracked"].append(rel)
    mp = root / R5_MANIFEST
    if mp.exists():
        try:
            rels = json.loads(mp.read_text(encoding="utf-8")).get("paths", [])
        except Exception as ex:  # noqa: BLE001
            return 2, f"{R5_MANIFEST} unreadable ({type(ex).__name__}); nothing frozen"
        rec["files"]["R5_FREEZE_MANIFEST.json"] = {"path": R5_MANIFEST, "sha256": sha(mp)}
        for rel in rels:
            p = root / rel
            rec["r5_manifest_files"][rel] = sha(p) if p.exists() else None
            if not p.exists():
                rec["missing_tracked"].append(rel)
    for p in labs:
        rec["label_files"][p.name] = {"sha256": sha(p), "mtime_utc": utc(st[p].st_mtime), "bytes": st[p].st_size}
    for stem in ("author_pass1", "author_pass2", "volunteer_pass1", "author_verification"):   # keys gate1.py / R5 read
        n = stem + ".csv"
        if n in rec["label_files"]:
            rec[stem + "_sha256"] = rec["label_files"][n]["sha256"]
            rec[stem + "_mtime_utc"] = rec["label_files"][n]["mtime_utc"]
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, indent=1, sort_keys=True), encoding="utf-8")
    try:
        with open(out, "xb") as f:               # exclusive create: never overwrite
            f.write(tmp.read_bytes())
    finally:
        tmp.unlink(missing_ok=True)
    ro = make_readonly(fr)
    return 0, f"frozen ({rec['trigger']}): first label file {first.name if first else None}; FROZEN_RULES.md read-only={ro}" + \
              (f"; missing tracked: {rec['missing_tracked']}" if rec["missing_tracked"] else "")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", default=None)
    ap.add_argument("--trigger", default="labels", choices=TRIGGERS)
    a = ap.parse_args()
    c, m = run(a.root, a.out, a.trigger)
    print(m)
    sys.exit(c)
