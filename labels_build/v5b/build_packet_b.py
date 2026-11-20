"""V5b (part 2, decisions.md D62) blind verification packet: build_packet.py with v5b paths, ids v5b-26..50, order seed "20261116:v5b-order", save name author_verification_b.csv (D49b).  Reads extraction_b.json (written by extract_b.py); no model call.
Writes packet_verification_b.html, TEMPLATE_author_verification_b.csv, INSTRUCTIONS_verification_b.md (shown) and
key_verification_b.csv (NEVER shown).  Order: the 25 items in slot order, shuffled with random.Random("20261116:v5b-order");
ids v5b-26..v5b-50 follow that order.  Never writes P/labels/.  Creates no label.
Run:  C:/Users/intel/miniconda3/python.exe -I build_packet_b.py
"""
import csv
import html
import json
import random
from pathlib import Path

V5 = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\v5b")
SAVE_TO = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels\author_verification_b.csv"
ORDER_SEED = "20261116:v5b-order"
Q1 = "Q1. Do these quotes disagree? (yes/no)"
Q2 = "Q2. Does the statement acknowledge this disagreement? (yes/no)"
TEMPLATE_COLS = ["item_id", "q1_quotes_disagree", "q2_statement_acknowledges", "comment", "pass_started_utc"]

STYLE = """:root{--bg:#fff;--fg:#111;--box:#f1f1f1;--line:#555;--q:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--box:#262626;--line:#888;--q:#1e1e1e}}
body{font-family:Georgia,serif;max-width:46em;margin:2em auto;padding:0 16px;line-height:1.5;color:var(--fg);background:var(--bg)}
h1{font-size:1.5em}h2{font-size:1.2em;border-top:2px solid var(--line);padding-top:.8em;margin-top:2.2em}
.qn{font-weight:bold}.quote{background:var(--q);border-left:4px solid var(--line);padding:.5em 1em;margin:.6em 0}
.st{background:var(--box);border-left:4px solid var(--line);padding:.6em 1em;margin-top:1em}
.ask{margin-top:1em}.ask p{margin:.2em 0}"""


def br(t):
    return html.escape(t or "").replace("\r\n", "\n").replace("\n", "<br>")


def main():
    ext = json.loads((V5 / "extraction_b.json").read_text(encoding="utf-8"))
    items = sorted(ext["items"], key=lambda x: x["slot_index"])
    assert len(items) == 25 and all(x["result"] for x in items), "extraction incomplete"
    order = list(items)
    random.Random(ORDER_SEED).shuffle(order)
    ids = [f"v5b-{i:02d}" for i in range(26, 26 + len(order))]
    n = len(order)

    parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             f"<title>Verification packet, part 2</title><style>{STYLE}</style></head><body>",
             "<h1>Verification packet, part 2</h1>",
             f"<p>{n} items. For each item, answer Q1 and Q2 with yes or no in the CSV template, using the item id shown. "
             "Answer Q2 even when your answer to Q1 is no. See the instructions file.</p>"]
    for it, iid in zip(order, ids):
        r = it["result"]
        parts.append(f"<section id='{iid}'><h2>Item {iid}</h2>")
        parts.append(f"<p class='qn'>Question: {br(it['question'])}</p>")
        parts.append(f"<p><strong>Quote A:</strong></p><div class='quote'>{br(r['quote_a'])}</div>")
        parts.append(f"<p><strong>Quote B:</strong></p><div class='quote'>{br(r['quote_b'])}</div>")
        parts.append(f"<div class='st'><strong>Statement:</strong><br>{br(it['statement'])}</div>")
        parts.append(f"<div class='ask'><p>{html.escape(Q1)}</p><p>{html.escape(Q2)}</p></div></section>")
    parts.append("</body></html>")
    (V5 / "packet_verification_b.html").write_text("\n".join(parts), encoding="utf-8", newline="\n")

    with open(V5 / "TEMPLATE_author_verification_b.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(TEMPLATE_COLS)
        for iid in ids:
            w.writerow([iid, "", "", "", ""])

    instr = f"""# Instructions

The packet `packet_verification_b.html` has {n} items. Each item shows a question that a small group discussed, two
quotes (Quote A and Quote B) taken from the written opinions of two different group members, and a statement
written for the group.

For each item, answer two questions:

- {Q1}
- {Q2}

Answer both questions for every item. Answer Q2 even when your answer to Q1 is no.

How to record your answers:

1. Open `TEMPLATE_author_verification_b.csv`. It has one row per item, with the item id shown in the packet.
2. In `q1_quotes_disagree` and `q2_statement_acknowledges`, write exactly `yes` or `no`. No other values.
3. `comment` is optional.
4. In `pass_started_utc`, write the time you started, in UTC, as `YYYY-MM-DDTHH:MMZ`, the same value on every row.
5. Keep `item_id` unchanged and do not add or remove rows or columns.
6. Save the file as `{SAVE_TO}`

Work from the packet only. Do not use any AI tool and do not look anything up.
"""
    (V5 / "INSTRUCTIONS_verification_b.md").write_text(instr, encoding="utf-8", newline="\n")

    cols = ["item_id", "slot_index", "slot", "source", "kind", "r4_uid", "r4_item_id", "statement_id", "launch_id",
            "round_id", "cand", "generator", "cell", "pid_a", "opinion_no_a", "quote_a", "pid_b", "opinion_no_b", "quote_b",
            "conflict_found", "located_by", "extraction_attempt_seed", "extraction_attempts"]
    with open(V5 / "key_verification_b.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for it, iid in zip(order, ids):
            r = it["result"]
            sid = it["job_id"] if it["kind"] == "n2" else f"{it['round_id']}#cand{it['cand']}"
            w.writerow(dict(item_id=iid, slot_index=it["slot_index"], slot=it["slot"], source=it["source"], kind=it["kind"],
                            r4_uid="" if it["uid"] is None else it["uid"], r4_item_id=it["r4_item_id"], statement_id=sid,
                            launch_id=it["launch_id"], round_id=it["round_id"], cand=it["cand"], generator=it["generator"],
                            cell=it["cell"], pid_a=r["pid_a"], opinion_no_a=r["opinion_no_a"], quote_a=r["quote_a"],
                            pid_b=r["pid_b"], opinion_no_b=r["opinion_no_b"], quote_b=r["quote_b"],
                            conflict_found=r["conflict_found"], located_by=r["located_by"],
                            extraction_attempt_seed=r["attempt_seed"], extraction_attempts=len(it["history"])))
    print("built", n, "items; order seed", ORDER_SEED)


if __name__ == "__main__":
    main()
