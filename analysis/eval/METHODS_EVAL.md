# METHODS_EVAL.md: methodologist evaluation of gate1 / A2 / N1 (BRIEF §9 critique protocol)

Evaluator: methodologist (fresh context, not the author; no edits made to author files).
Date: 2026-11-15. Scope: `analysis/{common,gate1,a2_within_round,n1_winner_vs_mean,run_log,test_all}.py`,
`analysis/RUNS.md`, `skills/stats_conventions.md`, BRIEF §3/§4/§5/§9, decisions.md D8, FROZEN_RULES.md (DRAFT).
Data rule kept: only synthetic data, or pilot covariates with ranks re-shuffled within rater; no real
rank was related to any covariate. Every number below cites an eval file in `analysis/eval/`.

## 0. Bottom line (read this first)

- **Coverage (GOAL 1): no undercoverage.** Pooled current-model percentile coverage is 949/1000 = 94.9%
  [93.4, 96.2]; wild (the method of record) 573/600 = 95.5% [93.5, 97.0]. Every design, including a
  hard few-cluster null, sits at 93.5-96.5% (§1). The D19 trigger (185/200) was noise: P = 7.8% under
  exact 95%. No method change is needed. Keep wild, and record in FR §7 that the choice rests on the pooled
  evidence (C1).
- **Open and material:** G1 (gate ordering not hash-locked; KAPPA.json can be overwritten), G2 (kappa
  step at n=20 has 34% power for 90%-accurate labelers), A1 (source-data hash never checked),
  A3 (the lock ignores gate status), N1a (N1 rejects 26.5% of the time under a pure length
  confound), L1/L3 (D8 numbers untraceable; outputs overwritten, unhashed).
- **Falsifier, stated plainly:** if the re-run coverage check with REAL E and shuffled ranks (C3) gives
  wild coverage whose Clopper-Pearson upper bound is below 0.93, or if A2 controlled rejects at more than
  10% in the length-confound null once real E exists, the A2 interval or its controls are wrong for this
  data and no rank claim should be made.

**The target moved during the evaluation.** At ~18:02Z (UTC) the author rewrote `common.py`,
`a2_within_round.py`, `n1_winner_vs_mean.py` and `gate1.py` to match FROZEN_RULES (see
`analysis/ALIGNMENT.md`). `a2_within_round.py` changed again between 18:13Z and 18:16Z
(`EVAL_RUNS.md` hashes 5b9c3e23 -> 3f87eb8e -> 66c741cc -> 3e9d43af). Wild became the default interval at about 18:34Z (D24),
and D21-D25 were written while this evaluation ran; D25 read an earlier draft of this file
with its placeholders unfilled. All findings and coverage numbers below are for the
**current** code (hashes in `EVAL_RUNS.md`), except where a line is explicitly marked OLD-CODE.

## 1. Coverage check (GOAL 1): verdict, no undercoverage; the 93% rule was triggered by noise

All intervals are two-sided 95%; truth is 0 in every replicate; "k/n" = intervals containing 0; brackets =
Clopper-Pearson 95% CI of the coverage. Model = A2 primary (E + z log-length + z Flesch, rater-round FE,
launch clusters), N1 = FR §8 mean-rank winner. B = 2000 per replicate (the bootstrap SE equals the
analytic CR1 SE to within 0.1-0.7% on average, `bootSE_over_CR1` 0.993-0.999, so B only moves the
interval ends by Monte Carlo noise).

| Null design | n reps | Percentile (old method) | Wild cluster bootstrap-t (method of record since D19) | CR1 t | BCa | N1 | File |
|---|---|---|---|---|---|---|---|
| Reshuffle, pilot covariates, dummy E, seeds 90000-90199 | 200 | **190/200 = 95.0%** [91.0, 97.6] | n/a (not yet in code) | 190/200 | 189/200 | 189/200 = 94.5% [90.4, 97.2] | `cov_reshuffle_200.json` |
| Reshuffle, seeds 90300-90499 | 200 | 187/200 = 93.5% [89.1, 96.5] | **187/200 = 93.5%** [89.1, 96.5] | 188/200 | 187/200 | not run | `cov_reshuffle_wild_200.json` |
| Author's synthetic generator (300 launches x 2 rounds, launch shock) | 200 | (BCa/normal shown) | **190/200 = 95.0%** [91.0, 97.6] | 191/200 | 192/200 | 188/200 = 94.0% [89.8, 96.9] | `cov_synth_new.json` |
| Hard synthetic: 60 launches, ~58 with E variation, discrete E, launch random slope on E (sd 0.3), dense ties | 200 | (BCa/normal shown) | **190/200 = 95.0%** | 191/200 | 190/200 | 193/200 = 96.5% [92.9, 98.6] | `cov_hard_null_new.json` |
| Hard synthetic + length effect 0.5, corr(E, length) 0.3, erasure effect 0 | 200 | (BCa/normal shown) | **A2 controlled 190/200 = 95.0%**; uncontrolled 121/200 = 60.5% | 189/200 | 189/200 | **147/200 = 73.5%** [66.8, 79.5] | `cov_hard_len_new.json` |

Pooled, current model, percentile interval: mine 377/400 = 94.25% [91.5, 96.3]; with the author's
`analysis/coverage_interval.json` (387/400) and the author's test_all run (185/200, ALIGNMENT.md:71):
**949/1000 = 94.9% [93.4, 96.2]**. Wild, mine plus the author's (386/400): **573/600 = 95.5% [93.5, 97.0]**.
OLD-code synthetic (pre-rewrite, `cov_synth.json`): percentile 195/200, N1 193/200 (rater) and 190/200 (group).

Reading. No interval method undercovers. In every design the methods agree replicate by replicate
(percentile, wild, CR1 and BCa differ by at most 2 of 200), so the choice of method does not matter at
871 clusters, nor at ~58 informative clusters with a launch-level random slope. Coverage does not fall
below the 93% threshold in any design except by sampling noise.

| # | Flaw | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| C1 | **The FR §7 rule "coverage < 93% over >= 200 reshuffles -> change method" fires on noise.** With true coverage exactly 95%, P(X <= 185 of 200) = 7.8% and P(X <= 186) = 13.0%. The author's 185/200 (B=500) triggered D19; the same estimator gave 387/400 at B=2000 and 190/200 in my run. The D19 selection rule ("pick >= 93% closest to 95%") then chose wild over percentile on a 386 vs 387 of 400 difference. | binomial computation in this eval; `coverage_interval.json`; decisions.md D19 | Low in consequence (wild is a sound choice and covers 95.5%); High as a precedent: a rule that changes the method on noise is a forking path | Keep wild (no reason to switch back). Before freeze, write in FR §7 that the choice rests on the pooled 1000 reshuffles above (94.9% percentile, 95.5% wild), not on the 185/200 trigger. Any future threshold rule should use the Clopper-Pearson upper bound (< 0.93 means fail) or >= 1000 replicates. |
| C2 | The FR §7 p-value formula (`2*min(#{b<=0}+1,#{b>=0}+1)/(B+1)`) is defined for percentile replicates. Under wild the code uses a different statistic, `(#{abs(t*) >= abs(t_obs)}+1)/(B+1)`. | `common.py` `ols_cluster_ci` docstring and wild branch; FROZEN §7 "Primary estimand and test" | Low-Medium (the reported p must match the frozen text) | Update the FR §7 p-value cell to the bootstrap-t formula before freeze. |
| C3 | The reshuffle null uses a dummy E that varies within round in about 800 of 871 launches. Real E (a share over 1-4 cruxes) will vary in far fewer (decisions.md D-entry on K_inf: about 57-390 launches projected). The reshuffle therefore does not test the few-informative-cluster regime. | `smoke2_reshuffle.json` `launches_with_E_variation` 800; decisions.md "K_inf" entry | Medium; mitigated | My hard synthetic design (about 58 informative launches, random slope) covers that regime at 95.0% (wild) and 96.5% (N1). Re-run one coverage check with real E (still shuffled ranks) once E exists and before ranks are read; it costs one CPU run. |
| C4 | The N1 coverage on reshuffles (189/200) was measured on the pre-`mean_ci` N1 (ratio percentile bootstrap, `n1_winner_vs_mean.py` hash 2cf3b12a). The current N1 (wild via intercept-only OLS, hash 8f3d2efa) was checked only on synthetic nulls (188/200, 193/200). | `cov_reshuffle_200.json` metas; `cov_synth_new.json`, `cov_hard_null_new.json` | Low | None needed beyond C3's re-run, which should include N1. |

Method notes: the reshuffle runs use `eval/coverage_fast.py`, which builds the author's design once and permutes ranks within rater-round. It was asserted equal to `A2.fit_models` and `N1.run` to 1e-12 on 2 permutations, under both the code it ran with and the current code ("VERIFY OK" in `log_wild_300.txt`). The author's code changed under three of the four percentile chunks (`common.py` 14fd5b0c -> 44851c7c -> 7e188533). The fast path calls only `add_y/zscore/fe_demean/ols_cluster_boot/summarize`, and the current-code verify passed. All runs were single-process, sequential, chunks of 4-10 min each, because free RAM was 0.05-2.9 GB (two `llama-server` processes from another project hold about 9.7 GB). Total local CPU was about 75 min in short chunks; nothing ran on Modal.

## 2. gate1.py against BRIEF §4 and FROZEN_RULES §5-6 (current code)

Checked and consistent (stated so the critique below is not read as total): exact token set
(`gate1.py:34`), 44-row schema and INCOMPLETE on any invalid row (`:44-63`), 3-category kappa on the
20 shared items with UNSURE as a category and >= 0.60 at full precision (`:108-131`), kappa step
writes KAPPA.json and validity refuses without it (`:157-159`), adjudication merge
(shared-agree / ADJ / unique, `:188-194`), missing E = wrong prediction (`:198-213`), one-class
resample = 0.5 (`:151`), lower = 2.5th percentile (`:221`). OLD code accepted synonyms and rejected
`NO_DISAGREEMENT` (`eval/gate1_probe.py` output: `tok('NO_DISAGREEMENT') -> ValueError`) and turned a
blank ai_score into a NEGATIVE call (`ai_v [1.0, 0.0, 0.0]`); both are fixed in the current code.

| # | Flaw | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| G1 | **Kappa step is not write-once and validity does not check that the labels are the ones kappa saw.** `--step kappa` overwrites `KAPPA.json` on every call; `--step validity` reads `K["kappa"]` but never compares `K["hashes"]` with the current L1/L2/item_key hashes. Labels edited after kappa (or kappa re-run after adjudication talk) pass silently. "Before adjudication" is enforced only by file existence. | `gate1.py:141` (unconditional write), `:160-165` (no hash comparison) | High (it is the one ordering BRIEF §4 makes explicit) | For `kind=real`: refuse to overwrite an existing KAPPA.json; in validity, recompute L1/L2/item_key SHA-256 and return INCOMPLETE on mismatch. ~10 lines. |
| G2 | **Gate 1 is badly under-powered on the kappa step at n = 20.** Two labelers who are each 90% accurate (population kappa 0.64, above the cut-off) pass kappa >= 0.60 only 34% of the time; at 95% accuracy (kappa 0.81) 67%; SD of kappa at n=20 is 0.16-0.19. A FAIL is the likely outcome even with a sound construct. | `eval/gate1_sim.json` (`kappa.acc0.9 P(kappa>=0.6)=0.344`, `acc0.95 = 0.672`, 2000 sims each, seed 777) | High (decides which paper is written); not a code bug | n=20 and 0.60 are fixed by BRIEF §4 and must not change. Before freeze, add to FROZEN §12 the sentence that a kappa FAIL at n=20 means "agreement not established", print the kappa CI (already computed, `:118`), and print this power table in the paper so a FAIL is not read as "humans disagree". |
| G3 | BA rule is mildly anti-conservative at n=20 and weak at realistic accuracies. False-pass with a chance-level AI: 3.7% (n=20) and 2.3-4.0% (n=40-60), nominal 2.5%; power at true BA 0.65 is 0.27 (n=20), 0.66 (n=60). | `eval/gate1_sim.json` (300 sims per cell, B=1000). Caveat: run against the OLD `balanced_acc`/`boot_stat` (one-class replicates dropped, not scored 0.5); the current rule is slightly more conservative. With 300 sims the false-pass CI is wide (11/300 -> CP95 ~[1.8%, 6.5%]). | Low-Medium | Report BA with the gate set size. If n_used falls well below 60 (many UNSURE), say the gate is weak. Optional, pre-freeze only: BCa or a stratified bootstrap (resample positives and negatives separately) for the BA lower bound. |
| G4 | **20 of the 60 gate labels come from the non-blind author (L2 unique items) with no adjudication.** Validity therefore partly tests the scorer against the labels of the person who knows the hypothesis. FROZEN reports BA on L1's labels only as "no rule". | `gate1.py:192-194`; FROZEN §6.4 "Also reported" | Medium (reviewers will ask; BRIEF §10 says stress the blind labelling) | Report BA on L1-only, L2-only, and all, side by side in the paper's main table, not an appendix. No rule change. |
| G5 | Sample hash can be silently null. `sha()` returns None when `gate1/sample.json` is missing, and the gate is still computed. | `gate1.py:74-75, 248` | Medium | In validity, make a missing sample.json / FROZEN_RULES.md hash an INCOMPLETE problem. |
| G6 | Duplicate checks: AI-side consistency is no longer computed; the human side is a count out of 4 per labeler. The AI is deterministic (temperature 0, FROZEN §4), so an AI duplicate check would be uninformative anyway; the human check at n=4 cannot detect anything below gross inconsistency. | `gate1.py:121-127`; FROZEN §6.1 (4 duplicates per labeler) | Low | State in the paper that the duplicate check has n=4 per labeler and is descriptive only. |
| G7 | RESOLVED during the evaluation: the ADJ column is unified to `adj_label` and `final_label` is now refused. | decisions.md (orchestrator add-on 1); current `gate1.py:170` | Closed | None. |
| G8 | Kappa bootstrap CI drops undefined replicates (conditioning on two categories present), so the "info only" interval is slightly narrow. | `gate1.py:115-118` | Low (info-only) | Score undefined replicates as 0 or report the number dropped. |

## 3. A2: within-round model (current code)

Verified from the data structure (structure only; ranks shuffled; `eval/structure.json`, `eval/ties.py`):
1,960 rounds, all with exactly 4 candidates; 9,501 rater-rounds; 3-5 raters per round; every rater ranks all
4 candidates (0 subsets); 871 launch clusters, 1-3 rounds per launch; **0 of 4,255 raters appear in more
than one launch**, so launch is a valid top-level cluster for rater dependence. Ranks are **dense-coded**
when tied (patterns `(0,1,2,2)` 272, `(0,1,1,2)` 224, `(0,1,1,1)` 122, `(0,0,1,2)` 109, `(0,0,0,1)` 68,
`(0,0,1,1)` 46, all-tied `(0,0,0,0)` 30; 871 of 9,501 rater-rounds = 9.2% have a tie).

Checked and consistent: mid-ranks via `rank(method="average")` on dense codes give correct mid-ranks
(`common.py:165`), `y=(k-mid)/(k-1)` scales by k (`:170`), all-tied raters dropped and counted (`:168-169`),
(rater, round) fixed effects by demeaning (`common.py:187-189`), E raw, controls z-scored over statements,
launch-cluster bootstrap carrying all rounds/raters (`common.py:211-223`), A2h (length only) reported
beside the primary (`a2_within_round.py:38-39`), interpretability-floor flag (`:41-45`).
The OLD code used dense ranks without mid-ranking, standardised E per within-round SD, and had no A2h.

| # | Flaw | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| A1 | **Source-data hash is never checked.** FROZEN §2 says every script re-checks the SHA-256 of `hm_all_candidate_comparisons.parquet` and stops on mismatch; stats_conventions says a mismatch stops the run. No analysis script does this; `read_long` accepts any CSV/parquet. | `grep 7cf8\|mismatch analysis/*.py` returns nothing; `common.py:151-156` | Medium-High (hard rule 4 traceability) | `read_long`: require a sidecar manifest naming the source parquet hash and `build_analysis_set.py` counts; `sys.exit` on mismatch for `kind=real`. |
| A2 | PARTLY RESOLVED during the evaluation: rank direction is now confirmed (decisions.md D24, slope -0.576 [-0.594, -0.557]), and the real-run lock now also requires `gate1/A2_TIER.json` (`common.py:60-61`). There is still no machine-readable record of the direction check that the lock reads. | decisions.md D24; `common.py:57-63` | Low | Write D24's number to `gate1/RANK_DIRECTION.json` and check that it exists in `check_kind('real')`. |
| A3 | **The real-run lock does not read the gate status.** `check_kind` unlocks on the existence of GATE1_RESULT.json; after a FAIL, FROZEN §12 allows real runs only as "exploratory, unvalidated instrument". Outputs are not tagged that way. | `common.py:59-60` | Medium | Read `status` from GATE1_RESULT.json; if not PASS, stamp every output and RUNS.md row `EXPLORATORY_UNVALIDATED`. |
| A4 | **Clarity as mediator is handled only by reporting A2h; the primary keeps clarity.** If hiding a crux makes text smoother, `beta_E` (controlled) estimates a direct effect and understates the total. A2h answers this, but A2h still conditions on length, which is also plausibly downstream of the writing choice (omitting a crux shortens text). | `a2_within_round.py:38-39`; FROZEN §7 A2h | Medium (interpretation, not validity) | Pre-freeze: state the estimand in words (direct effect net of length and Flesch). The uncontrolled model (already computed) is the total-effect read; promote it to the A2h sentence: "if controlled, A2h and uncontrolled differ in sign or significance, say so". |
| A5 | **Linear length and Flesch controls cannot absorb a non-linear scorer bias.** LLM judges are length-sensitive; if mis-scoring of E depends non-linearly on length, residual confounding survives `z_log_len`. | FROZEN §7 control definitions; `common.py:179-184` | Medium | Pre-freeze sensitivity (one line in FROZEN §7): add length as a 4-knot natural spline (or quintile dummies). Costs one extra fit. |
| A6 | Self-interest (own-opinion similarity) is only a sensitivity model (A2b); the primary is open to it. | FROZEN §7 A2b | Medium (already mitigated by A2b's binding wording rule) | None beyond A2b; keep the wording rule. |
| A7 | **Group-unit fallback equals the rater unit in balanced data, so it is not an independent check.** With equal raters per round, averaging y over raters gives the same OLS point estimate and the same cluster-bootstrap interval (OLD test_results: rater and group both `+0.520 [+0.491,+0.548]`). Real data have 3-5 raters, so only the weights differ. | `analysis/testout/test_results.json` (OLD code) "A2 planted effect recovered (rater/group)" | Low | Do not present group-unit agreement as robustness. |
| A8 | Not every rule is guarded in code: complete rankings (each rater ranks all k) are assumed by FE demeaning together with statement-level z-scores; true in this dataset (0 partial rankers), unchecked for other inputs. | `eval/structure.json` `rater_rounds_ranking_subset_of_round: 0`; no assert in `common.add_y` | Low | `assert` complete rankings in `add_y`. |
| A9 | `only_primary` and other params are silently accepted; any typo in `--params` is ignored rather than refused. | `common.load_params:40-45` (dict.update, no key validation) | Low | Reject unknown keys. |

## 4. N1 (current code)

| # | Flaw | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| N1a | **N1 has no length/clarity control, so it detects length-driven wins as erasure.** In the synthetic design with zero erasure effect, a length effect and corr(E, length) = 0.3, the N1 interval excludes 0 far more often than 5%, while A2 controlled stays near nominal. | `cov_hard_len_new.json`: N1 covers 0 in 147/200 = 73.5% [66.8, 79.5] (false-positive rate 26.5%), mean N1 = +0.043; A2 controlled 190/200 = 95.0%; A2 uncontrolled 121/200. | Medium (N1 is in the Holm family; a "significant" N1 can be length) | Report N1 only beside A2, with the length and clarity deltas (already computed) in the same table row; add a residualised N1 (E residualised on z_len, z_flesch within round) as a pre-specified sensitivity. |
| N1b | **Winner ties exclude about 14% of rounds**, chosen by the outcome. Under the null this is symmetric, but under an effect it drops rounds where raters split, which are plausibly the rounds where candidates differ least in E. | Reshuffle: 276.9 of 1,960 rounds excluded per replicate (14.1%, `cov_reshuffle_200.json` `N1_tied_excluded`); author synth 110 of 600 (18%). | Low-Medium | Report the tie count (already done) and a sensitivity with tied winners averaged (the OLD code's rule) next to the Schulze sensitivity. |
| N1c | N1 is computed from the same ranks and E as A2 and is close to a coarsened A2. It is not independent corroboration. | definitions in FROZEN §7-8 | Low | In the text, never call N1 a replication of A2. |

## 5. Logging / traceability (BRIEF rule 4)

| # | Flaw | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| L1 | **D8's numbers cannot be traced to a logged run or to code that still exists.** decisions.md D8 cites "Synthetic nulls: A2 56/60, N1 57/60"; no RUNS.md row reports 56/60 (the only synthetic-coverage row says 57/60 and 59/60 and comes from the NEW code, 18:06:20Z). The code that produced 36/40 and 56/60 was overwritten in place (no VCS; the project is not a git repository). | `analysis/RUNS.md` rows 17, 32, 48; `decisions.md:49` | High for the rule; the numbers themselves are superseded | Snapshot the code on every logged run (copy the scripts into `analysis/runs/<code_hash>/`, or a local-only `git init` with a commit per run, never pushed), and log synthetic-coverage loops as rows. Mark D8's 56/60 as UNTRACED in decisions.md. |
| L2 | RESOLVED during the evaluation for new rows: `code_hash` now hashes every `analysis/*.py`. Rows written before the change (including those that hold the D8 numbers) still pin only script + common + run_log. | current `run_log.py:29-35`; RUNS.md rows 5-48 | Low | None for new rows; treat old rows as in L1. |
| L3 | **Output files are overwritten at a fixed path and their hash is not logged**, so an old row's number cannot be checked against its output (e.g. rows 5 and 20 both point to `testout/a2_planted_rater.json`). | `analysis/RUNS.md` rows 5, 20 | Medium | Log the output SHA-256 in the row; write outputs to `<name>_<utc>.json`. |
| L4 | Library versions are not logged, though `skills/stats_conventions.md:13` requires it. | `run_log.py:376-378` (row format) | Low | Append python/numpy/pandas/scipy versions to the note. |
| L5 | Input hashes are truncated to 16 hex characters (64 bits). Enough to detect accidental change. | `run_log.py:374` | Info | None needed. |
| L6 | My own run log had the same defect: `cov_synth.json` (OLD-code run) logged code hashes computed at the end, after the author's rewrite. Corrected in `EVAL_RUNS.md` (CORRECTION row). The harness now hashes at start and flags `changed=`. | `eval/EVAL_RUNS.md` | Info | Done. |

## 6. Reproducibility checklist (current state)

| Item | State |
|---|---|
| Script, seed, input hash per run in RUNS.md | Yes for single runs; loops partly (L1) |
| Code version pinned per run | New rows: yes, the hash covers all analysis/*.py (L2). Old code is not retained, so old rows cannot be reproduced (L1) |
| Output hash per run | No (L3) |
| Library versions | No (L4) |
| Source parquet hash checked at run time | No (A1) |
| Rank direction confirmed | Yes (D24); not machine-checked by the lock (A2) |
| Gate ordering enforced by code | Partly (G1) |
| Determinism (same seed, same output) | Not tested by the author; the fast-path equality check matched the author's A2/N1 to 1e-12 on 2 permutations (`eval/coverage_fast.py --verify`) |
| Real-rank lock | Yes (existence of GATE1_RESULT.json), status not read (A3) |

## 7. Falsifiers (what would show this method is wrong)

1. **Interval method.** If the empirical coverage of A2 `beta_E` over >= 200 within-rater reshuffles falls
   below 93% (FROZEN §7), the percentile cluster bootstrap is wrong for this design. Measured: see §1.
2. **Confound control.** If, in synthetic data with a planted length effect and zero erasure effect, A2
   (controlled) rejects at well above 5%, the controls are not doing their job. Measured: see §1 (synth_hard len=0.5).
3. **Instrument.** If gate 1 passes but BA on L1-only (blind) labels is <= 0.5 while BA on L2-only labels
   is high, the validation is driven by the non-blind labeler (G4).
4. **Mediator.** If `beta_E` controlled and uncontrolled differ in sign, the headline depends on an
   untestable causal ordering of clarity and erasure; no directional claim.
