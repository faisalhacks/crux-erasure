# REDTEAM — T3-1 real-data results (RESULTS_MAIN sha dc236afc…, gate R5 VALIDATED_PRESENCE)

Red team, 2026-11-16. Read-only on everything outside `analysis\redteam\`. Every claim below cites a
script in this folder and the JSON it wrote. All red-team scripts were run with
`C:/Users/intel/miniconda3/python.exe -I -B` (`-B` so no `__pycache__` was written into `analysis\`).
Everything computed here that FROZEN_RULES (FR) does not define is **exploratory** (BRIEF §3.10) and
cannot change any pre-registered outcome. It can only change how the paper describes the outcome.

## What re-computation confirmed (no defect)

| Check | Result | Evidence |
|---|---|---|
| (1) A2 `beta_E`, own code from raw files (own mid-ranks, own Flesch and word regex, own within-transformation, CR1, own wild bootstrap-t) | **+0.051085, CR1 SE 0.021802**: identical to the record to 1e-15. Own wild-t (B = 4,000, seed 777) [+0.0092, +0.0945], p = 0.0195 (record, seed 20261119: [+0.0076, +0.0952], p = 0.024). Uncontrolled −0.0743 and A2h +0.0455 also identical. Group-unit (FR §11 form) +0.0519. | `rt_refit.py` → `rt_refit.json` (`A2_primary_own`, `A2_uncontrolled_own`, `A2h_own`, `X_group_unit`) |
| (2) Analysis set | 1,960 rounds / 871 launches / 9,501 rater rows (= FR §2); 150 development launches, all present; set = **1,622 rounds / 721 launches**. Dropped for A2: 397 zero-crux + 3 extraction failures + 11 all-4-`E`-missing + 45 partly-missing = **456**, leaving **1,166 rounds / 642 launches / 22,536 rows**; `R_inf` 150, `K_inf` 142. `round_id` is unique across launches; no −1 ranks; every rater is an opinion author. | `rt_refit.json` (`n_rounds_conf`, `drops_conf`, `n_rounds_fit`, `R_inf`, `K_inf`) |
| (2b) Ranks used = frozen source | All 9,501 rater rank vectors in `pilots\T3_1\all_groups.jsonl` equal `rankings.numerical_ranks` in the source parquet (sha `7cf8d5ce…`, re-hashed), and `rankings.candidate_ids` equals the candidate order used for `E` in 9,501 / 9,501 rows. | `rt_ranks_vs_source.py` → `rt_ranks_vs_source.json` (`raw_order_equal`, `rankings_candidate_ids_equal_cand_ids`) |
| (3) RESULTS_MAIN vs JSON | Every point, bound, p, Holm p and count in RESULTS_MAIN.md matches its JSON in `analysis\results\runs\` at the printed precision (A2, A2b, A2d–A2i, controls, N1/N1u/N1h/`g_L`/`g_C`, N4 + slopes, both Holm versions, 7 prevalence rows, drop counts). No discrepancy found. RESULTS_MAIN.md and COUNTS_RECONCILE.md hash to their sidecars. | manual line-by-line comparison; `sha256sum` |
| (4) Leakage of real ranks before the freeze / gate | None found. FREEZE `frozen_utc` 01:53:53.642Z; GATE1_RESULT recorded 02:05Z; the first real-rank artifact is `a2_long_real.parquet` (RUNS.md row 528, 02:12:21Z); all A2/N1/N4 runs 02:12:37Z–02:13:08Z. Analysis-code mtimes precede the freeze (`a2_within_round.py` 2026-11-15T19:31Z, `n1`/`n4` 19:31Z, `common.py` 2026-11-16T01:08Z). `human_signals_levels.json` (pre-freeze) holds only token *levels* of the position ratings, not counts or values. Step 2 re-computed from its per-round file: TP/FN/TN/FP 907/101/297/317, BA2 0.69176, sens 0.8998, spec 0.4837 (exact). | `ls --time-style=full-iso`; RUNS.md rows 525–540; `rt_step2.py` → `rt_step2.json` |
| (5) Tier after the `K_inf` defect | "Tier unchanged" is **correct** under FR §7.1: corrected `K_inf` 142 ≥ 100; `MDE80` (0.0563) was computed by `fit_models`, which already drops partly-missing rounds; one-way check 2.80 × 0.0218 = 0.0610 ≤ 0.10. Nothing pre-registered changes. (Residual text errata: see item 13.) | `rt_refit.json` (`K_inf`); `gate1\A2_TIER_R4.json`; `A2_primary__…json` `se` |
| (6) N4 definition | Matches FR §8 exactly: side from the **first-listed crux of the scorer-1 extractor's member lists** (not from pre-deliberation position ratings); minority = smaller side; equal sides / no side excluded. Own refit: interaction −0.146566, CR1 SE 0.053319 = record. | `rt_n4.py` → `rt_n4.json` (`N4_own`) |

## Findings, ranked

No BLOCKER was found: the numbers are right, the set is right, and the gate preceded every real-rank
read. The MAJOR items are about what the pre-registered A2 number can be read to mean, and about
rules the write-up has not yet met.

### 1. MAJOR — A2's sign and "interval excludes 0" depend on the linear log-length control

Evidence (`rt_refit.py` → `rt_refit.json`; exploratory; CR1 SE, t = est/SE):

| Length adjustment (clarity kept) | `beta_E` | SE | t |
|---|---|---|---|
| none (`E` only; record's "uncontrolled") | −0.0743 | 0.0254 | −2.93 |
| **linear z log words (FR primary)** | **+0.0511** | 0.0218 | 2.34 |
| cubic in z log words | +0.0395 | 0.0217 | 1.82 |
| 10 length-decile dummies | +0.0380 | 0.0221 | 1.72 |
| within-round length rank (1–4) | +0.0309 | 0.0230 | 1.35 |
| z raw word count | +0.0457 | 0.0231 | 1.98 |
| z raw words + z log words | +0.0366 | 0.0216 | 1.69 |

Within the 150 informative rounds, within-round corr(`E`, log length) = −0.34: statements that show a
crux are longer. Length dominates the rank (`beta_L` t ≈ 36; decile effects rise to ≈ +0.56 on `y`).
`beta_E` is therefore a small residual of a large, collinear length effect: its sign flips without the
control, and every more flexible length adjustment tried leaves |t| < 1.96. The linear log form is the
pre-registered model, so the A2 result of record stands as computed; but a reader cannot take "+0.051,
interval excludes 0" as robust evidence about hiding.
Fix: print this table (labelled exploratory, not in FROZEN_RULES) beside A2 and the uncontrolled
estimate; say in Results and Discussion that the A2 estimate is conditional on a linear log-length
adjustment, and that flexible adjustments give intervals that include 0. Do not use A2 for any direction
sentence beyond the FR §6.R5.6 wording (already barred from title and abstract).

### 2. MAJOR — The positive A2 coefficient is carried by `SIDED` and by majority-side raters, i.e. it is not separable from "the statement takes my side"

Evidence (`rt_n4.py` → `rt_n4.json`, exploratory): splitting `E` into its `SIDED` share and its
`BLENDED`+`OMITTED` share in the A2 model gives `SIDED` +0.0531 (SE 0.0218, t 2.43) and
`BLENDED/OMITTED` +0.0284 (SE 0.0257, t 1.10). A2e (`SIDED` counted as shown) is −0.0228
[−0.0519, +0.0056] (`A2e__…json`). N4's conditional slopes (record, `N4__…json`): majority-side raters
+0.0996 [+0.0369, +0.1628], minority-side raters −0.0470 [−0.1308, +0.0386]; with the `SIDED` share as
predictor the same pattern holds (`SIDED` +0.057, `SIDED × minority` −0.065, t −1.89). And A2b
(own-opinion similarity added) falls to +0.0443 with lower bound +0.0002 (item 3).
One reading consistent with all of this: one-sided statements are preferred by the raters whose side
they take (the majority), which is a self-interest / agreement effect, not a preference for hiding
disagreement as such. The construct choice (§4: `SIDED` = hidden) is pre-registered and stays; the
interpretation must not go beyond it.
Fix: Discussion states that the A2 association comes from `SIDED` labels and from majority-side raters,
and that the design cannot separate "rewarding hidden disagreement" from "rewarding a statement that
agrees with me". Cite A2e, A2b and the N4 slopes together.

### 3. MAJOR — The A2b binding-wording trigger sits inside Monte Carlo error

Evidence: A2b lower bound = +0.000178 (`A2b__…json`). RESULTS_MAIN says "the A2b rule does not fire;
the margin should be stated". The interval is a bootstrap-t quantile with B = 10,000; for the primary
model the record seed and my seed 777 give lower bounds 0.0076 vs 0.0092, a Monte Carlo spread of the
same order as A2b's margin. Seed sweep with the project's own code (`rt_seed_sensitivity.py` →
`rt_seed_sensitivity.json`), B = 10,000, 40 seeds other than the record's: A2b lower bound ranges
−0.0011 to +0.0017 (SD 0.00057) and is **≤ 0 for 7 of 40 seeds (17.5%)**; A2b p ranges 0.044–0.052.
For comparison A2 primary's lower bound ranges +0.0065 to +0.0091 (never ≤ 0), A2h +0.0005 to +0.0033,
A2g +0.0060 to +0.0086.
FR fixes the seed (20261119), so mechanically the rule does not fire. But whether it fires is a coin
flip of the bootstrap seed, not a property of the data.
Fix: state in the text that A2b's lower bound is +0.0002, within bootstrap Monte Carlo error of 0, and
apply the A2b sentence voluntarily (careful option, BRIEF §14): "the association cannot be clearly
separated from raters preferring statements close to their own view". This is stricter than FR and
loses nothing.

### 4. MAJOR — Step-2 specificity 0.48: a quarter of A2's identifying rounds come from groups that, by their own ratings, did not disagree; and RESULTS_MAIN omits the step-2 numbers FR requires in the main text

Evidence (`rt_step2.py` → `rt_step2.json`; per-round file `gate1\step2_private\rounds__20261116T015355Z.csv`,
read only after the gate was recorded): of 614 rounds with `Hsplit` = 0 the scorer found ≥ 1 crux in 317
(spec 0.484); PPV of "≥ 1 crux" for `Hsplit` = 1 is 0.741. In the A2 fit, **289 of 1,166 rounds and 39 of
the 150 informative rounds (39 launches)** have `Hsplit` = 0. Exploratory split (`rt_refit.json`):
`beta_E` = +0.015 (SE 0.046) in `Hsplit` = 0 rounds, +0.066 (SE 0.024) in `Hsplit` = 1 rounds;
interaction +0.072 (SE 0.050). So `E` varies, and is used to estimate "hiding disagreement", in rounds
where participants reported no split on the question; the point estimate is near 0 there, but the data
cannot tell the two apart.
Separately: FR §6.R5.1 puts BA2 with sens and spec, the `Hsplit` class counts and the 2×2 table in the
main text ("Reported, no rule (main text)"), and D54 says the 0.484 specificity is to be reported in the
main text. RESULTS_MAIN.md gives the stamp and the status but none of these numbers, and does not name the
reference ("participants' own pre-deliberation position ratings") in the step-2 wording of record.
Fix: add a step-2 block to RESULTS_MAIN (BA2 0.6918 [0.6690, 0.7140], sens 0.900, spec 0.484, 2×2,
class counts 614/437 and 1,008/605) with the binding step-2 sentence of §6.R5.6 and the pre-stated
"expected weakness" sentence of §6.R5.1; add the exploratory `Hsplit` split beside A2 with the counts
289/1,166 and 39/150.

### 5. MAJOR — N4, the only family test below 0.05, rests on 151 minority rater-rounds; its informative counts are not reported

Evidence (`rt_n4.json`): N4's sample has **114 informative rounds in 106 launches**, with **151
minority-side rater-rounds** inside informative rounds (1,142 minority rater-rounds overall). FR §8 [R1]:
"Each reports its own count of informative rounds and launches" — `N4__…json` has neither (RESULTS_MAIN
prints "—" for N4's rounds), and `N1__…json` has no informative-launch count. FR §7 [R2] states the
wild bootstrap's coverage was never checked for the N4 interaction. The side lists come from the LLM
extractor; step 2 validated presence only, not side membership. (Partial support, exploratory: the
extractor's two sides of the first crux differ in members' own pre-deliberation ratings by a mean
|Δ| of 2.57 scale points against 1.69 under within-round permutation, 1,164 rounds — `sides_vs_prerating`
in `rt_n4.json`.)
Multiplicity: Holm with m = 3 (N3 at p = 1) gives N4 0.0234; the family test survives Holm, but no
coverage check, 151 identifying minority rater-rounds and an unvalidated side assignment.
Fix: add N4's and N1's informative-round and informative-launch counts and the 151; print the
conservative Holm (item 9) as the column of record; state that N4 sides come from the extractor and were
not validated, and that the interaction's interval method was not coverage-checked.

### 6. MAJOR — The sealed `features.parquet` (D33) was loaded after sealing; the disclosure that it is "not used anywhere" is false

Evidence: decisions.md D33 (line 254): "features.parquet is SEALED — no agent may open, read or load it;
it is not used anywhere in T3-1". FR R4 (line 1111) lists it as sealed. `pilots\T3_1\TOUCHED_RANKINGS.md`
mtime = 2026-11-15T19:07Z. Yet RUNS.md rows **360–362 (2026-11-15T19:41Z), 389–391 (2026-11-16T01:16Z)
and 468–470 (01:27Z)** list `features.parquet:66ed880872dde8b9` as an input of `a2_within_round.py` /
`n1_winner_vs_mean.py` shuffled test runs: `common.load_habermas_shuffled` reads it (`common.py:285`), with
real ranks and the pilot's erasure proxy `markers` in memory, and shuffles ranks within rater before
fitting. decisions.md D38 (line 308) says "features.parquet (sealed, D33) not touched".
Impact on results: none found — ranks are shuffled before any fit, `E` is a dummy, and nothing from
those runs enters A2 or the tier. Impact on integrity: a sealed-file rule was broken and two records say
it was not.
Fix: correct the [PILOT-DISCLOSURE] text and add a decisions.md erratum listing the 9 RUNS rows; replace
`load_habermas_shuffled`'s source with `a2_long_shuffled.parquet` for any future test run.

### 7. MAJOR — Draft paper text already conflicts with §6.R5.6 / §6.R5.7 (frames, banned wording, defective counts)

Evidence: FR §6.R5.7 requires "one title, abstract results sentence and claims list per status of §6.R5.6
… written before the gate is recorded; … nothing is reframed after the result" (editor condition 2). No
such frames exist (`grep -rl VALIDATED_PRESENCE report/` finds nothing; `report\parts\05_abstract.md` has
one generic abstract). That abstract (mtime 2026-11-16T00:51Z) has an A2 RESULT SLOT in the abstract
("Within rounds, controlling for length and readability, [RESULT SLOT: A2 beta_E …]"), and asks for the
validation clause "in the D49 wording" — the bare D49 phrase is banned by §6.R5.6 ("is never used"), and
under VALIDATED_PRESENCE there is "no directional rank claim in title or abstract".
`report\parts\40_results.md` heads A2 "(A2, confirmatory)" — "confirmatory" is banned for `E`-based
results under VALIDATED_PRESENCE — quotes the defective "152 confirmatory rounds (144 launches)", and cites
the stale N2 spec hash `4085b78d…` (of record: `afada117…`). Every A2/N1/N4 JSON carries the label
"CONFIRMATORY (development launches excluded)" (`common.restrict_confirmatory`), which will leak into
tables if copied.
Fix: before any result enters the draft, write the VALIDATED_PRESENCE frame (title as a question,
abstract results sentence with no direction, the scope phrase) and log that it was written after the
gate (so the §6.R5.7 protection is disclosed as not met); replace the slot instructions; rename the label
in tables to "development launches excluded"; fix 152/144 → 150/142 and the N2 hash.

### 8. MINOR (check passed) — Wild bootstrap-t size under the real, sparse `E` had not been checked

Evidence: FR §7 [R2] checked coverage with a dummy `E` that varies in almost every round; the real `E`
varies in 150 rounds of 1,166. Own check, 200 within-rater shuffles of the real ranks with the real `E`,
project interval code, B = 999 (`rt_null_coverage.py` → `rt_null_coverage.json`): **coverage of 0 =
191/200 = 95.5%**, share p < 0.05 = 3.5%; null SD of `beta_E` 0.0207 vs mean CR1 SE 0.0203. The A2
interval method is well calibrated for the real `E` (for A2 only; not checked for N4's interaction).
Fix: report this figure beside the FR coverage limitation, labelled as a post-gate exploratory check.

### 9. MINOR — The "Holm p" column shows the anti-conservative version

Evidence: RESULTS_MAIN: "Holm p in the table above = the first version" (m = 2: N1 0.1154, N4 0.0156).
FR §9: family size "depends only on the data-availability counts in §8, never on results"; N3 qualifies
(713 launches), so it is in the family. Until N3 runs, the only Holm values that respect FR §9 are the
conservative ones (m = 3: N1 0.2308, N4 0.0234); D57 makes these the values of record if N3 is not scored
by 06:30Z.
Fix: put the conservative values in the table column; give the m = 2 values only in the note.

### 10. MINOR — A2's "excludes 0" is carried by a few launches

Evidence (`rt_refit.json`, exploratory): leave-one-launch-out over the 142 informative launches gives
`beta_E` in [+0.0457, +0.0550]; removing the 3 / 5 / 10 most influential launches gives +0.0371 (SE
0.0207) / +0.0287 (0.0202) / +0.0093 (0.0193). The removal is selected to lower the estimate, so this is a
fragility indicator, not a test.
Fix: one sentence in Results: removing the 3 most influential of 142 informative launches leaves an
interval that would include 0.

### 11. MINOR — FR §2's `build_analysis_set.py` / `analysis_set_manifest.json` never existed; the source-hash check is ceremonial

Evidence: neither file exists (`find` over `_apart_intel`). The real table is built from the pilot's
`all_groups.jsonl` (`build_a2_long_real.py`); its manifest field `build_analysis_set_counts` is the
constant `C.FROZEN_COUNTS` written by the builder itself, so `verify_source`'s comparison against
`FROZEN_COUNTS` is tautological, and the re-hashed source parquet is not the file the table is built from.
`report\parts\40_results.md` still has an open slot for `analysis_set_manifest.json`. Mitigation: item
(2b) above shows the ranks and candidate order equal the source in all 9,501 rows, and the table counts
(1,960 / 871 / 9,501) are computed, not copied.
Fix: disclose as a deviation from FR §2; cite `rt_ranks_vs_source.json` as the integrity check.

### 12. MINOR — 40 rounds show the same statement 2–3 times

Evidence (`rt_dup_ids.py` → `rt_dup_ids.json`): 40 eligible rounds have duplicated candidate ids with
identical text (36 non-development; 27 in the A2 fit; 4 informative). Raters rank identical texts
differently. FR §2 (c) "exactly 4 candidates" is met only nominally. Excluding them: `beta_E` +0.0539
(SE 0.0222) (`rt_refit.json`, `X_excl_duplicate_candidate_rounds`). No material effect.
Fix: disclose the count in Methods.

### 13. MINOR — `K_inf`/`R_inf` defect: residual errata

Evidence: tier unaffected (table above). But the defective 144 still stands in FR §1's "[R4] note" and
§7.1 disclosure (frozen; cannot be edited), `gate1\A2_TIER_R4.json` (write-once), decisions.md D32/D35/D57
and `report\parts\40_results.md`. Also FR §7.1 asks for the `E_pos` side counts in the tier file;
`counts_other` is `{}` in `A2_TIER_R4.json`.
Fix: one erratum sentence in the paper and the README: correct counts are 150 / 142 (dev-excluded) and
176 / 166 (including development launches); the frozen text's 144 counted 2 rounds with a partly missing
`E`. Add the `E_pos` counts as a post-hoc side figure, labelled.

### 14. MINOR — N1 reporting gaps

Evidence: FR §8 [R1] requires "descriptively, the mean `d_r` over those rounds [with `d_r` ≠ 0]" — not
in `N1__…json` or RESULTS_MAIN (derivable: −0.0041 × 1,042 / 132 = −0.032). FR §8 [R3] Schulze-winner
sensitivity not run (disclosed). The [R3] guard (192/200, RUNS rows 143/189, 18:56Z and 19:01Z) ran on an
earlier `n1_winner_vs_mean.py` (file mtime 19:31Z); RUNS.md's code hash covers every `analysis\*.py`, so
it cannot show whether the N1 estimator itself changed.
Fix: add the mean over `d_r` ≠ 0 rounds; state that the guard ran on the pre-R4 version of the script
(the change was the development-launch restriction, which does not apply to synthetic data — verify by
diff if a copy exists, otherwise say "not verified").

### 15. MINOR — RESULTS_MAIN cannot be regenerated from the current assembler

Evidence: `assemble_results.py` now hashes to `a16ff96b…`; RUNS.md row 542 logs `bdd6febc…` for the
version that wrote RESULTS_MAIN (02:15:33Z). The file was modified at 2026-11-16T02:19:34Z (N3 branches
added). RUNS.md code hashes are over all of `analysis\*.py`, so they cannot pin one script.
Fix: keep a copy of the `bdd6febc…` assembler (or regenerate RESULTS_MAIN with the new one and log both
hashes); hash individual scripts in RUNS.md from now on.

### 16. MINOR — Statements with a missing `E` are longer

Evidence (`rt_ranks_vs_source.json`): in rounds with ≥ 1 crux, the 123 statements with a label parse
failure have median 98 words vs 87 for the 5,781 scored ones. The 45 partly-missing rounds are dropped
whole (FR §4 rule, followed correctly). Given item 1 (length is the main confounder), the dropped rounds
are not missing at random with respect to length.
Fix: one limitation sentence with these counts.

## Answers to the eight questions

1. Refit: point estimate and sign reproduced exactly (+0.0511, positive). Robustness: item 1.
2. Set: 721 non-dev launches / 1,622 rounds; drops 397 + 3 + 11 + 45 = 456, as described.
3. No RESULTS_MAIN number differs from its JSON.
4. No leakage of real ranks before the freeze or the gate. The D33 seal was broken by shuffled test runs (item 6).
5. The defect changes nothing pre-registered; "tier unchanged" is correct under FR §7.1 (items 13 for errata).
6. N4 follows FR §8: minority comes from the extractor's first-crux member lists, not from position ratings. It survives Holm at m = 3 (0.0234) but rests on 151 minority rater-rounds (item 5).
7. RESULTS_MAIN complies with §6.R5.6; the draft paper does not (item 7).
8. Specificity 0.484 means `E` is estimated partly in non-split groups: 39 / 150 informative rounds (item 4).

## Files
Scripts and outputs in `analysis\redteam\`: `rt_refit.py`/`.json`, `rt_n4.py`/`.json`, `rt_step2.py`/`.json`,
`rt_ranks_vs_source.py`/`.json`, `rt_dup_ids.py`/`.json`, `rt_seed_sensitivity.py`/`.json`,
`rt_null_coverage.py`/`.json`.
