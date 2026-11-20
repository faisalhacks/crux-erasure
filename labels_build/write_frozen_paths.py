"""Derive P/gate1/sample.json and P/gate1/item_key.csv from labels_build/key.json (same content)."""
import csv, hashlib, json, sys
from pathlib import Path
P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
key = json.loads((P / "labels_build" / "key.json").read_text(encoding="utf-8"))
G = P / "gate1"
G.mkdir(exist_ok=True)
sample = {"source": "labels_build/key.json (written by build_packets.py)", "python": sys.version.split()[0],
          "data_sha256": key["data_sha256"], "seeds": key["seeds"], "sample": key["sample"],
          "duplicate_sources_index": key["duplicate_sources_index"]}
(G / "sample.json").write_text(json.dumps(sample, indent=1), encoding="utf-8", newline="\n")
with open(G / "item_key.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["item_id", "labeler", "launch_id", "round_id", "cand", "role", "dup_of"])
    for i in key["items"]:
        w.writerow([i["item_id"], i["labeler"], i["launch_id"], i["round_id"], i["cand"], i["role"], i["dup_of"] or ""])
sys.path.insert(0, str(P / "analysis"))
from run_log import log_run
log_run(__file__, "labelpacket", "n/a (derived from key.json)", [P / "labels_build" / "key.json"], str(G),
        "wrote gate1/sample.json and gate1/item_key.csv from key.json; no new draw")
print("ok", hashlib.sha256((G / "sample.json").read_bytes()).hexdigest()[:16])
