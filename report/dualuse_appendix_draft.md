<!-- MERGED 2026-11-16: X.2-X.4 of this file were merged into limitations_dualuse_draft.md (Appendix A), without the N6, F and B paragraphs. This file is NOT assembled by build.py. Its "blind human labels", "two gate-1 labelers" and "second scorer" text is stale (R4a, D48, D49). -->

<!-- DRAFT by the ethics and dual-use reviewer (analysis/ETHICS_REVIEW.md). The author merges this with
report/limitations_dualuse_draft.md. [SLOT] = fill from verified results only. [VERIFY] = a claim the
citation verifier must open a source for before it stays in. Remove a whole experiment's paragraph if it was not run. -->

# Appendix X: Limitations and Dual-Use / Ethical Considerations

## X.1 Limitations

1. **Associations, not preferences for erasure itself.** We test whether, within a round, participants rank candidate statements with higher crux erasure above statements with lower erasure. This is not evidence that people *want* disagreement hidden. Shorter, clearer or more agreeable statements may hide disagreement as a side effect. We control for length and clarity, but clarity may lie on the causal path, so we report estimates both with and without it [SLOT].
2. **The scorer.** Erasure is scored by an LLM judge. It was validated against blind human labels on a small sample (gate 1: [SLOT kappa, balanced accuracy with 95% CI, number of "unsure" items excluded]). One of the two labelers knew the hypothesis. A second scorer from a different family is reported in [SLOT].
3. **One dataset, one population, older mediators.** All ranking data come from the Habermas Machine release (Tessler et al., 2024), collected from UK participants [VERIFY: recruitment platform and dates from the paper]. The candidates were written by that study's fine-tuned mediator. Statements from newer models (Experiment N2) were scored but never ranked by people.
4. **A different construct from the original study.** Tessler et al. found that revised statements incorporated minority critiques. Our crux-erasure measure is defined from the opinions in each round and is not their stance-axis measure. Our results neither confirm nor refute theirs.
5. **Exploratory analyses.** Experiments N2 and N5 [SLOT: others outside FROZEN_RULES.md] were not pre-registered and are labelled exploratory. A pilot began before the analysis rules were frozen; its results are reported as exploratory only.
6. **Flat and negative results are reported:** [SLOT].

## X.2 Data, licence and privacy

**Attribution.** We use the Habermas Machine dataset (Tessler, Bakker et al., 2024, *Science*; © 2024 DeepMind Technologies Limited), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The accompanying code is licensed under Apache 2.0.

**What we changed.** We did not modify any record. We analyse a filtered subset (filters in Appendix [SLOT]), add our own erasure scores, and quote short excerpts.

**Consent.** The data were collected by the original authors under their own procedures [VERIFY: cite their ethics statement; state nothing about consent or approval that is not in it].

**Personal data.** The release contains pseudonymous participant codes and no demographic fields. Its free-text opinions are political views. A pattern scan of all opinions and critiques found no names, contact details or postcodes. A small number of texts disclose an age, a town, a religion or an occupation. To limit re-identification:
- we never print participant codes;
- we quote only short excerpts from opinions that contain no such details, and prefer quoting AI-written statements;
- we report rankings only in aggregate.

**Third parties.** Opinion texts were processed only on locally run or self-hosted open-weight models [SLOT: confirm, or name any external API and its data-retention terms].

**Annotators.** The two gate-1 labelers annotated statements. They were not study participants, and no data about them were collected.

**No new data from people.** No new human-subject data were collected: no new participants, no new rankings.

## X.3 Dual-use considerations

**Approval-optimised mediators.** If participants' rankings reward statements that hide disagreement, then a developer optimising a mediator, polling summariser or "consensus" product for approval is rewarded for hiding dissent. An erasure scorer like ours could be used as a reward signal to make this happen faster, rather than to audit it. We judge the added risk to be small. Approval-trained systems already receive this signal implicitly, whereas auditors currently lack any measure of it. We document the scorer as an audit tool and recommend that deployers report erasure alongside approval. [Release of the scorer and prompts: decided by the authors, not part of this submission unless stated.]

**Prompt grid (N2).** We publish the system and user prompts that produced the most and least erasure, because reproducibility outweighs the small uplift. Similar prompt effects are already reported (Mahajan et al., 2026 [VERIFY]). We present the high-erasure configuration as a failure mode to test for, not a recommendation.

**Hidden-instruction injection (N6).** [Include only if run.]
- *Setup.* We tested whether an instruction hidden in one participant's opinion tilts the mediator's statement. Every opinion in these tests, both clean and injected, was synthetic. Nothing was written by a real participant, and no real deliberation platform, public demo or person was involved. All runs used self-hosted models offline.
- *What we report.* Payload categories and aggregate effects with confidence intervals, plus one simple defence [SLOT: delimiting / instruction-hierarchy result].
- *What we withhold.* We do not print the most effective verbatim payloads, because the targeted mediator code is public and installable.
- *Implication for operators.* Deliberation systems that put participant text into a model prompt should treat that text as untrusted input.

**Fine-tuning on honesty-benchmark-style items (F).** [Include only if run.]
- *Design.* We fine-tuned LoRA adapters on newly generated items written in the style of an honesty benchmark (MASK [VERIFY licence]). No benchmark test item was used in training, and generated items that overlapped the style benchmark or either held-out benchmark above fixed thresholds were removed [SLOT counts]. We then measured transfer to two held-out benchmarks (TruthfulQA MC; Anthropic sycophancy evaluations).
- *Main dual-use concern.* If in-style scores rise without held-out gains, the recipe shows how to raise a headline honesty number without improving honesty. We report that gap as a warning to evaluators: in-style benchmark gains do not certify honesty, so held-out batteries are needed.
- *What we withhold.* No fine-tuned weights or adapters were released, and none will be. The generated training items are not released [or: are released only with a canary string so they can be excluded from future training data; authors' decision].

**Temporal calibration (B / T1-1).** [Include only if run.] Showing that a stated date in the prompt shifts a model's confidence in current facts also shows that an attacker can use a false date to make a model doubt correct present facts. Deployers should supply the current date from a trusted system source, not from user text. Tenure facts come from Wikidata [VERIFY licence, CC0], retrieved 2026-11-15. Named examples were checked against primary sources and are reported only for public office-holders.

## X.4 What we did not do

- We did not release fine-tuned weights or adapters.
- We did not run injection tests on real participants' text or on any live system.
- We did not collect new human rankings.
- We did not publish participant identifiers.
- We did not use mirrors or re-uploads of gated models.
