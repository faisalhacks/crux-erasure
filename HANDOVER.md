# HANDOVER: T3-1 crux erasure (BRIEF §13). Written 2026-11-16T03:02Z by the orchestrator

Deadline: 2026-11-16 11:59 UTC. Nothing was submitted, published, pushed or emailed. **Submitting is yours.**

## 1. Paper: ready to paste
- Draft PDF (layout and length check only): `report\build\out\DRAFT_layout.pdf`. Body 8 pages (cap 8, about 1 line spare); 17 pages in total.
- Paste source: `report\build\out\DRAFT_combined.md`. Paste it into your copy of the Apart Google Doc template (link in `skills\layout_apart_template.md`); fonts and margins in the trial build are assumptions.
- Figures: `figures\real_out\*.png` (script `figures\make_real_figures.py`).
- Number-to-source map: `report\DRAFT_STATUS.md`. References: `report\refs.bib`, `report\references_verified.md`.
- **Slots only you can fill:** author names and affiliations; the code/repository link; whether to release the scorer prompts and serving config; and whether you read the final text (editor edit 15). Then grep for `SLOT`: nothing else should remain once N3 is settled (section 4).

## 2. Gate and validation (FROZEN_RULES §6.R5; decisions D49–D55)
- Status of record: **VALIDATED_PRESENCE** (`gate1\GATE1_RESULT.json`), independently re-derived (`analysis\review\GATE_REVIEW.md`).
- Step 2, the participant presence check (`analysis\step2_reference.py` -> `gate1\STEP2_computed__20261116T015355Z.json`): BA2 0.692, launch 95% [0.669, 0.714]; sensitivity 0.900, specificity 0.484; PASS. Valid only for whether a group disagrees, not for whether a statement hides it.
- Step 3, the author's verification: **NOT DONE** (no file by T_cut 01:53Z; D51/D53). No human label exists. A file saved now is reported only as a labelled post-gate check, not a gate input.
- Panel (supplementary, not human): `analysis\panel\`. Panel vs scorer κ = 0.00 [−0.39, 0.37], n = 21 (`analysis\panel_vs_scorer.py`). Other LLMs do not corroborate the scorer's hide/show calls.

## 3. Results (all in `analysis\results\RESULTS_MAIN.md` and `analysis\n2_results\N2_RESULTS.md`)
- A2 primary (`analysis\a2_within_round.py`): beta_E +0.051 [+0.008, +0.095], p = 0.024, 1,166 rounds / 642 launches. "Pre-registered test; the predictor's hide/show contrast is not human-validated." Sensitive to how length is controlled: the sign flips without the length control, and 5 of 6 flexible length adjustments fall below |t| 1.96 (red team; `analysis\redteam\`).
- N1 +0.008 [−0.002, +0.019]; N4 −0.147 [−0.252, −0.041]. Holm of record (N3 counted at p = 1): N1 0.231, N4 0.023. `RESULTS_MAIN.md` final sha 5a0653b4….
- N2 (EXPLORATORY; `analysis\n2_analysis.py`): a satisfaction-optimising system prompt raises scored hiding in all 5 models (system effect 0.28–0.37); asking for differences mostly but not fully overrides it (C1 +0.03 Qwen to +0.43 Llama).
- Prevalence (scorer-based): 96.1% of statements hide every crux, mostly by stating one side (82.8% of crux labels SIDED).

## 4. Unfinished / failed
- **N3** (pre-registered Tier 2): **NOT RUN (infrastructure), final (D61).** The Modal scorer app never started a container in 4 attempts (503, $0). The 04:00Z retry never ran because the runner agent died from a network error, and the 06:00Z cut-off passed. The paper says so in Results; the conservative Holm is the one of record.
- The 15-min label watcher was stopped by Claude Code for low system memory (not restarted). `labels\` was empty at 07:49Z.
- A2c, A3, A4: not run (no second scorer passed the bar; A3 had 0 qualifying launches).
- Not done by design (D50): the survey and critique analyses; panel task P2.
- Process deviations (Appendix A item 13): the per-status frames were not written before the gate; the sealed pilot file was read by the shuffled-data test mode (D58.6); a counting defect in a2_informativeness.py (150/142 corrected).

## 5. Layout defects remaining
- Rebuilt 07:5xZ with the final N3 text: body 8 of 8 pages, 17 in total; no stamps or file paths in the PDF (`checks.json`). No N3 slot left; the only slots left are yours (section 1).
- Google Doc fonts and margins are not reproduced; re-check page count and figure legibility after pasting.

## 6. Spend and state
- Modal: $15.28 of $200 (`ledger.csv`). No container of ours is known to be running. An old idle qwen container (`ta-01M7G7WHWRPZAMKJA95T9T9BBR`) may still exist; my stop was blocked, so please run `modal container stop --yes ta-01M7G7WHWRPZAMKJA95T9T9BBR` if `modal container list` shows it.
- Every decision: `decisions.md` D0–D60. Every run: `analysis\RUNS.md`. Rules: `FROZEN_RULES.md` (frozen 01:53:53Z).
- Owed from earlier (NEEDS-HUMAN): the past-entry name typo ("Parez" vs "Parvez"), and the Secret Loyalties correction.
