## 4. Results

<!-- Gate status VALIDATED_PRESENCE (gate1/GATE1_RESULT.json). Every E-based result: "pre-registered test; the predictor's hide/show contrast is not human-validated". Banned for E-based results: confirm / confirmatory / detected. Edits from report/review_editor.md (2-4, 8-11, 13) and review_hostile.md (A1, B2, B6, B9) per decisions.md D60.
SOURCES (every number in this section):
- Counts 1,622 / 721; drops 397 + 3 + 11 + 45 = 456; 1,166 rounds / 642 launches / 22,536 rows; R_inf 150 / K_inf 142: analysis/results/RESULTS_MAIN.md (A2 note, Tier), analysis/redteam/REDTEAM.md item (2), figures/data/counts.csv.
- Step 2 (BA2 0.6918, CIs, sens 0.900, spec 0.484, confusion 907/101/297/317, classes 614/437 and 1,008/605, 3 failed extractions): gate1/STEP2_computed__20261116T015355Z.json. 315 + 2 and 100 + 1 split: gate1/step2_private/rounds__20261116T015355Z.csv cross-tab (hsplit x ext_ok x n_cruxes>0), also review_hostile.md A1.
- 289/1,166 and 39/150 rounds with Hsplit = 0: REDTEAM.md item 4; D58.4.
- Panel vs scorer (21 items, agreement 0.476, kappa 0.00 [-0.39, 0.37], 13 E=1 items with 7 acknowledged): analysis/panel/panel_vs_scorer.json (sha256 0d59c349...4039; RUNS.md row 2026-11-16T02:53:46Z).
- Prevalence: RESULTS_MAIN.md prevalence table; figures/data/prevalence.csv.
- A2 and sensitivities, beta_L, beta_C, one-way check 0.0610, uncontrolled -0.0743: RESULTS_MAIN.md; figures/data/a2_forest.csv, a2_controls.csv.
- Length specs (t 2.34; 1.82, 1.72, 1.35, 2.46, 1.98, 1.69): figures/data/a2_length_spec.csv (analysis/redteam_rerun/rt_refit.json). SIDED/BLENDED split, leave-out, null coverage 191/200, A2b seeds 7 of 40: REDTEAM.md items 2, 3, 8, 10; D58.1-3.
- N1, N4, Holm, A3/N3 counts: RESULTS_MAIN.md; figures/data/tier2_forest.csv, n1.csv; N4 informative counts 114/106/151: REDTEAM.md item 5; D58.5.
- N2: analysis/n2_results/N2_RESULTS.md sections 1, 4, 5, 6; n2_estimates.csv.
-->

### Sample

Of 1,622 rounds (721 launches), 456 left A2 (397 with no crux; 3 extraction failures; 56 with unscored statements), leaving 1,166 rounds, 642 launches and 22,536 rater-statement rows; only 150 rounds (142 launches) have candidates that differ in E (corrected counts, Appendix A item 8).

### Validation of the disagreement-presence component (step 2)

Over all 1,622 rounds (721 launches), balanced accuracy was `BA2` = 0.692 (launch-cluster 95% interval [0.669, 0.714]; question-cluster [0.670, 0.713]), above both pre-registered bars: PASS. Sensitivity was 0.900 but specificity only 0.484 (Table 1): of the 614 rounds whose members did not split on the question, 317 were called as disagreeing (315 with a crux found, 2 failed extractions counted as wrong calls). Low specificity was expected in advance, but it matters for A2: 289 of the 1,166 A2 rounds, and 39 of the 150 rounds that identify β_E, come from groups whose members did not split.

| | Split: 1,008 rounds, 605 launches | Not split: 614 rounds, 437 launches |
|---|---|---|
| Called disagreeing\* | 907 | 317 |
| Called not disagreeing\* | 101 | 297 |

Table 1. Step 2, round level. \*Includes 3 extraction failures counted as wrong, as pre-registered: 2 in the 317 and 1 in the 101.

**Step 3 was not done by the cut-off;** E is not human-validated. A later, results-aware partial check (12 of 25 items; Appendix A item 5) was too small to use. <!-- analysis/results/VERIFICATION_PARTIAL12.json; D65 -->

**LLM verification (supplementary; not human).** Three LLMs answered the step-3 questions on the 25 items; they saw the same LLM-chosen quotes, and their answers carry no validation weight (Appendix B.3). EXPLORATORY, LLM-vs-LLM; not human: on the 21 items where the panel majority said the quotes disagree, the panel's "not acknowledged" matched the scorer's E ≥ 0.5 call in 10 of 21 (agreement 0.48, Cohen's κ 0.00 [−0.39, 0.37]); of the 13 such statements the scorer read as hiding every crux, the panel said 7 acknowledged the disagreement (Table B3).

**How often statements hide disagreement, by the scorer's reading (pre-specified descriptive; the predictor's hide/show contrast is not human-validated).** Of 4,780 scored candidates in rounds with at least one crux, 96.1% [95.5, 96.7] hid every crux and 3.9% [3.3, 4.5] showed at least one. Of 6,628 crux labels, 82.8% were SIDED, 9.0% OMITTED, 4.9% BLENDED and 3.2% VISIBLE. Hiding a disagreement here mostly means presenting one side as the group's view.

### Within-round rank and crux erasure (A2)

Pre-registered test; the predictor's hide/show contrast is not human-validated. With length and readability controlled, β_E = +0.051 (95% interval [+0.008, +0.095], p = 0.024; 1,166 rounds, 642 launches) on the 0-1 rank scale, about 0.15 of a rank position between a statement scored as hiding every crux and one showing every crux. Length dominates the model (β_L = +0.167 [+0.158, +0.176] per SD of log length; readability β_C = −0.026 [−0.035, −0.017]). The one-way check (2.80 × SE = 0.061 ≤ 0.10) keeps the tier INFORMATIVE. The sensitivity models keep the sign (Figure 1), except A2e, which counts one-sided statements as shown: −0.023 [−0.052, +0.006].

![**Figure 1.** All pre-registered variants that control length give small positive estimates. Removing the length control (bottom row) reverses the sign, as does counting one-sided statements as shown (A2e); most flexible length adjustments (Figure B1) weaken it. Pre-registered test; the predictor's hide/show contrast is not human-validated. \* A2e does not measure crux erasure; the no-controls row is not pre-registered. 1,166 rounds / 642 launches (A2i 150 / 142; A2d 1,409 / 775), wild cluster bootstrap-t, B = 10,000.](figures/real_out/fig_a2_forest.png){width=5.23in}

**The estimate depends on the length control (exploratory, not pre-registered).** Without any control the sign reverses (−0.074 [−0.126, −0.024]): statements that show a crux are longer, and longer statements are ranked better. Of six alternative length adjustments, five keep the sign but lower |t| from 2.34 to between 1.35 and 1.98, and one (length rank plus log length) gives 2.46 (Figure B1). Removing the 3 most influential of the 142 informative launches gives +0.037 (SE 0.021). On real E with shuffled ranks, the interval method covered 0 in 191 of 200 datasets (post-gate check).

**"Hides" cannot be separated from "states my side" (exploratory).** Splitting E, the SIDED share carries the association (+0.053, SE 0.022) more than BLENDED or OMITTED (+0.028, SE 0.026). Raters on the majority side of the first crux show +0.100 [+0.037, +0.163], minority-side raters −0.047 [−0.131, +0.039]. A2b, which adds similarity to the rater's own opinion, gives +0.044 [+0.0002, +0.088], a lower bound at or below 0 for 7 of 40 other seeds: the association cannot be clearly separated from raters preferring statements close to their own view.

### Secondary tests (Tier 2, Holm family)

Pre-registered tests; the predictor's hide/show contrast is not human-validated. **N1** (winner minus average candidate, adjusted): α = +0.008 [−0.002, +0.019], p = 0.115 (1,042 rounds, 612 launches; 132 rounds with a non-zero gap). Unadjusted and length-only versions differ in sign and all three intervals include 0 (Appendix B.5). **N4** (E × minority-side rater): −0.147 [−0.252, −0.041], p = 0.008 (592 launches), resting on 114 informative rounds in 106 launches with 151 minority-side rater-rounds in them; the sides come from the LLM extractor and were not validated. **N3** (iteration 1 vs 0; 713 qualifying launches) was not run: the scorer app did not start (infrastructure), not a data decision. **Holm** of record therefore counts N3 at p = 1: N1 0.231, N4 0.023 (without N3: 0.115 and 0.016). <!-- D61; analysis/results/N3_STATUS.json; RESULTS_MAIN.md sha 5a0653b4 --> **A3** was not run (0 qualifying launches, floor 30) and **A4** was not run (no second scorer).

### What current models write under different instructions (N2, exploratory)

EXPLORATORY; the scorer's hide/show call was checked on 6 N2 statements only (descriptive), and these statements were never ranked by people. With 168 to 177 usable rounds per generator, a "keep everyone satisfied" system prompt raised E relative to "be accurate about differences" in all five generators (averaged over user prompts: 0.28 to 0.37). Asking the model to show where members disagree lowered the scored E in all five (COMMON minus DIS: Gemma 0.48 [0.44, 0.53], Qwen 0.57 [0.52, 0.61], Ministral 0.58 [0.53, 0.62], phi-4 0.64 [0.60, 0.68], Llama 0.54 [0.49, 0.59]); this main effect of the user instruction was reported first by Mahajan et al. [CITE:mahajan2026commitments]. Whether the satisfaction prompt still raised E when the user asked for disagreement (C1) varied from 0.03 [0.01, 0.05] for Qwen, whose text Qwen scored, to 0.43 [0.36, 0.51] for Llama, whose interaction C3 also has the opposite sign to the other four (−0.13 [−0.23, −0.03]). Length adjustment changed no sign and no interval-versus-0 reading (Figure 2; Appendix B).

![**Figure 2.** EXPLORATORY. A "keep everyone satisfied" system prompt (SAT) raises scored E over "be accurate about differences" (ACC) in all five generators (row 2), and a user prompt to show disagreement (DIS) lowers it (row 1). How much SAT still raises E when the user asks for disagreement (C1 = SAT-DIS − ACC-DIS) varies by generator, and the interaction C3 has the opposite sign for Llama only. C2 = SAT-COM − ACC-COM; C4a and C4b compare the neutral prompt (NEU) with SAT and ACC. The scorer's hide/show call was checked on 6 N2 statements only (descriptive); statements were not ranked by humans; \* Qwen-written text is scored by Qwen (open squares). Unadjusted primary set, 168-177 rounds per generator, launch-cluster percentile bootstrap, B = 2,000.](figures/real_out/fig_n2_contrasts.png){width=5.38in}
