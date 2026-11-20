"""Panel-majority vs scorer on the 25 R5 packet items. EXPLORATORY; LLM-vs-LLM; not human (decisions.md D60).

FR 6.R5.4 lists "panel-majority A vs scorer S on items with majority Q1 = YES" as reported (no rule). It was not
pre-specified to run without an author file; D60 orders it run and reported as EXPLORATORY "LLM-vs-LLM; not human".

Definitions (FR 6.R5.2 per-item quantities, with the panel majority in place of the author):
  A_i = 1 if panel-majority q2_statement_acknowledges == "no" (statement does NOT acknowledge the quoted disagreement)
  S_i = 1 if scorer-1 E >= 0.5; 0 if E < 0.5 or 0 cruxes (E null with ok = true)
  Item set: panel-majority q1_quotes_disagree == "yes". Items whose scorer output failed (ok = false) are
  excluded from agreement/kappa and counted (FR 6.R5.2 would count them as wrong calls; that variant is also printed).
Agreement = share with A == S; Cohen's kappa with an item percentile bootstrap, B = 10,000,
numpy.random.default_rng(20261145) (the FR 6.R5.4 panel seed); undefined (one-class) resamples counted.

Usage: C:/Users/intel/miniconda3/python.exe -I analysis/panel_vs_scorer.py
Output: analysis/panel/panel_vs_scorer.json (+ .sha256); one RUNS.md row via run_log.log_run.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_log  # noqa: E402

PANEL = HERE / "panel" / "panel_p1_summary.json"
SCORES = HERE / "scores" / "packet_v5_scores.jsonl"
OUT = HERE / "panel" / "panel_vs_scorer.json"
SEED, B = 20261145, 10000


def kappa(a, s):
    a, s = np.asarray(a, float), np.asarray(s, float)
    po = np.mean(a == s)
    pa, ps = a.mean(), s.mean()
    pe = pa * ps + (1 - pa) * (1 - ps)
    return None if pe == 1 else (po - pe) / (1 - pe)


def main():
    panel = json.loads(PANEL.read_text(encoding="utf-8"))
    q1 = panel["majority"]["q1_quotes_disagree"]["by_item"]
    q2 = panel["majority"]["q2_statement_acknowledges"]["by_item"]
    sc = {}
    for line in SCORES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            sc[r["item_id"]] = r
    rows, excluded = [], []
    for item in sorted(q1):
        if q1[item] != "yes":
            continue
        r = sc[item]
        if not r["ok"]:
            excluded.append({"item_id": item, "kind": r["kind"], "reason": "scorer output failed (ok = false)"})
            continue
        E = r["E"]
        S = 1 if (E is not None and E >= 0.5) else 0
        A = 1 if q2[item] == "no" else 0
        rows.append({"item_id": item, "kind": r["kind"], "E": E, "n_cruxes": r["n_cruxes"], "S": S, "A": A,
                     "panel_q2": q2[item]})
    a = np.array([x["A"] for x in rows])
    s = np.array([x["S"] for x in rows])
    n = len(rows)
    rng = np.random.default_rng(SEED)
    boots, undef = [], 0
    for _ in range(B):
        idx = rng.integers(0, n, n)
        k = kappa(a[idx], s[idx])
        if k is None:
            undef += 1
        else:
            boots.append(k)
    table = {"A1_S1": int(((a == 1) & (s == 1)).sum()), "A1_S0": int(((a == 1) & (s == 0)).sum()),
             "A0_S1": int(((a == 0) & (s == 1)).sum()), "A0_S0": int(((a == 0) & (s == 0)).sum())}

    def sub(kind):
        rr = [x for x in rows if x["kind"] == kind]
        aa = np.array([x["A"] for x in rr]); ss = np.array([x["S"] for x in rr])
        return {"n": len(rr), "agreement": float(np.mean(aa == ss)) if rr else None,
                "A1_S1": int(((aa == 1) & (ss == 1)).sum()), "A1_S0": int(((aa == 1) & (ss == 0)).sum()),
                "A0_S1": int(((aa == 0) & (ss == 1)).sum()), "A0_S0": int(((aa == 0) & (ss == 0)).sum())}

    e1 = [x for x in rows if x["E"] == 1]
    # FR 6.R5.2 variant: a failed scorer output counts as the wrong call (disagrees with A)
    n_fr = n + len(excluded)
    agree_fr = (int((a == s).sum())) / n_fr if n_fr else None
    out = {
        "stamp": "EXPLORATORY", "wording": "LLM-vs-LLM; not human", "gate_tag": "HIDE_NOT_HUMAN_VALIDATED",
        "rule": "decisions.md D60; FR 6.R5.4 'panel-majority A vs scorer S' (not pre-specified without an author file)",
        "definitions": "A = panel-majority Q2 'no' (not acknowledged); S = scorer E >= 0.5 (0 cruxes -> 0); "
                       "items with panel-majority Q1 = yes",
        "n_items_q1_yes": len(rows) + len(excluded), "n_used": n, "excluded": excluded,
        "table_A_by_S": table,
        "agreement": float(np.mean(a == s)),
        "cohen_kappa": {"point": kappa(a, s),
                        "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                        "B": B, "seed": SEED, "bootstrap": "item percentile; numpy.random.default_rng",
                        "undefined_resamples": undef},
        "agreement_failed_counted_wrong": agree_fr, "n_failed_counted_wrong_variant": n_fr,
        "by_kind": {"original": sub("original"), "n2": sub("n2")},
        "E_eq_1_items": {"n": len(e1), "panel_says_acknowledged": sum(1 for x in e1 if x["panel_q2"] == "yes"),
                         "original": {"n": sum(1 for x in e1 if x["kind"] == "original"),
                                      "acknowledged": sum(1 for x in e1 if x["kind"] == "original" and x["panel_q2"] == "yes")},
                         "n2": {"n": sum(1 for x in e1 if x["kind"] == "n2"),
                                "acknowledged": sum(1 for x in e1 if x["kind"] == "n2" and x["panel_q2"] == "yes")}},
        "caveats": ["panel judged one LLM-extracted quote pair; S summarises all scorer cruxes (unit mismatch, FR 6.R5.2)",
                    "both sides are LLMs; no human judgement", "n is small"],
        "rows": rows,
        "inputs_sha256": {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (PANEL, SCORES)},
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    Path(str(OUT) + ".sha256").write_text(f"{sha}  {OUT.name}\n", encoding="utf-8")
    run_log.log_run(__file__, "real (packet items; LLM-vs-LLM)", SEED, [PANEL, SCORES], f"{OUT} sha256:{sha}",
                    note="[EXPLORATORY; LLM-vs-LLM; not human] D60 panel-majority A vs scorer S on Q1=yes items")
    print(json.dumps({k: out[k] for k in ("n_items_q1_yes", "n_used", "excluded", "table_A_by_S", "agreement",
                                          "cohen_kappa", "agreement_failed_counted_wrong", "by_kind",
                                          "E_eq_1_items")}, indent=1))
    print("sha256", sha)


if __name__ == "__main__":
    main()
