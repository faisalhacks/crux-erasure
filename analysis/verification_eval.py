"""verification_eval.py -- FROZEN_RULES 6.R5 step 3 (R5; decisions.md D49b, D50, D51).

"human verification of LLM-extracted evidence by a hypothesis-aware author".
Inputs:
  labels/author_verification.csv  columns exactly item_id,q1_quotes_disagree,q2_statement_acknowledges,comment,pass_started_utc;
                                  25 rows; q1/q2 in {YES, NO} (case and spaces ignored); pass_started_utc ISO UTC.
  scores file (jsonl, one per item, written and hashed before the author's file): item_id, kind ('original'|'n2'),
                                  E (float or null), n_cruxes (int or null), ok (bool: extraction and labels parsed).
Derived (FR 6.R5 step 3):
  S_i = 1 if E >= 0.5; 0 if E < 0.5 or n_cruxes == 0; missing E -> counted as the wrong call (S = 1 - A).
  C_i = 1 if n_cruxes >= 1.   A_i = 1 if q2_statement_acknowledges == NO.
  Item ids and kind come from the packet key (labels_build/v5/key_verification.csv); a scores-file kind that disagrees
  with the key, or a key item without a score record, stops the run.
  V_ev = share Q1 = YES (Wilson 95%), also by kind; presence table C vs Q1;
  on Q1 = YES items: 2x2 S x A, sens/spec (Wilson), BA3 and kappa with item percentile bootstrap
  (B = 10,000, default_rng(20261144); one-class resamples counted), one-sided CONDITIONAL Fisher exact test
  (scipy fisher_exact, alternative='greater', on [[A1S1, A1S0], [A0S1, A0S0]]; no mid-p);
  H5 = originals with Q1 = YES: share Q2 = NO (Wilson), only if >= 10 such originals.
Outcome codes: SUPPORTED (usable and Fisher p <= 0.05), CONTRADICTED (usable and BA3 point <= 0.5),
  INCONCLUSIVE, UNUSABLE (file complete, >= 10 Q1-yes items, >= 3 items in each A class, else UNUSABLE),
  INCOMPLETE (file present but invalid: the pipeline waits, never fills).
Never shown to the author: nothing here is written into labels/.
"""
import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P_DEFAULT = HERE.parent
COLUMNS = ["item_id", "q1_quotes_disagree", "q2_statement_acknowledges", "comment", "pass_started_utc"]  # builder names, labels_build/v5/TEMPLATE
KEY_DEFAULT = P_DEFAULT / "labels_build" / "v5" / "key_verification.csv"   # packet key (sha edcf5eb3...): item ids and kind


def read_key(path):
    """item_id -> kind ('original' | 'n2') from the packet key.  Only item_id and kind are used."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["item_id"]: r["kind"] for r in csv.DictReader(f)}
N_ITEMS = 25
MIN_Q1_YES, MIN_PER_CLASS, MIN_H5 = 10, 3, 10
SEED = 20261144
B_DEFAULT = 10000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wilson(k, n, z=1.959964):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def parse_utc(s):
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def read_author_file(path, ids):
    """Returns (rows dict item_id -> (q1, q2), problems list).  Never repairs anything."""
    probs = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.reader(f)
        try:
            head = next(rd)
        except StopIteration:
            return {}, ["empty file"]
        if [h.strip() for h in head] != COLUMNS:
            return {}, [f"columns {head} != {COLUMNS}"]
        rows = [r for r in rd if any(c.strip() for c in r)]
    if len(rows) != N_ITEMS:
        probs.append(f"{len(rows)} rows, expected {N_ITEMS}")
    out, times = {}, set()
    for i, r in enumerate(rows, 2):
        if len(r) != len(COLUMNS):
            probs.append(f"line {i}: {len(r)} fields")
            continue
        iid, q1, q2, _c, ts = (x.strip() for x in r)
        q1, q2 = q1.upper(), q2.upper()
        if iid not in ids:
            probs.append(f"line {i}: unknown item_id {iid!r}")
        elif iid in out:
            probs.append(f"line {i}: repeated item_id {iid!r}")
        if q1 not in ("YES", "NO") or q2 not in ("YES", "NO"):
            probs.append(f"line {i}: invalid answer ({q1!r}, {q2!r})")
        if parse_utc(ts) is None:
            probs.append(f"line {i}: pass_started_utc {ts!r} unparseable")
        times.add(ts)
        out[iid] = (q1, q2)
    if len(times) > 1:
        probs.append("pass_started_utc differs between rows")
    missing = set(ids) - set(out)
    if missing:
        probs.append(f"{len(missing)} item_ids missing")
    return out, probs


def read_scores(path):
    d = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            d[r["item_id"]] = r
    return d


def kappa2(a, b):
    a, b = np.asarray(a, int), np.asarray(b, int)
    po = float((a == b).mean())
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def ba(a, s):
    a, s = np.asarray(a, int), np.asarray(s, int)
    if a.sum() == 0 or (1 - a).sum() == 0:
        return None
    return 0.5 * (((a == 1) & (s == 1)).sum() / (a == 1).sum() + ((a == 0) & (s == 0)).sum() / (a == 0).sum())


def fisher_greater(a, s):
    from scipy.stats import fisher_exact
    a, s = np.asarray(a, int), np.asarray(s, int)
    tab = [[int(((a == 1) & (s == 1)).sum()), int(((a == 1) & (s == 0)).sum())],
           [int(((a == 0) & (s == 1)).sum()), int(((a == 0) & (s == 0)).sum())]]
    if min(sum(tab[0]), sum(tab[1]), tab[0][0] + tab[1][0], tab[0][1] + tab[1][1]) == 0:
        return 1.0, tab                     # a margin is empty: no evidence (p = 1), as old FR 6.6
    return float(fisher_exact(tab, alternative="greater")[1]), tab


def boot_items(a, s, B, seed):
    a, s = np.asarray(a, int), np.asarray(s, int)
    rng = np.random.default_rng(seed)
    n = len(a)
    bas, ks = [], []
    one_ba = one_k = 0
    for _ in range(B):
        i = rng.integers(0, n, n)
        v = ba(a[i], s[i])
        if v is None:
            one_ba += 1
        else:
            bas.append(v)
        k = kappa2(a[i], s[i])
        if k is None or a[i].min() == a[i].max():
            one_k += 1
        else:
            ks.append(k)
    pct = lambda x: (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))) if x else (None, None)
    return {"BA3_ci": pct(bas), "BA3_one_class_resamples": one_ba, "kappa_ci": pct(ks), "kappa_undefined_resamples": one_k}


def decide(usable, p_fisher, ba3):
    """THE step-3 outcome rule (FR 6.R5)."""
    if not usable:
        return "UNUSABLE"
    if p_fisher <= 0.05:
        return "SUPPORTED"
    if ba3 is not None and ba3 <= 0.5:
        return "CONTRADICTED"
    return "INCONCLUSIVE"


def evaluate(answers, scores, B=B_DEFAULT, seed=SEED):
    """answers: item_id -> (q1, q2) for all 25 items (complete file).  scores: item_id -> score record."""
    ids = sorted(answers)
    res = {"n_items": len(ids), "B": B, "seed": seed}
    q1 = {i: answers[i][0] == "YES" for i in ids}
    kind = {i: scores[i].get("kind") for i in ids}
    k = sum(q1.values())
    res["V_ev"] = {"k": k, "n": len(ids), "rate": k / len(ids), "wilson": wilson(k, len(ids))}
    for kd in ("original", "n2"):
        sub = [i for i in ids if kind[i] == kd]
        kk = sum(q1[i] for i in sub)
        res[f"V_ev_{kd}"] = {"k": kk, "n": len(sub), "wilson": wilson(kk, len(sub))}
    C = {i: int((scores[i].get("n_cruxes") or 0) >= 1) for i in ids}
    agree = sum(C[i] == int(q1[i]) for i in ids)
    res["presence_table"] = {"C1_Q1yes": sum(C[i] and q1[i] for i in ids), "C1_Q1no": sum(C[i] and not q1[i] for i in ids),
                             "C0_Q1yes": sum((not C[i]) and q1[i] for i in ids),
                             "C0_Q1no": sum((not C[i]) and not q1[i] for i in ids),
                             "raw_agreement": agree / len(ids), "wilson": wilson(agree, len(ids))}
    yes = [i for i in ids if q1[i]]
    A = {i: int(answers[i][1] == "NO") for i in ids}
    S, n_missing = {}, 0
    for i in ids:
        e, nc = scores[i].get("E"), scores[i].get("n_cruxes")
        if nc == 0:
            S[i] = 0
        elif e is None or not scores[i].get("ok", True):
            S[i] = 1 - A[i]                  # missing E counts as the wrong call
            n_missing += i in yes
        else:
            S[i] = int(e >= 0.5)
    res["n_missing_E_on_q1_yes_counted_wrong"] = n_missing
    a = [A[i] for i in yes]
    s = [S[i] for i in yes]
    n1 = sum(a)
    n0 = len(a) - n1
    usable = len(yes) >= MIN_Q1_YES and n1 >= MIN_PER_CLASS and n0 >= MIN_PER_CLASS
    res["usable"] = usable
    res["n_q1_yes"], res["n_not_ack"], res["n_ack"] = len(yes), n1, n0
    p, tab = fisher_greater(a, s) if yes else (1.0, [[0, 0], [0, 0]])
    res["table_A_by_S"] = tab
    res["fisher_p_one_sided_conditional"] = p
    ba3 = ba(a, s) if yes else None
    res["BA3"] = ba3
    res["kappa"] = kappa2(a, s) if yes and len(set(a)) > 1 else None
    tp, fn = tab[0]
    fp, tn = tab[1]
    res["sens"] = {"k": tp, "n": tp + fn, "wilson": wilson(tp, tp + fn)}
    res["spec"] = {"k": tn, "n": tn + fp, "wilson": wilson(tn, tn + fp)}
    if yes:
        res.update(boot_items(a, s, B, seed))
    for kd in ("original", "n2"):
        sub = [i for i in yes if kind[i] == kd]
        res[f"split_{kd}"] = fisher_greater([A[i] for i in sub], [S[i] for i in sub])[1] if sub else None
    res["outcome"] = decide(usable, p, ba3)
    if res["outcome"] == "CONTRADICTED":
        ci = res.get("BA3_ci", (None, None))
        res["contradicted_wording"] = (f"point balanced accuracy <= 0.5 (BA3 = {ba3:.3f}, n = {len(yes)}, "
                                       f"bootstrap 95% CI [{ci[0]}, {ci[1]}])")
    orig_yes = [i for i in yes if kind[i] == "original"]
    if len(orig_yes) >= MIN_H5:
        kk = sum(A[i] for i in orig_yes)
        res["H5"] = {"k": kk, "n": len(orig_yes), "rate": kk / len(orig_yes), "wilson": wilson(kk, len(orig_yes))}
    else:
        res["H5"] = None
    return res


def run(labels_file, scores_file, gate_dir, B=B_DEFAULT, kind="dummy", key_file=None):
    """Returns (status, result).  status in INCOMPLETE / COMPUTED.  On real data the first complete author file's hash
    is written once to gate_dir/AUTHOR_VERIFICATION_HASH.json; a later different file is refused.
    key_file: packet key; its item ids are the item set and its 'kind' overrides nothing: a mismatch stops the run."""
    scores = read_scores(scores_file)
    if key_file:
        key = read_key(key_file)
        if set(key) != set(scores):
            sys.exit(f"REFUSED (FR 6.R5): scores file items != key items ({len(set(key) ^ set(scores))} differ).")
        bad = [i for i in key if scores[i].get("kind") != key[i]]
        if bad:
            sys.exit(f"REFUSED (FR 6.R5): kind in scores file != key for {bad}.")
    answers, probs = read_author_file(labels_file, set(scores))
    if probs:
        return "INCOMPLETE", {"outcome": "INCOMPLETE", "problems": probs}
    gd = Path(gate_dir)
    hp = gd / "AUTHOR_VERIFICATION_HASH.json"
    h = sha(labels_file)
    if hp.exists():
        if json.loads(hp.read_text(encoding="utf-8"))["sha256"] != h:
            sys.exit("REFUSED (FR 6.R5): author_verification.csv differs from the first complete file; never replaced.")
    else:
        gd.mkdir(parents=True, exist_ok=True)
        mt = datetime.fromtimestamp(Path(labels_file).stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(hp, "x", encoding="utf-8") as f:
            json.dump({"sha256": h, "mtime_utc": mt,
                       "first_seen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, f, indent=1)
    res = evaluate(answers, scores, B=B)
    res.update(rules="R5", step=3, kind=kind, labels_sha256=h, scores_sha256=sha(scores_file),
               key_sha256=sha(key_file) if key_file else None,
               wording="human verification of LLM-extracted evidence by a hypothesis-aware author")
    return "COMPUTED", res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=("dummy", "real"))
    ap.add_argument("--labels", default=str(P_DEFAULT / "labels" / "author_verification.csv"))
    ap.add_argument("--scores", required=True)
    ap.add_argument("--key", default=str(KEY_DEFAULT))
    ap.add_argument("--gate-dir", default=str(P_DEFAULT / "gate1"))
    ap.add_argument("--out", default=None, help="default (real): gate1/STEP3_computed__<utc>.json")
    a = ap.parse_args(argv)
    if a.kind == "real" and not (P_DEFAULT / "gate1" / "FREEZE.json").exists():
        sys.exit("REFUSED (FR 6.R5): gate1/FREEZE.json absent.")
    if a.out is None:
        if a.kind != "real":
            sys.exit("--out required for dummy")
        a.out = str(Path(a.gate_dir) / f"STEP3_computed__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json")
    st, res = run(a.labels, a.scores, a.gate_dir, kind=a.kind, key_file=a.key)
    with open(a.out, "x", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    print(st, res.get("outcome"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
