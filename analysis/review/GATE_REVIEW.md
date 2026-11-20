# Gate 1 (R5) independent review — FROZEN_RULES §6.R5.6

Reviewer: Opus gate reviewer, 2026-11-16. Read-only on everything except `analysis\review\`.
No rank column was read. `GATE1_RESULT.json` was not written (it does not exist).

## Verdict: **AGREE** — computed status `VALIDATED_PRESENCE` (step 2 = PASS; step 3 = NOT DONE by D51)

## 1. Step 2 re-derived from raw files

Script: `analysis\review\rederive_step2.py` (written from §2, §3, §6.R5.1 text; does not import
`step2_reference.py`; I read the reference only afterwards, to explain one appendix-only gap).
Output: `analysis\review\rederive_step2_out.json`, per-round `analysis\review\rederive_step2_rounds.csv`.

Inputs: `hm_all_candidate_comparisons.parquet` (SHA-256 re-checked = `7cf8d5ce…e4a4`, columns
launch_id, round_id, iteration_index, metadata.provenance, own_opinion participant_id/provenance,
question.id only); `hm_all_position_statement_ratings.parquet` (`b6debcb3…7255763`); round list from
`a2_long_shuffled.parquet` columns launch_id, round_id only; development launches from
`pilots\T3_1\pilot_groups.jsonl` (`085d7847…8daa`, = scorer_manifest); `a2_extractions_v2.jsonl`
(`9dddc782ccab6d3d591130bac42d2c502a8c7accd2babbbf3be2cf06e9fea086`).
Bootstrap: clusters in sorted order, `rng.integers(0, K, K)` per resample, `np.percentile` 2.5/97.5.

| Quantity | Re-derived | STEP2_computed | Match |
|---|---|---|---|
| Rounds in (A2 table minus 150 dev launches) | 1,622 (721 launches) | 1,622 | exact |
| Dropped for context length | 0 | 0 | exact |
| Unusable (q not unique / rating coverage) | 0 / 0 | 0 | exact |
| Duplicate rating keys | 0 | — | (feasibility said 0) |
| Extraction missing → wrong call | 3 | 3 | exact |
| Cruxes with an empty side after re-sanitising | 0 | — | — |
| Usable rounds / launches | 1,622 / 721 | 1,622 / 721 | exact |
| Hsplit = 0: rounds / launches | 614 / 437 | 614 / 437 | exact |
| Hsplit = 1: rounds / launches | 1,008 / 605 | 1,008 / 605 | exact |
| TP / FN / TN / FP | 907 / 101 / 297 / 317 | 907 / 101 / 297 / 317 | exact |
| **BA2** | **0.6917574711752237** | 0.6917574711752237 | exact |
| sens / spec | 0.8998015873015873 / 0.4837133550488599 | same | exact |
| Launch bootstrap (seed 20261141, K = 721) LB / UB | 0.6689521057995578 / 0.7140082337979413 | same | exact |
| Question in >1 launch | true (1,259 questions) | true | exact |
| Question bootstrap (seed 20261142, K = 1,259) LB / UB | 0.6699079258128309 / 0.7133818132887074 | same | exact |
| Single-class resamples (launch / question) | 0 / 0 | 0 / 0 | exact |
| Deciding LB (min) | 0.6689521057995578 | 0.6689521057995578 | exact |
| Usability (≥200 rounds/≥100 launches; each class ≥50/≥25; ≤1% one-class) | met | met | — |
| **Outcome** | **PASS** (LB > 0.5 and BA2 ≥ 0.60) | PASS | exact |
| Prevalence Hsplit / Sdis | 0.6214549938347719 / 0.7546239210850801 | same | exact |
| BA2, n_rated = 5 (1,422 rounds) | 0.6811456111209182 | same | exact |
| BA2, all rated | 0.6929251565615202 | same | exact |
| BA2, strong split | 0.6265131746435846 | same | exact |
| Spearman(crux count, SD of member values) | 0.40314027 | 0.40314815 | Δ 7.9e-6 (appendix, no rule) |
| Context-drop share | 0.0 | 0.0 | exact |

Rating tokens seen on members (all 7 valid, no MOCK): STRONGLY_DISAGREE 1,044; DISAGREE 987;
SOMEWHAT_DISAGREE 768; NEUTRAL 909; SOMEWHAT_AGREE 1,251; AGREE 1,614; STRONGLY_AGREE 1,333.

**Spearman gap explained** (`analysis\review\sd_ties.py`): the code of record sets missing extractions to
0 cruxes and uses `np.std`, which splits the 86 mathematically distinct SD values into 116 floats, so
Spearman's tie handling depends on member order. With exact ties and the record's missing→0 convention
the value is 0.40284; with missing rounds excluded, 0.40314. All variants lie within 3.2e-4.
Appendix-only, no rule; does not affect the outcome.

## 2. Freeze, labels, hashes, clock (`analysis\review\check_freeze.py`)

| Check | Finding |
|---|---|
| Freeze before step 2 | FREEZE.json `frozen_utc` 01:53:53.642Z, mtime 01:53:53.691Z; STEP2_computed and rounds CSV mtime 01:53:55.740Z; gate1_r5_computed 01:54:04.931Z. Order correct. (Whether no rating value was read before 01:53:53 cannot be checked from files.) |
| Single run | Exactly one `STEP2_computed__*` and one `gate1_r5_computed__*`; no GATE1_RESULT.json. |
| labels\ at freeze | FREEZE.json `label_files` {}, `first_label_file` null. |
| labels\ now | Directory listing (hidden included): empty. `author_verification.csv` absent. |
| FREEZE hashes | 29 entries recomputed (8 `files` + 21 `r5_manifest_files`): **0 mismatches**. R5_FREEZE_MANIFEST paths = FREEZE `r5_manifest_files` keys exactly. FROZEN_RULES.md = `ea9b7a97…94ae` and read-only. step2_reference.py = `47486cf0…3f76` = STEP2 `script_sha256`. |
| Clock | T_READY.txt = `2026-11-16T01:23Z` → T_cut 01:53Z. No author file at T_cut or now; gate1_r5 computed at 01:54:04Z ≥ T_cut → state NOT_DONE → step 3 "NOT DONE (no author file by T_cut)". Correct per the D51 table. |

## 3. Status mapping (§6.R5.6)

Step 2 = PASS and step 3 NOT DONE by D51 → row VALIDATED_PRESENCE ("step 2 = PASS and (step 3 ∈
{INCONCLUSIVE, UNUSABLE} or step 3 NOT DONE by D51)"). Not FAIL (step 2 not FAIL), not
EXPLORATORY_UNVALIDATED (step 2 is PASS and step 3 is not CONTRADICTED), not VALIDATED_BOTH/HIDE_EVIDENCE
(need step 3 ON_TIME). **Correct.**

## 4. Defects and observations (none changes the status)

1. **Step-2 scorer input not hashed.** `a2_extractions_v2.jsonl` (the Sdis source) is in neither
   FREEZE.json nor STEP2_computed, and its hash appears in no project json/md. Its mtime
   (2026-11-15T19:06:57Z) predates the freeze. Hash recorded here: `9dddc782…e9fea086`. Recommend adding
   input hashes (extractions, ratings parquet, A2 table) to the GATE1_RESULT record.
2. **Spearman tie handling** (above): `np.std` float noise breaks ties; round SDs before ranking. Appendix only.
3. **Strong-split variant** in the code of record scores a missing extraction as `1 − hsplit`, not
   `1 − hsplit_strong`. No numeric effect here (values identical to 16 digits). Appendix only.
4. **Timing notes.** FROZEN_RULES.md last modified 01:24:31Z, after T_ready 01:23Z (logged in D50a as
   the T_READY/T_cut insertion); freeze and packet-manifest hashing happened after T_ready (manifest
   01:45:56Z, freeze 01:53:53Z, 54 s after T_cut). Rules permit this because no author file ever existed.
5. **Scorer script drift** (D50b): scorer.py hash differs from scorer_manifest's script hash; E1/L1 prompt
   hashes match. Already disclosed; I re-applied the empty-side sanitising rule and it removed 0 cruxes.
6. **Construct caveat stays live:** spec 0.484 means about half of groups with no on-axis split still get a
   crux. PASS is scoped to presence of disagreement only.
