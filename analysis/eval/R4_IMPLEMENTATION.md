# R4_IMPLEMENTATION.md: FROZEN_RULES [R4] clause -> code -> test

Stats coder, 2026-11-16. Synthetic, dummy and shuffled data only. No label file was read or created, `P\labels\` was never
written (it is still empty), nothing relates an erasure measure to real rankings or ratings. Tests: `test_r4.py` (new, 61 checks),
`test_all.py`, `test_r1.py`, `test_fixes.py` all PASS. Every run is a row in `analysis\RUNS.md`.

## Tier of record (item 3)

`gate1\A2_TIER_R4.json` (write-once, sha256 `4b01b418b5e7845064ea4346c65f2d296c112f97cf82612b90255bbc5c4fb5e0`), computed by
`a2_informativeness.py --kind real` on `analysis\scores\a2_long_shuffled.parquet` (ranks shuffled at build, `random.Random(777000)`;
null fits `random.Random(430000+i)`, i = 0..399), 721 launches (871 minus the 150 development launches, checked by the script):

| | R_inf | K_inf | MDE80 | tier |
|---|---|---|---|---|
| **Confirmatory set (tier of record)** | 152 | 144 | 0.0563 (SD of null beta_E 0.02012) | **INFORMATIVE** |
| Side figure, including development launches | 178 | 168 | 0.0509 (old file) | INFORMATIVE |

Thresholds 50 / 100 / 0.10 unchanged. The pre-R4 `gate1\A2_TIER.json` is kept as it was; `common.check_kind` now requires
`A2_TIER_R4.json` and does not read the old one. The disclosure that 144 was logged before this row is stored in the JSON.

## Clause map

| FR clause | Code | Test |
|---|---|---|
| s5 label schema (5 columns incl. `pass_started_utc`, 50 / 20 / 50 rows, four tokens, one timestamp per file) | `gate1.read_label_file`, `COLS`, `N_P1/N_P2` | test_r4: blank label -> INCOMPLETE, nothing filled; volunteer incomplete |
| s5 item key (`item_id,pass,kind,launch_id,round_id,cand,generator,cell,dup_of`; pass in 1, 2, vol) | `gate1.load_ctx`, `vol_labels_on_p1` | all gate scenarios use it |
| s5 first-pass labels frozen on arrival (hash vs `FREEZE.json`, vs gate-time hash) | `gate1.integrity` | test_r4: first-pass edited after gate time -> STOP / INCOMPLETE |
| 6.0 design switch by volunteer-file existence only, `DESIGN.json` write-once with sha256 + mtime of every file | `gate1.get_design`, `read_design` | test_r4: single (absent), two-human (present), incomplete volunteer keeps two-human, late volunteer stays single, DESIGN altered / deleted refused |
| 6.0 late volunteer file: descriptive table only | `gate1.late_volunteer` | test_r4: late volunteer, status and H unchanged |
| 6.2 single-labeler: self-consistency kappa, 20 repeats, cut 0.60, CI, AC1 + CI | `gate1.step_kappa`, `agree_stats`, `ac1` | test_r4 single_good, single_kfail |
| 6.2 two-human: inter-rater kappa on 50, cut 0.40, CI, AC1; self-consistency printed, no rule | `step_kappa`, `step_selfcons` | test_r4 two_good, selfcons |
| 6.2 one-hour rule for pass 2 (start time and mtime), not computed if missing or early, replaced file accepted until KAPPA.json exists, every pass-2 hash logged | `pass2_rule`, `log_pass2_seen` | test_r4: missing, too early (start), too early (mtime), replacement accepted |
| 6.2 / 6.5 PROVISIONAL state until the self-consistency kappa is recorded; flag whether PROVISIONAL real-rank output existed at pass 2 | `step_validity` status logic, `provisional_outputs_exist` | test_r4: PROVISIONAL_PASS -> PASS, records kept; pass 2 missing stays PROVISIONAL |
| 6.3 labels of record (author pass 1 / adjudicated), `adj_label` only, no ADJ in single design | `records`, `read_adj` | test_r4: ADJ missing, final_label rejected, ADJ not required in single |
| 6.4 BA vs first-pass labels (38 originals minus UNSURE), 0.5 threshold, bootstrap lower bound > 0.5; FAIL final when bound <= 0.5 | `step_validity`, `gate_frame`, `ba_block` | test_r4: BA fail -> FAIL without kappa |
| 6.4 / 6.4a also reported (BA vs volunteer's own labels, BA_crux, BA_sh, zero-crux share, scorer-v1) | `step_validity` | test_r4: fields present |
| 6.6 N2 check, one-sided Fisher p <= 0.05, `N2_VALIDATED` / provisional / NOT PASSED, pooled 12 | `gate1.fisher_p`, `step_n2check` | test_r4: 10 of 12 passes, 9 of 12 not, one class p = 1, gate FAIL -> NOT PASSED, PROVISIONAL never N2_VALIDATED |
| 6.7 headline H, Wilson CI, UNSURE bounds, conditional rate, per-annotator H, LLM H, scorer rate secondary | `gate1.headline`, `step_headline` | test_r4: headline fields; stamps PROVISIONAL / AGREEMENT_NOT_ESTABLISHED |
| 6.8 LLM annotator agreement (kappa + AC1 + CI, seed 20261134), labelled LLM, refused before the author files are saved | `step_llm`, `llm_allowed` | test_r4 |
| header: validation wording for each design | `gate1.WORDING`, written into DESIGN.json and every record | test_r4 wording check |
| 6.5 real-rank lock: tier file of record, DESIGN.json valid, PROVISIONAL_PASS only in single design (tag PROVISIONAL) | `common.check_kind`, `TIER_FILE` | test_fixes A3 block |
| s2 / 7 analysis set: development launches excluded by default; `include_dev` = sensitivity A2d, labelled | `common.restrict_confirmatory`; used in `a2_within_round.fit_models`, `n1.run`, `n4.run`, `a3.diff_run` (A3, N3); `analysis_set` field in every output | test_r4 section B |
| 7.1 tier on the confirmatory set, shuffled ranks, side figure with development launches, 871 / 721 launch check for `real` | `a2_informativeness.py` (writes `gate1\A2_TIER_R4.json`; `--include-dev` cannot write it) | test_r4 section B; real run in RUNS.md |

## Choices not fixed by FR (flag if wrong)

* `FREEZE.json` keys read by `gate1.py`: `author_pass1_mtime_utc` (ISO), `author_pass1_sha256`, optional `author_pass1_completed_sha256`.
  If the file or key is absent the one-hour rule falls back to the file's own mtime and says so in the record.
* Volunteer rows are in `item_key.csv` with `pass=vol` and `dup_of` = the author pass-1 id; pass-2 rows have `dup_of` too.
* Scores: `scores.csv` (`item_id,E,n_cruxes`, the 38 originals) and `n2check_scores.jsonl` (the 12 N2 items, same fields).
* `WAITING_PASS2` (missing or early pass 2) writes no `KAPPA.json`; an INCOMPLETE kappa is written and archived as before (G1).
* A dummy run must use `DUMMY_` directories for both labels and gate; a real run refuses them; the gate directory may never sit inside labels.
* Not built (not in this brief): `build_analysis_set.py`, scorer-2 bars (A4_BAR.json),
  the whole-confirmatory-set prevalence in the headline's secondary line. The pre-R4 `gate1\A2_TIER.json` was left in place (not renamed) and is no longer read.
* `test_r1.py` / `test_all.py` gate sections moved to `test_r4.py` because the L1/L2 schema no longer exists; the shuffled Habermas A2 / N1 checks use
  `include_dev` (their rounds are the development launches).

## Freeze and adjudication sheet (added 2026-11-16; dummy data only, `test_freeze_adj.py`, 20 checks PASS)

* `analysis\freeze.py [--root P]`: if `labels\` has any file, writes `P\FREEZE.json` once (exclusive create; UTC time, sha256 of FROZEN_RULES.md,
  EXPERIMENTS.md, scorer_manifest.json, N2_ANALYSIS_SPEC.md, every label file with mtime, `first_label_file` by earliest mtime, plus the
  `author_pass1_sha256` / `author_pass1_mtime_utc` keys gate1 reads), then `attrib +R` on FROZEN_RULES.md. Re-run: never rewrites; re-locks;
  exit 2 if FROZEN_RULES.md differs from the recorded hash. Exit 1 when `labels\` is empty.
* **Path mismatch to resolve:** FR and `gate1.py` read `P\gate1\FREEZE.json`; this was built to the brief's `P\FREEZE.json`. Run with
  `--out P\gate1\FREEZE.json` or pass `--freeze` to gate1 (not done here).
* `analysis\make_adjudication_sheet.py`: two-human only. Items where author pass-1 and volunteer labels differ (four tokens; includes SHOWS vs
  NO_DISAGREEMENT pairs, which FR 6.3 may skip, so humans may ignore those). Shows item_id (author pass-1 id), question, opinions, statement, `label_1` /
  `label_2` (annotator order shuffled per item, key in `ADJ_SHEET_KEY.json`, not for the humans). Writes `labels_build\r4\ADJ_SHEET.csv/.html`,
  `ADJ_TEMPLATE.csv` (`item_id,adj_label,reason`); humans save it as `labels\ADJ.csv`. Refuses to write in `labels\`; rejects incomplete files.
  Text comes from `volunteer_packet.csv` + `key_volunteer.json`.
