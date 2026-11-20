"""Build the REAL A2 long table (schema in common.py) after gate 1 was recorded (GATE1_RESULT.json, rules R5).
Same construction as build_a2_long_shuffled.py, WITHOUT the shuffle, plus the columns the pre-registered
sensitivity models and N4 need (FR s7 / s8).  No definition is chosen here that FR does not fix:
  E      scorer-1 E (a2_scores_v2.jsonl; None -> NaN = zero cruxes or parse failure)            FR s4
  E_pos  A2e: SIDED counts as shown -> hidden = BLENDED or OMITTED; share over the cruxes          FR s7 A2e
  E_w    A2g: each crux weighted by the share of the round's members named on either side of it    FR s7 A2g
  vague  A2f: count of the FR word list (whole word, case-insensitive) per 100 words ([A-Za-z0-9']+)  FR s7 A2f
  own_sim A2b: cosine(statement, that rater's own opinion), sentence-transformers/all-MiniLM-L6-v2     FR s7 A2b
  minority N4: first-listed crux; side with fewer members = minority (1), other side 0; rater on neither
           side or equal sides -> NaN.  Members numbered 1.. over opinions sorted by participant_id (scorer.py)
  log_len, flesch: FR s7 (common.n_words / common.flesch)
Writes <out>.parquet + .manifest.json (same manifest form as the shuffled table; verify_source checks it).
Usage: python -I build_a2_long_real.py OUT.parquet"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402

out = Path(sys.argv[1])
if C.check_kind("real") != "HIDE_NOT_HUMAN_VALIDATED":
    sys.exit("unexpected gate tag")
VAGUE = ("some many various several certain often sometimes generally may might could perhaps possibly balance "
         "balanced appropriate reasonable important consider considered factors issues aspects range complex").split()
VRE = re.compile(r"\b(" + "|".join(VAGUE) + r")\b", re.IGNORECASE)
HIDDEN = {"SIDED", "BLENDED", "OMITTED"}
HIDDEN_POS = {"BLENDED", "OMITTED"}

sc = {}
for l in open(C.A / "scores" / "a2_scores_v2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    sc[(r["round_id"], int(r["cand"]))] = r
ex = {}
for l in open(C.A / "scores" / "a2_extractions_v2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    ex[r["round_id"]] = r

groups = [json.loads(l) for l in open(C.PILOT / "all_groups.jsonl", encoding="utf-8")]
from sentence_transformers import SentenceTransformer  # noqa: E402
st = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
texts = sorted({t for g in groups for t in list(g["candidates"]) + list(g["opinions"].values())})
emb = st.encode(texts, batch_size=128, normalize_embeddings=True, show_progress_bar=False)
EMB = dict(zip(texts, emb))

rows, n_label_mismatch = [], 0
for g in groups:
    rid = g["round_id"]
    order = [pid for pid, _ in sorted(g["opinions"].items())]
    num = {pid: i + 1 for i, pid in enumerate(order)}
    nmem = len(order)
    x = ex.get(rid)
    cruxes = x["cruxes"] if (x and x.get("ok")) else []
    stmt = []
    for j, c in enumerate(g["candidates"]):
        s = sc.get((rid, j))
        E = np.nan if (s is None or s["E"] is None) else float(s["E"])
        E_pos = E_w = np.nan
        if s is not None and s["E"] is not None and s.get("labels"):
            lab = s["labels"]
            if len(lab) != len(cruxes):
                n_label_mismatch += 1
            else:
                E_pos = sum(lb in HIDDEN_POS for lb in lab) / len(lab)
                w = [(len(set(cx["members_a"]) | set(cx["members_b"]))) / nmem for cx in cruxes]
                E_w = sum(wi for wi, lb in zip(w, lab) if lb in HIDDEN) / sum(w)
        nw = C.n_words(c)
        stmt.append(dict(E=E, E_pos=E_pos, E_w=E_w, log_len=float(np.log(nw)) if nw > 0 else np.nan, flesch=C.flesch(c),
                         vague=100.0 * len(VRE.findall(c)) / max(nw, 1), n_cruxes=(s or {}).get("n_cruxes")))
    for r in g["raters"]:
        mino = np.nan
        if cruxes:
            a, b = set(cruxes[0]["members_a"]), set(cruxes[0]["members_b"])
            k = num.get(r["pid"])
            if len(a) != len(b) and k is not None and (k in a) != (k in b):
                small = a if len(a) < len(b) else b
                mino = 1.0 if k in small else 0.0
        own = g["opinions"].get(r["pid"])
        for j in range(4):
            sim = float(np.dot(EMB[g["candidates"][j]], EMB[own])) if own else np.nan
            rows.append(dict(launch_id=g["launch_id"], round_id=rid, rater_id=r["pid"], cand=j, rank=r["ranks"][j],
                             own_sim=sim, minority=mino, **stmt[j]))
d = pd.DataFrame(rows)
d.to_parquet(out, index=False)
import sentence_transformers  # noqa: E402
man = {"source_parquet_sha256": C.FROZEN_SRC_SHA, "table_sha256": C.sha256_file(out),
       "build_analysis_set_counts": C.FROZEN_COUNTS, "table_counts": C.table_counts(pd.read_parquet(out)),
       "ranks": "REAL (numerical_ranks, 0 = best); built after GATE1_RESULT.json rules R5 VALIDATED_PRESENCE",
       "gate_tag": C.GATE_TAG["tag"],
       "label_extraction_length_mismatch_statements": n_label_mismatch,
       "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2", "sentence_transformers": sentence_transformers.__version__,
                     "normalize": True, "device": "cpu"},
       "inputs": {"a2_scores_v2.jsonl": C.sha256_file(C.A / "scores" / "a2_scores_v2.jsonl"),
                  "a2_extractions_v2.jsonl": C.sha256_file(C.A / "scores" / "a2_extractions_v2.jsonl"),
                  "all_groups.jsonl": C.sha256_file(C.PILOT / "all_groups.jsonl")}}
Path(str(out) + ".manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
import run_log  # noqa: E402
run_log.log_run(__file__, "real", "n/a", [C.A / "scores" / "a2_scores_v2.jsonl", C.A / "scores" / "a2_extractions_v2.jsonl",
                                          C.PILOT / "all_groups.jsonl"], str(out), f"[{C.GATE_TAG['tag']}] real A2 long table, {len(d)} rows")
print(json.dumps(man["table_counts"]), len(d), int(d.E.isna().sum()), "label/crux mismatches:", n_label_mismatch,
      "minority non-NaN rater-rounds:", int(d.drop_duplicates(["round_id", "rater_id"]).minority.notna().sum()))
