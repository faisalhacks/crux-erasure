# Crux erasure: do participants reward hidden disagreement?

Code, pre-registration, outputs and report for "Do Participants Reward Hidden Disagreement? Testing Whether Rankings of AI-Mediated Group Statements Favour Crux Erasure" (Mohammed Faisal Parvez; AI x Epistemics Research Sprint, Apart Research, November 2026).

- Paper: `report/SUBMIT/T3-1_crux_erasure.pdf`; slides `report/SUBMIT/T3-1_crux_erasure_slides.pptx`.
- Pre-registration: `FROZEN_RULES.md` (frozen 2026-11-16T01:53:53Z; `gate1/FREEZE.json`). Every decision: `decisions.md`. Spend: `ledger.csv`.
- Gate (step 2, participant presence check): `analysis/step2_reference.py`, `analysis/gate1_r5.py` -> `gate1/`.
- Primary test A2: `analysis/a2_within_round.py`; Tier 2: `n1_winner_vs_mean.py`, `n4_minority.py`; results `analysis/results/RESULTS_MAIN.md`.
- N2 (exploratory prompt grid): `analysis/n2_grid.py`, `n2_score.py`, `n2_analysis.py` -> `analysis/n2_results/`.
- Scorer serving (Modal): `serving/`. Scores: `analysis/scores/`.
- Verification packet: `labels_build/v5/`; partial post-gate author check (12/25): `labels/author_verification_partial12.csv`, `analysis/verification_partial12.py`.
- Figures: `figures/make_real_figures.py` -> `figures/real_out/`. Report build: `report/build/build.py --real`.

Data: Habermas Machine release (Google DeepMind, CC-BY 4.0), not redistributed here; download it from the original release. No model was fine-tuned.
Most code and text were drafted by AI agents (Claude) under human direction; see the LLM Usage Statement in the paper.
