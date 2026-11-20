"""V5 step-3 packet verification (decisions.md D49b/D49c).  Re-derives everything it can from the sources, never from
the packet alone.  Reads no score, rank or rating.  Prints ALL CHECKS PASS or the failures, and appends a hash table to
RUNS.md.  Run:  C:/Users/intel/miniconda3/python.exe -I verify.py
"""
import csv
import hashlib
import html
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
V5 = P / "labels_build" / "v5"
DEV = P.parent / "pilots" / "T3_1" / "pilot_groups.jsonl"
GENS = ["qwen3.8-27b", "gemma4-12b", "ministral3-14b", "phi4-14b", "llama3.1-8b"]
CELLS = ["ACC-DIS", "SAT-COMMON", "NEU-COMMON", "ACC-COMMON", "SAT-DIS"]
SHOWN = ["packet_verification.html", "TEMPLATE_author_verification.csv", "INSTRUCTIONS_verification.md"]
fails, infos = [], []


def chk(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("v5_" + name, V5 / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sel_mod = load("select_items")
ext_mod = load("extract")
key = list(csv.DictReader(open(V5 / "key_verification.csv", encoding="utf-8")))
tmpl = list(csv.reader(open(V5 / "TEMPLATE_author_verification.csv", encoding="utf-8")))
page = (V5 / "packet_verification.html").read_text(encoding="utf-8")
instr = (V5 / "INSTRUCTIONS_verification.md").read_text(encoding="utf-8")
ext = json.loads((V5 / "extraction.json").read_text(encoding="utf-8"))
by_slot = {x["slot_index"]: x for x in ext["items"]}

# ---- counts and composition
chk("25 items in key", len(key) == 25)
ids = [k["item_id"] for k in key]
chk("ids v5-01..v5-25 unique", sorted(ids) == [f"v5-{i:02d}" for i in range(1, 26)])
chk("template header", tmpl[0] == ["item_id", "q1_quotes_disagree", "q2_statement_acknowledges", "comment", "pass_started_utc"])
chk("template rows = key ids in order, answers blank", [r[0] for r in tmpl[1:]] == ids and all(r[1:] == ["", "", "", ""] for r in tmpl[1:]))
html_ids = re.findall(r"<h2>Item (v5-\d\d)</h2>", page)
chk("html blocks = key ids in order", html_ids == ids)
chk("19 original / 6 N2", sum(k["kind"] == "original" for k in key) == 19 and sum(k["kind"] == "n2" for k in key) == 6)
n2 = [k for k in key if k["kind"] == "n2"]
chk("each of the 5 generators has >= 1 N2 item (6 total)", all(sum(k["generator"] == g for k in n2) >= 1 for g in GENS),
    str([k["generator"] for k in n2]))
chk("one item per generator slot + 1 extra", sorted(k["slot"] for k in n2) == sorted([f"gen:{g}" for g in GENS] + ["extra"]))
chk("slot generator matches", all(k["slot"] == "extra" or k["slot"] == f"gen:{k['generator']}" for k in n2))
chk("originals carry no generator/cell", all(k["generator"] == "" and k["cell"] == "" for k in key if k["kind"] == "original"))
chk("each item from a distinct round", len({k["round_id"] for k in key}) == 25)
chk("N2 launches distinct", len({k["launch_id"] for k in n2}) == 6)

# ---- no dev launch
dev = {json.loads(l)["launch_id"] for l in open(DEV, encoding="utf-8") if l.strip()}
chk("no development launch included", not any(k["launch_id"] in dev for k in key))
g1 = json.loads((P / "gate1" / "sample.json").read_text(encoding="utf-8"))["sample"]
g1_l = {x["launch_id"] for v in g1.values() for x in v}
chk("N2 items outside the gate-1 launches", not any(k["launch_id"] in g1_l for k in n2))

# ---- statements re-derived from sources; quotes re-checked against the round's opinions
rounds = ext_mod.load_rounds({(k["launch_id"], k["round_id"]) for k in key})
texts = ext_mod.n2_texts()
stmts, bad_q, bad_md, bad_st, bad_html = {}, [], [], [], []
for k in key:
    rnd = rounds[(k["launch_id"], k["round_id"])]
    if k["kind"] == "original":
        st = rnd["cands"][int(k["cand"])]
    else:
        ts = texts[k["statement_id"]]
        st = next(iter(ts)) if len(ts) == 1 else None
        if st is None or sel_mod.has_markdown(st) or sel_mod.has_markdown_strict(st):    # D49b + D49e filters
            bad_md.append(k["item_id"])
        blk_st = page.split(f"<h2>Item {k['item_id']}</h2>", 1)[1].split("</section>", 1)[0]
        shown = html.unescape(blk_st.split("<strong>Statement:</strong><br>", 1)[1].split("</div>", 1)[0].replace("<br>", "\n"))
        if sel_mod.has_markdown_strict(shown):                                          # D49e, on the text as shown
            bad_md.append(k["item_id"] + "(shown)")
    stmts[k["item_id"]] = st
    if by_slot[int(k["slot_index"])]["statement"] != st:
        bad_st.append(k["item_id"])
    ops = rnd["opinions"]
    pa, pb = k["pid_a"], k["pid_b"]
    if not (rnd["human_only"] and pa != pb and pa in ops and pb in ops and k["quote_a"].strip() and k["quote_b"].strip()
            and k["quote_a"] in ops[pa] and k["quote_b"] in ops[pb]):
        bad_q.append(k["item_id"])
    blk = page.split(f"<h2>Item {k['item_id']}</h2>", 1)[1].split("</section>", 1)[0]
    want = [html.escape(rnd["question"]).replace("\r\n", "\n").replace("\n", "<br>"),
            html.escape(k["quote_a"]).replace("\r\n", "\n").replace("\n", "<br>"),
            html.escape(k["quote_b"]).replace("\r\n", "\n").replace("\n", "<br>"),
            html.escape(st or "").replace("\r\n", "\n").replace("\n", "<br>"),
            "Q1. Do these quotes disagree? (yes/no)", "Q2. Does the statement acknowledge this disagreement? (yes/no)"]
    pos = [blk.find(w) for w in want]
    if -1 in pos or pos != sorted(pos):
        bad_html.append(k["item_id"])
chk("no markdown in the shown N2 statements (D49e strict: *x*, **x**, _x_, backtick, #, list lines)", not bad_md, str(bad_md))
strict_tests = {"a *b* c": True, "**b**": True, "a _b_ c": True, "x `y`": True, "# h": True, "- item": True, "1. item": True,
                "snake_case_name": False, "5 * 3 = 15": False, "plain text, no marks.": False}
chk("strict markdown filter self-test", all(sel_mod.has_markdown_strict(t) == v for t, v in strict_tests.items()),
    str({t: sel_mod.has_markdown_strict(t) for t in strict_tests}))
chk("shown statement = source statement (candidate text / generation text)", not bad_st, str(bad_st))
chk("quotes are exact substrings of two DIFFERENT participants' opinions in that round", not bad_q, str(bad_q))
chk("html block shows question, Quote A, Quote B, statement, Q1, Q2 in that order, verbatim", not bad_html, str(bad_html))

# ---- leaks
strict = [re.escape(g) for g in GENS] + [re.escape(c) for c in CELLS] + \
         [r"qwen", r"gemma", r"ministral", r"mistral", r"llama", r"phi-?4", r"gpt-?oss", r"openai", r"\bN2\b",
          r"\b(SAT|ACC|NEU)-(COMMON|DIS)\b", r"r4uid", r"#cand"]
ids_hidden = {v for k in key for v in (k["pid_a"], k["pid_b"], k["launch_id"], k["round_id"], k["statement_id"], k["r4_item_id"]) if v}
ids_hidden |= {p for k in key for p in rounds[(k["launch_id"], k["round_id"])]["opinions"]}
broad = [r"score", r"\brank", r"erasure", r"condition", r"original", r"generator", r"\bmodel\b", r"hypothes", r"hidden",
         r"conflict_found", r"participant[_ ]id", r"\bsource\b", r"\bcell\b"]
content = [html.escape(x).replace("\r\n", "\n").replace("\n", "<br>") for k in key
           for x in (rounds[(k["launch_id"], k["round_id"])]["question"], k["quote_a"], k["quote_b"], stmts[k["item_id"]] or "")]
for name in SHOWN:
    txt = (V5 / name).read_text(encoding="utf-8")
    hits = [pat for pat in strict if re.search(pat, txt, re.I)]
    chk(f"{name}: no generator/model/cell/N2 marker", not hits, str(hits))
    leaked = [i for i in ids_hidden if i in txt]
    chk(f"{name}: no participant/launch/round/statement id", not leaked, str(leaked[:5]))
    scaffold = txt
    for c in sorted(content, key=len, reverse=True):
        scaffold = scaffold.replace(c, "")
    bh = [pat for pat in broad if re.search(pat, scaffold, re.I)]
    chk(f"{name}: scaffold (text outside verbatim content) has no score/rank/condition/source wording", not bh, str(bh))
    ch = [pat for pat in broad if re.search(pat, txt, re.I)] if not bh else []
    if ch:
        infos.append(f"{name}: words {ch} occur only inside verbatim question/quote/statement text (not a leak)")
chk("scores/ranks not in any shown file (no digits pattern like 'E=' or 'rank 1')",
    not any(re.search(r"\bE\s*=\s*\d|\brank(ed)?\s*#?\d", (V5 / n_).read_text(encoding="utf-8"), re.I) for n_ in SHOWN))
chk("instructions: yes/no only, Q2 always, save path", "exactly `yes` or `no`" in instr and "Answer Q2 even when" in instr
    and r"t3_1\labels\author_verification.csv" in instr)
chk("labels\\ still empty (listing only)", not any((P / "labels").iterdir()))
s = ext["summary"]
chk("extraction summary: 25 valid", s["n_valid"] == 25 and s["n_items"] == 25)
chk("selection.json unchanged since extraction", s["selection_sha256"] == sha(V5 / "selection.json"))
chk("X1 hash in extraction = file", s["x1_sha256"] == sha(V5 / "X1_prompt.md"))
for i in infos:
    print("INFO", i)
print("INFO conflict_found=false:", sum(k["conflict_found"] == "False" for k in key), "| replacements:", s["n_replacements"],
      "| located_by=search:", s["located_by_search"])
verdict = "ALL CHECKS PASS" if not fails else "FAILURES: " + "; ".join(fails)
print(verdict)
files = ["packet_verification.html", "TEMPLATE_author_verification.csv", "INSTRUCTIONS_verification.md", "key_verification.csv",
         "selection.json", "extraction.json", "extraction_attempts.jsonl", "container_check.json", "X1_prompt.md",
         "select_items.py", "extract.py", "redraw_d49e.py", "build_packet.py", "verify.py"]
with open(V5 / "RUNS.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(f"\n## {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())} verify.py: {verdict}\n\n| file | sha256 |\n|---|---|\n")
    for fn in files:
        f.write(f"| {fn} | {sha(V5 / fn)} |\n")
