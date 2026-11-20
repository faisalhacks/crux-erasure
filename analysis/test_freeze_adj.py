"""Tests for freeze.py and make_adjudication_sheet.py on dummy data in a temp dir only.  python -I test_freeze_adj.py"""
import csv, json, os, subprocess, sys, tempfile, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import freeze, make_adjudication_sheet as M

ok = 0
def chk(c, m):
    global ok
    if not c:
        print("FAIL:", m); sys.exit(1)
    ok += 1

t = Path(tempfile.mkdtemp(prefix="DUMMY_freeze_"))
(t / "analysis").mkdir(); (t / "labels").mkdir()
for rel, s in [("FROZEN_RULES.md", "rules"), ("EXPERIMENTS.md", "exp"), ("analysis/scorer_manifest.json", "{}"),
               ("analysis/N2_ANALYSIS_SPEC.md", "n2")]:
    (t / rel).write_text(s, encoding="utf-8")
c, m = freeze.run(t); chk(c == 1 and not (t / "FREEZE.json").exists(), "empty labels -> nothing frozen")
chk(not freeze.is_readonly(t / "FROZEN_RULES.md"), "not read-only before")
(t / "labels" / "volunteer_pass1.csv").write_text("a", encoding="utf-8"); time.sleep(0.05)
(t / "labels" / "author_pass1.csv").write_text("b", encoding="utf-8")
c, m = freeze.run(t); chk(c == 0, m)
rec = json.loads((t / "FREEZE.json").read_text(encoding="utf-8"))
chk(rec["first_label_file"] == "volunteer_pass1.csv", "first arrival")
chk(set(rec["label_files"]) == {"volunteer_pass1.csv", "author_pass1.csv"} and len(rec["files"]) == 4, "hashes recorded")
chk(freeze.is_readonly(t / "FROZEN_RULES.md"), "FROZEN_RULES read-only")
before = (t / "FREEZE.json").read_bytes()
(t / "labels" / "author_pass2.csv").write_text("c", encoding="utf-8")
c, m = freeze.run(t); chk(c == 0 and "already" in m and (t / "FREEZE.json").read_bytes() == before, "idempotent, no overwrite")
os.chmod(t / "FROZEN_RULES.md", 0o666); (t / "FROZEN_RULES.md").write_text("changed", encoding="utf-8")
c, m = freeze.run(t); chk(c == 2 and (t / "FREEZE.json").read_bytes() == before and freeze.is_readonly(t / "FROZEN_RULES.md"),
                          "changed rules reported, re-locked, FREEZE untouched")
p = subprocess.run([sys.executable, "-I", str(HERE / "freeze.py"), "--root", str(t)], capture_output=True, text=True)
chk(p.returncode == 2, "cli exit code")
os.chmod(t / "FROZEN_RULES.md", 0o666)

# adjudication sheet
b = Path(tempfile.mkdtemp(prefix="DUMMY_adj_")); (b / "labels").mkdir(); (b / "r4").mkdir()
toks = ["HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE"]
key, pk, al, vl = {}, [], [], []
for i in range(50):
    a, v = f"a{i:03d}", f"v{i:03d}"; key[v] = a
    pk.append({"item_id": v, "question": f"Q{i}", "opinions": f"1. op<b>{i}", "statement": f"S{i}", "label": "", "main_disagreement": "",
               "comment": "", "pass_started_utc": ""})
    la = toks[i % 4]; lv = la if i % 5 else toks[(i + 1) % 4]
    al.append([a, la.lower() + " ", "SECRET_MD", "SECRET_COMMENT", "2026-11-16T10:00Z"]); vl.append([v, lv, "x", "y", "2026-11-16T11:00Z"])
exp = {f"a{i:03d}" for i in range(50) if i % 5 == 0 and toks[i % 4] != toks[(i + 1) % 4]}
def wl(p, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["item_id", "label", "main_disagreement", "comment", "pass_started_utc"]); w.writerows(rows)
wl(b / "labels" / "author_pass1.csv", al); wl(b / "labels" / "volunteer_pass1.csv", vl)
with open(b / "r4" / "volunteer_packet.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, list(pk[0])); w.writeheader(); w.writerows(pk)
(b / "r4" / "key_volunteer.json").write_text(json.dumps({"volunteer_id_to_author_pass1_id": key}), encoding="utf-8")
k, od = M.build(b, b / "labels", b / "r4", b / "r4")
chk(k == len(exp), f"disagreement count {k} vs {len(exp)}")
rows = list(csv.DictReader(open(od / "ADJ_SHEET.csv", encoding="utf-8-sig")))
chk({r["item_id"] for r in rows} == exp, "right items")
chk(list(rows[0]) == ["item_id", "question", "opinions", "statement", "label_1", "label_2"], "only allowed columns")
blob = (od / "ADJ_SHEET.csv").read_text(encoding="utf-8-sig") + (od / "ADJ_SHEET.html").read_text(encoding="utf-8")
chk("SECRET" not in blob and "author" not in blob.lower().replace("adjudicat", "") and "volunteer" not in blob.lower(), "no leakage")
chk("&lt;b&gt;" in (od / "ADJ_SHEET.html").read_text(encoding="utf-8"), "html escaped")
tp = list(csv.reader(open(od / "ADJ_TEMPLATE.csv", encoding="utf-8")))
chk(tp[0] == ["item_id", "adj_label", "reason"] and len(tp) == k + 1 and all(r[1] == "" for r in tp[1:]), "blank template")
kj = json.loads((od / "ADJ_SHEET_KEY.json").read_text(encoding="utf-8"))["key"]
chk(all(kj[r["item_id"]]["label_1"] in ("author", "volunteer") for r in rows), "key present")
labs = {r["item_id"]: (r["label_1"], r["label_2"]) for r in rows}
chk(len({kj[i]["label_1"] for i in labs}) == 2, "order shuffled across items")
try:
    M.build(b, b / "labels", b / "r4", b / "labels"); chk(False, "should refuse labels dir")
except SystemExit as e:
    chk("labels" in str(e), "refuses to write in labels dir")
chk(not (b / "labels" / "ADJ.csv").exists(), "ADJ.csv never written")
wl(b / "labels" / "volunteer_pass1.csv", vl[:49])
try:
    M.build(b, b / "labels", b / "r4", b / "r4"); chk(False, "should reject short file")
except SystemExit as e:
    chk("INCOMPLETE" in str(e), "incomplete rejected")
print(f"ALL PASS ({ok} checks)")
