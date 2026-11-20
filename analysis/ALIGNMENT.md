# ALIGNMENT.md - analysis scripts vs FROZEN_RULES.md (draft) and figures/README.md

Written by the stats coder. FROZEN_RULES.md was not edited. Test results are at the end.

## Rank direction (FR s2) - confirmed from code and schema only
Rank 0 = best. Evidence (no erasure-vs-rank result was looked at):
- `data/habermas_repo/src/habermas_machine/social_choice/base_method.py:59-60`, `schulze_method.py:41-42`, `mock_method.py:37-38`, `reward_model/base_model.py:67`: "lower is better and the best candidate is thus given rank 0".
- `src/analysis/types.py:25`: `RANKING_MOCK = -1` (excluded by the eligibility filter; `live_loading.py:409-411`).
- `analysis/EXP0_rank_unit.md` (baseline agent) cites the same lines and `serialise.py:50-58` for the column `rankings.numerical_ranks`.
Not done here: the second half of FR s2 (sign of the within-rater rank vs `ratings.agreement` association). That uses ratings, not erasure, but it was outside my brief; FR says A2/N1 do not run until it is done. Scripts assume 0 = best (`y = (k - midrank)/(k-1)`).

## What changed, by FR section
| FR | Item | Before | Now |
|---|---|---|---|
| 5 | label tokens | free list of synonyms | exactly HIDES, SHOWS, NO_DISAGREEMENT, UNSURE (case/space ignored); anything else = INCOMPLETE |
| 5 | label schema | item_id,label,dup_of | exactly `item_id,label,main_disagreement,comment`, 44 rows; no dup_of column |
| 5 | dup handling | dup_of in label file | `gate1/item_key.csv` (item_id,labeler,launch_id,round_id,cand,role,dup_of); first appearance = label of record; repeats only give intra-labeler agreement (exact and 3-category match counts per labeler) |
| 5 | incomplete files | n/a | blank/invalid label, unknown/repeated/missing item_id, wrong columns/row count -> status INCOMPLETE with the rows listed; nothing filled |
| 6.2 | kappa | unsure as category or excluded | 3 categories HIDES / NOT_HIDING / UNSURE on the 20 shared items, point estimate >= 0.60 at full precision, undefined = fail; also 4-category kappa, kappa on both-definite, 4x4 table, percentile CI (B=10000, default_rng(20261116)) |
| 6.2 | order | one run | `--step kappa` writes `gate1/KAPPA.json`; `--step validity` refuses to run without it |
| 6.3 | adjudicated label | whole file | shared+agree (3-cat) = that label; shared+differ = ADJ.csv; unique = the labeler's own label |
| 6.4 | AI call | threshold 0.5 on ai_score | scores.csv `item_id,E,n_cruxes`: positive iff E >= 0.5; E < 0.5 or n_cruxes = 0 negative; blank E = wrong prediction |
| 6.4 | bootstrap | percentile over items, B variable | B=10000, `default_rng(20261116)`, one-class resample = 0.5, lower = 2.5th percentile, pass iff > 0.5 |
| 6.4 | record | `gate1.json` | `gate1/gate1_computed.json` (status PASS/FAIL/INCOMPLETE + `verdict` alias for the figure maker, confusion table, exclusions, hashes of L1, L2, ADJ, scores, item_key, FROZEN_RULES, sample). Never writes GATE1_RESULT.json |
| 6.4 | also reported | - | BA on L1's own labels, Spearman(E, human binary) |
| 6.5 / locks | real-rank lock | GATE1_PASSED.json | `P/gate1/GATE1_RESULT.json` must exist for `--kind real` |
| 6.5 | shuffle | numpy permutation | within-rater shuffle with `random.Random(424242)`, rater-rounds processed in sorted (launch, round, rater) order |
| 7 | outcome | centred rank | per rater-round mid-rank, `y = (k - midrank)/(k-1)`; all-tied raters dropped and counted |
| 7 | predictor | z-scored | E raw 0-1 |
| 7 | controls | z within round | log word count (`[A-Za-z0-9']+`) and Flesch (FR formula), z-scored over all statements of the analysis set (`common.flesch`) |
| 7 | model | pooled OLS, round-demeaned | OLS after demeaning within (rater, round) |
| 7 | bootstrap | seed 20261115, B=2000 | launch_id clusters, B=10000, default_rng(20261119), percentile CI, p = 2*min(#{b<=0}+1,#{b>=0}+1)/(B+1) |
| 7 | counts | - | rounds dropped for missing E, rounds with no E variation, launches with E variation, interpretability-floor flag (< 50 launches) |
| 7 | A2h | - | output key `A2h` (E + length, no clarity), beside `controlled` and `uncontrolled` |
| 7 | A2b-A2g, A4 | - | same script: `--params '{"controls":[...,"own_sim"]}'` (A2b), `{"predictor":"E_pos"}` (A2e), `E_w` (A2g), `{"predictor":"E2","seed":20261121}` (A4); extra columns must be in the long table |
| 8 | N1 | per-rater top choice, delta of rater | winner = lowest mean mid-rank over raters; ties for winner excluded and counted; d_r = E(winner) - mean E of 4; mean over rounds; B=10000, default_rng(20261120) |
| 8 | A3 / N3 / N4 | not written | `a3_ai_vs_human.py` (seed 20261122), `n3_draft_vs_revised.py` (20261123), `n4_minority.py` (20261124); A3/N3 return status NOT_RUN if < 30 launches qualify |
| 9 | Holm | - | `tier2_holm.py` (+ `common.holm`) over the family that ran |
| 11 | per-group fallback | y centred | `--params '{"unit":"group"}'`: y averaged over raters per statement, round fixed effect, same bootstrap. N4 refuses to run |

## Figure schema (figures/README.md)
- gate1.json (fig 1): keys `kappa.{primary,primary_ci_info_only,cutoff,n_shared,unsure_L1,unsure_L2}`, `balanced_accuracy.{ba,lo,hi,n_used,n_unsure_excluded}`, `verdict` all present in `gate1/gate1_computed.json`. File name differs: the figure maker reads `gate1.json`, so copy/rename it when real.
- a2.json (fig 2): `controlled.{erasure,length,clarity}`, `uncontrolled.erasure`, `n_clusters`, `B`, `seed` present. Key order unchanged. Extra keys (`p_boot`, `se`, counts) are additive.
- n1.json (fig 3): `erasure/length/clarity.{est,lo,hi}`, `n_clusters`, `B`, `seed` present.
- a3.json / n3.json: `{n_clusters, erasure:{est,lo,hi}}` plus `status`; when status is NOT_RUN there is no `erasure` key (the reader must treat that as "not available"). DIFF: not in the proposed schema.
- n4.json: `{minority:{est,lo,hi}, majority:{...}}` present, plus `interaction`. Definition: majority = beta_E, minority = beta_E + beta_int.
- n2.json: `n2_grid.py` belongs to the grid runner and was not touched; its output was not checked against the `cells` schema. DIFF unverified.
- a4.json: run `a2_within_round.py` with the scorer-2 predictor column (see above).

## Rules not implementable / ambiguities (FR was not edited)
1. FR s5 says ADJ.csv columns are `item_id,adj_label,reason`; FR 6.3 says `item_id, final_label, reason`. gate1.py accepts either column name. FR should pick one.
2. FR s6.1 says shared items appear with the same item_id in both packets; `item_key.csv` therefore has two rows per shared item (one per labeler). gate1.py assumes that. `dup_of` is assumed to hold the item_id of the first appearance.
3. FR s7: z-scoring "over all statements in the analysis set" is done after dropping rounds with missing E, not before (the final analysis set). The A2b `own_sim` column varies by rater, so it is z-scored over rows rather than unique statements.
4. FR s7 group fallback: the data only has per-rater vectors, so the group vector is built as the mean of the raters' `y`. The FR does not say how a group rank vector is formed.
5. FR s8 N1 per-group fallback ("group's top-ranked statement") is identical to the mean-rank winner, so no separate branch.
6. FR s4 "missing E in A2 -> whole round dropped" is implemented; "zero cruxes -> E undefined" requires the scorer runner to write NaN (not 0) for such rounds.
7. FR s6.4 Spearman and zero-crux agreement: Spearman done; "human NO_DISAGREEMENT vs AI zero cruxes" agreement is not computed (needs the label-level tokens and n_cruxes joined; add if wanted).
8. FR s4 order check (reversed crux list) belongs to the scorer runner, not to these scripts.
9. FR s7 coverage rule (>= 93% over >= 200 reshuffles): run in test_all.py (result below).
10. The shuffled-real test uses a DUMMY text proxy for E (1/(1+contestation markers per 100 words)), not an AI score; E on real data does not exist yet. log_len and flesch are the FR definitions.
11. Stale test fixtures `DUMMY_*_ai.csv` / `DUMMY_*_adjudicated.csv` and `testout/gate1_*.json`, `SYNTH_planted_er.csv`, `SYNTH_confound_len_no_er.csv` from the first version remain in analysis/ (deletion was denied by the sandbox); they are unused.

## Test results (test_all.py)
See the end of this file (filled after the run).

### Results (testout/test_stdout.txt, testout/test_results.json; all runs logged in analysis/RUNS.md)
- Synthetic planted: A2 beta_E +0.656 [0.619, 0.693] (both units); N1 mean d_r +0.157 [0.142, 0.171]; A3 +0.159 [0.139, 0.179]; N3 +0.159 [0.138, 0.179]; N4 interaction +0.929 [0.857, 1.002], majority +0.014 [-0.041, 0.069]. All recovered, sign correct.
- Confound (length drives rank, E correlated 0.6, true E effect 0): controlled A2 -0.007 [-0.048, 0.036] covers 0; uncontrolled +0.569 [0.521, 0.614] biased.
- Synthetic null coverage over 60 datasets (B=500): A2 57/60, N1 59/60.
- Habermas statements/raters, within-rater shuffled ranks (Random(424242)), DUMMY E proxy: A2 -0.003 [-0.023, 0.016] (871 launches, p=0.745), group unit identical-in-spirit -0.003 [-0.023, 0.016]; N1 -0.005 [-0.016, 0.006] (1666 rounds, 294 tied-winner rounds excluded). All cover 0.
- **FR s7 interval check FAILED its threshold: 185/200 = 92.5% coverage (< 93%), B=500, A2 primary model, 200 within-rater reshuffles.** Binding text of FR s7: below 93% the method is to be changed pre-freeze with a decisions.md entry. Not changed by me (FR read-only). Caveats: Monte Carlo SE of a 200-rep coverage near 0.93 is about 1.8 points; B=500 rather than 10000 adds extra interval noise; the earlier 36/40 run was on the old model. Suggested options for the planning room: re-run at B=10000 (costly, about 20 min), or switch the interval to a basic/BCa or a t-type bootstrap interval.
- gate1 on DUMMY fixtures: good scenario PASS (kappa 0.90, BA 0.86, lower 0.77, one parse failure counted wrong, 2 unsure excluded); bad scenario FAIL (kappa -0.35, BA lower 0.31); blank label -> INCOMPLETE; no GATE1_RESULT.json written; `--kind real` refused without GATE1_RESULT.json. Fixture "good" parameters (label accuracy 0.99) were chosen so that it passes; they are tests of the code, not of the instrument.
- Earlier incomplete run of test_all.py (killed because it was too slow, no results printed) left rows in RUNS.md; nothing was hidden.

---
## R1 update (2026-11-15/16): interval method, rank direction, informativeness tier, gate 6.4a

### Interval method of record: **wild cluster bootstrap-t (Rademacher weights, launch clusters, unrestricted residuals, CR1 SE)**
Selection run (`coverage_interval.py`, output `coverage_interval.json`, stdout `testout/coverage_stdout.txt`): 400 within-rater reshuffles of the real Habermas rankings (FR 6.5 shuffle, `random.Random(800000+i)`), DUMMY E proxy, A2 primary model, B = 2000, same design for every method.

| method | coverage of beta_E = 0 | CIs wholly above 0 / below 0 | mean width |
|---|---|---|---|
| percentile (old, not a candidate) | 387/400 = 96.75% | 10 / 3 | 0.0399 |
| cluster BCa (candidate) | 387/400 = 96.75% | 9 / 4 | 0.0399 |
| **wild cluster bootstrap-t (candidate)** | **386/400 = 96.50%** | 11 / 3 | 0.0401 |

Both candidates are >= 93%; wild is closest to 95% (96.50 vs 96.75), so by the selection rule wild is chosen. Honest reading: the two candidates differ by one reshuffle (Monte Carlo SE of a 400-rep coverage is about 1.0 point), so the choice is mechanical, not evidence that wild is better. All three methods are slightly conservative (about 96.5%, nominal 95%). The earlier 92.5% (185/200, percentile, B=500) was a different B and a different number of reshuffles; at B=2000 and 400 reshuffles the same percentile interval covers 96.75%, so the original shortfall looks like Monte Carlo/B noise rather than a real defect of the percentile interval. The rule was followed anyway (method changed, no re-run to pass).
Applied everywhere a launch-bootstrap interval is reported (A2 and variants, N1, A3, N3, N4, via `common.ols_cluster_ci`; the mean-type tests use an intercept-only regression so the same method applies). Default is `interval: "wild"` in `common.DEFAULTS`; `bca` and `percentile` remain selectable. Bootstrap p for wild = bootstrap-t p, `(#{|t*| >= |t_obs|}+1)/(B+1)` (the FR s7 p formula was written for percentile bootstrap estimates; the planning room should edit that row). Coverage was measured for A2 only; the intercept-only mean tests (N1, A3, N3) and N4 have not had their own coverage check (synthetic nulls: N1 58/60 at B=500).
Planning-room note for decisions.md: "D19 selection rule executed: wild cluster bootstrap-t chosen, coverage 386/400 = 96.50% (BCa 96.75%, percentile 96.75%) on 400 within-rater reshuffles, B=2000, DUMMY E; both candidates met the 93% bar, wild is closest to 95%; difference of one reshuffle is within noise. Blind to outcomes (shuffled ranks only)."

### FR s2 second half: rank direction CONFIRMED, 0 = best
`exp0_rank_direction.py` -> `exp0_rank_direction.json` (RUNS.md row, kind `exp0-rank-vs-rating`). Uses `rank` and the rater's own `ratings.agreement` only (no E, no text). Within-(rater, round) slope of agreement (1-7) on rank = -0.576 [-0.594, -0.557], launch-cluster bootstrap B=2000, 871 launches, 7,881 rater-rounds with variation in both; Spearman negative in 6,744, positive in 876, zero/NaN in 261. Lower rank number = higher agreement, so 0 = best, matching `base_method.py:59-60`. Source is the pilot `features.parquet` (same eligible groups as FR s2; sha256 prefix logged), not a re-read of the parquet.

### New / changed for R1
- `a2_informativeness.py` (FR 7.1): shuffles ranks with `random.Random(430000+i)`, i = 0..399, never uses real ranks; writes `P\gate1\A2_TIER.json` (`R_inf`, `K_inf`, `MDE80` = 2.80 x SD of the null beta_E point estimates, tier, counts also without the 150 development launches and for `E_pos`/`E2` if present). `--kind dummy` cannot write to P\gate1. `a2_within_round.py --kind real` now refuses without both `A2_TIER.json` and `GATE1_RESULT.json`, and records `tier_blind` and `tier_final` (one-way downgrade on 2.80 x SE > 0.10, SE only). Zero informative rounds => no fits, NOT MEASURABLE. Tested on dummy/synthetic only (`test_r1.py`): K_inf=120 varied-E synthetic -> LOW-POWER (MDE80 0.104); 30 informative launches -> NOT MEASURABLE; constant E -> NOT MEASURABLE. NOT run on real scorer E (none exists yet). The `K_inf` count assumes `E` is blank/NaN for zero-crux rounds and that a round needs all 4 candidates scored.
- `gate1.py`: ADJ accepts only `adj_label` (a `final_label` file -> INCOMPLETE); FR 6.4a block `FR_6_4a` in gate1_computed.json: `BA_crux`, `BA_sh` (with human-SHOWS count and NO_DISAGREEMENT left out), zero-crux share of correct AI negatives, `wording_rule_fires` (< 5 human SHOWS or lower bound <= 0.5), `D1h` Wilson 95% (share HIDES among non-UNSURE and among HIDES/SHOWS), optional scorer-v1 BA via `--scores-v1`. Pass rule unchanged (tested: good PASS, bad FAIL still). Items with unknown `n_cruxes` (parse failure) are excluded from BA_crux and counted. Not implemented: the "also reported" human-NO_DISAGREEMENT-vs-AI-zero-crux agreement; the scorer-v1 comparison needs the scores_v1.csv from the scorer runner.
- `run_log.py`: code hash now covers every `.py` in analysis/ (addresses METHODS_EVAL L2).
- `test_all.py` re-run with the wild default: ALL GATING TESTS PASS (its old 200-shuffle check is replaced by `coverage_interval.py`); `test_r1.py`: R1 TESTS PASS.

### METHODS_EVAL.md (analysis/eval/)
Present but its coverage and N1-length placeholders (`__COVERAGE__`, `__N1LEN__`) were still unfilled when read; it makes no interval-method recommendation other than that percentile is wrong if coverage < 93%. Items noted for follow-up: N1a (N1 has no length control: a length-driven winner can look like erasure; N1 is in the Holm family), G3 (gate BA rule slightly anti-conservative at n=20), L1/L2 (traceability of D8 numbers; code hash now broadened). Not acted on beyond L2.
