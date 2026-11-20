# Appendix: Limitations and dual-use (skeleton, required)

Fill [slots] from results and from the ethics reviewer. No claims here beyond files.

## Limitations
1. **What the result does not show.** [Rankings are associations, not proof that raters prefer erasure for its own sake; a vagueness or clarity effect is a rival explanation.]
2. **Scorer validity.** Gate 1 rests on a small shared sample (20 shared items; kappa interval is wide at n = 20) [kappa with CI]; "unsure" items excluded [count]. LLM judges carry position and verbosity bias; second scorer is a different family.
3. **Construct.** Crux erasure is defined from opinions; the stance-axis measure in Tessler et al. is a different construct. Our result neither confirms nor refutes their minority-incorporation finding.
4. **Data.** One dataset (Habermas Machine release); cohorts and bots filtered (all-human, four-candidate subset: 1,960 of 4,492 rounds, FR §2); raters within a group are dependent (bootstrap by group); we cite only the main text of Tessler et al. [CITE:tessler2024habermas]; the supplement could not be opened.
5. **Clarity as mediator.** Control may absorb real effect; both estimates shown.
6. **Pre-gate pilot.** Before the rules were frozen, a pre-registration pilot built a feature file that placed each rater's real rank and agreement rating in the same rows as two crude erasure proxies, for all 1,960 eligible rounds. No analysis relating the two was run: its analysis script never ran, no model, plot or summary of rank against any erasure score exists, and only per-display-position means (which do not use rank) were printed. The file was sealed and is not used anywhere in this study. The pilot's 150 rounds are our development set. They are excluded from gate-1 sampling, and A2 is reported both with and without them (A2d). (decisions.md D33.)
7. **Exploratory items.** N2, N5 and anything outside FROZEN_RULES.md [list].
8. **Not run.** No new human study; no weights released; synthetic opinions only for injection tests [if N6 run].
9. [Negative or flat results kept: list.]

### Weaknesses of the frozen design (from FROZEN_RULES.md, "Known weaknesses")
10. **One-sided statements count as hiding.** A statement that gives only one side of a crux counts as hiding it. This was a construct choice made before any result. It may push E close to 1 for most machine-written statements, leaving little variation within rounds. A2e and the 50-launch floor show this but do not fix it.
11. **Small, unstratified gate sample.** The gate uses 60 statements, 20 shared, drawn at random. If one class is rare, the lower bound on balanced accuracy can stay at or below 0.5 even for a good scorer, and kappa from 20 items is very imprecise. The gate can fail for lack of data rather than lack of validity.
12. **Gate tests the whole instrument, not its parts.** Humans label the whole statement. The AI score is built from AI-extracted cruxes. A failure cannot be traced to crux extraction or to labelling. The "half or more" rule is a coarse match to a continuous score.
13. **Weak controls.** Flesch Reading Ease measures word and sentence length, not clarity of argument. The primary model leaves out similarity to the rater's own opinion, because the brief fixes the controls, so beta_E is exposed to a self-interest confound. Only A2b and its wording rule guard against it.
14. **Uncarried uncertainty.** Each unique gate item has one labeler, and half of those are the author who knows the hypothesis. Scorer error is not propagated into the A2 interval, which biases beta_E toward 0. A linear model treats rank gaps as equal. The bot filter removes more than half of the rounds, so results describe the all-human, four-candidate subset only.

## Dual-use
- **Benefit.** Auditing whether approval-trained mediators hide disagreement.
- **Misuse paths.** [A scorer or fine-tuning recipe could be used to optimise statements for approval by hiding disagreement; prompt-injection findings (N6) could be used against mediation systems.] [Ethics reviewer to complete.]
- **Mitigations.** No fine-tuned weights released; injection tests use synthetic opinions only; data are CC-BY 4.0 public and unchanged; no human subjects added [confirm].
- **Data and privacy.** Opinions are participants' free text from a public release; [reviewer to assess re-identification risk and quoting policy].
- **Release decision.** [Code/scorer release: pending human decision. Pipeline never publishes.]

---
CHANGES (round 1): replaced FROZEN placeholder with the FR §2 filter and counts; Tessler supplement stated as unopened and not cited; Tessler cited by bib key; A2b self-interest confound and the scorer-error-biases-toward-zero point to be added from FR 'Known weaknesses' [OPEN: add as limitations 10-11]; Wen et al. and Costello not cited; no other citations in this file.
CHANGES (round 2): added weaknesses 10-14 from FROZEN_RULES.md; pilot item replaced by [PILOT-DISCLOSURE] placeholder; gate-1 and A2 numbers remain slots.
CHANGES (round 3): [PILOT-DISCLOSURE] filled from decisions.md D33 and FROZEN_RULES.md section 2 (development set excluded from gate-1 sampling; A2 shown with and without it, rather than excluded from every confirmatory test, to match FROZEN_RULES).
