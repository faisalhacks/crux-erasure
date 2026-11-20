# EXPERIMENTS.md — T3-1 crux erasure

P = `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1`. Scripts live in `P\analysis\`.
Definitions are in FROZEN_RULES.md (FR); this file says how each experiment is run.
No experiment below has been run by the planning room.

**Scripts that already exist** (stats coder and grid runner, tested on dummy and shuffled data
only): `exp0_check.py`, `gate1.py`, `a2_within_round.py`, `n1_winner_vs_mean.py`,
`make_dummy_labels.py`, `n2_grid.py`, `common.py`. They were written on assumptions and must be
brought into line with FR before freeze. Known gaps: label tokens and schema (FR §5);
`item_key.csv` instead of a `dup_of` column; the gate script writes `gate1_computed.json`, never
`GATE1_RESULT.json`; A2 uses `E` on its raw 0-1 scale with a (rater, round) fixed effect and
mid-rank outcome (FR §7); N1 is the plain mean of `d_r` (FR §8); seeds as in FR. All other
script names below are still to be written.

## Replan log

**R1, 2026-11-15 (decisions.md D21; FR "Replan log").** Changes in this file are marked **[R1]**.
Reason: on the development probe `E` varied within the round in 3 of 34 rounds, so A2 may have
little identifying variation. Decided blind to rankings.

- A2 stays the only confirmatory test. A new $0 step, **A2-tier**, fixes before unblinding what A2
  may claim (FR §7.1). New sensitivity model A2i.
- If the tier is LOW-POWER or NOT MEASURABLE, the paper leads with prevalence and N2 (FR §7.3).
  N2 keeps its own hashed spec and its exploratory label; only its place in the paper changes.
- Gate 1 gets the D18 additions (FR §6.4a). Pass rule unchanged.
- N1, A4, N4 inherit the tier wording. No between-round design. No graded score.
- Code to write or change (stats coder, scorer runner):
  1. `a2_informativeness.py` → `gate1\A2_TIER.json`; `a2_within_round.py --kind real` refuses to
     run without it. Tested on dummy data with a planted low-variation `E`.
  2. `a2_within_round.py`: A2i (`{"rounds":"informative"}`); 2.80 × bootstrap SE and the
     downgrade flag in the output; the interval method selected under D19.
  3. `gate1.py`: `BA_crux`, `BA_sh`, zero-crux share, `D1h` with Wilson intervals, the wording-rule
     flag, the scorer-v1 comparison, the human `NO_DISAGREEMENT` vs AI zero-crux table (ALIGNMENT
     item 7); accept only `adj_label` in `ADJ.csv`.
  4. `scorer.py`: drop a crux with an empty side, count and report (FR §3). Not present when this
     was written.
  5. `prevalence.py`: the FR §7.3 quantities, launch bootstrap, seed 20261128. Reads no ranks.
  6. `n1_winner_vs_mean.py`: count of rounds with `d_r ≠ 0` and their mean.
  7. `scores.csv` for the gate must carry `n_cruxes`, and zero-crux `E` must be NaN (ALIGNMENT item 6).

**R2, 2026-11-16 (decisions.md D25).** Every launch-clustered interval and p-value is the wild
cluster bootstrap-t of FR §7 "[R2] Interval method of record"; B = 10,000 and seeds unchanged.
Already the default in `common.py`. Where a table cell in this file says "bootstrap" it means that.

**R3, 2026-11-16 (decisions.md D29).** N1's family test is now adjusted for length and clarity
(FR §8 "N1 adjustment [R3]"); the unadjusted mean is printed beside it. Code still to write, by a
new author with a fresh-context reviewer (the stats coder was stopped, D26):
`n1_winner_vs_mean.py` → intercept of `d_r ~ dLen_r + dClar_r` via `common.ols_cluster_ci`
(seed 20261120), N1h (length only), N1u, and the synthetic length-confound check (≥ 200 datasets,
coverage logged in RUNS.md). If that check is below 93% or missing when real ranks are first
read, N1 leaves the Holm family (`tier2_holm.py` must take that flag). Gate 1: the paper prints
the kappa-step power note of FR §6.2 (about 34% pass rate for two 90%-accurate labelers at n = 20).

**R4, 2026-11-15 UTC, written 19:06Z to 19:25Z (decisions.md D31, D34, D36, D37; FR "Replan log" R4).**
Human-authored rule edits (D31 at 19:06Z, superseded in part by D34 at 19:10Z, extended by D37 at
19:16Z) and the council's model choices (D36). `labels\` was empty at each check. Where a table
below still shows the older design, this entry and FR govern; cells changed in place are marked
**[R4]**.

| # | Change | Reason | FR |
|---|---|---|---|
| 1 | **Labelling design.** One human labeler (the author, hypothesis-aware): 50 items in pass 1 (38 originals = first 38 of the existing seeded sample; 12 N2 statements), 20 of them (15 + 5) again in pass 2 at least one hour later. Files `labels\author_pass1.csv` (50 rows) and `author_pass2.csv` (20 rows), columns `item_id,label,main_disagreement,comment,pass_started_utc`. The 30 shared + 15 + 15 design and the 0.40 inter-rater cut-off of D31 edit 1 were replaced by D34 before anything was built to them. | Human (D31: weak kappa step at n = 20; D34: one labeler). | §5, §6.1 |
| 2 | **Optional volunteer (hypothesis-blind).** If `labels\volunteer_pass1.csv` exists when `gate1.py` first runs on real labels (the first poll at which the author's pass-1 file is complete): two-human design, inter-rater kappa ≥ 0.40 on the 50 items, labels adjudicated blind to scores in `labels\ADJ.csv`. Otherwise single-labeler design. Recorded write-once in `gate1\DESIGN.json`. | Human (D37). | §6.0, §6.2, §6.3 |
| 3 | **Agreement step.** Single-labeler: self-consistency kappa ≥ 0.60 on the 20 repeats. Both designs: bootstrap CI and Gwet's AC1 beside kappa; one-hour rule checked from the time stamps and `pass_started_utc`. | Human (D34 item 2; D37 item 3). | §6.2 |
| 4 | **Gate 1 validity.** Balanced accuracy of scorer 1 on the 38 originals against the labels of record (author's first pass, or adjudicated), lower bound > 0.5. Statuses `PASS`, `PROVISIONAL_PASS` (single-labeler design, before pass 2 is scored), `FAIL`, `INCOMPLETE`. In the PROVISIONAL state A2, Tier 2, prevalence and the headline may run with every output stamped PROVISIONAL; N2 scoring waits for the final PASS. | Human (D34 item 3 and process). | §6.4, §6.5 |
| 5 | **N2 scorer check.** The 12 N2 packet items (3, 3, 2, 2, 2 over five generators, seed 20261116, no generator-cell pair repeated, outside development and gate-sample launches) are scored by scorer 1 as gate items, stored in `gate1\n2check_scores.jsonl`. Pass = one-sided Fisher exact p ≤ 0.05 on the pooled 12 and gate 1 passed. PASS → `N2_VALIDATED`; otherwise `EXPLORATORY`. No other N2 statement is scored and no N2 analysis runs before gate 1. | Human (D31 edit 2, D34 item 3); D36. | §6.1a, §6.6 |
| 6 | **A4 second scorer = granite-4.2-30b** (no reasoning parser; fallback granite-4.2-8B), replacing Gemma-4-12B. Scope now: development smoke (≥ 200 calls), the 50 packet items, a seeded 1,000-statement sample (250 rounds, seed 20261133). Bar V1 / V2 / V3 before use. The full A2 refit needs a later council vote and is a family test only if that vote precedes the first real-rank run. | Human (D31 edit 3: different family from every N2 generator); D36. | §4, §6.9, §8 |
| 7 | **Headline rate** = share `HIDES` among definite human labels on the 38 originals, Wilson 95% interval, `UNSURE` excluded with both bounds printed; scorer rate secondary. | Human (D31 edit 4). | §6.7 |
| 8 | **N2 extended to five generators** (adds Ministral-3-14B, phi-4, Llama-3.1-8B-Instruct): same 250 rounds, 5 cells, k = 1, prompts and decoding; length covariate; every result split by generator; spec of record = `N2_ANALYSIS_SPEC.md` with Amendment 2, SHA-256 `126787ad…c60b` (the code owner computes any later hash). N2 cap $10 → $15 (D36). | Human (D31 edit 5); D36. | §10 |
| 9 | **Development launches excluded from every confirmatory and family test.** The confirmatory set is the 721 non-development launches (all 150 development launches out, which covers the 40 development-probe rounds, 29 to 35 evaluable). A2, the A2 tier, N1, A4, A3, N3, N4, gate 1, the N2 check, the headline and the prevalence quantities use it. The all-launch A2 is sensitivity A2d only. Before R4 the all-launch A2 was the primary, so the exclusion was not guaranteed. | Human (D31 edit 6, D34 item 8); orchestrator's instruction on the §2 conflict. | §2, §7, §7.1, §8, §10 |
| 10 | **LLM annotator = gpt-oss-120b**, temperature 0, seed 0, one item per fresh call, instructions verbatim (volunteer version) plus one format line, same blinding; labels in `gate1\llm_annotator\`, never in `labels\`; author–LLM kappa and AC1 with CI; supplementary, never called human. | Human (D34 item 4); D36. | §6.8 |
| 11 | **Wording.** "validated against a single hypothesis-aware human annotator", or the two-human form; volunteer = "hypothesis-blind human annotator". | Human (D34 item 9, D37 item 5). | FR header |

**Sample-size consequences (synthetic labels only, seed 777; `analysis\planning\r4_*.py` and `.json`; FR §6.1b, §6.6).**
Self-consistency kappa ≥ 0.60 on 20 repeats: pass rate about 34% for a labeler who reproduces their
own reading 9 times in 10 per pass, 70% at 19 in 20, 85% at 39 in 40 (23%, 51%, 70% if three
quarters of the items are `HIDES`); memory of the first pass is not modelled and would raise these.
Two-human kappa ≥ 0.40 on 50: 88% for two 90%-accurate labelers, 18% at 80%, 5% at 75%.
Balanced-accuracy rule at 38 items: chance scorer passes about 3%; true 0.70 passes 55 to 70%; 0.80
passes 88 to 98%. N2 check on 12 items: a scorer right on 90% of items passes 65 to 84%, on 80%
only 32 to 47%; chance about 1%. Headline interval at n = 38: about ±15 points near one half.
For the record, the D31 design that was replaced (inter-rater kappa ≥ 0.40 on 30): 82% at 90%
accuracy, 22% at 80%.

**Code and files to change before any packet is released (author = a build agent; reviewer = fresh context; all tests on dummy data).**
1. `g1_packets.py` / `labels_build\build_packets.py`: one author packet (50 rows) + pass-2 packet
   (20 rows) + volunteer packet (same 50, seed 20261135, own ids) + `SHARE.md`; new ids; new
   `item_key.csv` (`pass, kind, generator, cell, dup_of`); `gate1\n2_items.json` by the FR §6.1a
   formula; two instruction files (author and volunteer versions); archive the 44-row packets.
   Runs only after the extended N2 generation is complete. `verify_packets.py` updated to FR R4.
2. `gate1.py`: `DESIGN.json` switch; schemas and row counts; frozen pass-1 hash; one-hour rule;
   self-consistency or inter-rater kappa with the right cut-off; AC1; undefined-resample count;
   38-item gate set; labels of record per design; `PROVISIONAL_PASS`; N2 check (Fisher) →
   `N2CHECK` output; headline `H` with Wilson interval and bounds; volunteer-only and LLM-annotator
   side figures; flag "provisional real-rank output existed when pass 2 arrived".
3. `common.check_kind`: `PROVISIONAL_PASS` → stamp `PROVISIONAL`; re-stamping step for PASS / FAIL.
4. `poll_labels.py`: watch `author_pass1.csv`, `author_pass2.csv`, `volunteer_pass1.csv`, `ADJ.csv`;
   freeze on the first label file of any kind; report stray `L1.csv` / `L2.csv`.
5. `build_analysis_set.py`: confirmatory set (721 launches) + `analysis_set_manifest.json`; all
   real-rank scripts default to it; A2d = all launches; Tier-2 side figures with development launches.
6. `a2_informativeness.py`: re-run on the confirmatory set (shuffled ranks only); keep the D35 file
   under a dated name; planning room logs the tier of record.
7. `prevalence.py`: confirmatory set; printed beside `H`.
8. `scorer.py` / manifest: granite-4.2-30b entry and pinned revision; development smoke and V1;
   scoring of the 50 packet items and the 1,000-statement sample; `gate1\A4_BAR.json`.
9. `llm_annotate.py` (new): FR §6.8; `annotator_manifest.json`; output outside `labels\`.
10. `tier2_holm.py`: flags for A4 (vote date, V2) and N1 ([R3] guard).
11. `n2_grid.py --mode score`: refuses unless gate 1 is PASS (a PROVISIONAL_PASS is not enough); writes the
    `N2_VALIDATED` / `EXPLORATORY` label from `N2CHECK_RESULT.json`; the 12 packet items are the
    only N2 statements a scorer may touch before that.

**R4a, 2026-11-15T20:18Z to 20:21Z UTC (decisions.md D44, D45; FR §6.9, "Replan log" R4a).** Both
Granite models missed the A4 technical bar (75.4% and 57.5% of development statements without `E`;
bar 5%). Reason for the change: D44 allows one more attempt under a closed list. Scorer-2
candidates, in order: `tiiuae/Falcon-H1-34B-Instruct`, then `CohereLabs/c4ai-command-r7b-12-2024`
(gated: a human must accept its terms). Same smoke, same bar, same frozen prompts and parser, $2
cap each, development launches only. The first that passes is scorer 2 and takes Granite's place
everywhere in this file. If neither passes before the freeze, A4 is "not run: no candidate passed
the pre-registered technical bar". V3's interval is the launch-cluster percentile bootstrap already
in `analysis\a4_bar.py` (B = 10,000, seed 20261121), confirmed as the interval of record.

## Rules that apply to every row

- **Cost.** Modal prices from `modal_serving\README.md`: Qwen3.8-27B container $4.84/h
  ($0.001344/s), Gemma-4-12B container $2.40/h ($0.000665/s), fixed cost per session about
  $0.32 (Qwen) and $0.16 (Gemma). Throughput on long prompts is **unmeasured**. So each Modal
  job starts with a 200-call probe; the projected cost is logged to `ledger.csv` before the
  main job starts (BRIEF §3.5).
- **Cap enforcement.** The Modal session's `max_seconds` is set from the cap, so a job cannot
  spend past it. Caps come from BRIEF §11.
- **Random-prefix rule.** Scoring jobs process launches in a fixed random order
  (`random.Random(20261125)` over sorted `launch_id`s, all rounds of a launch together). If a
  cap or timeout stops a job, the analysed set is the launches completed so far, which is a
  random subset. The count is reported.
- **Council.** Any job with a cap over $5 and every Tier-4 experiment needs the experiment
  council (two of three votes) before launch.
- **Stop only on evidence** (BRIEF §5): pilot shows no signal, cap hit, or council rejects.
- **Owner** follows the model router (BRIEF §6): Sonnet writes and runs, Opus reviews
  statistics and evaluates, Fable takes gate decisions, Haiku watches logs and the ledger.
  The reviewer is never the author and starts with fresh context.
- **CPU timeout.** 30 minutes per script; a script that exceeds it is killed and investigated.

## Dependency order

```
0 ──► build_analysis_set ──► scorer manifest + dev-set smoke test ──► g1_sample ──► packets
                                                                          │
              (humans label)  L1.csv, L2.csv ──► kappa ──► ADJ.csv ──► A1 gate recorded
                                                                          │
 full scoring (scorer 1) may run while waiting ───────────────────────────┤
                                                                          ▼
                                               A2 ──► N1, A4, A3, N3, N4 ──► N2 ──► N5
 Tier 4 (N6, B, F): independent of the gate; each needs council approval first.
```

**[R1]** Added to the order: full scoring (scorer 1, E1 v2) ──► **A2-tier** (`A2_TIER.json`,
shuffled ranks only) ──► logged in decisions.md ──► only then may A2 read real ranks (and only
with `GATE1_RESULT.json`). N2 generation does not wait for any of this; N2 scoring waits for
gate 1 PASS as before. If the tier is not INFORMATIVE, N2 scoring and `prevalence.py` move ahead
of Tier 2 in the queue, because they carry the paper (FR §7.3). Nothing is dropped.

**[R4]** The order after the human edits (the diagram above shows the older two-labeler flow):

```
extended N2 generation (3 new generators) ──► n2_items.json ──► packets (author pass 1, pass 2, volunteer) + SHARE.md
scorer-2 development smoke (V1) ; LLM-annotator format try-out ; A2 tier re-run on the confirmatory set
        │
 author_pass1.csv complete = GATE TIME ──► DESIGN.json (volunteer file present? two-human : single-labeler)
        │
 single-labeler: validity on pass 1 ──► PROVISIONAL_PASS ──► A2, Tier 2 (stamped PROVISIONAL; no N2 scoring yet)
                 author_pass2.csv (≥ 1 h later) ──► self-consistency kappa ──► PASS or FAIL (stamps updated) ──► N2 scoring on PASS
 two-human:      inter-rater kappa ──► ADJ.csv ──► validity ──► PASS or FAIL ──► A2, Tier 2, N2 scoring
        │
 N2 check on the 12 packet items ──► N2_VALIDATED or EXPLORATORY ; scorer-2 bar V2, V3 ──► A4_BAR.json
```

## Tier 1 addition **[R1]**

| | A2-tier. Is A2 informative? |
|---|---|
| Purpose | Fix, before any real rank is read, which claims A2 may support (FR §7.1) |
| Inputs | Scorer-1 `E` for all eligible rounds (after the E1 v2 run); real statements; within-rater shuffled ranks |
| Script | `a2_informativeness.py` (to write) |
| Output | `gate1\A2_TIER.json`: `R_inf`, `K_inf`, `MDE80` (400 reshuffles, `random.Random(430000 + i)`), tier, hashes; same counts without the development launches, for `E_pos` and for scorer 2 when available |
| Decision rule | INFORMATIVE: `K_inf ≥ 100` and `MDE80 ≤ 0.10`. LOW-POWER: `K_inf ≥ 50` otherwise. NOT MEASURABLE: `K_inf < 50`. Thresholds are not moved after the counts are seen |
| Cost / cap / timeout | $0 / $0 / 30 min (400 fits; if too slow, the run is split, never shortened) |
| Stop condition | None. A missing `A2_TIER.json` blocks real-rank A2 |
| Depends on | Full scoring run; rank-direction check |
| Owner | Sonnet (stats coder); Opus re-derives `K_inf` from the score file; planning room logs the tier |
| What the paper says | INFORMATIVE: A2 leads. LOW-POWER: A2 in the main text with `R_inf`, `MDE80` and the low-power wording; prevalence and N2 lead. NOT MEASURABLE: no directional claim; prevalence and N2 lead |

## Tier 1

| | 0. Rank unit | A1. Gate 1 | A2. Within-round |
|---|---|---|---|
| Purpose | Confirm in writing that ranks are per rater, and the rank direction | Validate scorer 1 against blind human labels | Rank vs erasure, the confirmatory test |
| Inputs | Parquet (ID, rank, rating columns only); repo `analysis/types.py` | `gate1\sample.json`; scorer-1 scores for the 60 items; `labels\L1.csv`, `L2.csv`, `ADJ.csv` | Analysis set; scorer-1 `E` for all eligible rounds; features (length, Flesch, own-similarity); `GATE1_RESULT.json` |
| Status | **Done: per rater** (decisions.md D6, `analysis\EXP0_rank_unit.md`). Still open: the rank-direction check of FR §2 | Not started; waits for labels | Built and tested on dummy and shuffled data; must be aligned with FR §7 |
| Scripts | `exp0_check.py` (exists); add the rank-direction check; then `build_analysis_set.py` | `g1_sample.py`, `g1_packets.py`, `score_erasure.py --set gate`, `gate1.py` (exists; kappa step first, then `g1_adjudication_sheet.py`, then the validity step) | `score_erasure.py --set all`, `features.py`, `make_dummy_labels.py` (exists), `a2_within_round.py` (exists) |
| Cost estimate | $0 (local CPU) | About 120 Qwen calls in one session: fixed $0.32 plus generation; probe decides. Labelling is human time | 1,960 extraction + 7,840 labelling calls on Qwen. Unmeasured; scaling the 4-prompt smoke test to 32-way concurrency gives roughly $4 (ASSUMPTION, short outputs), could be more |
| Cost cap | $0 | $1.00 | $5.20 (needs council) |
| Timeout | 30 min | Modal `max_seconds` 600; CPU 30 min | Modal `max_seconds` 3,700; CPU 30 min per fit |
| Stop condition | FR §11 rule says per group → follow BRIEF §14 (see PLAN). Rank direction unconfirmed → A2 and N1 blocked | Gate FAIL → "not yet measurable" version (FR §12). No labels → keep polling, never substitute | Cap hit → random-prefix rule. FR §7 floor fires → report as not measurable. **[R1]** A2 runs in every tier; the tier (FR §7.1) sets the wording, not whether it runs |
| **[R1]** Added reports | — | FR §6.4a: `BA_crux`, `BA_sh`, zero-crux share, wording-rule flag, `D1h`, scorer-v1 comparison. Gate scores of record are the E1-v2 re-score | `R_inf`, `K_inf`, `MDE80`, tier, A2i; interval method per FR §7 (D19 selection) |
| **[R4]** Now | — | Inputs: `sample.json` (first 38), `n2_items.json` (12), scorer-1 scores for the 50 items, `labels\author_pass1.csv`, `author_pass2.csv`, optionally `volunteer_pass1.csv` + `ADJ.csv`. Design by `DESIGN.json` (FR §6.0). Outputs add: kappa of the design with CI and AC1, `PROVISIONAL_PASS`, N2 check, headline `H`, LLM-annotator figures, scorer-2 bar. The "20 shared / L1 / L2 / 60 items" wording in the cells above is superseded. Extra cost: scorer 1 on 12 N2 items (cents); LLM annotator 50 calls + ≤ 20 try-out calls; both under the $5 council line, estimate logged first | Data = confirmatory set (721 non-development launches); all-launch fit = A2d only; tier of record re-run on that set. In the single-labeler design the first real run is PROVISIONAL |
| Depends on | Nothing | 0; scorer manifest; human labels | A1 recorded. Before that, shuffled or dummy data only |
| Owner | Sonnet (stats coder); Opus reviews | Sonnet (scorer runner, stats coder); Haiku polls; Opus re-derives kappa and the gate independently; Fable records the gate decision | Sonnet (stats coder); Opus statistics review; results room approves numbers |

## Tier 2 (same data, all run after A2)

| | N1 | A4 | A3 | N3 | N4 |
|---|---|---|---|---|---|
| Purpose | Winner vs average candidate | Second scorer | AI-written vs human-written | First draft vs revised | Minority vs majority raters |
| Inputs | Scorer-1 `E`; per-rater ranks | Analysis set; Gemma-4-12B; gate labels (for its own balanced accuracy) | Rounds with mixed provenance (count from `build_analysis_set.py`) | Iteration-1 candidates of eligible rounds; cruxes from E1 | Scorer-1 crux member lists; per-rater ranks |
| Script | `n1_winner_vs_mean.py` (exists) | `score_erasure.py --scorer gemma4-12b`, `a4_second_scorer.py` | `a3_ai_vs_human.py` | `n3_draft_vs_revised.py` | `n4_minority.py` |
| Cost estimate | $0 | 9,800 erasure calls, then up to 7,840 clarity calls (A2c) on Gemma; unmeasured, probe decides | Extra Qwen labelling for the mixed rounds; size unknown until counted | Up to 4 extra Qwen label calls per round with iteration-1 candidates | $0 |
| Cost cap | $0 | $2.00 | $1.80 shared with N3 | (shared with A3) | $0 |
| Timeout | 30 min | Modal `max_seconds` 2,850 | Modal `max_seconds` 600 | Modal `max_seconds` 600 | 30 min |
| Stop condition | None beyond the timeout | Cap hit → erasure scoring first, A2c only with what is left; random-prefix rule | Fewer than 30 qualifying launches → not run, reported as "data does not allow" | Same 30-launch rule | Per-group ranks → skipped |
| Depends on | A2 | A1 recorded | A1 recorded; count step | A1 recorded; count step | A2; per-rater ranks |
| Owner | Sonnet; Opus review | Sonnet (scorer runner); Opus review | Sonnet; Opus review | Sonnet; Opus review | Sonnet; Opus review |

Tier 2 total cap $3.80; with A1 and A2 the core is $10.00, the BRIEF §11 line.

**[R4] Tier 2 after the human edits.** All five family tests run on the confirmatory set
(development launches excluded); each may print a with-development figure beside it, outside the
Holm family. **A4** in the table above is superseded: the second scorer is granite-4.2-30b
(fallback granite-4.2-8B), not Gemma-4-12B. What runs now: development smoke ≥ 200 calls (V1), the
50 packet items, and a seeded 1,000-statement sample (250 rounds, seed 20261133), giving scorer 2's
balanced accuracy against the human labels (V2) and its agreement with scorer 1 (V3) →
`gate1\A4_BAR.json`. Script `score_erasure.py --scorer granite4.2-30b`. Cost from the
"council-approved new experiment" pool (D36); probe first, estimate logged. The full refit of A2
under scorer 2 (about $5.9 worst case, D36) is deferred to a separate council vote; it is a Holm
family test only if that vote is recorded before the first real-rank run and V1 and V2 are met
(FR §8). A2c (LLM clarity) runs only with that full run.

## Tier 3 (new runs, exploratory)

| | N2. Prompt grid | N5. Shift to agreement |
|---|---|---|
| Purpose | Do current models hide more under "keep everyone satisfied / find common ground" prompts? | Is a hiding winner associated with a larger apparent shift to agreement? |
| Inputs | Opinions only, from the seeded sample of eligible rounds fixed by `n2_grid.py --mode plan` (`plan.json`, hashed before launch). 2×2: system prompt (keep everyone satisfied / be accurate about differences) × user prompt (find common ground / show where they disagree). Writers: the Modal-served models. Statements are scored by scorer 1 with the existing opinion-derived cruxes | N1 output; `hm_all_position_statement_ratings.parquet` and round-survey `view_movement` |
| What it adds to prior work | Mahajan et al. (arXiv:2611.05135) already report, with an LLM judge and no human check, that agreement prompts cover minority positions less. N2 adds (a) a scorer validated against blind human labels and (b) the system-prompt × user-prompt split, which shows whether a system-level instruction to be accurate survives a user-level request for common ground. If gate 1 does not pass, (a) is gone and N2 is reported as generation only, unscored | n/a |
| Script | `n2_grid.py` (exists: plan, dry-run, smoke, launch modes; generation only), then `score_erasure.py --set n2` | `n5_shift.py` |
| Cost estimate | Written by `n2_grid.py --mode plan` and its smoke mode before launch; scoring adds one label call per statement | $0 |
| Cost cap | $10 (needs council) | $0 |
| Timeout | Modal `max_seconds` 3,600 per writer | 30 min |
| Stop condition | Cap hit; or a 20-launch pilot shows parse failure above 20% | None beyond the timeout |
| Depends on | Generation: council approval only. Scoring: A1 recorded as PASS (the scorer must be valid to score new text) | N1 |
| Owner | Sonnet (grid runner); Opus evaluation | Sonnet; Opus review |
| Limits to state | Scorer 1 shares a family with one writer; statements are not ranked by humans, so N2 says what models write, not what people reward | Shift measures are self-reports; exploratory |
| **[R1]** Place in the paper | Lead result, with prevalence, if gate 1 is PASS and the A2 tier is not INFORMATIVE (FR §7.3), and only if its manipulation check passes. Never the confirmatory test of the rank question. Design, sample, cells and tests are those of `analysis\N2_ANALYSIS_SPEC.md` and decisions.md D12, D13 (runner), D20 (250 rounds, 5 cells, k = 1), which supersede the "Inputs" cell above where they differ. If gate 1 fails, N2 is generation only and cannot lead | If the tier is NOT MEASURABLE, N1 has almost no non-zero `d_r`, so N5 is reported as not measurable too |

**[R4] N2 after the human edits (supersedes the N2 column above where they differ).**
Generators: Qwen3.8-27B, Gemma-4-12B (2,500 statements already generated, kept) plus
Ministral-3-14B, phi-4 and Llama-3.1-8B-Instruct (3,750 to generate): same 250 rounds, 5 cells,
k = 1, prompts and decoding. Cap $15 (D36). Spec of record: `analysis\N2_ANALYSIS_SPEC.md` with
Amendments 1 and 2, SHA-256 `126787ad8c4932a3b4c9776f274e87b2e27787cd9cc7215cfe54e9f42c0dc60b`;
the earlier references in this file to decisions D12, D13, D20 and to hashes `3875c61e…` and
`707c7fa2…` are historical. Any further amendment: council vote, new hash computed by the code
owner and logged in decisions.md before scoring. Scorer 1 is the read of record for all five
generators (Qwen column marked same-family scored); Granite is the robustness read; every result is
split by generator; length is a covariate in every model. Two Holm families as in the spec (10 tests
for the first two generators, 15 for the three added). Twelve N2 statements go into the labelling
packet and are scored by scorer 1 as gate items (FR §6.1a); the N2 check on them (FR §6.6) decides
whether N2 results are labelled `N2_VALIDATED` or `EXPLORATORY`; `N2_VALIDATED` applies to scorer-1
estimates without the 45 development-launch rounds. Apart from those 12 items, no N2 statement is
scored and no N2 analysis runs before gate 1 is recorded. The line "Scorer 1 shares a family with
one writer" in "Limits to state" still holds and now reads: one of five.

## Tier 4 (council approval needed before anything runs)

| | N6. Hidden instruction | B. T1-1 pilot | F. Fine-tune test |
|---|---|---|---|
| Purpose | Does one opinion carrying a hidden instruction tilt the statement? | T1-1 temporal-calibration pilot on Modal GPU; stop the CPU run | Does training to score well on honesty-benchmark-style items change behaviour on held-out honesty benchmarks? |
| Inputs | **Synthetic opinions only** (hard rule 6); no participant text | `pilots\T1_1\`; chair ruling §4.2 protocol | New items written in a benchmark's style, never its test items. Minimum: 3 trained runs, 3 neutral-control runs, 2 held-out honesty benchmarks |
| Script | `n6_injection.py` | `b_t1_1_modal.py` | `f_finetune.py` |
| Cost estimate | To be written into the council request after a 20-call probe | To be written into the council request; the earlier $8 figure was set before the brief | To be written into the council request, per run, before any GPU starts |
| Cost cap | $5 | $10 | $25 minimum; $40 expansion only after a clean minimum result |
| Timeout | Set in the council request | Set in the council request | Set per run in the council request |
| Stop condition | Council rejects; cap hit; pilot shows no tilt | Council rejects; cap hit; chair ruling §4.2 stop rules | Council rejects; cap hit; minimum shows no clean result → no expansion. Weights are never released |
| Depends on | Council | Council | Council |
| Owner | Sonnet (grid runner); ethics and dual-use reviewer signs off | Sonnet (T1-1 runner); Opus review | Sonnet (fine-tune runner); Opus evaluation; cost cutter picks the GPU |

Second submission slot: B or F, whichever has the stronger verified result (BRIEF §5).
Not run: personalization drift; rewrite test.

## Budget check against BRIEF §11

| Line | Brief | Allocated here |
|---|---|---|
| T3-1 core and Tier 2 | $10 | A1 1.00 + A2 5.20 + A4 2.00 + A3/N3 1.80 = 10.00 |
| N2 | $10 | 10 |
| N6 | $5 | 5 |
| B | $10 | 10 |
| F minimum | $25 | 25 |
| F expansion | $40 | 40, locked until the minimum is clean |
| Council-approved new experiment | $30 | unallocated |
| Buffer | $20 | $0.65 already spent on Modal setup is booked here |
