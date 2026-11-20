"""Red-team independent refit of A2 (FR s7) from the raw inputs, without importing common.py or a2_within_round.py.
Inputs (read-only): pilots/T3_1/all_groups.jsonl (ranks, candidates), pilots/T3_1/pilot_groups.jsonl (dev launches),
analysis/scores/a2_scores_v2.jsonl (scorer-1 E), analysis/scores/a2_extractions_v2.jsonl (crux sides),
gate1/step2_private/rounds__20261116T015355Z.csv (Hsplit per round; read only after the gate was recorded).
Writes analysis/redteam/rt_refit.json.  Usage: python -I rt_refit.py"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parents[2]
PILOT = P.parent / "pilots" / "T3_1"
OUT = Path(__file__).resolve().parent / "rt_refit.json"

WORD = re.compile(r"[A-Za-z0-9']+")


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
    out = np.empty(len(v))
    for i, x in enumerate(v):
        out[i] = (v < x).sum() + ((v == x).sum() + 1) / 2.0
    return out


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
s2 = pd.read_csv(P / "gate1" / "step2_private" / "rounds__20261116T015355Z.csv")
hs = dict(zip(s2.round_id, s2.hsplit))

res = {}
# ---------------------------------------------------------------- sets and counts
rid_launch = {}
for g in groups:
    rid_launch.setdefault(g["round_id"], set()).add(g["launch_id"])
res["round_id_unique_across_launches"] = all(len(v) == 1 for v in rid_launch.values())
res["n_rounds_all"] = len(groups)
res["n_launches_all"] = len({g["launch_id"] for g in groups})
res["n_dev_launch_ids_in_file"] = len(dev)
res["n_dev_launches_present"] = len({g["launch_id"] for g in groups} & dev)
conf = [g for g in groups if g["launch_id"] not in dev]
res["n_rounds_conf"] = len(conf)
res["n_launches_conf"] = len({g["launch_id"] for g in conf})
res["n_rater_rows_all"] = sum(len(g["raters"]) for g in groups)
res["any_minus1_rank"] = any(-1 in r["ranks"] for g in groups for r in g["raters"])
res["raters_not_opinion_authors"] = sum(1 for g in groups for r in g["raters"] if r["pid"] not in g["opinions"])

drop = {"zero_crux": 0, "extract_fail": 0, "all4_missing": 0, "partial_missing": 0}
rows, stm = [], []
for g in conf:
    rid = g["round_id"]
    x = ex.get(rid)
    Es = []
    for j in range(4):
        s = sc.get((rid, j))
        Es.append(None if (s is None or s["E"] is None) else float(s["E"]))
    if x is None or not x.get("ok"):
        drop["extract_fail"] += 1
        continue
    if x["n_cruxes"] == 0:
        drop["zero_crux"] += 1
        continue
    nmiss = sum(e is None for e in Es)
    if nmiss == 4:
        drop["all4_missing"] += 1
        continue
    if nmiss:
        drop["partial_missing"] += 1
        continue
    labs = [sc[(rid, j)]["labels"] for j in range(4)]
    for j, c in enumerate(g["candidates"]):
        nw = len(WORD.findall(c))
        stm.append(dict(round_id=rid, cand=j, launch_id=g["launch_id"], E=Es[j], nw=nw, loglen=np.log(nw), fl=flesch(c),
                        anyvis=float(any(lb == "VISIBLE" for lb in labs[j])), nsided=sum(lb == "SIDED" for lb in labs[j]) / len(labs[j]),
                        hsplit=hs.get(rid, np.nan), ncrux=x["n_cruxes"]))
    for r in g["raters"]:
        if len(set(r["ranks"])) == 1:
            continue
        m = midrank(r["ranks"])
        for j in range(4):
            rows.append(dict(round_id=rid, rater=r["pid"], cand=j, y=(4 - m[j]) / 3.0))
res["drops_conf"] = drop
res["n_rounds_dropped_conf"] = sum(drop.values())
S = pd.DataFrame(stm)
R = pd.DataFrame(rows)
for c in ("loglen", "fl"):
    S["z_" + c] = (S[c] - S[c].mean()) / S[c].std(ddof=0)
D = R.merge(S, on=["round_id", "cand"], how="left")
D["rr"] = D["round_id"] + "|" + D["rater"]
res["n_rows"] = int(len(D))
res["n_rounds_fit"] = int(D.round_id.nunique())
res["n_launches_fit"] = int(D.launch_id.nunique())
inf = S.groupby("round_id")["E"].agg(lambda s: s.max() > s.min())
res["R_inf"] = int(inf.sum())
res["K_inf"] = int(S[S.round_id.isin(inf[inf].index)].launch_id.nunique())


def fit(d, cols, B=0, seed=1):
    g = d.groupby("rr")
    y = (d["y"] - g["y"].transform("mean")).to_numpy()
    X = np.column_stack([(d[c] - g[c].transform("mean")).to_numpy(float) for c in cols])
    XtX = X.T @ X
    b = np.linalg.solve(XtX, X.T @ y)
    e = y - X @ b
    codes, uniq = pd.factorize(d["launch_id"])
    G = len(uniq)
    sc_ = np.zeros((G, X.shape[1]))
    np.add.at(sc_, codes, X * e[:, None])
    Ai = np.linalg.inv(XtX)
    V = Ai @ (sc_.T @ sc_) @ Ai * G / (G - 1)
    se = np.sqrt(np.diag(V))
    out = {c: {"est": float(b[k]), "se_cr1": float(se[k])} for k, c in enumerate(cols)}
    if B:
        # own wild cluster bootstrap-t (Rademacher, unrestricted), different RNG than the record
        rng = np.random.default_rng(seed)
        Xc = [None] * G
        order = np.argsort(codes, kind="stable")
        bounds = np.flatnonzero(np.diff(codes[order])) + 1
        XtXc = np.zeros((G, X.shape[1], X.shape[1]))
        for ch in np.split(order, bounds):
            XtXc[codes[ch[0]]] = X[ch].T @ X[ch]
        ts = np.empty((B, X.shape[1]))
        for bb in range(B):
            w = rng.choice([-1.0, 1.0], size=G)
            delta = Ai @ (w @ sc_)
            gsc = w[:, None] * sc_ - np.einsum("cpq,q->cp", XtXc, delta)
            Vb = Ai @ (gsc.T @ gsc) @ Ai * G / (G - 1)
            ts[bb] = delta / np.sqrt(np.diag(Vb))
        for k, c in enumerate(cols):
            qlo, qhi = np.percentile(ts[:, k], [2.5, 97.5])
            out[c]["wild_lo"] = float(b[k] - se[k] * qhi)
            out[c]["wild_hi"] = float(b[k] - se[k] * qlo)
            out[c]["wild_p"] = float(((np.abs(ts[:, k]) >= abs(b[k] / se[k])).sum() + 1) / (B + 1))
    out["_n_clusters"] = G
    out["_n_rows"] = int(len(d))
    return out


res["A2_primary_own"] = fit(D, ["E", "z_loglen", "z_fl"], B=4000, seed=777)
res["A2_uncontrolled_own"] = fit(D, ["E"])
res["A2h_own"] = fit(D, ["E", "z_loglen"])

# --- functional form of the length control (exploratory)
D["z2"] = D["z_loglen"] ** 2
D["z3"] = D["z_loglen"] ** 3
D["zw"] = (D["nw"] - S["nw"].mean()) / S["nw"].std(ddof=0)
res["X_len_cubic"] = fit(D, ["E", "z_loglen", "z2", "z3", "z_fl"])
res["X_len_rawwords"] = fit(D, ["E", "zw", "z_fl"])
res["X_len_raw_and_log"] = fit(D, ["E", "zw", "z_loglen", "z_fl"])
qs = np.quantile(S["nw"], np.linspace(0, 1, 11))
D["lbin"] = np.clip(np.searchsorted(qs, D["nw"], side="right") - 1, 0, 9)
bins = []
for k in range(1, 10):
    D[f"lb{k}"] = (D["lbin"] == k).astype(float)
    bins.append(f"lb{k}")
res["X_len_decile_dummies"] = fit(D, ["E"] + bins + ["z_fl"])
# within-round length rank (which candidate is longest)
D["lenrank"] = D.groupby("rr")["nw"].rank(method="average")
res["X_len_withinround_rank"] = fit(D, ["E", "lenrank", "z_fl"])
res["X_len_rank_and_log"] = fit(D, ["E", "lenrank", "z_loglen", "z_fl"])

# --- E decomposition: anyVISIBLE indicator
res["X_anyvisible_instead_of_E"] = fit(D, ["anyvis", "z_loglen", "z_fl"])

# --- by step-2 Hsplit (does E predict ranks in groups where participants did not split?)
for h in (0, 1):
    d = D[D.hsplit == h]
    res[f"X_hsplit{h}"] = fit(d, ["E", "z_loglen", "z_fl"]) if len(d) else None
    res[f"X_hsplit{h}_informative_rounds"] = int(S[(S.hsplit == h) & S.round_id.isin(inf[inf].index)].round_id.nunique())
    res[f"X_hsplit{h}_informative_launches"] = int(S[(S.hsplit == h) & S.round_id.isin(inf[inf].index)].launch_id.nunique())
D["Exh"] = D["E"] * D["hsplit"]
res["X_E_x_hsplit"] = fit(D[D.hsplit.notna()], ["E", "Exh", "z_loglen", "z_fl"])

# --- descriptives on informative rounds
Si = S[S.round_id.isin(inf[inf].index)].copy()
Si["dE"] = Si["E"] - Si.groupby("round_id")["E"].transform("mean")
Si["dL"] = Si["loglen"] - Si.groupby("round_id")["loglen"].transform("mean")
Si["dF"] = Si["fl"] - Si.groupby("round_id")["fl"].transform("mean")
res["inf_within_corr_E_loglen"] = float(np.corrcoef(Si.dE, Si.dL)[0, 1])
res["inf_within_corr_E_flesch"] = float(np.corrcoef(Si.dE, Si.dF)[0, 1])
res["E_values_informative"] = Si["E"].round(4).value_counts().sort_index().to_dict()
res["share_rows_E_lt1_in_inf"] = float((Si.E < 1).mean())

# --- leave-one-launch-out influence on beta_E (exact refits on informative launches only)
infl = sorted(Si.launch_id.unique())
loo = []
for L in infl:
    loo.append(fit(D[D.launch_id != L], ["E", "z_loglen", "z_fl"])["E"]["est"])
loo = np.array(loo)
res["loo_min"], res["loo_max"] = float(loo.min()), float(loo.max())
res["loo_n_launches"] = len(infl)
# drop the k most influential launches (by drop in beta)
order = np.argsort(-(res["A2_primary_own"]["E"]["est"] - loo))
for k in (1, 3, 5, 10):
    drop_ids = [infl[i] for i in order[:k]]
    f = fit(D[~D.launch_id.isin(drop_ids)], ["E", "z_loglen", "z_fl"])["E"]
    res[f"drop_top{k}_influential"] = f

# --- group-level unit (FR s11 shape) for reference
Gm = D.groupby(["round_id", "cand"]).agg(y=("y", "mean"), E=("E", "first"), z_loglen=("z_loglen", "first"),
                                          z_fl=("z_fl", "first"), launch_id=("launch_id", "first")).reset_index()
Gm["rr"] = Gm["round_id"]
res["X_group_unit"] = fit(Gm, ["E", "z_loglen", "z_fl"])

dup_rounds = {g["round_id"] for g in groups if len(set(g["cand_ids"])) < len(g["cand_ids"])}
res["X_excl_duplicate_candidate_rounds"] = fit(D[~D.round_id.isin(dup_rounds)], ["E", "z_loglen", "z_fl"])
res["n_dup_rounds_in_fit"] = int(D[D.round_id.isin(dup_rounds)].round_id.nunique())

OUT.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
print(json.dumps(res, indent=1, default=float))
