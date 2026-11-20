"""Gate-1 labelling packet builder (T3-1).  Implements FROZEN_RULES.md section 5 and 6.1.

Reads: the Habermas candidate-comparison parquet (hash-checked), pilot_groups.jsonl (launch_id only,
to exclude development launches), FROZEN_RULES.md (instruction text, copied verbatim).
Writes ONLY inside P/labels_build/.  Never writes P/labels/.  Never creates a label.
The rater/ranking columns are read ONLY to apply the eligibility filter (rule 2 (e)); no ranking,
rating or score is joined to any statement or written to any output.

Run:  C:/Users/intel/miniconda3/python.exe -I build_packets.py
"""
import csv
import hashlib
import html
import json
import random
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
APART = P.parent
OUT = P / "labels_build"
DATA = APART / "data" / "habermas_gcs" / "hm_all_candidate_comparisons.parquet"
DEV = APART / "pilots" / "T3_1" / "pilot_groups.jsonl"
FROZEN = P / "FROZEN_RULES.md"
EXPECT_SHA = "7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4"
EXPECT = {"eligible_rounds": 1960, "eligible_launches": 871, "eligible_rater_rows": 9501}

SEED_SAMPLE = 20261115      # FROZEN 6.1
SEED_ORDER = {"L1": 20261117, "L2": 20261118}   # FROZEN 6.1
SEED_ITEM_ID = 20261130     # NOT specified in FROZEN; only names items, affects no sampling. Logged.


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


# ------------------------------------------------------------------ data hash
data_sha = sha256_file(DATA)
if data_sha != EXPECT_SHA:
    sys.exit(f"STOP: data hash mismatch {data_sha}")

# ------------------------------------------------------------------ eligible rounds (FROZEN section 2)
COLS = ["launch_id", "round_id", "iteration_index", "own_opinion.text", "own_opinion.metadata.provenance",
        "own_opinion.metadata.participant_id", "other_opinions.metadata.provenance",
        "other_opinions.metadata.participant_id", "other_opinions.text", "critique.metadata.provenance",
        "candidates.text", "candidates.metadata.id", "candidates.metadata.provenance",
        "rankings.candidate_ids", "rankings.numerical_ranks", "rankings.metadata.provenance",
        "ratings.metadata.provenance", "question.text"]
df = pq.read_table(DATA, columns=COLS).to_pandas()
bot_rounds = set(map(tuple, df.loc[df["critique.metadata.provenance"] == "BOT_CITIZEN",
                                   ["launch_id", "round_id"]].values))
it0 = df[df.iteration_index == 0]

groups = {}   # (launch, round) -> dict
n_raters = 0
for (lid, rid), g in it0.groupby(["launch_id", "round_id"], sort=True):
    if (lid, rid) in bot_rounds:
        continue
    opinions = {}
    bot = False
    for _, r in g.iterrows():
        if r["own_opinion.metadata.provenance"] != "HUMAN_CITIZEN":
            bot = True
        opinions[r["own_opinion.metadata.participant_id"]] = r["own_opinion.text"]
        for pid, pv, t in zip(r["other_opinions.metadata.participant_id"],
                              r["other_opinions.metadata.provenance"], r["other_opinions.text"]):
            if pv != "HUMAN_CITIZEN":
                bot = True
            opinions.setdefault(pid, t)
    if bot:
        continue
    r0 = g.iloc[0]
    cands = list(r0["candidates.text"])
    cids = list(r0["candidates.metadata.id"])
    cprov = list(r0["candidates.metadata.provenance"])
    if len(cands) != 4 or any(p != "MODEL_MEDIATOR" for p in cprov):
        continue
    if any((c or "").strip() == "Citizen's Jury" or len((c or "").split()) < 15 for c in cands):
        continue
    nr = 0
    for _, r in g.iterrows():
        if r["rankings.metadata.provenance"] != "HUMAN_CITIZEN" or r["ratings.metadata.provenance"] != "HUMAN_CITIZEN":
            continue
        if list(r["rankings.candidate_ids"]) != cids:
            continue
        ranks = list(map(int, r["rankings.numerical_ranks"]))
        if len(ranks) != 4 or -1 in ranks:
            continue
        nr += 1
    if nr < 3:
        continue
    n_raters += nr
    groups[(lid, rid)] = {"question": r0["question.text"], "opinions": opinions, "cands": cands, "cids": cids}

by_launch = {}
for (lid, rid) in groups:
    by_launch.setdefault(lid, []).append(rid)
counts = {"eligible_rounds": len(groups), "eligible_launches": len(by_launch), "eligible_rater_rows": n_raters}
if counts != EXPECT:
    sys.exit(f"STOP: eligible counts {counts} != frozen {EXPECT}")
del df, it0

dev = {json.loads(line)["launch_id"] for line in open(DEV, encoding="utf-8")}
pool = sorted(l for l in by_launch if l not in dev)
print("eligible", counts, "dev launches", len(dev), "pool", len(pool))

# ------------------------------------------------------------------ sample (FROZEN 6.1, exact recipe)
rng = random.Random(SEED_SAMPLE)
L = rng.sample(pool, 60)
sample = []
for lid in L:
    rid = rng.choice(sorted(by_launch[lid]))
    cand = rng.randrange(4)
    sample.append({"launch_id": lid, "round_id": rid, "cand": cand})
shared, u1, u2 = sample[0:20], sample[20:40], sample[40:60]
# duplicate checks, same rng, L1 first
dup = {"L1": (rng.sample(range(20), 2), rng.sample(range(20), 2)),
       "L2": (rng.sample(range(20), 2), rng.sample(range(20), 2))}

# ------------------------------------------------------------------ item ids (opaque)
rid_rng = random.Random(SEED_ITEM_ID)
used = set()


def new_id():
    while True:
        x = "%08x" % rid_rng.getrandbits(32)
        if x not in used:
            used.add(x)
            return x


for i, s in enumerate(shared):
    s["role"], s["item_id"], s["labelers"] = "shared", new_id(), ["L1", "L2"]
for s in u1:
    s["role"], s["item_id"], s["labelers"] = "unique", new_id(), ["L1"]
for s in u2:
    s["role"], s["item_id"], s["labelers"] = "unique", new_id(), ["L2"]

# ------------------------------------------------------------------ row order per labeler
packets = {}
for lab, own in (("L1", u1), ("L2", u2)):
    base = [dict(s) for s in shared] + [dict(s) for s in own]
    orng = random.Random(SEED_ORDER[lab])
    dshared, dunique = dup[lab]
    dsrc = [shared[i] for i in dshared] + [own[i] for i in dunique]
    src_ids = [s["item_id"] for s in dsrc]
    tries = 0
    while True:   # reshuffle (same rng) until each duplicated original sits in the first 30 rows so a
        orng.shuffle(base)      # repeat >= 10 rows later is always possible; count logged
        tries += 1
        if all(next(k for k, b in enumerate(base) if b["item_id"] == sid) <= 29 for sid in src_ids):
            break
    rows = [dict(b, dup_of=None) for b in base]
    for s in dsrc:
        pos = next(k for k, b in enumerate(rows) if b["item_id"] == s["item_id"])
        ins = orng.randint(pos + 10, len(rows))        # at least 10 rows after first appearance
        d = {"launch_id": s["launch_id"], "round_id": s["round_id"], "cand": s["cand"], "role": "duplicate",
             "item_id": new_id(), "labelers": [lab], "dup_of": s["item_id"]}
        rows.insert(ins, d)
    assert len(rows) == 44
    packets[lab] = (rows, tries)

# ------------------------------------------------------------------ instruction text, verbatim from FROZEN
ftxt = FROZEN.read_text(encoding="utf-8").splitlines()
k = next(i for i, l in enumerate(ftxt) if l.startswith("**Instructions given to both labelers (verbatim):**"))
instr = []
for l in ftxt[k + 1:]:
    if l.startswith(">"):
        instr.append(l[2:] if l.startswith("> ") else "")
    elif instr and l.strip() == "":
        break
    elif instr:
        break
# trailing blank '>' lines
while instr and instr[-1] == "":
    instr.pop()
INSTR_MD = "\n".join(instr) + "\n"
for banned in ("crux erasure", "sycophancy", "hypothes", "erasure", "ranking", "score"):
    assert banned not in INSTR_MD.lower(), banned


def fetch(item):
    g = groups[(item["launch_id"], item["round_id"])]
    ops = [g["opinions"][pid] for pid in sorted(g["opinions"])]   # sorted by participant_id (FROZEN 3)
    return g["question"], ops, g["cands"][item["cand"]], g["cids"][item["cand"]]


# ------------------------------------------------------------------ write outputs
OUT.mkdir(exist_ok=True)
STYLE = """body{font-family:Georgia,serif;max-width:46em;margin:2em auto;padding:0 1em;line-height:1.5;color:#111}
h1{font-size:1.5em}h2{font-size:1.2em;border-top:2px solid #444;padding-top:.8em;margin-top:2.2em}
.q{font-weight:bold}.op{margin:.4em 0}.st{background:#f1f1f1;border-left:4px solid #555;padding:.6em 1em;margin-top:1em}
pre.instr{white-space:pre-wrap;font-family:inherit;background:#fafafa;border:1px solid #ccc;padding:1em}
@media(prefers-color-scheme:dark){body{background:#161616;color:#eee}.st{background:#262626}pre.instr{background:#1e1e1e;border-color:#555}}"""

key_items = []
for lab in ("L1", "L2"):
    rows, tries = packets[lab]
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>Labelling packet {lab}</title><style>{STYLE}</style></head><body>",
             f"<h1>Labelling packet {lab}</h1>",
             "<p>44 items. Record each label in the CSV template, using the item id shown. "
             "Do not use any AI tool. Do not look anything up.</p>",
             f"<h2 id='instr'>Instructions</h2><pre class='instr'>{html.escape(INSTR_MD)}</pre>"]
    csv_rows = []
    for n, it in enumerate(rows, 1):
        q, ops, st, _ = fetch(it)
        parts.append(f"<h2 id='item-{it['item_id']}'>Item {n} of 44 &nbsp; (item_id: <code>{it['item_id']}</code>)</h2>")
        parts.append(f"<p class='q'>Question: {html.escape(q)}</p><p>Members' opinions:</p><ol>")
        for o in ops:
            parts.append(f"<li class='op'>{html.escape(o or '').replace(chr(10), '<br>')}</li>")
        parts.append("</ol>")
        parts.append(f"<div class='st'><strong>Statement:</strong><br>{html.escape(st).replace(chr(10), '<br>')}</div>")
        csv_rows.append({"item_id": it["item_id"], "question": q,
                         "opinions": "\n".join(f"{i}. {o}" for i, o in enumerate(ops, 1)),
                         "statement": st, "label": "", "main_disagreement": "", "comment": ""})
    parts.append("</body></html>")
    (OUT / f"packet_{lab}.html").write_text("\n".join(parts), encoding="utf-8", newline="\n")
    (OUT / f"LABELER_INSTRUCTIONS_{lab}.md").write_text(
        f"# Instructions for labeler {lab}\n\n" + INSTR_MD, encoding="utf-8", newline="\n")
    with open(OUT / f"TEMPLATE_{lab}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["item_id", "label", "main_disagreement", "comment"])
        for r in csv_rows:
            w.writerow([r["item_id"], "", "", ""])
    with open(OUT / f"packet_{lab}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "question", "opinions", "statement", "label",
                                          "main_disagreement", "comment"], lineterminator="\n")
        w.writeheader()
        w.writerows(csv_rows)
    for n, it in enumerate(rows, 1):
        key_items.append({"labeler": lab, "row": n, "item_id": it["item_id"], "launch_id": it["launch_id"],
                          "round_id": it["round_id"], "cand": it["cand"],
                          "cand_id": groups[(it["launch_id"], it["round_id"])]["cids"][it["cand"]],
                          "role": it["role"], "dup_of": it["dup_of"]})

key = {"WARNING": "NOT for labelers. Contains launch/round/candidate ids and duplicate links.",
       "data_sha256": data_sha, "frozen_rules_sha256": sha256_file(FROZEN),
       "seeds": {"sample_and_dups": SEED_SAMPLE, "row_order": SEED_ORDER, "item_id_naming": SEED_ITEM_ID},
       "reshuffle_tries_for_dup_spacing": {k: packets[k][1] for k in packets},
       "eligible_counts": counts, "development_launches_excluded": len(dev), "pool_launches": len(pool),
       "sample": {"shared": shared, "L1_unique": u1, "L2_unique": u2},
       "duplicate_sources_index": {"L1": {"shared_idx": dup["L1"][0], "unique_idx": dup["L1"][1]},
                                   "L2": {"shared_idx": dup["L2"][0], "unique_idx": dup["L2"][1]}},
       "items": key_items}
(OUT / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8", newline="\n")
print("written; reshuffle tries", {k: packets[k][1] for k in packets})

sys.path.insert(0, str(P / "analysis"))
from run_log import log_run  # noqa: E402
log_run(__file__, "labelpacket", f"{SEED_SAMPLE}/{SEED_ORDER['L1']}/{SEED_ORDER['L2']}/{SEED_ITEM_ID}",
        [DATA, DEV], str(OUT / "key.json"),
        f"gate1 packets 44 rows each; data sha256 full {data_sha}; no labels created; item-id seed unspecified in FROZEN")
