# PLAN.md — T3-1 start plan

P = `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1`. Written by the planning room,
2026-11-15. Definitions: FROZEN_RULES.md (FR). Run details: EXPERIMENTS.md.

Pace (BRIEF §0): this plan has no clock times. Steps are ordered by dependency. If something
is unfinished at handover it is reported as unfinished.

## 1. Where things stand

- Done: brief saved; data gate A passed; Modal serving smoke-tested for Qwen3.8-27B and
  Gemma-4-12B; spend $0.65.
- Experiment 0 is **confirmed in writing as per rater** (decisions.md D6;
  `analysis\EXP0_rank_unit.md`, `exp0_check.py`), in agreement with the pilot's
  `exp0_rank_unit.json`. The BRIEF §14 fallback is not triggered and N4 stays in. Still open
  from FR §2: the rank-direction check.
- Built and tested on dummy and shuffled data only (decisions.md D8): `gate1.py`,
  `a2_within_round.py`, `n1_winner_vs_mean.py`, `n2_grid.py`. They must be aligned with FR
  (list at the top of EXPERIMENTS.md).
- Not started: `build_analysis_set.py`, scorer manifest, gate sample, packets, any real-rank
  analysis.
- No label file exists. FR is a draft and the human may still edit it.

## 2. Agent roster

Each agent gets its own system prompt in `P\agents\<name>.md` (goal, inputs, outputs, how to
think, how to critique, done-test). An evaluator never reviews its own work and starts with
fresh context.

| Agent | Model | Job | First output |
|---|---|---|---|
| Orchestrator | Opus | Loop, status.md every 30 min, decisions.md | status.md |
| Planning room | Fable | This plan, gate decisions, replans, final coherence read | FR, EXPERIMENTS, PLAN |
| Baseline | Sonnet | Repo inventory; prompt and skill audit (write missing skills, incl. report layout and figure skills); data schema check; Modal check | `P\analysis\BASELINE.md` |
| Stats coder | Sonnet | `e0_rank_unit.py`, `build_analysis_set.py`, `make_dummy.py`, gate scripts, `a2_within_round.py`, Tier-2 scripts, unit tests | Tests passing on dummy data |
| Scorer runner | Sonnet | `score_erasure.py`, prompt files copied from FR Appendix A, `scorer_manifest.json`, dev-set smoke test | Manifest |
| Grid runner | Sonnet | N2, N6 | Council request |
| Fine-tune runner | Sonnet | F | Council request |
| T1-1 runner | Sonnet | B | Council request |
| Figure maker | Sonnet | Figures from scripts only, with intervals and takeaway captions | Figure scripts on dummy data |
| Methods and related-work drafter | Sonnet | Methods fact sheet, related work, prior-work notes | Drafts in `P\report\` |
| Optimizer | Sonnet | Batching, caching, parallel containers | Throughput probe report |
| Cost cutter | Haiku (ledger), Sonnet for GPU choice | Cheapest GPU per job, kill idle jobs, `ledger.csv` | Ledger kept current |
| Label poller | Haiku | Check for label files every 15 minutes (§6) | Poll log |
| Novelty scouts ×2 | Sonnet | Prior-work check on every claim; at most 3 new experiments each | Scout notes |
| Methodologist | Opus | Method review; experiment council; results room | Critiques |
| Skeptical judge | Opus | Experiment council; red team | Critiques |
| Statistics reviewer | Opus | Independent re-derivation of kappa, gate and A2 from raw files | Review notes |
| Ethics and dual-use reviewer | Opus | Tier 4 sign-off; limitations and dual-use appendix | Review notes |
| Citation verifier | Sonnet (fetching by Haiku) | Opens and checks every reference; results room | Reference table |

Concurrency follows BRIEF §3.9: if free RAM is under 2 GB or rate limits hit, reduce the
number of parallel agents first, never the checks.

## 3. Sequencing

**Stage A. Before any label can exist.**
1. Stats coder aligns the existing scripts with FR and writes `build_analysis_set.py`.
   The methodologist runs the ≥ 200-reshuffle coverage check (FR §7); any change of interval
   method must land in FR before freeze.
2. Experiment 0: done (§5 below). The rank-direction check is added to `exp0_check.py` and logged.
3. `build_analysis_set.py` reproduces the counts in FR §2 (1,960 rounds, 871 launches, 9,501
   rater rows) and counts the A3 and N3 qualifying launches.
4. Scorer runner copies the prompts from FR Appendix A, runs the smoke test on the
   development set (opinions and statements only), fixes format problems at most once, and
   writes `scorer_manifest.json`. This is a Modal job: estimate logged, timeout set.
5. `g1_sample.py` writes `gate1\sample.json`; `g1_packets.py` writes the two packets.
6. Opus checks the packets for leaks: no rankings, ratings, scores, IDs that reveal the
   round, or hypothesis wording.
7. The orchestrator tells the human in status.md that the packets are ready and that the
   first label file freezes FR. No reply is awaited.

**Stage B. While labels are out.** All on dummy or shuffled data, or not analysis at all.
- Scorer-1 scoring of the 60 gate items (A1 cap), then full scoring after council approval
  (A2 cap is over $5). Scoring is measurement, not analysis; it never reads ranks.
- Stats coder builds and tests every analysis script on `make_dummy.py` output and on
  within-rater shuffled ranks. A planted-effect dummy set must be recovered and a null dummy
  set must give coverage near 95%; both checks are logged.
- Figure maker, drafter, novelty scouts, citation verifier and the past-papers and report
  councils work in parallel.
- Tier-4 council requests are prepared and decided.

**Stage C. Labels arrive.** See §6. Kappa, then human adjudication, then the gate.

**Stage B, added [R1].** After the E1 v2 full scoring run: `a2_informativeness.py` writes
`gate1\A2_TIER.json` (FR §7.1) from scorer output and shuffled ranks. Opus re-derives the counts.
The planning room logs the tier in decisions.md. This happens before any real rank is read and
does not wait for labels. The thresholds are already fixed and are not revisited.

**Stage D. After the gate is recorded.**
- PASS: A2, then Tier 2, then N2 and N5. Each number goes to the results room.
- **[R1]** PASS and tier INFORMATIVE: as the line above; A2 leads the paper.
- **[R1]** PASS and tier LOW-POWER or NOT MEASURABLE: `prevalence.py` and N2 scoring go first,
  then A2 and Tier 2 (all still run and are reported). The paper leads with prevalence and N2
  and reports A2 with its tier wording (FR §7.3). The drafter prepares both paper skeletons now,
  on dummy numbers, so neither is written in a hurry.
- **[R1]** PASS and the FR §6.4a wording rule fires: no directional rank claim in title or
  abstract, whatever the tier.
- FAIL: the "not yet measurable" version (FR §12). Tier 4 work continues.
- NOT EVALUATED (labels still missing): keep building; no real-rank analysis.

**Stage E. Handover.** When Tiers 1 to 3 are complete and verified, or when the human asks,
write HANDOVER.md (BRIEF §13), then keep running approved Tier 4 work.

## 4. Rooms

| Room | Members | Meets |
|---|---|---|
| Planning | Fable + orchestrator | Now; after gate 1 is recorded; after each tier; on any §14 event |
| Experiment council | Skeptical judge, methodologist, cost cutter | Before any job over $5 (first: the A2 full-scoring job) and before every Tier 4 experiment. Needs: claim supported, prior-work check, cost, stop condition. Two of three; a tie is no |
| Results room | Methodologist + citation verifier | After every analysis run, before a number or reference enters a draft |
| Red team | Opus | On each draft of the results pack: scores 1-5 on impact and innovation, execution, clarity; top three fixes |
| Past-papers council | Sonnet fetch + Opus tagging | Once, in Stage B; writes PAPER_CHECKLIST.md |
| Report council | Drafter, figure maker, Opus page checker | From Stage B on dummy figures; after each tier on real ones. Prepares parts only; never calls a layout final |

Critique protocol (BRIEF §9) applies in every room: flaw, evidence, severity, cheapest fix;
no praise; critics do not edit; two rounds at most, then the orchestrator decides and logs why.

## 5. Experiment 0 and what happens if ranks are per group

Outcome so far: per rater, logged in decisions.md D6 from two independent checks (pilot `s08`
and baseline `exp0_check.py`). That entry is the "in writing" confirmation. Proceed with
per-rater A2, N1 and N4.

The branch below stays in the plan in case a later check (for example the rank-direction
check, or the statistics reviewer's re-derivation) contradicts D6.

**If a later check says per group** (BRIEF §14; nobody waits for the human):
- Log it in decisions.md with the two measured shares.
- A2 and N1 switch to the group-level models in FR §11. N4 is skipped.
- The planning room meets to move agent effort to F and B: their council requests go first
  in the queue, and the stats coder's Tier-2 time shrinks to N1, A4, A3, N3.
- The methods draft and the limitations section state that the outcome is a group aggregate
  with fewer data points.
- Gate 1 is unchanged: it does not use ranks.

**If the rank direction cannot be confirmed:** A2 and N1 are blocked and logged as blocked;
gate 1, N2, N3 (contents only) and Tier 4 continue.

## 6. Label-file polling (every 15 minutes)

The poller (`poll_labels.py`, Haiku) checks whether `P\labels\L1.csv`, `P\labels\L2.csv` or
`P\labels\ADJ.csv` exists. It reads file names, sizes and hashes; it does not interpret labels.

| Event | Action |
|---|---|
| Neither file exists | Log the check. Keep building on dummy data. Never create, fill or simulate a label |
| First of L1.csv / L2.csv appears | Immediately: set FROZEN_RULES.md read-only; write its SHA-256 and the UTC time to `gate1\FREEZE.json` and decisions.md. If `scorer_manifest.json` does not exist yet, log that as a deviation (packets should not have been released) |
| A file exists but has blank or invalid labels, or missing `item_id`s | Report in status.md exactly which rows are incomplete. Wait. Do not repair |
| Both files complete | Run the kappa step of `gate1.py` → `KAPPA.json`. Then `g1_adjudication_sheet.py`. Tell the human in status.md that the sheet is ready |
| Kappa below 0.60 or undefined | Computed status is FAIL already. Opus re-derives; planning room records it. Adjudication is optional and only for reporting |
| `ADJ.csv` complete (or no item needed adjudication) | Run the validity step of `gate1.py` → `gate1_computed.json`. Opus re-derives it from raw files. Planning room meets, writes `GATE1_RESULT.json` with the computed status and logs the gate decision |

Polling continues through handover. A label file that appears after HANDOVER.md is written
still triggers the same steps.

**[R4] The table above is superseded (decisions.md D34, D37; FR §5, §6.0 to §6.5).** The poller
watches `P\labels\author_pass1.csv`, `author_pass2.csv`, `volunteer_pass1.csv` and `ADJ.csv`. It
reads names, sizes, modification times and hashes; it does not interpret labels.

| Event | Action |
|---|---|
| No label file | Log the check. Keep building on dummy data. Never create, fill or simulate a label |
| First label file of any kind appears (`author_pass1.csv` or `volunteer_pass1.csv`) | Immediately: set FROZEN_RULES.md read-only; write its SHA-256, the UTC time and the label file's hash and modification time to `gate1\FREEZE.json` and decisions.md. If the scorer manifest, the annotator manifest or the N2 item list does not exist yet, log that as a deviation |
| `author_pass1.csv` exists but is incomplete | Report the rows in status.md. Wait. Do not repair |
| `author_pass1.csv` complete = **gate time** | Run `gate1.py`. It writes `gate1\DESIGN.json` once: two-human design if `volunteer_pass1.csv` exists at that moment, else single-labeler design. Nobody starts this run earlier or delays it |
| Single-labeler design | Validity step on the pass-1 labels → Opus re-derives → planning room records `PROVISIONAL_PASS` or `FAIL`. On `PROVISIONAL_PASS` the real-rank analyses may start, stamped PROVISIONAL; N2 scoring waits. Tell the human in status.md that pass 2 may be done once one hour has passed since the pass-1 file was saved, and that no result should be read before it |
| `author_pass2.csv` appears (single-labeler) | Check the one-hour rule. If it fails: report, do not compute kappa, wait. If it holds: kappa step → `KAPPA.json` (write-once) → Opus re-derives → planning room records `PASS` or `FAIL`; stamps updated; on PASS, N2 scoring may start |
| Two-human design | Inter-rater kappa → `KAPPA.json`. Below 0.40 or undefined: computed status FAIL. Otherwise `g1_adjudication_sheet.py`; tell the human the sheet is ready; when `ADJ.csv` is complete, validity step → Opus re-derives → planning room records `PASS` or `FAIL`. No real-rank run and no result shown to either annotator before that. `author_pass2.csv`, when it arrives, gives a reported self-consistency kappa with no rule |
| `volunteer_pass1.csv` appears after gate time | Hash it, report it; descriptive table only (FR §6.0). The design does not change |
| Gate recorded | `gate1.py` also gives the N2 check (→ `N2CHECK_RESULT.json`, recorded by the planning room), the headline rate, the LLM-annotator figures and the scorer-2 bar |
| `L1.csv` or `L2.csv` appears | Report it. Nothing reads it |

## 7. Guards built into the code

- Every script checks the parquet hash and writes its seed, input hashes and git-free
  script hash beside its output.
- Real-rank readers refuse to run without `GATE1_RESULT.json`.
- `g1_packets.py` and `g1_adjudication_sheet.py` cannot import score, rank or rating files
  (unit-tested).
- The crux extractor's input table has only question and opinion columns (unit-tested).
- Every Modal job logs an estimate to `ledger.csv` first and has `max_seconds` set from its cap.
  At $150 total, all Modal jobs stop and CPU-only work continues.

## 7a. Replan log

### R1 — 2026-11-15 (decisions.md D21). Changes in this file are marked [R1].

**Why.** Development probe: `E` varies within the round in 3 of 34 rounds (13 of 34 under A2e);
`SIDED` is 186 of 216 labels. A2 may have almost no identifying variation. Decided without
opening any ranking, rating or label.

**Decisions.**
1. **Primary confirmatory test: still A2 `beta_E`.** Nothing else is promoted. A2e would change
   the construct (omission, not hiding). N1 has the same identification and less of it. A
   between-round design adds no variation and adds confounds. A graded score would need invented
   weights. N2 cannot test what participants reward.
2. **Decision rule fixed in advance (FR §7.1).** `K_inf` = launches with an informative round;
   `MDE80` from 400 shuffled-rank fits. INFORMATIVE: `K_inf ≥ 100` and `MDE80 ≤ 0.10`.
   LOW-POWER: `K_inf ≥ 50`. NOT MEASURABLE: `K_inf < 50`. Written to `A2_TIER.json` before
   unblinding; one-way downgrade on the real standard error.
3. **"Not measurable" is pre-registered as the likely outcome** (FR §1), with its wording.
4. **N2 leads with prevalence when A2 is not INFORMATIVE** (FR §7.3). It keeps its own hashed
   spec and is never called the confirmatory test.
5. **Gate-1 additions (D18)** in FR §6.4a: accuracy on rounds with ≥ 1 crux, the show-vs-hide
   subset, a binding wording rule, human-labelled prevalence. Pass rule unchanged.
6. **Housekeeping:** `ADJ.csv` column is `adj_label` everywhere; the interval-method selection
   rule (D19) is in FR §7, method name pending.

**Changed in this file:** Stage B addition, Stage D branches, §8 items. Sections 1 to 7 are
otherwise as first written; §1 "Where things stand" is historical (see status.md for the
current state).

**To do, in order:** stats coder and scorer runner items in EXPERIMENTS "Replan log";
planning room copies the interval method name into FR §7 when ALIGNMENT.md records it;
planning room logs the A2 tier after the full scoring run.

### R2, R3 — no change to this file (decisions.md D25, D29): sequencing was unaffected.

### R4 — 2026-11-15 UTC, written 19:06Z to 19:25Z (decisions.md D31, D34, D36, D37). Changes in this file are marked [R4].

**Why.** Human-authored rule edits: D31 (19:06Z, six edits), D34 (19:10Z, supersedes D31 edit 1 and
adds the single-labeler design), D37 (19:16Z, optional hypothesis-blind volunteer), plus the
experiment council's model choices (D36). `labels\` was empty at every check; FR was not frozen.

**Decisions (each with its reason; full rules in FR, list in FR "Replan log" R4).**
1. **One human labeler, the author, hypothesis-aware; 50 items (38 originals + 12 N2), 20 repeated
   after at least one hour; self-consistency kappa ≥ 0.60.** Reason: human edit D34, replacing the
   two-labeler design and D31's 0.40 cut-off. Consequence: no blind human label unless the
   volunteer labels; the paper says "validated against a single hypothesis-aware human annotator".
2. **Volunteer switch.** `volunteer_pass1.csv` present at gate time → two-human design (kappa ≥ 0.40
   on 50, adjudication blind to scores). Reason: human edit D37. Gate time is the first poll at
   which the author's pass-1 file is complete, so the design cannot be picked later.
3. **PROVISIONAL state.** In the single-labeler design A2 and Tier 2 may start on the pass-1 labels;
   everything is stamped PROVISIONAL until the self-consistency step is recorded. Reason: D34
   process. N2 scoring still waits for the final PASS (N2 spec, D36).
4. **N2 check on 12 packet items**, pooled, one-sided Fisher exact p ≤ 0.05 → `N2_VALIDATED`, else
   `EXPLORATORY`. Reason: human edit D31.2 / D34.3. Stated in advance: low power.
5. **Second scorer = granite-4.2-30b** with a bar before use; LLM annotator = gpt-oss-120b,
   supplementary. Reason: D31.3 / D34.4, .5; council D36.
6. **Headline = human-labelled hide-rate on the 38 originals, Wilson interval.** Reason: D31.4.
7. **N2 on five generators, split by generator, length controlled.** Reason: D31.5; council D36.
8. **Development launches out of every confirmatory and family test; all-launch A2 = sensitivity.**
   Reason: D31.6 / D34.8; before R4, FR §2 made the all-launch fit primary.

**Sequencing after R4.**
- Stage A (before any label): extended N2 generation → `n2_items.json` → new packets, volunteer
  packet, `SHARE.md` → Opus leak check (now also: no model, condition or item kind visible; N2 rows
  laid out like originals) → scorer-2 development smoke (V1), LLM-annotator manifest and format
  try-out → code changes of EXPERIMENTS "R4" list tested on dummy data → A2 tier re-run on the
  confirmatory set and logged by the planning room. Only then does status.md tell the human the
  packets are ready. The 44-row packets announced earlier are void.
- Stage C (labels): §6 [R4] table.
- Stage D: as before, with the confirmatory set; in the single-labeler design the first results are
  PROVISIONAL; N2 scoring after the final PASS; N2 leads only if `N2_VALIDATED`. The drafter keeps
  skeletons for: single-labeler or two-human wording; N2 validated or exploratory; A2 tier.
- The planning room meets at: gate time (records the design and the provisional or final status),
  pass-2 arrival, and N2-check recording.

**Stale in this file.** §1, §2 "Label poller" row (file names), §3 Stage A steps 5 to 7 and Stage C,
the §6 table before its [R4] note, and "44 rows per labeler" in §8 describe the older design.

## 8. Open items for the human (none blocks the pipeline)

- **[R4]** To use the two-human design, save `labels\volunteer_pass1.csv` before or together with
  your completed `labels\author_pass1.csv`. A volunteer file saved later is reported but does not
  change the design. Either file, whichever is first, freezes FROZEN_RULES.md.
- **[R4]** Do pass 2 at least one hour after saving pass 1, write the start time in UTC, and do not
  read any provisional result before pass 2 is saved; the pipeline records whether results existed
  by then and the paper prints it.
- **[R4]** Labelling load: 50 rows, then 20 rows; each with a full set of opinions.
- **[R4]** Expect a real chance of a self-consistency FAIL even with careful labelling (about one
  in three to two in three, FR §6.1b), and expect the 12-item N2 check to miss more often than not
  unless the scorer is right on about nine N2 items in ten (FR §6.6). Twenty-four N2 items would
  about double that check's power; the number is yours to change before the first label file.
- **[R4]** `N2_VALIDATED` is restricted to scorer-1 estimates without development-launch rounds
  (planning-room choice e in FR R4); reverse it before freeze if you disagree.

- **[R1]** FR §7.1 thresholds (100 launches, MDE 0.10) are judgement calls. Edit them before
  the first label file if you disagree; they are not moved afterwards.
- **[R1]** Optional: a blind supplement of AI-"shown" statements would validate the contrast
  A2 rests on (methodologist F2). It needs extra labelling and an edit to FR §5 and §6.1 by you;
  the pipeline does not add it (BRIEF §3.1).
- **[R1]** Expect the "rank question not measurable; prevalence and N2 lead" paper as the more
  likely outcome.

- Read and, if wanted, edit FROZEN_RULES.md before the first label file is saved.
- Its "Known weaknesses" section lists five choices worth a second look, especially the
  decision to count one-sided statements as hiding.
- Labeling load: 44 rows per labeler, each with a full set of opinions to read.
