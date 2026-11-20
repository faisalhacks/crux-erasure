# Draft status (2026-11-16, results filled; D60 council edits applied)

REAL RESULTS, gate status VALIDATED_PRESENCE (gate1/GATE1_RESULT.json, rules R5; step 2 PASS, step 3 NOT DONE by the D51 time-out). Not a final layout: a human pastes into the Apart Google-Doc template and submits. Nothing was published, uploaded or submitted.

## D60 changes (report/review_editor.md, report/review_hostile.md)
- Editor edits 1-15 applied, with these adaptations: (1) new abstract kept, but the step-2 sentence stays in the binding FR 6.R5.6 scoped form, the hide/show stamp sits next to the 96% (D60 B2), and "nobody ranked these statements" was dropped to stay under 250 words; (2) robustness slot replaced by Figure B1 (appendix) plus one Results sentence; the N3 slot is KEPT until the orchestrator sends the final status; (5) the N2 sentence was not appended to the intro's last paragraph because edit 6 already puts it in Contributions; (14) worded "excluded from all confirmatory tests and reported only in labelled sensitivity analyses and side counts" (keeps the D49d.4 words); (15) Claude models filled per D60 (orchestrator Opus 5.5; agent frontmatter `model: opus` for methodologist, statistician, peer_reviewer, editor, adversary; general-purpose inherit Opus 5.5), and a HUMAN SLOT added for whether the human read the final text.
- Hostile A1: Table 1 relabelled "Called disagreeing / not disagreeing" with the footnote "includes 3 extraction failures counted as wrong" (2 in 317, 1 in 101); prose gives 315 + 2; B.2 gives 0.755 (failures counted) and 0.753 (crux-found only). A2: "three families". B2: stamp next to every 96%. B3: Methods pilot sentence now says all 1,960 rounds. B4: Zhu wording per references_verified.md item 11. B5: heading "Checks on the score"; "only step 2 is a validation". B7: Methods states the frames were not written before the gate. B8: "To our knowledge, prior work...". B9: "N4 survives Holm" replaced by "Holm-adjusted p = 0.023"; B.6 sensitivity sentence qualified. B6: panel versus scorer computed (below).
- New script `analysis/panel_vs_scorer.py` -> `analysis/panel/panel_vs_scorer.json` (sha256 0d59c349525c7a6e4e93866db5726435dc0fe18d282dee492c806e26b93c4039; RUNS.md row 2026-11-16T02:53:46Z). Reported as EXPLORATORY "LLM-vs-LLM; not human": one sentence in Results, Table B3, one clause each in Discussion and Appendix A item 5; Appendix A item 13 notes it was added after the results.
- `figures/make_real_figures.py` now draws `fig_a2_length` (Figure B1) from `figures/data/a2_length_spec.csv` (estimate +/- 1.96 CR1 SE, labelled approximate). That CSV adds a spec the earlier text did not have: length rank + log length, t = 2.46; Results, Discussion, Fig. 1 caption and Appendix A item 1 now say "five of six" adjustments fall below |t| 1.96.

## Build
- Command: `C:/Users/intel/miniconda3/python.exe -I figures/make_real_figures.py` then `C:/Users/intel/miniconda3/python.exe -I report/build/build.py --real`.
- `--real` (backup of the old build.py in `report/build/pre_edit_backup/build.py.pre_real`): no DUMMY stamp, no browser header/footer (checks.json `pages_with_file_path` = []), page numbers from CSS.
- Output: `report/build/out/DRAFT_layout.pdf`, `pg-01..17.png`, `checks.json`, `DRAFT_combined.md`, `build_log_real.txt`. `out/lengthcheck/` and `out/dummy_figs/` are stale; ignore.

## Page count (checks.json, every page PNG read by eye)
| Total pages | Body pages (before References) | Cap | Slack |
|---|---|---|---|
| 17 | 8 | 8 | about 1 line on p. 8; p. 4 ends ~8 lines early (Results heading kept with its first paragraph) |
Abstract 246 words (target 150-250). Body figures at native width (5.2, 5.4 in), Figure B1 5.7 in; text 8.5-9 pt; CIs on every estimate; no watermark.
**Warning:** the N3 sentence will push the body past 8 pages unless something is cut (about 2 lines). Candidates: the Discussion "Secondary tests and N2" paragraph, or the Methods N2 bullet.

## Remaining markers (visible text)
- `[RESULT SLOT: N3]` (40_results.md, Tier 2): orchestrator's final N3 status (D59). Then update Discussion "Holm-adjusted p = 0.023 with N3 at p = 1", B.5, Appendix A item 13, B.8 spend.
- Human-owned: author names (00_front); repository link (70_code_data); scorer/prompt release decision (Appendix A); whether the human read the final text (LLM Usage Statement).
- 0 robustness slot, 0 LABEL-DESIGN SLOT, 0 VERIFY, 0 [IF ...], 0 DUMMY stamp.

## Wording-rule check (text extracted from DRAFT_layout.pdf)
- "confirm*": 2 hits, both the D49d.4 development-launch phrase (Methods, Appendix A item 9). "detected" 0, "blind" 0, "significant" 0, "four families" 0, "single hypothesis-aware" 0, bare "own responses" 0. "survives" only in "whether β_E survives a change of scorer".
- "152": only in the counting-defect disclosure (Appendix A item 8).
- "pre-registered test; the predictor's hide/show contrast is not human-validated" on A2 (abstract, Results, Fig. 1, Table B1) and Tier 2; the 96% carries "the predictor's hide/show contrast is not human-validated". Title a question; no directional rank claim in the abstract; no panel number in the abstract.
- Panel always "supplementary; not human"; the panel-vs-scorer comparison always "EXPLORATORY, LLM-vs-LLM; not human".

## Deviations and things a reviewer should know
1. FR 6.R5.7 (editor condition 2) asked for per-status frames written before the gate; none existed. This text was written after the gate and results; disclosed in Appendix A item 13 (REDTEAM item 7).
2. The old methods draft said N2 results "without the 45 development-launch rounds are of record". Wrong: the N2 spec (sec. 1, 4) and n2_results use all 250 rounds as primary, `excl_dev_launch_rounds` is the sensitivity. Text now says so. This means development launches appear in a non-sensitivity exploratory result, which the D49d.4 phrase does not literally cover; Methods states it next to that phrase.
3. FR 6.R5.4 "panel-majority A vs scorer S": now computed by analysis/panel_vs_scorer.py under D60 (not pre-specified to run without an author file; disclosed in Appendix A item 13).
4. Milli et al. sentence and reference dropped (D49d.6). Farrow, Fish, Shandilya and Wen dropped from text and reference list for length (all still VERIFIED in refs.bib).
5. "about 0.15 of a rank position" in Results = 3 × β_E (y scale: one rank = 1/3, FR §7.1 Blind-MDE row); a derived figure, not in a results file.
6. Worked example (old B.2 HUMAN slot) dropped rather than invented; prompts referenced by file and hash instead of pasted.

## Every number in the assembled text, with its source
| Number(s) | Where | Source file |
|---|---|---|
| 721 launches; 1,622 rounds; BA2 0.692 [0.669, 0.714]; question-cluster [0.670, 0.713]; sens 0.900; spec 0.484; 2x2 907/317/101/297; classes 1,008/605 and 614/437; 3 failed extractions | Abstract, Results, Discussion, App. A | gate1/STEP2_computed__20261116T015355Z.json |
| B.2 variants 0.621, 0.755, 0.681 (1,422 rounds), 0.693, 0.627, 0.403, no context drop | App. B.2 | same file, `reported_no_rule` |
| 289/1,166 and 39/150 Hsplit=0 rounds; split +0.015 (SE 0.046) / +0.066 (SE 0.024) | Results, App. A 4 | analysis/redteam/REDTEAM.md item 4 (rt_step2.json, rt_refit.json); decisions.md D58.4 |
| T_ready 01:23Z, cut-off 01:53Z | Methods, Results | gate1/T_READY.txt; FR §6.R5.2; decisions.md D53 |
| Freeze 2026-11-16T01:53:53Z, FR SHA-256 ea9b7a97…f94ae | Methods, Code and Data | gate1/FREEZE.json |
| N2 spec hash afada117…91c0 | Methods, Code and Data | FR §7.3(c); gate1/FREEZE.json |
| scorer_manifest ed64b540…f9e; P1 prompt 9040afed… | App. B.1 | gate1/FREEZE.json; analysis/panel/panel_p1_summary.json |
| 1,960 rounds, 871 launches, 9,501 rater rows; 150 dev launches | Methods, App. A | FR §2; figures/data/counts.csv; REDTEAM.md (2) |
| 397 zero-crux, 3 extraction failures, 11 all-missing, 45 partly missing, 456 dropped; 1,166 rounds / 642 launches / 22,536 rows | Results Sample | analysis/results/RESULTS_MAIN.md (A2 note); figures/data/counts.csv; REDTEAM.md (2) |
| R_inf 150 / K_inf 142; defective 152/144; 176/166 incl. dev | Methods, Results, App. A 8 | RESULTS_MAIN.md (Tier); analysis/results/COUNTS_RECONCILE.md; figures/data/counts.csv; D57 |
| MDE80 0.056; one-way check 2.80 × 0.0218 = 0.061 ≤ 0.10 | Methods, Results, App. A 7 | gate1/A2_TIER_R4.json; RESULTS_MAIN.md |
| Coverage 96.5% (386/400) | Methods | FR §7 [R2] row |
| Panel: 20/20 format bar; 25 items; majority Q1 21 yes, Q2 12 yes; Fleiss 0.649 [0.143, 0.921], AC1 0.847; 0.570 [0.297, 0.787], AC1 0.577; pairwise raw 0.84-0.92 / 0.72-0.88; Falcon-Command κ 0.505 [−0.056, 0.884] | Results, App. B.3 | analysis/panel/panel_p1_summary.json |
| Prevalence 96.1% [95.5, 96.7] of 4,780; 3.9% [3.3, 4.5]; labels of 6,628: SIDED 82.8%, OMITTED 9.0%, BLENDED 4.9%, VISIBLE 3.2% | Abstract (96%), Results, Discussion, App. A 7 | RESULTS_MAIN.md prevalence table; figures/data/prevalence.csv |
| A2 +0.051 [+0.008, +0.095], p 0.024; β_L +0.167 [+0.158, +0.176]; β_C −0.026 [−0.035, −0.017] | Results, Discussion, Fig. 1 | RESULTS_MAIN.md; figures/data/a2_forest.csv, a2_controls.csv (A2_primary__20261116T021237469424Z.json) |
| A2b +0.0443 [+0.0002, +0.0882]; A2d +0.0532 [+0.0131, +0.0937] (1,409/775); A2e −0.0228 [−0.0519, +0.0056]; A2f +0.0561 [+0.0123, +0.1000]; A2g +0.0503 [+0.0068, +0.0942]; A2h +0.0455 [+0.0018, +0.0902]; A2i +0.0542 [+0.0082, +0.1005] (150/142); uncontrolled −0.0743 [−0.1262, −0.0239] | Results, Fig. 1, Table B1, App. A | figures/data/a2_forest.csv, a2_controls.csv; RESULTS_MAIN.md |
| Length table: t 2.34 (registered), cubic 1.82, deciles 1.72, rank 1.35, raw words 1.98 | Results, App. A 1 | REDTEAM.md item 1 (rt_refit.json); D58.1 |
| SIDED +0.053 (SE 0.022), BLENDED/OMITTED +0.028 (SE 0.026) | Results | REDTEAM.md item 2 (rt_n4.json) |
| A2b LB ≤ 0 in 7 of 40 other seeds | Results, App. A 3 | REDTEAM.md item 3 (rt_seed_sensitivity.json); D58.3 |
| Null coverage 191/200 | Results, App. A 11 | REDTEAM.md item 8 (rt_null_coverage.json) |
| Leave-3-out +0.037 (SE 0.021) | Results, App. A 7 | REDTEAM.md item 10 (rt_refit.json) |
| 40 duplicate-candidate rounds, 27 in fit, +0.054 | App. A 10 | REDTEAM.md item 12 (rt_dup_ids.json, rt_refit.json) |
| Parse-failed statements median 98 vs 87 words | App. A 11 | REDTEAM.md item 16 (rt_ranks_vs_source.json) |
| 9,501 rows equal source (integrity) | App. A 13 | REDTEAM.md (2b) (rt_ranks_vs_source.json) |
| 9 logged test runs reading the sealed file | App. A 9 | decisions.md D58.6; REDTEAM.md item 6 (RUNS rows 360-362, 389-391, 468-470) |
| N1 +0.008 [−0.002, +0.019], p 0.115, 1,042 rounds, 612 launches, 132 non-zero; N1u −0.004 [−0.013, +0.005]; N1h +0.008 [−0.002, +0.019]; g_L −0.0246 [−0.0428, −0.0063]; g_C +0.0074 [−0.0079, +0.0227]; 124 tied | Results, App. B.5 | RESULTS_MAIN.md; figures/data/n1.csv |
| N4 −0.147 [−0.252, −0.041], p 0.008, 592 launches; slopes +0.100 [+0.037, +0.163] / −0.047 [−0.131, +0.039]; 1,142 / 2,832 / 1,666 rater-rounds | Results, App. A 2, B.5 | RESULTS_MAIN.md; figures/data/tier2_forest.csv |
| N4 114 informative rounds, 106 launches, 151 minority rater-rounds | Results, Discussion | REDTEAM.md item 5 (rt_n4.json); D58.5 |
| Holm N1 0.231, N4 0.023 (m = 3, N3 at p = 1); 0.115 / 0.016 (m = 2) | Results | RESULTS_MAIN.md; figures/data/tier2_forest.csv |
| A3 0 launches; N3 713 launches, 1,607 rounds | Results, App. B.5 | RESULTS_MAIN.md; analysis/results/A3_N3_COUNTS.json |
| A4 smoke 75.4% (211/280), 57.5% (161/280), 5.36% (15/280), 27.857% (78/280) | App. A 6 | decisions.md D41, D44, D46, D47, D48 (lines 353-393) |
| N2: 168-177 rounds; MC 0.48 [0.44, 0.53], 0.57 [0.52, 0.61], 0.58 [0.53, 0.62], 0.64 [0.60, 0.68], 0.54 [0.49, 0.59]; SYS 0.28-0.37; C1 Qwen 0.03 [0.01, 0.05], Llama 0.43 [0.36, 0.51]; C3 Llama −0.13 [−0.23, −0.03]; Holm ≤ 0.02; 6 / 26 under-cap rounds | Results, Fig. 2, App. B.6 | analysis/n2_results/N2_RESULTS.md sec. 4-6, 8; n2_estimates.csv |
| N2 cell means (Table B2); parse failures 0.4%-2.4%; 69 zero-crux rounds | App. B.6 | analysis/n2_results/n2_cells.csv |
| 6,250 statements; 250 rounds; 45 from dev launches | Methods, App. A 12 | N2_RESULTS.md sec. 1; analysis/N2_ANALYSIS_SPEC.md sec. 1 |
| 6 N2 statements checked; 25 items = 19 + 6 | Methods, Results, N2 | FR §6.R5.2, §6.R5.7 |
| Spend $15.28 | App. B.8 | ledger.csv, cumulative_usd of the last ACTUAL row (2026-11-16T02:16Z N2 scoring; the 02:33Z N3 attempt row is $0.0) |
| Panel vs scorer: 21 Q1-yes items (16 original, 5 N2); table 6/3/8/4; agreement 10/21 = 0.476; κ 0.00 [−0.39, 0.37], B = 10,000, seed 20261145; originals 8/16, N2 2/5; 13 E = 1 items, 7 acknowledged (5 of 11 originals, 2 of 2 N2) | Results, Discussion, App. A 5, Table B3 | analysis/panel/panel_vs_scorer.json (sha256 0d59c349…4039) |
| 315 + 2 and 100 + 1 split of the step-2 confusion cells; 0.753 = 1,222/1,622 | Results, Table 1 note, App. A 4, B.2 | gate1/step2_private/rounds__20261116T015355Z.csv (cross-tab hsplit × ext_ok × crux); RESULTS_MAIN.md "Rounds with ≥ 1 crux: 1222" |
| Length specs: t 2.34 registered, cubic 1.82, deciles 1.72, rank 1.35, rank + log 2.46, raw 1.98, raw + log 1.69; −0.074 (t −2.93) | Results, Discussion, App. A 1, Figure B1 | figures/data/a2_length_spec.csv (analysis/redteam_rerun/rt_refit.json) |
| Claude models: orchestrator Opus 5.5; agent roles `model: opus` | LLM Usage | decisions.md D60; C:/Users/intel/Downloads/OU/projects/.claude/agents/{methodologist,statistician,peer_reviewer,editor,adversary}.md |
| Tessler 0.36 vs 0.29 | Intro (quote), Related Work | report/references_verified.md (Tessler entry) |
| Zhu "never exceed 0.4"; 18 LLMs | Related Work | report/references_verified.md |

## Figures
`figures/make_real_figures.py` (reads only the CSVs above) -> `figures/real_out/`: `fig_a2_forest` (Fig. 1), `fig_n2_contrasts` (Fig. 2), `fig_n2_<generator>` x5 (one per generator, referenced in B.6), each as PDF + PNG (220 dpi) + sidecar JSON with input SHA-256, plus `captions.md`. `fig_a2_length` (Figure B1) from `figures/data/a2_length_spec.csv`. Followed `skills/figures.md` (Okabe-Ito + markers, CIs, takeaway-first captions, PDF+PNG, fonttype 42, >= 8 pt at print size).
