"""Post-gate, results-aware, PARTIAL (12/25) author verification. Calls the frozen evaluate() unchanged.
Not a gate input; does not touch gate1/GATE1_RESULT.json (D65)."""
import csv, json, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P / "analysis"))
from verification_eval import evaluate

ans = {r["item_id"]: (r["q1_quotes_disagree"].strip().upper(), r["q2_statement_acknowledges"].strip().upper())
       for r in csv.DictReader(open(P / "labels" / "author_verification_partial12.csv", encoding="utf-8"))}
sc = {}
for line in open(P / "analysis" / "scores" / "packet_v5_scores.jsonl", encoding="utf-8"):
    r = json.loads(line); sc[r["item_id"]] = r
res = evaluate(ans, {i: sc[i] for i in ans})
res["note"] = "POST-GATE, RESULTS-AWARE, PARTIAL 12 of 25 items; descriptive only; not a gate input"
res["per_item"] = {i: {"q1": ans[i][0], "q2": ans[i][1], "kind": sc[i].get("kind"), "E": sc[i].get("E"),
                       "n_cruxes": sc[i].get("n_cruxes"), "ok": sc[i].get("ok")} for i in sorted(ans)}
out = P / "analysis" / "results" / "VERIFICATION_PARTIAL12.json"
out.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: res[k] for k in ("n_items", "V_ev", "presence_table", "n_q1_yes", "n_not_ack", "n_ack",
                  "table_A_by_S", "fisher_p_one_sided_conditional", "BA3", "kappa", "usable",
                  "n_missing_E_on_q1_yes_counted_wrong")}, indent=1, default=str))
print(json.dumps(res["per_item"], indent=0))
