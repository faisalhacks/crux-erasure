import csv, json, re
from pathlib import Path
B = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build")
key = json.loads((B / "key.json").read_text(encoding="utf-8"))
items = key["items"]
for lab in ("L1", "L2"):
    rows = [i for i in items if i["labeler"] == lab]
    t = list(csv.reader(open(B / f"TEMPLATE_{lab}.csv", encoding="utf-8")))
    assert t[0] == ["item_id", "label", "main_disagreement", "comment"]
    assert len(t) == 45 and all(r[1:] == ["", "", ""] for r in t[1:]), "template not empty"
    ids = [r[0] for r in t[1:]]
    assert ids == [i["item_id"] for i in rows] and len(set(ids)) == 44
    roles = {}
    for i in rows:
        roles[i["role"]] = roles.get(i["role"], 0) + 1
    print(lab, roles)
    pos = {i["item_id"]: i["row"] for i in rows}
    for i in rows:
        if i["role"] == "duplicate":
            gap = i["row"] - pos[i["dup_of"]]
            assert gap >= 10, gap
            print("  dup gap", gap, end="")
    print()
    launches = {i["launch_id"] for i in rows if i["role"] != "duplicate"}
    assert len(launches) == 40
    h = (B / f"packet_{lab}.html").read_text(encoding="utf-8")
    assert h.count("<h2 id='item-") == 44
    # leakage: scaffold = html with item bodies removed
    scaf = re.sub(r"<h2 id='item-.*?(?=<h2 id='item-|</body>)", "", h, flags=re.S)
    scaf += "".join((B / f"LABELER_INSTRUCTIONS_{lab}.md").read_text(encoding="utf-8"))
    for w in ("rank", "score", "winner", "erasure", "sycophan", "hypothes", "launch", "round_id", "provenance",
              "duplicate", "candidate", "cohort"):
        assert w.lower() not in scaf.lower(), (lab, w)
    print(" scaffold clean; whole-packet word hits (text of opinions/statements, not fields):",
          {w: len(re.findall(w, h, flags=re.I)) for w in ("rank", "score", "winner")})
    for it in rows:
        assert it["launch_id"] not in h and it["round_id"] not in h and it["cand_id"] not in h
a = {i["item_id"] for i in items if i["labeler"] == "L1" and i["role"] == "shared"}
b = {i["item_id"] for i in items if i["labeler"] == "L2" and i["role"] == "shared"}
assert a == b and len(a) == 20
l1 = {i["launch_id"] for i in items if i["labeler"] == "L1" and i["role"] != "duplicate"}
l2 = {i["launch_id"] for i in items if i["labeler"] == "L2" and i["role"] != "duplicate"}
assert len(l1 & l2) == 20 and len(l1 | l2) == 60
assert not (set(i["item_id"] for i in items if i["role"] == "duplicate") & (a | b))
print("ALL CHECKS PASS")
