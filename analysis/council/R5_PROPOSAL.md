# R5 — PROPOSED amendment to FROZEN_RULES.md (for council vote; NOT applied)

Status: **PROPOSAL.** Written by the planning room (methodologist seat) on 2026-11-16 UTC. Nothing in
this file is in force until the orchestrator applies it to `FROZEN_RULES.md` after a council vote and
logs it in decisions.md (proposed entry D50). This file does not edit `FROZEN_RULES.md`.

**Pre-edit check (directory listing only).** 2026-11-16T00:57:33Z and again 2026-11-16T00:59:06Z,
immediately before this file was written: `P\labels\` has 0 files; `P\gate1\FREEZE.json` absent;
`FROZEN_RULES.md` writable, SHA-256 `2ff8d6f6168ec2db36bd064408e3789d130b5c214b4ddf4625d3db354c1cde99`.
The orchestrator repeats this check immediately before applying R5.

**Authority.** decisions.md D49 (human labelling redesign, 2026-11-16T00:50Z), D49a (step-1 inventory),
D49b (step-3 packet spec). Sources read: D49/D49a/D49b, BRIEF.md §3 and §14, FROZEN_RULES.md (draft,
hash above), `analysis\human_signals_levels.json`, `analysis\human_signals_inventory.json`.

**Blindness statement.** No score, rank, rating value, label or critique text was read for this proposal.
Two scripts were run, both logged below (§R5.9): a feasibility count that reads only id/status columns
(no rating value, no `E`, no rank), and a design calculation on synthetic labels.

---

## R5.0 What R5 changes, in one table

| Area | Before R5 | After R5 |
|---|---|---|
| Who validates the scorer | Author labels 50 items with the §5 instrument (+ optional volunteer) | Step 2: participants' own pre-deliberation position ratings (round level, presence of disagreement only). Step 3: author verifies LLM-extracted evidence on 25 items. Step 4: LLM panel (supplementary). Step 5: fallback. |
| Freeze trigger | first of `author_pass1.csv` / `volunteer_pass1.csv` | first file of any kind in `labels\` (expected: `author_verification.csv`) **or** the first run of the step-2 script, whichever comes first; `FREEZE.json` written before the step-2 reference is computed |
| Gate statuses | PASS / PROVISIONAL_PASS / FAIL / INCOMPLETE | VALIDATED_BOTH / VALIDATED_PRESENCE / VALIDATED_HIDE_EVIDENCE / FAIL / EXPLORATORY_UNVALIDATED / NOT_EVALUATED (§R5.6) |
| §5, §6.0–§6.8 | in force | **superseded**, text kept verbatim for the audit trail (§R5.5) |
| §6.9 (scorer 2) | in force | unchanged (A4 = not run, D47/D48) |
| Headline rate (§6.7) | `H` on 38 author-labelled originals | `H5` from step 3 (§R5.2.5); scorer prevalence secondary |
| `N2_VALIDATED` | via 12-item Fisher check (§6.6) | cannot be earned under R5; N2 is EXPLORATORY in every state (§R5.2.7) |

---

## R5.1 STEP 2 — primary validation "validated against participants' own responses"

### R5.1.1 Choice of reference, and the alternatives rejected

The construct is "hidden disagreement" = (a) the group really disagrees **and** (b) the statement does not
show it. D49a found no human signal that says (b) for a given statement. The planning room's ruling:

**Chosen reference (round level): participant-reported disagreement exists**, from the pre-deliberation
position ratings (`hm_all_position_statement_ratings`, `rating_index == 0`). It covers component (a)
only. It is compared with the scorer's own round-level call for (a): whether extraction E1 found ≥ 1 crux.
For component (b) **there is no usable participant reference**, and step 2 makes no claim about it.

| Candidate signal (D49a) | Level | Ruling | Reason |
|---|---|---|---|
| (1) Pre-deliberation position ratings | participant × question, aggregated to round | **Adopted, for presence only** | Given before any candidate statement exists; no rank, rating of a candidate or statement text involved; covers all eligible rounds (feasibility: 1,622 rounds, 721 launches, §R5.9). It is constant within a round, so it carries no information about the within-round contrast A2 uses, and cannot be circular with A2. |
| (2) Per-candidate agreement / quality ratings | rater × candidate | **Rejected** | Collected beside the ranks and tied to them (Experiment 0 slope −0.576). A reference built from them would make the validation and A2's outcome two readings of the same responses: a scorer "validated" against agreement ratings and then found to predict rank would be largely restating the rating–rank link. **If the council overrides this:** A2 `beta_E` may no longer be called confirmatory or "independent"; every statement of it carries "the scorer was validated against ratings given by the same raters in the same task as the ranks"; no directional claim in title or abstract; and the reference must be computed from ratings of raters other than the ones whose ranks enter A2 for that round, which no round allows (every rater both rates and ranks), so in practice this override makes A2 exploratory. |
| (3) Critiques of the iteration-0 winner | participant × winning statement | **Rejected as primary** | (i) Winner-only: the statement is selected by rank, so any reference is defined on a rank-selected set. (ii) Identifying the winner (`top_candidate`, iteration-1 rows) is a rank-derived output; joining it with the winner's `E` before the gate reveals part of N1 (E of winners) and breaks BRIEF hard rule 3. (iii) Free text needs coding; an LLM coder makes it LLM-mediated, not participants' own responses; a keyword coder has no validity evidence. Allowed only as exploratory after the gate is recorded. |
| (4) Ranking explanations | rater, iteration 0, some cohorts | **Rejected** | Explanations of ranks (circular with A2), 1,750 texts in some cohorts only, needs coding. |
| (5) Round survey | participant × final statement | **Rejected as primary** | Refers to the displayed final statement (post-critique, rank-selected), not to the iteration-0 candidates that are scored and ranked in A2; the final statement has no scorer output of record; the items (`best_expression`, `own_influence`, …) ask about representation of oneself, not whether disagreement was acknowledged. A "minority-side gap" in `own_influence` would be an indirect, noisy signal on a different statement. Exploratory after the gate only. |
| (6) Outside-judge ratings | — | none exist | D49a item 6. |

**Consequence for wording (binding).** The phrase frozen in D49, "validated against participants' own
responses", is used only in the form: **"the scorer's detection of whether a group disagrees was validated
against participants' own pre-deliberation position ratings"**. It is never applied to the hide/show call,
to `E`, or to "crux erasure" as a whole. If the council prefers the bare D49 phrase, it must be scoped
in the same sentence ("…for the presence of disagreement only").

### R5.1.2 Exact rows

| Item | Rule |
|---|---|
| Round set | The eligible rounds of §2 in the 721 confirmatory launches (development launches excluded via `pilots\T3_1\pilot_groups.jsonl`, as `common.restrict_confirmatory`). The round list is taken from the analysis-set table by its `launch_id, round_id` columns only. Expected 1,622 rounds (feasibility, §R5.9); a different count stops the script. |
| Question of a round | `q_r` = the `question.id` of the round's iteration-0 `HUMAN_CITIZEN` rows in `hm_all_candidate_comparisons`. Not exactly one value → round unusable, counted. |
| Members | `M_r` = distinct `own_opinion.metadata.participant_id` over those rows (the opinion authors given to E1). The script asserts `|M_r|` equals the number of opinions in the round's E1 input; a mismatch is listed and the round is unusable. |
| Member's pre-rating | The row of `hm_all_position_statement_ratings` with `launch_id = L_r`, `question.id = q_r`, `metadata.participant_id = m`, `rating_index == 0`, `metadata.provenance == HUMAN_CITIZEN`, `metadata.status == COMPLETED`, and `ratings.agreement` an array of length 1 whose token is one of the 7 below. If several rows qualify, the one with the smallest `monotonic_timestamp` (feasibility found 0 such duplicates). Otherwise the member is **unrated**. |
| Value map | STRONGLY_DISAGREE −3, DISAGREE −2, SOMEWHAT_DISAGREE −1, NEUTRAL 0, SOMEWHAT_AGREE +1, AGREE +2, STRONGLY_AGREE +3. Any other token (e.g. `MOCK`) = unrated. |
| Usable round | ≥ 3 rated members **and** at most 1 member of `M_r` unrated. |
| **Human reference `Hsplit_r`** | 1 if at least one rated member has value ≥ +1 **and** at least one has value ≤ −1; else 0. NEUTRAL counts to neither side. |
| Scorer call `Sdis_r` | 1 if scorer 1's E1 extraction of record (`a2_extractions_v2.jsonl`) has ≥ 1 crux after the §3 sanitising rule; 0 if it has 0 cruxes. Extraction missing after the retry → counted as the wrong call (as §4 "Parse failure" does for the gate). Rounds dropped for context length: excluded, counted. |
| Not read | Any rank, `ratings.agreement`/`ratings.quality` of candidates, `E`, per-crux labels, critique, survey, `top_candidate`. A unit test asserts that the step-2 script's column lists contain none of these. |

### R5.1.3 Statistic, interval, bar

| Item | Rule |
|---|---|
| Primary statistic | Balanced accuracy of `Sdis` against `Hsplit` over usable rounds: `BA2 = (sens + spec)/2`, sens = P(Sdis=1 | Hsplit=1), spec = P(Sdis=0 | Hsplit=0). |
| Interval | Launch-cluster percentile bootstrap: resample the usable launches with replacement, keep all their usable rounds, recompute `BA2`; B = 10,000, `numpy.random.default_rng(20261141)`; a resample with only one `Hsplit` class scores 0.5 and is counted. 2.5th and 97.5th percentiles. |
| Usable data (else UNUSABLE = "no usable participant reference") | ≥ 200 usable rounds from ≥ 100 launches, **and** each `Hsplit` class has ≥ 30 rounds from ≥ 15 launches **(J)**. |
| Outcome | **PASS**: lower bound > 0.5 **and** point `BA2` ≥ 0.60 **(J)**. **WEAK**: lower bound > 0.5 and point < 0.60. **FAIL**: lower bound ≤ 0.5. **UNUSABLE**: usability rule not met. |
| Why a point bar | With ~1,600 rounds a lower bound above 0.5 is reached by almost any non-zero association; "better than chance" alone is not validation at this n. 0.60 is a judgement call, not derived. |
| Also reported, no rule | sens, spec, the 2×2 table; `BA2` on rounds with all members rated; `BA2` with a strong-split reference (≥ +2 and ≤ −2); Spearman between crux count (0–4) and the population SD of member values, same launch bootstrap; the counts of unusable rounds by reason. |
| Expected weakness, stated now | The ratings are on the question's one axis; cruxes may be on reasons or priorities among members on the same side. Rounds where all members are on one side but the scorer finds a crux count as scorer false positives, so `spec` is expected to be low for reasons of construct mismatch, not only scorer error. A WEAK or FAIL result is reported with this sentence and is not explained further after the fact. |
| Falsifier | FAIL (lower bound ≤ 0.5) falsifies the claim that the scorer's "disagreement present" call tracks the group's own reported positions. |
| What it cannot show | Anything about whether a statement shows or hides the disagreement; anything about `E`'s within-round variation; anything about N2 statements' labels. Validation of presence covers N2 rounds' crux extraction only to the extent the same opinions and E1 output are reused. |

### R5.1.4 Order and code discipline

1. The step-2 script (`analysis\step2_participant_reference.py`) is written and tested on synthetic data
   **before** the freeze; its SHA-256 is written into `FREEZE.json`.
2. It refuses to run unless `gate1\FREEZE.json` exists and `FROZEN_RULES.md` hashes to the value in it.
3. Its first real run computes reference and comparison in one pass and writes
   `gate1\STEP2_computed__<utc>.json` (never overwritten). It is run once; a crash before the output
   file is written may be re-run, logged; a completed run is never repeated.
4. Per-round outputs (scorer calls per round) are not shown to the author before `author_verification.csv`
   is saved (they include the packet rounds).

---

## R5.2 STEP 3 — verification packet (D49b), derived quantities

Wording of record: **"human verification of LLM-extracted evidence by a hypothesis-aware author"**.

### R5.2.1 Inputs fixed before the author's file

The 25 items, reserve list, extracted quotes, and scorer 1's `E` and crux count for each of the 25 items
are written and hashed before `author_verification.csv` exists; their hashes go into `FREEZE.json`. No
item is rescored after the file exists. Packet layout and hidden fields: D49b, unchanged.

### R5.2.2 Label file schema

`P\labels\author_verification.csv`, UTF-8, header row, exactly the columns
`item_id,q1_disagree,q2_acknowledged,comment,pass_started_utc`, exactly 25 rows, `item_id` as in the
packet. `q1_disagree`, `q2_acknowledged` ∈ {`YES`,`NO`} (case and surrounding spaces ignored; no other
token). `q2_acknowledged` is answered on every row, including rows with Q1 = NO (D49b). `comment`
optional. `pass_started_utc` as in old §5. Blank/invalid token, unknown or repeated id, or wrong row count
= incomplete; the pipeline reports and waits, never fills. First complete file is hashed into `FREEZE.json`
on arrival and never replaced. (If the packet builder has already fixed different column names, the
builder's names govern and the orchestrator records the mapping before the packet is released.)

### R5.2.3 Derived quantities

Notation per item i: `Q1_i`, `Q2_i` (author), `S_i` = scorer hide call (1 if `E ≥ 0.5`; 0 if `E < 0.5`
or 0 cruxes; missing `E` = the call opposite to the author's, i.e. counted wrong), `C_i` = scorer found ≥ 1
crux, `A_i` = 1 if `Q2_i = NO` (author: not acknowledged).

| Quantity | Definition | Interval |
|---|---|---|
| Evidence validity `V_ev` | share of the 25 items with `Q1 = YES` | Wilson 95% |
| Same, by kind | originals (19) and N2 (6) separately | Wilson 95% |
| Presence agreement (no rule) | 2×2 of `C` vs `Q1` on all 25; raw agreement | Wilson 95% on raw agreement |
| **Scorer vs author (the step-3 test)** | on items with `Q1 = YES` (pooled originals + N2): 2×2 of `S` vs `A`; sensitivity, specificity, `BA3`; Cohen's kappa; one-sided Fisher exact p (alternative: `S` agrees with `A` more than independence) | Wilson 95% on sens and spec; `BA3` and kappa with an item percentile bootstrap, B = 10,000, `default_rng(20261142)`, descriptive |
| Split reporting (no rule) | the same 2×2 for originals and for N2 items separately | — |
| `H5` (headline rate, §R5.2.5) | originals with `Q1 = YES`: share with `Q2 = NO` | Wilson 95% |

Each item is one launch, so item resampling equals launch resampling.

### R5.2.4 Usable and outcome rules

| Item | Rule |
|---|---|
| Usable for the scorer comparison | file complete **and** ≥ 10 items with `Q1 = YES` **and** ≥ 3 such items in each `A` class **(J)**. Otherwise step 3 = UNUSABLE for the comparison; `V_ev` and the presence table are still reported. |
| SUPPORTED | usable and Fisher p ≤ 0.05 (same rule as old §6.6). |
| CONTRADICTED | usable and point `BA3` ≤ 0.5. |
| INCONCLUSIVE | usable, neither of the above. |
| Not a gate FAIL | CONTRADICTED and INCONCLUSIVE never fail gate 1 on their own (power below). They decide wording (§R5.6). |
| Power, stated in advance (synthetic, `r5_step3_power.json`) | A scorer that matches the author on 80% of items is SUPPORTED with probability 0.32 at n = 10 Q1-yes items (half "not acknowledged"), 0.49 at 12, 0.62 at 15, 0.77 at 20, 0.87 at 25; 0.19 / 0.32 / 0.42 / 0.57 / 0.72 when three quarters are "not acknowledged". A chance-level scorer: 0.4–2.0%. A 70%-accurate scorer is CONTRADICTED with probability 0.10–0.23 at n = 10–12, which is why CONTRADICTED is not allowed to fail the gate. **An INCONCLUSIVE outcome is the likely outcome for an adequate scorer and is not evidence against it.** (The simulation does not apply the ≥ 3-per-class rule.) |
| Unit mismatch, stated now | The author judges one LLM-chosen pair of quotes; `S` summarises all of scorer 1's cruxes. A statement can show the quoted disagreement and hide another crux (`S = 1`, `A = 0`). Agreement is bounded below 1 by design. |
| What it cannot show | Hypothesis-blind validity (the author knows the hypothesis); self-consistency (there is no second pass under D49); generator- or cell-level validity on N2 (6 items). |
| Falsifier | CONTRADICTED is the observed failure of the scorer's hide call to agree with the author better than chance on these items. |

### R5.2.5 Headline rate `H5` (replaces §6.7)

`H5 = n(originals with Q1 = YES and Q2 = NO) / n(originals with Q1 = YES)`, Wilson 95%, n ≤ 19
(half-width about ±22 points near one half). Wording: "In N of 19 sampled original statements, the author
judged that the statement did not acknowledge a disagreement that an LLM had extracted from the group's
opinions (human verification of LLM-extracted evidence by a hypothesis-aware author)". Printed beside it,
always: `V_ev`, the count with Q1 = NO, and the scorer's rate on the same 19 items and on the confirmatory
set (secondary). Reported only if at least 10 originals have Q1 = YES; otherwise the scorer prevalence is
the only rate and is labelled "scorer estimate, not checked against human judgement". Never compared
numerically with rates from other studies.

### R5.2.6 Timing guard

No real-rank output, and no per-item scorer output for the 25 items, exists in any file the author can be
shown before `author_verification.csv` is complete and hashed. `gate1.py` records whether any real-rank
output existed at that moment; the paper prints it.

### R5.2.7 N2 consequence

With 6 N2 items there is no N2 validity check. `N2_VALIDATED` cannot be earned under R5. N2 results carry
**EXPLORATORY** and "the scorer's hide/show call was checked on 6 N2 statements only (descriptive)" in every
gate state, and N2 can lead the paper only under the old §7.3 rules with that label. This requires a matching
amendment of `N2_ANALYSIS_SPEC.md` (gate-status mapping, §R5.7) with a new hash before any N2 scoring.

---

## R5.3 STEP 4 — LLM annotator panel (supplementary; not human)

Wording of record: **"LLM annotator panel (supplementary; not human)"**. Never primary, never "human",
"rater", "inter-rater", "independent validation" or "annotators" without "LLM".

| Item | Rule |
|---|---|
| Members | (1) `tiiuae/Falcon-H1-34B-Instruct` (TII), alias `falcon-h1-34b`; (2) `CohereLabs/c4ai-command-r7b-12-2024` (Cohere), alias `command-r7b` (licence accepted, D48; CC-BY-NC); (3) `granite-4.2-30b` (IBM), alias `granite4.2-30b`. All differ from the scorer (Qwen) and the five N2 generators (Qwen, Gemma, Mistral, Phi, Llama); lineage limits as in old §6.9 [R4a]. |
| Why not gpt-oss-120b | It extracts the quotes (D49b). In the packet task it would judge its own extraction (Q1), which is self-evaluation. It keeps the extractor role only. |
| Format bar (decides membership; development launches only) | Per member: ≥ 20 calls on development-launch items built exactly like packet items (gpt-oss quotes on dev rounds); at most one revision of the added format line; bar **(J)**: ≥ 95% of calls valid after one retry with seed 1. Decided before any packet item is sent; never re-run after a packet-item call. The granite/Falcon/Command failures on the scorer's E1/L1 bar (D44–D48) do not carry over: the task and format differ. |
| Task P1 (primary panel task) | Exactly the author's view and questions: question, quote A, quote B, statement; Q1 and Q2 with the author's wording; format line `Return JSON only: {"q1_disagree": "YES" or "NO", "q2_acknowledged": "YES" or "NO"}`. Items: the 25 packet items. |
| Task P2 (secondary panel task) | The old §5 instrument (volunteer version text, verbatim, as in old §6.8) on the 50 R4 pass-1 items (38 originals, 12 N2), with old §6.8's format line. These items were never labelled by a human; P2 has no human comparison. |
| Decoding and isolation | temperature 0, seed 0, one item per call, fresh context, no system prompt beyond the template; settings and revisions in `gate1\llm_panel\panel_manifest.json` before the first packet-item call; one retry with seed 1; still invalid → missing, counted, never filled. Outputs in `gate1\llm_panel\`, **never in `labels\`**. |
| Majority rule | Per item and question: the value given by ≥ 2 members. If a member is missing, the two others must agree; otherwise `NO_MAJORITY` (counted, excluded). P2 majority over three categories (`HIDES`, `NOT_HIDING` = SHOWS or NO_DISAGREEMENT, `UNSURE`); no 2-of-3 → `NO_MAJORITY`. With only 2 members passing the format bar: unanimity of the two. With fewer than 2: no panel; members reported individually. |
| Reported (no rule) | Fleiss' kappa among members and pairwise Cohen's kappa; Gwet's AC1. P1: panel majority vs author on Q1 and Q2 (raw agreement, kappa, AC1; item bootstrap B = 10,000, `default_rng(20261143)`); panel-majority `A` vs scorer `S` on items with majority Q1 = YES (2×2, BA3-panel). P2: panel-majority HIDES vs scorer binary, balanced accuracy on the 38 originals (item bootstrap, same seed), 2×2 on the 12 N2 items; panel hide-rate on the 38. |
| Timing | Panel results are not shown to the author before `author_verification.csv` is complete. |
| Status | No cut-off, no rule, no effect on gate status, labels, `H5` or any wording state. High agreement with the author is not evidence that the author is unbiased; agreement between LLMs and the scorer is model-on-model agreement. |

---

## R5.4 STEP 5 — fallback: exploratory, not human-validated

**Trigger (exact).** Gate status `EXPLORATORY_UNVALIDATED` (§R5.6): no step FAILED, and neither step 2 =
PASS nor step 3 = SUPPORTED. This covers D49 item 5 ("neither (2) nor (3) yields usable data") and, as the
careful reading, also usable-but-unsupportive outcomes (step 2 WEAK, step 3 INCONCLUSIVE/CONTRADICTED).
Also applied to every output if the gate is `NOT_EVALUATED` at handover (then nothing on real ranks runs at
all, as old §12).

**Consequences.**
- Every real-data result (A2, A2b–A2i, N1, A3, N3, N4, prevalence, N2) is stamped `EXPLORATORY_UNVALIDATED`
  in file names' records, RUNS.md, tables, figures and text. No Holm family is reported as confirmatory;
  p-values may be printed but no "significant", "detected" or "confirm".
- **Title:** no directional claim; no "validated".
- **Abstract:** first sentence of results states that the scorer could not be validated against human
  judgement in this study, and why (no usable participant reference / author verification inconclusive or
  unusable). No rate is called a human-validated rate. A2 appears only as "an exploratory association
  between an unvalidated LLM score and rankings". The novelty sentence becomes "to our knowledge, the first
  attempt to test whether participants' rankings favour hiding statements"; never "first test" alone.
- **Methods:** describe steps 2–4 as pre-registered (R5, hash and freeze time), with their usable rules
  and the outcome; the panel wording of §R5.3.
- **Results:** every estimate with its interval and the stamp; step-2 and step-3 numbers printed even if
  UNUSABLE/INCONCLUSIVE (with n and the reason); power statements of §R5.2.4 printed.
- **Discussion:** a paragraph on what a validation would need (blind human labels at n giving power, a
  statement-level participant signal); no claim that rankings do or do not favour hiding statements.
- The §7.1 tier wording still applies on top (an EXPLORATORY_UNVALIDATED paper with a NOT MEASURABLE tier
  says both).

---

## R5.5 Old R4 sections

Mark as **[SUPERSEDED by R5; kept for the audit trail, not in force]**, text unchanged:
the header paragraph "Validation label [R4]"; §5 (all rows and the instructions; the instruction text is
reused verbatim only as P2's input); §6.0; §6.1 rows "Size", "Second pass", "Row order", "Use of the second
pass" (the sample of record `sample.json` and `n2_items.json` stay, as the frame of D49b's 25-item draw);
§6.1a "Allocation to labelers"; §6.1b; §6.2; §6.3; §6.4; §6.4a rows that need §6.3 labels (`BA_crux`, `BA_sh`,
`D1h`, scorer-v1 comparison), except the **binding wording rule**, which is re-anchored in §R5.6;
§6.5 PROVISIONAL state (the first paragraph, real-rank lock, stays, with "GATE1_RESULT.json" now holding an
R5 status); §6.6; §6.7; §6.8; §12 rows that reference kappa, pass 2, adjudication or `PROVISIONAL`; Known
weaknesses 6, 7, 8, 10 (kept, marked historical); §14 items 15–17.
Not superseded: §1–§4, §6.9 (A4 not run), §7 (with §R5.6 replacing "gate 1 PASS" in §7.3), §8–§11, §13,
Appendix A. `labels_build\r4\` stays VOID (D49).

---

## R5.6 Gate 1 under R5: statuses, what each unblocks, and the freeze

### Freeze trigger (replaces the header's trigger)

`FROZEN_RULES.md` freezes at the first of: (a) any file appearing in `P\labels\` (expected
`author_verification.csv`; any other name is reported and not read); (b) the first run of the step-2
script. **`gate1\FREEZE.json` must be written by `analysis\freeze.py --out gate1\FREEZE.json` before the
step-2 reference is computed**; the step-2 script refuses otherwise (§R5.1.4). `FREEZE.json` records: the
trigger, UTC time, `FROZEN_RULES.md` SHA-256, the SHA-256 of the step-2 script, the 25-item packet and key,
the extracted-quotes file, scorer outputs for the 25 items, and (if present) `author_verification.csv`.

### Statuses (computed by `gate1.py`, re-derived by Opus, recorded by the planning room in `GATE1_RESULT.json`)

Recorded only when step 2 has an outcome (PASS/WEAK/FAIL/UNUSABLE) **and** step 3 has one
(SUPPORTED/INCONCLUSIVE/CONTRADICTED/UNUSABLE). Step 3 is UNUSABLE without a file only if the human writes a
decisions.md entry that no file will come; the pipeline never declares that itself.

| Status | Condition | Real-rank analyses | Claims allowed |
|---|---|---|---|
| FAIL | step 2 = FAIL | run only as old §12 "after a FAIL" (appendix, unvalidated) | §12 "not yet measurable" |
| VALIDATED_BOTH | step 2 = PASS and step 3 = SUPPORTED | A2 confirmatory, Tier 2 Holm family | §1/§7.1 wording; every sentence names both validations with their wording; "hypothesis-aware author" and n stated |
| VALIDATED_PRESENCE | step 2 = PASS, step 3 ≠ SUPPORTED | A2 confirmatory as a test; Tier 2 family | Old §6.4a binding sentence fires: "the scorer is validated for detecting whether a disagreement is present, not for detecting whether a statement hides it"; every `beta_E` carries "the show-versus-hide contrast behind this estimate was not validated against human judgement"; **no directional rank claim in title or abstract**. If step 3 = CONTRADICTED, add "and on 25 author-checked items the hide call agreed with the author no better than chance". |
| VALIDATED_HIDE_EVIDENCE | step 3 = SUPPORTED, step 2 ∈ {WEAK, UNUSABLE} | as VALIDATED_PRESENCE | Directional claim allowed only in the §7.1 INFORMATIVE tier and only with "supported by human verification of LLM-extracted evidence by a hypothesis-aware author on N items"; step 2 outcome stated |
| EXPLORATORY_UNVALIDATED | no FAIL, no PASS in step 2, no SUPPORTED in step 3 | run, all stamped | §R5.4 |
| NOT_EVALUATED | step 3 unresolved at handover | none (hard rule 3) | old §12 "labels incomplete or absent" |

**What unblocks real data.** Real ranks, real ratings and N1/A2/Tier-2 real fits are unblocked only by a
recorded `GATE1_RESULT.json` holding one of the first five statuses. Step 2 alone does not unblock anything;
step 4 never blocks or unblocks anything. Hence BRIEF hard rule 3 is intact: no real-data main analysis
before the gate is recorded, and the gate cannot be recorded before the author's file is resolved, so the
author cannot see real-rank results before verifying. There is no PROVISIONAL state under R5.
**N2 scoring** beyond the 25 packet items: permitted once any of the first five statuses is recorded, with
N2 always EXPLORATORY (§R5.2.7). Needs the N2 spec amendment (§R5.7).

---

## R5.7 Follow-ups required before freeze (owners)

1. Code owner: `step2_participant_reference.py` + synthetic tests; `gate1.py` R5 statuses and the step-3
   statistics; column-whitelist unit test; `common.check_kind` mapping of R5 statuses
   (`EXPLORATORY_UNVALIDATED` and FAIL → exploratory stamp).
2. Packet builder: D49b packet + key; schema of §R5.2.2; scorer outputs of the 25 items hashed.
3. Runner: panel format smokes (dev launches only), `panel_manifest.json`.
4. N2 code owner: `N2_ANALYSIS_SPEC.md` Amendment 5 (R5 status mapping; `N2_VALIDATED` unavailable) with new
   hash, council vote, before any N2 scoring.
5. Orchestrator: poller watches `labels\` for any file; freeze before step 2.

---

## R5.8 The five weakest choices in R5

1. **Step 2 validates presence, not hiding.** The only clean participant signal says whether the group
   disagrees on the question's main axis; it says nothing about statements, and it mismatches the crux
   construct (cruxes can sit within one side), which depresses specificity. The "validated against
   participants' own responses" phrase is therefore scoped and much weaker than it sounds.
2. **The 0.60 point bar and the usability minimums (200/100/30/15) are judgement calls.** With ~1,600 rounds
   the lower-bound rule alone is nearly vacuous; the point bar decides PASS vs WEAK and was not derived.
3. **Step 3 is small, single, hypothesis-aware and unit-mismatched.** ≤ 25 items (probably 10–20 with Q1 =
   yes), one author who knows the hypothesis and sees the statement, no second pass, and a quote pair
   compared with a crux-set score. An adequate scorer is more likely INCONCLUSIVE than SUPPORTED at n ≤ 15.
4. **The panel is three models that each failed the scorer's format bar on another task**, judged on a new
   format bar; LLM errors are correlated; P2 is model-vs-model only. gpt-oss is excluded from the panel to
   avoid self-evaluation, at the cost of dropping the one model with a passed annotator smoke.
5. **The status logic is a judgement:** step 2 FAIL dominates a step-3 SUPPORTED; step 3 can never fail the
   gate; usable-but-unsupportive outcomes go to EXPLORATORY (stricter than D49 item 5's literal "no usable
   data"); and N2 loses any path to `N2_VALIDATED`.

---

## R5.9 Computations made for this proposal (logged)

| Script | Reads | Output | Result used here |
|---|---|---|---|
| `analysis\planning\r5_feasibility.py` (SHA-256 `3c7671e2…07c06d3`), run 2026-11-16T00:58:03Z | `a2_long_shuffled.parquet` columns `launch_id, round_id` only; `pilot_groups.jsonl`; candidate-comparisons id/provenance/question columns; position-ratings id/status/rating_index columns (**no `ratings.agreement`, no `E`, no rank**) | `r5_feasibility.json` (SHA-256 `e3faf040…b853103`), `log_r5_feasibility.txt` | 1,622 confirmatory rounds, 721 launches; all have one question id; members per round 3/4/5 = 3/180/1,439; under the usable rule 1,622 rounds / 721 launches have ≥ 3 members with a COMPLETED pre-rating row and ≤ 1 missing (1,604 rounds / 713 launches with none missing); 0 duplicate pre-rating keys. Upper bound: token validity not read. Class balance of `Hsplit` **not computed**. |
| `analysis\planning\r5_step3_power.py` (SHA-256 `c4f794a9…0030d7d`) | synthetic labels only, seed 777, 4,000 sims per cell | `r5_step3_power.json` (SHA-256 `702b737a…c6d100`), `log_r5_step3_power.txt` | power figures in §R5.2.4 |

---

## R5.10 Open questions for the council

1. Accept the scoped wording ("…detection of whether a group disagrees was validated against participants'
   own pre-deliberation position ratings") in place of D49's bare phrase? The human froze the bare phrase;
   using it unscoped would overstate.
2. Is a presence-only primary validation acceptable to the human as "step 2", or should step 2 be declared
   "no usable participant reference" for the hiding construct (and step 2 reported as a secondary check)?
3. PASS bar for step 2: point `BA2` ≥ 0.60 plus lower bound > 0.5 — or lower bound > 0.5 alone (the brief's
   bar), accepting that it is nearly certain at n ≈ 1,600?
4. Panel membership: exclude gpt-oss (self-evaluation on Q1) as proposed, or include it and drop one of
   Falcon / Command / Granite? Run P2 at all (adds model-vs-model numbers, more forking paths)?
5. Usable-but-unsupportive → EXPLORATORY_UNVALIDATED (stricter than D49 item 5's literal text): confirm.
6. Should step-3 CONTRADICTED be able to fail the gate? Proposed no, on power grounds (§R5.2.4).
7. N2: accept that `N2_VALIDATED` is unavailable and approve the N2 spec Amendment 5 path?
8. Exploratory after the gate: approve in advance a survey "minority-side gap" analysis and an LLM-coded
   critique analysis as labelled exploratory, or leave them out entirely?
