"""Run logger: appends one row per analysis run to P/analysis/RUNS.md.

Each row: UTC time, script, data kind, seed, git-free code hash (sha256 over the bytes of the
script plus every .py in analysis/), input data SHA256(s), output path,
note.  Import and call log_run(...) from a script, or use the CLI:
  python -I run_log.py --script X --kind K --seed S --inputs a b --output O [--note N]
"""
import argparse
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "RUNS.md"
HEADER = ("# RUNS (auto-appended by run_log.py; do not edit by hand)\n\n"
          "| UTC | script | data kind | seed | code sha256 (script+common+run_log) | input sha256 | output | note |\n"
          "|---|---|---|---|---|---|---|---|\n")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def code_hash(script):
    h = hashlib.sha256()
    for f in sorted(set(HERE.glob("*.py")) | {Path(script).resolve()}, key=lambda x: x.name):
        if f.exists():
            h.update(f.name.encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def log_run(script, kind, seed, inputs, output, note=""):
    ins = "; ".join(f"{Path(i).name}:{_sha(i)[:16]}" if Path(i).exists() else f"{Path(i).name}:MISSING"
                    for i in inputs)
    outcell = str(output)
    if output and Path(outcell).is_file():   # L3: the output's own sha256 goes in the row
        outcell += " sha256:" + _sha(outcell)
    row = "| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        Path(script).name, kind, seed, code_hash(script)[:16], ins, outcell, note.replace("|", "/"))
    if not RUNS.exists():
        RUNS.write_text(HEADER, encoding="utf-8")
    with open(RUNS, "a", encoding="utf-8", newline="\n") as f:
        f.write(row)
    return row


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("--output", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    print(log_run(a.script, a.kind, a.seed, a.inputs, a.output, a.note))
