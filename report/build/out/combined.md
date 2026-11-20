# Abstract skeleton (target 150-250 words; structure only, no results)

Fill every slot from verified outputs only. Delete this note in the final.

1. **Problem (1-2 sentences).** AI mediators write a group statement from many opinions and participants rank the candidates. Systems trained on that approval could learn to hide the group's real disagreement ("crux erasure"), a group version of sycophancy (our framing).
2. **Gap (1 sentence).** Prior work measured what statements contain or what people endorse. To our knowledge this is the first test of whether participants' rankings favour statements that hide disagreement. Original study's contrary finding (minority critiques incorporated) cited here.
3. **Method (2 sentences).** Habermas Machine release, per-rater rankings [N rounds, N raters]; crux erasure score validated by blind human labels (gate 1: kappa [__], balanced-accuracy lower bound [__]).
4. **MAIN MESSAGE (plain, 1-2 sentences).** [RESULT SLOT: state in one sentence whether rankings favour erasing statements, direction, effect size with 95% CI, and whether it survives length and clarity controls. If gate 1 failed or the result is flat, say that plainly.]
5. **What it does not show (1 sentence).** [LIMITS SLOT: e.g. observational, one dataset, scorer validity, no new human study.]
6. **Implication (1 sentence).** [IMPLICATION SLOT, bounded by the result.]


# Related work (draft, target <= 0.75 page)

STATUS: every [CITE:key] is PENDING VERIFICATION until `report/references_verified.md` lists it VERIFIED. Wording follows decisions.md D4/D5. Do not write "first on erasure".

**The original study found the opposite of erasure, on a different measure.** Tessler et al. [CITE:tessler2024] (PENDING VERIFICATION) report that, although support for the majority position rose after deliberation, the Habermas Machine "demonstrably incorporated minority critiques into revised statements", and that revised statements overweighted the minority on an embedding stance axis (0.36 against an empirical share of 0.29). We take this finding seriously. Their measure is a position on an agree-disagree axis. It cannot tell a statement that names a disagreement from a vague mid-point statement. They also did not test whether participants' rankings favour statements that hide disagreement, although the system selects its winner from per-participant rankings. We ask that question and do not claim their result is wrong. We have read their main text only; the supplement is unread.

**Content of AI consensus statements.** Mahajan et al. [CITE:mahajan2026] (PENDING VERIFICATION, arXiv 2611.05135) find that LLM mediator prompts seeking agreement cover minority positions less often than prompts asking for differences. Coverage is judged by an LLM, with no human ratings. Wan et al. [CITE:wan2026] (PENDING VERIFICATION, arXiv 2606.03032) study LLM agents and report loss of issue-critical facts in consensus. Zhu et al. [CITE:zhu2025] (PENDING VERIFICATION, arXiv 2510.05154) rate how well LLM summaries represent minority views. Their ratings are for one summary per rater, with no ranking of competing candidates. Off-the-shelf LLM judges correlated with human ratings at about 0.4 or less in that work, which is why we validate our scorer against blind human labels (gate 1) rather than assume it.

**Measuring omission.** Zaghouani [CITE:zaghouani2026] (PENDING VERIFICATION, arXiv 2605.26940) proposes a metric also called "Erasure". It is an embedding formula with no validation and no ranking study. We use a different name, "crux erasure score" [FROZEN:erasure_score_name], to avoid confusion. Coverage and fairness metrics for summaries [CITE:zhang2024fairsumm; CITE:khosravani2024; CITE:shandilya2021] (PENDING VERIFICATION) are the closest measurement precedents. They are validated on constructed or small-annotator data.

**Sycophancy.** Human preference data can reward responses that match a user's views over truthful ones [CITE:sharma2023], and RLHF can raise approval without raising correctness [CITE:wen2024] (both PENDING VERIFICATION). We frame crux erasure as the group analogue of this. The framing is ours, and we found no source stating it. It differs in one respect: no single rater is flattered. Each is partly pleased by a statement that does not name the clash. Whether rankings show this is the empirical question.

**Gap.** To our knowledge, this is the first test of whether participants' rankings of candidate consensus statements favour statements that hide the group's disagreement. Prior work did not link what participants reward to disagreement-hiding content. Our search was keyword-based. Two conceptual critiques of the Habermas Machine could not be opened and are not cited [PENDING: MDPI critique; bridging-ranking and Community Notes literature not yet searched].


# Methods (draft)

STATUS: FROZEN_RULES.md was not available when this was drafted. Every definition not taken from BRIEF.md or a measured file is a placeholder `[FROZEN:xxx]`. Align to FROZEN_RULES.md when it appears. No labels or real-ranking results are used here.

## 1. Data
We use the public Habermas Machine release of Tessler et al. [CITE:tessler2024] (PENDING VERIFICATION). It is hosted at the DeepMind GCS bucket, linked from the code repository. Data are CC-BY 4.0 and code is Apache 2.0 (from the repository README, per data_gates.md).

Main file: `hm_all_candidate_comparisons.parquet`, 39,955 rows, 1,485 groups (`launch_id`), 4,492 rounds, 2,280 questions. Each row is one participant in one iteration. It holds that participant's own opinion, the other members' opinions, four candidate statements, the participant's ranking of them, and ratings. `iteration_index` 0 is the opinion round; 1 is the post-critique revision. Input sha256 `7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4`.

Filters: human raters only (35,489 HUMAN_CITIZEN rows; 4,466 BOT_CITIZEN rows excluded); degenerate candidates such as "Citizen's Jury" in early cohorts excluded; eligibility needs at least 3 raters per group [FROZEN:eligibility]. Cohort handling [FROZEN:cohorts].

**Rankings are per rater (Experiment 0).** `rankings.metadata.participant_id` equals the row's own-opinion participant id in 100% of rows. Of 8,268 multi-rater (launch, round, iteration) groups, 8,131 have differing ranking vectors over an identical candidate list. The repository code builds one ranking per citizen (`machine.py` 125-156) and derives the group ranking afterwards (line 214). Source: `analysis/EXP0_rank_unit.md`, script `analysis/exp0_check.py`. The earlier data_gates.md note that `numerical_ranks` might be group-level was resolved by this check. Raters in a group share opinions and candidates, so we resample by `launch_id`.

## 2. Pipeline
1. Build one record per (round, candidate): the round's opinions, the statement, and the per-rater ranks.
2. Extract cruxes from the opinions only, never from rankings [FROZEN:crux_extraction].
3. Score each statement. Primary scorer: per-crux judge label (preserved / blurred / erased), aggregated to a crux erasure score [FROZEN:weights] [FROZEN:judge_settings: model id, temperature, prompt hash, order swaps, repeats]. Second scorer for A4: embedding position-axis score [FROZEN:embedding_scorer].
4. Clarity: rubric LLM rating from a different model family, plus token length and Flesch-Kincaid grade [FROZEN:clarity]. Clarity may be a mediator, so we report estimates with and without it.
5. Gate 1, then the main analysis (section 4).

## 3. Gate 1: blind human validation of the scorer
Design (BRIEF section 4). The labeler sees each round's original opinions beside the statement. Rankings and AI scores are hidden. Disagreement is defined from the opinions. Each labeler gets 20 shared and 20 unique statements, plus duplicate checks [FROZEN:packet_sampling].
- Labelers: a consultant, blind to the hypothesis (L1), and an author who knows it (L2). Labels come only from `labels/L1.csv` and `labels/L2.csv`.
- Step 1: Cohen's kappa on the shared 20 before adjudication; cut-off 0.60.
- Step 2: adjudication blind to AI scores.
- Step 3: pass if the bootstrap 95% lower bound of balanced accuracy (AI scorer against adjudicated labels) exceeds 0.5. "Unsure" items are excluded and reported.
- If gate 1 fails we report the "not yet measurable" version. Definitions are not changed afterwards.
Limitation to state: 20 shared items is a small sample for kappa [FROZEN:kappa_ci]. We will report its confidence interval.
Before gate 1 is recorded, the main analysis is run only on shuffled or dummy data.

## 4. Analysis plan
- **A2 (primary):** within-round association of per-rater rank with the erasure score, controlling for length and clarity, bootstrap by group [FROZEN:model_spec] [FROZEN:primary_estimand].
- **N1:** winning statement against the average candidate in its round.
- **A4:** repeat with the second scorer.
- **A3, N3, N4** (AI vs human statements, first vs revised, minority vs majority raters) if the data allow [FROZEN:N4_side_definition].
- **N2** (new generations, 2x2 prompt grid) and **N5** are labelled exploratory unless frozen.
- Every number reports a confidence interval, script path, seed and data hash. Flat and negative results are reported. Anything not in FROZEN_RULES.md is labelled exploratory.
- Ranking hazards: a clarity control may absorb real effect; Tessler et al. note that length affects rankings. We show with-clarity and without-clarity estimates.
- Pre-gate-1 pilot disclosure: a pilot started before the brief; any real-ranking result from it is exploratory and did not shape the frozen definitions (decisions.md D1). [Fill in once the pilot reports.]


## 4. Results (TRIAL SCAFFOLD: dummy figures, no data)

PLACEHOLDER results text for layout only. It carries no claim and must be replaced by script-generated outputs.

![DUMMY figure 1 (wide). Caption must state the takeaway.](dummy1.png){width=100%}

![DUMMY figure 2 (tall).](dummy2.png){width=100%}

![DUMMY figure 3 (small, about 3 in wide: readability test).](dummy3.png){width=45%}

| Condition | Estimate | 95% CI |
|---|---|---|
| DUMMY A | 0.40 | [0.30, 0.50] |
| DUMMY matched control | 0.50 | [0.40, 0.60] |


# Appendix: Limitations and dual-use (skeleton, required)

Fill [slots] from results and from the ethics reviewer. No claims here beyond files.

## Limitations
1. **What the result does not show.** [Rankings are associations, not proof that raters prefer erasure for its own sake; a vagueness or clarity effect is a rival explanation.]
2. **Scorer validity.** Gate 1 rests on a small shared sample (20 items per labeler pair) [kappa with CI]; "unsure" items excluded [count]. LLM judges carry position and verbosity bias; second scorer is a different family.
3. **Construct.** Crux erasure is defined from opinions; the stance-axis measure in Tessler et al. is a different construct. Our result neither confirms nor refutes their minority-incorporation finding.
4. **Data.** One dataset (Habermas Machine release); cohorts and bots filtered [FROZEN:filters]; raters within a group are dependent (bootstrap by group); supplement SM 4.3.7 unread.
5. **Clarity as mediator.** Control may absorb real effect; both estimates shown.
6. **Pre-gate pilot.** A pilot began before the rules existed; its results are exploratory (D1).
7. **Exploratory items.** N2, N5 and anything outside FROZEN_RULES.md [list].
8. **Not run.** No new human study; no weights released; synthetic opinions only for injection tests [if N6 run].
9. [Negative or flat results kept: list.]

## Dual-use
- **Benefit.** Auditing whether approval-trained mediators hide disagreement.
- **Misuse paths.** [A scorer or fine-tuning recipe could be used to optimise statements for approval by hiding disagreement; prompt-injection findings (N6) could be used against mediation systems.] [Ethics reviewer to complete.]
- **Mitigations.** No fine-tuned weights released; injection tests use synthetic opinions only; data are CC-BY 4.0 public and unchanged; no human subjects added [confirm].
- **Data and privacy.** Opinions are participants' free text from a public release; [reviewer to assess re-identification risk and quoting policy].
- **Release decision.** [Code/scorer release: pending human decision. Pipeline never publishes.]
