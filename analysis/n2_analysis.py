"""N2 analysis exactly as analysis/N2_ANALYSIS_SPEC.md (sha256 afada117..., Amendments 1-5) specifies.

EVERY output is EXPLORATORY (FROZEN_RULES 6.R5.7) and carries the gate tag HIDE_NOT_HUMAN_VALIDATED (GATE1_RESULT.json,
R5, VALIDATED_PRESENCE). Scorer = scorer 1 (qwen3.8-27b) for all 5 generators; A4 = none (Amendment 4). Results are split by
generator; qwen3.8-27b text is SELF-SCORED.

Pre-specified (spec section in brackets):
  manipulation check per generator [2]; C1, C2, C3, C4a, C4b per generator [3]; Holm family 1 = 5 contrasts x {gemma4-12b,
  qwen3.8-27b} (10 tests), family 2 = 5 contrasts x {ministral3-14b, phi4-14b, llama3.1-8b} (15 tests) [3, 10]; C5 baseline
  (descriptive) [3]; launch-cluster percentile bootstrap B=2000 seed 20261115 [4]; pooled mixed model (descriptive) with per-generator
  estimates beside it and the generator x contrast interaction [4, 10]; per-cell parse-failure, zero-crux, E distribution [4];
  missing / zero-crux drops counted, effective n [5]; flagged outputs with and without [5]; Wilcoxon for C3 [5]; with and without the
  development-launch rounds [5]; falsifiers [6]; MDE at effective n [7, 10]; length covariate log(words) centred within generator,
  unadjusted beside, over-cap rate, under-cap subset [9]; preamble covariate, preamble-exclusion sensitivity, preamble counts [11].
Implementation choices (the spec is silent; fixed here before any N2 score was read by this script's author):
  * Holm p-value = the FR s7 percentile-bootstrap p, 2*min(#{b<=0}+1, #{b>=0}+1)/(B+1), from the same launch resamples as the CI.
  * Holm is applied to the unadjusted and to the covariate-adjusted contrasts separately (both reported; neither preferred, spec 9/11).
  * Covariate adjustment of a paired contrast = intercept of the launch-clustered regression of the round-level difference d on the
    same linear combination of log(words) (centred within generator) and, if the generator has any preambled statement, of the
    preamble flag (FR N1's "intercept regression across rounds" form); the intercept is the contrast at equal length / preamble.
  * Manipulation check = ((SAT-COMMON + ACC-COMMON) - (SAT-DIS + ACC-DIS)) / 2 per round (same sign as the spec's sum form).
  * Section-6 system effect = ((SAT-COMMON - ACC-COMMON) + (SAT-DIS - ACC-DIS)) / 2 per round.
  * "flagged" = think-tag leak, refusal/meta, preamble or truncation (n2_grid regexes); exclusion drops the round for that generator.
  * Pooled mixed model: cell x generator means (25 columns) + log(words)_c x generator + preamble term(s); random intercept launch,
    variance component round within launch (statsmodels MixedLM, REML); fallback launch-cluster-robust OLS if it fails / does not converge.
Exploratory-extra (NOT in the spec; kept separate under "exploratory_extra"): wild cluster bootstrap-t intervals (the FR s7 method of
record for A2-family intervals) for the primary unadjusted contrasts; crux-set identity check of N2 vs A2 extractions.

Run (from P):  <python with statsmodels> -I analysis/n2_analysis.py
"""
import csv
import datetime
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
import common as C   # noqa: E402
import n2_grid as G  # noqa: E402

SEED, B = 20261115, 2000
GENS = ["gemma4-12b", "qwen3.8-27b", "ministral3-14b", "phi4-14b", "llama3.1-8b"]
FAMILY = {"gemma4-12b": 1, "qwen3.8-27b": 1, "ministral3-14b": 2, "phi4-14b": 2, "llama3.1-8b": 2}
CELLS = ["SAT-COMMON", "SAT-DIS", "ACC-COMMON", "ACC-DIS", "NEU-COMMON"]
W = {   # weights over CELLS
    "C1_override (SAT-DIS - ACC-DIS)": [0, 1, 0, -1, 0],
    "C2_protection (SAT-COMMON - ACC-COMMON)": [1, 0, -1, 0, 0],
    "C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D))": [1, -1, -1, 1, 0],
    "C4a (SAT-COMMON - NEU-COMMON)": [1, 0, 0, 0, -1],
    "C4b (NEU-COMMON - ACC-COMMON)": [0, 0, -1, 0, 1],
}
MC = ("MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2", [.5, -.5, .5, -.5, 0])
SYS = ("SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2", [.5, .5, -.5, -.5, 0])
FAMILY_CONTRASTS = list(W)
ALL_W = dict(W, **{MC[0]: MC[1], SYS[0]: SYS[1]})
SCORES = HERE / "scores" / "n2_scores_v2.jsonl"
EXTR = HERE / "scorer_runs" / "n2" / "extractions.jsonl"
SUMMARY = HERE / "scorer_runs" / "n2" / "summary.json"
A2 = HERE / "scores" / "a2_scores_v2.jsonl"
A2X = HERE / "scores" / "a2_extractions_v2.jsonl"
GENS_F = {g: HERE / "n2_runs" / ("full_k1" if g in ("gemma4-12b", "qwen3.8-27b") else "full_ext") / f"gens_{g}.jsonl" for g in GENS}
OUT = HERE / "n2_results"
STAMP = "EXPLORATORY"
GATE_TAG = "HIDE_NOT_HUMAN_VALIDATED"
WORDING = {
    "stamp": "EXPLORATORY (FROZEN_RULES 6.R5.7; N2 spec Amendment 5). Gate tag HIDE_NOT_HUMAN_VALIDATED.",
    "n2_check": "the scorer's hide/show call was checked on 6 N2 statements only (descriptive); not checked on newly generated text beyond 6 items",
    "gate": "R5 status VALIDATED_PRESENCE: the scorer is validated for detecting whether a disagreement is present, not for detecting whether a "
            "statement hides it; the hiding measure E is not human-validated. Step-2 scope: the scorer's detection of disagreement was validated "
            "against participants' own pre-deliberation position ratings, for whether a group disagrees, not for whether a statement hides it.",
    "scope": "five open-weight instruction-tuned models (8B-27B); statements are not ranked by humans: N2 says what models write, not what people reward",
    "self_scored": "qwen3.8-27b text is scored by qwen3.8-27b (self-scored) everywhere",
    "a4": "A4 = none (Amendment 4): no A4 robustness read, no generator x scorer interaction, no A4 agreement / zero-crux tables",
    "null": "a CI that includes 0 is reported as 'CI includes 0; MDE (d_z, 80% power) at the effective n = ...', never as 'no effect' "
            "(the spec's 'not detected' is replaced because FR 6.R5.6 bars 'detected' for E-based results under VALIDATED_PRESENCE)",
    "between_generators": "between-generator differences in the level of E are descriptive only and never attributed to family, size or release date",
}


# ------------------------------------------------------------------ load
def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def load():
    sc = {r["job_id"]: r for r in jl(SCORES)}
    rows = []
    for g in GENS:
        for r in jl(GENS_F[g]):
            s = sc[r["job_id"]]
            t = r["text"].strip()
            nw = r["n_words"]
            if not t:
                status = "empty_text"
            elif not s["extract_ok"]:
                status = "extract_fail"
            elif s["n_cruxes"] == 0:
                status = "zero_crux"
            elif not s["label_ok"]:
                status = "label_parse_fail"
            else:
                status = "ok"
            rows.append(dict(job_id=r["job_id"], gen=g, launch_id=r["launch_id"], round_id=r["round_id"],
                             cell=f"{r['sys_prompt']}-{r['user_prompt']}", E=s["E"] if status == "ok" else np.nan, status=status,
                             n_cruxes=s["n_cruxes"], n_words=nw, logw=math.log(nw) if nw > 0 else np.nan,
                             overcap=nw > 150, truncated=bool(r["truncated"]),
                             preamble=bool(G.RE_PREAMBLE.search(t[:80])), think=bool(G.RE_THINK.search(t)),
                             refusal=bool(G.RE_REFUSAL.search(t))))
    df = pd.DataFrame(rows)
    assert len(df) == 6250 and df["job_id"].is_unique
    df["flag_any"] = df[["preamble", "think", "refusal", "truncated"]].any(axis=1)
    df["logw_c"] = df["logw"] - df.groupby("gen")["logw"].transform("mean")
    dev = C.dev_launch_ids()
    df["dev"] = df["launch_id"].isin(dev)
    return df


def hm_baseline(keys):
    by = {}
    for r in jl(A2):
        k = (r["launch_id"], r["round_id"])
        if k in keys and r.get("E") is not None:
            by.setdefault(k, []).append(r["E"])
    return {k: float(np.mean(v)) for k, v in by.items()}


# ------------------------------------------------------------------ statistics
def mde(n, alpha, power=0.8):
    from scipy import stats, optimize
    if n < 3:
        return None
    df_ = n - 1
    tc = stats.t.ppf(1 - alpha / 2, df_)

    def pw(d):
        nc = d * math.sqrt(n)
        lower = stats.nct.cdf(-tc, df_, nc)          # negligible far tail; scipy returns NaN there for large nc
        return float(np.nan_to_num(stats.nct.sf(tc, df_, nc))) + float(np.nan_to_num(lower)) - power
    return float(optimize.brentq(pw, 1e-4, 1.0))


def est_mean(d, launches, method="percentile"):
    codes, nc = C.cluster_codes(pd.Series(launches))
    r = C.mean_ci(np.asarray(d, float), codes, nc, B, SEED, 0.05, method)
    sd = float(np.std(d, ddof=1)) if len(d) > 1 else float("nan")
    return dict(est=r["est"], lo=r["lo"], hi=r["hi"], se=r["se"], p_boot=r["p_boot"], n_rounds=int(len(d)), n_launches=int(nc),
                d_z=(r["est"] / sd) if sd > 0 else None, ci_excludes_0=bool(r["lo"] > 0 or r["hi"] < 0))


def est_adjusted(d, dx, dpre, launches):
    cols = [np.ones(len(d)), dx]
    names = ["intercept", "d_logw_c"]
    if dpre is not None and np.any(dpre != 0):
        cols.append(dpre)
        names.append("d_preamble")
    X = np.column_stack(cols)
    y = np.asarray(d, float)
    codes, nc = C.cluster_codes(pd.Series(launches))
    # launch-cluster percentile bootstrap, same multinomial scheme and seed as common.ols_cluster_boot, but pinv so a resample in which
    # a sparse covariate (preamble difference) is all zero keeps the intercept (that covariate's slope is 0 there); such resamples are counted.
    XtX, Xty = C.cluster_sums(X, y, codes, nc)
    est = np.linalg.solve(XtX.sum(0), Xty.sum(0))
    rng = np.random.default_rng(SEED)
    bs = np.empty((B, X.shape[1]))
    rankdef = 0
    for s in range(0, B, 2000):
        cnt = rng.multinomial(nc, np.full(nc, 1.0 / nc), size=min(2000, B - s)).astype(float)
        A_ = np.tensordot(cnt, XtX, axes=(1, 0))
        b_ = cnt @ Xty
        for i in range(len(cnt)):
            if np.linalg.matrix_rank(A_[i]) < X.shape[1]:
                rankdef += 1
            bs[s + i] = np.linalg.pinv(A_[i]) @ b_[i]
    r = C.summarize(est[0], bs[:, 0])
    return dict(est=r["est"], lo=r["lo"], hi=r["hi"], se=r["se"], p_boot=r["p_boot"], n_rounds=int(len(d)), n_launches=int(nc),
                covariates=names[1:], slope_logw=float(est[1]), slope_preamble=float(est[2]) if len(est) > 2 else None,
                n_rows_nonzero_d_preamble=int(np.sum(dpre != 0)) if dpre is not None else 0,
                rank_deficient_resamples=rankdef, ci_excludes_0=bool(r["lo"] > 0 or r["hi"] < 0))


def wide(df, g, col):
    """rounds x CELLS for one generator; every generated round is kept (no NaN-dropping), so drops are counted explicitly."""
    s = df[df["gen"] == g].pivot(index=["launch_id", "round_id"], columns="cell", values=col)
    return s.reindex(columns=CELLS).sort_index()


# ------------------------------------------------------------------ per generator
def per_generator(df, g, hm):
    d = df[df["gen"] == g]
    E = wide(df, g, "E")
    LW = wide(df, g, "logw_c")
    PR = wide(df, g, "preamble").astype(float)
    FL = wide(df, g, "flag_any").astype(float)
    WD = wide(df, g, "n_words")
    st = wide(df, g, "status")
    n_rounds = len(E)
    complete = E.notna().all(axis=1)
    # missing / drop accounting (spec 5): a round is dropped in all cells for this generator if any cell lacks E
    reason = {}
    for k, row in st.iterrows():
        s = set(row.values)
        if s == {"ok"}:
            continue
        for lab in ("empty_text", "extract_fail", "zero_crux", "label_parse_fail"):
            if lab in s:
                reason[lab] = reason.get(lab, 0) + 1
                break
    has_pre = bool(d["preamble"].any())
    sets = {
        "primary": complete,
        "excl_preamble_rounds": complete & (PR.sum(axis=1) == 0),
        "excl_any_flagged_rounds": complete & (FL.sum(axis=1) == 0),
        "under_cap_all_cells_le_150w": complete & (WD.max(axis=1) <= 150),
        "excl_dev_launch_rounds": complete & ~pd.Series([k[0] in C.dev_launch_ids() for k in E.index], index=E.index),
    }
    out = dict(generator=g, self_scored=g == "qwen3.8-27b", holm_family=FAMILY[g], n_rounds_generated=int(n_rounds),
               n_rounds_complete=int(complete.sum()), rounds_dropped_by_reason=reason,
               preamble_any=has_pre, sets={})
    for sname, m in sets.items():
        Ei, Li, Pi = E[m].to_numpy(), LW[m].to_numpy(), PR[m].to_numpy()
        la = [k[0] for k in E[m].index]
        res = dict(n_rounds=int(m.sum()), n_launches=len(set(la)), rounds_dropped_vs_primary=int(complete.sum() - m.sum()),
                   identical_to_primary=bool((m == complete).all()), unadjusted={}, adjusted={})
        for name, w in ALL_W.items():
            w = np.asarray(w, float)
            dd = Ei @ w
            if len(dd) < 3:
                continue
            res["unadjusted"][name] = est_mean(dd, la)
            res["adjusted"][name] = est_adjusted(dd, Li @ w, (Pi @ w) if has_pre else None, la)
        if sname == "primary":
            c3 = Ei @ np.asarray(W["C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D))"], float)
            from scipy.stats import wilcoxon
            nz = c3[c3 != 0]
            wt = wilcoxon(c3) if len(nz) > 0 else None
            res["wilcoxon_C3"] = dict(statistic=float(wt.statistic) if wt else None, p=float(wt.pvalue) if wt else None,
                                      n_nonzero=int(len(nz)), n=int(len(c3)), note="round-level, not launch-clustered (spec 5 rank check)")
            res["cell_means_E"] = {c: float(np.mean(Ei[:, i])) for i, c in enumerate(CELLS)}
            # C5 baseline (descriptive): cell E minus mean E of the round's iteration-0 HM candidates (A2 v2 scores)
            keys = list(E[m].index)
            hb = np.array([hm.get(k, np.nan) for k in keys])
            ok = ~np.isnan(hb)
            res["C5_baseline_vs_HM_candidates"] = {
                c: dict(est_mean(Ei[ok, i] - hb[ok], [k[0] for k, o in zip(keys, ok) if o]), descriptive=True)
                for i, c in enumerate(CELLS)} if ok.sum() >= 3 else None
            res["C5_n_rounds_with_HM_baseline"] = int(ok.sum())
            # exploratory-extra: wild cluster bootstrap-t for the primary unadjusted contrasts
            res["exploratory_extra_wild_t"] = {name: est_mean(Ei @ np.asarray(w, float), la, "wild") for name, w in ALL_W.items()}
        out["sets"][sname] = res
    n_eff = out["n_rounds_complete"]
    m_fam = 10 if FAMILY[g] == 1 else 15
    out["mde_dz_80pct"] = dict(n_effective=n_eff, alpha_05=mde(n_eff, 0.05), alpha_holm_strictest=mde(n_eff, 0.05 / m_fam),
                               holm_strictest_alpha=0.05 / m_fam)
    mc = out["sets"]["primary"]["unadjusted"][MC[0]]
    out["manipulation_check_pass"] = bool(mc["lo"] > 0)
    out["manipulation_check_text"] = ("registers (MC > 0, launch-bootstrap 95% CI excludes 0)" if out["manipulation_check_pass"] else
                                      "instrument does not register the construct (MC CI does not lie above 0); nothing else about this "
                                      "generator is interpreted")
    pu = out["sets"]["primary"]["unadjusted"]
    out["falsifiers"] = {
        "H-N2 system effect (SYS) falsified": not (pu[SYS[0]]["lo"] > 0),
        "SAT-NEU within COMMON (C4a) falsified": not (pu["C4a (SAT-COMMON - NEU-COMMON)"]["lo"] > 0),
        "override reading (C1) falsified (CI includes 0)": not pu["C1_override (SAT-DIS - ACC-DIS)"]["ci_excludes_0"],
    }
    return out


def cell_table(df):
    rows = []
    for g in GENS:
        for c in CELLS:
            d = df[(df["gen"] == g) & (df["cell"] == c)]
            n = len(d)
            e = d["E"].dropna()
            rows.append(dict(stamp=STAMP, gate_tag=GATE_TAG, generator=g, self_scored=g == "qwen3.8-27b", cell=c, n=n,
                             n_with_E=len(e), parse_fail=int(d["status"].isin(["extract_fail", "label_parse_fail"]).sum()),
                             parse_fail_rate=round(d["status"].isin(["extract_fail", "label_parse_fail"]).mean(), 4),
                             extract_fail=int((d["status"] == "extract_fail").sum()), label_parse_fail=int((d["status"] == "label_parse_fail").sum()),
                             zero_crux=int((d["status"] == "zero_crux").sum()), zero_crux_rate=round((d["status"] == "zero_crux").mean(), 4),
                             empty_text=int((d["status"] == "empty_text").sum()),
                             mean_E=round(float(e.mean()), 4) if len(e) else None,
                             share_E_eq_0=round(float((e == 0).mean()), 4) if len(e) else None,
                             share_E_eq_1=round(float((e == 1).mean()), 4) if len(e) else None,
                             mean_words=round(float(d["n_words"].mean()), 1), overcap_n=int(d["overcap"].sum()),
                             overcap_rate=round(float(d["overcap"].mean()), 4), preamble_n=int(d["preamble"].sum()),
                             preamble_rate=round(float(d["preamble"].mean()), 4), truncated_n=int(d["truncated"].sum()),
                             think_leak_n=int(d["think"].sum()), refusal_meta_n=int(d["refusal"].sum())))
    return rows


def apply_holm(per):
    """Holm within family 1 (10) and family 2 (15), separately for unadjusted and adjusted primary contrasts."""
    res = {}
    for fam in (1, 2):
        for kind in ("unadjusted", "adjusted"):
            pv = {f"{g}|{c}": per[g]["sets"]["primary"][kind][c]["p_boot"] for g in GENS if FAMILY[g] == fam for c in FAMILY_CONTRASTS}
            adj = C.holm(pv)
            res[f"family{fam}_{kind}"] = dict(m=len(pv), adjusted_p=adj, reject_at_05=[k for k, v in adj.items() if v < 0.05])
            for k, v in adj.items():
                g, c = k.split("|", 1)
                per[g]["sets"]["primary"][kind][c]["p_holm"] = v
                per[g]["sets"]["primary"][kind][c]["holm_family"] = fam
    return res


# ------------------------------------------------------------------ pooled (descriptive only)
def pooled(df, per):
    comp = None
    for g in GENS:
        E = wide(df, g, "E")
        k = set(E.index[E.notna().all(axis=1)])
        comp = k if comp is None else comp & k
    comp = sorted(comp)
    out = dict(n_rounds_intersection=len(comp), n_launches=len({k[0] for k in comp}), descriptive_only=True)
    # paired: contrast averaged over the 5 generators per round
    Es = {g: wide(df, g, "E").loc[comp].to_numpy() for g in GENS}
    la = [k[0] for k in comp]
    out["paired_mean_over_generators_unadjusted"] = {
        name: est_mean(np.mean([Es[g] @ np.asarray(w, float) for g in GENS], axis=0), la) for name, w in ALL_W.items()}
    # mixed model
    sub = df[df.set_index(["launch_id", "round_id"]).index.isin(comp)].copy()
    sub["round_key"] = sub["launch_id"] + "|" + sub["round_id"]
    out["mixed_model_unadjusted"] = fit_mixed(sub, covariates=False)
    out["mixed_model_adjusted"] = fit_mixed(sub, covariates=True)
    return out


def fit_mixed(sub, covariates):
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    X = pd.DataFrame(index=sub.index)
    mcols = []
    for g in GENS:
        for c in CELLS:
            nm = f"m_{GENS.index(g)}_{CELLS.index(c)}"
            X[nm] = ((sub["gen"] == g) & (sub["cell"] == c)).astype(float)
            mcols.append(nm)
    cov = []
    if covariates:
        for g in GENS:
            nm = f"lw_{GENS.index(g)}"
            X[nm] = sub["logw_c"] * (sub["gen"] == g)
            cov.append(nm)
        flagged = [g for g in GENS if sub.loc[sub["gen"] == g, "preamble"].any()]
        if len(flagged) == 1:
            X["pre"] = sub["preamble"].astype(float)
            cov.append("pre")
        else:
            for g in flagged:
                nm = f"pre_{GENS.index(g)}"
                X[nm] = sub["preamble"].astype(float) * (sub["gen"] == g)
                cov.append(nm)
    X["E"] = sub["E"].values
    X["launch"] = sub["launch_id"].values
    X["round_key"] = sub["round_key"].values
    cols = mcols + cov
    formula = "E ~ 0 + " + " + ".join(cols)
    info = dict(covariates=cov, n_obs=int(len(X)), formula=formula)
    fe, V, fitted_by = None, None, None
    try:
        md = smf.mixedlm(formula, X, groups="launch", re_formula="1", vc_formula={"round": "0 + round_key"})   # string column = categorical in patsy
        r = md.fit(reml=True, method=["lbfgs", "bfgs", "cg"])      # tried in sequence until one converges
        if not r.converged:
            raise RuntimeError("MixedLM did not converge")
        fe = r.fe_params[cols].to_numpy()
        V = r.cov_params().loc[cols, cols].to_numpy()
        fitted_by = ("statsmodels MixedLM (REML; optimisers lbfgs, bfgs, cg tried in sequence): random intercept launch + variance "
                     "component round within launch")
        info.update(converged=True, var_launch=float(r.cov_re.iloc[0, 0]), var_round=float(r.vcomp[0]), scale_resid=float(r.scale))
    except Exception as ex:  # noqa: BLE001
        info.update(converged=False, mixed_error=f"{type(ex).__name__}: {str(ex)[:200]}")
        o = sm.OLS(X["E"].to_numpy(), X[cols].to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(X["launch"])[0]})
        fe, V = np.asarray(o.params), np.asarray(o.cov_params())
        fitted_by = "FALLBACK launch-cluster-robust OLS (MixedLM failed or did not converge; stated per spec 4)"
    info["fitted_by"] = fitted_by
    from scipy import stats
    p = len(cols)

    def L_for(g, w):
        L = np.zeros(p)
        for i, c in enumerate(CELLS):
            L[mcols.index(f"m_{GENS.index(g)}_{i}")] = w[i]
        return L
    res = {}
    for name, w in ALL_W.items():
        Ls = {g: L_for(g, w) for g in GENS}
        Lp = np.mean(list(Ls.values()), axis=0)
        e, se = float(Lp @ fe), float(math.sqrt(Lp @ V @ Lp))
        per_g = {g: dict(est=float(Ls[g] @ fe), se=float(math.sqrt(Ls[g] @ V @ Ls[g]))) for g in GENS}
        for g in GENS:
            per_g[g].update(lo=per_g[g]["est"] - 1.959964 * per_g[g]["se"], hi=per_g[g]["est"] + 1.959964 * per_g[g]["se"])
        D = np.array([Ls[g] - Ls[GENS[0]] for g in GENS[1:]])     # generator x contrast interaction: equal across generators?
        dv = D @ fe
        chi2 = float(dv @ np.linalg.solve(D @ V @ D.T, dv))
        res[name] = dict(pooled_mean_over_generators=dict(est=e, se=se, lo=e - 1.959964 * se, hi=e + 1.959964 * se,
                                                          p_wald=float(2 * stats.norm.sf(abs(e / se)))),
                         per_generator_model_based=per_g,
                         generator_x_contrast_interaction=dict(chi2=chi2, df=len(GENS) - 1, p=float(stats.chi2.sf(chi2, len(GENS) - 1))))
    if covariates:
        info["covariate_coefs"] = {c: dict(est=float(fe[cols.index(c)]), se=float(math.sqrt(V[cols.index(c), cols.index(c)]))) for c in cov}
    info["contrasts"] = res
    return info


# ------------------------------------------------------------------ extras / provenance
def extraction_identity():
    """exploratory-extra: are the N2 crux sets identical to A2's for the same round (harness-cache reuse)?"""
    a2 = {(r["launch_id"], r["round_id"]): r.get("cruxes") for r in jl(A2X)}
    n2 = {(r["launch_id"], r["round_id"]): r.get("cruxes") for r in jl(EXTR)}
    same = sum(1 for k, v in n2.items() if k in a2 and json.dumps(a2[k], sort_keys=True) == json.dumps(v, sort_keys=True))
    return dict(n2_rounds=len(n2), in_a2=sum(1 for k in n2 if k in a2), identical_crux_sets=same)


def cost():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    rows = [r for r in csv.reader(open(P / "ledger.csv", encoding="utf-8")) if len(r) > 1 and r[1].startswith("scorer N2 qwen3.8-27b v2")]
    return dict(session=s.get("session"), wall_s=s.get("wall_s"), calls=s.get("calls"), harness_stats=s.get("harness_stats"),
                ledger_rows=[dict(utc=r[0], job=r[1], estimate_usd=r[5], actual_usd=r[6], timeout_s=r[8]) for r in rows],
                scoring_complete=s.get("complete"), container_check={k: v for k, v in (s.get("container_check") or {}).items() if k != "stdout_tail"})


def fmt(x, nd=3):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def ci(r):
    return f"{fmt(r['est'])} [{fmt(r['lo'])}, {fmt(r['hi'])}]"


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return C.write_sidecar(path)


def estimates_rows(per):
    rows = []
    for g in GENS:
        for sname, s in per[g]["sets"].items():
            for kind in ("unadjusted", "adjusted"):
                for name, r in s[kind].items():
                    rows.append(dict(stamp=STAMP, gate_tag=GATE_TAG, generator=g, self_scored=g == "qwen3.8-27b", analysis_set=sname,
                                     adjustment=kind, contrast=name, in_holm_family=(name in FAMILY_CONTRASTS and sname == "primary"),
                                     holm_family=FAMILY[g] if name in FAMILY_CONTRASTS else "", est=r["est"], ci_lo=r["lo"], ci_hi=r["hi"],
                                     se=r["se"], p_boot=r["p_boot"], p_holm=r.get("p_holm", ""), d_z=r.get("d_z", ""),
                                     n_rounds=r["n_rounds"], n_launches=r["n_launches"], ci_excludes_0=r["ci_excludes_0"],
                                     identical_to_primary=s["identical_to_primary"]))
    return rows


def render_md(res, paths):
    L = []
    a = L.append
    a("# N2 results — EXPLORATORY (gate tag HIDE_NOT_HUMAN_VALIDATED)\n")
    a(f"Generated {res['utc']} by `analysis/n2_analysis.py` (sha256 `{res['provenance']['n2_analysis_sha256']}`). "
      f"Spec of record: `analysis/N2_ANALYSIS_SPEC.md` sha256 `{res['provenance']['spec_sha256']}` (Amendments 1–5). "
      f"Scores: `{res['provenance']['scores_file']}` sha256 `{res['provenance']['scores_sha256']}`.\n")
    a("**Status and wording (binding).**\n")
    for k in ("stamp", "gate", "n2_check", "scope", "self_scored", "a4", "null", "between_generators"):
        a(f"- {WORDING[k]}")
    a("\nEvery number below is EXPLORATORY. Intervals: launch-cluster percentile bootstrap, B = 2000, seed 20261115 (spec §4), unless marked "
      "model-based. `p_boot` = FR §7 bootstrap p; `p_holm` = Holm within family (family 1 = gemma4-12b, qwen3.8-27b, 10 tests; "
      "family 2 = ministral3-14b, phi4-14b, llama3.1-8b, 15 tests). Adjusted = log(words) centred within generator, plus preamble where the "
      "generator has any preambled statement (Amendments 1, 3); unadjusted and adjusted are both reported, neither preferred.\n")
    # scoring
    sc = res["scoring"]
    a("## 1. Scoring counts and parse failures (scorer 1 = qwen3.8-27b, frozen v2)\n")
    a("| generator | statements | with E | extraction fail | label parse fail | parse-failure rate | zero-crux | empty text |")
    a("|---|---|---|---|---|---|---|---|")
    for g in GENS:
        s = sc["per_generator"][g]
        a(f"| {g}{' (self-scored)' if g == 'qwen3.8-27b' else ''} | {s['n']} | {s['with_E']} | {s['extract_fail']} | {s['label_parse_fail']} | "
          f"{fmt(s['parse_failure_rate'], 4)} | {s['zero_crux']} | {s['empty_text']} |")
    a(f"\nTotal statements {sc['total']}; with E {sc['total_with_E']}. Crux sets identical to A2's for the same round "
      f"(exploratory-extra check): {res['exploratory_extra']['extraction_identity']}.\n")
    # cost
    c = res["cost"]
    a("## 2. Cost\n")
    a(f"- Session (harness list price): {c['session']}; wall {c['wall_s']} s; harness stats {c['harness_stats']}.")
    for r in c["ledger_rows"]:
        a(f"- ledger.csv: {r['utc']} | {r['job']} | estimate {r['estimate_usd']} | actual {r['actual_usd']} | timeout {r['timeout_s']}")
    a(f"- Container check after the run: {c['container_check']}\n")
    # per-cell
    a("## 3. Per generator × cell descriptives (all 6,250 statements)\n")
    a("| generator | cell | n | n with E | parse-fail rate | zero-crux rate | mean E | share E=0 | share E=1 | mean words | over-cap rate | preamble n (rate) | truncated | think leak | refusal/meta |")
    a("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in res["cells"]:
        a(f"| {r['generator']}{' (self)' if r['self_scored'] else ''} | {r['cell']} | {r['n']} | {r['n_with_E']} | {fmt(r['parse_fail_rate'], 4)} | "
          f"{fmt(r['zero_crux_rate'], 4)} | {fmt(r['mean_E'], 4)} | {fmt(r['share_E_eq_0'], 4)} | {fmt(r['share_E_eq_1'], 4)} | {r['mean_words']} | "
          f"{fmt(r['overcap_rate'], 4)} | {r['preamble_n']} ({fmt(r['preamble_rate'], 4)}) | {r['truncated_n']} | {r['think_leak_n']} | {r['refusal_meta_n']} |")
    # effective n
    a("\n## 4. Effective n, drops and MDE (spec §5, §7, Amendment 2)\n")
    a("| generator | rounds | complete rounds | dropped by reason | launches (primary) | MDE d_z (α 0.05) | MDE d_z (strictest Holm α) |")
    a("|---|---|---|---|---|---|---|")
    for g in GENS:
        p = res["per_generator"][g]
        a(f"| {g} | {p['n_rounds_generated']} | {p['n_rounds_complete']} | {p['rounds_dropped_by_reason']} | "
          f"{p['sets']['primary']['n_launches']} | {fmt(p['mde_dz_80pct']['alpha_05'])} | {fmt(p['mde_dz_80pct']['alpha_holm_strictest'])} "
          f"(α={fmt(p['mde_dz_80pct']['holm_strictest_alpha'], 4)}) |")
    # manipulation check
    a("\n## 5. Manipulation / instrument check (spec §2; outside the Holm families)\n")
    a("| generator | MC estimate [95% CI] | n rounds | verdict |")
    a("|---|---|---|---|")
    for g in GENS:
        p = res["per_generator"][g]
        r = p["sets"]["primary"]["unadjusted"][MC[0]]
        a(f"| {g} | {ci(r)} | {r['n_rounds']} | {p['manipulation_check_text']} |")
    a(f"\nNew generators failing the check: {res['manipulation_summary']['new_generators_failing']} "
      f"(rule: 2 or more of 3 failing means the paper may not say the instruction effect generalises across models). "
      f"Mahajan et al. (2611.05135) is credited for the agreement-vs-differences main effect.\n")
    # main table
    a("## 6. Pre-specified contrasts, primary analysis set (every estimate, including flat or null ones)\n")
    a("| generator | contrast | unadjusted est [95% CI] | p_boot | p_holm | d_z | adjusted est [95% CI] | p_boot | p_holm | n rounds | n launches |")
    a("|---|---|---|---|---|---|---|---|---|---|---|")
    for g in GENS:
        s = res["per_generator"][g]["sets"]["primary"]
        for name in list(W) + [SYS[0]]:
            u, d = s["unadjusted"][name], s["adjusted"][name]
            a(f"| {g}{' (self)' if g == 'qwen3.8-27b' else ''} | {name} | {ci(u)} | {fmt(u['p_boot'], 4)} | {fmt(u.get('p_holm'), 4) if 'p_holm' in u else '—'} | "
              f"{fmt(u['d_z'])} | {ci(d)} | {fmt(d['p_boot'], 4)} | {fmt(d.get('p_holm'), 4) if 'p_holm' in d else '—'} | {u['n_rounds']} | {u['n_launches']} |")
    a("\nSYS (spec §6 system effect) is a falsifier quantity, not in the Holm family. Contrast that is CI-excluding-0 in only one of the "
      "unadjusted / adjusted columns is labelled as such below (JSON `only_in_one_variant`).\n")
    a("### Falsifiers (spec §6), primary unadjusted\n")
    for g in GENS:
        a(f"- {g}: {res['per_generator'][g]['falsifiers']}")
    a("\n### Labels: contrasts whose CI excludes 0 in only one variant (adjusted vs unadjusted; with vs without preambled rounds)\n")
    for x in res["only_in_one_variant"]:
        a(f"- {x}")
    if not res["only_in_one_variant"]:
        a("- none")
    # covariates
    a("\n## 7. Covariates (adjusted primary): slopes of the round-level difference on Δlog(words) and Δpreamble\n")
    a("| generator | contrast | slope Δlog(words) | slope Δpreamble | rounds with Δpreamble ≠ 0 | bootstrap resamples (of 2000) with a rank-deficient design |")
    a("|---|---|---|---|---|---|")
    for g in GENS:
        s = res["per_generator"][g]["sets"]["primary"]["adjusted"]
        for name in list(W) + [MC[0], SYS[0]]:
            a(f"| {g} | {name} | {fmt(s[name]['slope_logw'])} | {fmt(s[name]['slope_preamble'])} | {s[name]['n_rows_nonzero_d_preamble']} | "
              f"{s[name]['rank_deficient_resamples']} |")
    a("\nLength is labelled a possible mediator, not a confound to remove (spec §5, §9). In a rank-deficient resample (no round with a "
      "nonzero preamble difference drawn) the pseudo-inverse sets that slope to 0 and keeps the intercept; the count is reported because "
      "the preamble adjustment is then carried by few rounds.\n")
    # sensitivity
    a("## 8. Sensitivity analyses (unadjusted and adjusted; every pre-specified contrast)\n")
    for sname in ("excl_preamble_rounds", "excl_any_flagged_rounds", "under_cap_all_cells_le_150w", "excl_dev_launch_rounds"):
        a(f"### {sname}\n")
        a("| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |")
        a("|---|---|---|---|---|---|")
        for g in GENS:
            s = res["per_generator"][g]["sets"][sname]
            for name in list(W) + [MC[0], SYS[0]]:
                if name in s["unadjusted"]:
                    a(f"| {g} | {s['n_rounds']} ({s['rounds_dropped_vs_primary']}) | {s['identical_to_primary']} | {name} | "
                      f"{ci(s['unadjusted'][name])} | {ci(s['adjusted'][name])} |")
        a("")
    a("### Rank-based check for C3 (Wilcoxon signed-rank, round level; spec §5)\n")
    a("| generator | statistic | p | n nonzero / n |")
    a("|---|---|---|---|")
    for g in GENS:
        w = res["per_generator"][g]["sets"]["primary"]["wilcoxon_C3"]
        a(f"| {g} | {fmt(w['statistic'], 1)} | {fmt(w['p'], 4)} | {w['n_nonzero']} / {w['n']} |")
    # C5
    a("\n## 9. C5 baseline (descriptive): cell E minus mean E of the round's iteration-0 HM candidates (A2 v2 scores)\n")
    a("| generator | cell | est [95% CI] | n rounds |")
    a("|---|---|---|---|")
    for g in GENS:
        c5 = res["per_generator"][g]["sets"]["primary"]["C5_baseline_vs_HM_candidates"] or {}
        for cell, r in c5.items():
            a(f"| {g} | {cell} | {ci(r)} | {r['n_rounds']} |")
    # pooled
    po = res["pooled_descriptive"]
    a(f"\n## 10. Pooled over 5 generators — DESCRIPTIVE ONLY, not tested (intersection: {po['n_rounds_intersection']} rounds, "
      f"{po['n_launches']} launches)\n")
    a("| contrast | paired mean over generators [95% CI] | mixed model unadjusted [95% model CI] | interaction χ²(4) p | mixed model adjusted [95% model CI] | interaction χ²(4) p |")
    a("|---|---|---|---|---|---|")
    for name in list(W) + [MC[0], SYS[0]]:
        mu, ma = po["mixed_model_unadjusted"]["contrasts"][name], po["mixed_model_adjusted"]["contrasts"][name]
        a(f"| {name} | {ci(po['paired_mean_over_generators_unadjusted'][name])} | {ci(mu['pooled_mean_over_generators'])} | "
          f"{fmt(mu['generator_x_contrast_interaction']['p'], 4)} | {ci(ma['pooled_mean_over_generators'])} | {fmt(ma['generator_x_contrast_interaction']['p'], 4)} |")
    a(f"\nMixed model fitted by: unadjusted — {po['mixed_model_unadjusted']['fitted_by']} (converged {po['mixed_model_unadjusted'].get('converged')}); "
      f"adjusted — {po['mixed_model_adjusted']['fitted_by']} (converged {po['mixed_model_adjusted'].get('converged')}). "
      f"Adjusted covariate coefficients: {po['mixed_model_adjusted'].get('covariate_coefs')}. Per-generator model-based estimates are in the JSON.\n")
    # extras
    a("## 11. Exploratory-extra (NOT in the spec; separate)\n")
    a("Wild cluster bootstrap-t (FR §7 method of record for the A2 family; B = 2000, seed 20261115) for the primary unadjusted contrasts:\n")
    a("| generator | contrast | est [95% CI] | p (bootstrap-t) |")
    a("|---|---|---|---|")
    for g in GENS:
        ex = res["per_generator"][g]["sets"]["primary"]["exploratory_extra_wild_t"]
        for name in list(W) + [MC[0], SYS[0]]:
            a(f"| {g} | {name} | {ci(ex[name])} | {fmt(ex[name]['p_boot'], 4)} |")
    a("\n## 12. Files\n")
    for k, v in paths.items():
        a(f"- {k}: `{v}`")
    a("\nImplementation choices where the spec is silent are listed in the docstring of `analysis/n2_analysis.py` and in the JSON "
      "`implementation_choices`.")
    return "\n".join(L) + "\n"


def make_dummy():
    """Synthetic scores for a pipeline test (planted SAT-COMMON effect); written under analysis/testout/n2_dummy only."""
    global SCORES, EXTR, SUMMARY, OUT
    d = HERE / "testout" / "n2_dummy"
    d.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    zero = set()
    rows = []
    for g in GENS:
        for r in jl(GENS_F[g]):
            k = r["round_id"]
            if k not in zero and rng.random() < 0.1 and len(zero) < 25:
                zero.add(k)
            n = int(rng.integers(1, 5))
            base = 0.3 + (0.25 if r["sys_prompt"] == "SAT" and r["user_prompt"] == "COMMON" else 0) - (0.2 if r["user_prompt"] == "DIS" else 0)
            hid = int(rng.binomial(n, min(max(base, 0), 1)))
            zc = k in zero
            lf = (not zc) and rng.random() < 0.01
            rows.append(dict(launch_id=r["launch_id"], round_id=k, cand=r["job_id"], job_id=r["job_id"], extract_ok=True,
                             n_cruxes=0 if zc else n, label_ok=not lf, E=None if (zc or lf) else hid / n))
    SCORES, EXTR, SUMMARY, OUT = d / "scores.jsonl", d / "extractions.jsonl", d / "summary.json", d / "out"
    with open(SCORES, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    EXTR.write_text("", encoding="utf-8")
    SUMMARY.write_text(json.dumps(dict(session=None, wall_s=0, calls=0, complete=True)), encoding="utf-8")


def main():
    dummy = "--dummy" in sys.argv
    if dummy:
        make_dummy()
    tag = C.check_kind("real")                      # refuses unless GATE1_RESULT.json records an R5 status that unblocks real data
    gate = G.assert_scoring_allowed()
    assert tag == GATE_TAG, tag
    assert C.sha256_file(G.SPEC) == "afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0", "spec hash changed"
    OUT.mkdir(exist_ok=True)
    df = load()
    keys = set(zip(df["launch_id"], df["round_id"]))
    hm = hm_baseline(keys)
    per = {g: per_generator(df, g, hm) for g in GENS}
    holm = apply_holm(per)
    only_one = []
    for g in GENS:
        s = per[g]["sets"]
        for name in list(W) + [MC[0], SYS[0]]:
            u = s["primary"]["unadjusted"][name]["ci_excludes_0"]
            d = s["primary"]["adjusted"][name]["ci_excludes_0"]
            if u != d:
                only_one.append(f"{g} | {name}: CI excludes 0 only in the {'unadjusted' if u else 'adjusted'} primary analysis")
            if not s["excl_preamble_rounds"]["identical_to_primary"]:
                ep = s["excl_preamble_rounds"]["unadjusted"][name]["ci_excludes_0"]
                if ep != u:
                    only_one.append(f"{g} | {name}: CI excludes 0 only {'with' if u else 'without'} the preambled rounds (unadjusted)")
    sc_rows = jl(SCORES)
    scoring = dict(total=len(sc_rows), total_with_E=int(df["E"].notna().sum()), per_generator={})
    for g in GENS:
        d = df[df["gen"] == g]
        scoring["per_generator"][g] = dict(
            n=len(d), with_E=int(d["E"].notna().sum()), extract_fail=int((d["status"] == "extract_fail").sum()),
            label_parse_fail=int((d["status"] == "label_parse_fail").sum()), zero_crux=int((d["status"] == "zero_crux").sum()),
            empty_text=int((d["status"] == "empty_text").sum()),
            parse_failure_rate=float(d["status"].isin(["extract_fail", "label_parse_fail"]).mean()))
    new_fail = [g for g in GENS if FAMILY[g] == 2 and not per[g]["manipulation_check_pass"]]
    import scipy
    import statsmodels
    res = dict(
        stamp=STAMP, output_tag=GATE_TAG, wording=WORDING, utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        gate=dict(rules=gate.get("rules"), status=gate.get("status")), scorer="qwen3.8-27b (scorer 1, frozen v2) for all 5 generators",
        a4="none (Amendment 4)", scoring=scoring, cells=cell_table(df), per_generator=per, holm=holm,
        manipulation_summary=dict(new_generators_failing=new_fail, generalisation_statement_allowed=len(new_fail) < 2),
        only_in_one_variant=only_one, pooled_descriptive=pooled(df, per), cost=cost(),
        exploratory_extra=dict(extraction_identity=extraction_identity(),
                               note="wild cluster bootstrap-t intervals are under per_generator.*.sets.primary.exploratory_extra_wild_t"),
        implementation_choices=__doc__.split("Implementation choices")[1].split("Exploratory-extra")[0].strip(),
        provenance=dict(spec_sha256=C.sha256_file(G.SPEC), n2_analysis_sha256=C.sha256_file(Path(__file__)),
                        n2_grid_sha256=C.sha256_file(HERE / "n2_grid.py"), common_sha256=C.sha256_file(HERE / "common.py"),
                        scores_file=str(SCORES.relative_to(P)), scores_sha256=C.sha256_file(SCORES),
                        a2_scores_sha256=C.sha256_file(A2), gens_sha256={g: C.sha256_file(p) for g, p in GENS_F.items()},
                        python=sys.version.split()[0], numpy=np.__version__, pandas=pd.__version__, scipy=scipy.__version__,
                        statsmodels=statsmodels.__version__, B=B, seed=SEED))
    paths = {}
    paths["per-cell table (CSV)"] = str((OUT / "n2_cells.csv").relative_to(P))
    write_csv(OUT / "n2_cells.csv", res["cells"])
    paths["all estimates (CSV)"] = str((OUT / "n2_estimates.csv").relative_to(P))
    write_csv(OUT / "n2_estimates.csv", estimates_rows(per))
    jp = C.write_result(OUT / "n2_results.json", res, __file__, "dummy" if dummy else "real", SEED,
                        [SCORES, A2, G.SPEC] + list(GENS_F.values()),
                        note=("DUMMY synthetic scores, pipeline test only; " if dummy else "") +
                        f"{STAMP} N2 analysis per spec afada117 (Amendments 1-5); scorer 1 only, A4 none; 5 generators; B={B}")
    paths["full results (JSON)"] = str(Path(jp).relative_to(P))
    md = OUT / "N2_RESULTS.md"
    md.write_text(render_md(res, paths), encoding="utf-8")
    h = C.write_sidecar(md)
    print("wrote", jp, "\n", md, h)
    for k in ("n2_cells.csv", "n2_estimates.csv"):
        print(k, C.sha256_file(OUT / k))


if __name__ == "__main__":
    main()
