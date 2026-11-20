<!-- Front matter. Gate status of record: VALIDATED_PRESENCE (gate1/GATE1_RESULT.json, rules R5). FROZEN_RULES 6.R5.6: no directional rank claim and no "validated" in the title, so the title stays a question. -->

# Do Participants Reward Hidden Disagreement? Testing Whether Rankings of AI-Mediated Group Statements Favour Crux Erasure

Mohammed Faisal Parvez (independent researcher), mohammedfaisalparvez@gmail.com

With Apart Research

*Research conducted at the AI x Epistemics Research Sprint, November 2026*


## Abstract

<!-- Frame: VALIDATED_PRESENCE (FROZEN_RULES 6.R5.6; decisions.md D55). Editor edit 1 (report/review_editor.md) with D59/D60: SIDED clause and one exploratory N2 sentence; step-2 sentence kept in the binding scoped form (6.R5.6); hide/show stamp next to the 96% (D60 B2). No directional rank claim; no panel numbers; A2 "small and sensitive to how statement length is controlled" (D58.1).
SOURCES: 721, 1,622, 0.69 = gate1/STEP2_computed__20261116T015355Z.json; 96% = analysis/results/RESULTS_MAIN.md prevalence (0.9613); 82.8% = same table (SIDED 0.8285); 0.28 to 0.37 = analysis/n2_results/N2_RESULTS.md section 6 (SYS_system_effect 0.278-0.366). -->

AI mediators turn many people's opinions into one group statement, and participants' rankings of candidates are a natural training signal. If rankings favour statements that hide the group's real disagreement, a mediator optimised for approval would learn to hide it; we call this crux erasure. We present, to our knowledge, the first pre-registered test of whether participants' rankings favour it, on 721 held-out launches of the public Habermas Machine release. An open-weight LLM scorer takes the points of disagreement (cruxes) from the opinions alone and scores the share each candidate hides. Its detection of disagreement was validated against participants' own pre-deliberation position ratings, for whether a group disagrees, not for whether a statement hides it (balanced accuracy 0.69, 1,622 rounds); the planned author check of the hiding judgement was not done in time. By the scorer's reading (the predictor's hide/show contrast is not human-validated), 96% of candidates hid every crux, mostly by taking a side: 82.8% of crux labels are SIDED. The within-round rank test gave an association that is small, sensitive to how statement length is controlled, and not separable from raters preferring statements that state their own side (pre-registered test; the predictor's hide/show contrast is not human-validated); we draw no directional conclusion about rankings. In an exploratory grid, a "keep everyone satisfied" system prompt raised the scored share of hidden cruxes in all five open-weight models, relative to "be accurate about differences" (by 0.28 to 0.37). The data are observational, from one study's mediator.


## 1. Introduction

<!-- Editor edits 5, 6 and hostile B8 (report/review_editor.md, review_hostile.md; D60). SOURCES: 82.8% = RESULTS_MAIN.md prevalence (SIDED 0.8285); N2 = N2_RESULTS.md section 6. -->

Language models are being used as mediators in deliberation: group members write opinions on a question, a model drafts candidate statements meant to speak for the whole group, and the members rank the candidates. The Habermas Machine picks the winner by aggregating these rankings, and its statements helped groups find common ground (Tessler et al., 2024). Such rankings are also the obvious training signal for future mediators.

That creates a risk. A statement can win broad approval by leaving out, blurring or one-sidedly settling the points on which the group actually disagrees, so that each member reads it as compatible with their own view. We call this **crux erasure**: a statement hides a crux when a reader of the statement alone would not learn that members disagreed on that point. If rankings reward crux erasure, a system trained on approval will learn to hide disagreement. We frame this, as our own hypothesis, as a group analogue of sycophancy, in which preference data favour responses that match the user's views over accurate ones (Sharma et al., 2024). The original study points the other way: its revised statements "demonstrably incorporated minority critiques" (Tessler et al., 2024), on a stance measure that cannot tell a statement that names a disagreement from a vague one (Section 2). To our knowledge, prior work did not link what participants reward to disagreement-hiding content.

**Contributions.**

- To our knowledge, the first test of whether participants' rankings of candidate statements favour hiding disagreement: within-round and per-rater, with length and readability controls, pre-registered, on 721 launches held out from all prompt development.
- A crux erasure score that takes the disagreement from the opinions alone. Its detection of disagreement was validated against participants' own pre-deliberation position ratings, for whether a group disagrees, not for whether a statement hides it; its hide/show judgement is not human-validated.
- An exploratory prompt grid (N2): across five open-weight models writing for the same 250 rounds, a "keep everyone satisfied" system prompt raised scored E relative to "be accurate about differences" in all five (statements not ranked by people).
- A record of what did not work: no candidate second scorer, a human check not done in time, and an estimate that depends on the length control.

The pre-registered test gave a small association whose sign depends on whether length is controlled and whose precision depends on how (Section 4), so this paper does not settle whether participants reward hidden disagreement; it shows what such a test needs. By the scorer's reading, most hiding is one-sided (82.8% of crux labels are SIDED), so the test cannot separate rewarding hidden disagreement from rewarding a statement that states the rater's side.


## 2. Related Work

<!-- Draft note (not for the paper): All keys are in report/refs.bib and VERIFIED in report/references_verified.md. Milli et al. 2024 dropped (decisions.md D49d item 6). Wording follows decisions.md D4/D5. Never "first on erasure". Shortened for the 8-page cap; unused verified keys left out. -->

**The original study found the opposite of erasure, on a different measure.** Tessler et al. (2024) report that, although support for the majority position rose after deliberation, revised statements overweighted the minority on an embedding stance axis (0.36 against an empirical share of 0.29). That measure is a position on an agree-disagree axis and cannot tell a statement that names a disagreement from a vague mid-point one. They also report that rankings were affected by statement length, which is why we control for it. They did not test whether rankings favour statements that hide disagreement.

**Content of AI consensus statements.** Mahajan et al. (2026) find that mediator prompts seeking agreement cover minority positions much less often than prompts asking for differences (judged by LLMs only). Wan et al. (2026) show that LLM agents "can agree more while knowing less", and Zhu et al. (2025) benchmark 18 LLMs and report minority under-representation; they also find that off-the-shelf LLM judges' correlations with human ratings "never exceed 0.4", which is one reason we check our scorer against a participant signal. Zaghouani (2026) proposes an unvalidated embedding formula also called "Erasure", hence our name "crux erasure score"; coverage and fairness metrics for summaries (Zhang et al., 2024; Khosravani et al., 2024) are the closest measurement precedents. None of these tests human rankings of competing statements.

**Bridging and sycophancy.** Bridging-based ranking (Wojcik et al., 2022; Ovadya and Thorburn, 2023), quality-based comment ranking (Revel et al., 2025) and consensus-seeking opinion selection (Hafid et al., 2026) can reduce the visibility of contested or minority views, but they rank comments or opinions, not candidate group statements. Unlike individual sycophancy (Sharma et al., 2024), no single rater is flattered in the group form; each is partly pleased by a statement that does not name the clash. Our search was keyword-based, and for several cited works we read only abstracts or partial text.


## 3. Methods

<!-- Draft note (not for the paper): aligned to FROZEN_RULES.md (FR) through R5 and decisions.md through D58. SOURCES: freeze time and hash = gate1/FREEZE.json (frozen_utc, FROZEN_RULES.md sha256); counts 1,960/871/9,501 = FR §2 and figures/data/counts.csv; corrected R_inf 150 / K_inf 142 = analysis/results/RESULTS_MAIN.md (Tier) and analysis/results/COUNTS_RECONCILE.md; MDE80 0.0563 = gate1/A2_TIER_R4.json; coverage 96.5% = FR §7 [R2]; T_ready/T_cut = gate1/T_READY.txt, FR §6.R5.2; N2 spec hash = FR §7.3(c); N2 primary set includes the 45 development-launch rounds (N2 spec §1, §4; n2_results excl_dev_launch_rounds is the sensitivity). -->

Every rule below was fixed in a pre-registration (FROZEN_RULES.md, revision R5), frozen at 2026-11-16T01:53:53Z (SHA-256 `ea9b7a97…f94ae`) before any participant rating was compared with the scorer and before any scorer output was joined to a ranking. The per-status draft framings the pre-registration also required were not written before the gate (Appendix A, item 13).

**Data.** We use iteration 0 of the public Habermas Machine release (Tessler et al., 2024; Google DeepMind, n.d.), whose candidate statements are written from the members' opinions only. Rankings are per rater and rank 0 is best. A round is eligible if all opinions are human, no bot critique exists, there are exactly four model-written candidates of at least 15 words, and at least three human raters ranked all four: 1,960 rounds, 871 launches, 9,501 rater rows. **Development launches.** 150 launches were used to develop and revise the scorer prompts, and a pre-registration pilot had stored real ranks beside two crude erasure proxies for all 1,960 eligible rounds, including the held-out ones (Appendix A, item 9). The development launches are excluded from all confirmatory tests and reported only in labelled sensitivity analyses and side counts. The analysis set is the other 721 launches (1,622 rounds). Raters in a launch share opinions, so every interval resamples launches.

**Crux erasure score.** (1) Scorer 1 (Qwen3.8-27B, pinned revision, temperature 0) reads the question and the numbered opinions, never statements or rankings, and returns up to four cruxes, each with the members on each side; a crux is a point that one member asserts or prioritises and another denies or weighs very differently, and a member who did not address it is on neither side. (2) In a separate call per statement, each crux is labelled VISIBLE, SIDED (one side presented as the group's view), BLENDED (vague) or OMITTED; it is hidden unless VISIBLE. (3) E = hidden cruxes / cruxes, from 0 (shows every crux) to 1 (hides every crux). Rounds with no crux have no score; a round with a statement still unscored after one retry leaves A2 and is counted. Controls are log word count and Flesch Reading Ease, z-scored on the analysis set. A pre-registered second scorer (A4) was not run: none of four candidates (three families) met the technical bar (Appendix A, item 6).

### Checks on the score (three pre-registered steps)

No signal in the release says whether a given statement acknowledges the group's disagreement. Only step 2 is a validation, and only of disagreement presence.

- **Step 2: validation of the disagreement-presence component.** Reference `Hsplit` = 1 if at least one member rated the question at +1 or above and another at −1 or below on the 7-point scale, before deliberation and before any statement existed. Scorer call: at least one crux. Statistic: balanced accuracy `BA2` with launch- and question-cluster bootstraps (B = 10,000); the smaller lower bound decides. PASS: lower bound > 0.5 and `BA2` ≥ 0.60. Stated in advance: cruxes may lie on reasons or priorities among members on the same side of the rating axis, so specificity was expected to be low.
- **Step 3: human verification of LLM-extracted evidence by a hypothesis-aware author.** On 25 items (19 original statements, 6 N2 statements), gpt-oss-120b extracted the two most conflicting quotes from different members; the author was to answer "Do these quotes disagree?" and "Does the statement acknowledge this disagreement?" with scores, rankings, model and condition hidden, by a pre-registered cut-off (01:53Z).
- **Step 4: LLM verification of LLM-extracted evidence (supplementary; not human).** Falcon-H1-34B-Instruct, Command R7B and granite-4.2-30b (families used in no N2 or scorer role) answer the same questions; never a gate input.
- **Status.** Step 2 PASS with step 3 not done gives VALIDATED_PRESENCE: every E-based result is reported as "pre-registered test; the predictor's hide/show contrast is not human-validated", with no directional rank claim in title or abstract. Before it was recorded, analysis code ran only on shuffled ranks or dummy data.

### Analysis

- **A2, the pre-registered test.** Outcome y = (4 − midrank)/3 per rater and round (1 = ranked best). OLS with a fixed effect per (rater, round), plus E, length and readability. Estimand β_E, two-sided at 0.05; β_E > 0 means statements scored as hiding more were ranked better. 95% interval: wild cluster bootstrap-t over launches (Rademacher weights, CR1 SE, B = 10,000, seed 20261119), chosen before any real rank was read for its coverage on shuffled ranks (96.5%). Wording is observational.
- **Tier.** β_E is identified only by rounds whose candidates differ in E: 150 rounds in 142 launches (corrected; Section 4). The shuffled-rank minimum detectable effect is 0.056 on y, which gives the pre-registered INFORMATIVE tier (≥ 100 launches, ≤ 0.10), subject to a one-way downgrade check on the real-rank SE.
- **Sensitivity models** A2b, A2d–A2i: Figure 1, Table B1; length variants (exploratory): Figure B1.
- **Tier 2 (Holm family).** N1: E of each round's winner minus its average candidate, adjusted for length and readability; A3 (AI- versus human-written) and N3 (draft versus revision), each only if ≥ 30 launches qualify; N4: E × rater on the minority side of the first crux.
- **N2 (exploratory, own hashed plan `afada117…91c0`).** Five open-weight generators from five families (Qwen3.8-27B, Gemma-4-12B, Ministral-3-14B, phi-4, Llama-3.1-8B-Instruct) each wrote one statement for the same 250 rounds in five cells: system prompt "keep everyone satisfied" (SAT), "be accurate about differences" (ACC) or neutral (NEU), crossed with user prompt "find common ground" (COMMON) or "show where they disagree" (DIS), without NEU-DIS. Scorer 1 scores all 6,250 (Qwen text by its own model). Round-level paired contrasts per generator, launch-bootstrap intervals (B = 2,000), two Holm families, length-adjusted beside unadjusted. 45 of the 250 rounds come from development launches (results without them: Appendix B). Nobody ranked these statements.


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

EXPLORATORY; the scorer's hide/show call was checked on 6 N2 statements only (descriptive), and these statements were never ranked by people. With 168 to 177 usable rounds per generator, a "keep everyone satisfied" system prompt raised E relative to "be accurate about differences" in all five generators (averaged over user prompts: 0.28 to 0.37). Asking the model to show where members disagree lowered the scored E in all five (COMMON minus DIS: Gemma 0.48 [0.44, 0.53], Qwen 0.57 [0.52, 0.61], Ministral 0.58 [0.53, 0.62], phi-4 0.64 [0.60, 0.68], Llama 0.54 [0.49, 0.59]); this main effect of the user instruction was reported first by Mahajan et al. (2026). Whether the satisfaction prompt still raised E when the user asked for disagreement (C1) varied from 0.03 [0.01, 0.05] for Qwen, whose text Qwen scored, to 0.43 [0.36, 0.51] for Llama, whose interaction C3 also has the opposite sign to the other four (−0.13 [−0.23, −0.03]). Length adjustment changed no sign and no interval-versus-0 reading (Figure 2; Appendix B).

![**Figure 2.** EXPLORATORY. A "keep everyone satisfied" system prompt (SAT) raises scored E over "be accurate about differences" (ACC) in all five generators (row 2), and a user prompt to show disagreement (DIS) lowers it (row 1). How much SAT still raises E when the user asks for disagreement (C1 = SAT-DIS − ACC-DIS) varies by generator, and the interaction C3 has the opposite sign for Llama only. C2 = SAT-COM − ACC-COM; C4a and C4b compare the neutral prompt (NEU) with SAT and ACC. The scorer's hide/show call was checked on 6 N2 statements only (descriptive); statements were not ranked by humans; \* Qwen-written text is scored by Qwen (open squares). Unadjusted primary set, 168-177 rounds per generator, launch-cluster percentile bootstrap, B = 2,000.](figures/real_out/fig_n2_contrasts.png){width=5.38in}


## 5. Discussion and Limitations

<!-- Branch kept: VALIDATED_PRESENCE (gate1/GATE1_RESULT.json), step 3 NOT DONE (D53). Other branches deleted. Binding: FR 6.R5.6 (scoped wording, no confirm/confirmatory/detected for E-based results, no directional rank claim in title/abstract), FR 7 A2b rule (applied voluntarily, D58.3), D58.1-D58.4. SOURCES: as in 40_results.md. -->

**What this does and does not show.** The scorer is validated for detecting whether a disagreement is present, not for detecting whether a statement hides it, and the human check of the hiding judgement was not done; the only other reading of hide/show, an exploratory LLM panel, agreed with the scorer at chance level (κ 0.00, n = 21). The pre-registered test found a small positive association between the scored share of hidden cruxes and within-round rank (β_E = +0.051 [+0.008, +0.095]), but four facts limit what it can mean. (1) It is conditional on the registered linear log-length control: without it the sign reverses, and under five of six more flexible length adjustments it is no longer clearly separated from 0; length is by far the strongest predictor of rank. (2) It is carried by SIDED labels and majority-side raters and shrinks to the edge of 0 when similarity to the rater's own opinion is added; the data cannot separate "rewarding hidden disagreement" from "rewarding a statement that states my side", and N4's negative interaction points the same way. (3) A quarter of the identifying rounds come from groups whose members did not split on the question. (4) Only 150 rounds identify β_E. So the data do not show that participants reward hidden disagreement, and they do not show that they do not. They do show what the pre-registration anticipated: by the scorer's reading (the predictor's hide/show contrast is not human-validated), almost every candidate offered to participants (96%) hid every crux, mostly by presenting one side as the group's view, so participants were rarely offered a statement that showed the disagreement. This neither supports nor refutes Tessler et al.: their finding concerns where revised statements sit on a stance axis, ours whether points of disagreement are visible in first drafts.

**Secondary tests and N2.** N1's three versions differ in sign and all include 0; N1 is not a replication of A2. N4 has Holm-adjusted p = 0.023 with N3 at p = 1, but rests on 151 minority-side rater-rounds, extractor-assigned sides and an interval method not coverage-checked for interactions. In the exploratory N2 grid, the instruction given to the model changed the scored E of what all five generators wrote; but the hide/show call was checked on 6 N2 statements only, the Qwen figures are self-scored, and nobody ranked these statements.

**Limitations** (Appendix A). Observational data from one study and one mediator; one LLM scorer, also an N2 generator; no human judged hiding, and the author, who knew the hypothesis, did not label.

**Future work.** Candidate sets built to differ in whether they show the disagreement, ranked by people who did not write the opinions; hiding judgements from people who do not know the hypothesis; a working second scorer; a second dataset.


## 6. Conclusion

We asked whether participants in AI-mediated deliberation rank statements higher when they hide the group's real disagreement. A pre-registered within-round test on 721 held-out launches found a small association that is sensitive to how statement length is controlled and cannot be separated from raters preferring statements that state their own side, so these data do not answer the question. In an exploratory grid that nobody ranked, a "keep everyone satisfied" system prompt raised the scored share of hidden cruxes in all five open-weight models; the instruction a mediator receives may matter as much as what participants reward.  Future work: hiding labels from several independent, blind human annotators at scale (only 12 items, one author, so far), a second scorer, and N3.


## Code and Data

<!-- SOURCES: freeze = gate1/FREEZE.json; N2 hash = FR 7.3(c). -->

Data: Habermas Machine release (CC-BY 4.0) (Google DeepMind, n.d.), unmodified. Pre-registration `FROZEN_RULES.md`, frozen 2026-11-16T01:53:53Z, SHA-256 `ea9b7a97…f94ae` (`gate1/FREEZE.json`); N2 plan `afada117…91c0`. No model was fine-tuned; no weights are released. Code: https://github.com/faisalhacks/crux-erasure. Scripts, hashes and spend: Appendix B.


<div class="pb"></div>

## References

<!-- Built by hand from report/refs.bib (VERIFIED entries only), listing only keys cited in the assembled draft. build.py checks that every citation key in the text appears here and in refs.bib, and records any mismatch in checks.json. -->

Cachola, I., Khashabi, D., & Dredze, M. (2025). Evaluating the evaluators: Are readability metrics good measures of readability? In *Proceedings of EMNLP 2025* (pp. 24011-24027). https://doi.org/10.18653/v1/2025.emnlp-main.1225

Google DeepMind. (n.d.). habermas_machine (code and datasets). https://github.com/google-deepmind/habermas_machine

Hafid, S., Berriche, M., & Cointet, J.-P. (2026). Algorithmic approaches to opinion selection for online deliberation: A comparative study. arXiv:2602.15439.

Khosravani, M., Huang, C., & Trabelsi, A. (2024). Enhancing argument summarization: Prioritizing exhaustiveness in key point generation and introducing an automatic coverage evaluation metric. In *Proceedings of NAACL 2024*. arXiv:2404.11793.

Mahajan, S., Argota Sánchez-Vaquerizo, J., Capozzi, A., & Helbing, D. (2026). From opinions to commitments: Unstable assignments and silent choices in AI-mediated proposals. arXiv:2611.05135.

Ovadya, A., & Thorburn, L. (2023). Bridging systems: Open problems for countering destructive divisiveness across ranking, recommenders, and governance. arXiv:2301.09976.

Revel, M., Milli, S., Lu, T., Watson-Daniels, J., & Nickel, M. (2025). Representative ranking for deliberation in the public sphere. arXiv:2503.18962.

Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S. R., Kravec, S., Maxwell, T., McCandlish, S., Ndousse, K., Rausch, O., Schiefer, N., Yan, D., Zhang, M., & Perez, E. (2024). Towards understanding sycophancy in language models. In *ICLR 2024*. arXiv:2310.13548.

Tessler, M. H., Bakker, M. A., Jarrett, D., Sheahan, H., Chadwick, M. J., Koster, R., Evans, G., Campbell-Gillingham, L., Collins, T., Parkes, D. C., Botvinick, M., & Summerfield, C. (2024). AI can help humans find common ground in democratic deliberation. *Science, 386*(6719), eadq2852. https://doi.org/10.1126/science.adq2852

Wan, H., Wu, J., Luo, M., Li, F., Wang, N., Chen, N. F., & Kan, M.-Y. (2026). The deliberative illusion: Diagnosing factual attrition and stance homogenization in multi-agent LLM deliberation. arXiv:2606.03032.

Wojcik, S., Hilgard, S., Judd, N., Mocanu, D., Ragain, S., Hunzaker, M. B. F., Coleman, K., & Baxter, J. (2022). Birdwatch: Crowd wisdom and bridging algorithms can inform understanding and reduce the spread of misinformation. arXiv:2210.15723.

Zaghouani, W. (2026). Accountable human-AI deliberation with LLMs: Scaling collective intelligence through symbiotic scaffolding. arXiv:2605.26940.

Zhang, Y., Zhang, N., Liu, Y., Fabbri, A., Liu, J., Kamoi, R., Lu, X., Xiong, C., Zhao, J., Radev, D., McKeown, K., & Zhang, R. (2024). Fair abstractive summarization of diverse perspectives. In *Proceedings of NAACL 2024*. arXiv:2311.07884.

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. In *NeurIPS 2023 Datasets and Benchmarks Track*. arXiv:2306.05685.

Zhu, S., Yang, S., Bakker, M. A., Pentland, A., & Pei, J. (2025). Can AI truly represent your voice in deliberations? A comprehensive study of large-scale opinion aggregation with LLMs. arXiv:2510.05154 (v5, 2026).


<div class="pb"></div>

## Appendix A. Limitations and Dual-Use / Ethical Considerations

<!-- Draft note (not for the paper): items 1-4 = decisions.md D58.1-D58.4 (red-team rulings); item 9 sealed-file text = D58.6, worded as ruled; dev-launch wording = D49d item 4; Claude agents reading opinion text = D49d item 1. SOURCES: analysis/redteam/REDTEAM.md (items 1-4, 10-13, 16); analysis/results/RESULTS_MAIN.md; analysis/results/COUNTS_RECONCILE.md; gate1/STEP2_computed__20261116T015355Z.json; decisions.md D41-D48 (A4 rates), D50b (author exposure), D53 (step 3), D57 (counting defect). -->

### Limitations

1. **Length dependence.** A2 is a within-round association, not evidence that people want disagreement hidden. Its sign depends on the registered linear log-length control: without it the coefficient is −0.074 [−0.126, −0.024]; with cubic, decile, within-round-rank or raw-word length adjustments it stays positive but |t| falls to 1.35–1.98, while rank plus log length gives 2.46 (exploratory; Figure B1). Statements that show a crux are longer, and length is the strongest predictor of rank, so β_E is a small residual of a large, collinear length effect. Readability may lie on the causal path, so A2 is printed with and without it (A2h).
2. **Hiding versus "my side".** The positive coefficient comes from SIDED labels (one side presented as the group's view) and from majority-side raters (+0.100 against −0.047 for minority-side raters). Raters wrote the opinions they ranked against, so a statement that hides a crux by taking the majority's side also agrees with most raters. The design cannot separate rewarding hidden disagreement from rewarding a statement that states my side.
3. **A2b is borderline.** With similarity to the rater's own opinion added, the lower bound is +0.0002 at the registered seed and at or below 0 for 7 of 40 other bootstrap seeds. By the pre-registered rule the A2b sentence does not fire; we apply it anyway: the association cannot be clearly separated from raters preferring statements close to their own view.
4. **Specificity of the presence check.** Step 2 passed with specificity 0.484: of 614 rounds whose members did not split on the question, 317 were called as disagreeing (315 with a crux found, 2 failed extractions counted as wrong). 289 of the 1,166 A2 rounds and 39 of the 150 informative rounds come from such groups (exploratory split: β_E +0.015, SE 0.046, there; +0.066, SE 0.024, in split groups). Step 2 used ratings on one axis and validates presence of disagreement only.
5. **No human validation of hiding.** The step-3 file did not exist at the pre-registered cut-off, so no human validation of hiding entered the gate; after the gate, with results known, the author answered 12 of 25 items: the quotes disagreed in 7; of those the author judged 6 not acknowledged and 1 acknowledged; the scorer called 4 of the 6 hiding (2 had no crux found) and also called the acknowledged one hiding (kappa -0.24; below the pre-registered class minimum, so not usable). The author, who knew the hypothesis, did not label. The panel that answered the same questions is LLM verification of LLM-extracted evidence (supplementary; not human): it saw the same LLM-chosen quotes, and its numbers carry no validation weight. Compared with the scorer (exploratory, LLM-vs-LLM), it agreed at chance level (κ 0.00 [−0.39, 0.37], n = 21), and it judged a single quote pair while E summarises all cruxes. LLM judges have documented position and verbosity biases (Zheng et al., 2023).
6. **One scorer.** The pre-registered second scorer (A4) was not run: four candidates from three families (two IBM Granite models) failed the technical bar (at most 5% of development statements unscored): granite-4.2-30b 75.4% (211/280), granite-4.2-8b 57.5% (161/280), Falcon-H1-34B-Instruct 5.36% (15/280), and Command R7B, not deployable at first, 27.857% (78/280) after its licence was accepted. Every estimate rests on Qwen3.8-27B, and A2c could not run. We do not know whether β_E survives a change of scorer.
7. **Construct and variation.** Counting a one-sided statement as hiding was fixed before any result; it makes E = 1 for 96% of candidates and leaves variation in only 150 rounds (142 launches). A2e, which counts one-sided statements as shown, has the opposite sign (−0.023 [−0.052, +0.006]). Removing the 3 most influential informative launches gives +0.037 (SE 0.021). The shuffled-rank minimum detectable effect (0.056) is optimistic, which the one-way downgrade rule covers.
8. **Counting defect.** The tier file and the frozen text give 152 informative rounds in 144 launches; they counted 2 rounds with a partly missing E. The corrected counts are 150 rounds in 142 launches (176 / 166 including development launches). The INFORMATIVE tier does not change (142 ≥ 100).
9. **Development launches and the pre-gate pilot.** Before the rules were frozen, a pre-registration pilot built a feature file that placed each rater's real rank and agreement rating in the same rows as two crude erasure proxies, for all 1,960 eligible rounds. No analysis relating the two was run, and only per-display-position means (which do not use rank) were printed. The file was then sealed, and two project records said it was not touched afterwards. That was wrong: a shuffled-data test mode of our analysis code read it programmatically, permuted ranks in memory before any fit, used a dummy E proxy, and wrote only shuffled-rank outputs (9 logged test runs). No unshuffled rank statistic was computed or shown. The pilot's 150 launches, on which the scorer prompts were also tried and revised, are our development set; they are excluded from all confirmatory tests and reported only in labelled sensitivity analyses and side counts.
10. **Data.** One dataset from one study, one fine-tuned mediator and one population. Bots and cohorts are filtered out (1,960 eligible rounds), so results describe all-human, four-candidate rounds only. Raters in a launch are dependent; intervals resample launches. 40 eligible rounds show the same statement two or three times (27 in the A2 fit; excluding them gives +0.054). We cite only the main text of Tessler et al. (2024).
11. **Weak controls and uncarried uncertainty.** Flesch Reading Ease measures word and sentence length, not clarity of argument, and readability formulas correlate poorly with human judgements (Cachola et al., 2025). Scorer error is not propagated into any interval. Statements whose labels failed to parse are longer (median 98 against 87 words), so the dropped rounds are not missing at random with respect to length. The interval method's coverage was checked in advance for A2 only; a post-gate check on real E covered 0 in 191 of 200 shuffled datasets, but N1, N4 and the prevalence shares use it unchecked.
12. **N2.** The N2 statements were never ranked by people, so N2 says what models write, not what participants reward. The scorer's hide/show call was checked on 6 N2 statements only (descriptive). Qwen-written statements are scored by Qwen. Two generators often exceed the 150-word cap and one adds preambles; both are covariates or sensitivity sets, not fixed. 45 of the 250 rounds come from development launches; results without them keep every sign.
13. **Process deviations.** The pre-registration asked for one draft title, abstract and claims list per gate status, written before the gate was recorded; they were not written, and this text was written after the gate and the results were known. The analysis-set builder named in the pre-registration was never written; an integrity check shows the ranks and candidate order used equal the source file in all 9,501 rater rows. The Schulze-winner sensitivity for N1 was not run (no frozen implementation). N3 qualifies but had not run when this was written. The panel-versus-scorer comparison was listed as reported but not pre-specified to run without an author file; it was added after the results were known (decisions.md D60).
14. **Design changes before data.** The labelling design and agreement rules were changed by the human several times before any label or rating comparison existed (decisions.md D31, D34, D37, D49, D51). The sequence is logged in the pre-registration.

### Data, licence and privacy

**Attribution.** We use the Habermas Machine dataset (Tessler, Bakker et al., 2024, *Science*; © 2024 DeepMind Technologies Limited), licensed under CC BY 4.0. The accompanying code is licensed under Apache 2.0.

**What we changed.** We did not modify any record. We analyse a filtered subset (Section 3), add our own erasure scores, and quote no participant text verbatim.

**Consent.** The data were collected by the original authors under their own procedures; we make no claim about consent or approval beyond what their paper states.

**Personal data.** The release contains pseudonymous participant codes and no demographic fields. Its free-text opinions are political views. A pattern scan of all opinions and critiques found no names, contact details or postcodes; a small number disclose an age, a town, a religion or an occupation. We never print participant codes, we paraphrase rather than quote opinions, and we report rankings only in aggregate.

**Third parties.** Opinion texts were scored by open-weight models on our own Modal deployment. Claude agents (Anthropic API) also read some opinion and statement texts while inspecting scorer output and building packets; the dataset is public under CC-BY 4.0.

**No new data from people.** No new participants and no new rankings were collected. The author's verification task was not done, and no data about the author were collected.

### Dual-use considerations

**Approval-optimised mediators.** If participants' rankings reward statements that hide disagreement, a developer optimising a mediator, polling summariser or "consensus" product for approval is rewarded for hiding dissent, and an erasure scorer like ours could be used as a reward signal to do this faster rather than to audit it. We judge the added risk to be small: approval-trained systems already receive this signal implicitly, whereas auditors lack a measure of it. We document the scorer as an audit tool and recommend that deployers report erasure alongside approval. We do not publicly release the scorer prompts or serving configuration; they are available to researchers on request for audit use.

**Prompt grid (N2).** We report which system and user prompts produced more or less scored erasure, because reproducibility outweighs the small uplift; similar prompt effects are already reported (Mahajan et al., 2026). A high-erasure configuration is presented as a failure mode to test for, not a recommendation.

**What we did not do.** We did not fine-tune or release model weights or adapters, run injection tests on real participants' text or any live system, collect new human rankings, publish participant identifiers, or use mirrors of gated models.


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


## LLM Usage Statement

<!-- Required content: FROZEN_RULES 6.R5.7 "AI disclosure" (editor condition 6) and decisions.md D49d item 1. SOURCES: Claude roles = decisions.md D60 and C:/Users/intel/Downloads/OU/projects/.claude/agents/{methodologist,statistician,peer_reviewer,editor,adversary}.md (all model: opus); roles = FR §4, §6.R5.2, §6.R5.4, §10; panel result = analysis/panel/panel_p1_summary.json; step 3 not done = decisions.md D53; agents reading opinion text = D49d item 1. -->

**Models used as research instruments** (part of the method; all open-weight, served on our own Modal deployment). **gpt-oss-120b** (OpenAI) extracted the two most conflicting opinion quotes for the 25 verification items and for the panel's format-bar items; it was also format-tested as a planned annotator on 10 development items. **Qwen3.8-27B** is the only scorer: it extracted every crux and assigned every hide/show label behind every E-based number in this paper, and it is also one of the five N2 generators, so Qwen-written N2 text is scored by its own model. **Gemma-4-12B-it, Ministral-3-14B, phi-4 and Llama-3.1-8B-Instruct** wrote the other N2 statements. The **panel**, Falcon-H1-34B-Instruct, Command R7B and granite-4.2-30b, answered the two verification questions on the 25 items; all three passed the format bar, and their answers are reported only as "LLM verification of LLM-extracted evidence (supplementary; not human)". granite-4.2-30b, granite-4.2-8b, Falcon-H1-34B-Instruct and Command R7B were also tried as second scorers, on development launches only; none met the bar and none scored the analysis set. The sentence-embedding model all-MiniLM-L6-v2 computes the own-opinion similarity in A2b.

**Writing, coding and orchestration.** The project was run as an agentic pipeline of Claude models (Anthropic) in Claude Code under a human-written brief. The orchestrator was Claude Opus 5.5 (`claude-opus-5-5`). Subagents used the model set in their agent definitions (`.claude/agents/*.md` frontmatter): the methodologist, statistician, peer-reviewer, editor and adversary (red-team) roles are set to `model: opus`; general-purpose agents, used for coding, model runs and drafting, inherit the orchestrator's Opus 5.5. Agents planned the study, drafted the pre-registration, wrote and tested all analysis, serving and figure code, ran the model jobs, searched for and checked prior work, reviewed methods, statistics and ethics (including an independent re-derivation of the gate and a red-team re-analysis of the results), and drafted every section of this paper, including this statement. Every reference was opened by an agent and checked against the claim it supports (`report/references_verified.md`). While inspecting scorer output and building packets, these agents, running on Anthropic's API, read some participant opinion and statement texts from the public dataset.

**Human role.** The human wrote the brief, made every change to the labelling design and the time-out rule (decisions.md D31, D34, D37, D49, D51), accepted one model licence, and is responsible for the final text, the submission and every claim in it. The final text was drafted and reviewed by AI agents; the human directed its completion and approved its submission. The author verification (step 3) was not done by the cut-off; after the gate, with results known, the human answered 12 of the 25 items, reported only as a partial post-gate check.
