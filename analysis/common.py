"""Shared helpers for the T3-1 analysis scripts. Aligned to FROZEN_RULES.md (draft) - see ALIGNMENT.md.

Long-table schema (one row per rater x round x statement), all analysis scripts:
  launch_id (cluster), round_id, rater_id, cand, rank, E, log_len, flesch
  rank: numerical_ranks, 0 = best (FR s2; habermas_machine/social_choice/base_method.py:59-60)
  E: crux erasure score in [0,1], 1 = hides every crux (FR s4); NaN = missing / zero cruxes
  log_len: log(word count), words = [A-Za-z0-9']+ (raw; z-scored here, FR s7)
  flesch: Flesch Reading Ease per FR s7 (raw; z-scored here)
HARD RULE (BRIEF 3.3, FR 6.5): kind='real' is refused unless P/gate1/GATE1_RESULT.json exists.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parent.parent
A = P / "analysis"
GATE = P / "gate1"
PILOT = P.parent / "pilots" / "T3_1"

DEFAULTS = {
    "B": 10000,                # FR s7
    "seed": 20261119,          # FR s7 (A2); N1 20261120, A4 20261121, A3 20261122, N3 20261123, N4 20261124
    "alpha": 0.05,
    "interval": "wild",   # percentile | bca | wild; METHOD OF RECORD = wild cluster bootstrap-t (coverage_interval.json, ALIGNMENT.md)
    "unit": "rater",           # 'rater' (primary) or 'group' (FR s11 fallback)
    "predictor": "E",
    "controls": ["log_len", "flesch"],
    "control_labels": {"log_len": "length", "flesch": "clarity"},
    "min_informative_launches": 50,   # FR s7 interpretability floor (J)
    "min_launches_a3_n3": 30,         # FR s8 (J)
    "include_dev": False,             # FR s2 [R4]: confirmatory set = 721 non-development launches; True = sensitivity only (A2d)
}
KINDS = ("dummy", "synthetic", "shuffled", "real")
TIER_FILE = "A2_TIER_R4.json"         # FR 7.1 [R4]: tier of record, computed on the confirmatory set (the pre-R4 A2_TIER.json is kept, not read)
N_CONFIRMATORY_LAUNCHES = 721         # FR s2 [R4]: 871 - 150
N_ALL_LAUNCHES = 871


# ------------------------------------------------------------------ analysis set (FR s2 [R4], D31 edit 6 / D34 item 8)
_DEV = {}


def dev_launch_ids():
    """The 150 development launches (pilots/T3_1/pilot_groups.jsonl), or None if the file is absent.  Cached."""
    if "ids" not in _DEV:
        f = PILOT / "pilot_groups.jsonl"
        if f.exists():
            _DEV["ids"] = {json.loads(l)["launch_id"] for l in open(f, encoding="utf-8") if l.strip()}
            _DEV["sha"] = sha256_file(f)
        else:
            _DEV["ids"], _DEV["sha"] = None, None
    return _DEV["ids"]


def restrict_confirmatory(df, p, kind=None):
    """FR s2 [R4]: every confirmatory / family test runs on the eligible rounds of launches that are NOT development
    launches.  p['include_dev'] = True is the sensitivity version (A2d) and is labelled as such in the output.
    kind='real' refuses if the development-launch file is missing (the exclusion cannot be applied).
    Returns (df, info); info goes into the result JSON under 'analysis_set'."""
    n_in = int(df["launch_id"].nunique())
    if p.get("include_dev"):
        return df, {"set": "SENSITIVITY: including the development launches", "n_launches_in": n_in, "n_launches_out": n_in,
                    "n_dev_launches_dropped": 0, "dev_file_sha256": None}
    dev = dev_launch_ids()
    if dev is None:
        if kind == "real":
            sys.exit("REFUSED (FR s2 R4): pilots/T3_1/pilot_groups.jsonl missing; development launches cannot be excluded.")
        return df, {"set": "CONFIRMATORY (dev file absent: nothing to exclude; non-real kind only)", "n_launches_in": n_in,
                    "n_launches_out": n_in, "n_dev_launches_dropped": 0, "dev_file_sha256": None}
    out = df[~df["launch_id"].isin(dev)]
    n_out = int(out["launch_id"].nunique())
    return out, {"set": "CONFIRMATORY (development launches excluded)", "n_launches_in": n_in, "n_launches_out": n_out,
                 "n_dev_launches_dropped": n_in - n_out, "dev_file_sha256": _DEV["sha"]}


def load_params(path_or_json):
    p = json.loads(json.dumps(DEFAULTS))
    if path_or_json:
        s = str(path_or_json)
        p.update(json.loads(Path(s).read_text(encoding="utf-8")) if Path(s).exists() else json.loads(s))
    return p


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


GATE_TAG = {"tag": ""}   # set by check_kind; stamped on every output and RUNS.md row of a real run (METHODS_EVAL A3)
GATE_PASS = ("PASS",)
GATE_FAIL_PATH = ("FAIL", "NOT_YET_MEASURABLE")   # FR 12: after a FAIL, real runs are exploratory, unvalidated, appendix-only
# FR 6.R5 (R5): GATE1_RESULT.json with "rules": "R5" -> output stamp.  NOT_EVALUATED (or anything else) refuses.
R5_TAGS = {"VALIDATED_BOTH": "VALIDATED_R5_BOTH",
           "VALIDATED_HIDE_EVIDENCE": "VALIDATED_R5_HIDE_EVIDENCE_ONLY",
           "VALIDATED_PRESENCE": "HIDE_NOT_HUMAN_VALIDATED",
           "EXPLORATORY_UNVALIDATED": "EXPLORATORY_UNVALIDATED",
           "FAIL": "EXPLORATORY_UNVALIDATED"}


def check_kind(kind, gate_dir=None):
    """Lock for real ranks (BRIEF 3.3, FR 6.5, FR 7.1, FR 12).  Returns the tag stamped on outputs.
    real needs A2_TIER.json AND a readable GATE1_RESULT.json whose status is PASS (tag VALIDATED) or
    FAIL / NOT_YET_MEASURABLE (tag EXPLORATORY_UNVALIDATED).  Any other status (INCOMPLETE, NOT EVALUATED,
    missing, unparsable) refuses: FR 12 'labels incomplete -> no real-rank analysis is run'."""
    if kind not in KINDS:
        sys.exit(f"--kind must be one of {KINDS}")
    if kind != "real":
        GATE_TAG["tag"] = ""
        return ""
    gd = Path(gate_dir) if gate_dir else GATE
    if not (gd / TIER_FILE).exists():
        sys.exit(f"REFUSED (FR 7.1 R4): real-rank analysis needs P/gate1/{TIER_FILE} (a2_informativeness.py on the confirmatory set) first.")
    gp = gd / "GATE1_RESULT.json"
    if not gp.exists():
        sys.exit("REFUSED (BRIEF 3.3 / FR 6.5): real-rank analysis is locked until P/gate1/GATE1_RESULT.json exists.")
    try:
        g_rec = json.loads(gp.read_text(encoding="utf-8"))
    except Exception as ex:  # noqa: BLE001
        sys.exit(f"REFUSED (A3): GATE1_RESULT.json unreadable ({type(ex).__name__}); status cannot be checked.")
    if str(g_rec.get("rules", "")).upper() == "R5":     # FR 6.R5 (R5): statuses of gate1_r5.py; no DESIGN.json under R5
        st = str(g_rec.get("status", "")).strip().upper().replace(" ", "_")
        if st not in R5_TAGS:
            sys.exit(f"REFUSED (FR 6.R5): GATE1_RESULT.json R5 status {st!r} does not unblock real data (NOT_EVALUATED or unknown).")
        GATE_TAG["tag"] = R5_TAGS[st]
        return GATE_TAG["tag"]
    dp = gd / "DESIGN.json"     # FR 6.0 [R4]: every later step reads the design and refuses if it is missing or altered
    if not dp.exists():
        sys.exit("REFUSED (FR 6.0 R4): P/gate1/DESIGN.json missing.")
    sc = Path(str(dp) + ".sha256")
    if not sc.exists() or sc.read_text(encoding="utf-8").split()[0] != sha256_file(dp):
        sys.exit("REFUSED (FR 6.0 R4): DESIGN.json altered (sha256 sidecar mismatch).")
    try:
        design = json.loads(dp.read_text(encoding="utf-8")).get("design")
        st = str(json.loads(gp.read_text(encoding="utf-8")).get("status", "")).strip().upper().replace(" ", "_")
    except Exception as ex:  # noqa: BLE001
        sys.exit(f"REFUSED (A3): GATE1_RESULT.json or DESIGN.json unreadable ({type(ex).__name__}); status cannot be checked.")
    if st == "PROVISIONAL_PASS":   # FR 6.5 [R4]: single-labeler design only; every output is stamped PROVISIONAL
        if design != "single_labeler":
            sys.exit("REFUSED (FR 6.5 R4): PROVISIONAL_PASS exists only in the single-labeler design.")
        tag = "PROVISIONAL"
    elif st in GATE_PASS:
        tag = "VALIDATED"
    elif st in GATE_FAIL_PATH:
        tag = "EXPLORATORY_UNVALIDATED"
    else:
        sys.exit(f"REFUSED (A3 / FR 12): GATE1_RESULT.json status {st!r} is not PASS or FAIL/NOT_YET_MEASURABLE; no real-rank analysis.")
    GATE_TAG["tag"] = tag
    return tag


# ------------------------------------------------------------------ source-data check (METHODS_EVAL A1)
FROZEN_SRC_SHA = "7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4"   # FR s2
SRC_PARQUET = P.parent / "data" / "habermas_gcs" / "hm_all_candidate_comparisons.parquet"
FROZEN_COUNTS = {"n_rounds": 1960, "n_launches": 871, "n_rater_rows": 9501}               # FR s2


def table_counts(df):
    return {"n_rounds": int(df["round_id"].nunique()), "n_launches": int(df["launch_id"].nunique()),
            "n_rater_rows": int(len(df[["round_id", "rater_id"]].drop_duplicates()))}


def verify_source(kind, input_path, df=None):
    """FR s2: every real run re-checks the source parquet SHA-256 and stops on mismatch.
    Needs <input>.manifest.json = {source_parquet_sha256, table_sha256, build_analysis_set_counts{...},
    table_counts{...}}.  Checks: manifest source hash == FROZEN value (also present in FROZEN_RULES.md);
    the parquet on disk hashes to it; the table file hashes to table_sha256; build_analysis_set counts ==
    FROZEN counts; the table's own counts == manifest table_counts (when a rater-level df is given)."""
    if kind != "real":
        return
    p = Path(str(input_path))
    if str(input_path) == "HABERMAS_SHUFFLED" or not p.exists():
        sys.exit("REFUSED (A1): kind=real needs an input table file with a manifest.")
    fr = (P / "FROZEN_RULES.md")
    if fr.exists() and FROZEN_SRC_SHA not in fr.read_text(encoding="utf-8"):
        sys.exit("REFUSED (A1): FROZEN_SRC_SHA in common.py is not the value written in FROZEN_RULES.md.")
    mp = Path(str(p) + ".manifest.json")
    if not mp.exists():
        sys.exit(f"REFUSED (A1): manifest {mp.name} missing (source-data hash cannot be verified).")
    m = json.loads(mp.read_text(encoding="utf-8"))
    if m.get("source_parquet_sha256") != FROZEN_SRC_SHA:
        sys.exit("REFUSED (A1): manifest source_parquet_sha256 != FROZEN value.")
    if not SRC_PARQUET.exists():
        sys.exit(f"REFUSED (A1): source parquet {SRC_PARQUET} not found; hash cannot be re-checked.")
    if sha256_file(SRC_PARQUET) != FROZEN_SRC_SHA:
        sys.exit("REFUSED (A1): source parquet SHA-256 on disk != FROZEN value (FR s2: stop on mismatch).")
    if m.get("table_sha256") != sha256_file(p):
        sys.exit("REFUSED (A1): input table SHA-256 != manifest table_sha256.")
    if m.get("build_analysis_set_counts") != FROZEN_COUNTS:
        sys.exit("REFUSED (A1): build_analysis_set counts in manifest != FROZEN counts (FR s2).")
    if df is not None and m.get("table_counts") != table_counts(df):
        sys.exit("REFUSED (A1): table counts differ from manifest table_counts.")


# ------------------------------------------------------------------ outputs (METHODS_EVAL L3)
def utc_stamp():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def write_sidecar(path):
    path = Path(path)
    h = sha256_file(path)
    Path(str(path) + ".sha256").write_text(f"{h}  {path.name}\n", encoding="utf-8")
    return h


def write_new(path, text):
    """Exclusive create ('x'): raises FileExistsError instead of overwriting; adds the .sha256 sidecar."""
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return write_sidecar(path)


def write_result(out, res, script, kind, seed, srcs, note=""):
    """Writes <stem>__<utc><suffix> (never an existing path) + .sha256 sidecar, stamps the gate tag,
    appends the RUNS.md row (which carries the output sha256).  Returns the versioned path (str)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res["gate_tag"] = GATE_TAG["tag"] if kind == "real" else f"NOT_REAL({kind})"
    text = json.dumps(res, indent=1, default=float)
    while True:
        vp = out.with_name(f"{out.stem}__{utc_stamp()}{out.suffix}")
        try:
            write_new(vp, text)
            break
        except FileExistsError:
            continue
    import run_log
    run_log.log_run(script, kind, seed, srcs, str(vp), (f"[{res['gate_tag']}] " if kind == "real" else "") + note)
    return str(vp)


# ------------------------------------------------------------------ text features (FR s7)
WORD = re.compile(r"[A-Za-z0-9']+")


def n_words(t):
    return len(WORD.findall(t or ""))


def syllables(w):
    w = w.lower()
    n = len(re.findall(r"[aeiouy]+", w))
    if n > 1 and w.endswith("e") and not w.endswith("le"):
        n -= 1
    return max(n, 1)


def flesch(t):
    words = WORD.findall(t or "")
    nw = max(len(words), 1)
    sents = max(len([s for s in re.split(r"[.!?]+", t or "") if s.strip()]), 1)
    syl = sum(syllables(w) for w in words)
    return 206.835 - 1.015 * (nw / sents) - 84.6 * (syl / nw)


# ------------------------------------------------------------------ shuffle (FR 6.5)
def shuffle_ranks(df, seed=424242):
    """Within-rater shuffle: each rater's ranks permuted across the statements,
    random.Random(seed) (FR 6.5).  Order of processing: sorted (launch_id, round_id, rater_id)."""
    d = df.sort_values(["launch_id", "round_id", "rater_id", "cand"]).reset_index(drop=True)
    rng = random.Random(seed)
    r = d["rank"].to_numpy().copy()
    for idx in d.groupby(["round_id", "rater_id"], sort=True).indices.values():
        v = list(r[idx])
        rng.shuffle(v)
        r[idx] = v
    d["rank"] = r
    return d


def load_habermas_shuffled(shuffle_seed=424242):
    """Real Habermas statements/raters (pilot features.parquet + all_groups.jsonl) with rankings
    SHUFFLED in memory; the real rank vectors are never summarised.  E is a DUMMY text proxy
    1/(1+contestation markers per 100 words) in (0,1]; log_len and flesch are the FR definitions."""
    f = pd.read_parquet(PILOT / "features.parquet")
    txt = {}
    for line in open(PILOT / "all_groups.jsonl", encoding="utf-8"):
        g = json.loads(line)
        for j, c in enumerate(g["candidates"]):
            txt[(g["round_id"], j)] = (n_words(c), flesch(c))
    nl = [txt.get((r, c), (np.nan, np.nan)) for r, c in zip(f.round_id, f.cand)]
    d = pd.DataFrame({"launch_id": f.launch_id.values, "round_id": f.round_id.values, "rater_id": f.rater.values,
                      "cand": f.cand.values, "rank": f["rank"].values,
                      "E": 1.0 / (1.0 + f.markers.values),
                      "log_len": [np.log(a) if a and a > 0 else np.nan for a, _ in nl],
                      "flesch": [b for _, b in nl]}).dropna(subset=["log_len", "flesch"])
    return shuffle_ranks(d, shuffle_seed)


HAB_SOURCES = [PILOT / "features.parquet", PILOT / "all_groups.jsonl"]


def make_synth(n_launches=300, rounds_per_launch=2, raters=4, k=4, beta_E=0.0, beta_len=0.0,
               beta_flesch=0.0, E_len_corr=0.0, noise=1.0, seed=1, minority_beta=None, minority_frac=0.4):
    """Synthetic long table with planted effects on a latent utility
    u = beta_E*E + beta_len*zlen + beta_flesch*zflesch + noise*N(0,1), E in [0,1] raw.
    Within a launch the rounds share a launch-level shock to u (cluster dependence is real).
    minority_beta: if given, raters flagged minority use beta_E=minority_beta (column 'minority')."""
    rng = np.random.default_rng(seed)
    rows = []
    for g in range(n_launches):
        shock = 0.0
        for r in range(rounds_per_launch):
            rid = f"L{g}R{r}"
            ln = rng.normal(size=k)
            fl = rng.normal(size=k)
            e = 0.5 + 0.25 * (E_len_corr * ln + np.sqrt(1 - E_len_corr ** 2) * rng.normal(size=k))
            e = np.clip(e, 0, 1)
            for q in range(raters):
                mino = int(rng.random() < minority_frac)
                b = minority_beta if (minority_beta is not None and mino) else beta_E
                u = b * e + beta_len * ln + beta_flesch * fl + noise * rng.normal(size=k)
                rank = np.empty(k, dtype=int)
                rank[np.argsort(-u)] = np.arange(k)
                for j in range(k):
                    rows.append((f"L{g}", rid, f"{rid}q{q}", j, int(rank[j]), e[j], 5 + 0.3 * ln[j], 60 + 10 * fl[j], mino))
    return pd.DataFrame(rows, columns=["launch_id", "round_id", "rater_id", "cand", "rank", "E", "log_len", "flesch", "minority"])


def read_long(path, kind=None):
    """kind='real' triggers the A1 source-hash/manifest check (verify_source) and refuses HABERMAS_SHUFFLED."""
    p = str(path)
    if kind == "real":
        verify_source(kind, p)
    if p == "HABERMAS_SHUFFLED":
        return load_habermas_shuffled(), HAB_SOURCES
    df = pd.read_parquet(p) if p.endswith(".parquet") else pd.read_csv(p)
    if kind == "real":
        verify_source(kind, p, df)
    return df, [Path(p)]


# ------------------------------------------------------------------ outcome / design (FR s7)
def add_y(df, unit="rater"):
    """y = (k - midrank)/(k-1), 1 = best.  Raters whose ranks are all equal are dropped.
    unit='group': y averaged over raters per (round, statement) (FR s11 fallback)."""
    d = df.copy()
    g = d.groupby(["round_id", "rater_id"], sort=False)["rank"]
    d["_mid"] = g.rank(method="average")
    d["_k"] = g.transform("size")
    d["_nu"] = g.transform("nunique")
    n_tied = int(d.loc[d["_nu"] == 1].groupby(["round_id", "rater_id"]).ngroups)
    d = d[d["_nu"] > 1].copy()
    d["y"] = (d["_k"] - d["_mid"]) / (d["_k"] - 1)
    if unit == "group":
        agg = {c: "first" for c in d.columns if c not in ("y", "rater_id", "round_id", "cand")}
        agg["y"] = "mean"
        d = d.groupby(["round_id", "cand"], sort=False).agg(agg).reset_index()
        d["rater_id"] = "GROUP"
    return d.drop(columns=["_mid", "_k", "_nu"]), n_tied


def zscore(d, col):
    """z-score over all statements in the analysis set (unique round x cand) for statement-level
    columns; over all rows if the column varies by rater."""
    varies = (d.groupby(["round_id", "cand"])[col].nunique() > 1).any()
    base = d[col] if varies else d.drop_duplicates(["round_id", "cand"])[col]
    return (d[col] - base.mean()) / base.std(ddof=0)


def fe_demean(d, cols):
    g = d.groupby(["round_id", "rater_id"], sort=False)
    return {c: (d[c] - g[c].transform("mean")).to_numpy(float) for c in cols}


# ------------------------------------------------------------------ bootstrap
def cluster_codes(series):
    codes, uniq = pd.factorize(series)
    return codes, len(uniq)


def cluster_sums(X, y, codes, nc):
    p = X.shape[1]
    XtX = np.zeros((nc, p, p))
    Xty = np.zeros((nc, p))
    order = np.argsort(codes, kind="stable")
    bounds = np.flatnonzero(np.diff(codes[order])) + 1
    for chunk in np.split(order, bounds):
        Xc = X[chunk]
        XtX[codes[chunk[0]]] = Xc.T @ Xc
        Xty[codes[chunk[0]]] = Xc.T @ y[chunk]
    return XtX, Xty


def ols_cluster_boot(X, y, codes, nc, B, seed):
    """Returns est (p,), bs (B,p).  Cluster bootstrap, numpy default_rng(seed)."""
    XtX, Xty = cluster_sums(X, y, codes, nc)
    est = np.linalg.solve(XtX.sum(0), Xty.sum(0))
    rng = np.random.default_rng(seed)
    out = np.empty((B, X.shape[1]))
    step = 2000
    for s in range(0, B, step):
        cnt = rng.multinomial(nc, np.full(nc, 1.0 / nc), size=min(step, B - s)).astype(float)
        A_ = np.tensordot(cnt, XtX, axes=(1, 0))
        b_ = cnt @ Xty
        out[s:s + len(cnt)] = np.linalg.solve(A_, b_[..., None])[..., 0]
    return est, out


def ratio_cluster_boot(num_c, den_c, B, seed):
    nc = len(num_c)
    est = num_c.sum() / den_c.sum()
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    step = 2000
    for s in range(0, B, step):
        cnt = rng.multinomial(nc, np.full(nc, 1.0 / nc), size=min(step, B - s)).astype(float)
        out[s:s + len(cnt)] = (cnt @ num_c) / (cnt @ den_c)
    return est, out


def summarize(est, bs, alpha=0.05):
    """est scalar, bs (B,) -> dict with percentile CI and FR s7 bootstrap p."""
    bs = np.asarray(bs)
    lo, hi = np.percentile(bs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    B = len(bs)
    pv = 2 * min((bs <= 0).sum() + 1, (bs >= 0).sum() + 1) / (B + 1)
    return {"est": float(est), "lo": float(lo), "hi": float(hi), "se": float(bs.std(ddof=1)),
            "p_boot": float(min(pv, 1.0))}


def holm(pvals):
    """pvals: dict name -> p.  Returns name -> Holm-adjusted p (step-down)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, run = {}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, (m - i) * v)
        adj[k] = min(run, 1.0)
    return adj


# ------------------------------------------------------------------ interval methods (FR s7 interval check)
def _norm():
    from scipy.stats import norm
    return norm


def ci_percentile(est, bs, alpha):
    return np.percentile(bs, [100 * alpha / 2, 100 * (1 - alpha / 2)], axis=0)


def ci_bca(est, bs, XtX, Xty, alpha):
    """Cluster BCa: bootstrap replicates `bs` (B,p) are launch-cluster resamples; acceleration from the
    leave-one-cluster-out jackknife (exact for OLS via the sufficient statistics)."""
    nrm = _norm()
    B, p = bs.shape
    A_, b_ = XtX.sum(0), Xty.sum(0)
    jk = np.linalg.solve(A_[None] - XtX, (b_[None] - Xty)[..., None])[..., 0]  # (nc,p)
    d = jk.mean(0) - jk
    acc = (d ** 3).sum(0) / (6.0 * ((d ** 2).sum(0) ** 1.5))
    lo, hi = np.empty(p), np.empty(p)
    for k in range(p):
        frac = np.clip((bs[:, k] < est[k]).mean(), 0.5 / B, 1 - 0.5 / B)
        z0 = nrm.ppf(frac)
        out = []
        for za in (nrm.ppf(alpha / 2), nrm.ppf(1 - alpha / 2)):
            a1 = nrm.cdf(z0 + (z0 + za) / (1 - acc[k] * (z0 + za)))
            out.append(np.percentile(bs[:, k], 100 * np.clip(a1, 0, 1)))
        lo[k], hi[k] = out
    return lo, hi


def wild_cluster_t(XtX, Xty, B, seed, alpha):
    """Wild cluster bootstrap-t, Rademacher weights per cluster, unrestricted residuals.
    Returns est, se (CR1), lo, hi, tstar (B,p).  Interval: est - se*q(1-a/2), est - se*q(a/2) of t*."""
    nc, p = Xty.shape
    A_ = XtX.sum(0)
    Ai = np.linalg.inv(A_)
    est = Ai @ Xty.sum(0)
    s_c = Xty - np.einsum("cpq,q->cp", XtX, est)          # X_c' e_c
    cr1 = nc / (nc - 1.0)
    se = np.sqrt(np.diag(Ai @ (s_c.T @ s_c) @ Ai) * cr1)
    rng = np.random.default_rng(seed)
    ts = np.empty((B, p))
    step = 100
    for s in range(0, B, step):
        n = min(step, B - s)
        w = rng.choice([-1.0, 1.0], size=(n, nc))
        delta = (w @ s_c) @ Ai.T                           # b* - est
        g = w[:, :, None] * s_c[None] - np.einsum("cpq,bq->bcp", XtX, delta)
        meat = np.einsum("bcp,bcq->bpq", g, g)
        V = np.einsum("pi,bij,jq->bpq", Ai, meat, Ai.T) * cr1
        ts[s:s + n] = delta / np.sqrt(np.einsum("bkk->bk", V))
    q_lo, q_hi = np.percentile(ts, [100 * alpha / 2, 100 * (1 - alpha / 2)], axis=0)
    return est, se, est - se * q_hi, est - se * q_lo, ts


def ols_cluster_ci(X, y, codes, nc, B, seed, alpha=0.05, method="percentile"):
    """List (per coefficient) of dicts est/lo/hi/se/p_boot using the chosen interval method.
    p_boot: percentile/bca -> FR s7 formula on the bootstrap estimates; wild -> bootstrap-t
    p = (#{|t*| >= |t_obs|}+1)/(B+1)."""
    XtX, Xty = cluster_sums(X, y, codes, nc)
    if method == "wild":
        est, se, lo, hi, ts = wild_cluster_t(XtX, Xty, B, seed, alpha)
        tobs = est / se
        return [{"est": float(est[k]), "lo": float(lo[k]), "hi": float(hi[k]), "se": float(se[k]),
                 "p_boot": float(((np.abs(ts[:, k]) >= abs(tobs[k])).sum() + 1) / (B + 1))} for k in range(len(est))]
    est, bs = ols_cluster_boot(X, y, codes, nc, B, seed)
    if method == "bca":
        lo, hi = ci_bca(est, bs, XtX, Xty, alpha)
    elif method == "percentile":
        lo, hi = ci_percentile(est, bs, alpha)
    else:
        raise ValueError(method)
    out = []
    for k in range(len(est)):
        s = summarize(est[k], bs[:, k], alpha)
        s["lo"], s["hi"] = float(lo[k]), float(hi[k])
        out.append(s)
    return out


def mean_ci(values, codes, nc, B, seed, alpha=0.05, method="wild"):
    """Mean of per-round values with launch-cluster interval = intercept-only OLS, so every interval
    method of ols_cluster_ci applies (FR s7 R1: one method of record for all launch-bootstrap intervals)."""
    v = np.asarray(values, float)
    return ols_cluster_ci(np.ones((len(v), 1)), v, codes, nc, B, seed, alpha, method)[0]
