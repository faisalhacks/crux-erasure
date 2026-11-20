# SCORER_MANIFEST.md (human-readable; machine copy: analysis/scorer_manifest.json)

Status: DRAFT until the human/planning room freezes with FROZEN_RULES.md. Written 2026-11-15 by the scorer runner.

| Item | Value |
|---|---|
| Scorer 1 | `Qwen/Qwen3.8-27B`, revision `37561816e66b5b9153b1b64c10968c18c1e6f4a0`, alias `qwen3.8-27b`, vLLM v0.32.0 image, max-model-len 16384, H100 |
| Scorer 2 (A4, not run) | `google/gemma-4-12B-it`, revision `43c9d014b231474fa7212dbb48a762566c2b255d`, alias `gemma4-12b` |
| Prompts (byte-identical to FROZEN_RULES Appendix A, verified by `scorer.py prompts`) | E1 sha256 `65450760176c7ad4e79c9329664c2074f08df5c23db6098613c580b77228c0aa`; L1 `8799f803b571b4e584779b54f170c2f305cab5cddc10721ba47988aeda2e350e`; C1 `cea226abba1285912e76825327ed2d80449705381b46c4d5d0e4f369d737a3d1` |
| Decoding | temperature 0, seed 0 (retry seed 1 on any failure), max_tokens 700 (extract) / 300 (label), `response_format={type: json_object}`, `chat_template_kwargs.enable_thinking=False` |
| Thinking off | Requested. Not independently verified: the probe saw no truncation, `<think>` leakage was not checked in text beyond JSON parsing succeeding (97%+ of calls parsed). Recorded, not assumed. |
| Code | `analysis/scorer.py` (sha256 in the JSON). Inputs read: question, opinions, candidates only; `raters` dropped at load. |
| Dev-set probe (pilot_groups, 40 rounds, 184 calls, seed 20261126) | 0 extraction parse failures; 4 of 140 label calls failed after retry (model returned 2 labels for 1 crux); 0 truncations; 5 of 40 rounds zero cruxes; session $0.398 list price, 164.5 s wall incl. 109 s cold start. Prompts NOT changed. |
| Gate-1 scoring (60 statements, key.json sample) | 60 extraction + 50 label + 50 order-swapped label calls; 0 parse failures; 10 statements in zero-crux rounds; 49 of 50 scored statements have E >= 0.5; order-swap flipped the binary call on 0 of 50; session $0.383, 166.5 s. File `analysis/scores/gate1_scores.jsonl` (+ `gate1_extractions.jsonl`). Never shown to labelers, never joined to rankings. |
| Caveat | Nearly every scored statement is "hiding" under this definition (mean E 0.96). Gate-1 negatives will be few, so balanced accuracy may have a wide interval (FROZEN_RULES known weakness 1 and 2). Reported, not tuned. |
| Spend | Probe $0.398 + gate-1 $0.383 = $0.78 (ledger.csv cumulative $1.613 incl. earlier infra). `modal container list` checked empty after both (one stale row was stopped by container id). |
