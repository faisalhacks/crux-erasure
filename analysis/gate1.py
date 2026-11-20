"""Gate 1 [R4] (FR s5-s6.8; decisions D31, D34, D36, D37).  Steps (python -I gate1.py --step X --kind dummy|real):
  kappa     the agreement step of the design that applies (FR 6.2).  WRITE-ONCE <gate>/KAPPA.json (+ .sha256).
              single-labeler: self-consistency kappa, author pass 1 vs pass 2 on the 20 repeats, cut-off 0.60.  Needs
                author_pass2.csv that meets the one-hour rule; if missing or too early the kappa is NOT computed
                (status WAITING_PASS2, nothing written, the hash of every pass-2 file seen is logged).
              two-human: Cohen's kappa author pass 1 vs volunteer on the 50 items, cut-off 0.40; also lists the items
                to adjudicate (every pair whose four-token labels differ).
  selfcons  two-human design only: the author's self-consistency kappa, printed with CI, no rule (SELFCONS.json).
  validity  scorer validity (FR 6.4, 6.4a) -> <gate>/gate1_computed__<utc>.json (never overwritten).  Status:
              PASS / FAIL / INCOMPLETE and, single-labeler only, PROVISIONAL_PASS (BA lower bound > 0.5 while the
              self-consistency kappa is not recorded).  Also writes the headline rate (FR 6.7) and, in the single
              design, the descriptive table for a volunteer file that arrived after gate time (FR 6.0).
  headline  FR 6.7 only (needs labels, no scorer).
  n2check   FR 6.6: one-sided Fisher exact on the 12 N2 items -> N2_VALIDATED flag.
  llm       FR 6.8: LLM-annotator agreement (supplementary; always labelled LLM, never human).
The design switch (FR 6.0) is decided ONLY by the existence of labels/volunteer_pass1.csv at the first run in which
author_pass1.csv is complete; it is written once to <gate>/DESIGN.json with the sha256 and mtime of every file in labels/.
Never writes GATE1_RESULT.json or N2CHECK_RESULT.json (the planning room records them after an independent re-derivation).
Never writes into the labels directory.

Label files (FR s5): exactly item_id,label,main_disagreement,comment,pass_started_utc; label in {HIDES, SHOWS,
NO_DISAGREEMENT, UNSURE}, case and surrounding spaces ignored; author_pass1 50 rows, author_pass2 20, volunteer_pass1 50;
pass_started_utc = YYYY-MM-DDTHH:MMZ, one value per file.  item_key.csv: item_id,pass,kind,launch_id,round_id,cand,
generator,cell,dup_of with pass in {1, 2, vol}; kind original|n2; dup_of = the author's pass-1 id for pass 2 and vol rows.
Human positive = HIDES.  AI positive = E >= 0.5; E < 0.5 or zero cruxes negative; missing E = wrong prediction.
"""
import argparse
import datetime
import json
import sys
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402

TOK = {"HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE"}
COLS = ["item_id", "label", "main_disagreement", "comment", "pass_started_utc"]
B = 10000
SEED = 20261116           # FR 6.2, 6.4 (kappa, AC1, balanced accuracy)
SEED_LLM = 20261134       # FR 6.8
CUT_SELF, CUT_INTER = 0.60, 0.40
N_P1, N_P2, N_ORIG, N_N2 = 50, 20, 38, 12
GAP_MIN = 60
TS_FMT = "%Y-%m-%dT%H:%MZ"
SINGLE, TWO = "single_labeler", "two_human"
WORDING = {
    SINGLE: "validated against a single hypothesis-aware human annotator",
    TWO: ("validated against labels from two human annotators, a hypothesis-blind volunteer and the hypothesis-aware "
          "author, with disagreements adjudicated by the two together without sight of scores, rankings, model or condition"),
}
LLM_LABEL = "LLM annotator (gpt-oss-120b) given the same instructions; not a human label, not a second rater"
N2_LABEL = "scorer checked against human labels on 12 N2 statements pooled over five generators (2 or 3 per generator)"


# ------------------------------------------------------------------ small helpers
def cat3(t):
    return "HIDES" if t == "HIDES" else "UNSURE" if t == "UNSURE" else "NOT_HIDING"


def sha(p):
    return C.sha256_file(p) if p and Path(p).exists() else None


def iso_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_mtime(p):
    return datetime.datetime.fromtimestamp(Path(p).stat().st_mtime, datetime.timezone.utc)


def parse_ts(s):
    try:
        return datetime.datetime.strptime(str(s).strip(), TS_FMT).replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    except ValueError:
        return None


def read_label_file(path, ids, n_rows):
    """Returns (df or None, problems).  Nothing is filled, guessed or corrected (FR s5)."""
    probs = []
    name = Path(path).name
    d = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(d.columns) != COLS:
        return None, [f"{name}: columns {list(d.columns)} != {COLS}"]
    d["label"] = d["label"].str.strip().str.upper()
    if len(d) != n_rows:
        probs.append(f"{name}: {len(d)} rows, expected {n_rows}")
    ts = {x.strip() for x in d["pass_started_utc"]}
    if len(ts) != 1 or parse_ts(next(iter(ts))) is None:
        probs.append(f"{name}: pass_started_utc missing, unparseable or not the same on every row: {sorted(ts)[:3]}")
    for r in d.itertuples():
        if r.label not in TOK:
            probs.append(f"{name}: item {r.item_id}: invalid or blank label {r.label!r}")
        if r.item_id not in ids:
            probs.append(f"{name}: unknown item_id {r.item_id}")
    for i in d.item_id[d.item_id.duplicated()].unique():
        probs.append(f"{name}: repeated item_id {i}")
    for i in sorted(ids - set(d.item_id)):
        probs.append(f"{name}: item_id {i} (key) missing")
    return d, probs


def rows_sha(d, ids=None):
    import hashlib
    x = d if ids is None else d[d.item_id.isin(set(ids))]
    txt = "\n".join(f"{i}\t{l}" for i, l in sorted(zip(x.item_id, x.label)))
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ statistics
def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0:
        return float("nan")
    cats = np.unique(np.concatenate([a, b]))
    po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in cats)
    return float("nan") if pe >= 1 else float((po - pe) / (1 - pe))


def ac1(a, b, q=3):
    """Gwet's AC1, FR 6.2: (p_a - p_e)/(1 - p_e), p_e = (1/(q-1)) sum_k pi_k (1 - pi_k), q = 3 categories."""
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0:
        return float("nan")
    pa = float(np.mean(a == b))
    pe = sum(((np.mean(a == k) + np.mean(b == k)) / 2) * (1 - (np.mean(a == k) + np.mean(b == k)) / 2)
             for k in ("HIDES", "NOT_HIDING", "UNSURE")) / (q - 1)
    return float("nan") if pe >= 1 else float((pa - pe) / (1 - pe))


def agree_stats(a, b, seed):
    """kappa and AC1 on 3-category arrays, percentile bootstrap 95% CI over items, B = 10,000, default_rng(seed);
    undefined resamples are counted, not silently dropped (FR 6.2)."""
    a, b = np.asarray(a), np.asarray(b)
    n = len(a)
    out = {"n": int(n), "kappa": kappa(a, b), "ac1": ac1(a, b), "percent_agreement": float(np.mean(a == b)) if n else None,
           "B": B, "seed": seed}
    ks, cs, und = [], [], 0
    rng = np.random.default_rng(seed)
    for _ in range(B if n else 0):
        i = rng.integers(0, n, n)
        v, w = kappa(a[i], b[i]), ac1(a[i], b[i])
        if np.isnan(v):
            und += 1
        else:
            ks.append(v)
        if not np.isnan(w):
            cs.append(w)
    out["kappa_ci95"] = [float(x) for x in np.percentile(ks, [2.5, 97.5])] if ks else [float("nan")] * 2
    out["ac1_ci95"] = [float(x) for x in np.percentile(cs, [2.5, 97.5])] if cs else [float("nan")] * 2
    out["kappa_undefined_resamples"] = int(und)
    return out


def ba(y, yh):
    y, yh = np.asarray(y), np.asarray(yh)
    if (y == 1).sum() == 0 or (y == 0).sum() == 0:
        return 0.5  # FR 6.4: one-class resample scored as chance
    return 0.5 * ((yh[y == 1] == 1).mean() + (yh[y == 0] == 0).mean())


def ba_block(y, yh, seed=SEED):
    y, yh = np.asarray(y), np.asarray(yh)
    nP, nN = int((y == 1).sum()), int((y == 0).sum())
    if len(y) == 0 or nP == 0 or nN == 0:
        return {"n": int(len(y)), "n_human_pos": nP, "n_human_neg": nN, "ba": None, "lo": None, "hi": None}
    rng = np.random.default_rng(seed)
    bs = np.empty(B)
    for b in range(B):
        i = rng.integers(0, len(y), len(y))
        bs[b] = ba(y[i], yh[i])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"n": int(len(y)), "n_human_pos": nP, "n_human_neg": nN, "ba": float(ba(y, yh)), "lo": float(lo), "hi": float(hi)}


def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None, None]
    p_ = k / n
    den = 1 + z * z / n
    c = (p_ + z * z / (2 * n)) / den
    w = z * sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / den
    return [p_, c - w, c + w]


# ------------------------------------------------------------------ paths and context
def paths(a):
    ld, gd = Path(a.labels_dir), Path(a.gate_dir)
    return {"ld": ld, "gd": gd, "p1": ld / "author_pass1.csv", "p2": ld / "author_pass2.csv",
            "vol": ld / "volunteer_pass1.csv", "adj": Path(a.adj) if a.adj else ld / "ADJ.csv",
            "key": Path(a.item_key) if a.item_key else gd / "item_key.csv",
            "scores": Path(a.scores) if a.scores else gd / "scores.csv",
            "n2scores": Path(a.n2_scores) if a.n2_scores else gd / "n2check_scores.jsonl",
            "freeze": Path(a.freeze) if a.freeze else gd / "FREEZE.json",
            "llm": Path(a.llm_labels) if a.llm_labels else gd / "llm_annotator" / "llm_labels.csv"}


def load_ctx(a):
    P = paths(a)
    key = pd.read_csv(P["key"], dtype=str, keep_default_na=False)
    ctx = {"P": P, "key": key, "problems": []}
    k1 = key[key["pass"] == "1"]
    ctx["orig_ids"] = list(k1.loc[k1.kind == "original", "item_id"])
    ctx["n2_ids"] = list(k1.loc[k1.kind == "n2", "item_id"])
    if len(ctx["orig_ids"]) != N_ORIG or len(ctx["n2_ids"]) != N_N2:
        ctx["problems"].append(f"item_key: {len(ctx['orig_ids'])} original and {len(ctx['n2_ids'])} n2 pass-1 items, "
                               f"expected {N_ORIG} and {N_N2}")
    for nm, ps, n in (("A1", "1", N_P1), ("A2", "2", N_P2), ("V", "vol", N_P1)):
        f = P[{"A1": "p1", "A2": "p2", "V": "vol"}[nm]]
        ids = set(key.loc[key["pass"] == ps, "item_id"])
        if f.exists():
            ctx[nm], ctx[nm + "_probs"] = read_label_file(f, ids, n)
        else:
            ctx[nm], ctx[nm + "_probs"] = None, [f"{f.name}: file missing"]
    return ctx


def is_under(child, parent):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


# ------------------------------------------------------------------ design (FR 6.0)
def read_design(gd):
    dp = Path(gd) / "DESIGN.json"
    sc = Path(str(dp) + ".sha256")
    if not sc.exists() or sc.read_text(encoding="utf-8").split()[0] != C.sha256_file(dp):
        sys.exit("REFUSED (FR 6.0 R4): DESIGN.json does not match its .sha256 sidecar (altered or sidecar missing).")
    return json.loads(dp.read_text(encoding="utf-8"))


def get_design(ctx):
    """Returns the design dict, creating DESIGN.json at gate time (the first run with a complete author_pass1.csv).
    Returns None before gate time.  The only input to the choice is whether volunteer_pass1.csv exists (FR 6.0)."""
    P = ctx["P"]
    dp = P["gd"] / "DESIGN.json"
    if dp.exists():
        return read_design(P["gd"])
    if ctx["A1"] is None or ctx["A1_probs"]:
        return None
    if (P["gd"] / "KAPPA.json").exists() or list(P["gd"].glob("gate1_computed__*.json")):
        sys.exit("REFUSED (FR 6.0 R4): gate outputs exist but DESIGN.json is missing; the design cannot be re-decided.")
    P["gd"].mkdir(parents=True, exist_ok=True)
    files = {f.name: {"sha256": C.sha256_file(f), "mtime_utc": iso_mtime(f).strftime("%Y-%m-%dT%H:%M:%SZ")}
             for f in sorted(P["ld"].iterdir()) if f.is_file()}
    rec = {"design": TWO if P["vol"].exists() else SINGLE, "created_utc": iso_now(),
           "rule": "volunteer_pass1.csv exists at gate time -> two_human; otherwise single_labeler; nothing else decides (FR 6.0)",
           "files_in_labels_dir": files, "item_key_sha256": sha(P["key"]), "validation_wording": None}
    rec["validation_wording"] = WORDING[rec["design"]]
    C.write_new(dp, json.dumps(rec, indent=1))
    return rec


def integrity(ctx, design):
    """FR s5: first-pass labels are frozen on arrival.  Problems if a recorded file changed since gate time or since FREEZE.json."""
    P, pr = ctx["P"], []
    rec = design["files_in_labels_dir"]
    for nm in ("author_pass1.csv",) + (("volunteer_pass1.csv",) if design["design"] == TWO else ()):
        if rec.get(nm, {}).get("sha256") != sha(P["ld"] / nm):
            pr.append(f"STOP: {nm} changed since gate time (DESIGN.json)")
    if design.get("item_key_sha256") != sha(P["key"]):
        pr.append("STOP: item_key.csv changed since gate time (DESIGN.json)")
    if P["freeze"].exists():
        fz = json.loads(P["freeze"].read_text(encoding="utf-8"))
        want = fz.get("author_pass1_completed_sha256") or fz.get("author_pass1_sha256")
        if want and want != sha(P["p1"]):
            pr.append("STOP: author_pass1.csv differs from the hash recorded in FREEZE.json")
    return pr


def pass1_time(ctx):
    P = ctx["P"]
    if P["freeze"].exists():
        fz = json.loads(P["freeze"].read_text(encoding="utf-8"))
        t = parse_iso(fz.get("author_pass1_mtime_utc", ""))
        if t:
            return t, "FREEZE.json"
    return iso_mtime(P["p1"]), "file_mtime_fallback (no FREEZE.json)"


def pass2_rule(ctx):
    """FR 6.2 one-hour rule: (i) pass_started_utc of pass 2 and (ii) the mtime of author_pass2.csv are both >= 60 min after
    the pass-1 modification time.  Returns dict(ok, reasons, ...)."""
    P = ctx["P"]
    t1, src = pass1_time(ctx)
    gap = datetime.timedelta(minutes=GAP_MIN)
    ts = parse_ts(ctx["A2"]["pass_started_utc"].iloc[0])
    m2 = iso_mtime(P["p2"])
    reasons = []
    if ts is None or ts < t1 + gap:
        reasons.append(f"pass_started_utc {ts} is not >= {GAP_MIN} min after pass 1 ({t1.isoformat()})")
    if m2 < t1 + gap:
        reasons.append(f"author_pass2.csv mtime {m2.isoformat()} is not >= {GAP_MIN} min after pass 1 ({t1.isoformat()})")
    return {"ok": not reasons, "reasons": reasons, "pass1_mtime_utc": t1.isoformat(), "pass1_mtime_source": src,
            "pass2_started_utc": ts.isoformat() if ts else None, "pass2_mtime_utc": m2.isoformat()}


def log_pass2_seen(ctx, gd):
    f = ctx["P"]["p2"]
    if not f.exists():
        return
    h = C.sha256_file(f)
    lg = Path(gd) / "pass2_seen.jsonl"
    seen = {json.loads(l)["sha256"] for l in lg.read_text(encoding="utf-8").splitlines() if l.strip()} if lg.exists() else set()
    if h not in seen:
        with open(lg, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"utc": iso_now(), "sha256": h, "mtime_utc": iso_mtime(f).isoformat()}) + "\n")


def provisional_outputs_exist():
    return run_log.RUNS.exists() and "[PROVISIONAL]" in run_log.RUNS.read_text(encoding="utf-8")


# ------------------------------------------------------------------ labels of record (FR 6.3)
def lab_dict(d):
    return dict(zip(d.item_id, d.label))


def vol_labels_on_p1(ctx):
    """volunteer labels keyed by the author's pass-1 id (via item_key dup_of)."""
    key, V = ctx["key"], ctx["V"]
    m = dict(zip(key.loc[key["pass"] == "vol", "item_id"], key.loc[key["pass"] == "vol", "dup_of"]))
    return {m[i]: l for i, l in zip(V.item_id, V.label) if i in m}


def read_adj(ctx, need):
    P, pr = ctx["P"], []
    if not P["adj"].exists():
        return {}, [f"ADJ.csv: missing; {len(need)} items need an adjudicated label"] if need else []
    adj = pd.read_csv(P["adj"], dtype=str, keep_default_na=False)
    if "adj_label" not in adj:
        return {}, ["ADJ.csv: no adj_label column (final_label is not accepted, FR 6.3 R1)"]
    adj["lab"] = adj["adj_label"].str.strip().str.upper()
    known = set(ctx["A1"].item_id)
    for r in adj.itertuples():
        if r.lab not in TOK:
            pr.append(f"ADJ.csv: item {r.item_id}: invalid label {r.lab!r}")
        if r.item_id not in known:
            pr.append(f"ADJ.csv: unknown item_id {r.item_id}")
    for i in sorted(set(need) - set(adj.item_id)):
        pr.append(f"ADJ.csv: item {i} needs an adjudicated label")
    return dict(zip(adj.item_id, adj.lab)), pr


def records(ctx, design):
    """Label of record per pass-1 item (FR 6.3).  single: the author's pass-1 label, no ADJ.csv (reported, not read).
    two-human: equal labels -> that label; any difference -> ADJ.csv.  Returns (lab, to_adjudicate, problems, adj_present)."""
    A = lab_dict(ctx["A1"])
    if design["design"] == SINGLE:
        return dict(A), [], [], ctx["P"]["adj"].exists()
    if ctx["V"] is None or ctx["V_probs"]:
        return {}, [], ["volunteer_pass1.csv incomplete: " + "; ".join(ctx["V_probs"][:3])], ctx["P"]["adj"].exists()
    Vl = vol_labels_on_p1(ctx)
    need = [i for i in A if Vl.get(i) != A[i]]
    adj, pr = read_adj(ctx, need)
    lab = {i: (A[i] if i not in need else adj.get(i)) for i in A}
    return lab, need, pr, ctx["P"]["adj"].exists()


# ------------------------------------------------------------------ scores
def read_scores(files):
    rows = {}
    for f in files:
        f = Path(f)
        if not f.exists():
            continue
        if f.suffix == ".jsonl":
            for l in f.read_text(encoding="utf-8").splitlines():
                if l.strip():
                    j = json.loads(l)
                    rows[str(j["item_id"])] = ("" if j.get("E") is None else str(j["E"]), "" if j.get("n_cruxes") is None else str(j["n_cruxes"]))
        else:
            d = pd.read_csv(f, dtype=str, keep_default_na=False)
            for r in d.itertuples():
                rows[r.item_id] = (r.E.strip(), r.n_cruxes.strip())
    return rows


def ai_call(i, sc):
    """(binary or nan, missing flag, E or nan, n_cruxes or nan)"""
    if i not in sc:
        return (np.nan, True, np.nan, np.nan)
    e, n = sc[i]
    ncr = float(n) if n != "" else np.nan
    if n == "0":
        return (0, False, np.nan if e == "" else float(e), 0.0)
    if e == "":
        return (np.nan, True, np.nan, ncr)
    return (1 if float(e) >= 0.5 else 0, False, float(e), ncr)


def gate_frame(ids, lab, sc):
    g = pd.DataFrame({"item_id": ids, "adj": [lab.get(i) for i in ids]})
    r = [ai_call(i, sc) for i in ids]
    g["ai"], g["ai_missing"], g["E"], g["ncr"] = [x[0] for x in r], [x[1] for x in r], [x[2] for x in r], [x[3] for x in r]
    g["unsure"] = g["adj"] == "UNSURE"
    gs = g[~g.unsure].copy()
    gs["h"] = (gs["adj"] == "HIDES").astype(int)
    gs["pred"] = np.where(gs.ai_missing, 1 - gs.h, gs.ai.fillna(0)).astype(int)   # missing E = wrong prediction
    return g, gs


# ------------------------------------------------------------------ headline (FR 6.7)
def headline(ctx, design, lab, sc, llm=None, kappa_json=None):
    ids = ctx["orig_ids"]
    L = [lab[i] for i in ids]
    nH, nS, nN, nU = (L.count(x) for x in ("HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE"))
    nd = nH + nS + nN
    w = wilson(nH, nd)
    half = (w[2] - w[1]) / 2 if nd else None
    lower_b, upper_b = nH / len(ids), (nH + nU) / len(ids)
    out = {"n_originals": len(ids), "n_hides": nH, "n_shows": nS, "n_no_disagreement": nN, "n_unsure": nU,
           "unsure_items": [i for i in ids if lab[i] == "UNSURE"],
           "H": w[0], "H_wilson95": w[1:], "n_definite": nd,
           "bounds_unsure_as_not_hiding_and_as_hiding": [lower_b, upper_b],
           "rate_depends_on_unsure_items": bool(nd and (abs(lower_b - w[0]) > half or abs(upper_b - w[0]) > half)),
           "conditional_H_among_hides_or_shows": [nH, nH + nS] + wilson(nH, nH + nS),
           "share_no_disagreement_among_definite": (nN / nd if nd else None),
           "annotator_wording": WORDING[design["design"]],
           "sentence_requirements": "name n (38 or fewer), the interval, the annotator wording; call it an estimate from a small sample; "
                                    "no numeric comparison with other studies (FR 6.7)"}
    if design["design"] == TWO:
        Al, Vl = lab_dict(ctx["A1"]), vol_labels_on_p1(ctx)
        for nm, d in (("author_own_pass1", Al), ("volunteer_own_hypothesis_blind_annotator", Vl)):
            x = [d[i] for i in ids]
            n_ = sum(t in ("HIDES", "SHOWS", "NO_DISAGREEMENT") for t in x)
            out[nm] = {"n_definite": n_, "H": (x.count("HIDES") / n_ if n_ else None), "wilson95": wilson(x.count("HIDES"), n_)}
    if llm is not None:
        x = [llm.get(i) for i in ids]
        x = [t for t in x if t in TOK]
        n_ = sum(t in ("HIDES", "SHOWS", "NO_DISAGREEMENT") for t in x)
        out["llm_annotator_gpt_oss_120b_NOT_HUMAN"] = {"label": LLM_LABEL, "n_labelled": len(x), "n_definite": n_,
                                                       "H": (x.count("HIDES") / n_ if n_ else None), "wilson95": wilson(x.count("HIDES"), n_)}
    if sc:
        pr = [ai_call(i, sc) for i in ids]
        ok = [p_[0] for p_ in pr if not p_[1]]
        out["secondary_scorer1_rate_on_same_items"] = {
            "n_scored": len(ok), "n_missing_E": len(pr) - len(ok), "n_E_ge_0.5": int(sum(ok)),
            "rate_zero_crux_counts_as_not_hiding": (sum(ok) / len(ok) if ok else None), "wilson95": wilson(int(sum(ok)), len(ok)),
            "label": "SECONDARY: scorer-based rate, never alone in the abstract; whole-confirmatory-set prevalence is a separate analysis (FR 7.3)"}
    if design["design"] == SINGLE:
        out["state_stamp"] = "PROVISIONAL" if not (kappa_json and kappa_json.get("status") == "COMPUTED") else (
            "" if kappa_json["kappa"]["pass"] else "AGREEMENT_NOT_ESTABLISHED: not presented as the paper's headline (FR 6.7, s12)")
    else:
        out["state_stamp"] = "" if (kappa_json and kappa_json.get("status") == "COMPUTED" and kappa_json["kappa"]["pass"]) else (
            "AGREEMENT_NOT_ESTABLISHED: not presented as the paper's headline (FR 6.7, s12)")
    return out


# ------------------------------------------------------------------ common step plumbing
def read_kappa(gd):
    kp = Path(gd) / "KAPPA.json"
    if not kp.exists():
        return None
    sc_ = Path(str(kp) + ".sha256")
    if not sc_.exists() or sc_.read_text(encoding="utf-8").split()[0] != C.sha256_file(kp):
        return {"status": "TAMPERED"}
    return json.loads(kp.read_text(encoding="utf-8"))


def table4(a, b):
    t = pd.crosstab(pd.Series(a, name="first"), pd.Series(b, name="second")).reindex(
        index=sorted(TOK), columns=sorted(TOK), fill_value=0)
    return {r: {c: int(t.loc[r, c]) for c in t.columns} for r in t.index}


def agree_block(ids, la, lb, kinds, seed):
    """3-category kappa + AC1 + CIs on ids; also 4-cat kappa, both-definite kappa, 4x4 table, and the split by kind."""
    ra, rb = np.array([la[i] for i in ids]), np.array([lb[i] for i in ids])
    ca, cb = np.array([cat3(x) for x in ra]), np.array([cat3(x) for x in rb])
    both = np.array([(x != "UNSURE" and y != "UNSURE") for x, y in zip(ra, rb)])
    out = agree_stats(ca, cb, seed)
    out.update({"kappa_4cat": kappa(ra, rb), "kappa_both_definite": kappa(ra[both], rb[both]) if both.sum() > 1 else float("nan"),
                "n_both_definite": int(both.sum()), "unsure_first": int((ra == "UNSURE").sum()), "unsure_second": int((rb == "UNSURE").sum()),
                "table_4x4": table4(ra, rb)})
    kk = np.array([kinds[i] for i in ids])
    for k in ("original", "n2"):
        m = kk == k
        out["by_kind_" + k] = {"n": int(m.sum()), "kappa": kappa(ca[m], cb[m]), "ac1": ac1(ca[m], cb[m])}
    return out


def finish(a, res, name, version=True):
    """write the versioned result (never overwritten) and log the run"""
    gd = Path(a.gate_dir)
    if is_under(gd, a.labels_dir):
        sys.exit("REFUSED: output directory is inside the labels directory.")
    res["output_path"] = None
    P = paths(a)
    res["output_path"] = C.write_result(gd / name, res, __file__, a.kind, SEED,
                                        [x for x in (P["p1"], P["p2"], P["vol"], P["adj"], P["key"]) if x.exists()],
                                        f"gate1 {res['step']} status={res.get('status')}")
    return res


def early(a, res, ctx, why):
    res["status"] = "INCOMPLETE"
    res["problems"] = list(dict.fromkeys(res["problems"] + why))
    return finish(a, res, f"gate1_{res['step']}_incomplete.json")


# ------------------------------------------------------------------ step kappa (FR 6.2)
def step_kappa(a):
    ctx = load_ctx(a)
    P, gd = ctx["P"], ctx["P"]["gd"]
    gd.mkdir(parents=True, exist_ok=True)
    res = {"step": "kappa", "kind": a.kind, "problems": list(ctx["problems"]) + list(ctx["A1_probs"])}
    design = get_design(ctx)
    if design is None:
        res["status"] = "INCOMPLETE"
        res["note"] = "author_pass1.csv missing or incomplete: no gate time yet, DESIGN.json not written"
        run_log.log_run(__file__, a.kind, SEED, [P["p1"]], "", "gate1 kappa INCOMPLETE (pass 1)")
        print("gate1 kappa: INCOMPLETE", res["problems"][:3])
        return res
    d = design["design"]
    res["design"], res["validation_wording"] = d, design["validation_wording"]
    res["problems"] += integrity(ctx, design)
    kp0 = gd / "KAPPA.json"
    if kp0.exists():   # write-once: a COMPUTED kappa is never replaced; an INCOMPLETE one is archived (FR 6.2, G1)
        st0 = (read_kappa(gd) or {}).get("status")
        if st0 != "INCOMPLETE":
            sys.exit(f"REFUSED (G1): KAPPA.json already exists and is write-once (status {st0}); kappa is computed once.")
        st = C.utc_stamp()
        kp0.rename(gd / f"KAPPA.INCOMPLETE__{st}.json")
        sc0 = Path(str(kp0) + ".sha256")
        if sc0.exists():
            sc0.rename(gd / f"KAPPA.INCOMPLETE__{st}.json.sha256")
    rule = {"cut": CUT_SELF if d == SINGLE else CUT_INTER,
            "statistic": "self-consistency kappa (author pass 1 vs pass 2, 20 repeats)" if d == SINGLE else
                         "inter-rater kappa (author pass 1 vs hypothesis-blind volunteer, 50 items)"}
    kinds = dict(zip(ctx["key"].item_id, ctx["key"].kind))
    p2info = None
    if d == SINGLE:
        log_pass2_seen(ctx, gd)
        if ctx["A2"] is None:
            res.update({"status": "WAITING_PASS2", "reason": "author_pass2.csv missing; self-consistency not yet checked (not a pass)"})
            run_log.log_run(__file__, a.kind, SEED, [P["p1"], P["key"]], "", "gate1 kappa WAITING_PASS2 (missing)")
            print("gate1 kappa: WAITING_PASS2", res["reason"])
            return res
        if ctx["A2_probs"]:
            res["problems"] += ctx["A2_probs"]
        else:
            p2info = pass2_rule(ctx)
            if not p2info["ok"]:
                res.update({"status": "WAITING_PASS2", "reason": "; ".join(p2info["reasons"]), "pass2_rule": p2info,
                            "note": "kappa NOT computed (FR 6.2 one-hour rule); a replacement pass-2 file is accepted while KAPPA.json does not exist"})
                run_log.log_run(__file__, a.kind, SEED, [P["p1"], P["p2"], P["key"]], "", "gate1 kappa WAITING_PASS2 (one-hour rule)")
                print("gate1 kappa: WAITING_PASS2", res["reason"][:120])
                return res
    else:
        res["problems"] += ctx["V_probs"]
    if res["problems"]:
        res["status"] = "INCOMPLETE"
    elif d == SINGLE:
        m = dict(zip(ctx["key"].loc[ctx["key"]["pass"] == "2", "item_id"], ctx["key"].loc[ctx["key"]["pass"] == "2", "dup_of"]))
        l1, l2 = lab_dict(ctx["A1"]), lab_dict(ctx["A2"])
        ids2 = [i for i in ctx["A2"].item_id]
        orig_ids = [m[i] for i in ids2]
        A1l = {m[i]: l2[i] for i in ids2}   # second-pass label keyed by the pass-1 id it repeats
        blk = agree_block(orig_ids, l1, A1l, kinds, SEED)
        res["kappa"] = dict(blk, **rule, primary=blk["kappa"], primary_ci_info_only=blk["kappa_ci95"],
                            n_repeats=len(orig_ids), seed=SEED, pass_=bool(not np.isnan(blk["kappa"]) and blk["kappa"] >= CUT_SELF))
        res["kappa"]["pass"] = res["kappa"].pop("pass_")
        res["pass2_rule"] = p2info
        res["to_adjudicate"] = []
        res["provisional_real_rank_output_existed_when_pass2_arrived"] = provisional_outputs_exist()
        res["hashes"] = {"author_pass1": sha(P["p1"]), "author_pass2": sha(P["p2"]), "item_key": sha(P["key"])}
        res["row_hashes"] = {"author_pass1_repeated_rows": rows_sha(ctx["A1"], orig_ids), "author_pass1_all": rows_sha(ctx["A1"]),
                             "author_pass2_all": rows_sha(ctx["A2"])}
    else:
        ids = list(ctx["A1"].item_id)
        l1, Vl = lab_dict(ctx["A1"]), vol_labels_on_p1(ctx)
        blk = agree_block(ids, l1, Vl, kinds, SEED)
        res["kappa"] = dict(blk, **rule, primary=blk["kappa"], primary_ci_info_only=blk["kappa_ci95"], n_items=len(ids), seed=SEED)
        res["kappa"]["pass"] = bool(not np.isnan(blk["kappa"]) and blk["kappa"] >= CUT_INTER)
        res["kappa"]["moderate_wording_note"] = ("kappa in [0.40, 0.60): call it 'moderate agreement' and state that the brief's original 0.60 "
                                                 "would not have been met; 'substantial/good/high' only at >= 0.60 and never when the CI lower end < 0.40")
        res["to_adjudicate"] = [i for i in ids if Vl[i] != l1[i]]
        res["hashes"] = {"author_pass1": sha(P["p1"]), "volunteer_pass1": sha(P["vol"]), "item_key": sha(P["key"])}
        res["row_hashes"] = {"author_pass1_all": rows_sha(ctx["A1"]), "volunteer_pass1_all": rows_sha(ctx["V"])}
    res.setdefault("status", "COMPUTED")
    res["status"] = "INCOMPLETE" if res["problems"] else "COMPUTED"
    C.write_new(kp0, json.dumps(res, indent=1, default=float))   # exclusive create + sidecar
    run_log.log_run(__file__, a.kind, SEED, [P["p1"], P["p2"], P["vol"], P["key"]], str(kp0), f"gate1 kappa design={d} status={res['status']}")
    k = res.get("kappa", {})
    print("gate1 kappa:", res["status"], k.get("primary"), res["problems"][:3])
    return res


# ------------------------------------------------------------------ step selfcons (two-human only)
def step_selfcons(a):
    ctx = load_ctx(a)
    P, gd = ctx["P"], ctx["P"]["gd"]
    design = get_design(ctx)
    if design is None or design["design"] != TWO:
        sys.exit("selfcons applies to the two-human design only (single-labeler: it is the rule statistic, --step kappa).")
    sp = gd / "SELFCONS.json"
    if sp.exists():
        sys.exit("REFUSED: SELFCONS.json already exists (write-once).")
    res = {"step": "selfcons", "kind": a.kind, "design": TWO, "problems": integrity(ctx, design), "label": "no rule in this design (FR 6.2)"}
    log_pass2_seen(ctx, gd)
    if ctx["A2"] is None:
        res["status"] = "WAITING_PASS2"
        return res
    if ctx["A2_probs"]:
        res.update({"status": "INCOMPLETE", "problems": res["problems"] + ctx["A2_probs"]})
        return res
    r = pass2_rule(ctx)
    if not r["ok"]:
        res.update({"status": "WAITING_PASS2", "reason": "; ".join(r["reasons"]), "pass2_rule": r})
        return res
    m = dict(zip(ctx["key"].loc[ctx["key"]["pass"] == "2", "item_id"], ctx["key"].loc[ctx["key"]["pass"] == "2", "dup_of"]))
    l1, l2 = lab_dict(ctx["A1"]), lab_dict(ctx["A2"])
    ids = [m[i] for i in ctx["A2"].item_id]
    res["self_consistency"] = agree_block(ids, l1, {m[i]: l2[i] for i in ctx["A2"].item_id}, dict(zip(ctx["key"].item_id, ctx["key"].kind)), SEED)
    res["pass2_rule"] = r
    res["status"] = "COMPUTED"
    C.write_new(sp, json.dumps(res, indent=1, default=float))
    run_log.log_run(__file__, a.kind, SEED, [P["p1"], P["p2"]], str(sp), "gate1 selfcons (two-human, no rule)")
    return res


# ------------------------------------------------------------------ step validity (FR 6.4, 6.4a, 6.7)
def verify_kappa_hashes(K, ctx, design):
    P, pr = ctx["P"], []
    if K.get("status") == "TAMPERED":
        return ["G1: KAPPA.json does not match its .sha256 sidecar (edited or sidecar missing)"]
    now = {"author_pass1": sha(P["p1"]), "item_key": sha(P["key"])}
    if design["design"] == SINGLE:
        now["author_pass2"] = sha(P["p2"])
    else:
        now["volunteer_pass1"] = sha(P["vol"])
    for k, v in now.items():
        if K.get("hashes", {}).get(k) != v:
            pr.append(f"G1 hash mismatch: {k} changed since KAPPA.json")
    return pr


def step_validity(a):
    ctx = load_ctx(a)
    P, gd = ctx["P"], ctx["P"]["gd"]
    gd.mkdir(parents=True, exist_ok=True)
    res = {"step": "validity", "kind": a.kind, "problems": list(ctx["problems"]) + list(ctx["A1_probs"])}
    design = get_design(ctx)
    if design is None:
        return early(a, res, ctx, ["author_pass1.csv missing or incomplete: no gate time yet"])
    d = design["design"]
    res.update({"design": d, "validation_wording": design["validation_wording"],
                "llm_wording": LLM_LABEL})
    res["problems"] += integrity(ctx, design)
    K = read_kappa(gd)
    if K and K.get("status") == "INCOMPLETE":
        K_use = None
    else:
        K_use = K
    if K_use is not None:
        res["problems"] += verify_kappa_hashes(K_use, ctx, design)
    if d == TWO and (K_use is None or K_use.get("status") != "COMPUTED"):
        res["problems"].append("two-human design: KAPPA.json (COMPUTED) is required before adjudication and the validity step")
    lab, need, pr, adj_present = records(ctx, design)
    res["problems"] += pr
    if d == SINGLE and adj_present:
        res["adj_csv_note"] = "ADJ.csv exists in the single-labeler design: reported and NOT read (FR s5)"
    sc = read_scores([P["scores"], P["n2scores"]])
    for i in ctx["orig_ids"]:
        if i not in sc:
            res["problems"].append(f"scores: no row for gate item {i}")
    if res["problems"]:
        return early(a, res, ctx, [])
    g, gs = gate_frame(ctx["orig_ids"], lab, sc)
    y, yh = gs.h.to_numpy(), gs.pred.to_numpy()
    blk = ba_block(y, yh)
    est = blk["ba"] if blk["ba"] is not None else float("nan")
    lo, hi = (blk["lo"], blk["hi"]) if blk["lo"] is not None else (0.5, 0.5)
    tp, fn = int(((y == 1) & (yh == 1)).sum()), int(((y == 1) & (yh == 0)).sum())
    tn, fp = int(((y == 0) & (yh == 0)).sum()), int(((y == 0) & (yh == 1)).sum())
    ba_pass = bool(not np.isnan(est) and lo > 0.5)
    # ---- FR 6.4a [R1]: beside the gate, never part of the rule
    crux = gs[gs.ncr >= 1]
    sh = crux[crux.adj.isin(["HIDES", "SHOWS"])]
    corr_neg = gs[(gs.h == 0) & (gs.pred == 0)]
    n_shows = int((sh.adj == "SHOWS").sum())
    b_sh = ba_block(sh.h.to_numpy(), sh.pred.to_numpy())
    sec = {"BA_crux": ba_block(crux.h.to_numpy(), crux.pred.to_numpy()),
           "n_gate_items_dropped_ncruxes_unknown": int(gs.ncr.isna().sum()),
           "BA_sh": dict(b_sh, n_no_disagreement_left_out=int((crux.adj == "NO_DISAGREEMENT").sum()), n_human_shows=n_shows),
           "zero_crux_share_of_correct_AI_negatives": {"zero_crux_correct_negatives": int((corr_neg.ncr == 0).sum()),
                                                       "correct_negatives": int(len(corr_neg)),
                                                       "share": (float((corr_neg.ncr == 0).sum() / len(corr_neg)) if len(corr_neg) else None)},
           "wording_rule_fires": bool(n_shows < 5 or b_sh["lo"] is None or b_sh["lo"] <= 0.5)}
    if getattr(a, "scores_v1", None) and Path(a.scores_v1).exists():
        sc1 = read_scores([a.scores_v1])
        _, g1 = gate_frame(ctx["orig_ids"], lab, sc1)
        sec["scorer_v1_gate_BA"] = ba_block(g1.h.to_numpy(), g1.pred.to_numpy())
    from scipy.stats import spearmanr
    ok = gs.E.notna()
    rho = float(spearmanr(gs.E[ok], gs.h[ok])[0]) if ok.sum() > 2 and gs.h[ok].nunique() > 1 else float("nan")
    any_dis = float(np.mean([(l == "NO_DISAGREEMENT") == (n == 0) for l, n in zip(gs.adj, gs.ncr) if n == n])) if len(gs) else None
    also = {"spearman_E_vs_human_binary": rho, "agreement_on_is_there_any_disagreement": any_dis}
    A = lab_dict(ctx["A1"])
    if d == TWO:
        Vl = vol_labels_on_p1(ctx)
        for nm, src in (("ba_vs_volunteer_own_labels_before_adjudication_hypothesis_blind", Vl), ("ba_vs_author_pass1_labels", A)):
            _, g2 = gate_frame(ctx["orig_ids"], src, sc)   # UNSURE in that annotator's own labels excluded
            also[nm] = ba_block(g2.h.to_numpy(), g2.pred.to_numpy())
    # ---- status
    if not ba_pass:
        status = "FAIL"
        note = "balanced-accuracy lower bound <= 0.5: final whatever the kappa (FR 6.4)"
    elif d == SINGLE:
        if K_use is None or K_use.get("status") != "COMPUTED":
            status, note = "PROVISIONAL_PASS", "self-consistency kappa not yet recorded: every real-rank output is stamped PROVISIONAL (FR 6.5)"
        else:
            status = "PASS" if K_use["kappa"]["pass"] else "FAIL"
            note = "" if status == "PASS" else "self-consistency not established at n = 20: 'not yet measurable' write-up (FR s12), no definition changed"
    else:
        status = "PASS" if K_use["kappa"]["pass"] else "FAIL"
        note = "" if status == "PASS" else "agreement between the two annotators was not established: FR s12"
    res.update({"status": status, "verdict": status, "note": note,
                "kappa": (K_use or {}).get("kappa"),
                "kappa_recorded": bool(K_use and K_use.get("status") == "COMPUTED"),
                "balanced_accuracy": dict(blk, n_adjudicated_or_of_record=int(len(g)), n_unsure_excluded=int(g.unsure.sum()),
                                          unsure_items=list(g.item_id[g.unsure]), n_used=int(len(gs)),
                                          n_ai_parse_failure_or_missing=int(gs.ai_missing.sum()),
                                          must_exceed=0.5, B=B, seed=SEED, against=("author pass-1 labels (first pass)" if d == SINGLE else "adjudicated labels"),
                                          passed=ba_pass),
                "confusion": {"TP": tp, "FN": fn, "TN": tn, "FP": fp}, "FR_6_4a": sec, "also_reported": also,
                "labels_of_record_source": "author pass 1" if d == SINGLE else "agree -> author pass 1; differ -> ADJ.csv",
                "n_adjudicated": len(need)})
    res["balanced_accuracy"]["pass"] = ba_pass
    llm = None
    if P["llm"].exists() and llm_allowed(ctx, design, res):
        llm = read_llm(P["llm"], set(A))[0]
    res["headline"] = headline(ctx, design, lab, sc, llm, K_use)
    if d == SINGLE and P["vol"].exists() and design["files_in_labels_dir"].get("volunteer_pass1.csv") is None:
        res["late_volunteer_descriptive"] = late_volunteer(ctx)
    res["hashes"] = {"author_pass1": sha(P["p1"]), "author_pass2": sha(P["p2"]), "volunteer_pass1": sha(P["vol"]), "ADJ": sha(P["adj"]) if d == TWO else None,
                     "scores": sha(P["scores"]), "n2check_scores": sha(P["n2scores"]), "item_key": sha(P["key"]),
                     "DESIGN": sha(gd / "DESIGN.json"), "sample": sha(gd / "sample.json"), "n2_items": sha(gd / "n2_items.json"),
                     "FROZEN_RULES": sha(C.P / "FROZEN_RULES.md")}
    finish(a, res, "gate1_computed.json")
    print("gate1 validity:", status, f"BA={est:.3f} [{lo:.3f},{hi:.3f}]" if not np.isnan(est) else "BA undefined", "kappa recorded:", res["kappa_recorded"])
    return res


def late_volunteer(ctx):
    """FR 6.0: a volunteer file that arrives after gate time is hashed, reported and used only for this table; no rule."""
    out = {"note": "descriptive only; changes no label of record, gate status or headline (FR 6.0)", "sha256": sha(ctx["P"]["vol"])}
    if ctx["V"] is None or ctx["V_probs"]:
        out["status"] = "INCOMPLETE: " + "; ".join(ctx["V_probs"][:2])
        return out
    A, Vl = lab_dict(ctx["A1"]), vol_labels_on_p1(ctx)
    ids = list(A)
    blk = agree_block(ids, A, Vl, dict(zip(ctx["key"].item_id, ctx["key"].kind)), SEED)
    x = [Vl[i] for i in ctx["orig_ids"]]
    n_ = sum(t in ("HIDES", "SHOWS", "NO_DISAGREEMENT") for t in x)
    out.update({"author_vs_volunteer": blk, "volunteer_own_H_on_originals": (x.count("HIDES") / n_ if n_ else None)})
    return out


# ------------------------------------------------------------------ headline step
def step_headline(a):
    ctx = load_ctx(a)
    P, gd = ctx["P"], ctx["P"]["gd"]
    res = {"step": "headline", "kind": a.kind, "problems": list(ctx["problems"]) + list(ctx["A1_probs"])}
    design = get_design(ctx)
    if design is None:
        return early(a, res, ctx, ["author_pass1.csv missing or incomplete"])
    res["design"] = design["design"]
    res["problems"] += integrity(ctx, design)
    lab, need, pr, _ = records(ctx, design)
    res["problems"] += pr
    if res["problems"]:
        return early(a, res, ctx, [])
    K = read_kappa(gd)
    res["status"] = "COMPUTED"
    res["headline"] = headline(ctx, design, lab, read_scores([P["scores"]]), None, K if K and K.get("status") == "COMPUTED" else None)
    return finish(a, res, "headline.json")


# ------------------------------------------------------------------ LLM annotator (FR 6.8)
def read_llm(path, known):
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    out, missing, unknown = {}, [], []
    for r in d.itertuples():
        if r.item_id not in known:
            unknown.append(r.item_id)
            continue
        l = r.label.strip().upper()
        if l in TOK:
            out[r.item_id] = l
        else:
            missing.append(r.item_id)
    return out, missing, unknown


def llm_allowed(ctx, design, res=None):
    """FR 6.8: not shown / not computed before both author files are saved (single) or ADJ.csv is complete (two-human)."""
    if design["design"] == SINGLE:
        return ctx["A1"] is not None and not ctx["A1_probs"] and ctx["A2"] is not None and not ctx["A2_probs"]
    _, need, pr, _ = records(ctx, design)
    return not pr


def step_llm(a):
    ctx = load_ctx(a)
    P = ctx["P"]
    res = {"step": "llm", "kind": a.kind, "label": LLM_LABEL, "problems": list(ctx["problems"]) + list(ctx["A1_probs"]),
           "supplementary": "no cut-off, no rule, no effect on gate 1, the N2 check, the headline or any label (FR 6.8)"}
    design = get_design(ctx)
    if design is None:
        return early(a, res, ctx, ["author_pass1.csv missing or incomplete"])
    if not llm_allowed(ctx, design):
        res.update({"status": "NOT_ALLOWED_YET", "reason": "LLM labels are not computed or shown before both author files are saved "
                    "(single-labeler) or ADJ.csv is complete (two-human) (FR 6.8)"})
        print("gate1 llm: NOT_ALLOWED_YET")
        return res
    if not P["llm"].exists():
        res["status"] = "INCOMPLETE"
        res["problems"].append("llm_labels.csv missing")
        return early(a, res, ctx, [])
    A = lab_dict(ctx["A1"])
    L, miss, unk = read_llm(P["llm"], set(A))
    kinds = dict(zip(ctx["key"].item_id, ctx["key"].kind))
    ids = [i for i in A if i in L]
    res.update({"design": design["design"], "n_llm_labels": len(ids), "missing_or_invalid_llm_labels_left_out": miss, "unknown_ids_ignored": unk})
    res["author_pass1_vs_llm"] = agree_block(ids, A, L, kinds, SEED_LLM)
    lab, need, pr, _ = records(ctx, design)
    if design["design"] == TWO and not pr:
        Vl = vol_labels_on_p1(ctx)
        res["volunteer_vs_llm"] = agree_block([i for i in ids if i in Vl], Vl, L, kinds, SEED_LLM)
        res["labels_of_record_vs_llm"] = agree_block(ids, lab, L, kinds, SEED_LLM)
    sc = read_scores([P["scores"]])
    if sc:   # balanced accuracy of scorer 1 against the LLM annotator's labels, marked LLM (FR 6.4 also-reported row)
        g, gs = gate_frame([i for i in ctx["orig_ids"] if i in L], L, sc)
        res["scorer1_BA_vs_llm_labels_NOT_HUMAN"] = ba_block(gs.h.to_numpy(), gs.pred.to_numpy())
    res["status"] = "COMPUTED"
    return finish(a, res, "llm_agreement.json")


# ------------------------------------------------------------------ N2 check (FR 6.6)
def latest_gate_record(gd):
    fs = sorted(Path(gd).glob("gate1_computed__*.json"))
    fs = [f for f in fs if not f.name.endswith(".sha256")]
    if not fs:
        return None, "no gate1_computed record"
    f = fs[-1]
    sc_ = Path(str(f) + ".sha256")
    if not sc_.exists() or sc_.read_text(encoding="utf-8").split()[0] != C.sha256_file(f):
        return None, f"{f.name} does not match its sidecar"
    return json.loads(f.read_text(encoding="utf-8")), f.name


def fisher_p(tp, fn, tn, fp):
    """FR 6.6: one-sided Fisher exact test (scorer agrees with the labels more often than independence gives) on the 2x2 table
    rows = AI positive / negative, columns = human positive / negative.  A single class in either margin gives p = 1."""
    from scipy.stats import fisher_exact
    if (tp + fn == 0) or (tn + fp == 0) or (tp + fp == 0) or (tn + fn == 0):
        return 1.0
    return float(fisher_exact([[tp, fp], [fn, tn]], alternative="greater")[1])


def step_n2check(a):
    ctx = load_ctx(a)
    P, gd = ctx["P"], ctx["P"]["gd"]
    res = {"step": "n2check", "kind": a.kind, "problems": list(ctx["problems"]) + list(ctx["A1_probs"])}
    design = get_design(ctx)
    if design is None:
        return early(a, res, ctx, ["author_pass1.csv missing or incomplete"])
    res["design"] = design["design"]
    res["problems"] += integrity(ctx, design)
    lab, need, pr, _ = records(ctx, design)
    res["problems"] += pr
    sc = read_scores([P["n2scores"], P["scores"]])
    for i in ctx["n2_ids"]:
        if i not in sc:
            res["problems"].append(f"n2check_scores: no row for N2 item {i}")
    if res["problems"]:
        return early(a, res, ctx, [])
    G, gname = latest_gate_record(gd)
    gstat = (G or {}).get("status")
    g, gs = gate_frame(ctx["n2_ids"], lab, sc)
    y, yh = gs.h.to_numpy(), gs.pred.to_numpy()
    tp, fn = int(((y == 1) & (yh == 1)).sum()), int(((y == 1) & (yh == 0)).sum())
    tn, fp = int(((y == 0) & (yh == 0)).sum()), int(((y == 0) & (yh == 1)).sum())
    p = fisher_p(tp, fn, tn, fp)
    fisher_ok = bool(p <= 0.05)
    if gstat == "PASS" and fisher_ok:
        chk = "PASS"
    elif gstat == "PROVISIONAL_PASS" and fisher_ok:
        chk = "PROVISIONAL_PASS"
    else:
        chk = "NOT PASSED"
    res.update({"status": "COMPUTED", "n2_check": chk, "gate1_record_used": gname, "gate1_status": gstat,
                "fisher_one_sided_p": p, "fisher_rule": "one-sided Fisher exact p <= 0.05 and gate 1 PASS (PROVISIONAL_PASS -> provisional)",
                "table": {"TP": tp, "FN": fn, "TN": tn, "FP": fp},
                "n_items": 12, "n_used": int(len(gs)), "n_unsure_excluded": int(g.unsure.sum()), "unsure_items": list(g.item_id[g.unsure]),
                "n_missing_E_counted_wrong": int(gs.ai_missing.sum()),
                "balanced_accuracy_descriptive": ba_block(y, yh),
                "N2_VALIDATED": chk == "PASS", "N2_VALIDATED_PROVISIONAL": chk == "PROVISIONAL_PASS",
                "label_if_validated": N2_LABEL + "; " + design["validation_wording"],
                "label_otherwise": "EXPLORATORY: the scorer was not validated on newly generated text",
                "stated_in_advance": "NOT PASSED is a likely outcome for a scorer right 4 times in 5; it is not evidence that the scorer is invalid on N2 text (FR 6.6)",
                "scope": "pooled 12 only; no generator- or cell-level validity claim; scorer 1 only; estimates without the development-launch N2 rounds (FR 6.6)"})
    print("gate1 n2check:", chk, f"p={p:.4f}", "N2_VALIDATED" if chk == "PASS" else "")
    return finish(a, res, "n2check_computed.json")


# ------------------------------------------------------------------ cli
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=("kappa", "selfcons", "validity", "headline", "n2check", "llm"))
    ap.add_argument("--kind", required=True, choices=("dummy", "real"))
    ap.add_argument("--labels-dir", dest="labels_dir", default=str(C.P / "labels"))
    ap.add_argument("--gate-dir", dest="gate_dir", default=str(C.GATE))
    ap.add_argument("--adj", default=None)
    ap.add_argument("--item-key", dest="item_key", default=None)
    ap.add_argument("--scores", default=None)
    ap.add_argument("--n2-scores", dest="n2_scores", default=None)
    ap.add_argument("--scores-v1", dest="scores_v1", default=None)
    ap.add_argument("--freeze", default=None)
    ap.add_argument("--llm-labels", dest="llm_labels", default=None)
    a = ap.parse_args(argv)
    real_labels, real_gate = (C.P / "labels").resolve(), C.GATE.resolve()
    ps = [a.labels_dir, a.gate_dir] + [x for x in (a.adj, a.item_key, a.scores, a.n2_scores, a.freeze, a.llm_labels) if x]
    if a.kind == "dummy":
        if "DUMMY_" not in str(Path(a.labels_dir)) or "DUMMY_" not in str(Path(a.gate_dir)):
            sys.exit("kind=dummy needs a DUMMY_* labels dir and a DUMMY_* gate dir")
        if is_under(a.labels_dir, real_labels) or is_under(a.gate_dir, real_gate) or Path(a.gate_dir).resolve() == real_gate:
            sys.exit("kind=dummy may not use P/labels or P/gate1")
    elif any("DUMMY_" in str(x) for x in ps):
        sys.exit("kind=real with DUMMY_ inputs refused")
    if is_under(a.gate_dir, a.labels_dir):
        sys.exit("REFUSED: the gate directory is inside the labels directory (the pipeline never writes there).")
    P = paths(a)
    if not P["key"].exists():
        sys.exit(f"missing input (labels are never created or simulated): {P['key']}")
    return {"kappa": step_kappa, "selfcons": step_selfcons, "validity": step_validity, "headline": step_headline,
            "n2check": step_n2check, "llm": step_llm}[a.step](a)


if __name__ == "__main__":
    main()
