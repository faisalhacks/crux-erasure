"""Independent re-derivation of FROZEN_RULES.md section 6.R5.1 (gate 1, step 2).

Written by the Opus gate reviewer (FROZEN_RULES 6.R5.6). Does NOT import step2_reference.py.
Reads no rank, candidate rating, E, per-crux label, critique, survey, top_candidate or reward column.
Output: analysis/review/rederive_step2_out.json (and a per-round CSV beside it, private).
"""
import collections
import csv
import hashlib
import json
import os
import statistics
import sys

import numpy as np
import pyarrow.parquet as pq
from scipy.stats import spearmanr

P = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1"
ROOT = os.path.dirname(P)
GCS = os.path.join(ROOT, "data", "habermas_gcs")
CC = os.path.join(GCS, "hm_all_candidate_comparisons.parquet")
PR = os.path.join(GCS, "hm_all_position_statement_ratings.parquet")
CC_SHA = "7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4"
PILOT = os.path.join(ROOT, "pilots", "T3_1", "pilot_groups.jsonl")
PILOT_SHA = "085d78472d9df42894a065f279656260a35931c3176d9dc5d23c7a38a6868daa"
A2TABLE = os.path.join(P, "analysis", "scores", "a2_long_shuffled.parquet")
EXTR = os.path.join(P, "analysis", "scores", "a2_extractions_v2.jsonl")
OUT = os.path.join(P, "analysis", "review", "rederive_step2_out.json")
OUT_ROUNDS = os.path.join(P, "analysis", "review", "rederive_step2_rounds.csv")

B = 10000
SEED_L = 20261141
SEED_Q = 20261142
TOK = {"STRONGLY_DISAGREE": -3, "DISAGREE": -2, "SOMEWHAT_DISAGREE": -1, "NEUTRAL": 0,
       "SOMEWHAT_AGREE": 1, "AGREE": 2, "STRONGLY_AGREE": 3}

CC_COLS = ["launch_id", "round_id", "iteration_index", "metadata.provenance",
           "own_opinion.metadata.participant_id", "own_opinion.metadata.provenance", "question.id"]
PR_COLS = ["launch_id", "question.id", "metadata.participant_id", "rating_index", "metadata.provenance",
           "metadata.status", "ratings.agreement", "monotonic_timestamp"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ba(h, s):
    h = np.asarray(h); s = np.asarray(s)
    pos = h == 1; neg = h == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return None
    sens = (s[pos] == 1).mean(); spec = (s[neg] == 0).mean()
    return 0.5 * (sens + spec), sens, spec


def cluster_boot(h, s, cl, seed):
    """Percentile cluster bootstrap. Clusters in sorted order; each resample draws K cluster indices
    with rng.integers(0, K, K). Single-class resample scores 0.5 and is counted."""
    h = np.asarray(h); s = np.asarray(s); cl = np.asarray(cl)
    keys = sorted(set(cl.tolist()))
    K = len(keys)
    pos_idx = {k: i for i, k in enumerate(keys)}
    ci = np.array([pos_idx[c] for c in cl])
    # per-cluster sufficient stats
    tp = np.bincount(ci, weights=(h == 1) & (s == 1), minlength=K)
    npos = np.bincount(ci, weights=(h == 1), minlength=K)
    tn = np.bincount(ci, weights=(h == 0) & (s == 0), minlength=K)
    nneg = np.bincount(ci, weights=(h == 0), minlength=K)
    rng = np.random.default_rng(seed)
    vals = np.empty(B); one = 0
    for b in range(B):
        idx = rng.integers(0, K, K)
        P_ = npos[idx].sum(); N_ = nneg[idx].sum()
        if P_ == 0 or N_ == 0:
            vals[b] = 0.5; one += 1
        else:
            vals[b] = 0.5 * (tp[idx].sum() / P_ + tn[idx].sum() / N_)
    return dict(lb=float(np.percentile(vals, 2.5)), ub=float(np.percentile(vals, 97.5)), n_one_class=one,
                K=K, method="rng.integers(0,K,K), sorted clusters, np.percentile linear")


def main():
    out = {"hash_checks": {}}
    out["hash_checks"]["candidate_comparisons"] = sha(CC) == CC_SHA
    out["hash_checks"]["pilot_groups"] = sha(PILOT) == PILOT_SHA
    if not all(out["hash_checks"].values()):
        print("HASH MISMATCH", out["hash_checks"]); sys.exit(2)

    # ---- round set: A2 table, launch_id/round_id only, minus development launches
    a2 = pq.read_table(A2TABLE, columns=["launch_id", "round_id"]).to_pandas().drop_duplicates()
    dev = set()
    with open(PILOT, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dev.add(json.loads(line)["launch_id"])
    out["n_dev_launches"] = len(dev)
    out["n_a2_rounds_all"] = len(a2); out["n_a2_launches_all"] = a2.launch_id.nunique()
    conf = a2[~a2.launch_id.isin(dev)]
    rounds = sorted(set(zip(conf.launch_id, conf.round_id)))
    out["n_rounds_in"] = len(rounds)
    out["n_launches_in"] = len({l for l, _ in rounds})
    if len(rounds) != 1622:
        print("ROUND COUNT", len(rounds)); json.dump(out, open(OUT, "w"), indent=1); sys.exit(3)
    rset = set(rounds)

    # ---- question and members from iteration-0 HUMAN_CITIZEN comparison rows
    cc = pq.read_table(CC, columns=CC_COLS, filters=[("iteration_index", "==", 0)]).to_pandas()
    cc = cc[[(l, r) in rset for l, r in zip(cc.launch_id, cc.round_id)]]
    cch = cc[cc["metadata.provenance"] == "HUMAN_CITIZEN"]
    out["diag_own_opinion_prov_not_human_in_human_rows"] = int((cch["own_opinion.metadata.provenance"] != "HUMAN_CITIZEN").sum())
    g = cch.groupby(["launch_id", "round_id"])
    qmap = g["question.id"].agg(lambda x: sorted(set(x.dropna())))
    mmap = g["own_opinion.metadata.participant_id"].agg(lambda x: sorted(set(x.dropna())))

    # ---- position ratings (rating_index 0)
    pr = pq.read_table(PR, columns=PR_COLS).to_pandas()
    out["n_pr_rows_total"] = len(pr)
    pr0 = pr[(pr.rating_index == 0) & (pr["metadata.provenance"] == "HUMAN_CITIZEN") & (pr["metadata.status"] == "COMPLETED")]
    tokc = collections.Counter()
    best = {}
    dup_keys = 0
    for l, q, m, ag, ts in zip(pr0.launch_id, pr0["question.id"], pr0["metadata.participant_id"],
                               pr0["ratings.agreement"], pr0.monotonic_timestamp):
        k = (l, q, m)
        if k in best:
            dup_keys += 1
            if ts >= best[k][1]:
                continue
        best[k] = (ag, ts)
    out["n_duplicate_rating_keys"] = dup_keys

    def value(ag):
        if ag is None:
            return None
        ag = list(ag)
        if len(ag) != 1:
            return None
        return TOK.get(ag[0])

    # ---- extractions
    ext = {}
    with open(EXTR, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            ext[(r["launch_id"], r["round_id"])] = r

    rows = []
    reasons = collections.Counter()
    n_ctx = 0; n_missing = 0; n_crux_nonsan = 0
    for (l, r) in rounds:
        qs = qmap.get((l, r), [])
        if len(qs) != 1:
            reasons["q_not_exactly_one"] += 1; continue
        q = qs[0]; M = mmap.get((l, r), [])
        e = ext.get((l, r))
        if e is not None and e.get("dropped_too_long"):
            n_ctx += 1; reasons["context_length"] += 1; continue
        vals = []
        n_unrated = 0
        for m in M:
            got = best.get((l, q, m))
            v = value(got[0]) if got else None
            if got:
                tokc[tuple(got[0]) if got[0] is not None else None] += 1
            if v is None:
                n_unrated += 1
            else:
                vals.append(v)
        if len(vals) < 3 or n_unrated > 1:
            reasons["rating_coverage"] += 1; continue
        hs = int(any(v >= 1 for v in vals) and any(v <= -1 for v in vals))
        hs_strong = int(any(v >= 2 for v in vals) and any(v <= -2 for v in vals))
        if e is None or not e.get("ok") or e.get("cruxes") is None:
            missing = True; ncx = None
        else:
            missing = False
            cx = [c for c in e["cruxes"] if c.get("members_a") and c.get("members_b")]
            n_crux_nonsan += len(e["cruxes"]) - len(cx)
            ncx = len(cx)
        rows.append(dict(launch_id=l, round_id=r, q=q, n_members=len(M), n_rated=len(vals), n_unrated=n_unrated,
                         hsplit=hs, hsplit_strong=hs_strong, missing=missing, n_cruxes=ncx,
                         sd=statistics.pstdev(vals), sd_np=float(np.std(vals))))
        if missing:
            n_missing += 1
    out["token_counts_member_ratings"] = {str(k): v for k, v in tokc.items()}
    out["unusable_reasons"] = dict(reasons)
    out["n_dropped_context_length"] = n_ctx
    out["n_extraction_missing_counted_wrong"] = n_missing
    out["n_cruxes_removed_by_resanitising"] = n_crux_nonsan

    def sdis(row, ref):
        if row["missing"]:
            return 1 - row[ref]        # counted as the wrong call
        return int(row["n_cruxes"] >= 1)

    H = np.array([x["hsplit"] for x in rows]); S = np.array([sdis(x, "hsplit") for x in rows])
    L = [x["launch_id"] for x in rows]; Q = [x["q"] for x in rows]
    out["n_usable_rounds"] = len(rows); out["n_usable_launches"] = len(set(L))
    cls = {}
    for c in (0, 1):
        sel = [x for x in rows if x["hsplit"] == c]
        cls[str(c)] = {"rounds": len(sel), "launches": len({x["launch_id"] for x in sel})}
    out["hsplit_class_counts"] = cls
    out["confusion"] = {"tp": int(((H == 1) & (S == 1)).sum()), "fn": int(((H == 1) & (S == 0)).sum()),
                        "tn": int(((H == 0) & (S == 0)).sum()), "fp": int(((H == 0) & (S == 1)).sum())}
    b2, se, sp = ba(H, S)
    out["BA2"] = float(b2); out["sens"] = float(se); out["spec"] = float(sp)
    out["launch_boot"] = cluster_boot(H, S, L, SEED_L)
    qlaunch = collections.defaultdict(set)
    for x in rows:
        qlaunch[x["q"]].add(x["launch_id"])
    multi = any(len(v) > 1 for v in qlaunch.values())
    out["question_in_more_than_one_launch"] = multi
    out["n_questions"] = len(qlaunch)
    if multi:
        out["question_boot"] = cluster_boot(H, S, Q, SEED_Q)
    lbs = [out["launch_boot"]["lb"]] + ([out["question_boot"]["lb"]] if multi else [])
    lb = min(lbs)
    out["lb_used"] = lb
    usable = (len(rows) >= 200 and len(set(L)) >= 100 and all(cls[c]["rounds"] >= 50 and cls[c]["launches"] >= 25 for c in cls)
              and out["launch_boot"]["n_one_class"] <= 0.01 * B and (not multi or out["question_boot"]["n_one_class"] <= 0.01 * B))
    out["usable"] = usable
    if not usable:
        outcome = "UNUSABLE"
    elif lb <= 0.5:
        outcome = "FAIL"
    elif b2 >= 0.60:
        outcome = "PASS"
    else:
        outcome = "WEAK"
    out["outcome"] = outcome

    # ---- reported, no rule
    rep = {}
    rep["prevalence_hsplit"] = float(H.mean()); rep["prevalence_sdis"] = float(S.mean())
    i5 = [i for i, x in enumerate(rows) if x["n_rated"] == 5]
    rep["BA2_n_rated_5"] = float(ba(H[i5], S[i5])[0]); rep["n_rated_5_rounds"] = len(i5)
    ia = [i for i, x in enumerate(rows) if x["n_unrated"] == 0]
    rep["BA2_all_rated"] = float(ba(H[ia], S[ia])[0]); rep["n_all_rated"] = len(ia)
    Hs = np.array([x["hsplit_strong"] for x in rows]); Ss = np.array([sdis(x, "hsplit_strong") for x in rows])
    rep["BA2_strong_split"] = float(ba(Hs, Ss)[0])
    ok = [x for x in rows if not x["missing"]]
    rep["spearman_ncruxes_sd"] = float(spearmanr([x["n_cruxes"] for x in ok], [x["sd"] for x in ok]).correlation)
    # convention of the code of record (found after the independent run, to explain a 8e-6 gap):
    # missing extraction -> 0 cruxes, SD = np.std (float ties differ from exact pstdev)
    rep["spearman_ncruxes_sd_missing0_npstd"] = float(spearmanr(
        [0 if x["missing"] else x["n_cruxes"] for x in rows], [x["sd_np"] for x in rows]).correlation)
    rep["context_drop_share"] = n_ctx / len(rounds)
    out["reported_no_rule"] = rep

    with open(OUT_ROUNDS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ["sdis"])
        w.writeheader()
        for x in rows:
            w.writerow(dict(x, sdis=sdis(x, "hsplit")))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
