"""R4 packet builder (T3-1).  FROZEN_RULES.md sections 5, 6.1, 6.1a.  Writes ONLY inside P/labels_build/r4/
(and moves the void pre-R4 packets into P/labels_build/archive_void_preR4/).  Never writes P/labels/.
Never creates a label.  No score, ranking or rating is read or joined.

Run:  C:/Users/intel/miniconda3/python.exe -I r4_build.py
"""
import csv
import hashlib
import html
import json
import random
import shutil
import sys
from pathlib import Path

import pyarrow.parquet as pq

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
APART = P.parent
LB = P / "labels_build"
OUT = LB / "r4"
DATA = APART / "data" / "habermas_gcs" / "hm_all_candidate_comparisons.parquet"
DEV = APART / "pilots" / "T3_1" / "pilot_groups.jsonl"
FROZEN = P / "FROZEN_RULES.md"
SEL = LB / "n2_packet_selection.json"
EXPECT_SHA = "7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4"
EXPECT = {"eligible_rounds": 1960, "eligible_launches": 871, "eligible_rater_rows": 9501}

SEED_SAMPLE = 20261115      # FROZEN 6.1
SEED_P1 = 20261117          # FROZEN 6.1 row order pass 1
SEED_P2 = 20261118          # FROZEN 6.1 row order pass 2
SEED_REP = 20261131         # FROZEN 6.1 repeat selection
SEED_VOL = 20261135         # FROZEN 5 volunteer order
SEED_ID_A1, SEED_ID_A2, SEED_ID_V = 20261140, 20261141, 20261142   # NOT in FROZEN; name items only; logged


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


data_sha = sha256_file(DATA)
if data_sha != EXPECT_SHA:
    sys.exit(f"STOP: data hash mismatch {data_sha}")

# ------------------------------------------------------------------ eligible rounds (unchanged from build_packets.py)
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
groups = {}
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

# ------------------------------------------------------------------ 38 originals = L[0:38] (FROZEN 6.1)
rng = random.Random(SEED_SAMPLE)
L = rng.sample(pool, 60)
sample = []
for lid in L:
    rid = rng.choice(sorted(by_launch[lid]))
    cand = rng.randrange(4)
    sample.append({"launch_id": lid, "round_id": rid, "cand": cand})
rec = json.loads((P / "gate1" / "sample.json").read_text(encoding="utf-8"))["sample"]
rec_list = rec["shared"] + rec["L1_unique"] + rec["L2_unique"]
assert [(s["launch_id"], s["round_id"], s["cand"]) for s in sample] == \
       [(s["launch_id"], s["round_id"], s["cand"]) for s in rec_list], "regenerated sample != sample.json"
originals = []
for s in sample[:38]:
    g = groups[(s["launch_id"], s["round_id"])]
    originals.append(dict(kind="original", launch_id=s["launch_id"], round_id=s["round_id"], cand=s["cand"],
                          cell="", generator="", question=g["question"],
                          opinions=[g["opinions"][p] for p in sorted(g["opinions"])],
                          statement=g["cands"][s["cand"]]))
assert all(o["launch_id"] not in dev for o in originals)
sixty_launches = {s["launch_id"] for s in sample}

# ------------------------------------------------------------------ 12 N2 items (selection ids only -> texts by job_id)
sel = json.loads(SEL.read_text(encoding="utf-8"))
texts = {}
for f in list((P / "analysis" / "n2_runs" / "full_k1").glob("gens_*.jsonl")) + \
         list((P / "analysis" / "n2_runs" / "full_ext").glob("gens_*.jsonl")):
    for line in open(f, encoding="utf-8"):
        if line.strip():
            d = json.loads(line)
            texts.setdefault(d["job_id"], []).append(d)
n2 = []
for it in sel["items"]:
    c = texts.get(it["job_id"])
    assert c and len(c) >= 1, it["job_id"]
    texts_set = {x["text"] for x in c}
    assert len(texts_set) == 1, ("conflicting duplicate generations", it["job_id"])
    d = c[0]
    assert d["round_id"] == it["round_id"] and d["launch_id"] == it["launch_id"]
    assert d["text"].strip() and str(d["finish_reason"]) == "stop", it["job_id"]
    assert it["launch_id"] not in dev and it["launch_id"] not in sixty_launches
    g = groups[(it["launch_id"], it["round_id"])]
    n2.append(dict(kind="n2", launch_id=it["launch_id"], round_id=it["round_id"], cand=-1,
                   cell=it["cell"], generator=it["generator"], question=g["question"],
                   opinions=[g["opinions"][p] for p in sorted(g["opinions"])], statement=d["text"],
                   slot=it["slot"], job_id=it["job_id"]))
assert len(n2) == 12 and len({x["launch_id"] for x in n2}) == 12

base = originals + n2          # 50 items, canonical order (L order, then n2 slot order)
for i, b in enumerate(base):
    b["uid"] = i

# ------------------------------------------------------------------ repeats (FROZEN 6.1): 15 of 38 originals, 5 of 12 N2
rrng = random.Random(SEED_REP)
rep = rrng.sample(originals, 15) + rrng.sample(n2, 5)
assert len(rep) == 20

# ------------------------------------------------------------------ orders
p1 = list(base)
random.Random(SEED_P1).shuffle(p1)
p2 = list(rep)
random.Random(SEED_P2).shuffle(p2)
pv = list(base)
random.Random(SEED_VOL).shuffle(pv)
assert [x["uid"] for x in pv] != [x["uid"] for x in p1]


def draw_ids(seed, n, fmt):
    r = random.Random(seed)
    used, out = set(), []
    while len(out) < n:
        x = fmt(r)
        if x not in used:
            used.add(x)
            out.append(x)
    return out


ids_a1 = draw_ids(SEED_ID_A1, 50, lambda r: "%08x" % r.getrandbits(32))
ids_a2 = draw_ids(SEED_ID_A2, 20, lambda r: "%08x" % r.getrandbits(32))
ids_v = draw_ids(SEED_ID_V, 50, lambda r: "v%07x" % r.getrandbits(28))
assert not (set(ids_a1) & set(ids_a2)) and not (set(ids_a1 + ids_a2) & set(ids_v))

# ------------------------------------------------------------------ instructions (verbatim from FROZEN)
ftxt = FROZEN.read_text(encoding="utf-8").splitlines()
k = next(i for i, l in enumerate(ftxt) if l.startswith("> You will see a question"))
instr = []
for l in ftxt[k:]:
    if l.startswith(">"):
        instr.append(l[2:] if l.startswith("> ") else "")
    else:
        break
while instr and instr[-1] == "":
    instr.pop()
AUTHOR_TXT = "\n".join(instr) + "\n"
a0 = AUTHOR_TXT.index("Do not discuss rows with anyone")
a1 = AUTHOR_TXT.index("in `pass_started_utc`.") + len("in `pass_started_utc`.")
VOL_TXT = AUTHOR_TXT[:a0] + ("Do not discuss rows with anyone until you have returned your file. "
                             "Write the time you start, in UTC, in `pass_started_utc`.") + AUTHOR_TXT[a1:]
assert "second, shorter set" in AUTHOR_TXT and "second, shorter set" not in VOL_TXT
assert VOL_TXT.rstrip().endswith("Do not leave `label` blank.")

# ------------------------------------------------------------------ archive void packets, write outputs
ARCH = LB / "archive_void_preR4"
ARCH.mkdir(exist_ok=True)
for name in ["packet_L1.csv", "packet_L1.html", "packet_L2.csv", "packet_L2.html", "LABELER_INSTRUCTIONS_L1.md",
             "LABELER_INSTRUCTIONS_L2.md", "TEMPLATE_L1.csv", "TEMPLATE_L2.csv", "key.json"]:
    if (LB / name).exists():
        shutil.move(str(LB / name), str(ARCH / name))
OUT.mkdir(exist_ok=True)

STYLE = """body{font-family:Georgia,serif;max-width:46em;margin:2em auto;padding:0 1em;line-height:1.5;color:#111;background:#fff}
h1{font-size:1.5em}h2{font-size:1.2em;border-top:2px solid #444;padding-top:.8em;margin-top:2.2em}
.q{font-weight:bold}.op{margin:.4em 0}.st{background:#f1f1f1;border-left:4px solid #555;padding:.6em 1em;margin-top:1em}
pre.instr{white-space:pre-wrap;font-family:inherit;background:#fafafa;border:1px solid #ccc;padding:1em}
@media(prefers-color-scheme:dark){body{background:#161616;color:#eee}.st{background:#262626}pre.instr{background:#1e1e1e;border-color:#555}}"""


def br(t):
    return html.escape(t or "").replace("\r\n", "\n").replace("\n", "<br>")


def write_html(path, title, rows, ids):
    n = len(rows)
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
             f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>{title}</title><style>{STYLE}</style></head><body>",
             f"<h1>{title}</h1>",
             f"<p>{n} items. Record each label in the CSV template, using the item id shown. "
             "Do not use any AI tool. Do not look anything up.</p>",
             f"<h2 id='instr'>Instructions</h2><pre class='instr'>{html.escape(AUTHOR_TXT)}</pre>"]
    for i, (it, iid) in enumerate(zip(rows, ids), 1):
        parts.append(f"<h2 id='item-{iid}'>Item {i} of {n} &nbsp; (item_id: <code>{iid}</code>)</h2>")
        parts.append(f"<p class='q'>Question: {br(it['question'])}</p><p>Members' opinions:</p><ol>")
        for o in it["opinions"]:
            parts.append(f"<li class='op'>{br(o)}</li>")
        parts.append("</ol>")
        parts.append(f"<div class='st'><strong>Statement:</strong><br>{br(it['statement'])}</div>")
    parts.append("</body></html>")
    Path(path).write_text("\n".join(parts), encoding="utf-8", newline="\n")


def write_template(path, ids):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["item_id", "label", "main_disagreement", "comment", "pass_started_utc"])
        for i in ids:
            w.writerow([i, "", "", "", ""])


def opinions_cell(it):
    return "\n".join(f"{i}. {o}" for i, o in enumerate(it["opinions"], 1))


write_html(OUT / "packet_author_pass1.html", "Labelling packet, first set", p1, ids_a1)
write_html(OUT / "packet_author_pass2.html", "Labelling packet, second set", p2, ids_a2)
write_template(OUT / "TEMPLATE_author_pass1.csv", ids_a1)
write_template(OUT / "TEMPLATE_author_pass2.csv", ids_a2)
(OUT / "LABELER_INSTRUCTIONS_author.md").write_text("# Instructions\n\n" + AUTHOR_TXT, encoding="utf-8", newline="\n")

# volunteer: one CSV (Excel-safe: UTF-8 BOM, CRLF, quoted cells) + one instructions file
with open(OUT / "volunteer_packet.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, lineterminator="\r\n", quoting=csv.QUOTE_ALL)
    w.writerow(["item_id", "question", "opinions", "statement", "label", "main_disagreement", "comment",
                "pass_started_utc"])
    for it, iid in zip(pv, ids_v):
        w.writerow([iid, it["question"], opinions_cell(it), it["statement"], "", "", "", ""])
RETURN = """
---

## How to return your work

The file `volunteer_packet.csv` opens in Excel, Google Sheets or LibreOffice. It has one row per item. Fill in
the columns `label`, `main_disagreement`, `comment` and `pass_started_utc` for every row. `label` must be exactly
one of `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`. In `pass_started_utc` write the time you started, in UTC, as
`YYYY-MM-DDTHH:MMZ` (for example `2026-11-17T14:30Z`), the same value on every row.

When you are done:

1. Delete the three columns `question`, `opinions` and `statement` (columns B, C and D). Keep `item_id` unchanged.
   The file must then have exactly these five columns, in this order: `item_id`, `label`, `main_disagreement`,
   `comment`, `pass_started_utc`, and exactly 50 rows below the header.
2. Save it as a CSV file (UTF-8) named exactly `volunteer_pass1.csv` and send that one file back.
"""
(OUT / "VOLUNTEER_INSTRUCTIONS.md").write_text("# Instructions\n\n" + VOL_TXT + RETURN, encoding="utf-8", newline="\n")

# ------------------------------------------------------------------ keys (never shared)
def krow(it, iid, pas, dup_of=""):
    return {"item_id": iid, "pass": pas, "kind": it["kind"], "launch_id": it["launch_id"],
            "round_id": it["round_id"], "cand": it["cand"], "generator": it["generator"], "cell": it["cell"],
            "dup_of": dup_of, "uid": it["uid"]}


id_a1 = {it["uid"]: iid for it, iid in zip(p1, ids_a1)}
key_author = [krow(it, iid, "pass1") for it, iid in zip(p1, ids_a1)] + \
             [krow(it, iid, "pass2", id_a1[it["uid"]]) for it, iid in zip(p2, ids_a2)]
with open(OUT / "key_author.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(key_author[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(key_author)
key_vol = {"WARNING": "NOT for the volunteer. Maps volunteer ids to items.",
           "volunteer_id_to_author_pass1_id": {iid: id_a1[it["uid"]] for it, iid in zip(pv, ids_v)},
           "volunteer_id_to_item": {iid: {"kind": it["kind"], "launch_id": it["launch_id"], "round_id": it["round_id"],
                                          "cand": it["cand"], "generator": it["generator"], "cell": it["cell"]}
                                    for it, iid in zip(pv, ids_v)},
           "seeds": {"sample": SEED_SAMPLE, "pass1_order": SEED_P1, "pass2_order": SEED_P2, "repeat_selection": SEED_REP,
                     "volunteer_order": SEED_VOL, "ids_author_pass1": SEED_ID_A1, "ids_author_pass2": SEED_ID_A2,
                     "ids_volunteer": SEED_ID_V},
           "data_sha256": data_sha, "frozen_rules_sha256": sha256_file(FROZEN),
           "n2_selection_sha256": sha256_file(SEL), "dev_launches_excluded": len(dev)}
(OUT / "key_volunteer.json").write_text(json.dumps(key_vol, indent=1), encoding="utf-8", newline="\n")
print("built", len(p1), len(p2), len(pv))

sys.path.insert(0, str(P / "analysis"))
from run_log import log_run  # noqa: E402
log_run(__file__, "labelpacket_R4", f"{SEED_SAMPLE}/{SEED_P1}/{SEED_P2}/{SEED_REP}/{SEED_VOL}/ids {SEED_ID_A1},{SEED_ID_A2},{SEED_ID_V}",
        [DATA, DEV, SEL, FROZEN], str(OUT / "key_volunteer.json"),
        "R4 packets: 50 items (38 orig + 12 N2), 20 repeats; no labels created; id seeds unspecified in FROZEN")
