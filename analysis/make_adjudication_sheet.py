"""make_adjudication_sheet.py [R4] two-human design only (FR s5 Adjudication, s6.3).
python -I make_adjudication_sheet.py [--root P] [--labels-dir D] [--build-dir D] [--out-dir D]

Lists the items where the author's pass-1 label and the volunteer's label differ (four-token labels, case/space ignored).
Each row shows ONLY: item_id (the author's pass-1 id, = ADJ.csv item_id), question, numbered opinions, statement, and the two
labels as "label_1" / "label_2" (which annotator is which is shuffled per item with a seeded RNG and kept only in
ADJ_SHEET_KEY.json, which the adjudicators do not open).  No score, ranking, model, condition, crux list, comment or
main_disagreement text is shown.
Writes into <build-dir> (default labels_build\\r4): ADJ_SHEET.csv, ADJ_SHEET.html, ADJ_TEMPLATE.csv (item_id,adj_label,reason
blank), ADJ_SHEET_KEY.json.  The humans fill the template and save it as P\\labels\\ADJ.csv.  This script NEVER writes labels\\.
Text source: volunteer_packet.csv (same question/opinions/statement text as the author packet) + key_volunteer.json for the id map.
Exit 1 if either label file is missing/incomplete/invalid (nothing is guessed)."""
import argparse, csv, hashlib, html, json, random, sys
from pathlib import Path

TOK = {"HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE"}
DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def read_labels(p, n=50):
    with open(p, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out, bad = {}, []
    for r in rows:
        i = (r.get("item_id") or "").strip()
        l = (r.get("label") or "").strip().upper()
        if not i or l not in TOK or i in out:
            bad.append(i or "<blank id>")
        out[i] = l
    if bad or len(rows) != n:
        raise SystemExit(f"INCOMPLETE {p.name}: {len(rows)} rows (need {n}); bad/blank/repeated: {bad[:10]}")
    return out


def build(root, labels_dir=None, build_dir=None, out_dir=None, n=50):
    root = Path(root)
    ld = Path(labels_dir) if labels_dir else root / "labels"
    bd = Path(build_dir) if build_dir else root / "labels_build" / "r4"
    od = Path(out_dir) if out_dir else bd
    if od.resolve() == ld.resolve() or ld.resolve() in od.resolve().parents:
        raise SystemExit("refusing to write inside the labels directory")
    auth = read_labels(ld / "author_pass1.csv", n)
    vol = read_labels(ld / "volunteer_pass1.csv", n)
    key = json.loads((bd / "key_volunteer.json").read_text(encoding="utf-8"))["volunteer_id_to_author_pass1_id"]
    with open(bd / "volunteer_packet.csv", encoding="utf-8-sig", newline="") as f:
        text = {r["item_id"]: r for r in csv.DictReader(f)}
    if set(vol) != set(key) or set(auth) != set(key.values()):
        raise SystemExit("item ids in the label files do not match the key")
    rows, keyout = [], {}
    for vid, aid in sorted(key.items(), key=lambda kv: kv[1]):
        if auth[aid] == vol[vid]:
            continue
        t = text[vid]
        flip = random.Random(int(hashlib.sha256(("adj20261140" + aid).encode()).hexdigest()[:12], 16)).random() < 0.5
        pair = [("volunteer", vol[vid]), ("author", auth[aid])] if flip else [("author", auth[aid]), ("volunteer", vol[vid])]
        rows.append({"item_id": aid, "question": t["question"], "opinions": t["opinions"], "statement": t["statement"],
                     "label_1": pair[0][1], "label_2": pair[1][1]})
        keyout[aid] = {"label_1": pair[0][0], "label_2": pair[1][0]}
    od.mkdir(parents=True, exist_ok=True)
    cols = ["item_id", "question", "opinions", "statement", "label_1", "label_2"]
    with open(od / "ADJ_SHEET.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
    with open(od / "ADJ_TEMPLATE.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["item_id", "adj_label", "reason"])
        for r in rows:
            w.writerow([r["item_id"], "", ""])
    (od / "ADJ_SHEET_KEY.json").write_text(json.dumps(
        {"WARNING": "NOT for the adjudicators: which annotator is label_1/label_2", "key": keyout}, indent=1), encoding="utf-8")
    h = ["<!doctype html><meta charset='utf-8'><title>Adjudication sheet</title>",
         "<style>body{font:15px/1.45 sans-serif;max-width:900px;margin:1em auto}section{border:1px solid #888;margin:1.5em 0;padding:1em}"
         "pre{white-space:pre-wrap;font:inherit}.l{background:#eee;padding:2px 8px;margin-right:8px}</style>",
         f"<h1>Adjudication: {len(rows)} item(s)</h1><p>Decide together, using only what is on this page. Write one of HIDES, SHOWS, "
         "NO_DISAGREEMENT, UNSURE and a short reason in ADJ_TEMPLATE.csv, and save it as <code>labels\\ADJ.csv</code>.</p>"]
    for r in rows:
        h.append(f"<section><h2>{html.escape(r['item_id'])}</h2><p><b>Question:</b> {html.escape(r['question'])}</p>"
                 f"<p><b>Opinions</b></p><pre>{html.escape(r['opinions'])}</pre><p><b>Statement</b></p><pre>{html.escape(r['statement'])}</pre>"
                 f"<p><span class='l'>Label 1: {r['label_1']}</span><span class='l'>Label 2: {r['label_2']}</span></p></section>")
    (od / "ADJ_SHEET.html").write_text("\n".join(h), encoding="utf-8")
    return len(rows), od


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--labels-dir"); ap.add_argument("--build-dir"); ap.add_argument("--out-dir")
    a = ap.parse_args()
    k, od = build(a.root, a.labels_dir, a.build_dir, a.out_dir)
    print(f"{k} item(s) to adjudicate; wrote ADJ_SHEET.csv/.html, ADJ_TEMPLATE.csv, ADJ_SHEET_KEY.json in {od}")
