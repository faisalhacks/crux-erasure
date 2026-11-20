# N2 results — EXPLORATORY (gate tag HIDE_NOT_HUMAN_VALIDATED)

Generated 2026-11-16T02:20:59Z by `analysis/n2_analysis.py` (sha256 `3ca33c7fbecad02cf5414c1a7bf0b45972505eabd9eef1d50bcc3b70c5744ec0`). Spec of record: `analysis/N2_ANALYSIS_SPEC.md` sha256 `afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0` (Amendments 1–5). Scores: `analysis\testout\n2_dummy\scores.jsonl` sha256 `fc00a74990dc109d24094aded1dcfdbf614df46aee4e0e2d18248374efd776d4`.

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
| gemma4-12b | 1250 | 1153 | 0 | 9 | 0.0072 | 88 | 0 |
| qwen3.8-27b (self-scored) | 1250 | 1114 | 0 | 11 | 0.0088 | 125 | 0 |
| ministral3-14b | 1250 | 1120 | 0 | 5 | 0.0040 | 125 | 0 |
| phi4-14b | 1250 | 1114 | 0 | 11 | 0.0088 | 125 | 0 |
| llama3.1-8b | 1250 | 1117 | 0 | 8 | 0.0064 | 125 | 0 |

Total statements 6250; with E 5618. Crux sets identical to A2's for the same round (exploratory-extra check): {'n2_rounds': 0, 'in_a2': 0, 'identical_crux_sets': 0}.

## 2. Cost

- Session (harness list price): None; wall 0 s; harness stats None.
- ledger.csv: 2026-11-16T02:05Z | scorer N2 qwen3.8-27b v2 (6250 statements, 250 rounds; 6500 calls est.) ESTIMATE | estimate 3.407 | actual  | timeout 2400
- ledger.csv: 2026-11-16T02:16Z | scorer N2 qwen3.8-27b v2 ACTUAL | estimate  | actual 0.9332 | timeout 2400
- Container check after the run: {}

## 3. Per generator × cell descriptives (all 6,250 statements)

| generator | cell | n | n with E | parse-fail rate | zero-crux rate | mean E | share E=0 | share E=1 | mean words | over-cap rate | preamble n (rate) | truncated | think leak | refusal/meta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma4-12b | SAT-COMMON | 250 | 240 | 0.0080 | 0.0320 | 0.5535 | 0.1958 | 0.2708 | 125.8 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | SAT-DIS | 250 | 236 | 0.0080 | 0.0480 | 0.0907 | 0.7839 | 0.0212 | 126.8 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | ACC-COMMON | 250 | 230 | 0.0000 | 0.0800 | 0.3203 | 0.4391 | 0.1217 | 120.9 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | ACC-DIS | 250 | 223 | 0.0160 | 0.0920 | 0.1058 | 0.7713 | 0.0359 | 124.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| gemma4-12b | NEU-COMMON | 250 | 224 | 0.0040 | 0.1000 | 0.3017 | 0.3973 | 0.0804 | 125.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | SAT-COMMON | 250 | 223 | 0.0080 | 0.1000 | 0.5250 | 0.2287 | 0.2646 | 143.8 | 0.3000 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | SAT-DIS | 250 | 224 | 0.0040 | 0.1000 | 0.0800 | 0.8214 | 0.0179 | 146.4 | 0.3880 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | ACC-COMMON | 250 | 221 | 0.0160 | 0.1000 | 0.2839 | 0.4932 | 0.1041 | 142.5 | 0.2720 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | ACC-DIS | 250 | 224 | 0.0040 | 0.1000 | 0.1176 | 0.7232 | 0.0268 | 145.6 | 0.3520 | 0 (0.0000) | 0 | 0 | 0 |
| qwen3.8-27b (self) | NEU-COMMON | 250 | 222 | 0.0120 | 0.1000 | 0.2556 | 0.4820 | 0.0856 | 148.1 | 0.4120 | 0 (0.0000) | 0 | 0 | 0 |
| ministral3-14b | SAT-COMMON | 250 | 225 | 0.0000 | 0.1000 | 0.5633 | 0.1644 | 0.2667 | 148.9 | 0.4160 | 18 (0.0720) | 0 | 0 | 0 |
| ministral3-14b | SAT-DIS | 250 | 224 | 0.0040 | 0.1000 | 0.1034 | 0.7768 | 0.0312 | 154.9 | 0.6080 | 12 (0.0480) | 0 | 0 | 0 |
| ministral3-14b | ACC-COMMON | 250 | 224 | 0.0040 | 0.1000 | 0.3002 | 0.4643 | 0.1250 | 149.1 | 0.4000 | 16 (0.0640) | 0 | 0 | 0 |
| ministral3-14b | ACC-DIS | 250 | 223 | 0.0080 | 0.1000 | 0.1192 | 0.7578 | 0.0493 | 161.6 | 0.7240 | 0 (0.0000) | 0 | 0 | 0 |
| ministral3-14b | NEU-COMMON | 250 | 224 | 0.0040 | 0.1000 | 0.3110 | 0.4554 | 0.1295 | 148.3 | 0.4520 | 63 (0.2520) | 0 | 0 | 0 |
| phi4-14b | SAT-COMMON | 250 | 222 | 0.0120 | 0.1000 | 0.5465 | 0.2027 | 0.2658 | 126.8 | 0.0240 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | SAT-DIS | 250 | 222 | 0.0120 | 0.1000 | 0.1400 | 0.6982 | 0.0450 | 130.4 | 0.0760 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | ACC-COMMON | 250 | 225 | 0.0000 | 0.1000 | 0.3019 | 0.4400 | 0.1022 | 127.4 | 0.0400 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | ACC-DIS | 250 | 223 | 0.0080 | 0.1000 | 0.1039 | 0.7848 | 0.0314 | 137.6 | 0.1720 | 0 (0.0000) | 0 | 0 | 0 |
| phi4-14b | NEU-COMMON | 250 | 222 | 0.0120 | 0.1000 | 0.3510 | 0.3739 | 0.1441 | 129.8 | 0.0440 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | SAT-COMMON | 250 | 223 | 0.0080 | 0.1000 | 0.5344 | 0.2197 | 0.2556 | 119.4 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | SAT-DIS | 250 | 224 | 0.0040 | 0.1000 | 0.0930 | 0.7545 | 0.0089 | 117.6 | 0.0040 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | ACC-COMMON | 250 | 223 | 0.0080 | 0.1000 | 0.2859 | 0.4709 | 0.1031 | 117.5 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | ACC-DIS | 250 | 224 | 0.0040 | 0.1000 | 0.1064 | 0.7589 | 0.0312 | 115.1 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |
| llama3.1-8b | NEU-COMMON | 250 | 223 | 0.0080 | 0.1000 | 0.3438 | 0.3946 | 0.1480 | 120.6 | 0.0000 | 0 (0.0000) | 0 | 0 | 0 |

## 4. Effective n, drops and MDE (spec §5, §7, Amendment 2)

| generator | rounds | complete rounds | dropped by reason | launches (primary) | MDE d_z (α 0.05) | MDE d_z (strictest Holm α) |
|---|---|---|---|---|---|---|
| gemma4-12b | 250 | 216 | {'zero_crux': 25, 'label_parse_fail': 9} | 206 | 0.191 | 0.251 (α=0.0050) |
| qwen3.8-27b | 250 | 215 | {'zero_crux': 25, 'label_parse_fail': 10} | 205 | 0.192 | 0.251 (α=0.0050) |
| ministral3-14b | 250 | 220 | {'zero_crux': 25, 'label_parse_fail': 5} | 210 | 0.190 | 0.257 (α=0.0033) |
| phi4-14b | 250 | 214 | {'label_parse_fail': 11, 'zero_crux': 25} | 204 | 0.192 | 0.261 (α=0.0033) |
| llama3.1-8b | 250 | 217 | {'zero_crux': 25, 'label_parse_fail': 8} | 208 | 0.191 | 0.259 (α=0.0033) |

## 5. Manipulation / instrument check (spec §2; outside the Holm families)

| generator | MC estimate [95% CI] | n rounds | verdict |
|---|---|---|---|
| gemma4-12b | 0.335 [0.297, 0.373] | 216 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| qwen3.8-27b | 0.300 [0.262, 0.339] | 215 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| ministral3-14b | 0.322 [0.281, 0.361] | 220 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| phi4-14b | 0.300 [0.262, 0.336] | 214 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |
| llama3.1-8b | 0.308 [0.274, 0.343] | 217 | registers (MC > 0, launch-bootstrap 95% CI excludes 0) |

New generators failing the check: [] (rule: 2 or more of 3 failing means the paper may not say the instruction effect generalises across models). Mahajan et al. (2611.05135) is credited for the agreement-vs-differences main effect.

## 6. Pre-specified contrasts, primary analysis set (every estimate, including flat or null ones)

| generator | contrast | unadjusted est [95% CI] | p_boot | p_holm | d_z | adjusted est [95% CI] | p_boot | p_holm | n rounds | n launches |
|---|---|---|---|---|---|---|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | -0.011 [-0.055, 0.034] | 0.6827 | 1.0000 | -0.032 | -0.019 [-0.064, 0.026] | 0.4148 | 1.0000 | 216 | 206 |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.248 [0.181, 0.317] | 0.0010 | 0.0100 | 0.506 | 0.257 [0.185, 0.332] | 0.0010 | 0.0100 | 216 | 206 |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.259 [0.180, 0.342] | 0.0010 | 0.0100 | 0.423 | 0.257 [0.176, 0.342] | 0.0010 | 0.0100 | 216 | 206 |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | 0.264 [0.198, 0.328] | 0.0010 | 0.0100 | 0.543 | 0.265 [0.198, 0.329] | 0.0010 | 0.0100 | 216 | 206 |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | -0.016 [-0.072, 0.040] | 0.5987 | 1.0000 | -0.037 | -0.005 [-0.069, 0.057] | 0.8456 | 1.0000 | 216 | 206 |
| gemma4-12b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.119 [0.081, 0.158] | 0.0010 | — | 0.413 | 0.113 [0.073, 0.158] | 0.0010 | — | 216 | 206 |
| qwen3.8-27b (self) | C1_override (SAT-DIS - ACC-DIS) | -0.036 [-0.075, 0.002] | 0.0680 | 0.2719 | -0.118 | -0.039 [-0.078, -0.001] | 0.0460 | 0.1839 | 215 | 205 |
| qwen3.8-27b (self) | C2_protection (SAT-COMMON - ACC-COMMON) | 0.235 [0.167, 0.303] | 0.0010 | 0.0100 | 0.485 | 0.235 [0.166, 0.307] | 0.0010 | 0.0100 | 215 | 205 |
| qwen3.8-27b (self) | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.271 [0.196, 0.351] | 0.0010 | 0.0100 | 0.492 | 0.271 [0.195, 0.350] | 0.0010 | 0.0100 | 215 | 205 |
| qwen3.8-27b (self) | C4a (SAT-COMMON - NEU-COMMON) | 0.262 [0.199, 0.329] | 0.0010 | 0.0100 | 0.551 | 0.256 [0.193, 0.322] | 0.0010 | 0.0100 | 215 | 205 |
| qwen3.8-27b (self) | C4b (NEU-COMMON - ACC-COMMON) | -0.027 [-0.092, 0.035] | 0.4088 | 1.0000 | -0.058 | -0.029 [-0.096, 0.035] | 0.3868 | 1.0000 | 215 | 205 |
| qwen3.8-27b (self) | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.099 [0.060, 0.139] | 0.0010 | — | 0.334 | 0.096 [0.055, 0.137] | 0.0010 | — | 215 | 205 |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | -0.017 [-0.062, 0.027] | 0.4848 | 1.0000 | -0.052 | -0.007 [-0.057, 0.042] | 0.8576 | 1.0000 | 220 | 210 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.260 [0.194, 0.320] | 0.0010 | 0.0150 | 0.531 | 0.258 [0.190, 0.318] | 0.0010 | 0.0150 | 220 | 210 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.277 [0.196, 0.352] | 0.0010 | 0.0150 | 0.465 | 0.277 [0.194, 0.358] | 0.0010 | 0.0150 | 220 | 210 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.255 [0.191, 0.319] | 0.0010 | 0.0150 | 0.505 | 0.269 [0.199, 0.338] | 0.0010 | 0.0150 | 220 | 210 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.005 [-0.058, 0.068] | 0.8896 | 1.0000 | 0.011 | -0.001 [-0.068, 0.067] | 0.9735 | 1.0000 | 220 | 210 |
| ministral3-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.122 [0.081, 0.159] | 0.0010 | — | 0.424 | 0.123 [0.081, 0.162] | 0.0010 | — | 220 | 210 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | 0.035 [-0.011, 0.083] | 0.1319 | 0.6547 | 0.099 | 0.023 [-0.025, 0.072] | 0.3448 | 1.0000 | 214 | 204 |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.239 [0.170, 0.303] | 0.0010 | 0.0150 | 0.499 | 0.238 [0.170, 0.303] | 0.0010 | 0.0150 | 214 | 204 |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.204 [0.124, 0.286] | 0.0010 | 0.0150 | 0.339 | 0.215 [0.127, 0.299] | 0.0010 | 0.0150 | 214 | 204 |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.187 [0.118, 0.254] | 0.0010 | 0.0150 | 0.367 | 0.180 [0.113, 0.245] | 0.0010 | 0.0150 | 214 | 204 |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.052 [-0.013, 0.118] | 0.1309 | 0.6547 | 0.108 | 0.062 [-0.004, 0.130] | 0.0730 | 0.3648 | 214 | 204 |
| phi4-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.137 [0.097, 0.178] | 0.0010 | — | 0.464 | 0.130 [0.090, 0.170] | 0.0010 | — | 214 | 204 |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | -0.018 [-0.057, 0.019] | 0.3518 | 1.0000 | -0.062 | -0.018 [-0.057, 0.020] | 0.3428 | 1.0000 | 217 | 208 |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.252 [0.181, 0.327] | 0.0010 | 0.0150 | 0.470 | 0.248 [0.175, 0.322] | 0.0010 | 0.0150 | 217 | 208 |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.270 [0.192, 0.354] | 0.0010 | 0.0150 | 0.444 | 0.270 [0.191, 0.354] | 0.0010 | 0.0150 | 217 | 208 |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | 0.188 [0.114, 0.257] | 0.0010 | 0.0150 | 0.350 | 0.185 [0.110, 0.258] | 0.0010 | 0.0150 | 217 | 208 |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | 0.064 [0.002, 0.129] | 0.0450 | 0.2699 | 0.134 | 0.078 [0.010, 0.150] | 0.0220 | 0.1319 | 217 | 208 |
| llama3.1-8b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.117 [0.077, 0.158] | 0.0010 | — | 0.383 | 0.114 [0.073, 0.156] | 0.0010 | — | 217 | 208 |

SYS (spec §6 system effect) is a falsifier quantity, not in the Holm family. Contrast that is CI-excluding-0 in only one of the unadjusted / adjusted columns is labelled as such below (JSON `only_in_one_variant`).

### Falsifiers (spec §6), primary unadjusted

- gemma4-12b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': True}
- qwen3.8-27b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': True}
- ministral3-14b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': True}
- phi4-14b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': True}
- llama3.1-8b: {'H-N2 system effect (SYS) falsified': False, 'SAT-NEU within COMMON (C4a) falsified': False, 'override reading (C1) falsified (CI includes 0)': True}

### Labels: contrasts whose CI excludes 0 in only one variant (adjusted vs unadjusted; with vs without preambled rounds)

- qwen3.8-27b | C1_override (SAT-DIS - ACC-DIS): CI excludes 0 only in the adjusted primary analysis

## 7. Covariates (adjusted primary): slopes of the round-level difference on Δlog(words) and Δpreamble

| generator | contrast | slope Δlog(words) | slope Δpreamble |
|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | 0.426 | NA |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.220 | NA |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.147 | NA |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | -0.293 | NA |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | -0.290 | NA |
| qwen3.8-27b | C1_override (SAT-DIS - ACC-DIS) | 0.253 | NA |
| qwen3.8-27b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.023 | NA |
| qwen3.8-27b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.026 | NA |
| qwen3.8-27b | C4a (SAT-COMMON - NEU-COMMON) | -0.213 | NA |
| qwen3.8-27b | C4b (NEU-COMMON - ACC-COMMON) | 0.051 | NA |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | 0.101 | -0.122 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.044 | 0.114 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.036 | 0.085 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | -0.117 | 0.069 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | -0.186 | 0.023 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | -0.227 | NA |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | -0.231 | NA |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | -0.210 | NA |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | -0.299 | NA |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | -0.548 | NA |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | 0.020 | NA |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.223 | NA |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.022 | NA |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | -0.209 | NA |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | -0.516 | NA |

Length is labelled a possible mediator, not a confound to remove (spec §5, §9).

## 8. Sensitivity analyses (unadjusted and adjusted; every pre-specified contrast)

### excl_preamble_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 216 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.011 [-0.055, 0.034] | -0.019 [-0.064, 0.026] |
| gemma4-12b | 216 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.248 [0.181, 0.317] | 0.257 [0.185, 0.332] |
| gemma4-12b | 216 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.259 [0.180, 0.342] | 0.257 [0.176, 0.342] |
| gemma4-12b | 216 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.264 [0.198, 0.328] | 0.265 [0.198, 0.329] |
| gemma4-12b | 216 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | -0.016 [-0.072, 0.040] | -0.005 [-0.069, 0.057] |
| gemma4-12b | 216 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.335 [0.297, 0.373] | 0.336 [0.295, 0.378] |
| gemma4-12b | 216 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.119 [0.081, 0.158] | 0.113 [0.073, 0.158] |
| qwen3.8-27b | 215 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.036 [-0.075, 0.002] | -0.039 [-0.078, -0.001] |
| qwen3.8-27b | 215 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.235 [0.167, 0.303] | 0.235 [0.166, 0.307] |
| qwen3.8-27b | 215 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.271 [0.196, 0.351] | 0.271 [0.195, 0.350] |
| qwen3.8-27b | 215 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.262 [0.199, 0.329] | 0.256 [0.193, 0.322] |
| qwen3.8-27b | 215 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | -0.027 [-0.092, 0.035] | -0.029 [-0.096, 0.035] |
| qwen3.8-27b | 215 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.262, 0.339] | 0.306 [0.268, 0.345] |
| qwen3.8-27b | 215 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.099 [0.060, 0.139] | 0.096 [0.055, 0.137] |
| ministral3-14b | 131 (89) | False | C1_override (SAT-DIS - ACC-DIS) | -0.023 [-0.076, 0.030] | -0.022 [-0.080, 0.036] |
| ministral3-14b | 131 (89) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.253 [0.170, 0.334] | 0.252 [0.167, 0.334] |
| ministral3-14b | 131 (89) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.275 [0.181, 0.367] | 0.273 [0.171, 0.371] |
| ministral3-14b | 131 (89) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.250 [0.163, 0.335] | 0.253 [0.166, 0.338] |
| ministral3-14b | 131 (89) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.003 [-0.079, 0.087] | -0.001 [-0.082, 0.083] |
| ministral3-14b | 131 (89) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.339 [0.291, 0.387] | 0.350 [0.297, 0.401] |
| ministral3-14b | 131 (89) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.115 [0.063, 0.166] | 0.116 [0.064, 0.167] |
| phi4-14b | 214 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.035 [-0.011, 0.083] | 0.023 [-0.025, 0.072] |
| phi4-14b | 214 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.239 [0.170, 0.303] | 0.238 [0.170, 0.303] |
| phi4-14b | 214 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.204 [0.124, 0.286] | 0.215 [0.127, 0.299] |
| phi4-14b | 214 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.187 [0.118, 0.254] | 0.180 [0.113, 0.245] |
| phi4-14b | 214 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.052 [-0.013, 0.118] | 0.062 [-0.004, 0.130] |
| phi4-14b | 214 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.262, 0.336] | 0.296 [0.258, 0.334] |
| phi4-14b | 214 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.137 [0.097, 0.178] | 0.130 [0.090, 0.170] |
| llama3.1-8b | 217 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.018 [-0.057, 0.019] | -0.018 [-0.057, 0.020] |
| llama3.1-8b | 217 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.252 [0.181, 0.327] | 0.248 [0.175, 0.322] |
| llama3.1-8b | 217 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.270 [0.192, 0.354] | 0.270 [0.191, 0.354] |
| llama3.1-8b | 217 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.188 [0.114, 0.257] | 0.185 [0.110, 0.258] |
| llama3.1-8b | 217 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.064 [0.002, 0.129] | 0.078 [0.010, 0.150] |
| llama3.1-8b | 217 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.308 [0.274, 0.343] | 0.309 [0.275, 0.344] |
| llama3.1-8b | 217 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.117 [0.077, 0.158] | 0.114 [0.073, 0.156] |

### excl_any_flagged_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 216 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.011 [-0.055, 0.034] | -0.019 [-0.064, 0.026] |
| gemma4-12b | 216 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.248 [0.181, 0.317] | 0.257 [0.185, 0.332] |
| gemma4-12b | 216 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.259 [0.180, 0.342] | 0.257 [0.176, 0.342] |
| gemma4-12b | 216 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.264 [0.198, 0.328] | 0.265 [0.198, 0.329] |
| gemma4-12b | 216 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | -0.016 [-0.072, 0.040] | -0.005 [-0.069, 0.057] |
| gemma4-12b | 216 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.335 [0.297, 0.373] | 0.336 [0.295, 0.378] |
| gemma4-12b | 216 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.119 [0.081, 0.158] | 0.113 [0.073, 0.158] |
| qwen3.8-27b | 215 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.036 [-0.075, 0.002] | -0.039 [-0.078, -0.001] |
| qwen3.8-27b | 215 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.235 [0.167, 0.303] | 0.235 [0.166, 0.307] |
| qwen3.8-27b | 215 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.271 [0.196, 0.351] | 0.271 [0.195, 0.350] |
| qwen3.8-27b | 215 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.262 [0.199, 0.329] | 0.256 [0.193, 0.322] |
| qwen3.8-27b | 215 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | -0.027 [-0.092, 0.035] | -0.029 [-0.096, 0.035] |
| qwen3.8-27b | 215 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.262, 0.339] | 0.306 [0.268, 0.345] |
| qwen3.8-27b | 215 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.099 [0.060, 0.139] | 0.096 [0.055, 0.137] |
| ministral3-14b | 131 (89) | False | C1_override (SAT-DIS - ACC-DIS) | -0.023 [-0.076, 0.030] | -0.022 [-0.080, 0.036] |
| ministral3-14b | 131 (89) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.253 [0.170, 0.334] | 0.252 [0.167, 0.334] |
| ministral3-14b | 131 (89) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.275 [0.181, 0.367] | 0.273 [0.171, 0.371] |
| ministral3-14b | 131 (89) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.250 [0.163, 0.335] | 0.253 [0.166, 0.338] |
| ministral3-14b | 131 (89) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.003 [-0.079, 0.087] | -0.001 [-0.082, 0.083] |
| ministral3-14b | 131 (89) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.339 [0.291, 0.387] | 0.350 [0.297, 0.401] |
| ministral3-14b | 131 (89) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.115 [0.063, 0.166] | 0.116 [0.064, 0.167] |
| phi4-14b | 214 (0) | True | C1_override (SAT-DIS - ACC-DIS) | 0.035 [-0.011, 0.083] | 0.023 [-0.025, 0.072] |
| phi4-14b | 214 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.239 [0.170, 0.303] | 0.238 [0.170, 0.303] |
| phi4-14b | 214 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.204 [0.124, 0.286] | 0.215 [0.127, 0.299] |
| phi4-14b | 214 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.187 [0.118, 0.254] | 0.180 [0.113, 0.245] |
| phi4-14b | 214 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.052 [-0.013, 0.118] | 0.062 [-0.004, 0.130] |
| phi4-14b | 214 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.262, 0.336] | 0.296 [0.258, 0.334] |
| phi4-14b | 214 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.137 [0.097, 0.178] | 0.130 [0.090, 0.170] |
| llama3.1-8b | 217 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.018 [-0.057, 0.019] | -0.018 [-0.057, 0.020] |
| llama3.1-8b | 217 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.252 [0.181, 0.327] | 0.248 [0.175, 0.322] |
| llama3.1-8b | 217 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.270 [0.192, 0.354] | 0.270 [0.191, 0.354] |
| llama3.1-8b | 217 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.188 [0.114, 0.257] | 0.185 [0.110, 0.258] |
| llama3.1-8b | 217 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | 0.064 [0.002, 0.129] | 0.078 [0.010, 0.150] |
| llama3.1-8b | 217 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.308 [0.274, 0.343] | 0.309 [0.275, 0.344] |
| llama3.1-8b | 217 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.117 [0.077, 0.158] | 0.114 [0.073, 0.156] |

### under_cap_all_cells_le_150w

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 216 (0) | True | C1_override (SAT-DIS - ACC-DIS) | -0.011 [-0.055, 0.034] | -0.019 [-0.064, 0.026] |
| gemma4-12b | 216 (0) | True | C2_protection (SAT-COMMON - ACC-COMMON) | 0.248 [0.181, 0.317] | 0.257 [0.185, 0.332] |
| gemma4-12b | 216 (0) | True | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.259 [0.180, 0.342] | 0.257 [0.176, 0.342] |
| gemma4-12b | 216 (0) | True | C4a (SAT-COMMON - NEU-COMMON) | 0.264 [0.198, 0.328] | 0.265 [0.198, 0.329] |
| gemma4-12b | 216 (0) | True | C4b (NEU-COMMON - ACC-COMMON) | -0.016 [-0.072, 0.040] | -0.005 [-0.069, 0.057] |
| gemma4-12b | 216 (0) | True | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.335 [0.297, 0.373] | 0.336 [0.295, 0.378] |
| gemma4-12b | 216 (0) | True | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.119 [0.081, 0.158] | 0.113 [0.073, 0.158] |
| qwen3.8-27b | 33 (182) | False | C1_override (SAT-DIS - ACC-DIS) | -0.038 [-0.146, 0.056] | -0.026 [-0.125, 0.059] |
| qwen3.8-27b | 33 (182) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.301 [0.136, 0.470] | 0.306 [0.129, 0.475] |
| qwen3.8-27b | 33 (182) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.338 [0.154, 0.525] | 0.337 [0.150, 0.533] |
| qwen3.8-27b | 33 (182) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.250 [0.086, 0.409] | 0.236 [0.072, 0.391] |
| qwen3.8-27b | 33 (182) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.051 [-0.119, 0.220] | 0.091 [-0.095, 0.246] |
| qwen3.8-27b | 33 (182) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.247 [0.143, 0.345] | 0.254 [0.151, 0.357] |
| qwen3.8-27b | 33 (182) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.131 [0.023, 0.234] | 0.148 [0.046, 0.241] |
| ministral3-14b | 7 (213) | False | C1_override (SAT-DIS - ACC-DIS) | -0.060 [-0.215, 0.083] | 0.052 [-0.055, 0.165] |
| ministral3-14b | 7 (213) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.345 [0.023, 0.714] | 0.392 [-0.129, 0.902] |
| ministral3-14b | 7 (213) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.405 [0.023, 0.810] | 0.373 [-0.117, 0.931] |
| ministral3-14b | 7 (213) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.321 [0.024, 0.595] | 0.343 [0.144, 0.778] |
| ministral3-14b | 7 (213) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.024 [-0.274, 0.286] | -0.036 [-1.277, 0.347] |
| ministral3-14b | 7 (213) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.298 [0.018, 0.595] | 0.133 [-0.023, 0.411] |
| ministral3-14b | 7 (213) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.143 [-0.054, 0.339] | 0.189 [-0.035, 0.570] |
| phi4-14b | 150 (64) | False | C1_override (SAT-DIS - ACC-DIS) | 0.014 [-0.044, 0.068] | -0.005 [-0.060, 0.046] |
| phi4-14b | 150 (64) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.264 [0.195, 0.335] | 0.264 [0.195, 0.336] |
| phi4-14b | 150 (64) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.249 [0.161, 0.345] | 0.254 [0.162, 0.352] |
| phi4-14b | 150 (64) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.193 [0.112, 0.269] | 0.182 [0.100, 0.261] |
| phi4-14b | 150 (64) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.071 [-0.005, 0.148] | 0.080 [0.003, 0.157] |
| phi4-14b | 150 (64) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.296 [0.249, 0.344] | 0.288 [0.242, 0.335] |
| phi4-14b | 150 (64) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.139 [0.095, 0.183] | 0.130 [0.085, 0.177] |
| llama3.1-8b | 216 (1) | False | C1_override (SAT-DIS - ACC-DIS) | -0.018 [-0.058, 0.019] | -0.018 [-0.060, 0.019] |
| llama3.1-8b | 216 (1) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.251 [0.180, 0.326] | 0.247 [0.176, 0.322] |
| llama3.1-8b | 216 (1) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.269 [0.189, 0.354] | 0.269 [0.189, 0.354] |
| llama3.1-8b | 216 (1) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.186 [0.116, 0.256] | 0.184 [0.113, 0.257] |
| llama3.1-8b | 216 (1) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.064 [0.001, 0.129] | 0.078 [0.009, 0.150] |
| llama3.1-8b | 216 (1) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.308 [0.275, 0.342] | 0.310 [0.274, 0.344] |
| llama3.1-8b | 216 (1) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.116 [0.077, 0.159] | 0.114 [0.073, 0.154] |

### excl_dev_launch_rounds

| generator | n rounds (dropped vs primary) | identical to primary | contrast | unadjusted [95% CI] | adjusted [95% CI] |
|---|---|---|---|---|---|
| gemma4-12b | 179 (37) | False | C1_override (SAT-DIS - ACC-DIS) | -0.002 [-0.049, 0.045] | -0.010 [-0.058, 0.038] |
| gemma4-12b | 179 (37) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.235 [0.166, 0.309] | 0.235 [0.154, 0.317] |
| gemma4-12b | 179 (37) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.237 [0.154, 0.326] | 0.230 [0.146, 0.321] |
| gemma4-12b | 179 (37) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.257 [0.187, 0.330] | 0.258 [0.187, 0.333] |
| gemma4-12b | 179 (37) | False | C4b (NEU-COMMON - ACC-COMMON) | -0.022 [-0.087, 0.041] | -0.007 [-0.078, 0.062] |
| gemma4-12b | 179 (37) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.348 [0.308, 0.390] | 0.350 [0.307, 0.394] |
| gemma4-12b | 179 (37) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.117 [0.076, 0.160] | 0.115 [0.068, 0.164] |
| qwen3.8-27b | 180 (35) | False | C1_override (SAT-DIS - ACC-DIS) | -0.029 [-0.069, 0.015] | -0.031 [-0.071, 0.013] |
| qwen3.8-27b | 180 (35) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.256 [0.185, 0.329] | 0.255 [0.181, 0.329] |
| qwen3.8-27b | 180 (35) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.285 [0.203, 0.370] | 0.285 [0.205, 0.373] |
| qwen3.8-27b | 180 (35) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.279 [0.208, 0.349] | 0.271 [0.198, 0.343] |
| qwen3.8-27b | 180 (35) | False | C4b (NEU-COMMON - ACC-COMMON) | -0.023 [-0.088, 0.043] | -0.030 [-0.103, 0.041] |
| qwen3.8-27b | 180 (35) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.310 [0.269, 0.352] | 0.319 [0.280, 0.360] |
| qwen3.8-27b | 180 (35) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.114 [0.071, 0.159] | 0.110 [0.067, 0.155] |
| ministral3-14b | 182 (38) | False | C1_override (SAT-DIS - ACC-DIS) | -0.003 [-0.055, 0.048] | 0.010 [-0.046, 0.065] |
| ministral3-14b | 182 (38) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.263 [0.190, 0.332] | 0.258 [0.185, 0.326] |
| ministral3-14b | 182 (38) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.266 [0.181, 0.353] | 0.263 [0.173, 0.352] |
| ministral3-14b | 182 (38) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.258 [0.184, 0.332] | 0.276 [0.197, 0.356] |
| ministral3-14b | 182 (38) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.005 [-0.065, 0.076] | -0.015 [-0.092, 0.063] |
| ministral3-14b | 182 (38) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.321 [0.279, 0.364] | 0.323 [0.275, 0.372] |
| ministral3-14b | 182 (38) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.130 [0.086, 0.173] | 0.129 [0.083, 0.174] |
| phi4-14b | 180 (34) | False | C1_override (SAT-DIS - ACC-DIS) | 0.036 [-0.015, 0.085] | 0.023 [-0.030, 0.075] |
| phi4-14b | 180 (34) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.266 [0.198, 0.332] | 0.265 [0.197, 0.331] |
| phi4-14b | 180 (34) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.231 [0.147, 0.321] | 0.240 [0.153, 0.334] |
| phi4-14b | 180 (34) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.186 [0.114, 0.259] | 0.179 [0.107, 0.253] |
| phi4-14b | 180 (34) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.081 [0.015, 0.148] | 0.093 [0.024, 0.159] |
| phi4-14b | 180 (34) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.295 [0.253, 0.336] | 0.290 [0.248, 0.330] |
| phi4-14b | 180 (34) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.151 [0.112, 0.191] | 0.142 [0.102, 0.184] |
| llama3.1-8b | 179 (38) | False | C1_override (SAT-DIS - ACC-DIS) | -0.022 [-0.067, 0.023] | -0.021 [-0.066, 0.026] |
| llama3.1-8b | 179 (38) | False | C2_protection (SAT-COMMON - ACC-COMMON) | 0.232 [0.154, 0.312] | 0.224 [0.144, 0.304] |
| llama3.1-8b | 179 (38) | False | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.254 [0.161, 0.344] | 0.254 [0.158, 0.344] |
| llama3.1-8b | 179 (38) | False | C4a (SAT-COMMON - NEU-COMMON) | 0.174 [0.098, 0.249] | 0.172 [0.095, 0.251] |
| llama3.1-8b | 179 (38) | False | C4b (NEU-COMMON - ACC-COMMON) | 0.059 [-0.014, 0.128] | 0.070 [-0.010, 0.151] |
| llama3.1-8b | 179 (38) | False | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.298 [0.261, 0.339] | 0.298 [0.258, 0.338] |
| llama3.1-8b | 179 (38) | False | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.105 [0.062, 0.149] | 0.101 [0.057, 0.145] |

### Rank-based check for C3 (Wilcoxon signed-rank, round level; spec §5)

| generator | statistic | p | n nonzero / n |
|---|---|---|---|
| gemma4-12b | 4716.0 | 0.0000 | 188 / 216 |
| qwen3.8-27b | 3569.5 | 0.0000 | 181 / 215 |
| ministral3-14b | 4033.0 | 0.0000 | 190 / 220 |
| phi4-14b | 5235.5 | 0.0000 | 186 / 214 |
| llama3.1-8b | 4623.0 | 0.0000 | 192 / 217 |

## 9. C5 baseline (descriptive): cell E minus mean E of the round's iteration-0 HM candidates (A2 v2 scores)

| generator | cell | est [95% CI] | n rounds |
|---|---|---|---|
| gemma4-12b | SAT-COMMON | -0.415 [-0.476, -0.357] | 155 |
| gemma4-12b | SAT-DIS | -0.878 [-0.911, -0.844] | 155 |
| gemma4-12b | ACC-COMMON | -0.662 [-0.713, -0.606] | 155 |
| gemma4-12b | ACC-DIS | -0.865 [-0.901, -0.823] | 155 |
| gemma4-12b | NEU-COMMON | -0.656 [-0.706, -0.606] | 155 |
| qwen3.8-27b | SAT-COMMON | -0.434 [-0.496, -0.373] | 156 |
| qwen3.8-27b | SAT-DIS | -0.892 [-0.922, -0.859] | 156 |
| qwen3.8-27b | ACC-COMMON | -0.679 [-0.727, -0.630] | 156 |
| qwen3.8-27b | ACC-DIS | -0.846 [-0.884, -0.803] | 156 |
| qwen3.8-27b | NEU-COMMON | -0.688 [-0.740, -0.633] | 156 |
| ministral3-14b | SAT-COMMON | -0.404 [-0.460, -0.345] | 162 |
| ministral3-14b | SAT-DIS | -0.862 [-0.898, -0.821] | 162 |
| ministral3-14b | ACC-COMMON | -0.662 [-0.716, -0.604] | 162 |
| ministral3-14b | ACC-DIS | -0.857 [-0.895, -0.817] | 162 |
| ministral3-14b | NEU-COMMON | -0.676 [-0.725, -0.622] | 162 |
| phi4-14b | SAT-COMMON | -0.452 [-0.507, -0.397] | 157 |
| phi4-14b | SAT-DIS | -0.823 [-0.865, -0.780] | 157 |
| phi4-14b | ACC-COMMON | -0.667 [-0.719, -0.613] | 157 |
| phi4-14b | ACC-DIS | -0.864 [-0.903, -0.820] | 157 |
| phi4-14b | NEU-COMMON | -0.616 [-0.670, -0.558] | 157 |
| llama3.1-8b | SAT-COMMON | -0.440 [-0.500, -0.380] | 161 |
| llama3.1-8b | SAT-DIS | -0.862 [-0.896, -0.828] | 161 |
| llama3.1-8b | ACC-COMMON | -0.675 [-0.731, -0.620] | 161 |
| llama3.1-8b | ACC-DIS | -0.873 [-0.905, -0.840] | 161 |
| llama3.1-8b | NEU-COMMON | -0.629 [-0.684, -0.574] | 161 |

## 10. Pooled over 5 generators — DESCRIPTIVE ONLY, not tested (intersection: 185 rounds, 176 launches)

| contrast | paired mean over generators [95% CI] | mixed model unadjusted [95% model CI] | interaction χ²(4) p | mixed model adjusted [95% model CI] | interaction χ²(4) p |
|---|---|---|---|---|---|
| C1_override (SAT-DIS - ACC-DIS) | -0.012 [-0.033, 0.009] | -0.012 [-0.039, 0.015] | 0.3839 | -0.015 [-0.036, 0.007] | 0.2794 |
| C2_protection (SAT-COMMON - ACC-COMMON) | 0.238 [0.206, 0.272] | 0.238 [0.211, 0.265] | 0.3957 | 0.237 [0.204, 0.270] | 0.5228 |
| C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.250 [0.213, 0.288] | 0.250 [0.212, 0.288] | 0.6018 | 0.252 [0.213, 0.291] | 0.6747 |
| C4a (SAT-COMMON - NEU-COMMON) | 0.218 [0.187, 0.251] | 0.218 [0.191, 0.245] | 0.0974 | 0.219 [0.188, 0.251] | 0.1612 |
| C4b (NEU-COMMON - ACC-COMMON) | 0.020 [-0.011, 0.050] | 0.020 [-0.007, 0.047] | 0.0931 | 0.018 [-0.013, 0.049] | 0.0789 |
| MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.305 [0.287, 0.323] | 0.305 [0.286, 0.324] | 0.5060 | 0.304 [0.286, 0.322] | 0.3930 |
| SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.113 [0.093, 0.133] | 0.113 [0.094, 0.132] | 0.2396 | 0.111 [0.091, 0.131] | 0.1883 |

Mixed model fitted by: unadjusted — statsmodels MixedLM (REML, optimiser REML): random intercept launch + variance component round within launch (converged True); adjusted — FALLBACK launch-cluster-robust OLS (MixedLM failed or did not converge; stated per spec 4) (converged False). Adjusted covariate coefficients: {'lw_0': {'est': -0.09291022833820277, 'se': 0.13562159588295214}, 'lw_1': {'est': 0.2689622824854549, 'se': 0.10697987752909503}, 'lw_2': {'est': 0.04339883925316154, 'se': 0.08497159926123278}, 'lw_3': {'est': -0.15976106716285218, 'se': 0.10123404664636074}, 'lw_4': {'est': 0.08583512453028136, 'se': 0.11832285875794653}, 'pre': {'est': 0.009314387014121484, 'se': 0.041850588629451166}}. Per-generator model-based estimates are in the JSON.

## 11. Exploratory-extra (NOT in the spec; separate)

Wild cluster bootstrap-t (FR §7 method of record for the A2 family; B = 2000, seed 20261115) for the primary unadjusted contrasts:

| generator | contrast | est [95% CI] | p (bootstrap-t) |
|---|---|---|---|
| gemma4-12b | C1_override (SAT-DIS - ACC-DIS) | -0.011 [-0.055, 0.035] | 0.6402 |
| gemma4-12b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.248 [0.185, 0.313] | 0.0005 |
| gemma4-12b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.259 [0.179, 0.344] | 0.0005 |
| gemma4-12b | C4a (SAT-COMMON - NEU-COMMON) | 0.264 [0.199, 0.327] | 0.0005 |
| gemma4-12b | C4b (NEU-COMMON - ACC-COMMON) | -0.016 [-0.071, 0.040] | 0.5822 |
| gemma4-12b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.335 [0.297, 0.372] | 0.0005 |
| gemma4-12b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.119 [0.083, 0.160] | 0.0005 |
| qwen3.8-27b | C1_override (SAT-DIS - ACC-DIS) | -0.036 [-0.074, 0.003] | 0.0690 |
| qwen3.8-27b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.235 [0.167, 0.302] | 0.0005 |
| qwen3.8-27b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.271 [0.193, 0.346] | 0.0005 |
| qwen3.8-27b | C4a (SAT-COMMON - NEU-COMMON) | 0.262 [0.197, 0.324] | 0.0005 |
| qwen3.8-27b | C4b (NEU-COMMON - ACC-COMMON) | -0.027 [-0.089, 0.034] | 0.3853 |
| qwen3.8-27b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.260, 0.341] | 0.0005 |
| qwen3.8-27b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.099 [0.059, 0.137] | 0.0005 |
| ministral3-14b | C1_override (SAT-DIS - ACC-DIS) | -0.017 [-0.060, 0.028] | 0.4473 |
| ministral3-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.260 [0.196, 0.326] | 0.0005 |
| ministral3-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.277 [0.201, 0.355] | 0.0005 |
| ministral3-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.255 [0.190, 0.323] | 0.0005 |
| ministral3-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.005 [-0.058, 0.069] | 0.8711 |
| ministral3-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.322 [0.284, 0.362] | 0.0005 |
| ministral3-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.122 [0.082, 0.162] | 0.0005 |
| phi4-14b | C1_override (SAT-DIS - ACC-DIS) | 0.035 [-0.013, 0.083] | 0.1604 |
| phi4-14b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.239 [0.177, 0.303] | 0.0005 |
| phi4-14b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.204 [0.123, 0.288] | 0.0005 |
| phi4-14b | C4a (SAT-COMMON - NEU-COMMON) | 0.187 [0.121, 0.258] | 0.0005 |
| phi4-14b | C4b (NEU-COMMON - ACC-COMMON) | 0.052 [-0.009, 0.115] | 0.1089 |
| phi4-14b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.300 [0.261, 0.337] | 0.0005 |
| phi4-14b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.137 [0.098, 0.176] | 0.0005 |
| llama3.1-8b | C1_override (SAT-DIS - ACC-DIS) | -0.018 [-0.057, 0.021] | 0.3793 |
| llama3.1-8b | C2_protection (SAT-COMMON - ACC-COMMON) | 0.252 [0.177, 0.326] | 0.0005 |
| llama3.1-8b | C3_interaction ((SAT-C - SAT-D) - (ACC-C - ACC-D)) | 0.270 [0.187, 0.353] | 0.0005 |
| llama3.1-8b | C4a (SAT-COMMON - NEU-COMMON) | 0.188 [0.115, 0.256] | 0.0005 |
| llama3.1-8b | C4b (NEU-COMMON - ACC-COMMON) | 0.064 [0.002, 0.126] | 0.0435 |
| llama3.1-8b | MC_manipulation ((SAT-C + ACC-C) - (SAT-D + ACC-D))/2 | 0.308 [0.273, 0.342] | 0.0005 |
| llama3.1-8b | SYS_system_effect ((SAT-C - ACC-C) + (SAT-D - ACC-D))/2 | 0.117 [0.074, 0.157] | 0.0005 |

## 12. Files

- per-cell table (CSV): `analysis\testout\n2_dummy\out\n2_cells.csv`
- all estimates (CSV): `analysis\testout\n2_dummy\out\n2_estimates.csv`
- full results (JSON): `analysis\testout\n2_dummy\out\n2_results__20261116T022126689679Z.json`

Implementation choices where the spec is silent are listed in the docstring of `analysis/n2_analysis.py` and in the JSON `implementation_choices`.
