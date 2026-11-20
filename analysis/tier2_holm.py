"""Holm step-down over the Tier-2 family (FR s9): N1, A4, A3, N3, N4 that actually ran (<= 5).
Usage: tier2_holm.py --out F name=path.json:key.path ...   e.g. N1=n1.json:erasure.p_boot
Family membership depends only on data-availability counts (FR s9), so NOT_RUN items are skipped
only if their JSON says status NOT_RUN.  Intervals stay unadjusted."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import run_log  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--kind", required=True, choices=C.KINDS)
ap.add_argument("items", nargs="+")
a = ap.parse_args()
TAG = C.check_kind(a.kind)   # [fix 2026-11-16, logged in RUNS.md] stamp the gate tag on real outputs like every other script
raw, srcs = {}, []
for it in a.items:
    name, spec = it.split("=", 1)
    path, key = spec.split(":", 1)
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    srcs.append(path)
    if j.get("status") == "NOT_RUN":
        continue
    for k in key.split("."):
        j = j[k]
    raw[name] = float(j)
res = {"kind": a.kind, "family": sorted(raw), "raw_p": raw, "holm_p": C.holm(raw), "alpha": 0.05,
       "gate_tag": TAG if a.kind == "real" else f"NOT_REAL({a.kind})"}
Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8")
run_log.log_run(__file__, a.kind, "none", srcs, a.out, (f"[{TAG}] " if a.kind == "real" else "") + f"Holm over {sorted(raw)}")
print(json.dumps(res))
