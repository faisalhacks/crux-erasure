## Appendix B. Supplementary Methods and Results

<!-- SOURCES: B.2 = gate1/STEP2_computed__20261116T015355Z.json (reported_no_rule); B.3 = analysis/panel/panel_p1_summary.json; B.4 = figures/data/a2_forest.csv, a2_controls.csv (= analysis/results/RESULTS_MAIN.md); B.5 = RESULTS_MAIN.md, figures/data/n1.csv, tier2_forest.csv, analysis/results/A3_N3_COUNTS.json; B.6 = analysis/n2_results/n2_cells.csv and N2_RESULTS.md sections 4-6, 8; B.8 = ledger.csv; Figure B1 = figures/data/a2_length_spec.csv (analysis/redteam_rerun/rt_refit.json); Table B3 = analysis/panel/panel_vs_scorer.json (sha256 0d59c349525c7a6e4e93866db5726435dc0fe18d282dee492c806e26b93c4039). -->

- **B.1 Prompts of record.** The extraction (E1) and labelling (L1) prompts are printed verbatim in `FROZEN_RULES.md` Appendix A; their SHA-256 values are in `analysis/scorer_manifest.json` (file SHA-256 `ed64b540…f9e`, frozen with the pre-registration). The panel prompt is `analysis/panel/P1_prompt.md` (SHA-256 `9040afed…`).
- **B.2 Step 2, variants reported without a rule.** Prevalence of a member split 0.621 and of a scorer "disagreeing" call 0.755 (counting the 3 failed extractions as wrong calls, as in Table 1; 0.753 = 1,222/1,622 counting crux-found rounds only); `BA2` 0.681 in the 1,422 rounds with five rated members, 0.693 on all-rated rounds, 0.627 with a strong-split reference (≥ +2 and ≤ −2); Spearman correlation between crux count and the SD of members' ratings 0.403; no round dropped for context length. None of these can change the step-2 outcome.
- **B.3 LLM verification of LLM-extracted evidence (supplementary; not human).** All three panel models (Falcon-H1-34B-Instruct, Command R7B, granite-4.2-30b) passed the format bar (20/20 valid each on development items) and gave valid answers on all 25 items. By majority, the quotes disagreed in 21 items and the statement acknowledged the disagreement in 12. Fleiss' κ among the three models: 0.649 [0.143, 0.921] (Gwet's AC1 0.847 [0.664, 0.968]) for the first question and 0.570 [0.297, 0.787] (AC1 0.577 [0.333, 0.818]) for the second, n = 25, item bootstrap (B = 10,000). The panel saw the same LLM-chosen quotes the author would have seen. Raw agreement between pairs of panel models was 0.84 to 0.92 on the first question and 0.72 to 0.88 on the second (n = 25 each); pairwise Cohen's κ intervals are wide (for example Falcon-H1-34B versus Command R7B on the first question: 0.505 [−0.056, 0.884]).
- **B.4 Sensitivity models (Table B1).**

| Model | Change from A2 | β_E [95% CI] | Rounds / launches |
|---|---|---|---|
| A2 | primary: length + readability, development launches excluded | +0.0511 [+0.0076, +0.0952] | 1,166 / 642 |
| A2b | + similarity to the rater's own opinion | +0.0443 [+0.0002, +0.0882] | 1,166 / 642 |
| A2d | including the 150 development launches | +0.0532 [+0.0131, +0.0937] | 1,409 / 775 |
| A2e | one-sided statements counted as shown (not crux erasure) | −0.0228 [−0.0519, +0.0056] | 1,166 / 642 |
| A2f | + vagueness term rate | +0.0561 [+0.0123, +0.1000] | 1,166 / 642 |
| A2g | member-weighted E | +0.0503 [+0.0068, +0.0942] | 1,166 / 642 |
| A2h | length only, no readability control | +0.0455 [+0.0018, +0.0902] | 1,166 / 642 |
| A2i | informative rounds only | +0.0542 [+0.0082, +0.1005] | 150 / 142 |
| (exploratory) | no controls | −0.0743 [−0.1262, −0.0239] | 1,166 / 642 |

Table B1. Pre-registered test; the predictor's hide/show contrast is not human-validated. Wild cluster bootstrap-t, B = 10,000, seed 20261119. A2c was not run (no second scorer).

![**Figure B1.** EXPLORATORY (red team; not pre-registered). The A2 coefficient under alternative length adjustments, readability kept: positive under every adjustment, with |t| above 1.96 only under the registered linear log-length form (2.34), length rank plus log length (2.46) and raw word count (1.98, at the margin); without length control the sign reverses. Bars are estimate ± 1.96 × CR1 SE (approximate, not the bootstrap-t of record); 22,536 rows, 642 launches. Source: figures/data/a2_length_spec.csv.](figures/real_out/fig_a2_length.png){width=5.71in}

- **B.4b Panel versus scorer (Table B3).** EXPLORATORY, LLM-vs-LLM; not human (decisions.md D60; `analysis/panel_vs_scorer.py` → `analysis/panel/panel_vs_scorer.json`). Items where the panel majority said the quotes disagree (n = 21; 16 original, 5 N2). A = panel says the statement does not acknowledge the disagreement; S = scorer E ≥ 0.5 (0 cruxes counts as S = 0).

| | Scorer: hides (E ≥ 0.5) | Scorer: shows (E < 0.5 or 0 cruxes) |
|---|---|---|
| Panel: not acknowledged | 6 | 3 |
| Panel: acknowledged | 8 | 4 |

Table B3. Agreement 10/21 = 0.476; Cohen's κ 0.00, item-bootstrap 95% interval [−0.39, 0.37] (B = 10,000, seed 20261145). Originals 8/16 agree, N2 2/5. Of the 13 statements with E = 1, the panel majority said 7 acknowledged the disagreement (5 of 11 originals, 2 of 2 N2). The panel judged one LLM-chosen quote pair, while E summarises all of the scorer's cruxes, so agreement is bounded below 1 by design.

- **B.5 Tier-2 detail.** N1: unadjusted gap N1u −0.004 [−0.013, +0.005]; length-only N1h +0.008 [−0.002, +0.019]; 124 rounds with a tied winner excluded; slopes g_L −0.0246 [−0.0428, −0.0063] and g_C +0.0074 [−0.0079, +0.0227]. N4: 1,142 minority-side and 2,832 majority-side rater-rounds; 1,666 rater-rounds with equal sides or on neither side excluded. A3: 0 qualifying launches. N3: 713 qualifying launches (1,607 rounds); its iteration-1 statements were being scored when this was written.
- **B.6 N2 cell means.** Mean scored E per generator and cell (about 180 scored statements per cell; parse failures 0.4% to 2.4%; 69 of 250 rounds had no crux and are the same for all generators):

| Generator | SAT-COMMON | SAT-DIS | ACC-COMMON | ACC-DIS | NEU-COMMON |
|---|---|---|---|---|---|
| Gemma-4-12B | 0.830 | 0.124 | 0.267 | 0.011 | 0.622 |
| Qwen3.8-27B (self-scored) | 0.862 | 0.042 | 0.323 | 0.014 | 0.667 |
| Ministral-3-14B | 0.899 | 0.101 | 0.342 | 0.009 | 0.795 |
| phi-4 | 0.932 | 0.238 | 0.599 | 0.016 | 0.786 |
| Llama-3.1-8B | 0.947 | 0.491 | 0.644 | 0.059 | 0.853 |

Table B2. EXPLORATORY. Every pre-specified contrast (unadjusted and length-adjusted, Holm families of 10 and 15 tests, with and without development-launch, preambled, over-cap and flagged rounds), the pooled descriptive model and the rank-based C3 check are in `analysis/n2_results/N2_RESULTS.md`; one contrast figure per generator is in `figures/real_out/fig_n2_<generator>.png`. Every Holm-adjusted p for the five generators' contrasts was ≤ 0.02. No sensitivity set reversed the sign of any contrast, but this is weak evidence of robustness: the under-150-word set keeps only 6 Ministral and 26 Qwen rounds (Ministral C1 there is 0.000 [0.000, 0.000]), and phi-4's C3 interval includes 0 in that set.

- **B.7 Exploratory N5** was not run (no script was written).
- **B.8 Runs, code, hashes and compute.** Every analysis run, including flat results, is a row in `analysis/RUNS.md` with its output SHA-256. Data file `hm_all_candidate_comparisons.parquet`, SHA-256 `7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4`; A2 table `a2_long_real.parquet` `c74fa19a…c912`. Scorer `analysis/scorer.py`; gate `step2_reference.py`, `gate1_r5.py`; A2 `a2_within_round.py`, `a2i_informative.py`; tier `a2_informativeness.py`; Tier 2 `n1_winner_vs_mean.py`, `n4_minority.py`, `tier2_holm.py`; prevalence `prevalence.py`; N2 `n2_grid.py`, `n2_analysis.py`; red-team re-analysis `analysis/redteam/`; panel versus scorer `panel_vs_scorer.py`; figures `figures/make_real_figures.py`. Open-weight models were served with vLLM on Modal; total spend at list price was $15.28 through the N2 scoring run (`ledger.csv`); the N3 scoring run is not yet included.
