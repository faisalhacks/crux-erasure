# N2 experiment council: SKEPTIC vote

Reviewer: skeptic (fresh context, not the author, does not edit the work). Date 2026-11-15.
Read: BRIEF.md (5, 8, 9), analysis/N2_COUNCIL_PACKET.md, analysis/n2_grid.py, decisions.md (D4),
analysis/novelty_claims.md (Mahajan entry, E1), FROZEN_RULES.md (2-4, 7, 9), ledger.csv,
analysis/n2_runs/*/plan.json.
State at review: labels/ is empty, analysis/scorer_manifest.json does not exist, FROZEN_RULES.md is
still marked DRAFT. Scorer is not frozen, gate 1 has not run. plan_default and full plan.json both
carry plan_sha256 a27be1f49e25a00d25759e3bf9d9085fafb2805201674111af17276fc12d5e46, worst case $6.259.

Format per BRIEF 9: flaw, evidence, severity, cheapest fix.

## F1. The generators are the scorers (self-scoring)
- Evidence: N2 generators are `gemma4-12b` and `qwen3.8-27b` (n2_grid.py DEFAULT_MODELS). FROZEN_RULES 4:
  scorer 1 = `qwen3.8-27b`, scorer 2 = `gemma4-12b`. Every N2 statement will be labelled by the same
  model that wrote it (scorer 1 on qwen outputs) or by the one other model in the study. A model that
  writes "accurate about differences" text in its own idiom is plausibly more likely to label its own
  phrasing VISIBLE. That inflates the SAT/ACC and COMMON/DIS contrasts for qwen under scorer 1, and
  the packet does not mention it.
- Severity: HIGH for interpretation (no cost impact; it is an analysis-plan defect).
- Cheapest fix ($0): pre-specify the full 2x2 generator x scorer matrix, with CROSS-scored cells
  (qwen outputs by scorer 2, gemma outputs by scorer 1) as the primary N2 read and self-scored cells
  reported beside them. Report the generator x scorer interaction. Any contrast that holds only
  under self-scoring is reported as such.

## F2. The main effects are close to manipulation checks; what is new over Mahajan is narrower than claimed
- Evidence: Mahajan et al. 2611.05135 (novelty_claims.md line 39) already report "prompts seeking
  agreement covered minority positions much less often than prompts asking to describe differences".
  The N2 user factor (COMMON vs DIS) is that contrast again. The system factor ACC literally says
  "accurate about the differences". A model that follows instructions will show both main effects;
  finding them is a check that the manipulation worked, not a result. Packet 2 lists four additions;
  (3) matched material and (4) open weights are context, not findings. (2) "validated scorer" holds
  only if gate 1 passes AND F3 is addressed.
- What N2 adds that Mahajan does not: (a) the INTERACTION and the off-diagonal cells: does a SAT
  system prompt keep hiding cruxes even when the user asks to see disagreement (SAT-DIS vs ACC-DIS),
  and does ACC protect them under a COMMON user request (ACC-COMMON vs SAT-COMMON)? That is the
  "system operator vs user" question and it is the actual contribution. (b) Placement on the same
  rounds as the human-ranked candidates.
- Missing: a default/neutral cell. With no neutral baseline N2 cannot say what today's models do
  unprompted, so "a satisfaction-seeking instruction produces hiding statements" (packet 1) cannot
  be separated from "every condition hides and ACC/DIS hide less".
- Severity: MEDIUM-HIGH (claim wording and novelty).
- Cheapest fix ($0): (i) name the off-diagonal system-prompt contrasts (SAT-ACC within DIS; SAT-ACC
  within COMMON) and the interaction as the N2 contrasts of interest, and call the main effects
  manipulation checks; (ii) use the round's existing iteration-0 Habermas Machine candidates, which
  A2 scores anyway, as the free baseline (same rounds, same cruxes). Paid alternative: add a fifth
  neutral cell (+25% gens, worst case about $7.8, under the $10 N2 cap but above the $6.50 ceiling,
  so it would need a new vote). I do not require the paid option.

## F3. Scorer validity does not transfer to N2 text by default
- Evidence: gate 1 validates scorer 1 on iteration-0 HM candidates (FROZEN_RULES 2, 6) with a binary
  threshold E >= 0.5 and a balanced-accuracy lower bound > 0.5. N2's DIS/ACC outputs will be a
  different genre ("Some participants hold X, while others hold Y"). A pass on HM text, at a lower
  bound just above chance, does not certify the continuous E contrasts on that genre. Packet 2(2)
  says the outcome is "validated against blind human labels"; that overstates it for N2.
- Severity: MEDIUM.
- Cheapest fix ($0): in the paper, say "scorer validated on Habermas Machine candidates; its
  validity on N2 outputs is assumed, not tested". Report per-cell parse-failure and zero-crux rates
  and the E distribution per cell (ceiling/floor). Do not add N2 text to the gate-1 packets
  (FROZEN_RULES is about to freeze and the label instrument must not change for N2).

## F4. Generate now, score later: allowed, but the order must be locked
- Evidence: hard rule 3 restricts the MAIN analysis on real data before gate 1. N2 generation reads
  no rankings or labels (n2_grid.py docstring, build_messages uses only question and opinions), so
  generating now does not breach it. But the scorer is NOT frozen (no scorer_manifest.json, FROZEN_RULES
  DRAFT, pre-freeze prompt changes still allowed per FROZEN_RULES 4). If anyone reads N2 outputs
  while the scorer prompts can still change, scorer development is contaminated by N2.
  Also, the N2 analysis plan (contrasts, alpha/Bonferroni choice, zero-crux handling, length
  handling, k-averaging) lives only in the packet; FROZEN_RULES 9 lists N2 as exploratory with no spec.
- Severity: MEDIUM (process; cheap to fix, expensive to undo).
- Cheapest fix ($0): generation may run now. No N2 output is scored, and none is read beyond
  automated format counters, until (a) scorer_manifest.json exists and (b) GATE1_RESULT.json records
  PASS. Before generation, write a hashed N2 analysis spec (the contrasts in F2, F1 cross-scoring,
  alpha rule: pick Bonferroni over 2 models x 3 contrasts or state "uncorrected, exploratory"; one,
  not both), and record its hash in decisions.md. N2 outputs are never used for scorer prompt
  development. If gate 1 fails or is NOT EVALUATED, the outputs stay unscored and the paper says so.

## F5. Confounds in the 4 prompts: length, refusal, meta-text, thinking leakage
- Evidence: the 150-word cap (USER_FORMAT) is identical across cells, but it is a ceiling, not a
  match. DIS/ACC statements must list positions and will likely run longer; E is the share of cruxes
  shown, and longer text can show more. Length is plausibly a mediator here, but the packet has no
  length reporting rule. Refusal or meta-text ("As a mediator, I cannot take sides...", "Here is the
  statement:") is not detected; such outputs would be labelled OMITTED, which inflates E in whichever
  cell provokes them (likely SAT-DIS, the conflicting cell). `enable_thinking: False` is sent, but
  FROZEN_RULES 4 says the thinking switch is unverified; a leaked think block would be scored as
  statement text. The only smoke output check is truncation/empty > 10%.
- Severity: MEDIUM.
- Cheapest fix ($0): extend the smoke and full-run format check to count per cell: n_words
  (already logged), think-tag presence, refusal/meta-text (fixed regex list written before the run),
  and preamble. Pre-specify: such outputs are kept, flagged, and the N2 contrasts are reported with
  and without them; a cell with > 10% flagged outputs in the smoke means fix and re-smoke. Report
  length per cell and a length-adjusted contrast (log words, as FROZEN_RULES 7) as secondary,
  labelled as a possible mediator, not a confound to remove.

## F6. n and power are stated for the wrong effects and an unknown usable n
- Evidence: the power table (packet 3) uses one d_z for all three contrasts. Interaction effects
  are typically smaller than main effects; the contrasts that carry the novelty (F2) are the
  weakest-powered. The table also assumes all 250 rounds are usable, but FROZEN_RULES 3 drops
  zero-crux rounds and rounds with a missing E; the zero-crux rate is unknown (no figure found in the
  pilot outputs). At 200 usable rounds power at d_z=0.20 falls to 0.80 uncorrected.
- Severity: LOW-MEDIUM. Generation cost is linear and modest; 250 rounds is defensible.
- Cheapest fix ($0): state the minimum detectable d_z for the interaction and for the off-diagonal
  contrasts separately, recompute the table at the observed usable n after scoring, and keep the
  packet's "null = no effect larger than about X SD" wording. No change to n.

## F7. Two models: enough for an exploratory 2x2, not for "current models"
- Evidence: two open models (12B, 27B), both also the scorers (F1). Neither is the class of model
  actually deployed as mediators. Packet 1 says "today's models".
- Severity: MEDIUM for wording, LOW for running.
- Cheapest fix ($0): claim scope "two open-weight models", model as a replication factor; report each
  model separately; drop "today's models". A third, non-scorer family would also ease F1, but that
  is a new plan and new vote; not required here.

## F8. The approval hash will not match the re-planned launch
- Evidence: make_plan puts `assumptions.tok_per_s_overrides` inside `core`, so plan_sha256 changes the
  moment the runner re-plans with `--tok-per-s` from the smoke (packet 4, step 2). check_gates then
  refuses because the approval's plan_sha256 is a27be1f4... Either the launch is refused, or someone
  writes a fresh approval file without a council vote.
- Severity: MEDIUM (process: it invites an unapproved approval file).
- Cheapest fix ($0): the approval covers ONLY plan_sha256 a27be1f4...5e46 (default assumptions,
  worst case $6.259). Launch that plan unchanged if the smoke's measured tok/s is at or above the
  assumed 450/400; the session timeout already bounds spend. If measured throughput is lower, or any
  prompt, model, n, k, seed or temperature changes after the smoke, the approval is void and the
  council votes again. No one but the council writes the approval file.

## F9. Stop conditions: operational, not scientific, which is acceptable here with one gap
- Evidence: packet 5 stops on budget, timeout, error rate, truncation; it explicitly excludes effect
  size, which is correct (no stopping on the result). It sets aside "pilot shows no signal"; with a
  4-round, k=1 smoke there is no signal to read anyway, so that is honest. Gap: no stop on a dead
  manipulation, e.g. smoke outputs that are near-identical across all 4 cells (prompt ignored).
- Severity: LOW.
- Cheapest fix ($0): add a smoke check that is pre-specified and outcome-blind: if the 4 cells
  of a round are near-duplicates (e.g. mean pairwise word-overlap above a threshold set now) in most
  smoke rounds, stop and return to the council. This uses text form only, no scorer.

## Cost check
Expected $3.27, worst case $6.26 at list price; ledger shows $0.65 spent to date (infra), none on N2.
Within the $10 N2 cap (BRIEF 11). Session timeouts are set (2x expected wall). Cost is not the problem.

## Council criteria (BRIEF 8)
- Claim supported: only in the narrowed form of F2 and after F1/F4 conditions. As written, the main
  effects are manipulation checks and largely replicate Mahajan.
- Prior-work check: done (D4, novelty_claims.md), but Mahajan was read via scout notes; the citation
  verifier must open it before the paper relies on the delta.
- Cost: adequate, bounded, logged before launch.
- Stop condition: adequate operationally; F8 and F9 gaps fixable at $0.

VOTE: APPROVE-WITH-CONDITIONS: (1) approval binds plan_sha256 a27be1f49e25a00d25759e3bf9d9085fafb2805201674111af17276fc12d5e46 at max_usd 6.50 only; any re-plan (tok/s override, prompt, model, n, k, seed) voids it and returns to council; (2) before generation, a hashed N2 analysis spec is logged in decisions.md naming the off-diagonal system-prompt contrasts and the interaction as the contrasts of interest, main effects as manipulation checks, cross-scored cells as primary, one alpha rule, zero-crux and length handling, and the HM iteration-0 candidates as the $0 baseline; (3) generation may run now, but no N2 output is scored or read beyond automated format counters until scorer_manifest.json exists and GATE1_RESULT.json records PASS, and N2 outputs are never used in scorer development; (4) the smoke and full-run format checks count per cell think-tag leakage, refusal/meta-text, preamble and near-duplicate cells, with thresholds written before the smoke; (5) claim scope is "two open-weight models", Mahajan's agreement-vs-differences finding is credited for the main effects, and scorer validity on N2 text is stated as untested.
