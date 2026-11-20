"""Scorer-1 (v2) outputs for the 25 Part-2 (v5b) verification items -> analysis/scores/packet_v5b_scores.jsonl (+ .sha256).
decisions.md D62: EXISTING v2 scores only, no new scoring.  Originals: gate1_scores.jsonl first, then a2_scores_v2.jsonl
(never v1), as analysis/packet_v5_scores.py assemble(); N2: analysis/scores/n2_scores_v2.jsonl (row cand == job_id).
Same schema and key order as packet_v5_scores.jsonl.  Reads the v5b key for the mapping; reads no labels file.
Run:  C:/Users/intel/miniconda3/python.exe -I scores_b.py
"""
import csv
import hashlib
import json
from pathlib import Path

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
KEY = P / "labels_build" / "v5b" / "key_verification_b.csv"
SC = P / "analysis" / "scores"
OUT = SC / "packet_v5b_scores.jsonl"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def one(m, what):
    if len(m) > 1 and any(json.dumps(x, sort_keys=True) != json.dumps(m[0], sort_keys=True) for x in m):
        raise SystemExit(f"STOP: {len(m)} differing v2 rows for {what}")
    return m[0] if m else None


def main():
    rows = list(csv.DictReader(open(KEY, encoding="utf-8", newline="")))
    g1, a2, n2 = jl(SC / "gate1_scores.jsonl"), jl(SC / "a2_scores_v2.jsonl"), jl(SC / "n2_scores_v2.jsonl")
    out = []
    for k in rows:
        if k["kind"] == "original":
            key = (k["launch_id"], k["round_id"], int(k["cand"]))
            r, src = one([x for x in g1 if (x["launch_id"], x["round_id"], x["cand"]) == key], k["item_id"]), "analysis/scores/gate1_scores.jsonl"
            if r is None:
                r, src = one([x for x in a2 if (x["launch_id"], x["round_id"], x["cand"]) == key], k["item_id"]), "analysis/scores/a2_scores_v2.jsonl"
        else:
            r = one([x for x in n2 if x["cand"] == k["statement_id"]], k["item_id"])
            src = "analysis/scores/n2_scores_v2.jsonl"
            if r is not None:
                assert (r["launch_id"], r["round_id"]) == (k["launch_id"], k["round_id"]), k["item_id"]
        if r is None:
            raise SystemExit(f"STOP: no existing v2 score for {k['item_id']} ({k['kind']}); no new scoring allowed (D62)")
        ok = bool(r["extract_ok"]) and (r["n_cruxes"] == 0 or bool(r["label_ok"]))
        out.append(dict(item_id=k["item_id"], kind=k["kind"], E=r["E"], n_cruxes=r["n_cruxes"], ok=ok,
                        statement_id=k["statement_id"], source=src, launch_id=k["launch_id"], round_id=k["round_id"],
                        packet_source=k["source"], scorer=r["scorer"], scorer_version="v2", labels=r["labels"],
                        provenance="reused_v2"))
    assert len(out) == 25 and len({o["item_id"] for o in out}) == 25
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for o in sorted(out, key=lambda o: o["item_id"]):
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    h = hashlib.sha256(OUT.read_bytes()).hexdigest()
    OUT.with_name(OUT.name + ".sha256").write_text(f"{h}  analysis/scores/packet_v5b_scores.jsonl\n", encoding="utf-8", newline="\n")
    print("rows", len(out), "ok", sum(o["ok"] for o in out), "sources",
          {s: sum(o["source"] == s for o in out) for s in sorted({o["source"] for o in out})}, "sha256", h)


if __name__ == "__main__":
    main()
