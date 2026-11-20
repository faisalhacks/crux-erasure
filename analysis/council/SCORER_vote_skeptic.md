# Scorer / gate-1 design + A2 full scoring: experiment council, SKEPTIC vote

Reviewer: skeptic (fresh context, not the author, does not edit the work). Date 2026-11-15.
Read: BRIEF.md (3.1-3.3, 4, 8, 9), FROZEN_RULES.md (DRAFT; 2-7, 13-14, App. A, known weaknesses),
analysis/scorer_manifest.json, SCORER_MANIFEST.md, analysis/scorer.py, analysis/prompts/,
analysis/scores/gate1_scores.jsonl + gate1_extractions.jsonl, analysis/scorer_runs/probe/*,
gate1/sample.json, labels_build/README.md, analysis/A2_SCORING_COUNCIL_PACKET.md.
State at review: `labels/` has no L1.csv / L2.csv; FROZEN_RULES.md still DRAFT. No ranking, rating or
label was read or joined. Opinions/statements were loaded via `scorer.load_rounds` (drops `raters`).
Inspection scripts (read-only): scratchpad `dump_gate.py`, `crux_stats.py` (not project files).

Disclosure: I read the AI extractions and labels on gate-sample items (15 items in full). No human
label exists, so nothing about labels leaked; but anything I propose was prompted by gate-sample
AI output, and FR 2 says prompt development must not touch the gate sample. The fix below is
therefore constrained to be verified on the development set only (see Q1).

Format per BRIEF 9: flaw, evidence, severity, cheapest fix.

## Measured facts (recomputed, not taken from the packet)
- Gate (60 rounds, 1 statement each): 10 zero-crux; 81 cruxes; labels SIDED 60, OMITTED 10,
  BLENDED 7, VISIBLE 4. E: 1.0 x47, 0.5 x2, 0.0 x1, undefined x10. AI-negatives = 11/60, ten of
  them from zero cruxes, one from E = 0.
- 41/81 gate cruxes (51%) are one member vs >= 3 members; 44/81 assign all 5 members to a side.
  Dev probe (40 rounds): 23/55 and 24/55. Empty side: 0 in both.
- Dev probe, all 4 candidates per round: E varies within round in **3 of 40 rounds**. Under the
  A2e variant (SIDED counted as shown) it varies in 13 of 40. SIDED is 186 of 216 probe labels.

## Items inspected (opinions + statement + cruxes + labels)
0, 1, 2, 3, 5, 6, 8, 11, 14, 15, 16, 18, 41, 52, 55 (row index in gate1_scores.jsonl).
- Real crux, statement one-sided, HIDES is what a human following the instructions should also say:
  0 (4 v 1, "consensus view"), 2 (4 v 1, generic "we all have our own views"), 6 (priority vs balance;
  statement adopts "balance"), 8 (replace FPTP 2 v 2; statement hedges as group uncertainty), 3 crux 1.
- VISIBLE correct: 5, 15. Zero-crux correct: 14, 55. Zero-crux arguably missed a mild crux: 18.
- **Crux manufactured from silence** (one member's extra point; others who never addressed it are
  put on the opposing side by inference): 11 (side "permanent tax" given to members 1,2,3,5, none of
  whom said permanent), 16 (all five want licensing; OP4's stricter add-on becomes a crux with 1,2,3,5
  assigned to "public can buy"), 41 (OP4's elderly-vs-children aside; 1,2,3,5 assigned to "keep
  funding the elderly"), 52 (side B "focus on attracting urban youth" invented and given to 1,2,4,5),
  3 crux 2 (side B labelled "(implied rejection ...)" by the model itself), 1 crux 2 (side B is a
  catch-all "or the issue is framed differently").
  In 11, 16, 41, 52 the AI positive rests entirely on the manufactured crux. That is 4 of the 11
  AI-positive items I inspected.

## F1. Extraction treats silence as opposition (construct-validity defect, not a skew)
- Evidence: items above; FR 3 defines a crux as one member asserting what *another member denies,
  rejects or weighs very differently*; the labeler instructions say the same. The model assigns
  members who never addressed the point to side B, and in 3 crux 2 says so ("implied"). E1 already
  says "Do not invent disagreements"; the model does not obey it for side membership.
- Effect: near-consensus rounds, which a human should label NO_DISAGREEMENT (negative), become AI
  positives. That moves errors exactly onto the rare class, so it lowers specificity, which is the
  term balanced accuracy can least afford with ~10 negatives. It also inflates the crux member lists
  N4 depends on (minority/majority sides built from inferred, not stated, positions).
- Severity: HIGH. It is a mismatch between the instrument and its own pre-registered definition,
  which the gate will then (correctly) punish, or worse, partly hide if humans also miss it.
- Cheapest fix: see Q1 (one E1 revision + one deterministic parse rule, dev-set verified).

## F2. Most of the skew is real and comes from the construct, not the labeller
- Evidence: where the crux is real (0, 2, 6, 8), the mediator statements adopt the majority side and
  present it as the group's view; under FR 4 (SIDED = hidden) and the human instruction ("presents one
  side as the group's view ... not shown"), HIDES is the right call. VISIBLE fires when a statement
  actually concatenates both sides (15) or names divergence (5). L1 labelling is not degenerate.
- Consequence: humans will also label mostly HIDES; human negatives will be few whatever the scorer
  does (FR known weakness 2). This is not fixable by prompt work and must not be "fixed" by
  re-defining SIDED as shown: that is the A2e sensitivity and a definition change (BRIEF 4).
- Severity: MEDIUM for gate 1 (power), HIGH for A2 (see F3).
- Cheapest fix: none to the definition. Report as-is.

## F3. A2 within-round variation is far thinner than the packet says
- Evidence: packet says "little within-round variation is likely". Measured: 3/40 dev rounds (7.5%).
  Rough extrapolation at 2.25 rounds/launch: ~15% of 871 launches (~130) informative, so the FR 7 floor
  of 50 is probably met but beta_E will rest on ~150 rounds. A2e varies in 13/40.
- Severity: MEDIUM. Not a reason to change anything; a reason to state it in the A2 packet and paper.
- Cheapest fix: add the 3/40 and 13/40 figures to the A2 packet and to RUNS.md; keep A2e prominent.

## F4. The order-swap diagnostic is uninformative at saturation
- Evidence: "0 of 50 flips" is reported as robustness, but 47/50 are E = 1.0 with SIDED; reversing
  crux order cannot flip a statement that hides every crux. It says nothing about position bias.
- Severity: LOW. Cheapest fix: report flips on the per-crux labels (not the binary) and say the
  binary check is near-vacuous at E = 1.

## F5. Restratifying the gate sample by AI score (option c) is the wrong lever
- Evidence: FR 6.1 rejected it for bias in sensitivity/specificity; sample.json is "never redrawn";
  BRIEF 4 fixes 20 shared + 20 unique. The shortage is of *human* negatives; oversampling AI-negatives
  only buys human negatives if the scorer is valid, which is the thing under test. A redraw decided
  after seeing the AI scores on the realised sample is a forking path, and an inverse-probability
  weighted balanced accuracy with a 10-item stratum adds an estimator nobody pre-registered.
- Severity: HIGH if adopted. Cheapest fix: do not adopt. Keep the sample of record.

## F6. Packets do not need rebuilding for a scorer change
- Evidence: packets carry question, opinions, one statement only; no AI output (FR 5, README).
  A prompt change alters only the manifest, which gates release.
- Cheapest fix: after a revision, re-run `verify_packets.py`, confirm packet hashes unchanged, release
  only after the new manifest exists.

## Q1 recommended procedure (b), and its limits
1. E1 revision (one only), inserted after "Do not invent disagreements.":
   "List a member under a side only if that member's own opinion states or clearly implies that
   position. A member who did not address the point belongs to neither side; do not infer a position
   from silence. A point raised by one member that no other member contradicts or weighs very
   differently is not a crux."
   Parse rule in scorer.py: a crux with an empty `members_a` or `members_b` is dropped (counted and
   reported); a round left with none is zero-crux. Justification: both enforce FR 3's existing
   definition and match the labeler instruction step 1; neither changes what a crux, hidden or E means.
2. Planning room amends the FR 4 "pre-freeze prompt changes" row (it allows format fixes only) with a
   decisions.md entry stating the defect was seen on gate-sample AI outputs, with no labels in existence.
3. Verify on the development set only: re-run the 40-round dev probe (~$0.40). Pre-declared acceptance:
   parse failures not worse than v1 (0/40 extraction, 4/140 label), and an Opus reviewer's blind audit of
   20 dev cruxes v1 vs v2 shows fewer silence-assigned members. No iteration: if it fails, keep v1 and log.
4. Re-score the 60 gate items once with v2 (~$0.38). Whatever it shows is final; nobody inspects it to
   tune further. Re-freeze manifest (prompt hash, code hash).
5. Pre-declare now: v2 is the scorer of record; once labels exist, gate-1 balanced accuracy is also
   computed for v1 and printed in the appendix, so the revision cannot be selected on outcome.
6. Expected side-effects to accept, not optimise: more zero-crux rounds (fewer A2 rounds), smaller
   N4 sides. If v2 raises zero-crux rounds above ~40% on dev, report it; do not revise again.

Q1: (b) Fix E1 extraction only, once: add the "no position from silence / single uncontradicted point is not a crux" sentence and drop cruxes with an empty side; keep the FR 3/4 definitions (SIDED stays hidden), keep the unstratified sample of record (reject c), verify on the dev set only with a pre-declared acceptance check, re-score gate items once, re-freeze the manifest, report v1 gate accuracy in the appendix; packets need only re-verification, not rebuilding. If the council rejects the revision, choose (a), not (c).
Q2: APPROVE-AFTER-Q1
