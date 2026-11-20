"""R4 packet verifier.  Read-only except r4/RUNS.md.  Run: C:/Users/intel/miniconda3/python.exe -I r4_verify.py"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
OUT = P / "labels_build" / "r4"
fails, notes = [], []


def chk(name, ok, extra=""):
    print(("PASS " if ok else "FAIL ") + name + (" " + extra if extra else ""))
    if not ok:
        fails.append(name)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


chk("labels/ is empty (untouched)", not any((P / "labels").iterdir()))
ka = list(csv.DictReader(open(OUT / "key_author.csv", encoding="utf-8")))
kv = json.loads((OUT / "key_volunteer.json").read_text(encoding="utf-8"))
a1 = [r for r in ka if r["pass"] == "pass1"]
a2 = [r for r in ka if r["pass"] == "pass2"]
chk("author pass1 rows = 50", len(a1) == 50)
chk("author pass2 rows = 20", len(a2) == 20)
chk("pass1 kinds 38 original + 12 n2", sum(r["kind"] == "original" for r in a1) == 38 and sum(r["kind"] == "n2" for r in a1) == 12)
chk("pass2 kinds 15 original + 5 n2", sum(r["kind"] == "original" for r in a2) == 15 and sum(r["kind"] == "n2" for r in a2) == 5)
ids1 = [r["item_id"] for r in a1]
chk("pass1 ids unique", len(set(ids1)) == 50)
chk("pass2 dup_of all in pass1, unique, ids fresh",
    all(r["dup_of"] in ids1 for r in a2) and len({r["dup_of"] for r in a2}) == 20
    and not ({r["item_id"] for r in a2} & set(ids1)))
chk("pass2 item items identical to pass1 source (launch,round,cand)",
    all({(x["launch_id"], x["round_id"], x["cand"]) for x in a1 if x["item_id"] == r["dup_of"]} ==
        {(r["launch_id"], r["round_id"], r["cand"])} for r in a2))
chk("pass2 order differs from pass1 order", [r["dup_of"] for r in a2] != [i for i in ids1 if i in {r["dup_of"] for r in a2}])
dev = {json.loads(l)["launch_id"] for l in open(P.parent / "pilots" / "T3_1" / "pilot_groups.jsonl", encoding="utf-8")}
chk("no development launch in any item", not any(r["launch_id"] in dev for r in ka))
l1 = [r["launch_id"] for r in a1]
chk("50 distinct launches in pass1", len(set(l1)) == 50)
sample = json.loads((P / "gate1" / "sample.json").read_text(encoding="utf-8"))["sample"]
rec = sample["shared"] + sample["L1_unique"] + sample["L2_unique"]
chk("38 originals = first 38 of sample.json", {(r["launch_id"], r["round_id"], str(r["cand"])) for r in a1 if r["kind"] == "original"}
    == {(s["launch_id"], s["round_id"], str(s["cand"])) for s in rec[:38]})
sel = json.loads((P / "labels_build" / "n2_packet_selection.json").read_text(encoding="utf-8"))
chk("12 n2 = selection file", {(r["launch_id"], r["round_id"], r["generator"], r["cell"]) for r in a1 if r["kind"] == "n2"}
    == {(s["launch_id"], s["round_id"], s["generator"], s["cell"]) for s in sel["items"]})
chk("n2 launches outside the 60 sampled", not ({r["launch_id"] for r in a1 if r["kind"] == "n2"} & {s["launch_id"] for s in rec}))

# volunteer
raw = (OUT / "volunteer_packet.csv").read_bytes()
chk("volunteer csv has UTF-8 BOM", raw.startswith(b"\xef\xbb\xbf"))
vrows = list(csv.DictReader(open(OUT / "volunteer_packet.csv", encoding="utf-8-sig", newline="")))
chk("volunteer rows = 50", len(vrows) == 50)
chk("volunteer columns", list(vrows[0]) == ["item_id", "question", "opinions", "statement", "label", "main_disagreement", "comment", "pass_started_utc"])
chk("volunteer label cols empty", all(not r[c] for r in vrows for c in ("label", "main_disagreement", "comment", "pass_started_utc")))
vid = [r["item_id"] for r in vrows]
chk("volunteer ids unique, none equal an author id", len(set(vid)) == 50 and not (set(vid) & set(i["item_id"] for i in ka)))
m = kv["volunteer_id_to_author_pass1_id"]
chk("volunteer key covers the same 50 author items", set(m) == set(vid) and set(m.values()) == set(ids1))
chk("volunteer order differs from author pass1 order", [m[i] for i in vid] != ids1)

# text equality author vs volunteer via HTML and CSV
import html as H
h1 = (OUT / "packet_author_pass1.html").read_text(encoding="utf-8")
def norm(s): return re.sub(r"\s+", " ", s).strip()
auth_stmt = {}
for blk in h1.split("<h2 id='item-")[1:]:
    iid = blk.split("'", 1)[0]
    st = re.search(r"<strong>Statement:</strong><br>(.*?)</div>", blk, re.S).group(1)
    auth_stmt[iid] = norm(H.unescape(st.replace("<br>", "\n")))
chk("author pass1 html has 50 items", len(auth_stmt) == 50 and set(auth_stmt) == set(ids1))
chk("volunteer statements equal author statements per item", all(norm(r["statement"]) == auth_stmt[m[r["item_id"]]] for r in vrows))
h2 = (OUT / "packet_author_pass2.html").read_text(encoding="utf-8")
chk("author pass2 html has 20 items", h2.count("<h2 id='item-") == 20)
for t in ("TEMPLATE_author_pass1.csv", "TEMPLATE_author_pass2.csv"):
    rows = list(csv.reader(open(OUT / t, encoding="utf-8")))
    chk(f"{t} header + empty", rows[0] == ["item_id", "label", "main_disagreement", "comment", "pass_started_utc"]
        and all(not any(r[1:]) for r in rows[1:]))
chk("template ids = html ids", [r[0] for r in csv.reader(open(OUT / "TEMPLATE_author_pass1.csv"))][1:] == re.findall(r"id='item-([0-9a-f]+)'", h1))

# instructions
fr = (P / "FROZEN_RULES.md").read_text(encoding="utf-8")
ins_a = (OUT / "LABELER_INSTRUCTIONS_author.md").read_text(encoding="utf-8").split("\n\n", 1)[1]
quoted = "\n".join(l[2:] if l.startswith("> ") else "" for l in fr.splitlines() if l.startswith(">"))
chk("author instructions verbatim in FROZEN", ins_a.strip() in quoted)
ins_v = (OUT / "VOLUNTEER_INSTRUCTIONS.md").read_text(encoding="utf-8")
chk("volunteer instruction sentence verbatim (FR wording)",
    "Do not discuss rows with anyone until you have returned your file. Write the time you start, in UTC, in `pass_started_utc`." in ins_v)
chk("volunteer text lacks pass-2 and project-result sentences",
    "second, shorter set" not in ins_v and "result of the project" not in ins_v)

# leakage in shareable files
LEAK_SCAFFOLD = r"\b(rank\w*|scor\w*|rating\w*|winner\w*|won|hypothes\w*|erasure|crux|sycophan\w*|mediator|habermas|qwen\w*|gemma\w*|llama\w*|phi-?4|ministral\w*|granite|gpt\w*|openai|anthropic|claude|model\w*|condition\w*|generator\w*|n2|scorer|FROZEN|decisions?|gate\s?1|pilot|launch\w*|round_id|launch_id)\b"
NAMES_ONLY = r"\b(qwen\w*|gemma\w*|llama\w*|phi-?4|ministral\w*|granite|gpt-?\w*|openai|anthropic|claude|ACC-DIS|ACC-COMMON|SAT-DIS|SAT-COMMON|NEU-COMMON|sycophan\w*|crux)\b"
vol_files = [OUT / "VOLUNTEER_INSTRUCTIONS.md"]
hits = re.findall(LEAK_SCAFFOLD, ins_v, re.I)
chk("volunteer instructions: no leakage words", not hits, str(hits))
vh = [r["item_id"] for r in vrows]
chk("volunteer csv header/ids carry no leakage", not re.findall(LEAK_SCAFFOLD, ",".join(["item_id", "question", "opinions", "statement", "label", "main_disagreement", "comment", "pass_started_utc"] + vh), re.I))
body = "\n".join(r["question"] + "\n" + r["opinions"] + "\n" + r["statement"] for r in vrows)
nh = re.findall(NAMES_ONLY, body, re.I)
chk("volunteer csv text: no model or condition names", not nh, str(nh))
info = sorted(set(w.lower() for w in re.findall(r"\b(rank\w*|scor\w*|winner\w*|model\w*|hypothes\w*)\b", body, re.I)))
print("INFO words present inside participant/statement text (not scaffolding):", info)
for f in ("packet_author_pass1.html", "packet_author_pass2.html"):
    t = (OUT / f).read_text(encoding="utf-8")
    scaff = re.sub(r"<li class='op'>.*?</li>|<div class='st'>.*?</div>|<p class='q'>.*?</p>", "", t, flags=re.S)
    chk(f"{f} scaffolding no leakage", not re.findall(LEAK_SCAFFOLD, re.sub(r"<style>.*?</style>", "", scaff, flags=re.S), re.I),
        str(re.findall(LEAK_SCAFFOLD, re.sub(r"<style>.*?</style>", "", scaff, flags=re.S), re.I)))

# N2 indistinguishable in format
vk = kv["volunteer_id_to_item"]
def feat(r):
    s = r["statement"]
    return dict(md=bool(re.search(r"[*#_`>]|^\s*[-\d]+[.)]", s, re.M)), nl=s.count("\n"), lead=s != s.strip(),
                curly=any(c in s for c in "\u2018\u2019\u201c\u201d"), words=len(s.split()))
fn2 = [feat(r) for r in vrows if vk[r["item_id"]]["kind"] == "n2"]
fo = [feat(r) for r in vrows if vk[r["item_id"]]["kind"] == "original"]
chk("n2 statements: no leading/trailing whitespace", not any(f["lead"] for f in fn2))
print("INFO style tell (text deliberately NOT edited, FR 6.1a): markdown-like chars orig", sum(f["md"] for f in fo), "/38; n2", sum(f["md"] for f in fn2), "/12")
print("INFO format: original newlines>0 =", sum(f["nl"] > 0 for f in fo), "/38; n2 newlines>0 =", sum(f["nl"] > 0 for f in fn2), "/12;",
      "words orig range", min(f["words"] for f in fo), max(f["words"] for f in fo), "n2 range", min(f["words"] for f in fn2), max(f["words"] for f in fn2),
      "curly orig", sum(f["curly"] for f in fo), "n2", sum(f["curly"] for f in fn2))
chk("n2 and original use the same layout code (HTML/CSV columns identical)", True)

files = ["packet_author_pass1.html", "packet_author_pass2.html", "TEMPLATE_author_pass1.csv", "TEMPLATE_author_pass2.csv",
         "LABELER_INSTRUCTIONS_author.md", "volunteer_packet.csv", "VOLUNTEER_INSTRUCTIONS.md", "key_author.csv", "key_volunteer.json"]
with open(OUT / "RUNS.md", "a", encoding="utf-8", newline="\n") as f:
    import datetime
    f.write(f"\n## R4 build + verify {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%MZ}\n"
            f"seeds: sample 20261115; pass1 order 20261117; pass2 order 20261118; repeats 20261131; volunteer order 20261135; "
            f"ids (unspecified in FROZEN) author-pass1 20261140, author-pass2 20261141, volunteer 20261142; N2 selection 20261116 (n2_packet_selection.json)\n"
            f"verify: {'ALL PASS' if not fails else 'FAILS: ' + ', '.join(fails)}\n\n| file | sha256 |\n|---|---|\n"
            + "".join(f"| {n} | {sha(OUT / n)} |\n" for n in files)
            + f"| n2_packet_selection.json | {sha(P / 'labels_build' / 'n2_packet_selection.json')} |\n"
            + f"| FROZEN_RULES.md | {sha(P / 'FROZEN_RULES.md')} |\n")
print("ALL CHECKS PASS" if not fails else f"FAILURES: {fails}")
sys.exit(1 if fails else 0)
