# R5 vote: statistician

**Vote: APPROVE-WITH-CONDITIONS.**

Blind: I read no scores, ranks, rating values or labels, and computed no reference value. I ran two synthetic simulations: `analysis\planning\r5_stat_council_sim.py` → `.json` and `r5_stat_council_sim2.py` → `.json` (seeds 4242 and 4243).

What the simulations show (synthetic only). BA2 does not depend on prevalence, so it is a sound choice. A scorer that finds a crux in nearly every round gets BA2 ≈ 0.50 and FAILs, which is the right result. The launch bootstrap's false-pass rate (LB > 0.5 when there is no signal) was 0.7–2.7%. With only 30 rounds in the Hsplit=0 class, the CI width for a true-0.60 scorer is about 0.155. At 50 rounds it is about 0.12, and at 100 rounds about 0.08. P(PASS) for a true BA of 0.60 is about 0.5 at every imbalance level, so the point bar is a coin flip at its own threshold. That is acceptable only because the bar is stated in advance. In the synthetic data, a scorer driven only by group size did not pass.

## Binding conditions

1. **Raise the step-2 class minimums.** Each `Hsplit` class needs ≥ 50 usable rounds from ≥ 25 launches. Below that, the result is UNUSABLE.
2. **Count one-class bootstrap resamples.** Report the count. If more than 1% of the B resamples have only one class, step 2 is UNUSABLE.
3. **Question clustering.** If any `q_r` appears in more than one launch, also run a question-cluster bootstrap with the same B and seed+1. The PASS/WEAK/FAIL outcome then uses the smaller of the two lower bounds.
4. **Report these step-2 numbers, with no rule attached:** the prevalence of `Hsplit` and of `Sdis`, and BA2 within the `n_rated == 5` stratum. Rounds dropped for context length: if they are more than 5% of eligible rounds, also report BA2 with those rounds scored as wrong calls.
5. **Only the primary BA2 sets the step-2 outcome.** None of the "also reported" variants (strong split, all-rated, Spearman, stratum, cluster sensitivity, except as in condition 3) can change PASS/WEAK/FAIL. A unit test asserts this.
6. **Reword CONTRADICTED.** "agreed with the author no better than chance" becomes "point balanced accuracy ≤ 0.5 (n = …, bootstrap 95% CI …)". A point estimate at n ≤ 25 does not show chance-level agreement.
7. **Re-run `r5_step3_power.py` before the freeze** with the ≥ 3-per-class usable rule applied. Report P(UNUSABLE) for each cell, and print those figures in the place of the §R5.2.4 numbers.
8. **Step-3 fixed choices.** The Fisher test is one-sided and conditional (scipy `fisher_exact`, `alternative="greater"` on the S×A table). There is no mid-p. Kappa and BA3 bootstrap resamples that have one class are counted and reported.
9. **Panel statistics.** Report each kappa or AC1 with its bootstrap CI and n. No panel number is described with "agreement was good/substantial".

## Open questions

1. **Yes, use the scoped wording.** The bare phrase would overstate, because step 2 covers only component (a), the presence of disagreement.
2. **Acceptable as step 2 if it is labelled "presence only".** Statistically it says nothing about E's within-round contrast. So under VALIDATED_PRESENCE, A2 is a confirmatory test of an association with an *unvalidated* exposure, and the §R5.6 wording must stay.
3. **Keep LB > 0.5 plus a point BA2 ≥ 0.60.** With about 1,600 rounds, LB > 0.5 alone tests only "not exactly chance". An equivalent alternative is LB ≥ 0.55. I prefer the proposal's form.
4. **Exclude gpt-oss.** It would be judging its own extraction, which biases Q1. Statistically, P2 is model-on-model with no human anchor and adds forking paths. Drop it, or fix its output to the appendix with no text claim.
5. **Confirm.** Usable data that do not support the scorer must not count as validation.
6. **No.** At n = 10–12, a 70%-accurate scorer is CONTRADICTED with probability 0.10–0.23 (`r5_step3_power.json`). Failing the gate on that would be mostly noise.
7. **Yes.** Six items give essentially no power. N2_VALIDATED cannot be justified.
8. **Approve both in advance only if** each one has a single pre-stated estimand and test, written into R5 before the freeze, and is stamped EXPLORATORY. Otherwise leave both out.
