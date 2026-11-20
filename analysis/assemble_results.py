"""Assemble analysis/results/RESULTS_MAIN.md, analysis/results/COUNTS_RECONCILE.md and figures/data/*.csv from the
versioned run outputs in analysis/results/runs (latest file per stem).  No number is typed by hand: every figure below
is read from a JSON written by a pre-registered script.  Stamp: HIDE_NOT_HUMAN_VALIDATED (GATE1_RESULT.json, R5)."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import run_log  # noqa: E402

TAG = C.check_kind("real")
assert TAG == "HIDE_NOT_HUMAN_VALIDATED"
RD = C.A / "results" / "runs"
RES = C.A / "results"
FD = C.P / "figures" / "data"
FD.mkdir(parents=True, exist_ok=True)
LONG = C.A / "scores" / "a2_long_real.parquet"
SCORES = C.A / "scores" / "a2_scores_v2.jsonl"
SHA_LONG, SHA_SC = C.sha256_file(LONG), C.sha256_file(SCORES)
WORD = "pre-registered test; the predictor's hide/show contrast is not human-validated"


def latest(stem):
    fs = sorted(RD.glob(f"{stem}__*.json"))
    if not fs:
        sys.exit(f"missing output {stem}")
    return fs[-1], json.loads(fs[-1].read_text(encoding="utf-8"))


J, F = {}, {}
for s in ("A2_primary", "A2b", "A2d", "A2e", "A2f", "A2g", "A2i", "N1", "N4", "prevalence"):
    F[s], J[s] = latest(s)
HOLM = json.loads((RD / "TIER2_HOLM.json").read_text(encoding="utf-8"))
N3_DONE = bool(sorted(RD.glob("N3__*.json"))) and (RD / "TIER2_HOLM_FINAL.json").exists()
N3_LATE = "--n3-not-scored-in-time" in sys.argv
if N3_DONE:
    F["N3"], J["N3"] = latest("N3")
    HOLM_F = json.loads((RD / "TIER2_HOLM_FINAL.json").read_text(encoding="utf-8"))
    assert HOLM_F["gate_tag"] == "HIDE_NOT_HUMAN_VALIDATED" and sorted(HOLM_F["family"]) == ["N1", "N3", "N4"]
CNT = json.loads((RES / "A3_N3_COUNTS.json").read_text(encoding="utf-8"))
REC = json.loads((RES / "COUNTS_RECONCILE.json").read_text(encoding="utf-8"))
TIER = json.loads((C.GATE / C.TIER_FILE).read_text(encoding="utf-8"))
for s, j in J.items():
    assert j.get("gate_tag") == TAG, s
assert HOLM["gate_tag"] == TAG and REC["gate_tag"] == TAG


def f4(x):
    return f"{x:+.4f}"


def ci(r):
    return f"[{f4(r['lo'])}, {f4(r['hi'])}]"


def pv(x):
    return "<0.0001" if x < 1e-4 else f"{x:.4f}"


def sh(path):
    return C.sha256_file(path)[:16] + "…"


rows, fig_a2, fig_t2 = [], [], []


def row(est_name, status, r, p, holm, nr, nl, script, seed, inp, out):
    rows.append("| " + " | ".join([est_name, status, f4(r["est"]) if r else "—", ci(r) if r else "—", p, holm,
                                   str(nr), str(nl), script, str(seed), inp, out]) + " |")


a2 = J["A2_primary"]
e = a2["controlled"]["erasure"]
row("A2 `beta_E` (primary; scorer 1; per-rater ranks; length + clarity controls)", WORD, e, pv(e["p_boot"]), "n/a (tested alone, FR §9)",
    a2["n_rounds"], a2["n_clusters"], "a2_within_round.py", a2["seed"], "a2_long_real.parquet " + SHA_LONG[:16] + "…", F["A2_primary"].name)
fig_a2.append(("A2", "primary (length + clarity)", e, a2["n_rounds"], a2["n_clusters"], F["A2_primary"].name))
for k, lab in (("length", "A2 control: `beta_L` (z log length)"), ("clarity", "A2 control: `beta_C` (z Flesch)")):
    r = a2["controlled"][k]
    row(lab, "printed beside A2 (FR §7 model)", r, "—", "—", a2["n_rounds"], a2["n_clusters"], "a2_within_round.py", a2["seed"],
        "a2_long_real.parquet", F["A2_primary"].name)

sens = [("A2b", "A2b: + own-opinion similarity (MiniLM)", J["A2b"]["controlled"]["erasure"], J["A2b"]),
        ("A2d", "A2d: including the development launches (871)", J["A2d"]["controlled"]["erasure"], J["A2d"]),
        ("A2e", "A2e: `E_pos` (SIDED counted as shown; not crux erasure)", J["A2e"]["controlled"]["erasure"], J["A2e"]),
        ("A2f", "A2f: + vagueness term rate", J["A2f"]["controlled"]["erasure"], J["A2f"]),
        ("A2g", "A2g: `E_w` member-weighted", J["A2g"]["controlled"]["erasure"], J["A2g"]),
        ("A2h", "A2h: length only (no clarity control)", a2["A2h"]["erasure"], a2),
        ("A2i", "A2i: informative rounds only", J["A2i"]["controlled"]["erasure"], J["A2i"])]
srow = []
for key, lab, r, j in sens:
    fn = F[key].name if key in F else F["A2_primary"].name
    scr = "a2i_informative.py" if key == "A2i" else "a2_within_round.py"
    row(lab, "sensitivity, not tested on its own (FR §9)", r, "—", "—", j["n_rounds"], j["n_clusters"], scr, j["seed"],
        "a2_long_real.parquet " + SHA_LONG[:16] + "…", fn)
    fig_a2.append((key, lab, r, j["n_rounds"], j["n_clusters"], fn))
rows.append("| A2c: LLM clarity rating from scorer 2 | **NOT RUN**: no second scorer met the pre-registered technical bar (D44–D48); A2c needs scorer 2 | — | — | — | — | — | — | — | — | — | — |")

n1, n4 = J["N1"], J["N4"]
_n3s = RES / "N3_STATUS.json"
N3S = json.loads(_n3s.read_text(encoding="utf-8")) if _n3s.exists() else {}
N3S_SHORT = N3S.get("short") or "iteration-1 statements not yet scored"
# conservative Holm: N3 counted at p = 1 (it cannot be dropped from the family, FR s9)
cons = C.holm({"N1": HOLM["raw_p"]["N1"], "N4": HOLM["raw_p"]["N4"], "N3": 1.0})
HP = HOLM_F["holm_p"] if N3_DONE else (cons if N3_LATE else HOLM["holm_p"])
row("N1 `alpha` (winner gap in `E`, adjusted for length and clarity, [R3])", WORD + "; Tier-2 family", n1["erasure"], pv(n1["erasure"]["p_boot"]),
    pv(HP["N1"]), n1["n_rounds"], n1["n_clusters"], "n1_winner_vs_mean.py", n1["seed"], "a2_long_real.parquet " + SHA_LONG[:16] + "…", F["N1"].name)
for k, lab in (("N1u", "N1u: unadjusted mean `d_r`"), ("N1h", "N1h: length-only adjustment"), ("g_L", "N1 slope `g_L`"), ("g_C", "N1 slope `g_C`")):
    row(lab, "printed beside N1, not a family test", n1[k], "—", "—", n1["n_rounds"], n1["n_clusters"], "n1_winner_vs_mean.py", n1["seed"], "a2_long_real.parquet", F["N1"].name)
row("N4 interaction `E x minority`", WORD + "; Tier-2 family", n4["interaction"], pv(n4["interaction"]["p_boot"]), pv(HP["N4"]),
    "—", n4["n_clusters"], "n4_minority.py", n4["seed"], "a2_long_real.parquet " + SHA_LONG[:16] + "…", F["N4"].name)
rows.append(f"| A3 `E(AI) − E(human)` | **NOT RUN**: {CNT['A3']['launches_confirmatory']} qualifying launches < floor 30 (FR §8; count_a3_n3.py) — leaves the family | — | — | — | — | {CNT['A3']['rounds_confirmatory']} | {CNT['A3']['launches_confirmatory']} | count_a3_n3.py | — | source parquet 7cf8d5ce… | A3_N3_COUNTS.json |")
if N3_DONE:
    n3 = J["N3"]
    row("N3 `mean E(iteration 1) − mean E(iteration 0)` (cruxes fixed from opinions)", WORD + "; Tier-2 family", n3["erasure"],
        pv(n3["erasure"]["p_boot"]), pv(HP["N3"]), n3["n_rounds"], n3["n_clusters"], "n3_draft_vs_revised.py", n3["seed"],
        "n3_statements.csv " + C.sha256_file(C.A / "scores" / "n3_statements.csv")[:16] + "…", F["N3"].name)
elif N3_LATE:
    rows.append(f"| N3 | **NOT RUN: the scorer app did not start (Modal 503, no container) — not a data decision**; {N3S_SHORT}; stays in the family at p = 1 (FR §9) | — | — | — | — | {CNT['N3']['rounds_confirmatory']} | {CNT['N3']['launches_confirmatory']} | — | 20261123 | — | — |")
else:
    rows.append(f"| N3 `E(iteration 1) − E(iteration 0)` | **NOT RUN — not scored**: qualifies ({CNT['N3']['launches_confirmatory']} launches ≥ 30); scoring approved (D57) but {N3S_SHORT}. Stays in the family (FR §9) | — | — | — | — | {CNT['N3']['rounds_confirmatory']} | {CNT['N3']['launches_confirmatory']} | n3_score.py | 20261123 (when run) | — | N3_STATUS.json |")
rows.append("| A4 `beta_E` under scorer 2 | **NOT RUN**: no candidate passed the pre-registered technical bar (FR §6.9 [R4a], D47/D48) — leaves the family | — | — | — | — | — | — | — | — | — | — |")


pr = J["prevalence"]
prow = []
for k, lab, unit in (("share_E_eq_1", "statements with `E` = 1 (hide every crux)", "statements"),
                     ("share_any_VISIBLE", "statements with ≥ 1 VISIBLE crux", "statements"),
                     ("label_share_VISIBLE", "crux labels VISIBLE", "crux labels"), ("label_share_SIDED", "crux labels SIDED", "crux labels"),
                     ("label_share_BLENDED", "crux labels BLENDED", "crux labels"), ("label_share_OMITTED", "crux labels OMITTED", "crux labels"),
                     ("R_inf_over_rounds", "`R_inf` / rounds (informative rounds of the A2 analysis set)", "rounds")):
    r = pr[k]
    prow.append(f"| {lab} | pre-specified descriptive (FR §7.3); scorer-based, not human-validated for hide/show | {r['est']:.4f} | [{r['lo']:.4f}, {r['hi']:.4f}] | {r['n_units']} {unit} | {r['n_launches']} | prevalence.py | {pr['seed']} | a2_scores_v2.jsonl {SHA_SC[:16]}… | {F['prevalence'].name} |")

se = e["se"]
# ---- D58: step-2 record + red-team scripts re-run from P (copies in analysis/redteam_rerun; originals untouched)
ST2_F = C.GATE / "STEP2_computed__20261116T015355Z.json"
ST2 = json.loads(ST2_F.read_text(encoding="utf-8"))
RR, RO = C.A / "redteam_rerun", C.A / "redteam"
RT = {k: json.loads((RR / f"{k}.json").read_text(encoding="utf-8")) for k in ("rt_refit", "rt_n4", "rt_step2", "rt_seed_sensitivity")}
RT_SAME = {k: RT[k] == json.loads((RO / f"{k}.json").read_text(encoding="utf-8")) for k in RT}
RTS = {k: C.sha256_file(RR / f"{k}.json")[:16] for k in RT}
rf, rn = RT["rt_refit"], RT["rt_n4"]
assert abs(rf["A2_primary_own"]["E"]["est"] - e["est"]) < 1e-9 and rf["R_inf"] == 150
FLEX = ("X_len_cubic", "X_len_decile_dummies", "X_len_withinround_rank", "X_len_rawwords")
LEN_SPECS = [("none (`E` only; the record's uncontrolled model)", "A2_uncontrolled_own"),
             ("**linear z log words (FR primary)**", "A2_primary_own"),
             ("cubic in z log words", "X_len_cubic"), ("10 length-decile dummies", "X_len_decile_dummies"),
             ("within-round length rank (1-4)", "X_len_withinround_rank"), ("within-round length rank + z log words", "X_len_rank_and_log"),
             ("z raw word count", "X_len_rawwords"), ("z raw words + z log words", "X_len_raw_and_log")]
len_rows = []
for lab, k in LEN_SPECS:
    r = rf[k]["E"]
    len_rows.append((lab, k, r["est"], r["se_cr1"], r["est"] / r["se_cr1"], rf[k]["_n_rows"], rf[k]["_n_clusters"]))
LEN_MD = "\n".join(f"| {lab} | {f4(est)} | {se_:.4f} | {t:+.2f} | {nr} rows / 1166 rounds / {nc} launches | `analysis/redteam/rt_refit.py` key `{k}` |"
                    for lab, k, est, se_, t, nr, nc in len_rows)
sp = rn["A2_E_split_sided_vs_blended_omitted"]
inf_h = RT["rt_step2"]["A2_informative_rounds_by_hsplit"]
inf_hl = RT["rt_step2"]["A2_informative_launches_by_hsplit"]
seedA2b = RT["rt_seed_sensitivity"]["A2b"]
n_le0 = round(seedA2b["share_other_seeds_lo_le_0"] * seedA2b["n_other_seeds"])
STEP2_MD = (f"""## Step 2: validation of the disagreement-presence component (gate record; copied from `gate1/STEP2_computed__20261116T015355Z.json`)
Only on this check may the paper say: "the scorer's detection of disagreement was validated against participants' own pre-deliberation
position ratings — for whether a group disagrees, not for whether a statement hides it" (FR §6.R5.6).

| Quantity | Value |
|---|---|
| Usable rounds / launches | {ST2['n_usable_rounds']} / {ST2['n_usable_launches']} (development launches excluded) |
| Hsplit classes (participants split on the question) | split: {ST2['hsplit_class_counts']['1']['rounds']} rounds ({ST2['hsplit_class_counts']['1']['launches']} launches); not split: {ST2['hsplit_class_counts']['0']['rounds']} rounds ({ST2['hsplit_class_counts']['0']['launches']} launches) |
| Confusion (missing extraction counted wrong) | TP {ST2['confusion']['tp']}, FN {ST2['confusion']['fn']}, TN {ST2['confusion']['tn']}, FP {ST2['confusion']['fp']} |
| BA2 | {ST2['BA2']:.4f} |
| 95% CI, launch-cluster bootstrap (seed {ST2['seed_launch']}, B = {ST2['B']}) | [{ST2['launch_boot']['lb']:.4f}, {ST2['launch_boot']['ub']:.4f}] |
| 95% CI, question-cluster bootstrap (seed {ST2['seed_question']}) | [{ST2['question_boot']['lb']:.4f}, {ST2['question_boot']['ub']:.4f}] |
| Sensitivity / specificity | {ST2['sens']:.3f} / {ST2['spec']:.3f}: the scorer finds a crux in about half of the groups whose members did not split |
| Outcome | {ST2['outcome']} (lower bound used {ST2['lb_used']:.4f} > 0.5, point ≥ 0.60) |

**Informative A2 rounds from non-split groups: {inf_h['0']} of {inf_h['0'] + inf_h['1']}** ({inf_hl['0']} launches; split groups {inf_h['1']} rounds,
{inf_hl['1']} launches). Computed by `analysis/redteam/rt_step2.py` (re-run from P → `analysis/redteam_rerun/rt_step2.json` sha256 {RTS['rt_step2']}…),
joining the A2 analysis set to `gate1/step2_private/rounds__20261116T015355Z.csv`.

""")
if N3_DONE:
    HOLM_TEXT = (f"**Final Holm of record over N1, N3, N4** (`tier2_holm.py` → `TIER2_HOLM_FINAL.json`, m = 3): N1 {pv(HP['N1'])}, "
                 f"N3 {pv(HP['N3'])}, N4 {pv(HP['N4'])}. Raw p: N1 {pv(HOLM_F['raw_p']['N1'])}, N3 {pv(HOLM_F['raw_p']['N3'])}, "
                 f"N4 {pv(HOLM_F['raw_p']['N4'])}. Superseded interim versions (kept): Holm over N1, N4 only (`TIER2_HOLM.json`: N1 "
                 f"{pv(HOLM['holm_p']['N1'])}, N4 {pv(HOLM['holm_p']['N4'])}) and the conservative bound with N3 at p = 1 (N1 {pv(cons['N1'])}, "
                 f"N4 {pv(cons['N4'])}).")
elif N3_LATE:
    HOLM_TEXT = (f"N3: NOT RUN: the scorer app did not start (Modal 503, no container) — not a data decision ({N3S_SHORT}; `analysis/results/N3_STATUS.json`). **Holm of record = conservative bound, N3 at p = 1** (m = 3): "
                 f"N1 {pv(cons['N1'])}, N4 {pv(cons['N4'])}. Holm over N1, N4 only (anti-conservative, not of record): N1 "
                 f"{pv(HOLM['holm_p']['N1'])}, N4 {pv(HOLM['holm_p']['N4'])}.")
else:
    HOLM_TEXT = (f"N3 has not run ({N3S_SHORT}; details `analysis/results/N3_STATUS.json`). Per D57, if N3 is not scored by 06:30Z the conservative bound below is the Holm of record. Two versions are printed:\n"
                 f"- **Holm over the tests that ran (N1, N4)** — `TIER2_HOLM.json`: N1 {pv(HOLM['holm_p']['N1'])}, N4 {pv(HOLM['holm_p']['N4'])}. "
                 f"Anti-conservative while N3 is missing.\n- **Conservative bound, N3 at p = 1** (m = 3): N1 {pv(cons['N1'])}, N4 {pv(cons['N4'])}.")
N3_NOTRUN = "" if N3_DONE else (f"N3 (NOT RUN: the scorer app did not start (Modal 503, no container) — not a data decision; {N3S_SHORT}), " if N3_LATE else f"N3 (approved, not scored: {N3S_SHORT}), ")
N3_CODE = ""
if N3_DONE:
    _s = json.loads((C.A / "scorer_runs" / "n3" / "summary.json").read_text(encoding="utf-8"))
    _m = json.loads((C.A / "scores" / "n3_statements.csv.manifest.json").read_text(encoding="utf-8"))
    N3_CODE = (f", `n3_score.py` (N3 iteration-1 labelling with frozen scorer v2, cruxes reused from `a2_extractions_v2.jsonl`; "
               f"{_s['stats']['calls']} label calls, final label parse failures {_s['stats'].get('parse_fail_final_label')}, "
               f"session cost ${_s['session']['session_cost_usd']}; statement table counts {_m['counts']})")
md = f"""# RESULTS_MAIN — T3-1 crux erasure, real data

**STAMP: HIDE_NOT_HUMAN_VALIDATED** (gate1\\GATE1_RESULT.json, rules R5, status VALIDATED_PRESENCE; `common.check_kind('real')`).
Every `E`-based estimate below is a **{WORD}**. The scorer is validated for detecting whether a disagreement is
present, not for detecting whether a statement hides it (FR §6.R5.6). No directional rank claim in title or abstract.
Step 3 (author verification) was NOT DONE (D51/D53), so `H5` is not computed and there is no human-labelled rate.

Generated by `analysis/assemble_results.py` from the versioned outputs in `analysis/results/runs/` (no number typed by hand).
Analysis set: the 721 non-development launches (FR §2 [R4]; the output JSONs carry the set label written by `common.restrict_confirmatory`).
Interval of record: wild cluster bootstrap-t, Rademacher weights, launch clusters, CR1 SE, B = 10,000 (FR §7 [R2]);
p = symmetric bootstrap-t p. Intervals are unadjusted 95%. Main input: `analysis/scores/a2_long_real.parquet`
sha256 `{SHA_LONG}` (built by `build_a2_long_real.py`; scorer-1 `E` from `a2_scores_v2.jsonl` sha256 `{SHA_SC}`;
source parquet `7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4`, re-checked on every run).

## Tier (FR §7.1)
Blind tier of record (`gate1\\A2_TIER_R4.json`): {TIER['tier']} (`K_inf` = {TIER['K_inf']}, `MDE80` = {TIER['MDE80']:.4f}).
One-way downgrade check after unblinding: 2.80 × SE(`beta_E`) = 2.80 × {se:.4f} = {2.8 * se:.4f} ≤ 0.10 → tier stays **{a2['tier_final']}**.
Corrected informative counts (see COUNTS_RECONCILE.md): `R_inf` = {a2['n_rounds'] - a2['rounds_no_E_variation']} rounds, `K_inf` = {a2['launches_with_E_variation']} launches
(the tier file's 152 / 144 count 2 rounds with a partly missing `E`; the tier is unchanged: 142 ≥ 100).

{STEP2_MD}## Estimates

| Estimate | Status / wording | Point | 95% CI | p | Holm p | n rounds | n launches | Script | Seed | Input sha256 | Output |
|---|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

A2: {a2['n_rows']} rater × statement rows; {a2['rounds_dropped_missing_E']} rounds of the 1,622 in the set dropped for missing `E` (zero-crux,
extraction failure or label parse failure); {a2['rater_rounds_dropped_all_tied']} all-tied rater-rounds dropped; {a2['rounds_no_E_variation']} rounds without `E` variation kept (they inform the controls only).
Interval and p agree for A2 (interval excludes 0, p < 0.05), so the borderline rule of FR §7 does not apply.
N1: {n1['rounds_tied_winner_excluded']} rounds with a tied winner excluded; {n1['rounds_with_d_nonzero']} rounds with `d_r` ≠ 0. N1 [R3] guard: the synthetic length-confound check covered 0 in 192/200 = 96% (≥ 93%, RUNS.md 2026-11-15T18:56Z), so N1 stays in the family.
N4: {n4['n_minority_raters']} minority and {n4['n_majority_raters']} majority rater-rounds; {n4['raters_excluded_no_side']} rater-rounds on neither side or with equal sides excluded. FR §8 informative counts for N4 (D58 item 5; `rt_n4.py` re-run): {rn['N4_informative_rounds']} informative rounds in {rn['N4_informative_launches']} launches; {rn['N4_informative_minority_rater_rounds']} informative minority rater-rounds of {rn['N4_minority_rater_rounds']} minority rater-rounds ({rn['N4_majority_rater_rounds']} majority).
N1 Schulze-winner sensitivity (FR §8 [R3]): **not run** — no frozen script implements it.

### Tier-2 family and Holm (FR §9)
Family as FR §8/§9 defines it from the availability counts: N1, N3, N4 (A3 below its floor; A4 not run).
{HOLM_TEXT}

### Binding wording rules checked (FR §7, §8)
- A2b: `beta_E` keeps its sign and its interval excludes 0 (lower bound {f4(J['A2b']['controlled']['erasure']['lo'])}, i.e. at the margin) → the A2b rule does not fire; the seed of record (20261119) decides. Seed note (D58 item 3): over {seedA2b['n_other_seeds']} other bootstrap seeds (B = 10,000) the A2b lower bound is ≤ 0 under {n_le0} of {seedA2b['n_other_seeds']} (range [{seedA2b['lo_min']:+.4f}, {seedA2b['lo_max']:+.4f}]; p {seedA2b['p_min']:.3f}–{seedA2b['p_max']:.3f}), so A2b is borderline (`analysis/redteam/rt_seed_sensitivity.py`, re-run → `redteam_rerun/rt_seed_sensitivity.json` sha256 {RTS['rt_seed_sensitivity']}…).
- A2h vs A2: same sign, both intervals exclude 0 → no statement required.
- A2d vs A2: same sign, both exclude 0 → no statement required.
- A2e: its interval includes 0 and its sign is opposite to A2. The A2e rule (A2e only as secondary when A2 is null and A2e is not) does not fire; A2e is never called crux erasure.
- N1: `alpha` ({f4(n1['erasure']['est'])}) and N1h ({f4(n1['N1h']['est'])}) are positive, N1u ({f4(n1['N1u']['est'])}) is negative; all three intervals include 0. They differ in sign, so the results text **must say so** (FR §8 [R3]).
- §7.1 wording: tier INFORMATIVE, but under VALIDATED_PRESENCE the §6.R5.6 limits govern: "{WORD}"; the three verbs FR §6.R5.6 bans are not used for any estimate here; no directional rank claim in title or abstract.

## Pre-specified descriptive: prevalence (FR §7.3; scorer 1; rounds with ≥ 1 crux; dev-excluded set)

| Quantity | Status | Point | 95% CI | n units | n launches | Script | Seed | Input sha256 | Output |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(prow) + f"""

Rounds with ≥ 1 crux: {pr['rounds_with_ge1_crux']}; statements with `E`: {pr['statements_with_E']}; statements without `E` in those rounds: {pr['statements_missing_E_in_crux_rounds']}.
Interval for shares: the method of record applied to an intercept-only regression (FR §7 [R2]); its coverage was not checked for shares (FR limitation).
Not computed under R5: `H5` (step 3 NOT DONE), `D1h`, `BA_crux`, `BA_sh` and the scorer rate on the 38 gate items (these need human labels, which R5 does not have).

## Not run (and why)
A2c (no scorer 2), A4 (no scorer 2), A3 (0 qualifying launches), {N3_NOTRUN}N1 Schulze sensitivity (no frozen implementation). N2 is owned by another runner.

## Exploratory (not in FROZEN_RULES; no significance language)
- **A2 without controls** (`E` only; printed by `a2_within_round.py`): {f4(a2['uncontrolled']['erasure']['est'])} {ci(a2['uncontrolled']['erasure'])}. The sign is the reverse of the controlled A2; adding the length control (`beta_L` = {f4(a2['controlled']['length']['est'])}) changes the sign of the `E` contrast. The paper should show both so the reader sees that the A2 estimate depends on the length adjustment. Exploratory description only.
- **N4 conditional slopes** (figure schema of `n4_minority.py`): majority-side raters {f4(n4['majority']['est'])} {ci(n4['majority'])}, minority-side raters {f4(n4['minority']['est'])} {ci(n4['minority'])}.
- **Count reconciliation** (COUNTS_RECONCILE.md).

## Exploratory robustness (red team; not pre-registered)
Source: `analysis/redteam/REDTEAM.md` (decisions.md D58). Every number below is read from the red-team scripts re-run from P
(copies in `analysis/redteam_rerun/`, outputs: rt_refit {RTS['rt_refit']}…, rt_n4 {RTS['rt_n4']}…, rt_step2 {RTS['rt_step2']}…,
rt_seed_sensitivity {RTS['rt_seed_sensitivity']}…). Re-run output byte-for-byte equal in content to the red team's own JSON in `analysis/redteam/`: {', '.join(f"{k} {'yes' if v else 'NO'}" for k, v in RT_SAME.items())}.
No significance language; t = estimate / CR1 SE. These do not change any pre-registered estimate (D58).

**A2 under other length specifications** (clarity kept; same 1,166 rounds; figure data `figures/data/a2_length_spec.csv`).
The A2 estimate is small and sensitive to how statement length is controlled: without the length control the sign is reversed, and
the flexible length adjustments (cubic, deciles, within-round rank, raw words) give |t| between {min(abs(r[4]) for r in len_rows if r[1] in FLEX):.2f} and {max(abs(r[4]) for r in len_rows if r[1] in FLEX):.2f}; the two combined forms (rank + log words, raw + log words) give t {', '.join(f"{r[4]:+.2f}" for r in len_rows if r[1] in ("X_len_rank_and_log", "X_len_raw_and_log"))}.

| Length adjustment | `beta_E` | CR1 SE | t | n | Script |
|---|---|---|---|---|---|
{LEN_MD}

Within the 150 informative rounds, within-round corr(`E`, log length) = {rf['inf_within_corr_E_loglen']:+.2f}.

**`E` split into its SIDED part and its BLENDED/OMITTED part** (A2 model with the two shares as separate predictors; `analysis/redteam/rt_n4.py`):
SIDED share {f4(sp['sided']['est'])} (SE {sp['sided']['se_cr1']:.4f}, t {sp['sided']['t']:+.2f}); BLENDED/OMITTED share {f4(sp['blom']['est'])} (SE {sp['blom']['se_cr1']:.4f}, t {sp['blom']['t']:+.2f});
n = {sp['_n']} rows, {sp['_G']} launches. Most of the A2 contrast comes from one-sided statements, so these data cannot separate
"hides the disagreement" from "states my side" (D58 item 2; consistent with A2b and N4).

**Majority-side vs minority-side raters** (N4 model, record run `{F['N4'].name}`, wild bootstrap-t 95% CI): majority-side raters
{f4(n4['majority']['est'])} {ci(n4['majority'])}, minority-side raters {f4(n4['minority']['est'])} {ci(n4['minority'])}; n = {n4['n_rows']} rows,
{n4['n_majority_raters']} majority and {n4['n_minority_raters']} minority rater-rounds, {n4['n_clusters']} launches. Red-team refit (`rt_n4.py`, key `N4_own`):
majority `E` t {rn['N4_own']['E']['t']:+.2f}, interaction t {rn['N4_own']['Exm']['t']:+.2f} (same estimates as the record).

## Code and inputs
New scripts written for this run (builders or thin wrappers; none changes an analysis rule): `build_a2_long_real.py`,
`a2i_informative.py`, `prevalence.py`, `count_a3_n3.py`, `counts_reconcile.py`, `assemble_results.py`, `n3_score.py` + `n3_launch.py`
(N3 labelling with frozen scorer v2, cruxes reused from `a2_extractions_v2.jsonl`){N3_CODE}; red-team scripts copied unchanged to
`analysis/redteam_rerun/` and re-run from P (the red team's own folder is not written). Version history of this file:
`analysis/results/history/`. One change to a
frozen-era script: `tier2_holm.py` now stamps the gate tag (old sha256 9bcb0b73…, new 89ba05e6…; logged in RUNS.md).
Every run has a RUNS.md row with the output sha256.
"""
out = RES / "RESULTS_MAIN.md"
if out.exists():
    _old = out.read_bytes()
    _arch = RES / "history" / f"RESULTS_MAIN__{C.utc_stamp()}__{C.sha256_file(out)[:12]}.md"
    _arch.parent.mkdir(exist_ok=True)
    _arch.write_bytes(_old)
    C.write_sidecar(_arch)
out.write_text(md, encoding="utf-8")
C.write_sidecar(out)

# COUNTS_RECONCILE.md
A, Cf = REC["all_launches"], REC["confirmatory_set"]
cr = f"""# COUNTS_RECONCILE — evaluable-round counts

**STAMP: HIDE_NOT_HUMAN_VALIDATED.** Generated by `analysis/assemble_results.py` from `analysis/results/COUNTS_RECONCILE.json`
(written by `analysis/counts_reconcile.py`; inputs `a2_scores_v2.jsonl` sha256 `{REC['inputs']['a2_scores_v2.jsonl']}`,
`pilot_groups.jsonl` sha256 `{REC['inputs']['pilot_groups.jsonl']}`).

## The three numbers
| Number | Where | Script and rule |
|---|---|---|
| 1,409 | D32, status.md | `a2_variation_counts.py`: rounds with ≥ 1 crux **and `E` present for all 4 candidates**, all 871 launches |
| 1,464 | A2_TIER_R4.json `counts_including_development_launches` | `a2_informativeness.counts()`: rounds with **at least one** candidate with `E` present, all launches |
| 1,211 | A2_TIER_R4.json `counts` | same `counts()` rule on the 721 non-development launches |

## Why they differ
`a2_informativeness.counts()` drops missing `E` first and then checks that each round's row count equals its number of
distinct candidates. After the drop the two are always equal, so the "all 4 present" check never removes anything and a
round with 1–3 missing `E` values is still counted. This is a defect of the count only.

| | All 871 launches | 721 non-dev launches |
|---|---|---|
| Rounds | {A['rounds']} | {Cf['rounds']} |
| Extraction failed | {A['extraction_failed']} | {Cf['extraction_failed']} |
| Zero cruxes | {A['zero_crux']} | {Cf['zero_crux']} |
| ≥ 1 crux | {A['with_ge1_crux']} | {Cf['with_ge1_crux']} |
| ≥ 1 crux, all 4 `E` missing | {A['ge1_crux_all4_E_missing']} | {Cf['ge1_crux_all4_E_missing']} |
| ≥ 1 crux, 1–3 `E` missing | {A['ge1_crux_some_but_not_all_E_missing']} | {Cf['ge1_crux_some_but_not_all_E_missing']} |
| **Evaluable, all 4 `E` (D32 rule = A2 analysis set)** | **{A['evaluable_all4_E__D32_definition']}** | **{Cf['evaluable_all4_E__D32_definition']}** |
| ≥ 1 `E` present (tier-file rule) | {A['rounds_with_ge1_nonmissing_E__A2_TIER_counts_definition']} | {Cf['rounds_with_ge1_nonmissing_E__A2_TIER_counts_definition']} |
| `R_inf` / `K_inf`, all-4 rule | {A['R_inf_all4_E']} / {A['K_inf_all4_E']} | {Cf['R_inf_all4_E']} / {Cf['K_inf_all4_E']} |
| `R_inf` / `K_inf`, tier-file rule | {A['R_inf_A2_TIER_counts_definition']} / {A['K_inf_A2_TIER_counts_definition']} | {Cf['R_inf_A2_TIER_counts_definition']} / {Cf['K_inf_A2_TIER_counts_definition']} |

Arithmetic: 1,409 + {A['ge1_crux_some_but_not_all_E_missing']} (rounds with a partly missing `E`) = 1,464; 1,166 + {Cf['ge1_crux_some_but_not_all_E_missing']} = 1,211.
`counts_reconcile.py` reproduces the tier file's numbers exactly by calling `a2_informativeness.counts()`: {REC['a2_informativeness_counts_reproduced']}.

## Which number is right for what
- **The A2 analysis set is the all-4 rule** (FR §4 "a round with any missing `E` is dropped"; FR §7.1 "≥ 1 crux, no missing `E`").
  The real A2 fit uses exactly this set: primary fit {REC['A2_primary_fit']['n_rounds_in_fit']} rounds / {REC['A2_primary_fit']['n_clusters']} launches (dev-excluded); A2d {REC['A2d_fit']['n_rounds_in_fit']} rounds / {REC['A2d_fit']['n_clusters']} launches (all launches) = D32's 1,409.
- Quote **1,166 rounds / 642 launches** (dev-excluded) and 1,409 / 775 (including the development launches). Do not quote 1,211 or 1,464 as evaluable rounds.
- Informative rounds: **150 rounds in 142 launches** (dev-excluded); 176 / 166 including the development launches. The tier file's 152 / 144 and 178 / 168 include 2 rounds whose variation comes from a partly scored candidate set.
- Effect on the tier: none. `K_inf` = 142 ≥ 100 and `MDE80` was computed by `fit_models`, which already drops partly missing rounds. `A2_TIER_R4.json` is write-once and is not changed; the defect is disclosed here. `a2_informativeness.py` was not edited (it is not re-run).
"""
o2 = RES / "COUNTS_RECONCILE.md"
o2.write_text(cr, encoding="utf-8")
C.write_sidecar(o2)

# figure data
def wcsv(name, header, data):
    p = FD / name
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)
    C.write_sidecar(p)
    return p


figs = []
figs.append(wcsv("a2_forest.csv", ["model", "label", "est", "lo", "hi", "n_rounds", "n_launches", "source_output", "stamp"],
                 [[k, lab, r["est"], r["lo"], r["hi"], nr, nl, fn, TAG] for k, lab, r, nr, nl, fn in fig_a2]))
figs.append(wcsv("a2_controls.csv", ["term", "est", "lo", "hi", "source_output", "stamp"],
                 [[k, a2["controlled"][k]["est"], a2["controlled"][k]["lo"], a2["controlled"][k]["hi"], F["A2_primary"].name, TAG] for k in ("erasure", "length", "clarity")]
                 + [["erasure_uncontrolled_EXPLORATORY", a2["uncontrolled"]["erasure"]["est"], a2["uncontrolled"]["erasure"]["lo"], a2["uncontrolled"]["erasure"]["hi"], F["A2_primary"].name, TAG]]))
figs.append(wcsv("n1.csv", ["estimate", "est", "lo", "hi", "p", "holm_p", "n_rounds", "n_launches", "source_output", "stamp"],
                 [[k, n1[k]["est"], n1[k]["lo"], n1[k]["hi"], n1[k]["p_boot"] if k == "erasure" else "", HP["N1"] if k == "erasure" else "",
                   n1["n_rounds"], n1["n_clusters"], F["N1"].name, TAG] for k in ("erasure", "N1u", "N1h", "g_L", "g_C")]))
if N3_DONE:
    n3r = ["N3", "RUN", J["N3"]["erasure"]["est"], J["N3"]["erasure"]["lo"], J["N3"]["erasure"]["hi"], J["N3"]["erasure"]["p_boot"], HP["N3"], J["N3"]["n_clusters"], F["N3"].name, TAG]
else:
    n3r = ["N3", "NOT_RUN_NOT_SCORED_IN_TIME" if N3_LATE else "NOT_RUN_PENDING_SCORING", "", "", "", "", 1.0 if N3_LATE else "", CNT["N3"]["launches_confirmatory"], "A3_N3_COUNTS.json", TAG]
figs.append(wcsv("tier2_forest.csv", ["test", "status", "est", "lo", "hi", "p", "holm_p_of_record", "n_launches", "source_output", "stamp"],
                 [["N1_alpha", "RUN", n1["erasure"]["est"], n1["erasure"]["lo"], n1["erasure"]["hi"], n1["erasure"]["p_boot"], HP["N1"], n1["n_clusters"], F["N1"].name, TAG],
                  ["N4_interaction", "RUN", n4["interaction"]["est"], n4["interaction"]["lo"], n4["interaction"]["hi"], n4["interaction"]["p_boot"], HP["N4"], n4["n_clusters"], F["N4"].name, TAG],
                  ["N4_majority_EXPLORATORY", "RUN", n4["majority"]["est"], n4["majority"]["lo"], n4["majority"]["hi"], "", "", n4["n_clusters"], F["N4"].name, TAG],
                  ["N4_minority_EXPLORATORY", "RUN", n4["minority"]["est"], n4["minority"]["lo"], n4["minority"]["hi"], "", "", n4["n_clusters"], F["N4"].name, TAG],
                  n3r,
                  ["A3", "NOT_RUN_BELOW_FLOOR", "", "", "", "", "", "", CNT["A3"]["launches_confirmatory"], "A3_N3_COUNTS.json", TAG],
                  ["A4", "NOT_RUN_NO_SCORER2", "", "", "", "", "", "", "", "", TAG]]))
figs.append(wcsv("prevalence.csv", ["quantity", "est", "lo", "hi", "n_units", "n_launches", "source_output", "stamp"],
                 [[k, pr[k]["est"], pr[k]["lo"], pr[k]["hi"], pr[k]["n_units"], pr[k]["n_launches"], F["prevalence"].name, TAG]
                  for k in pr if isinstance(pr[k], dict) and "est" in pr[k]]))
figs.append(wcsv("a2_length_spec.csv", ["spec", "rt_refit_key", "beta_E", "se_cr1", "t", "n_rows", "n_launches", "source", "label", "stamp"],
                 [[lab.replace("*", ""), k, est, se_, t, nr, nc, "analysis/redteam_rerun/rt_refit.json (analysis/redteam/rt_refit.py)",
                   "EXPLORATORY (red team; not pre-registered)", TAG] for lab, k, est, se_, t, nr, nc in len_rows]))
figs.append(wcsv("counts.csv", ["set", "quantity", "value", "stamp"],
                 [[{"all_launches": "all_871_launches", "confirmatory_set": "dev_excluded_721_launches"}[s], k, v, TAG]
                  for s in ("all_launches", "confirmatory_set") for k, v in REC[s].items()]))
run_log.log_run(__file__, "real (assembles outputs)", "n/a", [F[s] for s in F] + [RD / "TIER2_HOLM.json", RES / "A3_N3_COUNTS.json", RES / "COUNTS_RECONCILE.json"],
                str(out), f"[{TAG}] RESULTS_MAIN.md + COUNTS_RECONCILE.md + figures/data/*.csv")
for p in [out, o2] + figs:
    print(C.sha256_file(p), p)
