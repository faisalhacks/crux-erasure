"""Reviewer check: recompute every hash recorded in gate1/FREEZE.json; timing and labels checks (listing only)."""
import datetime as dt
import hashlib
import json
import os

P = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def mt(p):
    return dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc).isoformat()


fz = json.load(open(os.path.join(P, "gate1", "FREEZE.json"), encoding="utf-8"))
bad = []
n = 0
for k, v in fz["files"].items():
    n += 1
    got = sha(os.path.join(P, v["path"]))
    if got != v["sha256"]:
        bad.append(("files", v["path"], v["sha256"], got))
for path, h in fz["r5_manifest_files"].items():
    n += 1
    fp = os.path.join(P, path)
    if not os.path.exists(fp):
        bad.append(("r5", path, h, "MISSING")); continue
    got = sha(fp)
    if got != h:
        bad.append(("r5", path, h, got))
man = json.load(open(os.path.join(P, "gate1", "R5_FREEZE_MANIFEST.json"), encoding="utf-8"))
mp = sorted(p.replace("\\", "/") for p in man["paths"])
print("hashes checked:", n, "mismatches:", bad)
print("manifest paths == r5_manifest_files keys:", mp == sorted(fz["r5_manifest_files"]),
      "| only in manifest:", sorted(set(mp) - set(fz["r5_manifest_files"])),
      "| only in FREEZE:", sorted(set(fz["r5_manifest_files"]) - set(mp)))
for f in ["gate1/FREEZE.json", "gate1/R5_FREEZE_MANIFEST.json", "gate1/T_READY.txt",
          "gate1/STEP2_computed__20261116T015355Z.json", "gate1/step2_private/rounds__20261116T015355Z.csv",
          "gate1/gate1_r5_computed__20261116T015404Z.json", "FROZEN_RULES.md", "analysis/step2_reference.py"]:
    print(f, "mtime", mt(os.path.join(P, f)))
print("frozen_utc", fz["frozen_utc"], "label_files", fz["label_files"], "first_label_file", fz["first_label_file"])
lab = os.path.join(P, "labels")
print("labels listing (incl. hidden):", os.listdir(lab))
print("author file exists:", os.path.exists(os.path.join(lab, "author_verification.csv")))
print("T_READY.txt:", repr(open(os.path.join(P, "gate1", "T_READY.txt"), encoding="utf-8").read()))
print("FROZEN_RULES read-only attr:", not os.access(os.path.join(P, "FROZEN_RULES.md"), os.W_OK))
print("other STEP2_computed files:", [x for x in os.listdir(os.path.join(P, "gate1")) if x.startswith("STEP2_computed")])
print("other gate1_r5_computed files:", [x for x in os.listdir(os.path.join(P, "gate1")) if x.startswith("gate1_r5_computed")])
print("GATE1_RESULT exists:", os.path.exists(os.path.join(P, "gate1", "GATE1_RESULT.json")))
