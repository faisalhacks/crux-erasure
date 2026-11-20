# Hostile workshop review: "Do Participants Reward Hidden Disagreement?"

Reviewed: `report/build/out/DRAFT_combined.md` (mtime 2026-11-16T02:45:50Z) and page images `report/build/out/pg-01..07.png`.
Rules checked: `FROZEN_RULES.md` §6.R5.5-6.R5.7 (status of record VALIDATED_PRESENCE, `gate1/GATE1_RESULT.json`), `decisions.md` D58 and D59.
Reviewer wrote blind to other reviews. The paper was not edited.

---

## (A) Numbers that do not match their source (ranked)

**A1. Table 1 and the step-2 specificity sentence misstate what the scorer did (the clearest numeric error).**
- Paper, `DRAFT_combined.md:95`: "in 317 of the 614 rounds whose members did not split on the question, the scorer still found a crux". The Table 1 row labels at `:99-100` read "Scorer finds ≥ 1 crux | 907 | 317" and "Scorer finds no crux | 101 | 297". The same claim is repeated in Appendix A item 4 (`:204`).
- Source: `gate1/STEP2_computed__20261116T015355Z.json` counts the 3 failed extractions as wrong calls (`n_extraction_missing_counted_wrong: 3`). The per-round file `gate1/step2_private/rounds__20261116T015355Z.csv`, cross-tabbed by me with pandas (ext_ok × n_cruxes>0 × hsplit), gives:
  - Hsplit = 0: 315 rounds with a crux found, 297 with none, **2 failed extractions**.
  - Hsplit = 1: 907 with a crux, 100 with none, **1 failed extraction**.
- So the scorer found a crux in **315** of the 614 non-split rounds, not 317. "Scorer finds no crux" in split groups is **100**, not 101. The cell values are the confusion-matrix entries (FP, FN), and the row labels describe something else. The same check gives TP+FP = 1,224 against "Rounds with ≥ 1 crux: 1222" in `analysis/results/RESULTS_MAIN.md`.
- B.2's "prevalence ... of a scorer crux 0.755" (`:244`) also includes the 2 failures: 1,222/1,622 = 0.753.
- BA2, sensitivity and specificity are correct as the pre-registered statistic. The error is in the row labels and in the prose.
- Fix: relabel the rows "called crux (failed extraction counted wrong)" or split out the failures, and write "315 (+2 failed extractions)".

**A2. "four candidates from four families" is false** (Appendix A item 6, `:206`). The four candidates are granite-4.2-30b, granite-4.2-8b, Falcon-H1-34B-Instruct and Command R7B. Two are IBM Granite, so there are three families. Methods (`:54`) correctly says only "none of four candidates".

**A3. No other mismatch was found in the 40+ numbers spot-checked** (table below). Two rounding cases were checked against the raw JSON and are correct: β_C upper bound −0.01746 prints as −0.017, and the BLENDED share 0.04949 prints as 4.9%.

| Paper number (location) | Source | Value in source | Match |
|---|---|---|---|
| 721 launches / 1,622 rounds (abstract, `:95`) | STEP2_computed json `n_usable_launches/rounds` | 721 / 1622 | yes |
| BA2 0.692 [0.669, 0.714]; question [0.670, 0.713] | STEP2 json | 0.69176 [0.66895, 0.71401]; [0.66991, 0.71338] | yes |
| sens 0.900 / spec 0.484 | STEP2 json | 0.8998 / 0.4837 | yes |
| class counts 1,008/605 and 614/437 | STEP2 json `hsplit_class_counts` | same | yes |
| B.2: 0.621, 0.681 (1,422), 0.693, 0.627, 0.403 | STEP2 json `reported_no_rule` | 0.6215, 0.6811 (1422), 0.6929, 0.6265, 0.4031 | yes |
| B.2: 0.755 | STEP2 json `prevalence_sdis` | 0.7546 | matches the file, but see A1 |
| 397 + 3 + 11 + 45 = 456; 1,166 / 642 / 22,536 | RESULTS_MAIN A2 note; REDTEAM (2) | 456; 22536 rows | yes |
| R_inf 150 / K_inf 142; 152/144 defect | RESULTS_MAIN Tier | same | yes |
| MDE 0.056; 2.80 × SE = 0.061 | RESULTS_MAIN Tier | 0.0563; 0.0610 | yes |
| β_E +0.051 [+0.008, +0.095], p 0.024 | RESULTS_MAIN A2 row | +0.0511 [+0.0076, +0.0952], 0.0240 | yes |
| β_L +0.167 [+0.158, +0.176]; β_C −0.026 [−0.035, −0.017] | RESULTS_MAIN; A2_primary json | +0.1669 [+0.1579, +0.1760]; −0.0260 [−0.03456, −0.01746] | yes |
| Table B1, all 9 rows | RESULTS_MAIN rows A2-A2i, uncontrolled | identical to 4 dp | yes |
| Fig. 1 labels (pg-06) | same | rounded consistently | yes |
| \|t\| 2.34, cubic 1.82, deciles 1.72, rank 1.35, raw 1.98 | RESULTS_MAIN length table | same | yes |
| SIDED +0.053 (0.022), BLENDED/OMITTED +0.028 (0.026) | RESULTS_MAIN red-team block | +0.0531 (0.0218), +0.0284 (0.0257) | yes |
| majority +0.100 [+0.037, +0.163]; minority −0.047 [−0.131, +0.039] | RESULTS_MAIN | +0.0996 [+0.0369, +0.1628]; −0.0470 [−0.1308, +0.0386] | yes |
| A2b LB ≤ 0 in 7 of 40 seeds | RESULTS_MAIN; REDTEAM:76 | 7 of 40 | yes |
| leave-3-out +0.037 (SE 0.021) | REDTEAM:177 | +0.0371 (0.0207) | yes |
| null coverage 191/200 | REDTEAM:161 | 191/200 | yes |
| 289/1,166; 39/150; split +0.015 / +0.066 | RESULTS_MAIN; REDTEAM:90-92 | same | yes |
| prevalence 96.1 [95.5, 96.7]; 3.9 [3.3, 4.5]; labels 82.8/9.0/4.9/3.2; 4,780; 6,628 | prevalence json; RESULTS_MAIN | 0.96130 [0.95511, 0.96739] etc. | yes |
| N1 +0.008 [−0.002, +0.019] p 0.115; N1u; N1h; 1,042/612/132; 124 tied | RESULTS_MAIN | same | yes |
| N4 −0.147 [−0.252, −0.041] p 0.008, 592; 114/106/151; 1,142/2,832/1,666 | RESULTS_MAIN | same | yes |
| Holm 0.231 / 0.023; 0.115 / 0.016 | RESULTS_MAIN | 0.2308 / 0.0234; 0.1154 / 0.0156 | yes |
| N3 713 launches / 1,607 rounds; A3 0 | RESULTS_MAIN | same | yes |
| N2 MC, all 5 generators with CIs | N2_RESULTS.md §5 | e.g. Llama 0.537 [0.485, 0.586] | yes |
| N2 SYS 0.28-0.37 | N2_RESULTS §6 | 0.278-0.366 | yes |
| C1 Qwen 0.03 [0.01, 0.05]; Llama 0.43 [0.36, 0.51]; C3 Llama −0.13 [−0.23, −0.03] | N2_RESULTS §6 | 0.028 [0.006, 0.053]; 0.431 [0.356, 0.509]; −0.129 [−0.226, −0.032] | yes |
| 168-177 rounds; 69 zero-crux; parse fail 0.4-2.4% | N2_RESULTS §3-4 | same | yes |
| Table B2, all 25 cell means | N2_RESULTS §3 | same to 3 dp | yes |
| Holm ≤ 0.02; under-cap 6 Ministral / 26 Qwen | N2_RESULTS §6, §8 | max 0.0200; 6 and 26 | yes |
| panel 21 / 12; κ 0.649 [0.143, 0.921], AC1 0.847; 0.570 [0.297, 0.787], AC1 0.577 | analysis/panel/panel_p1_summary.json | same | yes |
| A4 211/280, 161/280, 15/280, 78/280 | DRAFT_STATUS → D41-D48 | arithmetic correct | yes (families: see A2) |
| coverage 96.5% | FR:595 | 386/400 | yes |
| spend $15.28 | ledger.csv last ACTUAL cumulative | 15.2787 | yes |
| Tessler 0.36 vs 0.29 | references_verified.md:88 | same | yes |

---

## (B) Overclaims and wording-rule violations (ranked)

**B1. The abstract does not carry the D59 orchestrator ruling** (`decisions.md:518`). D59 requires two things the abstract (`:16`) lacks:
- "96%" must say that most hiding is SIDED (82.8% of crux labels).
- The abstract must include one exploratory N2 sentence.

Currently "By the scorer's reading, 96% of candidates hid every point of disagreement" stands alone. A reader takes it as "statements omit disagreement", when 82.8% of the labels mean "took one side". This is the most quotable number in the paper, and it is the one most likely to be misread.

The draft is timestamped 02:45Z and D59 is ~02:50Z, so this is outstanding work rather than defiance, but it is binding. The abstract is at 235 of 250 words, so something has to be cut to fit the two additions.

**B2. E-based rates are reported without the binding stamp** (FR §6.R5.6, VALIDATED_PRESENCE row). The rule: "`beta_E`, N1 and every `E`-based rate are reported as 'pre-registered test; the predictor's hide/show contrast is not human-validated'".
- The 96% prevalence appears in the abstract (`:16`) and the Discussion (`:135`) with only "by the scorer's reading".
- The Results heading (`:108`) uses a self-invented "pre-specified descriptive; not human-validated".
- Either use the binding string or document why a descriptive share is exempt. FR does not exempt it.

**B3. Methods understates who was exposed in the pre-freeze pilot.**
- `:52` says the pilot "had stored real ranks beside crude erasure proxies for them", where "them" means the 150 development launches.
- Appendix A item 9 (`:209`) and `decisions.md` D33 (line 254) say the feature file covered **all 1,960 eligible rounds**, including the 721 "held-out" launches. That file was later read programmatically by the shuffled-test path (D58.6).
- `:50` "before any erasure score was joined to a ranking" is strictly true only if the "crude erasure proxies" are not erasure scores.
- The body text should match the appendix. Otherwise a referee reading only the body gets a false picture of the hold-out.

**B4. Two citations of Zhu et al. (2025) are overstated against the project's own verification file.**
- `:41` "report minority under-representation across 18 LLMs": `report/references_verified.md:62` says this "goes beyond the text" and prescribes "benchmarks 18 LLMs and reports minority under-representation".
- "LLM-judge correlations ... that 'never exceed 0.4'" drops the qualifier "off-the-shelf". The same paper's main text reports ρ = 0.60 and ~0.48 (`references_verified.md:61`).
- The quote is used to justify the participant-signal check, so the cherry-pick is load-bearing.

**B5. The validation is framed more broadly than the scope rule allows** (FR §6.R5.6: "The scope applies everywhere").
- `:56-58`, the heading "Validation (three pre-registered steps)" and the sentence "so the score is validated in parts", is a bare validation claim about the score with no scope phrase.
- It also counts step 4 (the LLM panel; "supplementary; never a gate input", §6.R5.4) as a validation step. Step 3 was never done, so only one of the three "validation steps" validated anything, and that step only validated the presence of disagreement.
- Suggested rewording: "Checks (three pre-registered steps); only step 2 is a validation, and only of disagreement presence."

**B6. A required, unfavourable comparison was not reported.**
- FR §6.R5.4 lists "panel-majority A vs scorer S" as reported. The paper says "no panel-versus-scorer table was produced" (`:106`; DRAFT_STATUS deviation 3), but the inputs exist.
- My exploratory cross-tab joins `analysis/panel/panel_p1_summary.json` majority answers to `analysis/scores/packet_v5_scores.jsonl` (script: scratchpad `xtab.py`). Of the 13 items where the scorer gives E = 1 (hides every crux) and the panel says the quotes disagree, the panel majority says the statement **acknowledges** the disagreement in 7 (5 of 11 originals, 2 of 2 N2).
- Caveats: n is tiny, it is LLM against LLM, and the panel judged a different quote pair from the scorer's cruxes.
- It is still the only second opinion on the hide/show call, and it points against the 96% headline. Leaving it out while printing panel κ is selective reporting. Report it as supplementary, with the caveats.

**B7. The pre-registration violation is disclosed only in the appendix.**
- FR §6.R5.7 "Draft frames ... nothing is reframed after the result" was broken: the text was written after results were known (Appendix A item 13, `:213`).
- Methods opens with "Every rule below was fixed in a pre-registration" (`:50`). One clause there ("the per-status frames required by the pre-registration were not written before the gate") would remove the impression that the framing was locked.

**B8. An unhedged prior-work claim.** `:23` "Prior work did not link what participants reward to disagreement-hiding content." D4 requires "to our knowledge" for novelty claims. Related Work (`:43`) concedes a keyword search and abstract-only reading of several works. Hedge it.

**B9. Minor wording issues.**
- "N4 survives Holm" (`:137`) is significance-adjacent phrasing for an E-based Tier-2 result. It is not banned verbatim, but it reads like a significance claim. Better: "Holm-adjusted p = 0.023 with N3 at p = 1".
- B.6 "No sensitivity set reversed the sign of any contrast" (`:273`) is true but implies robustness the data do not show. Ministral C1 in the under-cap set is 0.000 [0.000, 0.000] (n = 6), and phi-4 C3 in that set has an interval including 0 (N2_RESULTS §8).

**B10. The rendered PDF is not submittable.**
- Visible placeholders on p. 6: "[RESULT SLOT: robustness]" and "[RESULT SLOT: N3]".
- Further placeholders on p. 1 and in the appendices: "[HUMAN SLOT: ...]".
- Under D59, N3 must become "NOT RUN: scorer app did not start (infrastructure), not a data decision" if it is not scored by 06:00Z. `analysis/results/N3_STATUS.json` still cites a 06:30Z deadline (D57), so the two records disagree on the cut-off.

**Checked and compliant:**
- The title is a question with no "validated".
- No directional rank claim in the abstract.
- The step-2 binding sentence is used verbatim in the abstract, Contributions, Results and Conclusion.
- No bare "validated against participants' own responses".
- "confirm" appears only in the D49d.4 dev-launch phrase, and "detected" and "significant" are absent.
- N2 is always EXPLORATORY with the 6-statement clause, and Qwen is flagged as self-scored.
- The LLM-use statement has all the elements §6.R5.7 requires.
- No blind-labelling claim.
- The A2b rule is applied voluntarily, per D58.3.
- D58.1-58.6 content is present.
- The "first test" novelty sentence is hedged and backed by a logged search (D4/D5).

---

## (C) The three changes that would most improve the paper within the 8-page body

1. **Replace Figure 1 with a length-specification figure, and fill the robustness slot with it.**
   - The paper's real finding is "β_E exists only under one length model". Figure 1 spends a full figure on seven near-identical sensitivity models that all share the linear log-length control. It shows only the two extremes (linear, none), not the five flexible specifications that actually carry the argument (`RESULTS_MAIN.md` length table).
   - One forest plot of β_E ± CI across the eight length specifications would show the fragility directly. Move the current Fig. 1 content to Table B1, which already holds it.
   - This also removes "[RESULT SLOT: robustness]" at no page cost.
2. **Make the 96% / SIDED result and its weak instrument the headline, and cut A2 back to what it supports.**
   - The defensible contribution is descriptive: by one unvalidated scorer, 83% of crux labels are "presents one side as the group's view", and participants almost never saw a candidate that showed the disagreement. That leaves only 150 identifying rounds, so the rank test cannot answer the question. FR §7.3's LOW-POWER key message is essentially this, and the text arrives there in Discussion.
   - Lead the abstract and conclusion with it, add the SIDED clause and the N2 sentence (D59), and pay for them by cutting the Related Work sycophancy paragraph to two sentences.
   - Put the Table 1 correction (A1) and the panel-versus-scorer cross-tab (B6) next to the 96% figure. These let the reader see that the hide/show call has no supporting human signal and weak LLM support.
3. **State the instrument limits once, in Methods, as a short "what E is and is not" box, and delete the repetitions.**
   - The VALIDATED_PRESENCE caveat, the step-3-not-done sentence and the "cannot separate hides from my side" point each appear 3-5 times across the abstract, Contributions, Methods, Results, Discussion and Conclusion.
   - A single box, combined with the pilot-scope correction (B3) and the frames deviation (B7), would free roughly half a page. Use that space for the length figure and one paraphrased worked example of a SIDED versus a VISIBLE statement. Without an example, a referee cannot judge whether "SIDED" means what the paper says it means.

---

## (D) Score

**4 / 10 (weak reject at a workshop; borderline at an epistemics sprint venue).** The study is unusually honest and its numbers are almost all exact, but its central estimate disappears under reasonable length controls. Its hide/show instrument has no human validation, and the only other judge (the LLM panel) disagrees with it more than half the time on the shared items. That leaves a well-documented null-ish result framed as a test, plus a striking descriptive number that is not yet trustworthy.
