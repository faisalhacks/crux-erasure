# Experiment council: scorer skew / A2 full scoring. METHODOLOGIST vote

Written blind to other members' votes. Read: BRIEF.md (§3, §4, §5 A2, §8, §9), FROZEN_RULES.md (DRAFT),
scorer_manifest.json, scorer.py, prompts/, scores/gate1_scores.jsonl, scorer_runs/probe/{scores,extractions}.jsonl,
gate1/sample.json, A2_SCORING_COUNCIL_PACKET.md. No ranking, rating or label file was opened
(`labels/` and `gate1/packets/` do not exist, so FROZEN_RULES is still a draft).
Raters were never read: pilot_groups.jsonl was read only for `question` and `candidates`.

Checks I ran (scratch scripts, read-only, no network, no Modal, $0):
- `within.py`: within-round variation of E and E_pos in the probe and gate scores.
- `lex.py`, `cr.py`: explicit disagreement wording in the probe statements vs. scorer labels; read 4 crux/statement pairs.
- `ba_sim.py`: HYPOTHETICAL confusion tables run through the FR §6.4 bootstrap (seed 20261116). This is a design
  calculation, not data.
Paths: `C:\Users\intel\AppData\Local\Temp\claude\c5e7167f935dab11\923bfd22-ec75-469e-bd83-5aa51a370dcb\scratchpad\{within,lex,cr,ba_sim}.py`.

## Measured facts (what the critique rests on)

| Fact | Value | Source |
|---|---|---|
| Probe (dev, 40 rounds x 4) label counts | SIDED 186, OMITTED 17, BLENDED 10, VISIBLE 3 (of 216) | probe/scores.jsonl via within.py |
| Probe E values | 1.0: 133, 0.5: 2, 0.0: 1; 20 zero-crux statements (5 rounds); 4 missing E | same |
| **Probe rounds with within-round variation in E** | **3 of 34** evaluable rounds (8.8%; Wilson 95% about 3% to 23%) | same |
| Probe rounds with within-round variation in E_pos (A2e, SIDED = shown) | 13 of 34 | same |
| Gate (60, one statement per round) E values | 1.0: 47, 0.5: 2, 0.0: 1; zero cruxes: 10 | gate1_scores.jsonl |
| Gate AI binary | 49 positive, 11 negative; **10 of the 11 negatives are zero-crux rounds** | same, `ai_binary()` scorer.py:210 |
| Gate order check | 0 flips of 50 | same |
| Gate rounds that can show within-round variation | 0 (one statement per round by design, FR §6.1) | sample.json |
| Probe statements with explicit disagreement wording | 8 of 136 labelled; 1 of those has a VISIBLE label | lex.py |
| Probe missing E | 4 statements, 3 in one round (c884bf60) | scores.jsonl |

Reading of the spot check (4 pairs, cr.py): the scorer's SIDED calls looked defensible. Example: round 6a583a11 cand 3 says
"the citizen's jury is split on the idea of Churchill as a hero", but that split is not one of the two extracted cruxes,
so SIDED on those cruxes is a correct reading of the rule. This is 4 items, not a validation. It suggests that the skew is mostly the
population (consensus statements that take one side), plus a construct choice (SIDED = hidden). It does not look like a parsing or prompt bug.

## Critique (flaw, evidence, severity, cheapest fix)

**F1. The gate validates a different discrimination from the one A2 uses.** Severity: HIGH (validity of the confirmatory claim).
- Evidence: 10 of the 11 AI negatives in the gate are zero-crux rounds. A2 drops zero-crux rounds (FR §3 "Zero cruxes").
  A2's beta_E is identified only by rounds where one statement receives a VISIBLE label (3 of 34 probe rounds). The gate
  SRS contains 3 statements with E < 1 in rounds that have cruxes. Sensitivity will be near 1 because the AI says "hides" for almost everything.
  So the gate's balanced accuracy is about (1 + specificity) / 2. Specificity comes almost entirely from humans' `NO_DISAGREEMENT` agreeing with
  AI zero-crux calls. In ba_sim.py, a hypothetical table with 10 human negatives, 7 caught, gives BA 0.83 and LB 0.66: a PASS.
  The scorer could earn that pass without having shown any ability to tell SHOWS from HIDES inside a disagreement round.
- Cheapest fix (pre-freeze, no rerun): keep the §6.4 pass rule as the brief wrote it. Add to §6.4 "also reported" a **disagreement-subset BA**:
  items with AI n_cruxes > 0 and adjudicated label in {HIDES, SHOWS}. Report how many gate negatives are zero-crux agreements.
  Add a **binding wording rule**: if the subset has fewer than 5 human SHOWS, or its bootstrap LB is ≤ 0.5, then the abstract and discussion
  must say: "the scorer is validated for detecting whether disagreement is present, not for detecting whether a statement hides it".
  beta_E is then reported with that caveat.

**F2. The rare AI "shows" calls that identify A2 receive no human validation.** Severity: HIGH.
- Evidence: there are 3 VISIBLE labels of 216 in the probe and 4 of 81 in the gate. beta_E is a contrast between those statements and their round-mates.
  An SRS of 60 can contain only about 3 such items.
- Cheapest fix (option c, done as a supplement rather than a replacement): keep the 60-item SRS gate unchanged, because it is unbiased for sensitivity and specificity.
  Add a separate **S-stratum** that is outside the gate and never enters kappa or the gate BA. Each labeler gets 8 statements with at least one VISIBLE label, plus
  8 matched round-mates with E = 1 from the same rounds. Draw them from non-dev, non-gate launches with a fixed seed (`random.Random(20261127)`), after the full scoring run.
  Interleave them blind in the packets with fresh opaque item_ids; `item_key.csv` records role = `supplement`. Report:
  (i) the human HIDES rate on AI-VISIBLE statements vs. their E = 1 round-mates, which is a direct check of the within-round contrast;
  (ii) the agreement count with a Wilson interval. Never reweight these items into the gate.
  Needs: a FROZEN_RULES §6.1/§5 edit before freeze (44 → 60 rows per packet), the human's consent to the extra labelling time, and the full scoring run (Q2).
  If the human declines the extra rows, log F2 as a limitation instead.

**F3. Changing the threshold or binarization is not justified and would not change anything.** Severity: LOW (as a proposed fix).
- Evidence: E effectively takes 3 values here {0, 0.5, 1}. Moving to `E > 0.5` flips the 2 gate items at 0.5 and nothing else. The ≥ 0.5 rule mirrors
  the human "half or more not shown" rule (FR §5 step 4). Changing it would break the shared threshold, and choosing it from the AI distribution buys no construct validity.
- Fix: none. Keep `HIDE_THRESHOLD = 0.5` (scorer.py:71). Per-crux labels are stored, so any later binarization is recomputed without a rerun.

**F4. Counting SIDED as hidden makes E nearly constant. This is a construct choice and should not be patched in the prompt.** Severity: MEDIUM.
- Evidence: SIDED is 86% of probe labels. E_pos varies within 13 of 34 rounds, against 3 of 34 for E. The FR "Known weaknesses #1" predicted this.
- Risk: a forking path. If A2 is flat and A2e is not, A2e will be reported as "the finding".
- Cheapest fix (pre-freeze text only): add to A2e: "A2e measures topic omission or blurring, not hiding. It is never described as crux erasure.
  If A2 is unmeasurable or null and A2e is not, A2e appears only as a secondary result, with that wording." Do not swap the primary.
  The swap would be outcome-blind, but it would change the construct the brief names.

**F5. The interpretability floor may fire, and its margin is unknown.** Severity: MEDIUM.
- Evidence: the probe shows 3 of 34 rounds varying (95% CI about 3% to 23%). Rough projection over 871 launches, about 2.25 eligible rounds per launch
  under an independence assumption: about 57 to 390 launches with variation, point estimate about 160. The lower end is at the floor of 50.
- Fix: the full scoring run measures this exactly and is outcome-blind. Record the count in decisions.md **before freeze**. Do not move the floor after seeing it.

**F6. Parse failures are clustered and drop whole rounds.** Severity: LOW to MEDIUM.
- Evidence: 4 missing E in the probe, 3 of them in round c884bf60. FR §4 drops a round in A2 if any E is missing.
- Fix: report dropped rounds and their mean length, together with the row counts in the A2 output. The FR allows one pre-freeze format fix. Use it only if the full run's
  label parse-fail rate is above 5%, and only for output format.

**F7. The order check cannot fail.** Severity: LOW.
- Evidence: 0 flips of 50. Most items have 1 or 2 cruxes, all SIDED, so reversing the crux order cannot change a saturated E. Label-option order (VISIBLE listed first) is never permuted.
- Fix: report it as uninformative at ceiling. Optional exploratory step: permute the label-menu order on the 60 gate items (60 calls, about $0.1).

## Confounds in A2 given this distribution
- Statements that show a crux (VISIBLE) are probably longer and more hedged. Length is controlled, but A2f vagueness and A2h (no clarity) matter more than usual,
  because the identifying contrast is almost binary.
- Self-interest (A2b): a statement that names both sides is closer to more raters' own opinions. The A2b wording rule is the guard; keep it.
- The development launches supply the probe estimate of variation. Non-dev launches may differ. A2d covers this.

## Missing ablations or reports
1. Disagreement-subset BA (F1).
2. Human rate on AI-VISIBLE vs. round-mates (F2).
3. Per-crux label distribution and within-round-variation counts for E and E_pos, from the full run, written to decisions.md before freeze.
4. Determinism check: the full run re-scores the 60 gate statements, because their launches are in ALL_GROUPS. Count mismatches against `gate1_scores.jsonl`.
   The gate score of record stays gate1_scores.jsonl. A mismatch rate above 0 is reported as vLLM batch nondeterminism.

## Reproducibility checklist
- [ ] Prompt hashes in scorer_manifest.json match the prompts/ files and FR Appendix A at run time (`verify_prompts()`).
- [ ] Data SHA-256 7cf8d5ce… re-checked. The all_groups/pilot_groups hashes match the manifest.
- [ ] Launch order is `random.Random(20261125)`. A stop leaves a random prefix, and the count is logged.
- [ ] Thinking off and response_format recorded as actually used (the manifest still says UNVERIFIED in `decoding`, but the probe summary says "off").
      Reconcile this in the manifest before freeze.
- [ ] Gate re-score mismatch count (ablation 4).
- [ ] Parse-fail counts per step, and dropped-round count with ids.
- [ ] Ledger estimate and timeout row before launch, ACTUAL after; `modal container list` empty.

## Falsifier
The worry "the scorer is valid but A2 cannot test the question" is **refuted** if **both** of these hold:
(a) the full run shows ≥ 50 launches with within-round variation in E;
(b) in the S-stratum, humans label AI-VISIBLE statements HIDES less often than their E = 1 round-mates, and the Wilson intervals do not overlap.
It is **confirmed** if (a) fails, or if in (b) humans call AI-VISIBLE statements HIDES at the same rate as their round-mates.
In that case A2 is reported as not measurable at this instrument (FR §12), whatever gate 1 says.

## Brief (schema per ORCHESTRATOR §8.4 as far as given in this task)
```json
{"role": "methodologist", "item": "t3_1 scorer skew + A2 full scoring",
 "verdict": "Keep the instrument; add the disagreement-subset report, a supplementary stratum and wording rules; approve scoring now",
 "score": "UNKNOWN (the §8.5 rubric bands were not supplied in this task, so no anchored score is given)",
 "evidence": ["probe/scores.jsonl: 3/34 rounds vary in E, 13/34 in E_pos", "gate1_scores.jsonl: 10/11 AI negatives are zero-crux",
              "scorer.py:71 HIDE_THRESHOLD, :203 erasure, :210 ai_binary", "FROZEN_RULES §6.4, §7 floor, Known weaknesses #1"],
 "falsifier": "see Falsifier section"}
```

Q1: (d) combination, as follows.
Keep the scorer, the prompts, the E definition and the ≥ 0.5 threshold. Do not apply option (b).
Keep the 60-item SRS gate and its pass rule unchanged. Zero-crux rounds stay AI negatives in the gate (FR §6.4) and stay excluded from A2/N1 (FR §3).
Pre-freeze edits to FROZEN_RULES:
(1) §6.4: add the disagreement-subset BA, the zero-crux share of correct negatives, and the binding wording rule (F1);
(2) §6.1/§5: add the blind, non-gating S-stratum of 8 AI-VISIBLE statements plus 8 round-mates per labeler (F2). This needs the human's consent; if refused, log it as a limitation;
(3) §7 A2e: the wording rule (F4);
(4) record the within-round-variation launch count from the full run before freeze, with the floor unchanged (F5).
Re-run: nothing that has already run. The S-stratum draw and the packet build (`g1_packets.py`) run after the full scoring run. The gate scores stand.
Q2: APPROVE. Approval is conditional on Q1 leaving E1/L1 and the E definition unchanged. If the council instead adopts a prompt change, the vote becomes APPROVE-AFTER-Q1.
The run is outcome-blind, and Q1(d) depends on its output.
