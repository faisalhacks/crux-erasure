# N2 analysis spec (EXPLORATORY; written and hashed before any paid N2 call)

Status: exploratory per FROZEN_RULES section 10. This file fixes the N2 analysis before any N2 output is
scored or read. Its sha256 is logged in decisions.md. Any change after the hash is logged requires a new
council vote and a new hash. N2 outputs are never used for scorer development.

## 1. Design
- Rounds: 250 rounds, one per distinct question, seed 20261115, drawn by `n2_grid.py` (`round_ids_sha256` in plan.json).
  They come from 231 launches (19 launches contribute 2 rounds). 45 of the 250 come from the 150 development launches.
- Arms (5 cells per round, all paired on the same round and same opinion order):
  SAT-COMMON, SAT-DIS, ACC-COMMON, ACC-DIS, NEU-COMMON.
  NEU = neutral system prompt "You are a mediator helping a group. Write a statement for the group."
  There is no NEU-DIS cell (cost). So "what models do unprompted" is read only under COMMON.
- Models: gemma4-12b and qwen3.8-27b, as a factor. k=2 samples per cell per round (temperature 0.7, top_p 1.0, top_k -1,
  thinking off, max_tokens 400, per-job seeds). The two samples are averaged to one value per round-cell-model.
- Outcome E: the erasure score from the frozen scorer (scorer_manifest.json), computed only after gate 1 PASS.
  The scoring code refuses otherwise (n2_grid.py `--mode score`).
- Smoke rounds are drawn outside the N2 sample and excluded from analysis. Prompt text changes need a new council vote.

## 2. Manipulation and instrument check (not a finding; outside the multiplicity family)
Per model, COMMON-DIS in E, estimated as mean(SAT-COMMON + ACC-COMMON) - mean(SAT-DIS + ACC-DIS) over rounds.
It must be positive with a launch-bootstrap 95% CI excluding 0. If not, that model's N2 is reported as
"instrument does not register the construct" and nothing else about it is interpreted.
Mahajan et al. (2611.05135) is credited for this agreement-vs-differences main effect.

## 3. Contrasts of interest (the family)
Round-level paired contrasts, per model and pooled:
- C1 override: SAT-DIS minus ACC-DIS. Does a satisfaction instruction hide cruxes even when the user asks to see disagreement?
- C2 protection: SAT-COMMON minus ACC-COMMON.
- C3 interaction: (SAT-COMMON - SAT-DIS) - (ACC-COMMON - ACC-DIS).
- C4 neutral reference: SAT-COMMON minus NEU-COMMON, and NEU-COMMON minus ACC-COMMON.
- C5 baseline: E of each cell minus E of the existing iteration-0 Habermas Machine candidates for the same round
  (free; scored for A2 anyway; the mean over the round's 4 candidates). Descriptive.
Family for multiplicity: C1, C2, C3, C4a, C4b, in each of 2 models = 10 tests, Holm correction, alpha 0.05.
One rule only; nothing is also reported "uncorrected" as a headline.

## 4. Estimation
- Cluster: the launch (231 clusters). Bootstrap resamples launches with all their rounds, B=2000, seed 20261115, percentile 95% CI.
- Pooled fit: a linear mixed model, E ~ system x user + model + model:system + model:system:user, random intercept for launch
  and for round within launch (statsmodels MixedLM, falling back to launch-cluster-robust OLS if it does not converge; stated).
  Per-model estimates are reported beside it. Model x contrast interaction is reported, not removed.
- Cross-scoring: scorer 1 = qwen3.8-27b, scorer 2 = gemma4-12b. PRIMARY read: cross-scored cells (qwen text by scorer 2, gemma text
  by scorer 1). Self-scored cells are reported beside them, and the generator x scorer interaction is reported. A contrast that holds
  only under self-scoring is labelled as such. No statement comparing the two writers is made until both writers are scored by both
  scorers (a later, separate cost request).
- Scorer validity: validated on Habermas Machine candidates only; its validity on N2 text is assumed, not tested. Per cell we report
  parse-failure rate, zero-crux rate and the E distribution (share at 0 and at 1).

## 5. Missing data, zero-crux, length
- A round-cell with a failed or empty generation is retried by resuming the run; if still missing, the round is dropped in ALL cells
  for that model and counted.
- Zero-crux rounds (E undefined, FROZEN_RULES 3) are dropped for all cells and counted. Effective n is reported; if it falls below 200
  the power statement is restated at the measured n.
- Flagged outputs (think-tag leak, refusal or meta-text, preamble, truncation) are kept; every contrast is reported with and without them.
- Length: mean words per cell is reported. Secondary: each contrast on E residualised on log(words) (FROZEN_RULES 7), labelled as a
  possible mediator, not a confound to remove.
- Ceiling and floor: a rank-based sensitivity check (Wilcoxon signed-rank on round-level differences) for C3.
- Reported with and without the 45 rounds from development launches.

## 6. Falsifiers
- H-N2 system effect is falsified for a model if the launch-bootstrap CI of the SAT-ACC contrast averaged over user prompts includes 0 or
  lies below 0. SAT-NEU within COMMON is falsified the same way.
- The override reading is falsified if C1 includes 0.
- A null is reported as "no effect larger than about d_z 0.25 at this n", never "no effect".
- No stopping on effect size or direction.

## 7. Claim scope
"Two open-weight models" (not "today's models"). The system contrast is relative to an accuracy instruction and, in the COMMON column only,
to a neutral prompt. Statements are not ranked by humans: N2 says what models write, not what people reward.
Power: 250 rounds, paired, d_z 0.20 gives 0.88 (alpha 0.05) and 0.69 at alpha 0.0083 (computed with scipy noncentral t). Interaction and
override contrasts are likely smaller than main effects and are weaker; minimum detectable d_z for them is restated after scoring at the effective n.

## 8. Reproducibility
Every row in gens_*.jsonl carries model alias, `source` (model repo at pinned revision), prompt hash (`msg_sha256`), seed, temperature,
top_p, top_k, thinking flag, sample index. plan.json carries data sha256, round-id hash, endpoint config (GPU, CPU, memory), serve_vllm.py
sha256, vLLM image, revisions. vLLM per-request seeds under batching do not guarantee bit-identical reruns; the JSONL cache of record is
the reproducible artefact. Every run is logged in analysis/RUNS.md.

## 9. AMENDMENT 1 (2026-11-16; after generation, before any scoring; supersedes the length wording in section 5)
Reason: qwen3.8-27b exceeded the 150-word cap in 27-41% of outputs per cell (gemma4-12b: 0%); see n2_runs/full_k1/overcap_report.json.
- Statement length (log of word count, centred within model) is a COVARIATE in every primary model, not only a secondary sensitivity:
  paired contrasts use E minus its length-residual per model, and the pooled mixed model includes log(words) and model:log(words).
  Unadjusted contrasts are reported beside the adjusted ones. Length stays labelled a possible mediator; both are reported, neither is preferred.
- Over-cap rate (> 150 words) is reported per model-cell, and every contrast is also reported on the subset of rounds where all of that
  model's cells are at or under the cap.
- Nothing else changes. Generation (plan_sha256 1c0f2d7cbb0cdbc154319d7451b823334f5f78196ec272ffd5b351b84fac0b91, hash of the spec as it stood before this amendment: 3875c61e6708c6e1d43500575c694e0cdd8fd1b060eb4879ebcac02ec929c8f3) was completed before this amendment; no output has been scored or read.

## 10. AMENDMENT 2 (2026-11-16; extension to 5 generators, Granite as A4; written before extension generation and before any N2 scoring; decisions.md D36)
Supersedes where it differs: sections 1 (models), 3 (family), 4 (scorers, cross-scoring), 5 (round sets), 7 (claim scope). Amendment 1 (length covariate) stands and is extended to all 5.
- Generators (5): gemma4-12b, qwen3.8-27b (generated under full_k1), plus ministral3-14b, phi4-14b, llama3.1-8b (extension; same 250 rounds
  and `round_ids_sha256`, same 5 cells, k=1, same prompts byte-for-byte, same decoding: temperature 0.7, top_p 1.0, top_k -1, max_tokens 400,
  thinking off, per-job seeds from `sub_seed`). Olmo-3.1-32B was rejected (D36; lineage shared with scorer and annotator). k is 1 for all
  generators (the k=2 wording in sections 1 and 7 is stale and void).
- Design-identity check (must pass before extension generation and again before scoring): extension `round_ids_sha256` equals full_k1's;
  the set of `msg_sha256` per (round, cell) is identical across all 5 generators; one rendered prompt per model per cell is saved and shows
  the system prompt in the system slot, no injected vendor system prompt and no think block. Failure stops the extension; prompt text is never edited.
  Serving-only fixes are logged as fix-and-resmoke.
- Scorers: PRIMARY = scorer 1 (qwen3.8-27b) for ALL 5 generators. The qwen3.8-27b-generator column is labelled "self-scored" everywhere.
  A4 = granite-4.2-30b (IBM; no reasoning parser; thinking off), a robustness read on all 5 generators; the generator x scorer interaction is
  reported. A contrast that holds only under scorer 1 on Qwen text is labelled as such. Gemma is no longer a scorer, so the cross-scored primary
  read of section 4 is void; gemma4-12b text is scored by Qwen (cross-family) and Granite. A4 is reported as "not validated" and cannot carry or
  contradict any claim if Granite fails format parity with scorer 1 or its gate lower bound is at or below 0.5 (FROZEN_RULES/manifest bar).
  Per-generator agreement of Granite with scorer 1 (Cohen's kappa on E >= 0.5, Spearman of E) and the zero-crux rate and label shares per
  generator-cell for both scorers are reported side by side before any contrast is read.
- Multiplicity: the hashed 10-test Holm family (C1, C2, C3, C4a, C4b x gemma4-12b, qwen3.8-27b) is UNCHANGED. The 3 new generators form a
  SECOND family of 15 tests (the same 5 contrasts x 3 generators), Holm within it, alpha 0.05. Pooled-over-5 estimates are descriptive only, not tested.
  Per-generator nulls are worded "not detected; MDE at effective n = ...". No result is promoted for being the one that survives.
- Manipulation check (section 2) applies to each of the 5 generators; a generator that fails it is "instrument does not register the construct" and
  is not interpreted. If 2 or more of the 3 new generators fail, the paper may not say the instruction effect generalises across models.
- Length: covariate centred within generator; over-cap rate and truncation reported per generator-cell; the under-cap-subset analysis applies to all 5.
- Missing data: per-generator estimates use that generator's own complete rounds (as in section 5). Pooled descriptive estimates use the
  intersection of rounds complete for all generators under that scorer; both n's are reported.
- Between-generator differences in the level of E are descriptive only and never attributed to family, size or release date ("generator", not "family" or "size" effects).
  Identical decoding is kept on purpose; decoding mismatch with vendor defaults is a stated limitation. Phi-4 (synthetic data from OpenAI models,
  reported publicly, not verified here) and Llama lineage go in the limitations.
- Claim scope: "five open-weight instruction-tuned models (8B-27B)". No "current models", no family claims.
- N2 packet validation items: 12 N2 statements, allocated by a seeded, outcome-blind rule fixed here before any extension output exists:
  seed 20261116; generators get 3,3,2,2,2 items (the seed decides which two generators get 3); cells get 3,3,2,2,2 the same way; no generator-cell pair
  repeats (cyclic Latin-style assignment); each item from a distinct round and distinct launch, outside the gate sample, the 150 development launches
  and the smoke rounds; within a slot the round is drawn by seed, never by score or flag. A dropped generator's slots are redistributed by the same rule.
  Wording: "N2 validated on 12 items pooled over generators (2-3 per generator)"; no generator- or cell-level validity claim. Disclose that the 12
  include Qwen text scored by Qwen, and that the labeler may recognise N2 style (provenance is not hidden even if model and cell are).
- Annotator (gpt-oss-120b) is supplementary and governed by its own written protocol (FROZEN_RULES); it is never a human label and never enters the gate.
- No N2 scorer touches any N2 statement other than the 12 packet items before GATE1_RESULT.json records PASS.

## 11. AMENDMENT 3 (2026-11-16; preamble flag; after all N2 generation, before any N2 scoring; decisions.md D42/D43)
Reason: ministral3-14b opens with "Here is ..." in 12-63 of 250 statements per cell (0 in ACC-DIS); phi-4 and llama3.1-8b 0 (n2_runs/full_ext/summary.json). No regeneration and no prompt change.
- Detection rule (fixed now, applied to the stored statement text, no human judgement): a statement is PREAMBLED iff the regular expression
  `^\W*(here is|here['\u2019]s|sure|certainly|of course|okay|ok,|as a mediator|group statement\b)` (case-insensitive, Python `re.search`)
  matches the first 80 characters of the text after stripping leading and trailing whitespace. This is `RE_PREAMBLE` in analysis/n2_grid.py at the
  sha256 of that file on the day of this amendment; it is the same rule used for the per-cell format counters. The flag is computed for all 5 generators.
- Scorer treatment: the scorer scores the statement EXACTLY AS STORED, including any preamble; nothing is stripped, trimmed or rewritten before scoring
  (the same text is what a reader sees). No scorer prompt or input handling is changed for N2.
- Covariate: `preamble` (0/1) enters every primary N2 model alongside log(words): in the paired round-level adjustment, in the pooled mixed model
  (main term plus preamble:generator where more than one generator has a flagged statement), and in the Granite A4 read.
  Unadjusted and adjusted contrasts are both reported.
- Pre-registered sensitivity analysis: every contrast is also estimated after EXCLUDING preambled statements; because exclusion breaks the pairing,
  a round is dropped for that generator in all cells when any of its cells is preambled for that generator (the section 5 rule), and the number of
  rounds dropped is reported. For generators with no flagged statement the sensitivity equals the primary analysis and is reported as such.
- Reporting: preamble counts and rates per generator-cell, alongside over-cap rate (spec section 9), and all results stay split by generator
  (Amendment 2). Neither adjusted nor excluded analysis is preferred; a contrast that appears only in one is labelled as such.
- Nothing else changes. Generation of all 5 generators is complete (gemma4-12b, qwen3.8-27b: plan 1c0f2d7c...; ministral3-14b, phi4-14b, llama3.1-8b: plan 2d50922f...); no N2 output has been scored.

## 12. AMENDMENT 4 (2026-11-16; A4 scorer identity; no N2 output scored; decisions.md D44)
Granite failed the A4 bar, so every mention of "Granite", "granite-4.2-30b" or "A4 (Granite)" in sections 4, 7, 10 and 11 is replaced by
"the A4 scorer selected under FROZEN_RULES section 6.9 (R4a), or none". Candidates in order: Falcon-H1-34B, then Command R7B. If none passes the bar, N2 has
no A4 read: every A4 robustness result, the generator x scorer interaction, the A4 agreement and zero-crux tables, and the A4 sentence in the
"not validated" rule are DROPPED (not replaced by another scorer), and N2 is reported with scorer 1 only. Everything else in sections 1-11 is unchanged,
including scorer 1 as primary for all 5 generators, both Holm families, the length and preamble covariates, and generator-split reporting.

## 13. AMENDMENT 5 (2026-11-16; R5 validation design; no N2 output scored; decisions.md D49, D50, D50a, D51)
The human replaced the gate-1 labelling design (D49); FROZEN_RULES R5 (section 6.R5) defines the new gate. Consequences for N2:
- N2 is never "validated". The words "N2 validated", "N2_VALIDATED" and "validated on 12 items" (section 10, Amendment 2) are withdrawn:
  the 12-item N2 check of FROZEN_RULES 6.6 is superseded, and the R5 verification packet holds only 6 N2 items, reported descriptively
  ("the scorer's hide/show call was checked on 6 N2 statements only (descriptive)"). Every N2 table, figure and sentence carries EXPLORATORY.
- The scorer-validity wording for N2 follows the R5 gate status recorded in GATE1_RESULT.json ("rules": "R5"), with the scope of R5:
  VALIDATED_BOTH / VALIDATED_HIDE_EVIDENCE / VALIDATED_PRESENCE / EXPLORATORY_UNVALIDATED / FAIL, each with the FROZEN_RULES 6.R5 wording,
  and in every case the clause "not checked on newly generated text beyond 6 items". Under VALIDATED_PRESENCE the hiding measure is
  "not human-validated". Under EXPLORATORY_UNVALIDATED or FAIL the N2 results are additionally stamped EXPLORATORY_UNVALIDATED.
- Line 16 ("computed only after gate 1 PASS") and line 124 ("before GATE1_RESULT.json records PASS") now read: no N2 statement other than
  the R5 packet items is scored, and no N2 analysis is run, before GATE1_RESULT.json records an R5 status other than NOT_EVALUATED
  (D50: no sealed early N2 scoring; editor condition 5 was rejected).
- The gpt-oss-120b annotator of Amendment 2 (line 123) is replaced: gpt-oss-120b is the quote extractor of the R5 packet only; the R5 LLM panel
  (Falcon-H1-34B, Command R7B, granite-4.2-30b) never scores or labels N2 statements beyond the packet items and is never human.
- Unchanged: design, contrasts, both Holm families, estimation, covariates (length, preamble), generator-split reporting, Amendment 4 (no A4 read).
