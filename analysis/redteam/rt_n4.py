"""Red-team checks on N4 and on what drives A2 (exploratory; read-only inputs; writes analysis/redteam/rt_n4.json).
(a) Do the extractor's side lists for the first-listed crux (the N4 'minority' source) separate members by their own
    pre-deliberation position rating (hm_all_position_statement_ratings, rating_index 0)?  Within-round permutation null.
(b) A2 with E split into its SIDED share and its BLENDED+OMITTED share (E = sided + blended_omitted shares).
(c) N4 re-fit independently (own code) and N4 with the sided share as the predictor.
Usage: python -I rt_n4.py"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parents[2]
PILOT = P.parent / "pilots" / "T3_1"
DATA = P.parent / "data" / "habermas_gcs"
OUT = Path(__file__).resolve().parent / "rt_n4.json"
WORD = re.compile(r"[A-Za-z0-9']+")
TOK = {"STRONGLY_DISAGREE": -3, "DISAGREE": -2, "SOMEWHAT_DISAGREE": -1, "NEUTRAL": 0,
       "SOMEWHAT_AGREE": 1, "AGREE": 2, "STRONGLY_AGREE": 3}


def syl(w):
    w = w.lower()
    n = len(re.findall(r"[aeiouy]+", w))
    if n > 1 and w.endswith("e") and not w.endswith("le"):
        n -= 1
    return max(n, 1)


def flesch(t):
    ws = WORD.findall(t)
    nw = max(len(ws), 1)
    ns = max(len([s for s in re.split(r"[.!?]+", t) if s.strip()]), 1)
    return 206.835 - 1.015 * nw / ns - 84.6 * sum(syl(w) for w in ws) / nw


def midrank(v):
    v = np.asarray(v, float)
    return np.array([(v < x).sum() + ((v == x).sum() + 1) / 2.0 for x in v])


dev = {json.loads(l)["launch_id"] for l in open(PILOT / "pilot_groups.jsonl", encoding="utf-8") if l.strip()}
groups = [json.loads(l) for l in open(PILOT / "all_groups.jsonl", encoding="utf-8")]
sc = {}
for l in open(P / "analysis" / "scores" / "a2_scores_v2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    sc[(r["round_id"], int(r["cand"]))] = r
ex = {}
for l in open(P / "analysis" / "scores" / "a2_extractions_v2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    ex[r["round_id"]] = r

ps = pd.read_parquet(DATA / "hm_all_position_statement_ratings.parquet",
                     columns=["launch_id", "question.id", "metadata.participant_id", "metadata.provenance", "metadata.status",
                              "rating_index", "ratings.agreement", "monotonic_timestamp"])
ps = ps[(ps.rating_index == 0) & (ps["metadata.provenance"] == "HUMAN_CITIZEN") & (ps["metadata.status"] == "COMPLETED")].copy()


def mv(a):
    if a is None:
        return None
    a = list(a)
    return TOK.get(str(a[0]).strip().upper()) if len(a) == 1 else None


ps["v"] = [mv(a) for a in ps["ratings.agreement"]]
ps = ps[ps.v.notna()].sort_values("monotonic_timestamp").drop_duplicates(["launch_id", "question.id", "metadata.participant_id"])
val = {(a, q, m): v for a, q, m, v in zip(ps.launch_id, ps["question.id"], ps["metadata.participant_id"], ps.v)}

res = {}
rng = np.random.default_rng(5)
obs, null_means, n_rounds_sep = [], [], 0
rows, stm = [], []
for g in groups:
    if g["launch_id"] in dev:
        continue
    rid = g["round_id"]
    x = ex.get(rid)
    if not x or not x.get("ok") or x["n_cruxes"] == 0:
        continue
    Es = [sc.get((rid, j)) for j in range(4)]
    if any(s is None or s["E"] is None for s in Es):
        continue
    order = sorted(g["opinions"])
    num = {i + 1: pid for i, pid in enumerate(order)}
    c0 = x["cruxes"][0]
    A = [num[k] for k in c0["members_a"] if k in num]
    Bm = [num[k] for k in c0["members_b"] if k in num]
    va = [val.get((g["launch_id"], g["question_id"], p)) for p in A]
    vb = [val.get((g["launch_id"], g["question_id"], p)) for p in Bm]
    va = [v for v in va if v is not None]
    vb = [v for v in vb if v is not None]
    if va and vb:
        n_rounds_sep += 1
        d = abs(np.mean(va) - np.mean(vb))
        obs.append(d)
        allv = np.array(va + vb, float)
        nn = []
        for _ in range(200):
            p_ = rng.permutation(allv)
            nn.append(abs(p_[:len(va)].mean() - p_[len(va):].mean()))
        null_means.append(np.mean(nn))
    sa, sb = set(c0["members_a"]), set(c0["members_b"])
    pid2num = {pid: i + 1 for i, pid in enumerate(order)}
    for j, c in enumerate(g["candidates"]):
        lab = Es[j]["labels"]
        nw = len(WORD.findall(c))
        stm.append(dict(round_id=rid, cand=j, launch_id=g["launch_id"], E=float(Es[j]["E"]),
                        sided=sum(l_ == "SIDED" for l_ in lab) / len(lab),
                        blom=sum(l_ in ("BLENDED", "OMITTED") for l_ in lab) / len(lab),
                        loglen=np.log(nw), fl=flesch(c)))
    for r in g["raters"]:
        if len(set(r["ranks"])) == 1:
            continue
        k = pid2num.get(r["pid"])
        mino = np.nan
        if len(sa) != len(sb) and k is not None and ((k in sa) != (k in sb)):
            mino = 1.0 if k in (sa if len(sa) < len(sb) else sb) else 0.0
        m = midrank(r["ranks"])
        for j in range(4):
            rows.append(dict(round_id=rid, rater=r["pid"], cand=j, y=(4 - m[j]) / 3.0, minority=mino))

obs, null_means = np.array(obs), np.array(null_means)
res["sides_vs_prerating"] = {"n_rounds_both_sides_rated": n_rounds_sep, "mean_abs_diff_obs": float(obs.mean()),
                             "mean_abs_diff_perm_null": float(null_means.mean()),
                             "share_rounds_obs_gt_null_mean": float((obs > null_means).mean())}
S = pd.DataFrame(stm)
for c in ("loglen", "fl"):
    S["z_" + c] = (S[c] - S[c].mean()) / S[c].std(ddof=0)
D = pd.DataFrame(rows).merge(S, on=["round_id", "cand"])
D["rr"] = D.round_id + "|" + D.rater


def fit(d, cols):
    g = d.groupby("rr")
    y = (d.y - g.y.transform("mean")).to_numpy()
    X = np.column_stack([(d[c] - g[c].transform("mean")).to_numpy(float) for c in cols])
    Ai = np.linalg.inv(X.T @ X)
    b = Ai @ X.T @ y
    e = y - X @ b
    codes, u = pd.factorize(d.launch_id)
    G = len(u)
    s = np.zeros((G, X.shape[1]))
    np.add.at(s, codes, X * e[:, None])
    se = np.sqrt(np.diag(Ai @ s.T @ s @ Ai) * G / (G - 1))
    return {c: {"est": float(b[i]), "se_cr1": float(se[i]), "t": float(b[i] / se[i])} for i, c in enumerate(cols)} | {"_G": G, "_n": int(len(d))}


res["A2_check"] = fit(D, ["E", "z_loglen", "z_fl"])
res["A2_E_split_sided_vs_blended_omitted"] = fit(D, ["sided", "blom", "z_loglen", "z_fl"])
res["corr_within_inf_sided_blom"] = None
N = D[D.minority.notna()].copy()
N["Exm"] = N.E * N.minority
res["N4_own"] = fit(N, ["E", "Exm", "z_loglen", "z_fl"])
N["Sxm"] = N.sided * N.minority
res["N4_sided_share"] = fit(N, ["sided", "Sxm", "z_loglen", "z_fl"])
res["N4_rows"] = int(len(N))
res["N4_minority_rater_rounds"] = int(N[N.minority == 1].rr.nunique())
res["N4_majority_rater_rounds"] = int(N[N.minority == 0].rr.nunique())
# informative rounds within N4 sample
inf = S.groupby("round_id").E.agg(lambda s: s.max() > s.min())
ir = set(inf[inf].index)
res["N4_informative_rounds"] = int(N[N.round_id.isin(ir)].round_id.nunique())
res["N4_informative_launches"] = int(N[N.round_id.isin(ir)].launch_id.nunique())
res["N4_informative_minority_rater_rounds"] = int(N[N.round_id.isin(ir) & (N.minority == 1)].rr.nunique())
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
