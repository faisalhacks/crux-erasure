"""LLM annotator panel (supplementary; not human), task P1: summary per FROZEN_RULES.md 6.R5.4.

Computes ONLY what 6.R5.4 lists that needs no human label and no scorer output: per-model format validity (bar and
packet), membership and panel status (PANEL / NO_PANEL), the per-item majority answers, and the inter-model agreement
(Fleiss' kappa, pairwise Cohen's kappa, Gwet's AC1 multi-rater and pairwise), each with an item percentile bootstrap
CI (B = 10,000; every statistic's bootstrap starts from numpy.random.default_rng(20261145)) and n.  Agreement
statistics use complete cases (items answered validly by every model in the set).  A resample where a statistic is
undefined (chance agreement = 1) is counted and excluded.  No comparison with the author or the scorer (that is
gate1_r5.py / verification_eval.py).  No panel number is described qualitatively.
Usage (from P): C:/Users/intel/miniconda3/python.exe -I analysis/panel_summary.py
"""
import hashlib
import itertools
import json
import shutil
from pathlib import Path

import numpy as np

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
OUT = P / "analysis" / "panel"
GATE = P / "gate1" / "llm_panel"
MEMBERS = ["falcon-h1-34b", "command-r7b", "granite4.2-30b"]
QS = ["q1_quotes_disagree", "q2_statement_acknowledges"]
B, SEED = 10000, 20261145
WORDING = "LLM annotator panel (supplementary; not human)"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fleiss(M):
    """M: n x m array of 0/1. Returns kappa or nan."""
    n, m = M.shape
    yes = M.sum(1)
    cnt = np.stack([m - yes, yes], 1)
    pa = ((cnt * (cnt - 1)).sum(1) / (m * (m - 1))).mean()
    pk = cnt.sum(0) / (n * m)
    pe = (pk ** 2).sum()
    return np.nan if np.isclose(pe, 1.0) else (pa - pe) / (1 - pe)


def ac1(M):
    """Gwet's AC1 for m >= 2 raters, 2 categories (Gwet 2008); m = 2 gives the pairwise AC1."""
    n, m = M.shape
    yes = M.sum(1)
    cnt = np.stack([m - yes, yes], 1)
    pa = ((cnt * (cnt - 1)).sum(1) / (m * (m - 1))).mean()
    pk = cnt.sum(0) / (n * m)
    pe = (pk * (1 - pk)).sum() / (2 - 1)
    return np.nan if np.isclose(pe, 1.0) else (pa - pe) / (1 - pe)


def cohen(M):
    a, b = M[:, 0], M[:, 1]
    po = (a == b).mean()
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return np.nan if np.isclose(pe, 1.0) else (po - pe) / (1 - pe)


def boot(fn, M):
    n = M.shape[0]
    pt = fn(M) if n else np.nan
    rng = np.random.default_rng(SEED)
    vals = np.empty(B)
    for b in range(B):
        vals[b] = fn(M[rng.integers(0, n, n)]) if n else np.nan
    ok = vals[~np.isnan(vals)]
    ci = [float(np.percentile(ok, 2.5)), float(np.percentile(ok, 97.5))] if len(ok) else [None, None]
    return dict(point=None if np.isnan(pt) else float(pt), ci95=ci, n=int(n), B=B, undefined_resamples=int(B - len(ok)),
                bootstrap="item percentile; numpy.random.default_rng(20261145)")


def main():
    man = json.loads((GATE / "panel_manifest.json").read_text(encoding="utf-8"))
    per_model, answers = {}, {}
    for m in MEMBERS:
        bf, rf, pf = OUT / f"bar_p1_{m}.json", OUT / f"run_p1_{m}.json", OUT / f"panel_p1_{m}.jsonl"
        bar = json.loads(bf.read_text(encoding="utf-8")) if bf.exists() else None
        run = json.loads(rf.read_text(encoding="utf-8")) if rf.exists() else None
        rows = [json.loads(x) for x in pf.read_text(encoding="utf-8").splitlines() if x.strip()] if pf.exists() else None
        pm = dict(format_bar=bar, bar_pass=bool(bar and bar.get("bar_pass")),
                  session_cost_usd=(run or {}).get("session") and run["session"]["session_cost_usd"],
                  packet_called=bool(rows))
        if rows:
            pm.update(packet_items=len(rows), packet_calls=sum(len(r["attempts"]) for r in rows),
                      packet_first_attempt_valid=sum(1 for r in rows if r["attempts"] and r["attempts"][0].get("valid")),
                      packet_valid_after_retry=sum(1 for r in rows if r["valid"]),
                      packet_missing=sum(1 for r in rows if not r["valid"]),
                      packet_valid_share=sum(1 for r in rows if r["valid"]) / len(rows))
            answers[m] = {r["item_id"]: r["parsed"] for r in rows}
        per_model[m] = pm
    passed = [m for m in MEMBERS if per_model[m]["bar_pass"]]
    status = "PANEL" if len(passed) >= 2 else "NO_PANEL"
    summ = dict(wording=WORDING, task="P1", rules="FROZEN_RULES.md 6.R5.4; decisions.md D50, D51",
                manifest_sha256=sha(GATE / "panel_manifest.json"), prompt_sha256=man["prompt_sha256"],
                per_model=per_model, members=passed, panel_status=status,
                note=("P1 shares its inputs (the same quotes) with the author, so agreement with the author is partly built "
                      "in. Not human; never a gate input; no effect on the gate status, H5 or any wording state."))
    if status == "PANEL":
        missing_members = [m for m in passed if m not in answers]
        items = sorted(set().union(*[set(answers[m]) for m in passed if m in answers]))
        maj, agree = {}, {}
        for q in QS:
            mq, nomaj = {}, 0
            for it in items:
                vals = {m: (answers.get(m, {}).get(it) or {}).get(q) for m in passed}
                got = [v for v in vals.values() if v is not None]
                if len(passed) == 2:
                    v = got[0] if len(got) == 2 and got[0] == got[1] else "NO_MAJORITY"
                else:
                    c = {x: got.count(x) for x in set(got)}
                    win = [x for x, k in c.items() if k >= 2]
                    v = win[0] if win else "NO_MAJORITY"
                nomaj += v == "NO_MAJORITY"
                mq[it] = v
            maj[q] = dict(by_item=mq, n_items=len(items), n_no_majority=nomaj,
                          n_yes=sum(1 for v in mq.values() if v == "yes"), n_no=sum(1 for v in mq.values() if v == "no"))
            # agreement among members (complete cases)
            def mat(ms):
                rows = []
                for it in items:
                    v = [(answers.get(m, {}).get(it) or {}).get(q) for m in ms]
                    if all(x is not None for x in v):
                        rows.append([1 if x == "yes" else 0 for x in v])
                return np.array(rows, dtype=float).reshape(-1, len(ms))
            ms = [m for m in passed if m in answers]
            aq = dict(members=ms)
            if len(ms) >= 2:
                Mall = mat(ms)
                aq["fleiss_kappa"] = boot(fleiss, Mall)
                aq["gwet_ac1"] = boot(ac1, Mall)
                aq["pairwise"] = {}
                for x, y in itertools.combinations(ms, 2):
                    Mp = mat([x, y])
                    aq["pairwise"][f"{x}|{y}"] = dict(cohen_kappa=boot(cohen, Mp), gwet_ac1=boot(ac1, Mp),
                                                      raw_agreement=float((Mp[:, 0] == Mp[:, 1]).mean()) if len(Mp) else None)
            agree[q] = aq
        summ.update(majority=maj, agreement=agree, members_without_packet_answers=missing_members,
                    majority_rule=man["majority"])
    f = OUT / "panel_p1_summary.json"
    f.write_text(json.dumps(summ, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    GATE.mkdir(parents=True, exist_ok=True)
    copied = {}
    for p in sorted(OUT.glob("*")):
        if p.is_file() and p.suffix in (".json", ".jsonl", ".md"):
            shutil.copyfile(p, GATE / p.name)
            copied[p.name] = sha(p)
    print(json.dumps(dict(status=status, members=passed, sha256=copied), indent=1))


if __name__ == "__main__":
    main()
