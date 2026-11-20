# N2 results — EXPLORATORY (gate tag HIDE_NOT_HUMAN_VALIDATED)

Generated 2026-11-16T02:24:26Z by `analysis/n2_analysis.py` (sha256 `85a5b81666cdcd3ad4c3cdceace53caf2bb41bbaccbe0202020897e6812efc68`). Spec of record: `analysis/N2_ANALYSIS_SPEC.md` sha256 `afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0` (Amendments 1–5). Scores: `analysis\scores\n2_scores_v2.jsonl` sha256 `84498639a841a5683004332c4db7eee7a62ea36baaa98ea1acda2f4d75510615`.

**Status and wording (binding).**

- EXPLORATORY (FROZEN_RULES 6.R5.7; N2 spec Amendment 5). Gate tag HIDE_NOT_HUMAN_VALIDATED.
- R5 status VALIDATED_PRESENCE: the scorer is validated for detecting whether a disagreement is present, not for detecting whether a statement hides it; the hiding measure E is not human-validated. Step-2 scope: the scorer's detection of disagreement was validated against participants' own pre-deliberation position ratings, for whether a group disagrees, not for whether a statement hides it.
- the scorer's hide/show call was checked on 6 N2 statements only (descriptive); not checked on newly generated text beyond 6 items
- five open-weight instruction-tuned models (8B-27B); statements are not ranked by humans: N2 says what models write, not what people reward
- qwen3.8-27b text is scored by qwen3.8-27b (self-scored) everywhere
- A4 = none (Amendment 4): no A4 robustness read, no generator x scorer interaction, no A4 agreement / zero-crux tables
- a CI that includes 0 is reported as 'CI includes 0; MDE (d_z, 80% power) at the effective n = ...', never as 'no effect' (the spec's 'not detected' is replaced because FR 6.R5.6 bars 'detected' for E-based results under VALIDATED_PRESENCE)
- between-generator differences in the level of E are descriptive only and never attributed to family, size or release date

Every number below is EXPLORATORY. Intervals: launch-cluster percentile bootstrap, B = 2000, seed 20261115 (spec §4), unless marked model-based. `p_boot` = FR §7 bootstrap p; `p_holm` = Holm within family (family 1 = gemma4-12b, qwen3.8-27b, 10 tests; family 2 = ministral3-14b, phi4-14b, llama3.1-8b, 15 tests). Adjusted = log(words) centred within generator, plus preamble where the generator has any preambled statement (Amendments 1, 3); unadjusted and adjusted are both reported, neither preferred.

## 1. Scoring counts and parse failures (scorer 1 = qwen3.8-27b, frozen v2)

| generator | statements | with E | extraction fail | label parse fail | parse-failure rate | zero-crux | empty text |
|---|---|---|---|---|---|---|---|
| gemma4-12b | 1250 | 890 | 5 | 10 | 0.0120 | 345 | 0 |
| qwen3.8-27b (self-scored) | 1250 | 895 | 5 | 5 | 0.0080 | 345 | 0 |
| ministral3-14b | 1250 | 886 | 5 | 14 | 0.0152 | 345 | 0 |
| phi4-14b | 1250 | 894 | 5 | 6 | 0.0088 | 345 | 0 |
| llama3.1-8b | 1250 | 892 | 5 | 8 | 0.0104 | 345 | 0 |

Total statements 6250; with E 4457. Crux sets identical to A2's for the same round (exploratory-extra check): {'n2_rounds': 250, 'in_a2': 250, 'identical_crux_sets': 250}.

## 2. Cost

- Session (harness list price): {'billed_s': 694.4, 'session_cost_usd': 0.9332, 'cold_start_s': 116.3}; wall 633.4 s; harness stats {'calls': 4539, 'cache_hits': 255, 'retries': 0, 'spent_usd': 0.9331902719999999}.
- ledger.csv: 2026-11-16T02:05Z | scorer N2 qwen3.8-27b v2 (6250 statements, 250 rounds; 6500 calls est.) ESTIMATE | estimate 3.407 | actual  | timeout 2400
- ledger.csv: 2026-11-16T02:16Z | scorer N2 qwen3.8-27b v2 ACTUAL | estimate  | actual 0.9332 | timeout 2400
- Container check after the run: {'waited_s': 71, 'own_rows_final': 0, 'other_app_rows': 0, 'stopped_by_id': [], 'returncode': 0, 'error': None}

## 3. Per generator × cell descriptives (all 6,250 statements)

| generator | cell | n | n with E | parse-fail rate | zero-crux rate | mean E | share E=0 | share E=1 | mean words | over-cap rate | preamble n (rate) | truncated | think leak | refusal/meta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma4-12b | SAT-COMMON | 250 | 180 | 0.0040 | 0.2760 | 0.8296 | 0.1389 | 0.8000 | 125.8 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | SAT-DIS | 250 | 178 | 0.0120 | 0.2760 | 0.1236 | 0.8427 | 0.0899 | 126.8 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | ACC-COMMON | 250 | 177 | 0.0160 | 0.2760 | 0.2674 | 0.6667 | 0.2034 | 120.9 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | ACC-DIS | 250 | 177 | 0.0160 | 0.2760 | 0.0113 | 0.9831 | 0.0056 | 124.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | NEU-COMMON | 250 | 178 | 0.0120 | 0.2760 | 0.6217 | 0.3315 | 0.5730 | 125.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | SAT-COMMON | 250 | 178 | 0.0120 | 0.2760 | 0.8624 | 0.1011 | 0.8258 | 143.8 | 0.3000 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | SAT-DIS | 250 | 179 | 0.0080 | 0.2760 | 0.0419 | 0.9385 | 0.0223 | 146.4 | 0.3880 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | ACC-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.3231 | 0.6145 | 0.2626 | 142.5 | 0.2720 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | ACC-DIS | 250 | 180 | 0.0040 | 0.2760 | 0.0139 | 0.9778 | 0.0056 | 145.6 | 0.3520 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | NEU-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.6667 | 0.2905 | 0.6257 | 148.1 | 0.4120 | 0 (0.0000) | 0 | 0 | 0 |
| ministral3-14b | SAT-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.8994 | 0.0894 | 0.8883 | 148.9 | 0.4160 | 18 (0.0720) | 0 | 0 | 0 |
| ministral3-14b | SAT-DIS | 250 | 176 | 0.0200 | 0.2760 | 0.1013 | 0.8750 | 0.0795 | 154.9 | 0.6080 | 12 (0.0480) | 0 | 0 | 0 |
| ministral3-14b | ACC-COMMON | 250 | 178 | 0.0120 | 0.2760 | 0.3418 | 0.5955 | 0.2809 | 149.1 | 0.4000 | 16 (0.0640) | 0 | 0 | 0 |
| ministral3-14b | ACC-DIS | 250 | 175 | 0.0240 | 0.2760 | 0.0086 | 0.9886 | 0.0057 | 161.6 | 0.7240 | 0 (0.0000) | 0 | 0 | 0 |
| ministral3-14b | NEU-COMMON | 250 | 178 | 0.0120 | 0.2760 | 0.7949 | 0.1742 | 0.7640 | 148.3 | 0.4520 | 63 (0.2520) | 0 | 0 | 0 |
| phi4-14b | SAT-COMMON | 250 | 180 | 0.0040 | 0.2760 | 0.9315 | 0.0389 | 0.9000 | 126.8 | 0.0240 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | SAT-DIS | 250 | 178 | 0.0120 | 0.2760 | 0.2378 | 0.6910 | 0.1685 | 130.4 | 0.0760 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | ACC-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.5987 | 0.3575 | 0.5531 | 127.4 | 0.0400 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | ACC-DIS | 250 | 178 | 0.0120 | 0.2760 | 0.0159 | 0.9719 | 0.0056 | 137.6 | 0.1720 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | NEU-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.7858 | 0.1788 | 0.7486 | 129.8 | 0.0440 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | SAT-COMMON | 250 | 178 | 0.0120 | 0.2760 | 0.9466 | 0.0449 | 0.9382 | 119.4 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | SAT-DIS | 250 | 179 | 0.0080 | 0.2760 | 0.4907 | 0.4581 | 0.4413 | 117.6 | 0.0040 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | ACC-COMMON | 250 | 179 | 0.0080 | 0.2760 | 0.6443 | 0.2905 | 0.5810 | 117.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | ACC-DIS | 250 | 176 | 0.0200 | 0.2760 | 0.0587 | 0.9148 | 0.0341 | 115.1 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | NEU-COMMON | 250 | 180 | 0.0040 | 0.2760 | 0.8528 | 0.1222 | 0.8278 | 120.6 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |

## 4. Effective n, drops and MDE (spec §5, §7, Amendment 2)

| generator | rounds | complete rounds | dropped by reason | launches (primary) | MDE d_z (α 0.05) | MDE d_z (strictest Holm α) |
|---|---|---|---|---|---|---|
| gemma4-12b | 250 | 174 | {'zero_crux': 69, 'label_parse_fail': 6, 'extract_fail': 1} | 166 | 0.214 | 0.280 (α=0.0050) |
| qwen3.8-27b | 250 | 177 | {'zero_crux': 69, 'extract_fail': 1, 'label_parse_fail': 3} | 169 | 0.212 | 0.277 (α=0.0050) |
| ministral3-14b | 250 | 168 | {'zero_crux': 69, 'label_parse_fail': 12, 'extract_fail': 1} | 162 | 0.217 | 0.295 (α=0.0033) |
| phi4-14b | 250 | 176 | {'zero_crux': 69, 'extract_fail': 1, 'label_parse_fail': 4} | 168 | 0.212 | 0.288 (α=0.0033) |
| llama3.1-8b | 250 | 173 | {'zero_crux': 69, 'extract_fail': 1, 'label_parse_fail': 7} | 167 | 0.214 | 0.291 (α=0.0033) |

## 5. Manipulation / instrument check (spec §2; outside the Holm families)

| generator | MC estimate [95% CI] | n rounds | verdict |
|---|---|---|---|
| gemma4-12b | 0.482 [0.440, 0.527] | 174 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| qwen3.8-27b | 0.566 [0.522, 0.611] | 177 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| ministral3-14b | 0.576 [0.534, 0.618] | 168 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| phi4-14b | 0.641 [0.599, 0.683] | 176 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| llama3.1-8b | 0.537 [0.485, 0.586] | 173 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |

New generators failing the check: [] (rule: 2 or more of 3 failing means the paper may not say the instruction effect generalises across models). Mahajan et al. (2611.05135) is credited for the agreement-vs-differences main effect.

## 6. Pre-specified contrasts, primary analysis set (every estimate, including flat or null ones)

| generator | contrast | unadjusted est [95% CI] | p_boot | p_holm | d_z | adjusted est [95% CI] | p_boot | p_holm | n rounds | n launches |
|---|---|---|---|---|---|---|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | 0.115 [0.074, 0.160] | 0.0010 | 0.0100 | 0.382 | 0.116 [0.074, 0.163] | 0.0010 | 0.0100 | 174 | 166 |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.557 [0.491, 0.629] | 0.0010 | 0.0100 | 1.191 | 0.553 [0.482, 0.630] | 0.0010 | 0.0100 | 174 | 166 |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.443 [0.356, 0.529] | 0.0010 | 0.0100 | 0.771 | 0.435 [0.348, 0.521] | 0.0010 | 0.0100 | 174 | 166 |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | 0.205 [0.140, 0.271] | 0.0010 | 0.0100 | 0.441 | 0.205 [0.140, 0.271] | 0.0010 | 0.0100 | 174 | 166 |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | 0.352 [0.281, 0.427] | 0.0010 | 0.0100 | 0.687 | 0.383 [0.304, 0.465] | 0.0010 | 0.0100 | 174 | 166 |
| gemma4-12b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.336 [0.297, 0.376] | 0.0010 | — | 1.247 | 0.344 [0.302, 0.386] | 0.0010 | — | 174 | 166 |
| qwen3.8-27b (self) | C1_override (SAT-DIS - ACC-DIS) | 0.028 [0.006, 0.053] | 0.0120 | 0.0120 | 0.170 | 0.028 [0.006, 0.052] | 0.0100 | 0.0100 | 177 | 169 |
| qwen3.8-27b (self) | C2_protection (SAT-COMMON - ACC-COMMON) | 0.535 [0.462, 0.606] | 0.0010 | 0.0100 | 1.066 | 0.536 [0.462, 0.607] | 0.0010 | 0.0100 | 177 | 169 |
| qwen3.8-27b (self) | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.507 [0.429, 0.582] | 0.0010 | 0.0100 | 0.950 | 0.506 [0.427, 0.582] | 0.0010 | 0.0100 | 177 | 169 |
| qwen3.8-27b (self) | C4a (SAT-COMMON - NEU-COMMON) | 0.193 [0.126, 0.261] | 0.0010 | 0.0100 | 0.404 | 0.192 [0.121, 0.266] | 0.0010 | 0.0100 | 177 | 169 |
| qwen3.8-27b (self) | C4b (NEU-COMMON - ACC-COMMON) | 0.342 [0.264, 0.414] | 0.0010 | 0.0100 | 0.635 | 0.360 [0.279, 0.437] | 0.0010 | 0.0100 | 177 | 169 |
| qwen3.8-27b (self) | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.282 [0.244, 0.318] | 0.0010 | — | 1.075 | 0.282 [0.244, 0.318] | 0.0010 | — | 177 | 169 |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | 0.085 [0.046, 0.128] | 0.0010 | 0.0150 | 0.301 | 0.080 [0.042, 0.120] | 0.0010 | 0.0150 | 168 | 162 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.555 [0.480, 0.625] | 0.0010 | 0.0150 | 1.140 | 0.558 [0.482, 0.625] | 0.0010 | 0.0150 | 168 | 162 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.469 [0.377, 0.556] | 0.0010 | 0.0150 | 0.797 | 0.476 [0.386, 0.561] | 0.0010 | 0.0150 | 168 | 162 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.107 [0.054, 0.164] | 0.0010 | 0.0150 | 0.274 | 0.113 [0.054, 0.178] | 0.0010 | 0.0150 | 168 | 162 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.447 [0.367, 0.524] | 0.0010 | 0.0150 | 0.852 | 0.445 [0.361, 0.525] | 0.0010 | 0.0150 | 168 | 162 |
| ministral3-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.320 [0.279, 0.359] | 0.0010 | — | 1.194 | 0.320 [0.278, 0.359] | 0.0010 | — | 168 | 162 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | 0.219 [0.165, 0.272] | 0.0010 | 0.0150 | 0.581 | 0.223 [0.162, 0.281] | 0.0010 | 0.0150 | 176 | 168 |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.338 [0.273, 0.403] | 0.0010 | 0.0150 | 0.715 | 0.337 [0.271, 0.402] | 0.0010 | 0.0150 | 176 | 168 |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.119 [0.028, 0.216] | 0.0120 | 0.0200 | 0.179 | 0.134 [0.039, 0.231] | 0.0100 | 0.0180 | 176 | 168 |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.148 [0.088, 0.209] | 0.0010 | 0.0150 | 0.365 | 0.130 [0.070, 0.191] | 0.0010 | 0.0150 | 176 | 168 |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.190 [0.113, 0.269] | 0.0010 | 0.0150 | 0.357 | 0.199 [0.121, 0.278] | 0.0010 | 0.0150 | 176 | 168 |
| phi4-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.278 [0.241, 0.315] | 0.0010 | — | 1.037 | 0.274 [0.234, 0.313] | 0.0010 | — | 176 | 168 |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | 0.431 [0.356, 0.509] | 0.0010 | 0.0150 | 0.860 | 0.458 [0.381, 0.531] | 0.0010 | 0.0150 | 173 | 167 |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.302 [0.236, 0.367] | 0.0010 | 0.0150 | 0.679 | 0.306 [0.239, 0.376] | 0.0010 | 0.0150 | 173 | 167 |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.129 [-0.226, -0.032] | 0.0100 | 0.0200 | -0.193 | -0.136 [-0.233, -0.037] | 0.0090 | 0.0180 | 173 | 167 |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | 0.110 [0.061, 0.160] | 0.0010 | 0.0150 | 0.327 | 0.105 [0.058, 0.152] | 0.0010 | 0.0150 | 173 | 167 |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | 0.192 [0.124, 0.260] | 0.0010 | 0.0150 | 0.403 | 0.196 [0.123, 0.268] | 0.0010 | 0.0150 | 173 | 167 |
| llama3.1-8b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.366 [0.316, 0.417] | 0.0010 | — | 1.089 | 0.384 [0.330, 0.436] | 0.0010 | — | 173 | 167 |

SYS (spec §6 system effect) is a falsifier quantity, not in the Holm family. Contrast that is CI-excluding-0 in only one of the unadjusted / adjusted columns is labelled as such below (JSON `only_in_one_variant`).

### Falsifiers (spec §6), primary unadjusted

- gemma4-12b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': False}
- qwen3.8-27b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': False}
- ministral3-14b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': False}
- phi4-14b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': False}
- llama3.1-8b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': False}

### Labels: contrasts whose CI excludes 0 in only one variant (adjusted vs unadjusted; with vs without preambled rounds)

- none

## 7. Covariates (adjusted primary): slopes of the round-level difference on Δlog(words) and Δpreamble

| generator | contrast | slope Δlog(words) | slope Δpreamble | rounds with Δpreamble ≠ 0 | bootstrap resamples (of 2000) with a rank-deficient design |
|---|---|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | -0.054 | NA | 0 | 0 |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.116 | NA | 0 | 0 |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.319 | NA | 0 | 0 |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | -0.027 | NA | 0 | 0 |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | -0.841 | NA | 0 | 0 |
| gemma4-12b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | -0.633 | NA | 0 | 0 |
| gemma4-12b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | -0.268 | NA | 0 | 0 |
| qwen3.8-27b | C1_override (SAT-DIS - ACC-DIS) | 0.141 | NA | 0 | 0 |
| qwen3.8-27b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.147 | NA | 0 | 0 |
| qwen3.8-27b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.061 | NA | 0 | 0 |
| qwen3.8-27b | C4a (SAT-COMMON - NEU-COMMON) | -0.050 | NA | 0 | 0 |
| qwen3.8-27b | C4b (NEU-COMMON - ACC-COMMON) | -0.509 | NA | 0 | 0 |
| qwen3.8-27b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | -0.334 | NA | 0 | 0 |
| qwen3.8-27b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | -0.021 | NA | 0 | 0 |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | -0.232 | -0.086 | 9 | 1 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.186 | -0.104 | 23 | 0 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.190 | -0.096 | 32 | 0 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | -0.077 | 0.026 | 52 | 0 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | -0.494 | -0.005 | 51 | 0 |
| ministral3-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | -0.438 | 0.166 | 33 | 0 |
| ministral3-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | -0.223 | -0.103 | 32 | 0 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | 0.080 | NA | 0 | 0 |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.571 | NA | 0 | 0 |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.294 | NA | 0 | 0 |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | -0.636 | NA | 0 | 0 |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | -0.333 | NA | 0 | 0 |
| phi4-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | -0.226 | NA | 0 | 0 |
| phi4-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | -0.171 | NA | 0 | 0 |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | -0.873 | NA | 0 | 0 |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.247 | NA | 0 | 0 |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.528 | NA | 0 | 0 |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | -0.405 | NA | 0 | 0 |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | -0.135 | NA | 0 | 0 |
| llama3.1-8b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | -0.868 | NA | 0 | 0 |
| llama3.1-8b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | -0.721 | NA | 0 | 0 |

Length is labelled a possible mediator, not a confound to remove (spec §5, §9). In a rank-deficient resample (no round with a nonzero preamble difference drawn) the pseudo-inverse sets that slope to 0 and keeps the intercept; the count is reported because the preamble adjustment is then carried by few rounds.

## 8. Sensitivity analyses (unadjusted and adjusted; every pre-specified contrast)

### excl_preamble_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 174 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.115 [0.074, 0.160] | 0.116 [0.074, 0.163] |
| gemma4-12b | 174 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.557 [0.491, 0.629] | 0.553 [0.482, 0.630] |
| gemma4-12b | 174 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.443 [0.356, 0.529] | 0.435 [0.348, 0.521] |
| gemma4-12b | 174 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.205 [0.140, 0.271] | 0.205 [0.140, 0.271] |
| gemma4-12b | 174 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.352 [0.281, 0.427] | 0.383 [0.304, 0.465] |
| gemma4-12b | 174 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.482 [0.440, 0.527] | 0.472 [0.430, 0.517] |
| gemma4-12b | 174 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.336 [0.297, 0.376] | 0.344 [0.302, 0.386] |
| qwen3.8-27b | 177 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.028 [0.006, 0.053] | 0.028 [0.006, 0.052] |
| qwen3.8-27b | 177 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.535 [0.462, 0.606] | 0.536 [0.462, 0.607] |
| qwen3.8-27b | 177 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.507 [0.429, 0.582] | 0.506 [0.427, 0.582] |
| qwen3.8-27b | 177 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.193 [0.126, 0.261] | 0.192 [0.121, 0.266] |
| qwen3.8-27b | 177 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.342 [0.264, 0.414] | 0.360 [0.279, 0.437] |
| qwen3.8-27b | 177 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.566 [0.522, 0.611] | 0.565 [0.522, 0.609] |
| qwen3.8-27b | 177 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.282 [0.244, 0.318] | 0.282 [0.244, 0.318] |
| ministral3-14b | 97 (71) | False | C1_override (SAT-DIS - ACC-DIS) | 0.088 [0.036, 0.143] | 0.077 [0.031, 0.128] |
| ministral3-14b | 97 (71) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.572 [0.469, 0.661] | 0.581 [0.475, 0.667] |
| ministral3-14b | 97 (71) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.485 [0.361, 0.592] | 0.498 [0.376, 0.603] |
| ministral3-14b | 97 (71) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.134 [0.056, 0.216] | 0.135 [0.051, 0.217] |
| ministral3-14b | 97 (71) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.438 [0.328, 0.546] | 0.425 [0.317, 0.523] |
| ministral3-14b | 97 (71) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.562 [0.503, 0.619] | 0.551 [0.490, 0.607] |
| ministral3-14b | 97 (71) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.330 [0.276, 0.379] | 0.326 [0.271, 0.374] |
| phi4-14b | 176 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.219 [0.165, 0.272] | 0.223 [0.162, 0.281] |
| phi4-14b | 176 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.338 [0.273, 0.403] | 0.337 [0.271, 0.402] |
| phi4-14b | 176 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.119 [0.028, 0.216] | 0.134 [0.039, 0.231] |
| phi4-14b | 176 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.148 [0.088, 0.209] | 0.130 [0.070, 0.191] |
| phi4-14b | 176 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.190 [0.113, 0.269] | 0.199 [0.121, 0.278] |
| phi4-14b | 176 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.641 [0.599, 0.683] | 0.631 [0.579, 0.681] |
| phi4-14b | 176 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.278 [0.241, 0.315] | 0.274 [0.234, 0.313] |
| llama3.1-8b | 173 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.431 [0.356, 0.509] | 0.458 [0.381, 0.531] |
| llama3.1-8b | 173 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.302 [0.236, 0.367] | 0.306 [0.239, 0.376] |
| llama3.1-8b | 173 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.129 [-0.226, -0.032] | -0.136 [-0.233, -0.037] |
| llama3.1-8b | 173 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.110 [0.061, 0.160] | 0.105 [0.058, 0.152] |
| llama3.1-8b | 173 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.192 [0.124, 0.260] | 0.196 [0.123, 0.268] |
| llama3.1-8b | 173 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.537 [0.485, 0.586] | 0.553 [0.501, 0.604] |
| llama3.1-8b | 173 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.366 [0.316, 0.417] | 0.384 [0.330, 0.436] |

### excl_any_flagged_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 174 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.115 [0.074, 0.160] | 0.116 [0.074, 0.163] |
| gemma4-12b | 174 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.557 [0.491, 0.629] | 0.553 [0.482, 0.630] |
| gemma4-12b | 174 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.443 [0.356, 0.529] | 0.435 [0.348, 0.521] |
| gemma4-12b | 174 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.205 [0.140, 0.271] | 0.205 [0.140, 0.271] |
| gemma4-12b | 174 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.352 [0.281, 0.427] | 0.383 [0.304, 0.465] |
| gemma4-12b | 174 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.482 [0.440, 0.527] | 0.472 [0.430, 0.517] |
| gemma4-12b | 174 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.336 [0.297, 0.376] | 0.344 [0.302, 0.386] |
| qwen3.8-27b | 177 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.028 [0.006, 0.053] | 0.028 [0.006, 0.052] |
| qwen3.8-27b | 177 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.535 [0.462, 0.606] | 0.536 [0.462, 0.607] |
| qwen3.8-27b | 177 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.507 [0.429, 0.582] | 0.506 [0.427, 0.582] |
| qwen3.8-27b | 177 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.193 [0.126, 0.261] | 0.192 [0.121, 0.266] |
| qwen3.8-27b | 177 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.342 [0.264, 0.414] | 0.360 [0.279, 0.437] |
| qwen3.8-27b | 177 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.566 [0.522, 0.611] | 0.565 [0.522, 0.609] |
| qwen3.8-27b | 177 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.282 [0.244, 0.318] | 0.282 [0.244, 0.318] |
| ministral3-14b | 97 (71) | False | C1_override (SAT-DIS - ACC-DIS) | 0.088 [0.036, 0.143] | 0.077 [0.031, 0.128] |
| ministral3-14b | 97 (71) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.572 [0.469, 0.661] | 0.581 [0.475, 0.667] |
| ministral3-14b | 97 (71) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.485 [0.361, 0.592] | 0.498 [0.376, 0.603] |
| ministral3-14b | 97 (71) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.134 [0.056, 0.216] | 0.135 [0.051, 0.217] |
| ministral3-14b | 97 (71) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.438 [0.328, 0.546] | 0.425 [0.317, 0.523] |
| ministral3-14b | 97 (71) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.562 [0.503, 0.619] | 0.551 [0.490, 0.607] |
| ministral3-14b | 97 (71) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.330 [0.276, 0.379] | 0.326 [0.271, 0.374] |
| phi4-14b | 176 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.219 [0.165, 0.272] | 0.223 [0.162, 0.281] |
| phi4-14b | 176 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.338 [0.273, 0.403] | 0.337 [0.271, 0.402] |
| phi4-14b | 176 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.119 [0.028, 0.216] | 0.134 [0.039, 0.231] |
| phi4-14b | 176 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.148 [0.088, 0.209] | 0.130 [0.070, 0.191] |
| phi4-14b | 176 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.190 [0.113, 0.269] | 0.199 [0.121, 0.278] |
| phi4-14b | 176 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.641 [0.599, 0.683] | 0.631 [0.579, 0.681] |
| phi4-14b | 176 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.278 [0.241, 0.315] | 0.274 [0.234, 0.313] |
| llama3.1-8b | 173 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.431 [0.356, 0.509] | 0.458 [0.381, 0.531] |
| llama3.1-8b | 173 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.302 [0.236, 0.367] | 0.306 [0.239, 0.376] |
| llama3.1-8b | 173 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.129 [-0.226, -0.032] | -0.136 [-0.233, -0.037] |
| llama3.1-8b | 173 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.110 [0.061, 0.160] | 0.105 [0.058, 0.152] |
| llama3.1-8b | 173 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.192 [0.124, 0.260] | 0.196 [0.123, 0.268] |
| llama3.1-8b | 173 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.537 [0.485, 0.586] | 0.553 [0.501, 0.604] |
| llama3.1-8b | 173 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.366 [0.316, 0.417] | 0.384 [0.330, 0.436] |

### under_cap_all_cells_le_150w

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 174 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.115 [0.074, 0.160] | 0.116 [0.074, 0.163] |
| gemma4-12b | 174 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.557 [0.491, 0.629] | 0.553 [0.482, 0.630] |
| gemma4-12b | 174 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.443 [0.356, 0.529] | 0.435 [0.348, 0.521] |
| gemma4-12b | 174 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.205 [0.140, 0.271] | 0.205 [0.140, 0.271] |
| gemma4-12b | 174 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.352 [0.281, 0.427] | 0.383 [0.304, 0.465] |
| gemma4-12b | 174 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.482 [0.440, 0.527] | 0.472 [0.430, 0.517] |
| gemma4-12b | 174 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.336 [0.297, 0.376] | 0.344 [0.302, 0.386] |
| qwen3.8-27b | 26 (151) | False | C1_override (SAT-DIS - ACC-DIS) | 0.077 [0.000, 0.173] | 0.082 [0.000, 0.187] |
| qwen3.8-27b | 26 (151) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.712 [0.558, 0.865] | 0.715 [0.571, 0.856] |
| qwen3.8-27b | 26 (151) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.635 [0.442, 0.808] | 0.633 [0.427, 0.819] |
| qwen3.8-27b | 26 (151) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.212 [0.077, 0.365] | 0.248 [0.081, 0.466] |
| qwen3.8-27b | 26 (151) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.500 [0.327, 0.673] | 0.492 [0.288, 0.681] |
| qwen3.8-27b | 26 (151) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.510 [0.423, 0.606] | 0.506 [0.421, 0.605] |
| qwen3.8-27b | 26 (151) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.394 [0.317, 0.471] | 0.404 [0.331, 0.476] |
| ministral3-14b | 6 (162) | False | C1_override (SAT-DIS - ACC-DIS) | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| ministral3-14b | 6 (162) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.750 [0.417, 1.000] | 0.816 [-2.621, 1.000] |
| ministral3-14b | 6 (162) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.750 [0.417, 1.000] | 0.710 [0.180, 2.896] |
| ministral3-14b | 6 (162) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| ministral3-14b | 6 (162) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.750 [0.417, 1.000] | 0.747 [-0.226, 2.564] |
| ministral3-14b | 6 (162) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.458 [0.250, 0.625] | 0.456 [0.150, 0.555] |
| ministral3-14b | 6 (162) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.375 [0.208, 0.500] | 0.282 [0.140, 0.754] |
| phi4-14b | 125 (51) | False | C1_override (SAT-DIS - ACC-DIS) | 0.220 [0.153, 0.288] | 0.226 [0.153, 0.302] |
| phi4-14b | 125 (51) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.324 [0.244, 0.407] | 0.325 [0.244, 0.409] |
| phi4-14b | 125 (51) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.104 [-0.012, 0.223] | 0.097 [-0.024, 0.215] |
| phi4-14b | 125 (51) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.152 [0.082, 0.226] | 0.140 [0.068, 0.214] |
| phi4-14b | 125 (51) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.172 [0.078, 0.266] | 0.190 [0.095, 0.290] |
| phi4-14b | 125 (51) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.640 [0.590, 0.693] | 0.626 [0.572, 0.681] |
| phi4-14b | 125 (51) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.272 [0.224, 0.319] | 0.269 [0.219, 0.317] |
| llama3.1-8b | 172 (1) | False | C1_override (SAT-DIS - ACC-DIS) | 0.427 [0.356, 0.500] | 0.455 [0.381, 0.526] |
| llama3.1-8b | 172 (1) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.300 [0.235, 0.367] | 0.305 [0.237, 0.375] |
| llama3.1-8b | 172 (1) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.127 [-0.223, -0.030] | -0.133 [-0.227, -0.032] |
| llama3.1-8b | 172 (1) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.110 [0.064, 0.164] | 0.106 [0.061, 0.157] |
| llama3.1-8b | 172 (1) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.190 [0.120, 0.259] | 0.195 [0.119, 0.268] |
| llama3.1-8b | 172 (1) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.538 [0.489, 0.587] | 0.557 [0.508, 0.607] |
| llama3.1-8b | 172 (1) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.364 [0.313, 0.415] | 0.383 [0.331, 0.434] |

### excl_dev_launch_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 146 (28) | False | C1_override (SAT-DIS - ACC-DIS) | 0.106 [0.062, 0.155] | 0.108 [0.063, 0.160] |
| gemma4-12b | 146 (28) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.538 [0.458, 0.612] | 0.516 [0.433, 0.598] |
| gemma4-12b | 146 (28) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.432 [0.333, 0.523] | 0.420 [0.321, 0.510] |
| gemma4-12b | 146 (28) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.200 [0.124, 0.275] | 0.200 [0.124, 0.275] |
| gemma4-12b | 146 (28) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.338 [0.256, 0.420] | 0.361 [0.271, 0.455] |
| gemma4-12b | 146 (28) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.478 [0.428, 0.529] | 0.470 [0.421, 0.520] |
| gemma4-12b | 146 (28) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.322 [0.278, 0.365] | 0.328 [0.281, 0.374] |
| qwen3.8-27b | 147 (30) | False | C1_override (SAT-DIS - ACC-DIS) | 0.037 [0.010, 0.069] | 0.036 [0.010, 0.067] |
| qwen3.8-27b | 147 (30) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.528 [0.450, 0.606] | 0.528 [0.448, 0.605] |
| qwen3.8-27b | 147 (30) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.491 [0.407, 0.574] | 0.491 [0.405, 0.575] |
| qwen3.8-27b | 147 (30) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.188 [0.111, 0.266] | 0.184 [0.099, 0.270] |
| qwen3.8-27b | 147 (30) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.340 [0.257, 0.424] | 0.355 [0.258, 0.446] |
| qwen3.8-27b | 147 (30) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.557 [0.506, 0.608] | 0.557 [0.506, 0.608] |
| qwen3.8-27b | 147 (30) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.283 [0.242, 0.325] | 0.283 [0.242, 0.324] |
| ministral3-14b | 140 (28) | False | C1_override (SAT-DIS - ACC-DIS) | 0.092 [0.050, 0.141] | 0.076 [0.038, 0.120] |
| ministral3-14b | 140 (28) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.565 [0.482, 0.648] | 0.569 [0.486, 0.651] |
| ministral3-14b | 140 (28) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.474 [0.375, 0.569] | 0.483 [0.381, 0.581] |
| ministral3-14b | 140 (28) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.114 [0.050, 0.179] | 0.121 [0.051, 0.192] |
| ministral3-14b | 140 (28) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.451 [0.368, 0.536] | 0.450 [0.364, 0.537] |
| ministral3-14b | 140 (28) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.571 [0.525, 0.617] | 0.538 [0.485, 0.588] |
| ministral3-14b | 140 (28) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.329 [0.283, 0.375] | 0.328 [0.284, 0.373] |
| phi4-14b | 146 (30) | False | C1_override (SAT-DIS - ACC-DIS) | 0.205 [0.149, 0.264] | 0.207 [0.148, 0.271] |
| phi4-14b | 146 (30) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.329 [0.250, 0.401] | 0.329 [0.253, 0.403] |
| phi4-14b | 146 (30) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.123 [0.020, 0.220] | 0.143 [0.029, 0.249] |
| phi4-14b | 146 (30) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.154 [0.091, 0.220] | 0.134 [0.074, 0.195] |
| phi4-14b | 146 (30) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.175 [0.089, 0.257] | 0.187 [0.105, 0.268] |
| phi4-14b | 146 (30) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.653 [0.605, 0.699] | 0.647 [0.593, 0.698] |
| phi4-14b | 146 (30) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.267 [0.223, 0.310] | 0.258 [0.215, 0.302] |
| llama3.1-8b | 144 (29) | False | C1_override (SAT-DIS - ACC-DIS) | 0.424 [0.336, 0.507] | 0.448 [0.359, 0.530] |
| llama3.1-8b | 144 (29) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.307 [0.238, 0.379] | 0.315 [0.243, 0.390] |
| llama3.1-8b | 144 (29) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.117 [-0.228, -0.006] | -0.122 [-0.230, -0.012] |
| llama3.1-8b | 144 (29) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.125 [0.070, 0.182] | 0.120 [0.067, 0.178] |
| llama3.1-8b | 144 (29) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.182 [0.107, 0.257] | 0.189 [0.106, 0.270] |
| llama3.1-8b | 144 (29) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.549 [0.494, 0.606] | 0.564 [0.510, 0.619] |
| llama3.1-8b | 144 (29) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.365 [0.309, 0.424] | 0.385 [0.327, 0.443] |

### Rank-based check for C3 (Wilcoxon signed-rank, round level; spec §5)

| generator | statistic | p | n nonzero / n |
|---|---|---|---|
| gemma4-12b | 502.0 | 0.0000 | 109 / 174 |
| qwen3.8-27b | 264.0 | 0.0000 | 112 / 177 |
| ministral3-14b | 727.5 | 0.0000 | 116 / 168 |
| phi4-14b | 1893.0 | 0.0149 | 101 / 176 |
| llama3.1-8b | 1928.0 | 0.0212 | 101 / 173 |

## 9. C5 baseline (descriptive): cell E minus mean E of the round's iteration-0 HM candidates (A2 v2 scores)

| generator | cell | est [95% CI] | n rounds |
|---|---|---|---|
| gemma4-12b | SAT-COMMON | -0.136 [-0.188, -0.084] | 174 |
| gemma4-12b | SAT-DIS | -0.839 [-0.885, -0.790] | 174 |
| gemma4-12b | ACC-COMMON | -0.693 [-0.752, -0.633] | 174 |
| gemma4-12b | ACC-DIS | -0.954 [-0.973, -0.932] | 174 |
| gemma4-12b | NEU-COMMON | -0.341 [-0.408, -0.278] | 174 |
| qwen3.8-27b | SAT-COMMON | -0.103 [-0.152, -0.060] | 177 |
| qwen3.8-27b | SAT-DIS | -0.922 [-0.948, -0.893] | 177 |
| qwen3.8-27b | ACC-COMMON | -0.638 [-0.701, -0.571] | 177 |
| qwen3.8-27b | ACC-DIS | -0.951 [-0.970, -0.929] | 177 |
| qwen3.8-27b | NEU-COMMON | -0.296 [-0.357, -0.234] | 177 |
| ministral3-14b | SAT-COMMON | -0.064 [-0.111, -0.023] | 168 |
| ministral3-14b | SAT-DIS | -0.875 [-0.914, -0.830] | 168 |
| ministral3-14b | ACC-COMMON | -0.619 [-0.686, -0.548] | 168 |
| ministral3-14b | ACC-DIS | -0.960 [-0.978, -0.939] | 168 |
| ministral3-14b | NEU-COMMON | -0.171 [-0.229, -0.118] | 168 |
| phi4-14b | SAT-COMMON | -0.029 [-0.064, 0.004] | 176 |
| phi4-14b | SAT-DIS | -0.730 [-0.784, -0.676] | 176 |
| phi4-14b | ACC-COMMON | -0.367 [-0.435, -0.302] | 176 |
| phi4-14b | ACC-DIS | -0.948 [-0.968, -0.926] | 176 |
| phi4-14b | NEU-COMMON | -0.177 [-0.234, -0.122] | 176 |
| llama3.1-8b | SAT-COMMON | -0.012 [-0.046, 0.019] | 173 |
| llama3.1-8b | SAT-DIS | -0.484 [-0.554, -0.412] | 173 |
| llama3.1-8b | ACC-COMMON | -0.313 [-0.377, -0.251] | 173 |
| llama3.1-8b | ACC-DIS | -0.914 [-0.944, -0.880] | 173 |
| llama3.1-8b | NEU-COMMON | -0.121 [-0.176, -0.070] | 173 |

## 10. Pooled over 5 generators — DESCRIPTIVE ONLY, not tested (intersection: 163 rounds, 158 launches)

| contrast | paired mean over generators [95% CI] | mixed model unadjusted [95% model CI] | interaction χ²(4) p | mixed model adjusted [95% model CI] | interaction χ²(4) p |
|---|---|---|---|---|---|
| C1_override (SAT-DIS - ACC-DIS) | 0.176 [0.151, 0.201] | 0.176 [0.146, 0.206] | 0.0000 | 0.177 [0.147, 0.207] | 0.0000 |
| C2_protection (SAT-COMMON - ACC-COMMON) | 0.453 [0.412, 0.496] | 0.453 [0.423, 0.483] | 0.0000 | 0.457 [0.427, 0.487] | 0.0000 |
| C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.277 [0.222, 0.331] | 0.277 [0.234, 0.319] | 0.0000 | 0.281 [0.238, 0.323] | 0.0000 |
| C4a (SAT-COMMON - NEU-COMMON) | 0.149 [0.118, 0.185] | 0.149 [0.119, 0.179] | 0.0892 | 0.147 [0.117, 0.177] | 0.0892 |
| C4b (NEU-COMMON - ACC-COMMON) | 0.304 [0.264, 0.343] | 0.304 [0.274, 0.334] | 0.0000 | 0.310 [0.280, 0.341] | 0.0000 |
| MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.560 [0.533, 0.584] | 0.560 [0.538, 0.581] | 0.0004 | 0.557 [0.535, 0.578] | 0.0014 |
| SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.315 [0.293, 0.335] | 0.315 [0.294, 0.336] | 0.0518 | 0.317 [0.296, 0.338] | 0.0157 |

Mixed model fitted by: unadjusted — statsmodels MixedLM (REML; optimisers lbfgs, bfgs, cg tried in sequence): random intercept launch + variance component round within launch (converged True); adjusted — statsmodels MixedLM (REML; optimisers lbfgs, bfgs, cg tried in sequence): random intercept launch + variance component round within launch (converged True). Adjusted covariate coefficients: {'lw_0': {'est': -0.15659378343548008, 'se': 0.1609533693903409}, 'lw_1': {'est': -0.257359811775185, 'se': 0.12743787457161723}, 'lw_2': {'est': -0.20834953289277297, 'se': 0.09704942210049029}, 'lw_3': {'est': -0.18672390370468164, 'se': 0.11762055430896759}, 'lw_4': {'est': -0.5599339519991051, 'se': 0.14407477199538551}, 'pre': {'est': 0.013637872860095887, 'se': 0.039187687410418}}. Per-generator model-based estimates are in the JSON.

## 11. Exploratory-extra (NOT in the spec; separate)

Wild cluster bootstrap-t (FR §7 method of record for the A2 family; B = 2000, seed 20261115) for the primary unadjusted contrasts:

| generator | contrast | est [95% CI] | p (bootstrap-t) |
|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | 0.115 [0.070, 0.160] | 0.0005 |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.557 [0.483, 0.631] | 0.0005 |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.443 [0.352, 0.532] | 0.0005 |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | 0.205 [0.136, 0.271] | 0.0005 |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | 0.352 [0.275, 0.431] | 0.0005 |
| gemma4-12b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.482 [0.437, 0.526] | 0.0005 |
| gemma4-12b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.336 [0.294, 0.376] | 0.0005 |
| qwen3.8-27b | C1_override (SAT-DIS - ACC-DIS) | 0.028 [0.004, 0.053] | 0.0255 |
| qwen3.8-27b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.535 [0.459, 0.612] | 0.0005 |
| qwen3.8-27b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.507 [0.428, 0.587] | 0.0005 |
| qwen3.8-27b | C4a (SAT-COMMON - NEU-COMMON) | 0.193 [0.126, 0.261] | 0.0005 |
| qwen3.8-27b | C4b (NEU-COMMON - ACC-COMMON) | 0.342 [0.268, 0.422] | 0.0005 |
| qwen3.8-27b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.566 [0.519, 0.609] | 0.0005 |
| qwen3.8-27b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.282 [0.243, 0.321] | 0.0005 |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | 0.085 [0.042, 0.127] | 0.0005 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.555 [0.479, 0.627] | 0.0005 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.469 [0.378, 0.556] | 0.0005 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.107 [0.051, 0.163] | 0.0005 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.447 [0.370, 0.526] | 0.0005 |
| ministral3-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.576 [0.533, 0.618] | 0.0005 |
| ministral3-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.320 [0.279, 0.360] | 0.0005 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | 0.219 [0.159, 0.275] | 0.0005 |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.338 [0.270, 0.410] | 0.0005 |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.119 [0.024, 0.220] | 0.0215 |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.148 [0.093, 0.209] | 0.0005 |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.190 [0.111, 0.269] | 0.0005 |
| phi4-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.641 [0.597, 0.684] | 0.0005 |
| phi4-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.278 [0.239, 0.318] | 0.0005 |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | 0.431 [0.355, 0.502] | 0.0005 |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.302 [0.232, 0.367] | 0.0005 |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.129 [-0.226, -0.026] | 0.0140 |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | 0.110 [0.059, 0.163] | 0.0005 |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | 0.192 [0.122, 0.259] | 0.0005 |
| llama3.1-8b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.537 [0.486, 0.585] | 0.0005 |
| llama3.1-8b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.366 [0.315, 0.417] | 0.0005 |

## 12. Files

- per-cell table (CSV): `analysis\n2_results\n2_cells.csv`
- all estimates (CSV): `analysis\n2_results\n2_estimates.csv`
- full results (JSON): `analysis\n2_results\n2_results__20261116T022434105493Z.json`

Implementation choices where the spec is silent are listed in the docstring of `analysis/n2_analysis.py` and in the JSON `implementation_choices`.
