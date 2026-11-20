# FROZEN_RULES.md — T3-1 crux erasure pre-registration

**DRAFT — [R5] freezes (read-only) at the first of: (a) any file appearing in `P\labels\` (expected:
`author_verification.csv`; any other name is reported and not read); (b) the first run of
`analysis\step2_reference.py` on real data. `P\gate1\FREEZE.json` is always written (by
`analysis\freeze.py`, `--trigger labels` or `--trigger step2`) BEFORE the step-2 reference is computed;
`step2_reference.py` writes it itself if it is absent and refuses to run otherwise (§6.R5.1).**
([R5], D49–D51. Before R5 the trigger was `author_pass1.csv` or `volunteer_pass1.csv` ([R4], D34, D37), and
before R4 `L1.csv` or `L2.csv`. None of these files exists in the R5 design; if one appears it is reported
and nothing reads it.)

P = `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1`.
Written 2026-11-15 by the planning room from BRIEF.md, the pre-brief `pilots\T3_1\PREREG.md`,
the chair ruling, the methodologist and statistician briefs and `data_gates.md`.

**Blindness statement.** The author of this file has not opened any output that relates an
erasure measure to real rankings or ratings (`features.parquet`, any output of `s06_analyze.py`,
any label file). Files read from the pilot: `PREREG.md`, `s03_prep.py`, `s04_judge.py`,
`eligible_groups.json`, `exp0_rank_unit.json` (rank-unit check, no erasure measure),
the first lines of `run_extract.log` (crux counts per round) and the header row of
`HUMAN_LABEL_SHEET.csv`.

**At freeze.** The poller sets this file read-only, writes its SHA-256 and the UTC time to
`P\gate1\FREEZE.json` and to decisions.md. After that, any analysis not defined here is
exploratory (BRIEF §3.10). Before freeze, only the human or the planning room may edit, and
every edit gets a decisions.md entry.

**Supersession.** This file replaces `pilots\T3_1\PREREG.md`. Differences are listed in §13.

Every table has a "Why" column: one line of reason per choice. Thresholds marked **(J)** are
judgement calls, not derived from a power analysis.

**Replan R1 (decisions.md D21, 2026-11-15, before any label file exists).** Rows changed or added
by the replan are marked **[R1]**. The full list is in the "Replan log" at the end of this file.
The replan used only scorer outputs on opinions and statements (label counts, within-round
variation of `E`). No ranking, rating or label was read. BRIEF §4 definitions are unchanged.

**Replan R4 (decisions.md D31, D34, D36, D37, 2026-11-15 UTC, before any label file exists).** Rows
changed or added are marked **[R4]**. R4 writes in the HUMAN-authored rule edits of D31 (19:06Z) as
superseded in part by D34 (19:10Z; decisions.md calls that second set "R5") and extended by D37
(19:16Z, optional volunteer labeler), together with the experiment council's model choices (D36).
All of it is consolidated here under the one tag [R4]. **These edits change BRIEF §3.1 and §4** (who labels, the agreement
statistic, the packet design, the label file names). The human owns the brief; the authority for
every such change is D31/D34, cited in the row. Where an older row, the "Not changed" paragraphs of
R1 to R3, or an older log entry says "BRIEF §4 is unchanged", "L1/L2", "20 shared", "60 gate
items", "adjudication" or "blind labeler", the [R4] rows govern. The full list, with what D34
replaced from D31, is in the "Replan log" at the end. No ranking, rating, label or rank-related
output was read for R4; the two design calculations it cites use synthetic labels only.

**Replan R5 (decisions.md D49, D49a, D49b, D49c, D50, D50a, D51; 2026-11-16 UTC; `labels\` empty, no
`FREEZE.json`, checked at 2026-11-16T01:17:05Z immediately before the edit).** The human replaced the
labelling design (D49): no volunteer, no 50-item labelling. Gate 1 is now §6.R5: step 2, a participant
presence check from pre-deliberation position ratings; step 3, the author's verification of LLM-extracted
evidence on 25 items, with a 30-minute time-out (D51); step 4, an LLM panel (supplementary; not human);
step 5, the exploratory fallback. **Where any older row conflicts with §6.R5, §6.R5 governs.** Rows changed
by R5 are marked **[R5]**; the R4 sections 5 and 6.0–6.8 are marked superseded and kept verbatim for the
audit trail. Full list in the Replan log ("R5"). The design was approved by the council 3/3 with
conditions (`analysis\council\R5_vote_*.md`; proposal `analysis\council\R5_PROPOSAL.md`). No score,
rank, rating value, label or critique text was read for R5.

**[SUPERSEDED by R5 — kept for the audit trail, not in force; the R5 wording is in §6.R5.8.]**
**Validation label [R4] (D34 item 9, D37 item 5; binding wording).** Which of two designs applies is
decided by §6.0. **Single-labeler design:** everything that this file calls validated (gate 1, the
scorer, `N2_VALIDATED`, the labels behind the headline rate) is described in the paper as
"validated against a single hypothesis-aware human annotator", in the abstract, in the methods and
at first use in the results. The human labels are never called "blind" without qualification: the
annotator did not see scores, rankings, model or condition, and did know the hypothesis.
**Two-human design:** the wording is "validated against labels from two human annotators, a
hypothesis-blind volunteer and the hypothesis-aware author, with disagreements adjudicated by the
two together without sight of scores, rankings, model or condition". The volunteer is called a
"hypothesis-blind human annotator", never an expert, a consultant or an independent rater panel.
The validation is not called "blind validation": one of the two annotators, and one of the two
adjudicators, knew the hypothesis. The balanced accuracy against the volunteer's own labels before
adjudication (§6.4) is printed in the same table as the gate number. **Both designs:** no sentence
may call the LLM annotator of §6.8 a human, a second rater or an inter-rater check.

---

## 1. Question, hypothesis, primary estimand

| Item | Rule | Why |
|---|---|---|
| Question | Within a round, do participants rank statements that hide the group's real disagreement better than statements that show it? | BRIEF §1. |
| Hypothesis direction | None fixed. The test is two-sided. | The original study reports that statements incorporated minority views; either sign is a result. |
| Single confirmatory estimand | `beta_E` in the A2 model (§7), scorer 1, per-rater ranks. **[R1]** It stays the only confirmatory test of the rank question. What may be claimed from it depends on the informativeness tier fixed in §7.1, which is computed without real ranks. | One primary estimand (statistician rule 2). No other measure is promoted: see §7.2. |
| **[R1]** Expected outcome, stated in advance | *([R4] note: this expectation was written from the development probe. The full scoring run has since shown more variation than the probe suggested: decisions.md D32 and D35 report, from scorer output and shuffled ranks only, 168 launches with an informative round, 144 of them outside the development launches, and an all-launch tier of INFORMATIVE. The row is kept as written, because it is what was expected in advance. The tier of record is the one recomputed on the confirmatory set, §7.1.)* On the 40-round development probe, `E` varied within the round in 3 of 34 evaluable rounds (13 of 34 under A2e); 186 of 216 crux labels were `SIDED`. The planning room therefore expects the A2 tier to be LOW-POWER or NOT MEASURABLE more likely than INFORMATIVE. That outcome is a pre-registered result, not a failure to be repaired. | Said before the data, so a "not measurable" paper cannot be read as a post-hoc retreat. |
| Claim wording allowed on a positive result | "Rankings were associated with ..." Observational only. | Raters wrote the opinions; no causal design. |
| Name of the measure | "Crux erasure score", never bare "Erasure". | Zaghouani (arXiv:2605.26940) already uses "Erasure" for an embedding formula (decisions.md D5). |
| Prior-work sentence | "Prior work did not link what participants reward to disagreement-hiding content." Not "prior work measured only what statements contain". | Tessler et al. also measured rankings (decisions.md D4). |

## 2. Data and unit of analysis

| Item | Rule | Why |
|---|---|---|
| Source file | `_apart_intel\data\habermas_gcs\hm_all_candidate_comparisons.parquet`, SHA-256 `7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4` (measured by `s08_exp0_rank_unit.py`). Every script re-checks the hash and stops on mismatch. | BRIEF §3.4: every number traces to a data hash. |
| Round | One `(launch_id, round_id)` at `iteration_index == 0`. | Iteration-0 statements are written from opinions only, before any critique. |
| Group / cluster | `launch_id`. | The same people answer several questions in one launch; rounds in a launch are not independent. |
| Statement | One of the round's 4 candidates. | The thing that is scored and ranked. |
| Observation in A2 | One (rater, round, statement) rank. | Outcome is each rater's own ranking (per-rater ranks; see §11 for the fallback). |
| Eligibility filter | A round is eligible if all hold: (a) every opinion in the group has provenance `HUMAN_CITIZEN`; (b) no `BOT_CITIZEN` critique anywhere in that (launch, round); (c) exactly 4 candidates, all provenance `MODEL_MEDIATOR`; (d) no candidate equals "Citizen's Jury" and every candidate has ≥ 15 whitespace-separated words; (e) ≥ 3 raters whose ranking and rating rows are `HUMAN_CITIZEN`, whose `rankings.candidate_ids` match the round's candidate IDs, and whose 4 ranks contain no `-1`. | Same filter as `s03_prep.py`, fixed before the brief and before any outcome was joined. Conservative on bots: a round touched by a bot at any stage is not an all-human deliberation. |
| Measured size under this filter | 1,960 rounds, 871 launches, 9,501 rater rows (`pilots\T3_1\eligible_groups.json`). `build_analysis_set.py` must reproduce these counts or stop. | A count mismatch means the filter was not reproduced. |
| Development set | The 150 launches in `pilots\T3_1\pilot_groups.jsonl` (file SHA-256 recorded in `P\analysis\scorer_manifest.json`). Prompts may be tried on these, using opinions and statements only. **[R4]** "Development launches" means every round of these 150 launches. That includes the 40 development-probe rounds on which the scorer prompts were tried and revised (29 to 35 of them evaluable, depending on the prompt version; decisions.md D17, D22) and the pilot's rounds (D33). | Prompt development must not touch the gate-1 sample. |
| **[R4]** Analysis set (confirmatory set) | **Eligible rounds of the 721 eligible launches that are not development launches** (871 − 150; `labels_build\README.md` reports 721). `build_analysis_set.py` writes the confirmatory set, must reproduce 721 launches or stop, and records its round and rater-row counts in `P\analysis\analysis_set_manifest.json` before any real rank is read. **Every confirmatory or family test in this file is computed on this set and on nothing else:** gate 1 (§6), the N2 scorer check (§6.6), the headline rate (§6.7), A2 `beta_E` and the §7.1 tier, the Tier-2 family tests N1, A4, A3, N3, N4 (§8), and the §7.3 prevalence quantities. The all-launch version (871 launches, development launches included) is computed for A2 only as sensitivity model A2d and for the tier counts as a printed side figure; it is never the estimate of record, never tested in a family, and never quoted without the words "including the development launches". Before R4 this row made the all-launch A2 primary and the development-free A2 the secondary; that order is reversed. | D31 edit 6 / D34 item 8 (human): development rounds are excluded from confirmatory tests. The scorer's prompts were revised after looking at its output on these launches, and the pilot stored cheap erasure proxies beside real ranks for them (D33), so they cannot carry a confirmatory result. |
| Rank direction | `numerical_ranks` 0 = best. Must be confirmed in experiment 0 from the repo's `analysis/types.py` and by the sign of the within-rater association between rank and the rater's own `ratings.agreement`. If it cannot be confirmed, A2 and N1 do not run. | The one sampled example suggests 0 = best; one example is not confirmation. This check uses no erasure score. |
| Ties in ranks | Kept, as mid-ranks. A rater whose 4 ranks are all equal carries no information and is dropped and counted. | Ties exist in the data (`exp0_rank_unit.json`); dropping tied raters would discard real responses. |

## 3. The group's real disagreement (cruxes), from the opinions only

| Item | Rule | Why |
|---|---|---|
| Definition | A **crux** is a specific point on which at least one member asserts or prioritises something that at least one other member denies, rejects or weighs very differently. Points everyone agrees on, and differences only of wording, emphasis or example, are not cruxes. | BRIEF §4: disagreement is defined from the opinions, not the rankings. |
| Inputs to crux derivation | The question text and the members' opinion texts. Nothing else. The extractor never receives candidate statements, rankings, ratings, critiques, cohort or any outcome. `score_erasure.py` must build the extraction prompt from a table that contains only these columns (asserted in a unit test). | Keeps the predictor free of outcome information. |
| Opinion order | Opinions sorted by `participant_id`, numbered from 1, untruncated. A round whose prompt exceeds the served context length is dropped and counted. | Deterministic; an outside judge can rebuild the prompt. |
| Extraction | One call per round, prompt E1 (Appendix A), 0 to 4 cruxes, most important first, each with the member numbers on side A and side B. | Cap of 4 as in the pilot; member lists are needed for N4. |
| **[R1]** Side membership | A member is listed on a side only if that member's own opinion states or clearly implies that position. A member who did not address the point is on neither side; silence is not opposition. Parse rule in `scorer.py`: a crux whose `members_a` or `members_b` is empty after sanitising is dropped, counted and reported; a round left with no crux is a zero-crux round. | Enforces the definition in the row above ("at least one other member denies, rejects or weighs very differently"). The first extractor put silent members on the opposing side (decisions.md D18, skeptic F1). This is conformance to the existing definition, not a new one. |
| Zero cruxes | The round has no measurable disagreement. Its erasure score is undefined for A2/N1 (round excluded and counted). For gate 1 see §6. | A statement cannot hide what is not there. |
| Human counterpart | Labelers derive the disagreement themselves from the same opinions (§5). They never see the AI's crux list. | Gate 1 then tests the whole instrument end to end, not just the last step. |

## 4. The erasure score

| Item | Rule | Why |
|---|---|---|
| Scorer 1 (primary) | `Qwen/Qwen3.8-27B`, revision `37561816e66b5b9153b1b64c10968c18c1e6f4a0`, served by `modal_serving\serve_vllm.py` alias `qwen3.8-27b`. | Largest deployed and smoke-tested rung; revision pinned. |
| Scorer 2 (A4) **[R4]** | **No longer `google/gemma-4-12B-it`** (it is an N2 generator). Scorer 2 is **`granite-4.2-30b` (IBM)**, alias `granite4.2-30b` in `P\serving\endpoints.json`, served with **no reasoning parser** and thinking off; fallback **`granite-4.2-8B`** under the rule of §6.9 only. Chosen by the experiment council, 3 of 3 approve with conditions (decisions.md D36; `analysis\council\EXT_vote_*.md`). The repository revision is not in D36; the scorer runner pins it in `scorer_manifest.json` before scorer 2's first call on any non-development item, and it does not change after. Scorer 2 runs both steps (extraction and labelling) itself, with the prompts and decoding of this section unchanged. It may not be used for anything until it has met the bar of §6.9. **[R4a]** Both Granite models missed the technical bar (decisions.md D44). Scorer 2 is now the first of the two ordered candidates in §6.9 that meets it (`tiiuae/Falcon-H1-34B-Instruct`, then `CohereLabs/c4ai-command-r7b-12-2024`); if neither does before the freeze there is no scorer 2 and A4 is "not run". Wherever this file says "Granite" for scorer 2, read "scorer 2 as determined by §6.9". | D31 edit 3 / D34 item 5 (human): the second scorer must come from a family different from every N2 generator. |
| **[R4]** Model-family rule | A "family" is one developer's model line; fine-tunes, merges, quantisations and distillations of a model belong to its family (so every Qwen model is one family, and Gemma and Gemini are one family). Roles as filled by decisions.md D36: scorer 1 = Qwen3.8-27B (Alibaba Qwen, fixed above); scorer 2 = granite-4.2-30b (IBM Granite); N2 generators = Qwen3.8-27B, Gemma-4-12B (Google), Ministral-3-14B (Mistral), phi-4 (Microsoft), Llama-3.1-8B-Instruct (Meta), §10; LLM annotator = gpt-oss-120b (OpenAI), §6.8. Olmo-3.1-32B was rejected by the council because its training data draws on Qwen3 and gpt-oss-120b outputs (D36). Required: (a) scorer 2 shares a family with no N2 generator and not with scorer 1; (b) the LLM annotator shares a family with neither scorer and with no N2 generator; (c) every added N2 generator is from a family not yet used by any role. The one overlap that remains is the existing one: scorer 1 is Qwen and Qwen is also an N2 generator. It cannot be removed without changing the scorer that was already built and run; it is handled by splitting every N2 result by generator and flagging the Qwen-written cells as same-family scored (§10). | D31 edit 3; D34 items 4, 5 and the orchestrator's choice under D34 (all new roles mutually distinct). A judge must not grade its own family's text unseen. |
| Decoding | temperature 0, seed 0, JSON output; `max_tokens` 700 (extraction), 300 (labelling). Reasoning/thinking mode off if the served template supports it; the setting actually used is written to `scorer_manifest.json` before freeze and does not change after. | Deterministic and auditable. The thinking switch is unverified today, so it is recorded rather than assumed. |
| Prompt location | Text of record: Appendix A of this file. Working copies: `P\analysis\prompts\E1_extract.txt`, `L1_label.txt`, `C1_clarity.txt`, byte-identical to Appendix A; their SHA-256 values go in `scorer_manifest.json`. | The frozen file carries the prompts, so freezing it freezes them. |
| Labelling | One call per statement (not four statements per call). Per crux, exactly one of `VISIBLE`, `SIDED`, `BLENDED`, `OMITTED`. | Scoring statements separately avoids contrast effects between candidates. |
| Hidden | A crux is **hidden** by a statement if its label is `SIDED`, `BLENDED` or `OMITTED`. It is **shown** only if `VISIBLE`. | The construct is "hides the disagreement": a reader of a one-sided statement does not learn that anyone disagreed. |
| Score and scale | `E(s) = (number of hidden cruxes) / (number of cruxes)`, in [0, 1]; 0 = shows every crux, 1 = hides every crux. | Continuous share; simple to recompute by hand. |
| Parse failure | One retry with seed 1. If it still fails, `E` is missing. In A2/N1 a round with any missing `E` is dropped and counted. In gate 1 a missing `E` counts as a wrong prediction. Parse-failure rates are reported per scorer and step. | Failures are kept and counted, never silently dropped (methodologist checklist). |
| Weighting | Unweighted. A member-weighted variant is reported as sensitivity model A2g (§7). | No validated salience weights exist; an unweighted share can be checked by hand. |
| Order check (diagnostic, no rule) | On the gate items only (**[R4]** the 50 packet items of §6.1), labelling is repeated once with the crux list reversed and sides A/B swapped. The share of items whose binary call changes is reported. The score of record is the original order. | Judge position bias is documented; one deterministic pass stays the instrument so the score is reproducible. |
| Pre-freeze prompt changes | Allowed only to fix output-format or parse problems seen on the development set, at most one revision, logged in decisions.md. No change after freeze, for any reason. **Used once (decisions.md D18/D19, 2026-11-15, before any label existed):** one sentence block added to E1 so that silence is not read as opposition; verified on the development set only; v1 draft preserved in `analysis/v1_archive/`. No further revision. **[R1]** Disclosure: the defect was first seen in AI extractions on gate-sample items, when no label existed. The 60 gate items are re-scored once with E1 v2 and that result is final; E1 v2 is the scorer of record. After labels exist, gate-1 balanced accuracy is also computed with the archived v1 gate scores and printed in the appendix (§6.4a). | BRIEF §4: never change definitions. The v1 number is printed so the revision cannot be selected on outcome. |

## 5. Gate-1 labelling instrument

**[SUPERSEDED by R5 (§6.R5) — kept for the audit trail, not in force.** No human labels with this instrument
under R5; the packets in `labels_build\r4\` are VOID (D49). The instruction text below is not reused: the
R5 LLM panel answers the two packet questions instead (task P2 dropped, D50).**]**

| Item | Rule | Why |
|---|---|---|
| **[R4]** Labeler | **One human labeler: the author, who knows the hypothesis.** There is no consultant and no hypothesis-blind human. Files `P\labels\author_pass1.csv` and `P\labels\author_pass2.csv`, written only by that human. (Before R4: L1 consultant, blind to the hypothesis, and L2 author, in `L1.csv` and `L2.csv`.) | D34 item 1 (human), superseding BRIEF §3.1 and D31 edit 1. |
| **[R4]** Optional second labeler | A volunteer who is not told the hypothesis and is given no project note may label the same 50 pass-1 items once. File `P\labels\volunteer_pass1.csv`, written only by that human and saved into `labels\` by the author unchanged. The volunteer has no second pass. Whether this file counts is decided by §6.0 and by nothing else. The only label files are `author_pass1.csv`, `author_pass2.csv`, `volunteer_pass1.csv` and, in the two-human design, `ADJ.csv`. | D37 (human). |
| **[R4]** Volunteer packet | The same 50 items in a different order (`random.Random(20261135)`), each with a fresh opaque `item_id` of its own, as one spreadsheet-friendly file plus one instructions file. It contains the question, numbered opinions, statement and the empty label columns, and nothing else: no score, ranking, model name, condition, hypothesis or project note, and no author item id. The volunteer's ids are mapped to the items by the key file only. `SHARE.md`, written by the packet builder, lists the exact files that may be sent, the files that may never be sent, the returned file name and columns, and the path where the author saves the returned file. | D37 items 1 and 2. A different order keeps the two humans' order effects from lining up. |
| Item | One statement with its round's question and all members' opinions. **[R4]** An item is either an original statement (one of a round's 4 candidates in the source data) or an N2 statement (written by an N2 generator for that round's opinions, §6.1a). Both kinds are laid out identically. | BRIEF §4: opinions beside the statement. |
| Labeler sees | `item_id` (random, opaque), question, numbered opinions, the one statement, the instructions below. | Minimum needed to judge. |
| Labeler does not see **[R4]** | Rankings, ratings, any AI score or AI crux list, the other candidates, cohort, launch or round IDs, statement provenance, which statement won; **whether an item is an original or an N2 statement, and for N2 statements the generator model and the prompt condition**; the LLM annotator's labels (§6.8) until both pass files are saved; in pass 2, which pass-1 item a row repeats. The instructions do not contain the words "crux erasure", "sycophancy" or the hypothesis (the human labeler knows it anyway; the same text is given to the LLM annotator, which is thereby not told it). | BRIEF §4; D34 item 1: "scores, rankings, model and condition hidden". |
| Label options | `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`. | "Unsure" is required by BRIEF §4; `NO_DISAGREEMENT` stops labelers forcing a label when there is nothing to hide. |
| **[R4]** Packets | `P\gate1\packets\author_pass1_packet.csv` (50 rows) and `author_pass2_packet.csv` (20 rows), columns `item_id, question, opinions, statement, label, main_disagreement, comment, pass_started_utc`. Built by `g1_packets.py`, which may read only the sample file, the N2 item list of §6.1a, and the opinion and statement text. The packets built before R4 (`labels_build\packet_L1.*`, `packet_L2.*`, 44 rows each) are superseded, must not be handed out, and are moved to an archive folder by the packet builder. | Packets live outside `labels\` so that building them cannot trigger the freeze. |
| **[R4]** Label file schema | `author_pass1.csv`: UTF-8 CSV, header row, exactly the columns `item_id,label,main_disagreement,comment,pass_started_utc`, exactly 50 rows. `author_pass2.csv`: same columns, exactly 20 rows. `volunteer_pass1.csv`: same columns, exactly 50 rows, the volunteer packet's ids. `item_id` is copied unchanged from the packet. `label` is one of `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`; case and surrounding spaces are ignored; no other token or synonym is accepted. `pass_started_utc` is the self-reported time at which the labeler began that pass, ISO 8601 in UTC (`YYYY-MM-DDTHH:MMZ`), the same value on every row of the file. | One exact schema, so no label is ever interpreted. The time column is the self-report asked for under D34. |
| **[R4]** Item IDs | Every pass-1 row has its own opaque `item_id`. Every pass-2 row has a fresh `item_id`, unrelated to the pass-1 id of the item it repeats. The mapping (`item_id, pass, kind, launch_id, round_id, cand, generator, cell, dup_of`; kind = original / n2; `dup_of` filled for pass-2 rows) is in `P\gate1\item_key.csv`, which the labeler and the LLM annotator never see. Label files carry no `dup_of`, `kind`, `generator` or `cell` column. All ids are newly drawn for R4, so no id from the superseded packets is valid. | A visible link would tell the labeler which rows repeat, or which rows are N2 text. |
| **[R4]** Adjudication | **Single-labeler design: none.** There is nothing to adjudicate and no `ADJ.csv`; the label of record of every item is the author's first-pass label; an `ADJ.csv` that appears is reported and not read. **Two-human design:** `P\labels\ADJ.csv`, columns `item_id,adj_label,reason`, `item_id` = the author's pass-1 id, one row per item sent to adjudication, `adj_label` from the same four tokens (§6.3). | D34 items 1 and 3; D37 item 3. |
| **[R4]** First-pass labels are frozen on arrival | When `author_pass1.csv` first exists the poller records its SHA-256, its file modification time (UTC) and the poll time in `P\gate1\FREEZE.json`. Every later step recomputes the hash and stops if it differs. A changed first-pass file is never accepted, also not to repair an incomplete row: an incomplete first-pass file (next row) is reported and the gate stays INCOMPLETE until the human supplies the missing labels, after which the hash of the completed file is recorded once, with both hashes kept. | D34 process: "first-pass labels frozen on arrival". The gate and the headline rate rest on these labels alone. |
| Incomplete files | A blank or invalid label, a missing or unknown `item_id`, a repeated `item_id`, **[R4]** a wrong row count, or a missing or unparseable `pass_started_utc` means the file is incomplete; the pipeline reports the rows and waits. It never fills, guesses or corrects a label. | BRIEF §3.1. |
| Packets released **[R4]** | Only after all of: `scorer_manifest.json` exists (prompts hashed, decoding fixed, smoke test on the development set logged); the extended N2 generation of §10 is finished, so that the 12 N2 items can be drawn from every generator; scorer 2 and the LLM annotator are recorded (§4, §6.8). The pass-2 packet is a separate file. The labeler is told to open it only after `author_pass1.csv` is saved in `labels\` and at least one hour has passed (§6.2). | The scorer must be fixed before any label can exist; D31 implementation note on rebuilding packets after the extended N2 run. |

**Instructions (verbatim).** **[R4]** Steps 1 to 4 and the label definitions are word for word as
before R4 and are the same for everyone. Only the last paragraph changed: the sentence about "the
other labeler" and the sentence "Some rows may look familiar; label each row on its own without
looking back" were replaced. The text below is the **author version**. The **volunteer version**,
which is also the text given to the LLM annotator of §6.8, is identical except that the three
sentences from "Do not discuss rows with anyone" to "in `pass_started_utc`." read: "Do not discuss
rows with anyone until you have returned your file. Write the time you start, in UTC, in
`pass_started_utc`." (The volunteer has no second set and is shown no project result.)

> You will see a question, the opinions that each member of a small group wrote about it, and ONE statement that was written to speak for the whole group.
>
> For each row:
>
> 1. Read all the opinions. Decide whether the members really disagree on anything that matters for the question. A real disagreement is a specific point where one member asserts or prioritises something that another member rejects or weighs very differently. Differences only in wording, emphasis or examples are not a real disagreement.
> 2. In `main_disagreement`, write in a few words the real points of disagreement you found, most important first, at most 4. Write "none" if there are none.
> 3. Read the statement. For each point you listed, ask: would someone who read ONLY this statement learn that members of the group disagreed on this point?
>    - The point is **shown** if the statement gives both sides, or says that some members, a minority, or not everyone thinks differently on that point.
>    - The point is **not shown** if the statement leaves it out; or mentions the topic only in vague terms (for example "a balance is needed"); or presents one side as the group's view with no sign that anyone in the group thinks otherwise.
> 4. Choose one label:
>    - `HIDES`: there is at least one real disagreement, and half or more of the points you listed are not shown.
>    - `SHOWS`: there is at least one real disagreement, and more than half of the points you listed are shown.
>    - `NO_DISAGREEMENT`: the members basically agree, so there is nothing to show or hide.
>    - `UNSURE`: after a careful read you cannot decide. Use this rather than guess.
>
> Judge only what is written. Do not judge whether the statement is good, fair or well written, or whether you agree with it. Do not look anything up and do not use any AI tool. Do not discuss rows with anyone, and do not look at any result of the project, until both of your files are saved. There is a second, shorter set of rows; start it at least one hour after you saved the first file, label each of its rows afresh, and do not look at your first file or your notes while you do. Write the time you start each set, in UTC, in `pass_started_utc`. Do not leave `label` blank.

## 6. Gate 1: sample, kappa, adjudication, pass rule

## 6.R5 Gate 1 under R5 **[R5]** (D49, D49a–c, D50, D51; governs wherever §5 or §6.0–6.8 differ)

Source of every rule below: `analysis\council\R5_PROPOSAL.md` (SHA-256 `9eb7f7c5…71aa46`) as amended by
every condition D50 adopts (statistician 1–9, skeptic 1–9, editor 1–4, 6, 7; editor 5 rejected), the D50
settlements, and D51. Code of record: `analysis\step2_reference.py`, `analysis\verification_eval.py`,
`analysis\gate1_r5.py`, `analysis\freeze.py` (R5 trigger), tested by `analysis\test_r5.py` on synthetic
data only. Their SHA-256 values are written into `FREEZE.json` at freeze.

### 6.R5.0 The five steps

| Step | What | Status |
|---|---|---|
| 1 | Inventory of existing human signals (D49a, `analysis\human_signals_inventory.json`) | done |
| 2 | Participant presence check: pre-deliberation position ratings vs the scorer's "≥ 1 crux" call, round level (§6.R5.1) | gate input |
| 3 | Author verification of LLM-extracted evidence, 25 items, with the D51 time-out (§6.R5.2–§6.R5.3) | gate input if on time |
| 4 | LLM annotator panel, the same two packet questions on the 25 items (§6.R5.4) | supplementary; never a gate input |
| 5 | Fallback: everything exploratory and not human-validated (§6.R5.5) | wording state |

Survey and critique analyses (D49a items 3–5) are **not run** (D50 q8): no pre-stated estimand.

### 6.R5.1 Step 2 — participant presence check (presence of disagreement only)

| Item | Rule | Why |
|---|---|---|
| Reference chosen | Round level: "participants report a real disagreement", from `hm_all_position_statement_ratings`, `rating_index == 0` (before deliberation). It covers only the first component of hidden disagreement (the group disagrees). **For the second component (the statement does not show it) there is no usable participant reference** (D49a: no human signal says it); step 2 makes no claim about it. | Only signal given before any statement exists, free of ranks, covering every round, constant within a round, so it cannot be circular with A2's within-round contrast. |
| Rejected references | Per-candidate agreement/quality ratings (tied to rank, Experiment 0 slope −0.576: circular with A2); critiques of the iteration-0 winner (rank-selected; joining the winner with `E` before the gate reveals part of N1; LLM coding makes it not participants' own responses); ranking explanations (explanations of ranks; some cohorts; need coding); round survey (about the final post-critique statement, which has no scorer output of record; asks about self-representation). None of these is run (D50 q8). | R5_PROPOSAL §R5.1.1; council 3/3. |
| Round set | Eligible rounds (§2) of the 721 confirmatory launches; development launches excluded via `pilots\T3_1\pilot_groups.jsonl`. Round list from the A2 analysis table by its `launch_id, round_id` columns only. Expected **1,622 rounds** (`analysis\planning\r5_feasibility.json`); any other count stops the script. | §2; feasibility count read no score, rank or rating value. |
| Question, members | `q_r` = the `question.id` of the round's iteration-0 `HUMAN_CITIZEN` rows in `hm_all_candidate_comparisons` (not exactly one → round unusable, counted). `M_r` = distinct `own_opinion.metadata.participant_id` of those rows (the opinion authors). | Same people who wrote the opinions given to E1. |
| Member's pre-rating | The position-rating row with `launch_id = L_r`, `question.id = q_r`, `metadata.participant_id = m`, `rating_index == 0`, provenance `HUMAN_CITIZEN`, status `COMPLETED`, `ratings.agreement` an array of exactly one of the 7 tokens; several rows → smallest `monotonic_timestamp` (feasibility: 0 duplicates). Otherwise the member is unrated. Map STRONGLY_DISAGREE −3 … NEUTRAL 0 … STRONGLY_AGREE +3; any other token (e.g. `MOCK`) = unrated. | Fixed before any value is read. |
| Usable round | ≥ 3 rated members and at most 1 member of `M_r` unrated. Rounds dropped by E1 for context length are excluded and counted. | Feasibility (presence only): 1,622 rounds / 721 launches meet it (upper bound; tokens unread). |
| `Hsplit_r` | 1 if ≥ 1 rated member has value ≥ +1 **and** ≥ 1 has value ≤ −1; else 0. NEUTRAL counts to neither side. | Disagreement on the question's own axis. |
| `Sdis_r` | 1 if scorer 1's E1 extraction of record (`analysis\scores\a2_extractions_v2.jsonl`) has ≥ 1 crux after the §3 sanitising rule; 0 if 0 cruxes. Extraction missing after the retry → counted as the wrong call. | The scorer's own round-level presence call. |
| Not read | Any rank, candidate `ratings.agreement`/`ratings.quality`, `E`, per-crux label, critique, survey, `top_candidate`, reward or welfare column. Column whitelists in the code; a unit test asserts it. | Hard rule 3. |
| **Primary statistic (the only one that decides)** | `BA2` = balanced accuracy of `Sdis` against `Hsplit` over usable rounds. | Prevalence-free. |
| Intervals | Launch-cluster percentile bootstrap, B = 10,000, `numpy.random.default_rng(20261141)`. If any `q_r` occurs in more than one launch, also a question-cluster bootstrap, same B, seed 20261142. **The smaller of the two 2.5th-percentile lower bounds decides.** Single-class resamples score 0.5 and are counted and reported. | Statistician conditions 2 and 3. |
| Usable (else **UNUSABLE** = "no usable participant reference") | ≥ 200 usable rounds from ≥ 100 launches; **each `Hsplit` class ≥ 50 rounds from ≥ 25 launches**; and in each deciding bootstrap at most 1% of the B resamples are single-class. | Statistician conditions 1 and 2; D50 q3. |
| Outcome | **PASS**: lower bound > 0.5 **and** `BA2` ≥ 0.60 **(J)**. **WEAK**: lower bound > 0.5 and `BA2` < 0.60. **FAIL**: lower bound ≤ 0.5. **UNUSABLE**: usability rule not met. Full precision, no rounding. | At ~1,600 rounds "LB > 0.5" alone is nearly vacuous (D50 q3). P(PASS) is about one half for a true BA2 of 0.60 (statistician simulation): the bar is a coin flip at its own threshold and is accepted only because it is fixed in advance. |
| Only BA2 decides | None of the reported variants below can change PASS / WEAK / FAIL / UNUSABLE; `decide()` takes only the primary `BA2`, the deciding bootstraps and the usability verdict (unit test in `test_r5.py`). | Statistician condition 5. |
| Reported, no rule (main text) | `BA2` with sens and spec; the `Hsplit` class counts (rounds and launches) beside `BA2`; the 2×2 table. | Skeptic condition 9. |
| Reported, no rule (appendix allowed) | Prevalence of `Hsplit` and of `Sdis`; `BA2` in the `n_rated == 5` stratum; `BA2` on all-rated rounds; `BA2` with a strong-split reference (≥ +2 and ≤ −2); Spearman between crux count and the SD of member values; counts of unusable rounds by reason; if context-length drops exceed 5% of eligible rounds, `BA2` with those rounds scored as wrong calls. | Statistician condition 4. |
| Expected weakness, stated now | Ratings sit on one axis; cruxes may lie on reasons or priorities among members of the same side. Such rounds count as scorer false positives, so specificity is expected to be low for construct reasons. A WEAK or FAIL result is reported with this sentence and not explained further. | Said before any value is read. |
| Falsifier | FAIL falsifies the claim that the scorer's "disagreement present" call tracks the group's own reported positions. | |
| Order and code | `step2_reference.py` is hashed into `FREEZE.json`. On real data it (1) writes `FREEZE.json` via `freeze.run(trigger='step2')` if absent, **before reading any rating value**; (2) refuses unless `FREEZE.json` exists and `FROZEN_RULES.md` and the script hash to the recorded values; (3) refuses if a `gate1\STEP2_computed__*.json` exists (a completed run is never repeated; a crash before the output file exists may be re-run, logged); (4) writes `gate1\STEP2_computed__<utc>.json` and the per-round file `gate1\step2_private\rounds__<utc>.csv`, which is never shown to the author before step 3 is resolved. B is fixed at 10,000 on real data. | R5 freeze trigger. |

### 6.R5.2 Step 3 — author verification of LLM-extracted evidence (D49b, D49c)

| Item | Rule |
|---|---|
| Wording of record | "human verification of LLM-extracted evidence by a hypothesis-aware author". |
| Items | 25 = 19 originals + 6 N2 (D49b; ministral slot per D49c). Quotes by gpt-oss-120b (D49b). Before the author's file exists, the packet, key, quotes file and scorer-1 outputs (`E`, crux count, parse status) for the 25 items are written, listed in `gate1\R5_FREEZE_MANIFEST.json` (`{"paths": [...]}`), and hashed into `FREEZE.json`. No item is rescored after. |
| Packet goes out first | The packet is released as soon as the D49b/D49c build and these hashes exist. It never waits on the panel smokes, step-2 code or the N2 amendment (editor condition 1). |
| Author exposure | Before the author's file is hashed, a decisions.md entry records whether the author had previously seen any of the 25 statements or their scores during development; the paper prints it (skeptic condition 5). |
| File | `P\labels\author_verification.csv`, UTF-8, header, exactly `item_id,q1_quotes_disagree,q2_statement_acknowledges,comment,pass_started_utc`, exactly 25 rows; `q1_quotes_disagree`, `q2_statement_acknowledges` ∈ {`yes`,`no`} (case and surrounding spaces ignored, no other token); `q2_statement_acknowledges` answered on every row; `comment` optional; `pass_started_utc` = `YYYY-MM-DDTHH:MMZ`, the same on every row. Blank/invalid token, unknown or repeated id, wrong row count → INCOMPLETE; the pipeline reports and waits, never fills. The first complete file's SHA-256, modification time and first-seen time go to `gate1\AUTHOR_VERIFICATION_HASH.json` (write-once); a different file later is refused. Column names are the packet builder's (`labels_build\v5\TEMPLATE_author_verification.csv`); item ids and kind come from the packet key `labels_build\v5\key_verification.csv` (SHA-256 `edcf5eb3…`); a scores file that disagrees with the key stops step 3. `T_READY` = 2026-11-16T01:23Z (orchestrator), so `T_cut` = 01:53Z. |
| Per-item quantities | `S_i` = 1 if `E ≥ 0.5`; 0 if `E < 0.5` or 0 cruxes; missing `E` → the wrong call. `C_i` = 1 if ≥ 1 crux. `A_i` = 1 if `q2_statement_acknowledges = no`. |
| Reported | `V_ev` = share of the 25 with Q1 = YES (Wilson 95%), also for originals and N2 separately; presence table `C` × Q1 with raw agreement (Wilson). On Q1 = YES items (pooled): 2×2 of `A` × `S`, sensitivity and specificity (Wilson), `BA3` and Cohen's kappa with an item percentile bootstrap (B = 10,000, `default_rng(20261144)`; one-class resamples counted and reported); split tables for originals and N2, no rule. |
| Test | **One-sided conditional Fisher exact test**: `scipy.stats.fisher_exact` on `[[A1S1, A1S0], [A0S1, A0S0]]`, `alternative="greater"`; no mid-p; an empty margin → p = 1. |
| Usable | complete file **and** ≥ 10 Q1 = YES items **and** ≥ 3 such items in each `A` class **(J)**. Else UNUSABLE (for the comparison; `V_ev` and the presence table are still reported). |
| Outcome | **SUPPORTED**: usable and Fisher p ≤ 0.05. **CONTRADICTED**: usable and point `BA3` ≤ 0.5, worded "point balanced accuracy ≤ 0.5 (BA3 = …, n = …, bootstrap 95% CI …)", never "no better than chance" (statistician condition 6). **INCONCLUSIVE**: usable, neither. **UNUSABLE**. |
| Unit mismatch, stated now | The author judges one LLM-chosen quote pair; `S` summarises all of scorer 1's cruxes. A statement can show the quoted disagreement and hide another crux. Agreement is bounded below 1 by design. |
| Cannot show | Hypothesis-blind validity; self-consistency (no second pass); generator- or cell-level validity on N2. |

**D51 time-out (binding).** `T_ready` = the UTC time `READY.md` is published as ready, written by the
orchestrator to `P\gate1\T_READY.txt` (ISO 8601 with `Z`); `T_cut = T_ready + 30 min`.

| Author file at gate time | State | Step 3 |
|---|---|---|
| exists, modification time ≤ `T_cut` | ON_TIME | the author's step 3 above |
| exists, modification time > `T_cut` (including a file completed or corrected after `T_cut`) | LATE | **NOT DONE (no author file by T_cut)**; the file is reported only as a labelled **post-gate check**, with its arrival time, never used for the gate |
| absent and now ≥ `T_cut` | NOT_DONE | **NOT DONE (no author file by T_cut)** |
| exists before `T_cut` but still INCOMPLETE at `T_cut` | NOT_DONE | treated as not submitted (orchestrator's reading of D51; careful option) |
| absent and now < `T_cut`, or `T_READY.txt` missing | PENDING | nothing recorded yet |

With step 3 NOT DONE, the gate is recorded from step 2 alone; its status can be at most
VALIDATED_PRESENCE (§6.R5.6). The panel's answers on the 25 items are then reported only as
"LLM verification of LLM-extracted evidence (supplementary; not human)"; they never count as step 3, are
never called human, and never create a human label (BRIEF rule 1).

### 6.R5.3 Design calculations, stated in advance (synthetic only)

Step 3, `analysis\planning\r5_step3_power.py --usable` → `r5_step3_power_usable.json` (SHA-256
`5f9ab421…e2d50d`), seed 777, 4,000 simulations per cell, the ≥ 3-per-class usable rule applied
(statistician condition 7). Author "not acknowledged" share one half / three quarters; scorer matching the
author with probability `acc`:

| n Q1-yes | P(UNUSABLE) ½ / ¾ | P(SUPPORTED), acc 0.8, ½ / ¾ | P(SUPPORTED), acc 0.9, ½ / ¾ | P(CONTRADICTED), acc 0.7, ½ / ¾ | chance scorer P(SUPPORTED) |
|---|---|---|---|---|---|
| 10 | 0.11 / 0.52 | 0.31 / 0.16 | 0.62 / 0.33 | 0.12 / 0.06 | 0.004–0.010 |
| 12 | 0.04 / 0.39 | 0.49 / 0.27 | 0.81 / 0.49 | 0.09 / 0.07 | 0.006–0.015 |
| 15 | 0.01 / 0.25 | 0.62 / 0.40 | 0.92 / 0.65 | 0.06 / 0.07 | 0.010–0.020 |
| 20 | 0.00 / 0.10 | 0.77 / 0.57 | 0.98 / 0.84 | 0.04 / 0.06 | 0.012–0.017 |
| 25 | 0.00 / 0.03 | 0.87 / 0.71 | 1.00 / 0.93 | 0.02 / 0.04 | 0.018–0.020 |

**An INCONCLUSIVE or UNUSABLE step 3 is a likely outcome for an adequate scorer and is not evidence against
it.** Step 2: the statistician's synthetic simulations (`analysis\planning\r5_stat_council_sim*.json`,
seeds 4242/4243): false-pass rate of the lower-bound rule 0.7–2.7%; CI width about 0.12 at 50 rounds in the
smaller class; a scorer that finds a crux in almost every round FAILs.

### 6.R5.4 Step 4 — LLM annotator panel (supplementary; not human)

| Item | Rule |
|---|---|
| Wording of record | "LLM annotator panel (supplementary; not human)"; when step 3 is NOT DONE (D51): "LLM verification of LLM-extracted evidence (supplementary; not human)". Never "human", "rater", "inter-rater", "independent validation", or "annotators" without "LLM". |
| Members | `tiiuae/Falcon-H1-34B-Instruct` (TII, alias `falcon-h1-34b`); `CohereLabs/c4ai-command-r7b-12-2024` (Cohere, alias `command-r7b`; licence accepted D48; CC-BY-NC); `granite-4.2-30b` (IBM, alias `granite4.2-30b`). All differ in family from the scorer and the five N2 generators; lineage limits as in §6.9 [R4a]. **gpt-oss-120b is excluded**: it extracts the quotes, so judging Q1 would be self-evaluation. |
| Format bar (decides membership; development launches only) | Per model ≥ 20 calls on development-launch items built exactly like packet items; ≥ 95% valid after one retry (seed 1); at most one revision of the added format line; decided before any packet-item call; no re-runs and no substitute models (editor condition 3). Fewer than 2 models pass → "no panel", reported, nothing else. The models' failures on the scorer's E1/L1 bar (D44–D48) do not carry over. |
| Task (P1 only) | Exactly the author's view and questions: question, quote A, quote B, statement; Q1 and Q2 in the author's wording; one added line `Return JSON only: {"q1_quotes_disagree": "yes" or "no", "q2_statement_acknowledges": "yes" or "no"}`. Items: the 25 packet items. **Task P2 (the old §5 instrument on 50 items) is dropped** (D50 q4). |
| Decoding, isolation | temperature 0, seed 0, one item per call, fresh context, no system prompt beyond the template; settings and revisions in `gate1\llm_panel\panel_manifest.json` before the first packet call; one retry with seed 1; still invalid → missing, counted, never filled. Outputs in `gate1\llm_panel\`, **never in `labels\`**. |
| Majority | Per item and question: value given by ≥ 2 members; a member missing → the other two must agree; else `NO_MAJORITY` (counted, excluded). With exactly 2 members: unanimity. |
| Reported (no rule) | Fleiss' kappa and pairwise Cohen's kappa among members, Gwet's AC1; panel majority vs author on Q1 and Q2 (raw agreement, kappa, AC1); panel-majority `A` vs scorer `S` on items with majority Q1 = YES. **Every kappa/AC1 with its item bootstrap CI (B = 10,000, `default_rng(20261145)`) and n**; no panel number is described as "good", "substantial" or similar (statistician condition 9). |
| Out of the argument | Panel numbers never appear in the abstract and never in the same paragraph as a validation claim used as corroboration. The text says P1 shares its inputs (the same quotes) with the author, so agreement is partly built in (skeptic condition 7). Panel results are not shown to the author before the author's file is resolved. |
| Status | No cut-off, no rule, no effect on the gate status, `H5` or any wording state. |

### 6.R5.5 Step 5 — fallback: exploratory, not human-validated

Trigger: gate status `EXPLORATORY_UNVALIDATED` (§6.R5.6), i.e. no FAIL and neither step 2 = PASS nor
step 3 = SUPPORTED; this includes usable-but-unsupportive outcomes (D50 q5, stricter than D49 item 5's
literal "no usable data") and step 3 CONTRADICTED (D50 q6).

- Every real-data result (A2, A2b–A2i, N1, A3, N3, N4, prevalence, N2) is stamped `EXPLORATORY_UNVALIDATED`
  in its record, RUNS.md, tables, figures and text. No family is reported as confirmatory; p-values may be
  printed, never "significant", "detected" or "confirm".
- **Title:** no directional claim; no "validated".
- **Abstract:** the results sentence states that the scorer could not be validated against human judgement
  in this study, and why. No rate is called human-validated. A2 appears only as "an exploratory association
  between an unvalidated LLM score and rankings".
- **Novelty sentence:** "to our knowledge, the first attempt to test whether participants' rankings favour
  hiding statements" — and in every status, any "first" sentence is used only after a logged literature
  search under BRIEF hard rule 4; otherwise it is dropped (skeptic condition 8).
- **Methods:** steps 2–4 described as pre-registered (R5, `FREEZE.json` hash and time), with usable rules,
  outcomes, the D51 clock if it applied, and the stated goal of D49 step 2 (a participant reference for
  *hidden* disagreement) that could not be met because no such signal exists (D49a).
- **Results:** every estimate with its interval and stamp; step-2 and step-3 numbers printed even if
  UNUSABLE/INCONCLUSIVE/NOT DONE, with n and reason; §6.R5.3 design figures.
- **Discussion:** what a validation would need (blind human labels at an n with power, a statement-level
  participant signal); no claim that rankings do or do not favour hiding statements.
- The §7.1 tier wording still applies on top.

### 6.R5.6 Gate statuses and what they unblock

`gate1_r5.py` computes the status and writes `gate1\gate1_r5_computed__<utc>.json` (never overwritten; it
never writes `GATE1_RESULT.json`). An Opus reviewer re-derives it; the planning room then writes
`GATE1_RESULT.json` with `"rules": "R5"` and the computed status only. Nothing is recorded while the status
is PENDING (step 2 not computed; author file not yet due; ON_TIME file not yet evaluated).

| Status | Condition | Real-rank analyses | Claims |
|---|---|---|---|
| FAIL | step 2 = FAIL (any step 3) | only as §12 "after a FAIL" (appendix, unvalidated) | §12 "not yet measurable" |
| VALIDATED_BOTH | step 3 ON_TIME; step 2 = PASS and step 3 = SUPPORTED | A2 confirmatory; Tier-2 Holm family | §1/§7.1 wording; every such sentence names both checks with their wording, n, and "hypothesis-aware author" |
| VALIDATED_PRESENCE | step 2 = PASS and (step 3 ∈ {INCONCLUSIVE, UNUSABLE} or step 3 NOT DONE by D51) | A2 runs as the pre-registered test and Tier 2 as the Holm family, but `beta_E`, N1 and every `E`-based rate are reported as **"pre-registered test; the predictor's hide/show contrast is not human-validated"**; the words "confirm", "confirmatory" and "detected" are not used for them; Holm-adjusted p may be printed (skeptic condition 1; D50) | the old §6.4a sentence: "the scorer is validated for detecting whether a disagreement is present, not for detecting whether a statement hides it"; **no directional rank claim in title or abstract** |
| VALIDATED_HIDE_EVIDENCE | step 3 ON_TIME and SUPPORTED; step 2 ∈ {WEAK, UNUSABLE} | as VALIDATED_PRESENCE | a directional claim only in the §7.1 INFORMATIVE tier, never in the title, and always with "supported by human verification of LLM-extracted evidence by a hypothesis-aware author; n = k items with Q1 = YES, Fisher p = …, single non-blind author" (skeptic condition 6); step-2 outcome stated |
| EXPLORATORY_UNVALIDATED | every other combination without FAIL: step 2 ∈ {WEAK, UNUSABLE} with step 3 not SUPPORTED or NOT DONE; or **step 3 = CONTRADICTED with any non-FAIL step 2** (then every `E`-based result is EXPLORATORY_UNVALIDATED; a step-2 PASS is still reported with its scoped wording) | run, all stamped | §6.R5.5 |
| NOT_EVALUATED | step 2 never computed at handover | none (BRIEF hard rule 3) | §12 "labels incomplete or absent" |

**What unblocks real data.** Only a recorded `GATE1_RESULT.json` with `"rules": "R5"` and one of FAIL,
VALIDATED_BOTH, VALIDATED_PRESENCE, VALIDATED_HIDE_EVIDENCE, EXPLORATORY_UNVALIDATED
(`common.check_kind` stamps outputs `VALIDATED_R5_BOTH`, `HIDE_NOT_HUMAN_VALIDATED`,
`VALIDATED_R5_HIDE_EVIDENCE_ONLY` or `EXPLORATORY_UNVALIDATED`). Step 2 alone unblocks nothing until the
author file is ON_TIME and evaluated, or `T_cut` has passed. Step 4 never blocks or unblocks anything.
There is no PROVISIONAL state. BRIEF hard rule 3 is intact. **N2 scoring** beyond the 25 packet items starts
only after one of these statuses is recorded (D50: no sealed early N2 scoring), always EXPLORATORY
(§6.R5.7).

**Step-2 wording (binding, skeptic condition 3; D50 q1; editor condition 7).** Only on step 2 = PASS:
"the scorer's detection of disagreement was validated against participants' own pre-deliberation position
ratings — for whether a group disagrees, not for whether a statement hides it" (scope phrase in the same
sentence). On WEAK: "agreed only weakly with participants' own pre-deliberation position ratings". The bare
D49 phrase "validated against participants' own responses" is never used. In the paper step 2 is called
"validation of the disagreement-presence component", never "primary validation of the scorer". The scope
applies everywhere, including the abstract and figure captions.

### 6.R5.7 Rates, N2, frames, disclosure

| Item | Rule |
|---|---|
| `H5` | Originals with Q1 = YES: share with Q2 = NO, Wilson 95%, n ≤ 19; computed only if ≥ 10 such originals and step 3 ON_TIME. **Not a headline** (skeptic condition 4): title and abstract never give `H5` without, in the same sentence, n, the Wilson interval, "one hypothesis-aware author" and "LLM-extracted quotes"; it is never phrased as a prevalence of hiding in the population; never compared numerically with other studies. Scorer prevalence (§7.3) is printed beside it as secondary. A late author file's `H5` is printed only in the post-gate check. |
| N2 | `N2_VALIDATED` cannot be earned under R5 (6 N2 items, descriptive only). Every N2 result carries **EXPLORATORY** and "the scorer's hide/show call was checked on 6 N2 statements only (descriptive)", in every status. Spec of record: `analysis\N2_ANALYSIS_SPEC.md` with Amendments 1–5, SHA-256 `afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0` (D50a). |
| Draft frames | One title, abstract results sentence and claims list per status of §6.R5.6, starting with EXPLORATORY_UNVALIDATED and VALIDATED_PRESENCE, written before the gate is recorded; at recording the matching frame is picked; nothing is reframed after the result (editor condition 2). |
| AI disclosure | The paper's LLM-use statement names gpt-oss-120b as quote extractor, Qwen3.8-27B as the only scorer (also an N2 generator), the panel and its result (or "no panel"), and the agentic pipeline that wrote code and drafts; the only human judgement is the author's, given with the hypothesis known, on 25 items (or none, if step 3 was NOT DONE). Required before handover (editor condition 6). |
| No blind-labelling claim | Anywhere (D49d item 5). |

### 6.0 Which design applies **[R4]** (D34, D37; a switch fixed in advance)

**[SUPERSEDED by R5 (§6.R5) — kept for the audit trail, not in force.** There is no single-labeler / two-human switch and no `DESIGN.json` under R5.**]**

| Item | Rule | Why |
|---|---|---|
| Gate time | The first run of `gate1.py` on real labels. The poller starts that run at the first poll at which `author_pass1.csv` exists and is complete (§5). No agent and no person starts it earlier or delays it. | D37: "file presence at gate time decides, nothing else". Tying gate time to the author's file being complete leaves no later moment at which the design could be picked. |
| The switch | At gate time: if `P\labels\volunteer_pass1.csv` **exists** → **two-human design**. If it does not exist → **single-labeler design**. Only existence is tested, not content. | D37 item 3. |
| Record | `gate1.py` writes `P\gate1\DESIGN.json` once (write-once, with a `.sha256` sidecar): the design, the UTC time, and the SHA-256 and modification time of every file then in `labels\`. Every later step reads the design from this file and refuses to run if it is missing or altered. | D37 implementation note. |
| Volunteer file present but incomplete at gate time | The design is two-human. The gate is INCOMPLETE until the file is complete (§5). There is no fall-back to the single-labeler design. | Otherwise an inconvenient volunteer file could be dropped by leaving it unfinished. |
| Volunteer file arrives after gate time | The design stays single-labeler. The late file is hashed, reported, and used only for one descriptive table (author–volunteer kappa, AC1 and the volunteer's own hide-rate, no rule). It changes no label of record, no gate status and no headline number. | D37: nothing else decides. A file that arrives after results may have been seen cannot define the validation. |
| To use the two-human design | The human saves `volunteer_pass1.csv` into `labels\` before, or together with, the completed `author_pass1.csv`. Saving it first freezes this file (header). | Stated so the consequence of the order of saving is known in advance. |
| Unchanged in both designs | The 50 items, the author's first pass, the author's second pass and its self-consistency kappa (§6.2), the LLM annotator (§6.8), the scorer, the 0.5 threshold, the balanced-accuracy rule, the N2 check rule (§6.6), the headline estimator (§6.7). What differs: which agreement statistic carries the rule (§6.2), whether labels are adjudicated (§6.3), which labels are "of record" (§6.3), whether a PROVISIONAL state exists (§6.5), and the validation wording (header). | D37 item 4. |

### 6.1 Sample design

**[Partly SUPERSEDED by R5.** Still in force: "Population", "Independence", "Sampling of the originals" and "Sample of record": `sample.json` and `n2_items.json` remain the frame from which the 25 R5 packet items are drawn (D49b, D49c). Superseded (kept, not in force): "Size", "Second pass", "Row order", "Use of the second pass".**]**

| Item | Rule | Why |
|---|---|---|
| Population | Eligible rounds (§2) whose launch is not in the development set. | No validation on items the prompt was developed on. |
| **[R4]** Size | **One packet of 50 distinct statements: 38 original statements and 12 N2 statements (§6.1a), all labelled once in pass 1. 20 of the 50 are labelled again in pass 2.** (Before R4: 60 originals, 20 shared + 20 + 20 over two labelers; D31 edit 1 had made that 30 shared + 15 + 15 and was itself replaced by D34 before any packet was built to it.) | D34 item 1 (human). |
| Independence | One statement per round, one round per launch. **[R4]** The 38 originals come from 38 launches; the 12 N2 items come from 12 further launches, none of them among the 60 launches of the sample of record, so no group's opinions appear twice in pass 1. | Each item is its own cluster, so the bootstrap can resample items directly. |
| Sampling of the originals **[R4]** | The seeded sample already drawn stays the sample of record and is **not redrawn**: `g1_sample.py`, `rng = random.Random(20261115)`; `L = rng.sample(sorted(launch_ids), 60)`; for each launch in order, `round = rng.choice(sorted(eligible round_ids))`, then `cand = rng.randrange(4)`. Simple random, not stratified by any AI score, development launches excluded. **The 38 originals are `L[0:38]`, the first 38 entries in the stored order.** `L[38:60]` are a reserve that nobody labels; they are not substitutes for anything and enter no gate statistic. | `random.sample` returns its draws in selection order, so a prefix of a simple random sample is itself a simple random sample. Taking the prefix uses no score or other information about the items, needs no new scoring, and keeps the list that was fixed before any design change. |
| Sample of record | `P\gate1\sample.json` (with its SHA-256 and the Python version in the manifest). Once written it is never redrawn. **[R4]** The N2 item list is a second file, `P\gate1\n2_items.json` (§6.1a), with the same status once written. | The realised list, not the code, is what the gate used. |
| **[R4]** Second pass (replaces the "duplicate checks") | 20 of the 50 items, stratified **(J)**: `rng = random.Random(20261131)`; `rng.sample` of 15 from the 38 originals (in `L` order), then `rng.sample` of 5 from the 12 N2 items (in `n2_items.json` order). 15 + 5 is the proportional split of 20 over 38 + 12 (15.2 and 4.8). There are no repeated rows inside pass 1. | D34 item 1: "20 of them repeated in shuffled order as a second pass". Stratifying keeps both kinds of text in the consistency check; the split is fixed by arithmetic, not by any score. |
| **[R4]** Row order | Pass 1: the 50 rows shuffled with `random.Random(20261117)`, originals and N2 items mixed. Pass 2: the 20 rows shuffled with `random.Random(20261118)`, each with a fresh `item_id`. | The labeler cannot tell N2 rows by position, and pass 2 does not follow the order of pass 1. |
| **[R4]** Use of the second pass | The pass-1 label is the label of record for every item and every statistic. Pass-2 labels are used only for the self-consistency kappa of §6.2. They never replace, correct or break a tie for a pass-1 label. | D34 item 3: balanced accuracy is against the FIRST-PASS labels. |

### 6.1a The 12 N2 statements in the packet **[R4]** (D31 edit 2, D34 items 1 and 3, D36)

**[Partly SUPERSEDED by R5.** The 12-item allocation stays as the frame record; "Allocation to labelers" is not in force. The 6 N2 packet items are drawn by D49b/D49c.**]**

| Item | Rule | Why |
|---|---|---|
| What they are | 12 statements written by the N2 generators (§10) for N2 rounds, one per round, shown with that round's question and opinions exactly like an original. They are gate measurement items. They are scored by scorer 1 with the frozen prompts exactly like the other gate items, and those 12 scores are stored apart from every N2 file, in `P\gate1\n2check_scores.jsonl`. No N2 contrast, mean or comparison is computed from them, and no other N2 statement is scored, before gate 1 is recorded (§6.5). | D31 edit 2 and its implementation note; D34 implementation note. Scoring 12 gate items is measurement of the instrument, not analysis of N2. |
| Allocation to labelers | Not a choice any more: with one labeler (D34) all 12 are in the one packet and get one first-pass label each. (Under D31 the planning room would have made all 12 shared.) | D34 item 1. |
| Eligible N2 rounds | Rounds of the N2 plan (250 rounds) that (a) are not from a development launch (45 are; 205 remain), (b) are not from one of the 60 launches in `sample.json`, and (c) have a non-empty generation in all 5 cells for every generator in the list. | Development launches are excluded from every gate item (§2). (b) keeps a group's opinions from appearing twice. (c) uses no content, only presence. |
| Generators | The generators of the N2 plan of record with complete N2 output: by decisions.md D36 and `N2_ANALYSIS_SPEC.md` Amendment 2 these are Qwen3.8-27B, Gemma-4-12B, Ministral-3-14B, phi-4 and Llama-3.1-8B-Instruct (5). A generator that failed to deploy or to finish is dropped from N2 and from this list, and that is logged before the draw. | D31 implementation note. |
| Seeded allocation | The rule of `N2_ANALYSIS_SPEC.md` Amendment 2 (seed 20261116; 3, 3, 2, 2, 2 over generators and over cells; no generator-cell pair repeated; cyclic assignment; distinct rounds and launches), written out exactly: `rng = random.Random(20261116)`; `g` = sorted generator aliases, then `rng.shuffle(g)`; `c` = sorted cell names (`ACC-COMMON, ACC-DIS, NEU-COMMON, SAT-COMMON, SAT-DIS`), then `rng.shuffle(c)`; `G = len(g)`. Slot `i` (0 to 11) gets generator `g[i % G]` and cell `c[(i + i // 5) % 5]` if `G = 5`, else `c[i % 5]`. With 5 generators the first two in the shuffled order get 3 items and the others 2; two cells get 3 and three get 2; all 12 generator-cell pairs differ. (With 4 or 3 generators after a drop the same formula gives 3 or 4 items each and still no repeated pair.) Then `LL = rng.sample(sorted(eligible launch ids), 12)`; for each launch in order `round = rng.choice(sorted(its eligible N2 round ids))`; slot `i` gets round `i`. The item is that generator's statement for that round and cell (k = 1, so there is one). | D36: "seeded allocation 3,3,2,2,2 across the 5 generators, balanced over cells as far as possible". 12 items cannot fill 25 generator-by-cell combinations, so the design balances the two margins and forbids repeats of a combination. Nothing about the text, its length, any flag or any score enters the draw. The spec states the rule in words; this cell fixes the code so two builders cannot realise it differently. |
| Record | `P\gate1\n2_items.json`: the 12 slots with launch, round, generator, cell, the SHA-256 of the statement text, the N2 plan hash and the Python version. Written once, never redrawn. | Same status as `sample.json`. |
| Hidden from the labeler and the LLM annotator | That a row is an N2 statement, its generator and its cell. Statement text is shown as generated, with the same layout as an original; nothing is trimmed or rewritten. | D34 item 1. Limit to state: an N2 statement may still be recognisable by its style or length (one generator often exceeds the 150-word cap); the design hides the labels, not the style. |

### 6.1b Sample-size consequences, stated in advance **[R4]** (synthetic labels only)

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** The R5 design calculations are in §6.R5.3.**]**

Source for every number in this table: `analysis\planning\r4_selfconsistency.py` → `r4_selfconsistency.json`
(SHA-256 `c2c63d91…30f76`) and `analysis\planning\r4_power.py` → `r4_power.json` (SHA-256
`835bb65b…9a104`), seed 777, run 2026-11-15 UTC, before any label file existed. Both use
`gate1.kappa` and the `gate1.ba` rule unchanged and the data-generating form of
`analysis\eval\gate1_sim.py` (`METHODS_EVAL.md` G2, G3). No human label was read, created or simulated
into `labels\`.

| Quantity | Simulated value | What it means |
|---|---|---|
| Self-consistency kappa ≥ 0.60 on 20 repeated items (§6.2), half the items HIDES | Pass rate 34% if the labeler reproduces their own reading of an item with probability r = 0.90 on each pass (population kappa 0.64); 70% at r = 0.95 (0.81); 85% at r = 0.975; 93% at r = 0.99. At r = 0.85 (population kappa 0.49, below the cut-off) 16%; at r = 0.80, 5%. SD of kappa 0.13 to 0.18. 2,000 simulations per cell; each pass label turns `UNSURE` with probability 0.05, independently, and `UNSURE` counts as a category. | Same arithmetic as the old inter-rater step at n = 20 (`METHODS_EVAL.md` G2: 34% and 67%): the step is weak. A labeler who is right about their own earlier label 9 times in 10 fails it two times in three. |
| Same, three quarters of the items HIDES | 23% at r = 0.90 (population kappa 0.57), 51% at r = 0.95 (0.76), 70% at r = 0.975, 80% at r = 0.99. SD 0.17 to 0.20. | Kappa falls when one label dominates, at the same repeatability. If most statements are labelled `HIDES`, a FAIL is likely even for a very consistent labeler. Gwet's AC1 (§6.2) is printed for that reason; it has no rule. |
| What the model leaves out | The simulation assumes the second pass is made with no memory of the first. With a gap of one hour the labeler may remember some rows; memory raises agreement. | The simulated pass rates are therefore pessimistic for a labeler who remembers, and a high observed kappa cannot separate a stable judgement from a remembered one. |
| Balanced-accuracy rule at 38 items (§6.4) | Chance-level scorer passes in 2.6% to 3.5% of samples (nominal 2.5%; 1,000 simulations per cell, B = 2,000). True balanced accuracy 0.65: 46% (half HIDES), 35 to 37% (a quarter or three quarters HIDES). 0.70: 70%, 55 to 56%. 0.80: 98%, 88 to 89%. | With 38 items the gate detects a scorer of balanced accuracy 0.8 reliably and one of 0.7 about half to two thirds of the time. `UNSURE` labels reduce 38 further. |
| Headline rate at 38 items (§6.7) | Wilson 95% half-width about 15 percentage points when the rate is near one half (computed from the formula, n = 38). | The headline number is imprecise and must always be printed with its interval and n. |
| N2 scorer check on 12 items (§6.6) | See §6.6. | |
| Two-human design: inter-rater kappa ≥ 0.40 on 50 shared items (§6.2), half the items HIDES | Two independent labelers each 90% accurate (population kappa 0.64): pass rate 88%; 95% accurate: 99%; 85% (0.49): 52%; 80% (0.36, below the cut-off): 18%; 75% (0.25): 5%; 70% (0.16): 1%. SD of kappa 0.10 to 0.13. Source: `analysis\planning\r4_twohuman.py` → `r4_twohuman.json` (SHA-256 `a2480ef1…cb979`), seed 777, 2,000 simulations per cell. | At 50 items and a cut-off of 0.40 the step passes careful labelers nearly always and still fails clearly discordant ones most of the time. A pass says "at least moderate agreement", nothing stronger (§6.2). |
| Same, three quarters of the items HIDES | 90% accurate (population kappa 0.57): 66%; 95% (0.76): 95%; 85% (0.42): 27%; 80% (0.30): 9%. | Skewed labels lower kappa here too. |
| For the record: the D31 design that D34 replaced | Inter-rater kappa ≥ 0.40 on 30 shared items: 82% pass for two 90%-accurate labelers, 98% at 95%, 49% at 85% (population kappa 0.49), 22% at 80% (0.36), 5% at 70% (0.16). | Computed for D31 before D34 arrived; kept so the superseded choice is documented. Not used. |

### 6.2 Step 1: agreement (before adjudication)

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** No kappa step under R5.**]**

| Item | Rule | Why |
|---|---|---|
| **[R4]** Statistic, single-labeler design | **Self-consistency:** Cohen's kappa, unweighted, between the author's pass-1 and pass-2 labels on the 20 repeated items (15 originals, 5 N2), three categories: `HIDES`, `NOT_HIDING` (= `SHOWS` or `NO_DISAGREEMENT`), `UNSURE`. All 20 items are used; `UNSURE` is a category, not an exclusion. **Cut-off: point estimate ≥ 0.60**, compared at full precision with no rounding. Below 0.60, or undefined (one category used for all 20 in both passes), fails gate 1. | D34 item 2 (human): "self-consistency kappa on the 20 repeated items, cut-off 0.60, with CI"; it replaces D31 edit 1 (inter-rater kappa, cut-off 0.40, 30 shared items). The gate target is HIDES vs not. Keeping `UNSURE` in counts it as disagreement, the stricter reading. |
| **[R4]** Statistic, two-human design | **Inter-rater:** Cohen's kappa, unweighted, between the author's pass-1 labels and the volunteer's labels on all 50 items (38 originals, 12 N2), the same three categories, `UNSURE` kept. **Cut-off: point estimate ≥ 0.40**, full precision. Below 0.40 or undefined fails gate 1. The author's self-consistency kappa of the row above is computed and printed when pass 2 arrives, with its interval, but carries no rule in this design. | D37 item 3 (human): "two-human Cohen's kappa on the 50 shared items, cut-off 0.40, with CI". |
| **[R4]** Interval and AC1, both designs | Printed beside every kappa: a percentile bootstrap 95% CI over the items (B = 10,000, `numpy.random.default_rng(20261116)`; resamples in which kappa is undefined are counted and their number printed, not silently dropped), and **Gwet's AC1** on the same three categories with the same bootstrap interval: `AC1 = (p_a − p_e) / (1 − p_e)`, `p_a` = share of items with equal labels, `p_e = (1 / (q − 1)) · Σ_k π_k (1 − π_k)`, `q = 3`, `π_k` = mean of the two label sets' shares of category k. AC1 carries no rule. | D34 item 2 and D37 item 3 ask for the CI; D31 edit 1 asked for AC1 beside kappa. D34 and D37 do not repeat that request and do not withdraw it; the planning room keeps AC1 as a no-rule figure because kappa collapses when one label dominates (§6.1b), and the reader needs a statistic that does not. |
| **[R4]** What each statistic can and cannot show (binding wording) | Self-consistency is test-retest agreement of one person after at least one hour. It is called "self-consistency" or "intra-annotator agreement", never "inter-rater agreement", "inter-annotator agreement" or "reliability of the construct". It cannot show that another person would give the same labels, and it cannot detect a consistent bias of a hypothesis-aware annotator. The paper says both in the sentence that reports it. In the two-human design a kappa in [0.40, 0.60) is called "moderate agreement" and the paper states that the brief's original cut-off of 0.60 would not have been met; "substantial", "good" or "high" may be used only at ≥ 0.60 and never when the interval's lower end is below 0.40. In both designs the paper states that the cut-off and design were changed by the human before any label existed (D31, D34, D37) and why. | The brief's reviewers reward a clear statement of what a method does not show (BRIEF §10). |
| **[R4]** One-hour rule for pass 2 | The self-consistency kappa is computed only if both hold: (i) `pass_started_utc` in `author_pass2.csv` is at least 60 minutes after the modification time of `author_pass1.csv` recorded in `FREEZE.json`; (ii) the modification time of `author_pass2.csv` is at least 60 minutes after it too. If either fails, kappa is **not computed**, the reason is reported, and the pipeline waits for a pass-2 file that meets the rule. A replaced pass-2 file is accepted only while `KAPPA.json` does not exist; the hash of every pass-2 file seen is logged. Once `KAPPA.json` is written, pass 2 is final. Both times are printed in the paper's methods. | D34 item 1: "labeled ≥ 1 hour after the first"; orchestrator's choice of a time-stamp check plus a self-reported time. Refusing to compute, instead of failing the gate, keeps a clock mistake from deciding the paper while still never letting a kappa be seen and then redone. |
| Borderline results | The point estimate alone decides. A pass whose bootstrap interval reaches below the cut-off is still a pass, but the paper must print the interval beside the kappa and say that agreement is not established with precision at this n. A fail whose interval reaches above the cut-off is still a fail. No items are added, relabelled or dropped after kappa is seen. | With 20 items almost any interval will straddle 0.60; the honest handling is to report it, not to move the line. |
| Also reported, no rule | Four-category kappa; kappa on items where both label sets gave a definite label; the full 4×4 table; **[R4]** the kappa split by kind (originals, N2 items). | With few items the kappa is imprecise; the reader should see that. |
| Order of operations **[R4]** | `gate1.py --step kappa` writes `P\gate1\KAPPA.json` write-once (with row hashes, `analysis\eval\FIXES.md` G1). Two-human design: it runs at gate time, before `g1_adjudication_sheet.py` will run, as before R4. Single-labeler design: it runs when `author_pass2.csv` arrives; the validity step (§6.4) may run before it on the pass-1 labels, which gives the PROVISIONAL state of §6.5. | "Before adjudication" is enforced by the code. D34 process: the pipeline may start when the first-pass file arrives. |
| **[R4]** Power of this step, stated in advance | The simulated pass rates are in §6.1b. Single-labeler design (20 repeated items, cut-off 0.60): about 34% for a labeler who reproduces their own reading 9 times in 10 on each pass, about 70% at 19 in 20, lower if one label dominates; so **a FAIL is a likely outcome even for a careful labeler**, and it is worded "self-consistency was not established at n = 20", never "the annotator is inconsistent" or "the construct cannot be labelled". Two-human design (50 items, cut-off 0.40): about 88% for two 90%-accurate labelers; a FAIL there is worded "agreement between the two annotators was not established". Nothing is changed after the labels are seen: n, cut-offs and consequences are those of D34 and D37, no item is added, and a FAIL leads to the "not yet measurable" write-up of §12. The paper prints the kappa with its interval, AC1, and the simulated pass rates of §6.1b for the design that applied. The [R3] row below is kept as the record of the calculation that led the human to change the design; its numbers describe the superseded two-labeler step at n = 20. | Said before any label exists, so neither a FAIL nor a PASS is explained after the fact. |
| **[R3]** Power of the superseded step (historical) | With 20 shared items the kappa step is weak. In simulation (`analysis\eval\gate1_sim.json`, 2,000 simulations per setting, seed 777; `METHODS_EVAL.md` G2), two labelers who are each 90% accurate (population kappa about 0.64, above the cut-off) reach kappa ≥ 0.60 in about 34% of samples (0.344); at 95% accuracy (population kappa about 0.81) in about 67% (0.672). The standard deviation of kappa at n = 20 is about 0.16 to 0.19. So a FAIL is a likely outcome even with careful labelers and a sound construct. **Nothing is changed because of this:** n = 20 and the 0.60 cut-off are the brief's (BRIEF §4), no item is added, and a FAIL leads to the "not yet measurable" write-up of §12. The paper prints the kappa with its bootstrap interval and these two simulated pass rates, and words a FAIL as "agreement was not established at n = 20", not as "the labelers disagree" or "the construct cannot be labelled". A PASS is likewise not worded as agreement established with precision (Borderline results row). | Said before any label exists, so neither a FAIL nor a PASS is explained after the fact. The simulation is a design calculation on synthetic labels. |

### 6.3 Step 2: labels of record; adjudication in the two-human design only (humans only) **[R4]**

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** No labels of record and no adjudication under R5.**]**

| Item | Rule | Why |
|---|---|---|
| **[R4]** Label of record, single-labeler design | The author's pass-1 label, for all 50 items. No adjudication, no `ADJ.csv`. | D34 item 3. |
| **[R4]** Label of record, two-human design | Author pass-1 and volunteer labels agree in the three-category scheme: the author's pass-1 label (if the two differ only as `SHOWS` against `NO_DISAGREEMENT`, both are negatives for every gate statistic; for the §6.4a `SHOWS` counts the item is sent to adjudication too). Otherwise: `adj_label` from `ADJ.csv`. | D37 item 3: "gate 1 uses labels adjudicated blind to scores". A deterministic merge; no label is created by the pipeline. |
| Which items are adjudicated (two-human) | All 50-item pairs whose labels differ in the three-category scheme (including one `UNSURE` against a definite label), plus the `SHOWS` / `NO_DISAGREEMENT` pairs of the row above. | Only disagreements need resolving. |
| Sheet (two-human) | `g1_adjudication_sheet.py` writes `P\gate1\adjudication_sheet.csv`: the author's `item_id`, question, opinions, statement, both labels and both `main_disagreement` notes. It contains no score, ranking, rating, model, condition or item kind, and the script may not import or read any such file (asserted in a unit test). It runs only after `KAPPA.json` exists. | BRIEF §4 and D37: adjudication blind to AI scores, rankings, model and condition. |
| Who and how (two-human) | The author and the volunteer discuss each listed item and agree one final label from the same four options. If they cannot agree, the final label is `UNSURE`. They write `P\labels\ADJ.csv` with exactly the columns `item_id,adj_label,reason` (`gate1.py` accepts only `adj_label`). The pipeline never writes this file. Before `ADJ.csv` is complete, no scorer output on the gate items, no LLM-annotator label and no result of any kind is shown to either of them, and no real-rank analysis runs (§6.5). The volunteer is not told the hypothesis during adjudication. | D37 implementation note. One adjudicator knows the hypothesis; that is stated in the paper (header wording). |

### 6.4 Step 3: scorer validity

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** The pass rule is §6.R5.6.**]**

| Item | Rule | Why |
|---|---|---|
| **[R4]** Gate set | **The 38 original statements** (`L[0:38]`), minus items whose label of record (§6.3) is `UNSURE` (excluded, counted and listed). The 12 N2 items are **not** in the gate set; they have their own check (§6.6). | D34 item 3: balanced accuracy of the scorer against the author's FIRST-PASS labels, the 12 N2 items checked separately. D37 item 3: adjudicated labels in the two-human design. |
| Human binary | Positive = `HIDES`. Negative = `SHOWS` or `NO_DISAGREEMENT`. | Matches the three-category scheme used for kappa. |
| AI binary (fixed now) | Scorer 1. Positive if `E ≥ 0.5`. Negative if `E < 0.5` or the extractor found zero cruxes. Missing `E` (parse failure) = wrong prediction. | 0.5 mirrors the labelers' "half or more not shown" rule, so both sides use one threshold. No threshold is tuned on labels. |
| Statistic | Balanced accuracy = (sensitivity + specificity) / 2. | BRIEF §4; insensitive to class imbalance. |
| Bootstrap | Resample the gate-set items with replacement, B = 10,000, `numpy.random.default_rng(20261116)`. A resample with no positives or no negatives scores 0.5. Lower bound = 2.5th percentile (lower end of the two-sided 95% interval). | The brief's "95% lower bound" could mean the 5th or the 2.5th percentile; the stricter one is used. A one-class resample carries no evidence of skill, so it is scored as chance. |
| **[R4]** Pass | **PASS** = the agreement step of §6.2 for the design that applies passed **and** lower bound > 0.5. **FAIL** = lower bound ≤ 0.5 (final as soon as it is computed, whatever the kappa), or the agreement step failed. **PROVISIONAL_PASS** (single-labeler design only) = lower bound > 0.5 on the pass-1 labels while the self-consistency kappa is not yet recorded (§6.5). | BRIEF §4 as amended by D34 items 2 and 3 and D37 item 3. |
| Record **[R4]** | `gate1.py` writes `P\gate1\gate1_computed__<utc>.json` (never overwritten): the design (from `DESIGN.json`), computed status (`PASS` / `PROVISIONAL_PASS` / `FAIL` / `INCOMPLETE`), kappa, AC1, balanced accuracy, bounds, confusion table, exclusions, hashes of every label file, `ADJ.csv` if any, sample, N2 item list, scores, this file. An Opus reviewer re-derives it from the raw files. Only then does the planning room (Fable, BRIEF §6 "gate decisions") write `P\gate1\GATE1_RESULT.json` and the decisions.md entry. The planning room may not record a status different from the computed one. A `PROVISIONAL_PASS` record is replaced exactly once, by `PASS` or `FAIL`, when the kappa step is recorded; the earlier record is kept under a dated name. | Hard rule 3 turns on this record, so it is written after an independent check and never by the analysis script itself. |
| Also reported, no rule **[R4]** | In the two-human design: balanced accuracy against the volunteer's own labels before adjudication (the hypothesis-blind number; same bootstrap), and against the author's pass-1 labels. In both designs: balanced accuracy against the LLM annotator's labels (§6.8), marked "LLM annotator, not a human label"; the same figures for scorer 2 (§8, A4 bar); Spearman correlation between `E` and the human binary; agreement on "is there any disagreement" (human `NO_DISAGREEMENT` vs AI zero cruxes). (Before R4 this row promised the number for the blind consultant's 40 items; there is no blind human in the single-labeler design, and the paper says so.) | None of these can rescue or sink the gate. |

### 6.4a Gate-1 additions **[R1]** (decisions.md D18; reported beside the gate, never part of the pass rule)

**[SUPERSEDED by R5 — kept for the audit trail, not in force,** except the "Binding wording rule", whose substance is re-anchored in §6.R5.6 (VALIDATED_PRESENCE).**]**

The pass rule of §6.4 is the brief's and is unchanged. These rows exist because, in the first
scoring of the gate sample, 10 of the 11 AI negatives were zero-crux rounds: the gate could pass on
"is there any disagreement" alone, while A2 uses a different contrast (shown vs hidden inside rounds
that have cruxes).

| Item | Rule | Why |
|---|---|---|
| BA on rounds with ≥ 1 crux (`BA_crux`) | Gate-set items where scorer 1 found ≥ 1 crux. Human binary and AI binary as in §6.4. Same bootstrap, same seed. Reported with its 2.5th-percentile lower bound, its n, and the count of human positives and negatives. | D18 item 2. Removes the zero-crux agreements from the specificity term. |
| Show-vs-hide subset (`BA_sh`) | Items of `BA_crux` whose adjudicated label is `HIDES` or `SHOWS` (human `NO_DISAGREEMENT` items are left out here and counted). Same bootstrap. | This is the contrast that identifies `beta_E`. |
| Zero-crux share | Number of correct AI negatives in the gate set that are zero-crux rounds, out of all correct AI negatives. | Shows where the gate's specificity comes from. |
| **Binding wording rule** | If the `BA_sh` subset has fewer than 5 human `SHOWS`, or its lower bound is ≤ 0.5, then wherever the abstract, results or discussion state that gate 1 passed, the same sentence must say: "the scorer is validated for detecting whether a disagreement is present, not for detecting whether a statement hides it". Every statement of `beta_E` (A2, A4, N1, N4) then carries the clause "the show-versus-hide contrast behind this estimate was not validated against human labels", and no directional claim about rankings appears in the title or abstract. | A pass earned on the presence of disagreement must not be worded as validation of the hide/show call. With an unstratified sample of 60 and few `VISIBLE` calls, this rule is expected to fire. |
| Human-labelled prevalence (`D1h`) **[R4]** | Now the paper's headline rate; defined in §6.7 (38 originals, labels of record). | D31 edit 4 / D34 item 7. |
| Scorer-v1 comparison | Gate balanced accuracy and lower bound recomputed with the E1-v1 scores. Appendix only. | §4, pre-freeze prompt changes. |
| Supplement of AI-`VISIBLE` statements | Not part of this pipeline. **[R4]** Human labels exist only in the files named in §5, whose row counts are fixed. (Before R4: "BRIEF §3.1 allows human labels only in `L1.csv` and `L2.csv`, whose schema is fixed at 44 rows, and the packets are built.") The human may add such a supplement by editing this file before freeze. Without it, the limitation is stated: the rare AI "shown" calls that identify `beta_E` were checked by humans only as far as they fall in the random sample. | D18 item 3 deferred it; the careful option is not to add label files the brief does not name. |

### 6.5 Before the gate is recorded

**[Partly SUPERSEDED by R5.** Still in force: the first paragraph (real-rank lock until `GATE1_RESULT.json` exists, now holding an R5 status with `"rules": "R5"`). Superseded (kept, not in force): the PROVISIONAL state; there is no PROVISIONAL state under R5.**]**

`a2_within_round.py`, `n1_winner_vs_mean.py` and every Tier-2 script refuse to read real ranks or
ratings unless `GATE1_RESULT.json` exists. Until then they run only on (a) within-rater shuffled ranks
(each rater's 4 ranks permuted across the 4 statements, `random.Random(424242)`), or
(b) synthetic dummy data from `make_dummy.py`. Why: BRIEF §3.3.

**[R4] PROVISIONAL state (D34 process; single-labeler design only).**

| Item | Rule | Why |
|---|---|---|
| When it exists | Single-labeler design, pass-1 file complete, validity step computed with lower bound > 0.5, re-derived by Opus, and recorded by the planning room as `PROVISIONAL_PASS` in `GATE1_RESULT.json`; `KAPPA.json` not yet written. | D34: "pipeline may start when the first-pass label file arrives ... results PROVISIONAL until the self-consistency check is recorded". |
| What it allows | Real-rank A2 and Tier 2, the N2 check on the 12 packet items, prevalence and the headline rate. **Not N2 scoring:** the N2 spec of record and D36 allow a scorer to touch N2 statements beyond the 12 packet items only once `GATE1_RESULT.json` records `PASS`, so N2 scoring waits for the final record. Everything that does run has every output file, RUNS.md row, table, figure and sentence stamped `PROVISIONAL`. The real-run lock (`common.check_kind`) maps `PROVISIONAL_PASS` to that stamp. No provisional number enters an abstract or a results section as a finding; a draft may hold it only with the stamp. | BRIEF §3.3 requires the gate to be recorded before the main analysis; the provisional record is that record, limited by its stamp. |
| How it ends | Kappa step recorded ≥ 0.60 → `PASS`; the stamp is removed by re-running the stamping step, not by editing outputs; no analysis is re-run or re-specified. Kappa < 0.60 or undefined → `FAIL`; every provisional output is re-stamped `EXPLORATORY_UNVALIDATED` and §12 applies. Pass 2 absent at handover → the results stay PROVISIONAL and are reported as "self-consistency not yet checked", which is not a pass. | Nothing about the analyses may depend on which way the consistency check falls. |
| Known weakness, to be stated in the paper | The author can see provisional results before making the second pass. The pass-2 labels feed only the self-consistency kappa, never a label of record, the balanced accuracy or the headline rate, so they cannot change any estimate; they can change whether the gate is final. The instructions tell the author not to look at any result before both files are saved. `gate1.py` records whether any `PROVISIONAL` real-rank output existed when `author_pass2.csv` arrived, and the paper prints that fact. | An honest record is the only guard available; the pipeline cannot control what a person reads. |
| Two-human design | No PROVISIONAL state. Nothing reads real ranks and no N2 statement beyond the 12 packet items is scored until kappa, adjudication and the validity step are all recorded. | The adjudicators must not have seen results (§6.3). |

### 6.6 N2 scorer check **[R4]** (D31 edit 2, D34 item 3, D36; separate from the gate-1 pass rule)

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** `N2_VALIDATED` cannot be earned under R5 (§6.R5.7).**]**

There are **12 items**. That is very few, and every row below is written with that in mind.

| Item | Rule | Why |
|---|---|---|
| Items | The 12 N2 statements of §6.1a, minus those whose label of record (§6.3) is `UNSURE` (excluded, counted, listed). Pooled over generators and cells; never split. | D36: "N2 validity claimed only for the pooled 12". |
| Scores | Scorer 1, frozen prompts, cruxes extracted from that round's opinions, binarised exactly as in §6.4 (`E ≥ 0.5` positive; zero cruxes negative). A missing `E` after the retry counts as the wrong call for that item. | "Scored by the frozen primary scorer like other gate items" (D31, D34 notes). |
| Statistic | The 2×2 table of AI binary against human binary and its balanced accuracy, printed with the same item bootstrap interval as §6.4 (descriptive at this n). | Same definitions as the gate, so the two can be read side by side. |
| **Pass rule (fixed now)** | `N2_CHECK = PASS` if and only if (a) gate 1 is PASS (or PROVISIONAL_PASS, in which case the N2 check is PROVISIONAL too), and (b) the one-sided Fisher exact test of association between AI binary and human binary on the 12 items (alternative: the scorer agrees with the labels more often than independence would give) has `p ≤ 0.05`. If the human labels, or the AI calls, are all in one class, p = 1 and the check does not pass. Any other outcome is `N2_CHECK = NOT PASSED`. Computed by `gate1.py`, re-derived by Opus, recorded by the planning room in `P\gate1\N2CHECK_RESULT.json`. | An exact test keeps its error rate at any n; a bootstrap bound on 12 items does not. With 6 `HIDES` and 6 not, `p ≤ 0.05` needs at least 10 of 12 calls right (5 and 5: p = 0.040); 9 of 12 does not pass. |
| Why not the gate's bootstrap rule | Simulated on synthetic labels (`analysis\planning\r4_power.py` → `r4_power.json`, seed 777, 2,000 simulations per cell; 1,000 with B = 2,000 for the bootstrap rule): at 12 items both rules pass a chance-level scorer rarely (Fisher 1.1 to 1.5%, bootstrap 0.6 to 2.6%, depending on class balance), and the Fisher rule passes a good scorer more often in every simulated cell (90%-accurate scorer: 84%, 74%, 65% against 71%, 47%, 28% with one half, two thirds, three quarters of the items `HIDES`). A one-sided 0.025 level was also simulated and rejected as too weak to be worth running (66% for a 90%-accurate scorer with balanced classes, 24% at 80%). | The choice between the candidate rules was made on synthetic data before any label or any N2 score existed. |
| What the rule can do (simulated, synthetic) | Pass rate with half the items `HIDES`: scorer right on 95% of items: 95%; 90%: 84%; 80%: 47%; 70%: 22%; chance: 1.5%. With three quarters `HIDES`: 78%, 65%, 32%, 13%; chance 1.1%. | **Stated in advance: a scorer that is right four times in five on N2 text fails this check more often than it passes.** `NOT PASSED` is a likely outcome and is not evidence that the scorer is invalid on N2 text. |
| What a PASS shows | That scorer 1's hide / not-hide calls on N2-style text agree with the human labels better than chance, in a pooled sample of 12. | |
| What a PASS does not show | How accurate the scorer is on N2 text (with 12 items the interval for balanced accuracy spans tens of points). That it is as accurate as on original statements. That it is valid for any one generator (2 or 3 items each) or any one cell (2 or 3 items each). That it is valid on the Qwen-written items independently of being the same family as the scorer. That differences between cells are measured without bias: the check has no power to detect a scorer whose errors differ by cell. | D36; `N2_ANALYSIS_SPEC.md` Amendment 2 ("no generator- or cell-level validity claim"). |
| Consequence | `PASS` → N2 results carry the label **`N2_VALIDATED`**, always written out as "scorer checked against human labels on 12 N2 statements pooled over five generators (2 or 3 per generator)" plus the validation wording of the header. `NOT PASSED` (or gate 1 not PASS) → every N2 table, figure and sentence carries **`EXPLORATORY`** and the words "the scorer was not validated on newly generated text"; N2 does not lead the paper (§7.3) and does not appear in the title; the abstract may mention it only with the word "exploratory". | D31 edit 2 / D34 item 3 (human): "N2 results count as VALIDATED only if this check passes; else EXPLORATORY". |
| Scope of the label | `N2_VALIDATED` attaches only to results from scorer 1, and only to estimates computed without the 45 N2 rounds that come from development launches (the N2 spec computes both versions; the version with them is printed beside it and labelled "including development launches"). Scorer-2 results on N2 are a robustness read and are never called validated on N2 text. `N2_VALIDATED` is a statement about the scorer on N2 text; it does not make N2 confirmatory (§10). | The 12 check items come from outside the development launches (§6.1a), and the scorer's prompts were revised on development launches. |
| Open to the human before freeze | With 24 items instead of 12 the same rule would pass an 80%-accurate scorer in about 85% of samples (balanced classes; 74% with three quarters `HIDES`). The number 12 is the human's (D31, D34) and is not changed here. | Said so the cost of the small n is visible while it can still be changed. |

### 6.7 Headline rate: how often statements hide the disagreement, from human labels **[R4]** (D31 edit 4, D34 item 7)

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** The human-checked rate is `H5` (§6.R5.3), which is not a headline.**]**

| Item | Rule | Why |
|---|---|---|
| What is the headline | Wherever the paper says how often statements hide the group's disagreement (title, abstract, first result, discussion), the number is `H` below, from human labels on original statements. A scorer-based rate never appears alone in the abstract and is always called secondary. | D31 edit 4 (human): headline = share in the HUMAN-labelled sample, with CI; scorer rate secondary. |
| Sample | The 38 original statements `L[0:38]`: a simple random sample of launches outside the development set, one random eligible round per launch, one random candidate of its 4. N2 statements are not in it. | "Original statements". The sample was drawn before any label or score existed and is not stratified. |
| Labels | Labels of record (§6.3): the author's pass-1 labels in the single-labeler design, adjudicated labels in the two-human design. | D34 item 3; D37 item 3. |
| Estimator | `H = n_HIDES / (n_HIDES + n_SHOWS + n_NO_DISAGREEMENT)`: the share labelled `HIDES` among the items with a definite label. | The simplest reading of "share of statements that hide disagreement". |
| `UNSURE` | Left out of numerator and denominator, counted and listed. Printed beside `H`, always: the two bounds obtained by counting every `UNSURE` item as not hiding (`n_HIDES / 38`) and as hiding (`(n_HIDES + n_UNSURE) / 38`). If the bounds differ from `H` by more than the half-width of its interval, the text says the rate depends on the unsure items. | BRIEF §4 excludes and reports unsure items; the bounds show what the exclusion could hide. |
| Interval | Wilson 95% score interval on `H` with n = the number of definite labels. No finite-population correction (721 launches). | Each item is a different launch and a different round, so a cluster bootstrap by round or launch is the same as an item bootstrap; at n ≤ 38 the Wilson interval has better coverage than a percentile bootstrap and needs no seed. |
| What it estimates | The probability that a randomly chosen candidate, from a randomly chosen eligible round of a randomly chosen non-development launch, is labelled as hiding. Launches count equally; rounds of launches with several eligible rounds count less than in a round-weighted rate. All-human, four-candidate rounds only (§2). | Said so the number is not read as a rate over all statements the system ever produced. |
| Printed beside it, always | (i) The conditional rate `n_HIDES / (n_HIDES + n_SHOWS)` (among statements whose group did disagree) with its Wilson interval, and the share `NO_DISAGREEMENT`. (ii) Two-human design: each annotator's own `H` before adjudication, the volunteer's first, labelled "hypothesis-blind annotator". (iii) The LLM annotator's `H` on the same 38, labelled as such. (iv) **Secondary:** scorer 1's rate on the same 38 items (share with `E ≥ 0.5`, zero-crux = not hiding, Wilson interval) and over the whole confirmatory set (§7.3 prevalence). | D34 item 7: scorer rate secondary. A reader can see at once whether the scorer over- or under-counts against the labels. |
| Binding wording | The headline sentence names n (38 or fewer), the interval, and the annotator wording of the header ("as labelled by a single hypothesis-aware human annotator", or the two-human form). At n = 38 the interval is about ±15 percentage points near one half (§6.1b); the paper calls the rate an estimate from a small sample and does not compare it numerically with rates in other studies. | BRIEF §10: reviewers dislike small samples and implicit messages. |
| When it is reported | It needs no scorer, so it is reported in every state in which the labels are complete. If the agreement step of §6.2 failed, it is printed with the sentence that agreement was not established and is not presented as the paper's headline (§12). In the PROVISIONAL state it carries the stamp. | A rate from labels whose consistency failed the pre-set check cannot head the paper. |

### 6.8 LLM annotator **[R4]** (D34 item 4, D36; supplementary, never a human label)

**[SUPERSEDED by R5 — kept for the audit trail, not in force.** gpt-oss-120b is the quote extractor only; the supplementary LLM panel is §6.R5.4.**]**

| Item | Rule | Why |
|---|---|---|
| Model | `gpt-oss-120b` (OpenAI), served through `P\serving\endpoints.json` alias `gptoss-120b`; repository revision and serving settings are written to `P\gate1\llm_annotator\annotator_manifest.json` before its first call on a packet item and do not change after. Family rule of §4 holds: not Qwen, not Gemma, not Mistral, not Microsoft phi, not Meta Llama, not IBM Granite. | D36. |
| Input | One packet item per call, in a new conversation with no history (fresh context), no system prompt beyond what the served chat template adds by itself. User message = the volunteer version of the §5 instructions, verbatim, then the item in the packet's own text layout (question, numbered opinions, statement), then one added line: `Return JSON only: {"main_disagreement": "<your points, or none>", "label": "HIDES" or "SHOWS" or "NO_DISAGREEMENT" or "UNSURE"}`. That line is the only text not in the human instructions. | D34 item 4: "same instructions and blinding". A format line is needed to read the answer; it adds no guidance about the task. |
| Blinding | Identical to the human packet: it receives nothing the labeler does not see (§5 "does not see" row), and the instruction text does not state the hypothesis. It never receives another item, a score, a crux list, or any human label. | D34 item 4; D36. |
| Decoding | temperature 0, seed 0, `max_tokens` and the reasoning setting as recorded in the manifest (the model's reasoning stays on at the served default; it is a labeler here, not the instrument). One retry with seed 1 on a parse failure or an invalid token; if it still fails the label is missing, counted and reported, and never filled. | D36: "fix temperature/seed". |
| Format try-out | Before any packet item: at most 20 calls on development-launch rounds to check that the output parses; at most one revision of the added format line; logged. No change after the first packet-item call. | Same discipline as the scorer prompts (§4). |
| Items and timing | All 50 pass-1 items, once. No second pass (its decoding is deterministic). It may run as soon as the packets and the manifest exist. | |
| Output | `P\gate1\llm_annotator\llm_labels.csv` (`item_id,label,main_disagreement`, author pass-1 ids). **Never in `P\labels\`**; it is not a label file, does not trigger the freeze, and no step that reads human labels reads it in their place. It is not shown to the author or the volunteer before the author's two files are saved and, in the two-human design, `ADJ.csv` is complete. It is never used in adjudication and never changes a label of record. | BRIEF §3.1: never create or substitute labels. D34 item 4: "never called human". |
| Author–LLM agreement | Cohen's kappa on the three categories of §6.2 (`UNSURE` kept) between the author's pass-1 labels and the LLM labels on the 50 items, with Gwet's AC1 (formula of §6.2), each with a percentile bootstrap 95% CI over items (B = 10,000, `numpy.random.default_rng(20261134)`); items with a missing LLM label are left out and counted. Also printed: the 4×4 table, the same two statistics on the 38 originals and on the 12 N2 items separately, and in the two-human design the same against the volunteer's labels and against the labels of record. | D34 item 4, D36: "kappa + AC1 with CI". |
| Status | Supplementary. No cut-off, no rule, no effect on gate 1, the N2 check, the headline or any label. Reported whatever it shows (BRIEF §3.10). | D34 item 4. |
| Binding wording | "an LLM annotator (gpt-oss-120b) given the same instructions". Never "human", "second rater", "second annotator" without "LLM", "inter-rater", "inter-annotator" or "independent validation". High agreement is worded "the LLM annotator's labels agreed with the author's"; it is not evidence that the author's labels are unbiased, since a model can share a reading with a hypothesis-aware person for reasons unrelated to correctness. Low agreement is reported as a limitation of the labels' generality, not explained away. | D34 item 4. |

### 6.9 Second scorer: validity bar before use **[R4]** (D36; applies to A4, §8)

| Item | Rule | Why |
|---|---|---|
| Model | `granite-4.2-30b` (IBM), alias `granite4.2-30b`, served with no reasoning parser, thinking off; revision in `scorer_manifest.json` before its first call on a non-development item. Prompts E1, L1, C1 and decoding exactly as §4. | D36. |
| V1, technical bar (decides the fallback; development launches only) | Smoke of at least 200 calls on development-launch rounds, extraction and labelling. Bar **(J)**: after the one retry, statements left without `E` are at most 5% of the statements in the smoke. If the 30b model cannot be deployed or misses the bar, the fallback `granite-4.2-8B` is put through the same smoke with the same bar. If both miss it there is no scorer 2: A4 is reported as "not run: no second scorer met the technical bar" and leaves the Holm family. **The fallback is decided on this smoke only**, before scorer 2 has scored any gate item or any item of the confirmatory set, and never because of V2 or V3. | D36: smoke ≥ 200 calls on development launches only; fallback named. Scorer 1's own rate on the full run was 135 of 7,840 statements without `E` (1.7%, decisions.md D32), so 5% is a loose format-parity bar. Choosing between two scorers after seeing how they agree with labels or with scorer 1 would be choosing on outcome. |
| **[R4a]** Outcome of V1 for Granite, and the ordered fallback list (decisions.md D44) | Both Granite models missed V1 on the development smoke: `granite-4.2-30b` left 75.4% of statements without `E`, `granite-4.2-8b` 57.5% (bar 5%). Failure mode: on one-crux rounds the model returns two labels, which the frozen parser rejects. Neither is scorer 2. **Two further candidates, tried in this order, and no others:** (1) `tiiuae/Falcon-H1-34B-Instruct` (Technology Innovation Institute); (2) `CohereLabs/c4ai-command-r7b-12-2024` (Cohere). Each gets the same V1 smoke (at least 200 calls, development launches only, statements without `E` after the one retry at most 5%), with prompts E1 and L1, the decoding of §4 and the parser **exactly as frozen**: no prompt, parser, retry or output-format change is made to help a candidate pass. Serving-only settings (image version, chat template as shipped by the model's own repository, thinking off if the template has such a switch) are logged and are not prompt changes. The first candidate that meets V1 is scorer 2; the second is tried only if the first cannot be deployed or misses V1. A candidate that cannot be deployed for any reason, including a licence gate nobody has accepted, counts as not meeting V1. Cap $2 per candidate (D44). **If neither meets V1 before this file freezes, there is no scorer 2:** A4 is reported as "not run: no candidate passed the pre-registered technical bar", with all four smoke results printed; A4 leaves the Holm family; N2 has no robustness scorer and says so; nothing else changes. No candidate is added, and no smoke is re-run to pass, after the freeze. | D44. The list is closed and ordered so that the second scorer cannot be picked by trying models until one agrees. Family check, from the model cards opened on 2026-11-15: Falcon-H1 is TII's own hybrid Transformer + Mamba architecture, and the Instruct model's listed base is TII's own `Falcon-H1-34B-Base`; the Command R7B card lists no base model and describes Cohere's own pretraining followed by supervised fine-tuning and preference training. Neither card names Qwen, Llama, Mistral, Gemma, Phi, Granite or an OpenAI model as a base or teacher; those names appear only in benchmark tables. **Limit:** neither card states "trained from scratch" or lists its training data, so the absence of synthetic data from other families is not verified, only not indicated. Command R7B is gated (terms must be accepted on the hub by the account holder, a human step) and is CC-BY-NC; Falcon-H1 is under the Falcon-LLM licence. Falcon is first because it is close in size to scorer 1 (34B against 27B) and is not shown as gated. |
| Scope of scorer-2 scoring now | (a) The 50 packet items. (b) A seeded sample of 250 rounds, all 4 candidates each (1,000 statements): `rng = random.Random(20261133)`; `S = rng.sample(sorted(confirmatory launch ids), 250)`; for each, `rng.choice(sorted(its eligible round ids))`. (c) N2 statements, only after gate 1 and under the N2 spec. Scorer 2 does **not** score the full confirmatory set unless the experiment council votes for it later (D36). | D36 (cost cutter): gate items + seeded ~1,000-statement sample; full refit deferred. |
| V2, validity against the human labels | Scorer 2's own balanced accuracy on the 38-item gate set against the labels of record, same binarisation, bootstrap and seed as §6.4. Bar: 2.5th-percentile lower bound > 0.5. | The same bar scorer 1 must clear; no looser bar for the robustness instrument. |
| V3, agreement with scorer 1 | On the 1,000-statement sample: Cohen's kappa of the two binary calls (`E ≥ 0.5`; zero cruxes = negative; statements missing either `E` left out and counted) and Spearman correlation of `E` over statements where both found at least one crux, **[R4a]** each with a **launch-cluster percentile bootstrap** 95% interval: resample the 250 sampled launches with replacement, keep each launch's 4 statements together, recompute the statistic; B = 10,000, `numpy.random.default_rng(20261121)`; 2.5th and 97.5th percentiles; resamples in which kappa is undefined are counted and printed. This is what `analysis\a4_bar.py` computes, and it is confirmed as the interval of record for V3. (R4 first wrote "§7 method of record" here. That was wrong: the wild cluster bootstrap-t is defined for a regression coefficient with a cluster-robust standard error, and kappa and Spearman have neither.) The interval is descriptive: its coverage was not checked, the reference line is compared with the point estimate only, and no rule reads the interval. Reference line **(J)**: kappa ≥ 0.40. | D36 asks for agreement with the primary scorer, with a threshold. D44 asks for the interval to be confirmed. One round per launch is sampled, so the launch is the natural resampling unit. |
| What the bars decide | V1 and V2 both met → scorer 2 is "a second scorer validated against the same human labels" (with the header's annotator wording) and its results may be used as the robustness read in A4 and N2. V2 not met → every scorer-2 number is still reported, marked "second scorer not validated", A4 leaves the Holm family, and scorer 2 can neither support nor contradict any claim. **V3 never removes scorer 2**: if V1 and V2 are met and kappa with scorer 1 is below 0.40, the paper states "two scorers that each agree with the human labels disagree with each other; results depend on the scorer", and every scorer-1 estimate of `beta_E`, of prevalence and of an N2 contrast carries that clause. | A robustness check that is dropped whenever it disagrees with the primary is not a robustness check. So agreement with scorer 1 has a threshold that changes the wording of the primary results, not the membership of the second scorer. |
| Order | V1 before any non-development item. V2 and V3 are computed after the labels exist (V2 needs them) and before any scorer-2 real-rank fit; both are recorded in `P\gate1\A4_BAR.json` with the gate record. | "Before use". |

## 7. A2: within-round rank vs erasure (confirmatory)

| Item | Rule | Why |
|---|---|---|
| **[R4]** Data | The confirmatory set of §2: eligible rounds of the 721 launches outside the development set. Z-scoring constants for length and clarity are computed once on the statements of this set. The fit on all 871 launches is sensitivity model A2d and nothing else. | D31 edit 6 / D34 item 8 (human). |
| Outcome | Per rater and round, ranks converted to mid-ranks 1..4 (1 = best) and then to `y = (4 − midrank) / 3`, so 1 = ranked best, 0 = ranked worst. | Outcome is rank within round (BRIEF §5); mid-ranks keep ties; the 0-1 scale gives a readable coefficient. |
| Predictor | `E` from scorer 1, raw 0-1 scale. | A coefficient per unit of `E` is the gap between a fully hiding and a fully showing statement. |
| Control: length | `log(word count)`, words = matches of `[A-Za-z0-9']+`; z-scored over all statements in the analysis set. | Longer statements can show more and may be ranked differently for length alone. |
| Control: clarity | Flesch Reading Ease, `206.835 − 1.015·(words/sentences) − 84.6·(syllables/words)`. Sentences = number of non-empty pieces after splitting on `[.!?]+`, minimum 1. Syllables per word = number of `[aeiouy]+` groups in the lower-cased word, minus 1 if the word ends in "e" but not "le" and the count is above 1, minimum 1. Z-scored like length. | Deterministic, no model and no package version; an outside judge can recompute it with a regex. |
| Model | `y_irs = a_ir + beta_E·E_s + beta_L·zLen_s + beta_C·zClar_s + e_irs`, with a fixed effect `a_ir` for each (rater, round). Fitted by OLS after demeaning within (rater, round). Every rater-round has equal weight. | The fixed effect makes it a within-round comparison only. A linear model on ranks is simple and handles ties. |
| Rounds with no variation in `E` | Kept (they inform the controls) and counted. They add nothing to `beta_E`. | Dropping them would change nothing for `beta_E` and would hide how often the scorer cannot separate candidates. |
| Uncertainty | Cluster bootstrap over `launch_id`: resample launches with replacement, keep all their rounds and raters, refit. B = 10,000, `numpy.random.default_rng(20261119)`, percentile 95% interval. Z-scoring constants are computed once on the full set. **[R2] Superseded as to method:** the interval of record is the wild cluster bootstrap-t of the "[R2] Interval method of record" row below. Clusters (`launch_id`), B, seed and the z-scoring rule are unchanged. | Bootstrap by group (BRIEF §5). |
| Interval method check (pre-freeze only) | Coverage of the percentile interval is checked on ≥ 200 null reshuffles of shuffled or dummy data. If coverage is below 93% **(J)**, the method is changed to a more conservative one in this row, with a decisions.md entry, before freeze. After freeze the method written here is fixed. | decisions.md D8 saw 36 of 40; that is within noise but must be settled before real data, not after. |
| **[R1]** Interval method of record | The check ran: 185 of 200 = 92.5%, below 93% (decisions.md D19, `analysis\ALIGNMENT.md`). The rule is obeyed; the check is not re-run to pass. **Selection rule (fixed here):** candidates are the launch-cluster BCa interval and the wild cluster bootstrap interval, each checked on ≥ 400 within-rater reshuffles at B = 2,000 with the A2 primary model. The method of record is the candidate with coverage ≥ 93% that is closest to 95%; if neither reaches 93%, the one with the higher coverage, and the paper states the measured coverage as a limitation. The selected method replaces "percentile" in the Uncertainty row above and in §8 for every launch-bootstrap interval (A2, A2b-A2i, N1, A4, A3, N3, N4), with seeds and B unchanged; the bootstrap p-value is computed by the matching method. **Method selected: see the [R2] row below** (this cell said "not yet recorded" when R1 was written). The selection uses shuffled ranks only, so it stays blind to outcomes. Gate-1 intervals (§6) are item-level and are not affected. | The rule was written before the check; a failed check changes the method, never the threshold. |
| **[R2]** Interval method of record | **Wild cluster bootstrap-t**, Rademacher weights (+1 or −1 with equal probability, one draw per launch), clusters = `launch_id`, unrestricted residuals, CR1 cluster-robust standard error (`se`, factor G/(G−1), G = number of launches). Source: `analysis\ALIGNMENT.md` "Interval method of record", decisions.md D24, `coverage_interval.py` → `coverage_interval.json`; implemented in `common.wild_cluster_t`. For each draw b: flip the sign of each launch's score contribution, recompute the coefficient and its CR1 standard error, `t*_b = (beta*_b − beta_hat) / se*_b`. **95% interval (equal-tailed bootstrap-t):** `[beta_hat − se·q_0.975(t*), beta_hat − se·q_0.025(t*)]`. **Selection result:** on 400 within-rater reshuffles of the real ranks (`random.Random(800000 + i)`), dummy `E` proxy, A2 primary model, B = 2,000: wild 386/400 = 96.50%, cluster BCa 387/400 = 96.75%, old percentile 387/400 = 96.75%. Both candidates passed 93%; wild is the closer to 95%, so the rule picks it. The two differ by one reshuffle, so the choice is mechanical and is not evidence that wild is better. The earlier 92.5% (B = 500, 200 reshuffles) is read as Monte Carlo noise; the rule was followed anyway. **B and seeds for the analyses of record are unchanged** (B = 10,000; seeds as written in §7 and §8, now seeding the Rademacher draws); B = 2,000 was the setting of the coverage check only. **Applies to** every launch-clustered interval in this file: A2, A2b-A2i, A4, N4 (regression coefficients) and N1, A3, N3 and the §7.3 prevalence shares (means, fitted as an intercept-only regression so the same method applies). "Launch-bootstrap standard error" in §7.1 means the CR1 `se` above. **Limitation, to be stated in the paper:** coverage was checked for the A2 primary model only, with a dummy `E` and shuffled ranks. The mean-type tests (N1, A3, N3), the N4 interaction and the prevalence shares had no coverage check of their own under this method. With few informative launches (§7.1) the coverage for `beta_E` on the real `E` may differ from the checked value. | D19 rule, executed blind. One method for every launch-level interval keeps the paper consistent. The interval written here is the one whose coverage was measured. |
| Primary estimand and test | `beta_E`. Two-sided, alpha = 0.05. The association is called detected if the 95% interval excludes 0. **[R2]** Bootstrap p (replaces the percentile formula `2·min(#{b ≤ 0}+1, #{b ≥ 0}+1) / (B+1)`, which was written for bootstrap estimates and does not apply to bootstrap-t): two-sided, symmetric, `p = (#{b : |t*_b| ≥ |t_obs|} + 1) / (B + 1)` with `t_obs = beta_hat / se` and `t*_b` as in the "[R2] Interval method of record" row. Reported. The decision stays with the interval: "detected" means the 95% interval excludes 0. The interval is equal-tailed and the p-value is symmetric, so near 0.05 they can disagree; if they do, both are printed, the interval decides, and the result is called borderline in the text. The same p formula is used for every Tier-2 family test (§8, §9). | One estimand, one test. The interval is what the coverage check measured, so it carries the decision. |
| Sign reading | `beta_E > 0`: hiding statements are ranked better. `beta_E < 0`: showing statements are ranked better. | Stated before the data are seen. |
| If the interval includes 0 | Reported as "no association detected at this precision", with the interval. No claim of "no effect", no rebuttal of prior work: no equivalence margin was set that we could justify. | Statistician rule 3; a noisy scorer biases `beta_E` toward 0. |
| Interpretability floor **(J)** | If fewer than 50 launches have at least one round with within-round variation in `E`, `beta_E` is still reported, but the paper says the rank question was not measurable at this sample and makes no directional claim. **[R1]** This floor is now the NOT MEASURABLE tier of §7.1; the number 50 is unchanged. | A cluster bootstrap on a few dozen informative clusters is not trustworthy. |

### 7.1 Informativeness tiers for A2 **[R1]** (fixed before any real rank is read)

`beta_E` is identified only by rounds whose four candidates do not all have the same `E`. The tier
says what the paper may claim. It is computed from scorer output and shuffled ranks only, so it is
known, and logged, before unblinding.

| Item | Rule | Why |
|---|---|---|
| Informative round | A round in the A2 analysis set (≥ 1 crux, no missing `E`) whose 4 candidates take at least 2 distinct values of `E`. | Only these rounds move `beta_E` under the (rater, round) fixed effect. |
| Counts **[R4]** | `R_inf` = number of informative rounds; `K_inf` = number of launches with ≥ 1 informative round, **both counted in the confirmatory set (development launches excluded)**. The `MDE80` of the next row is likewise computed on the confirmatory set. Also reported as side figures: the same counts with the 150 development launches included, and for `E_pos` (A2e). **The tier of record is the one computed on the confirmatory set.** `gate1\A2_TIER.json` as first written (decisions.md D35: all launches, `K_inf` = 168, `MDE80` = 0.0509, INFORMATIVE; 144 informative launches outside the development set) was computed before R4 on all launches; it is kept under a dated name and `a2_informativeness.py` is re-run on the confirmatory set, with shuffled ranks only, before any real rank is read. Disclosure: the count 144 was already logged when this row was written; the thresholds below were fixed before it (R1) and are not changed; excluding launches can only lower `K_inf` and raise `MDE80`. | The launch is the bootstrap cluster, so `K_inf` is the effective cluster count. D31 edit 6 / D34 item 8. |
| Blind minimum detectable effect | `MDE80 = 2.80 × SD(beta_E)` over 400 null fits of the A2 primary model on the real statements and real scorer-1 `E`, with each rater's 4 ranks permuted (`random.Random(430000 + i)`, i = 0..399). Units: the 0-1 rank scale `y`; 0.10 on `y` is 0.3 of a rank position. | 2.80 = 1.96 + 0.84 (two-sided 5%, 80% power). Shuffled ranks are allowed before the gate (BRIEF §3.3). Known bias: the shuffle removes agreement between raters of a round, so this MDE is optimistic; hence the downgrade rule below. |
| When and where recorded | `a2_informativeness.py` writes `P\gate1\A2_TIER.json` (`R_inf`, `K_inf`, `MDE80`, tier, seeds, input hashes) after the full scoring run and before `GATE1_RESULT.json` allows real ranks. `a2_within_round.py --kind real` refuses to run without it. The counts and tier go into decisions.md. | The tier cannot be chosen after the estimate is seen. |
| Tier INFORMATIVE **(J)** | `K_inf ≥ 100` and `MDE80 ≤ 0.10`. A2 is the lead result. A directional claim is allowed in the wording of §1, subject to §6.4a and A2b. | 100 clusters is a common working minimum for a cluster bootstrap; an effect below 0.3 of a rank position between a fully hiding and a fully showing statement is too small to carry the paper's argument. Both are judgement calls, fixed now. |
| Tier LOW-POWER **(J)** | `K_inf ≥ 50` and not INFORMATIVE. A2 is run and reported in the main text with its interval, `R_inf`, `K_inf` and `MDE80`. If the interval excludes 0: "an association was detected in `R_inf` informative rounds; the estimate comes from a small, selected subset, is likely to overstate the effect and needs replication". Not in the title; in the abstract only with `R_inf` and that caveat. If the interval includes 0: "not measurable at this sample: an effect up to `MDE80` could not have been detected". Never "no association". | A significant result at low power overstates the effect; a null at low power says nothing. |
| Tier NOT MEASURABLE | `K_inf < 50`. `beta_E` is printed in a table with its interval. No directional claim anywhere. The paper says the rank question could not be tested in these data and gives the reason: the candidate sets offered to participants almost never differed in whether they showed the disagreement. | The floor that was already in §7. |
| One-way downgrade after unblinding | If the tier is INFORMATIVE but `2.80 ×` the launch-bootstrap standard error of `beta_E` on real ranks exceeds 0.10, the tier becomes LOW-POWER. The rule looks at the standard error only, never at the estimate or its sign. There is no upgrade. | Covers the optimism of the shuffled MDE. |
| Thresholds are final | 50, 100 and 0.10 are not moved after `K_inf` or `MDE80` is known, whether or not this file has frozen by then. | D18 item 2: record the count before freeze, floor unchanged. |
| What the tier does not change | The model, the estimand, the test, the sensitivity models, the Tier-2 family and gate 1. Every run is reported in every tier (BRIEF §3.10). | The tier governs wording and ordering only. |

### 7.2 Alternatives considered and not adopted as primary **[R1]**

| Option | Ruling | Why |
|---|---|---|
| Restrict A2 to informative rounds | Not the primary; added as sensitivity A2i. | Under the fixed effect the other rounds add nothing to `beta_E` and only inform the control slopes, so the restriction changes little; reporting `R_inf` beside A2 says the same thing openly. |
| Promote A2e (`E_pos`, `SIDED` counted as shown) | Rejected as primary; stays a sensitivity model with a wording rule. | It varies in more rounds (13 of 34 against 3 of 34 on the development probe), but it measures leaving a topic out or blurring it, not hiding a disagreement. A one-sided statement tells the reader nobody disagreed, which is the construct of BRIEF §1 and §4. Promoting it because it varies more would change the construct to fit the data. |
| A graded per-crux severity score (for example VISIBLE 0, SIDED part-way, OMITTED 1) | Rejected. | `E` is already the per-crux share. Any intermediate weights would be invented; there are no human labels to validate them, and the gate validates the binary hide/show call only. |
| Promote N1 (winner vs round mean) | Rejected. | Same identification: `d_r` is exactly 0 in every round with no variation in `E`. N1 uses less of the data than A2 and has no controls. |
| Between-round design (round-mean `E` against a between-round outcome) | Rejected, also as secondary. | Ranks are forced within a round, so they carry no between-round information; an absolute outcome (`ratings.agreement`) would be confounded with question, group and how much disagreement there is. And it adds no variation: a round's mean `E` differs from 1 only in the informative rounds A2 already uses. Any such analysis stays exploratory (§10). |
| Make N2 the confirmatory test | Rejected as confirmatory; adopted as lead result when A2 is not INFORMATIVE (§7.3). | N2 creates variation by design, but its statements are never ranked by participants. It answers "what do models write under which instructions", not "what do participants reward". It cannot test the hypothesis of §1. |

### 7.3 What the paper leads with **[R1]** (decided by gate 1 and the §7.1 tier, both fixed before unblinding)

| State | Lead result | Binding wording |
|---|---|---|
| Gate 1 FAIL or NOT EVALUATED | §12, unchanged. | §12. |
| Gate 1 PASS, tier INFORMATIVE | A2 `beta_E`. Then Tier 2, then N2. | §1, §6.4a, A2b. |
| Gate 1 PASS, tier LOW-POWER or NOT MEASURABLE | (1) **Prevalence** (descriptive, pre-specified here): `D1h` from §6.4a; and from scorer 1 over all eligible rounds with ≥ 1 crux, the share of statements with `E = 1`, the share with at least one `VISIBLE` crux, the label shares, and `R_inf / rounds`, each with a launch-bootstrap 95% interval (seed 20261128). (2) **N2**, under its own analysis spec, whose SHA-256 is logged in decisions.md before any N2 statement is scored; only if its manipulation check passes. (3) A2 with its §7.1 wording. | The title and abstract make no claim that rankings favour or do not favour hiding statements. The key message is stated plainly: "participants were almost never offered a candidate that showed the disagreement, so these data cannot say what they would reward; whether a statement shows it is under the control of the instruction given to the model" (second half only if N2 supports it). N2 is described as "pre-specified in a hashed analysis plan, not the confirmatory test of the rank question, statements not ranked by humans". The prevalence result is worded as description of the all-human, four-candidate rounds, and carries the §6.4a clause if that rule fires. The novelty sentence of BRIEF §1 stays "first test of whether rankings favour hiding statements", followed by the plain statement that the test was not informative and why. |

**[R4] Changes to the table above (they govern where the cells differ).**
(a) **Headline rate.** In every state in which the agreement step of §6.2 passed, the first number
the paper gives for how often statements hide disagreement is `H` of §6.7, from human labels on 38
original statements, with its Wilson interval. Scorer-based prevalence ("from scorer 1 over all
eligible rounds…" in the third row) is secondary, is computed on the confirmatory set of §2 only,
and is printed beside `H`, never instead of it. In the INFORMATIVE state A2 is still the lead
result on the rank question; `H` is the headline for the rate.
(b) **N2 leads only if it is `N2_VALIDATED`** (§6.6) and its manipulation check passes. If the N2
check is NOT PASSED, the lead in the third row is `H` and the prevalence quantities alone; N2 is
reported in the main text with the label EXPLORATORY and the second half of the key message
("whether a statement shows it is under the control of the instruction given to the model") is
dropped from the abstract.
(c) **N2 spec reference. [R5]** The N2 analysis spec of record is `analysis\N2_ANALYSIS_SPEC.md` with
Amendments 1 to 5, SHA-256 `afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0`
(decisions.md D50a; Amendment 5 = R5 validation status, N2 never "validated"). It supersedes
`4085b78d…77ba91` (Amendment 4, D44), `9a966d57…94c81c0d` (Amendment 3, D43), `126787ad…2c0dc60b`
(Amendment 2; the hash this cell carried before R5 was stale, D49d item 3), `707c7fa2…` and `3875c61e…`.
If the spec is amended again before any N2 statement is scored, the hash logged last in decisions.md
before that scoring is the one of record.
(d) **PROVISIONAL.** In the single-labeler design every lead result carries the PROVISIONAL stamp
until the self-consistency step is recorded (§6.5).
(e) **Validation wording** of the header applies to every sentence that states gate 1 passed.

**[R5] Reading of this table under §6.R5.** "Gate 1 PASS" reads as VALIDATED_BOTH, VALIDATED_PRESENCE or
VALIDATED_HIDE_EVIDENCE; "Gate 1 FAIL or NOT EVALUATED" reads as FAIL or NOT_EVALUATED; EXPLORATORY_UNVALIDATED
follows §6.R5.5. Under VALIDATED_PRESENCE and VALIDATED_HIDE_EVIDENCE the §6.R5.6 claim limits govern the
INFORMATIVE row (no "confirm"/"detected" for `E`-based results under VALIDATED_PRESENCE; no directional claim
in title or abstract). (a) "`H` of §6.7" reads as `H5` of §6.R5.7, which is not a headline. (b) N2 is never
`N2_VALIDATED` (§6.R5.7), so N2 never leads as validated; it may be reported as an EXPLORATORY descriptive
extension. (d) There is no PROVISIONAL state. (e) The validation wording is that of §6.R5.6 and §6.R5.2.

The prevalence quantities use no ranks. They may be computed before the gate is recorded but are
reported as findings only after gate 1 is PASS.

**Pre-specified sensitivity models (reported beside A2; they never replace it):**

| Model | Change from A2 | Why |
|---|---|---|
| A2b | Adds rater-level `zOwnSim` = cosine similarity between the statement and that rater's own opinion, `sentence-transformers/all-MiniLM-L6-v2`, z-scored. | The methodologist's self-interest confound. The brief fixes A2's controls as length and clarity, so this is a sensitivity model. **Binding wording rule:** if `beta_E` in A2b has the opposite sign or its 95% interval includes 0, the abstract and discussion must say the association cannot be separated from raters preferring statements close to their own view. |
| A2c | Replaces Flesch clarity with a 1-5 clarity rating from scorer 2 (prompt C1), z-scored. Runs only if the A4 cost cap allows after scorer-2 erasure scoring. **[R4]** Scorer 2 is now granite-4.2-30b and scores the full set only after a further council vote (§8, A4); without that run A2c is not run and is reported as such. | Readability is a narrow proxy for clarity; a different model than scorer 1 avoids shared error with `E`. |
| A2d **[R4]** | A2 on all 871 launches, **including** the 150 development launches (z-scoring constants recomputed on that set). Before R4, A2d was the fit without them and the all-launch fit was the primary; the two have changed places. A2d is a sensitivity figure only. If it differs from A2 in sign or in whether its interval excludes 0, the results text says so and the claim follows A2. | Chair ruling §4.1 (report with and without pilot groups); D31 edit 6 / D34 item 8 decide which one is confirmatory. |
| A2e | Alternative score `E_pos` in which `SIDED` counts as shown (the pilot PREREG's "retention" definition). | Shows how much the result depends on the one-sided-statement choice in §4. **[R1] Binding wording rule:** A2e measures leaving a point out or blurring it, not hiding a disagreement; it is never called crux erasure. If A2 is LOW-POWER, NOT MEASURABLE or its interval includes 0 while A2e's interval excludes 0, A2e appears only as a secondary result with that wording, never in the title or as the answer to the question of §1. |
| A2f | Adds `zVague` = count of vague terms per 100 words, z-scored. Fixed list **(J)**, whole-word, case-insensitive: some, many, various, several, certain, often, sometimes, generally, may, might, could, perhaps, possibly, balance, balanced, appropriate, reasonable, important, consider, considered, factors, issues, aspects, range, complex. | Novelty scout 1 asked for a vagueness control. It is a sensitivity model, not a primary control: the brief fixes the controls, and vagueness is partly the construct itself (`BLENDED`), so controlling for it in the main model would remove real effect. |
| A2g | `E_w`: each crux weighted by the share of members named on either side of it. | Scout 2's salience weighting, with weights that come from the opinions and are fixed in advance. |
| A2h | A2 without the clarity control (length only). | Clarity may be a mediator: the writing choice that hides a crux may also make text read more smoothly, so the clarity control can absorb real effect. Both estimates are always printed side by side. If they differ in sign or in whether the interval excludes 0, the results section must say so. The primary stays with clarity because the brief names it. |
| **[R1]** A2i | A2 fitted on informative rounds only (§7.1); control slopes are then estimated inside those rounds. | Checks that `beta_E` does not depend on control slopes learned from rounds that cannot identify it. |

**Novelty-scout recommendations (decisions.md D4, D5): adopted, modified or rejected.**

| Recommendation | Ruling | Why |
|---|---|---|
| Per-crux LLM-judge label as the primary score | Adopted in substance. Our four labels map to the scout's three (preserved = `VISIBLE`; blurred = `BLENDED`; erased = `SIDED` or `OMITTED`) and collapse to shown / hidden. | Four labels keep the one-sided case separate, which A2e needs. |
| Salience weighting in the primary | Modified: unweighted primary, weighted variant as A2g. | No validated weights. |
| Embedding position-axis score as the A4 second scorer | Rejected for A4; allowed as exploratory. | The brief says "second scorer model". A stance-position score cannot tell a statement that names the disagreement from a vague mid-point statement (scout 1's own reading), and embedding results flip with the embedding model. |
| LLM-judge clarity as the primary clarity control | Modified: Flesch stays in the primary; the LLM rating is A2c. | The primary must not depend on a budget-capped job or on a second unvalidated judge; no human clarity labels exist to validate it. |
| Flesch-Kincaid grade as covariate | Modified: Flesch Reading Ease, which uses the same two ratios. | One formula, already defined in this file. |
| Pre-register clarity-as-mediator handling | Adopted as A2h. | See A2h. |
| Two crux-list orders and repeats | Modified: single deterministic pass is the instrument; one order-swapped pass on gate items as a diagnostic (§4). | Reproducibility; cost. |
| Vagueness control | Modified: A2f sensitivity, not primary. | See A2f. |

## 8. Tier 2 (pre-specified secondary; same data)

Each experiment has one test that enters the multiple-comparison family (§9).

**[R1]** N1, A4 and N4 are identified by the same informative rounds as A2 (for A4, scorer 2's
own). Each reports its own count of informative rounds and launches. Their wording follows the
§7.1 tier of the scorer they use: below INFORMATIVE, no directional claim is made from them
either. N1 also reports the number of rounds with `d_r ≠ 0` and, descriptively, the mean `d_r`
over those rounds; the family test stays the mean over all rounds.

**[R2]** Wherever a cell in this section says "launch-cluster bootstrap", "launch bootstrap",
"same bootstrap" or "percentile interval", the interval and p-value are those of the §7 "[R2]
Interval method of record" row (wild cluster bootstrap-t; B and seeds as written in the cell).
Only A2's coverage was checked. N1 is never called a replication of A2
(`analysis\eval\METHODS_EVAL.md` N1c). **[R3]** The R2 sentence that N1 has no length or
clarity control is superseded: N1's family test is now adjusted for both (see "N1 adjustment
[R3]" after the table).

**[R4]** Every family test in this section (N1, A4, A3, N3, N4) is computed on the confirmatory
set of §2: development launches are excluded. The "≥ 30 launches" conditions for A3 and N3 are
counted among non-development launches. Each test may also be printed with the development
launches included, as a sensitivity figure beside it, labelled as such, outside the Holm family.
(D31 edit 6 / D34 item 8.)

| Exp | Definition | Family test | Why |
|---|---|---|---|
| N1 | Winner of a round = the statement with the lowest mean mid-rank over the round's eligible raters. Rounds with a tie for winner are excluded and counted. `d_r = E(winner) − mean E of all 4 candidates in the round`. | **[R3] Family test = the length- and clarity-adjusted winner gap `alpha` defined in "N1 adjustment [R3]" below** (wild cluster bootstrap-t, launch clusters, B = 10,000, seed 20261120, 95% interval, two-sided). The unadjusted mean of `d_r` over rounds (the test written here before R3) is still computed and printed beside it as N1u, with the same interval method, but is no longer the family test. | Mean-rank winner is deterministic and needs no tie-break RNG. "Average candidate" is read literally as all 4; the gap to the other 3 is `d_r·4/3`. Sensitivity: Schulze winner from the repo's `schulze_method.py`. |
| A4 **[R4]** | Second scorer = `granite-4.2-30b` (fallback `granite-4.2-8B`), §4 and §6.9; it replaces Gemma-4-12B. **What runs now (D36):** the validity bar of §6.9 (V1, V2, V3) on the 50 packet items and the seeded 1,000-statement sample: scorer 2's balanced accuracy against the human labels, and its agreement with scorer 1 (binarised kappa, Spearman), with intervals. These are descriptive; none is a family test. **What is deferred:** A2 refitted with scorer 2's own `E` (own cruxes, own labels) on the confirmatory set needs scorer 2 to score that whole set, which needs a further experiment-council vote. | `beta_E` under scorer 2, same bootstrap (seed 20261121), **enters the Holm family only if** (i) the council vote for the full scorer-2 scoring run is recorded in decisions.md before `GATE1_RESULT.json` first permits a real-rank run (PASS or PROVISIONAL_PASS), and (ii) scorer 2 meets V1 and V2 of §6.9. If the vote comes later, or V2 is not met, the refit may still be run and is reported as exploratory, outside the family, with the date of the vote. If it is never run, A4 is reported as the §6.9 agreement figures only, and the paper says the second scorer was not used to re-estimate `beta_E`. A refit on the 250-round sample alone is not a family test (too few informative rounds) and, if shown, is exploratory. | A second instrument from a family that wrote none of the N2 text (D31 edit 3). The membership rule is fixed here so that the decision to pay for the refit cannot follow a look at the scorer-1 result. |
| A3 | Runs only if ≥ 30 launches **(J)** have a round that otherwise passes §2 but contains at least one `HUMAN_MEDIATOR` and at least one `MODEL_MEDIATOR` candidate. Counted by `build_analysis_set.py` before any score exists. | Mean within-round difference `E(AI-written) − E(human-written)`; launch bootstrap, seed 20261122. | "If data allows" is decided by a count fixed in advance, not by the result. The A2 slope inside these rounds is reported descriptively. |
| N3 | For eligible rounds that also have `iteration_index == 1` candidates: cruxes stay those derived from the opinions; iteration-1 candidates are labelled with the same prompt. Runs only if ≥ 30 launches **(J)** qualify. | Mean within-round difference `mean E(iteration 1) − mean E(iteration 0)`; launch bootstrap, seed 20261123. | Disagreement is defined from opinions, so the cruxes must not change between drafts. |
| N4 | Per-rater ranks only. A rater's side is taken from the first-listed crux: minority = the side with fewer members. Rounds with equal sides, and raters on neither side, are excluded and counted. Model = A2 plus `E × minority`. | The interaction coefficient; launch bootstrap, seed 20261124. | Uses the extractor's member lists, which come from opinions only. Skipped under the per-group fallback (BRIEF §14). |

### N1 adjustment **[R3]** (length and clarity control, same definitions as A2)

Reason: N1 as first written had no control. On a synthetic design with zero erasure effect, a
length effect on rank and corr(`E`, length) = 0.3, its interval excluded 0 in 53 of 200 runs
(26.5%; nominal 5%), while controlled A2 covered 0 in 190 of 200
(`analysis\eval\METHODS_EVAL.md` N1a, `analysis\eval\cov_hard_len_new.json`; synthetic data only).

| Item | Rule | Why |
|---|---|---|
| Round set | Unchanged: rounds with no missing `E` and a unique mean-mid-rank winner. | Same N1 population as before. |
| Per-round quantities | `d_r = E(winner) − mean E of the 4 candidates` (unchanged). `dLen_r = zLen(winner) − mean zLen of the 4 candidates`. `dClar_r = zClar(winner) − mean zClar of the 4 candidates`. `zLen` and `zClar` are exactly A2's controls (§7): log word count with words = `[A-Za-z0-9']+`, and Flesch Reading Ease, each z-scored over all statements in the analysis set with the same constants A2 uses. | The winner-minus-round-mean form is the round-level counterpart of A2's within-round demeaning, applied to the same two covariates. |
| Model | OLS across rounds, one row per round, equal weight, with intercept: `d_r = alpha + g_L·dLen_r + g_C·dClar_r + u_r`. | Linear, as in A2. `alpha` does not depend on the scale of the covariates, so raw or z-scored differences give the same `alpha`; z-scored is the form of record. |
| Estimand and family test | `alpha`: the expected gap in `E` between the winner and its round's average candidate, for a winner whose length and clarity equal the round average. Two-sided; interval and p-value by the §7 "[R2] Interval method of record" row, clusters = `launch_id`, B = 10,000, seed 20261120. `alpha > 0`: winners hide more than the average candidate of the same length and clarity. This `alpha` is what enters the Holm family (§9). | A winner chosen for being longer or easier to read no longer counts as a winner chosen for hiding. |
| Printed beside it, always | N1u = unadjusted mean of `d_r` (the brief's literal "winner vs. average candidate"); N1h = the model with `dLen_r` only (clarity may be a mediator, as in A2h); `g_L`, `g_C`; the means of `dLen_r` and `dClar_r`; the number of rounds with `d_r ≠ 0`. None of these is a family test. If `alpha`, N1u and N1h differ in sign or in whether the interval excludes 0, the results text must say so. | The brief's unadjusted comparison stays visible; the reader sees what the adjustment did. |
| Check before real ranks **(J)** | The adjusted test is run on the same synthetic length-confound design as the evaluator's (zero erasure effect, length effect on rank, corr(`E`, length) = 0.3), ≥ 200 datasets, and the share of intervals that cover 0 is logged in RUNS.md. If that share is below 93%, or the check has not been run when real ranks are first read, N1 is taken out of the Holm family and reported as descriptive only, with that reason. No other repair is tried. | The adjustment is specified here but its code did not exist when this was written. The 93% line is the one §7 already uses. |
| Sensitivity | Schulze winner (as before), with the same adjustment. | Unchanged. |
| Limits to state | The adjustment is linear in length and clarity. `d_r` is 0 in every round where `E` does not vary, so `alpha` is identified by the informative rounds only (§7.1) and follows the tier wording. N1 uses the same ranks and `E` as A2 and is not a replication of it. | METHODS_EVAL N1a, N1c. |
| Per-group fallback (§11) | Same model on the group-level winner. | No separate rule needed. |

## 9. Multiple comparisons

| Item | Rule | Why |
|---|---|---|
| A2 | Tested alone at two-sided alpha = 0.05, no correction. | It is the single confirmatory test. |
| Tier 2 family | The family tests of N1, A4, A3, N3, N4 that actually run (at most 5). Holm step-down at family-wise alpha = 0.05. Raw and Holm-adjusted p-values are both reported; intervals stay unadjusted 95% and are marked as such. | Holm controls family-wise error with no independence assumption. Family size depends only on the data-availability counts in §8, never on results. **[R4]** All family tests are computed on the confirmatory set (§2). A4 is in the family only under the two dated conditions of its §8 row; N1 only under its [R3] guard. Both conditions are settled before real ranks are read. |
| Sensitivity models A2b-A2h | Not tested for significance on their own; reported as estimates with intervals. | They qualify A2; they are not extra chances to find an effect. |
| Everything else | Exploratory; reported with intervals, no significance language. | BRIEF §3.10. |

## 10. Confirmatory, secondary, exploratory

| Label | What |
|---|---|
| Confirmatory | Gate 1 (§6). A2 `beta_E`, scorer 1 (§7). **[R4]** Both on the confirmatory set only: no development launch enters gate 1, the N2 check, the headline rate, A2, the tier, or any Tier-2 family test (§2). |
| **[R4]** Development-launch exclusion, confirmed in writing | The 150 development launches, which include the 40 development-probe rounds (29 to 35 evaluable) and the pilot's rounds, are excluded from every confirmatory and family test in this file. Rules that guarantee it: §2 "Analysis set" (the confirmatory set), §6.1 "Population" and §6.1a "Eligible N2 rounds" (gate items), §6.7 (headline sample), §7 "Data" and §7.1 "Counts" (A2 and its tier), §8 opening note (Tier 2), §6.6 "Scope of the label" (N2). Before R4 only the gate sample was guaranteed; A2's primary fit and the Tier-2 tests included the development launches. That is corrected here. Where development launches still appear: A2d and the labelled side figures, scorer prompt try-outs, the scorer-2 and LLM-annotator format smokes, and the N2 version "including development launches". | D31 edit 6 / D34 item 8 (human); orchestrator's instruction to resolve the §2 conflict in favour of the human edit. |
| **[R4]** Pre-specified headline (descriptive) | `H`, the human-labelled hide-rate of §6.7, with its Wilson interval. No significance test. |
| **[R4]** Supplementary, no rule | The LLM annotator's labels and every agreement figure built on them (§6.8); the author's self-consistency kappa in the two-human design; a volunteer file that arrives after gate time (§6.0). |
| Pre-specified secondary | A2b-A2i; N1, A4, A3, N3, N4 with the Holm family. Never described as confirming the main claim. |
| **[R1]** Pre-specified descriptive | The prevalence quantities of §7.3 and `D1h`, `BA_crux`, `BA_sh` of §6.4a. No significance test. |
| **[R1]** N2 status | Unchanged: exploratory with respect to this file, pre-specified in its own hashed spec (`analysis\N2_ANALYSIS_SPEC.md`; hash and any amendment logged in decisions.md before scoring). §7.3 decides only where it is placed in the paper. This file does not alter the N2 spec. |
| **[R4]** N2 after the human edits (D31 edits 2, 3, 5; D34 items 3, 5 to 7; D36) | N2 stays exploratory with respect to the rank question and is never confirmatory. What R4 fixes from outside the spec: (1) **Generators:** five, from five families: Qwen3.8-27B, Gemma-4-12B, Ministral-3-14B, phi-4, Llama-3.1-8B-Instruct; the three added ones use the same 250 rounds, the same 5 cells, k = 1, the same prompts byte for byte and the same decoding; the 2,500 statements already generated are kept, not regenerated. (2) **Every N2 result is reported split by generator.** A figure pooled over generators may appear only beside the five per-generator figures, is descriptive, and is never the only support for a sentence. (3) **Length stays a control** in every N2 model (log word count, centred within generator; Amendment 1 extended to all five), with the unadjusted figure beside it. (4) **Scorers:** scorer 1 is the read of record for all five generators; the Qwen-written column is marked "same-family scored" wherever it appears; scorer 2 (Granite) is a robustness read. (5) **Label:** `N2_VALIDATED` or `EXPLORATORY` as decided by §6.6, with the scope stated there. (6) **Multiplicity:** as in the spec of record (the 10-test Holm family for the first two generators unchanged, and a second 15-test Holm family for the three added ones; pooled estimates untested). (7) **Spec of record [R5]:** `analysis\N2_ANALYSIS_SPEC.md` with Amendments 1 to 5, SHA-256 `afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0` (D50a; before R5 this cell carried the stale Amendment-2 hash `126787ad…2c0dc60b`, D49d item 3); (5) under R5 reads: N2 is EXPLORATORY in every gate status and `N2_VALIDATED` is unavailable (§6.R5.7); (8) under R5 reads: no N2 statement other than the 25 R5 packet items is scored before an R5 gate status is recorded (§6.R5.6); a later amendment needs a council vote and a new hash in decisions.md before any N2 scoring. (8) No N2 statement other than the 12 packet items is scored, and no N2 analysis is run, before gate 1 is recorded. Where an older row of this file says "two models", "cross-scored cells are the primary read" or "scorer 2 = Gemma", this row and the spec of record govern. |
| Exploratory | N2, N5, N6, B, F as far as they bear on this paper. N2 statements are scored only after gate 1 is recorded as PASS (**[R1]** which scorer scores which cell is set by the hashed N2 spec, which makes cross-scored cells the primary read; the earlier words "only with scorer 1" here contradicted that spec), so that N2 adds a human-validated scorer and a system-by-user prompt grid to what Mahajan et al. (arXiv:2611.05135) already report. Also exploratory: an embedding position-axis score; any analysis with `ratings.agreement` or `ratings.quality` as the outcome; reliability-corrected coefficients; iteration-1 replications of A2; rounds excluded by the bot filter; a 70B or closed-model third scorer; the pilot's lexical and embedding measures; anything not written here. |
| Pre-brief pilot | Anything the pilot computed on real rankings before this file existed is labelled "pre-gate exploratory, executed before frozen rules existed" (decisions.md D1) and is not evidence for any claim. |

## 11. Per-group fallback (BRIEF §14)

| Item | Rule | Why |
|---|---|---|
| Decision rule for experiment 0 | Ranks are **per rater** if (i) `rankings.metadata.participant_id` equals the row's own participant in ≥ 99% of human rank rows **(J)** and (ii) among round-iterations with ≥ 2 human raters, fewer than 50% **(J)** have identical rank vectors for all raters. Otherwise **per group**. | A written, checkable rule. The pilot's `exp0_rank_unit.json` reports 100% for (i) and 234 of 7,871 for (ii). The baseline's independent check (decisions.md D6, `analysis\EXP0_rank_unit.md`) reports 100% and 8,131 of 8,268 multi-rater groups with differing rankings: **per rater; fallback not triggered.** The rule stays here in case a later check contradicts that. |
| If per group | Log in decisions.md. A2 uses one rank vector per round: `y_rs = a_r + beta_E·E_s + beta_L·zLen_s + beta_C·zClar_s + e_rs`, round fixed effect, same bootstrap. N1 uses the group's top-ranked statement as winner. A2b uses the mean similarity to all members' opinions. N4 is skipped. | BRIEF §14. |
| Reporting | The paper states that the outcome is a group aggregate, that the data points are fewer, and that individual preference cannot be separated from the aggregation rule. More effort moves to F and B. | BRIEF §14: "stated as a limitation". |

## 12. "Not yet measurable" write-up

**[R5]** The triggers below that refer to kappa, pass 2, the volunteer, adjudication or `PROVISIONAL` are
superseded (kept, not in force). Under R5: gate FAIL = step 2 FAIL (§6.R5.6) → this section's "not yet
measurable" version and its "After a FAIL" row apply; EXPLORATORY_UNVALIDATED → §6.R5.5; NOT_EVALUATED → the
"Labels incomplete or absent at handover" row; the interpretability-floor and §7.1-tier rows apply unchanged.

| Trigger | Consequence | Why |
|---|---|---|
| **[R4]** Agreement step of §6.2 fails or is undefined (single-labeler design: self-consistency kappa < 0.60; two-human design: inter-rater kappa < 0.40) | Gate 1 = FAIL. The paper is the "not yet measurable" version. Wording per §6.2 "Power of this step": "self-consistency was not established at n = 20" or "agreement between the two annotators was not established", with the kappa interval, AC1 and the simulated pass rates of §6.1b. The human-labelled rate `H` is printed with that sentence and is not the paper's headline. Provisional outputs are re-stamped `EXPLORATORY_UNVALIDATED` (§6.5). (Before R4: "Kappa < 0.60 or undefined", two labelers, 20 shared items.) | BRIEF §4 as amended by D34 and D37. |
| **[R4]** Single-labeler design, pass 2 absent or not meeting the one-hour rule at handover | Gate 1 stays PROVISIONAL_PASS (or INCOMPLETE). Every result is reported with the PROVISIONAL stamp and the sentence "the annotator's self-consistency has not yet been checked". Not a pass, not a fail. | D34 process; unfinished work reported honestly (BRIEF §0). |
| **[R4]** N2 check NOT PASSED while gate 1 is PASS | Gate 1 is reported as passed for original statements. N2 is `EXPLORATORY` (§6.6) and cannot lead; the paper says the scorer was not validated on newly generated text and gives the simulated pass rates of §6.6, so that the outcome is not read as evidence against the scorer. | D31 edit 2 / D34 item 3. |
| Balanced-accuracy lower bound ≤ 0.5 | Gate 1 = FAIL. The paper is the "not yet measurable" version: the scorer is not shown to beat chance. | BRIEF §4. |
| After a FAIL | No definition, prompt, threshold, sample or label option is changed and no re-labelling is requested. A2 and Tier 2 may be run on real ranks only as "exploratory, unvalidated instrument", in an appendix, never in the abstract or as a finding. The write-up reports kappa, the confusion table, the unsure items and what a better instrument would need. | "Never change definitions." Hard rule 10: every run is reported. |
| Labels incomplete or absent at handover | Gate 1 = NOT EVALUATED. This is reported as such and is not a fail. No real-rank analysis is run. | Hard rules 1 and 3; unfinished work reported honestly. |
| Gate passes but the §7 interpretability floor fires | Gate 1 is reported as passed; the rank question is reported as not measurable at this sample. | The instrument can be valid and still not vary within rounds. |
| **[R1]** Gate passes, A2 tier is LOW-POWER or NOT MEASURABLE (§7.1) | The paper follows §7.3: prevalence and N2 lead, A2 is reported with its tier wording. This is a "rank question not yet measurable in these data" paper with a validated instrument, and is written as such, not as a weakened positive. | Expected in advance (§1). The brief's reviewers reward a clear statement of what a method does not show. |
| **[R1]** Gate passes, §6.4a wording rule fires | Gate 1 is reported as passed with the §6.4a sentence. No directional rank claim in title or abstract, in any tier. | The pass does not validate the contrast A2 uses. |

## 13. Differences from the pilot PREREG.md, and why

| Pilot | This file | Why |
|---|---|---|
| Retention counts NAMED or RESOLVED as retained | Only `VISIBLE` counts as shown; one-sided statements count as hidden. The pilot definition is kept as A2e. | The brief's construct is hiding disagreement. Chosen without sight of any result. |
| Pairwise conditional logit | Linear model on mid-ranks with rater-round fixed effects | BRIEF §5: "rank vs. erasure score"; ties are kept. |
| Own-opinion similarity in the primary model | In A2b, with a binding wording rule | BRIEF §5 fixes A2's controls as length and clarity. |
| Validation by Spearman rho ≥ 0.5 on a reference sample; ICC and power kills | Gate 1 as in BRIEF §4. Inter-scorer agreement is reported under A4, no kill. | The brief replaced the gate. |
| Judges qwen2.5:7b and llama3.1:8b on Ollama | Qwen3.8-27B and Gemma-4-12B on Modal | Chair ruling §0.1: the instrument must be current. |
| All 4 statements labelled in one call | One statement per call | Avoids contrast effects. |
| One round per launch, 150 launches | All eligible rounds, launch-clustered | Uses all the data; the cluster bootstrap handles dependence. |

## 14. Careful-option log (choices where the brief was unclear)

1. "95% lower bound" read as the 2.5th percentile, not the 5th.
2. `UNSURE` kept as a category in kappa instead of dropped.
3. Parse failures on gate items count against the scorer.
4. Gate sample excludes the development launches and is one item per launch.
5. No stratification on AI scores, at the cost of possible class imbalance.
6. `ADJ.csv` is a human-written third file; the pipeline never writes it.
7. After a FAIL, real-rank analysis is appendix-only and labelled unvalidated.
8. No equivalence claim on a null.
9. The gate is recorded by the planning room only after an independent re-derivation, and only
   with the computed status.
10. Label tokens are an exact list of four; synonyms are rejected, not mapped.

**[R4] additions** (items 2, 4, 6 and 9 above are read with §6 as amended: item 6's `ADJ.csv`
exists only in the two-human design).

11. The 38 originals are the first 38 of the sample already drawn, not a new draw.
12. The 12 N2 items come from outside the development launches and outside the 60 sampled launches.
13. The N2 check uses an exact test, and its low power is stated before the data.
14. `N2_VALIDATED` attaches only to scorer-1 estimates computed without development-launch rounds.
15. A pass-2 file that misses the one-hour rule is not scored, instead of being scored and failed.
16. An incomplete volunteer file at gate time keeps the two-human design; a late one changes nothing.
17. LLM-annotator labels are kept outside `labels\` and are hidden from the humans until their files are in.
18. Agreement between the two scorers changes the wording of results, never whether scorer 2 is kept.
19. The A4 refit counts as a family test only if it is approved before real ranks can be read.
20. Gwet's AC1 is kept beside every kappa, with no rule.

---

## Appendix A. Prompts of record

### E1 (crux extraction; inputs: question, opinions)

```
A small group of people each wrote an opinion on the question below.

Question: {question}

Opinions:
{numbered_opinions}

Task: list the CRUXES of this group: specific points on which members' opinions genuinely
DISAGREE (one member asserts or prioritises something that another member denies, rejects,
or weighs very differently). Do not list points everyone agrees on. Do not list differences
that are only wording, emphasis or examples. Do not invent disagreements. A crux needs
members who EXPLICITLY take opposing positions in their own opinions. List a member under a
side only if that member's own opinion states or clearly implies that position. A member who
did not address the point belongs to neither side: silence is not opposition, so never infer
a position from silence. A point raised by one member that no other member contradicts or
weighs very differently is not a crux. List between 0 and
4 cruxes, most important first. If the members basically agree, return an empty list.

Return JSON only:
{"cruxes": [{"issue": "<one short sentence naming the disputed point>",
  "side_a": "<position A>", "members_a": [<opinion numbers>],
  "side_b": "<position B>", "members_b": [<opinion numbers>]}]}
```

### L1 (labelling; inputs: question, cruxes from E1, one statement)

```
A small group of people each wrote an opinion on the question below. Their opinions disagree
on the points listed. Then one statement was written to speak for the whole group.

Question: {question}

Points of disagreement:
{numbered_cruxes_as: "<n>. <issue> (Side A: <side_a> | Side B: <side_b>)"}

Group statement:
"""{statement}"""

For EACH point, decide how the statement treats it. Use exactly one label per point:
- VISIBLE: a reader of the statement alone would learn that people in the group hold differing
  views on this specific point (it gives both sides, or says that some members, a minority, or
  not everyone thinks differently on this point).
- SIDED: the statement presents one side of this point as the group's view and gives no sign
  that anyone in the group thinks otherwise.
- BLENDED: the statement touches the topic only in vague or general terms that do not reveal
  a disagreement (for example "a balance is needed", "many factors matter").
- OMITTED: the statement does not address this point at all.

Judge only the statement's text. A general phrase such as "there are many views" counts as
VISIBLE only if it is tied to this specific point.

Return JSON only: {"labels": ["VISIBLE|SIDED|BLENDED|OMITTED", ...]}
with one label per point, in the order given.
```

### C1 (clarity, used only in A2c; inputs: question, one statement)

```
Question put to a group: {question}

Statement:
"""{statement}"""

Rate how clear this statement is to a general adult reader. Ignore whether you agree with it
and ignore how long it is. 1 = very hard to follow, 2 = hard, 3 = acceptable, 4 = clear,
5 = very clear.

Return JSON only: {"clarity": <integer 1-5>}
```

---

## Known weaknesses (the five weakest choices in this file)

1. **Counting one-sided statements as "hiding" (§4).** This is a construct choice, made blind,
   that departs from the pilot. It may make `E` close to 1 for most machine-written consensus
   statements, leaving little within-round variation. A2e and the §7 floor expose this; they do
   not fix it. **[R1]** Measured on the development probe before any label: `E` varied within
   the round in 3 of 34 rounds. The definition was kept; §7.1 to §7.3 fix in advance what the
   paper says if this holds in the full set. The thresholds in §7.1 (100 launches, 0.10) are
   judgement calls, and the blind MDE is optimistic.
2. **Gate sample of 60, unstratified, 20 shared (§6).** If one class is rare, the lower bound on
   balanced accuracy can stay at or below 0.5 even for a good scorer, and a kappa from 20 items
   is very imprecise. The gate can therefore fail for lack of data, not lack of validity. The
   sizes are the brief's; stratifying would have biased sensitivity and specificity.
3. **Humans label the whole statement; the AI score is built from AI-extracted cruxes (§3, §5).**
   The gate tests the instrument end to end but cannot say whether a failure comes from crux
   extraction or from labelling. The "half or more" rule is also a coarse match to a continuous
   score, and with a single crux both reduce to a yes/no.
4. **Controls (§7).** Flesch Reading Ease measures sentence and word length, not clarity of
   argument. The primary model omits own-opinion similarity because the brief fixes the controls,
   so the main coefficient is exposed to the self-interest confound; only A2b and its wording
   rule guard against it.
5. **Uncertainty that is not carried through.** Unique gate items have one labeler each, half of
   them the hypothesis-aware author. Scorer error is not propagated into the A2 interval, which
   biases `beta_E` toward 0. A linear model treats rank gaps as equal. The bot filter removes
   more than half of the 4,492 iteration-0 rounds, so results describe the all-human,
   four-candidate subset only.

6. **[R4] One hypothesis-aware annotator (§5, §6.0), unless the volunteer file is present at gate
   time.** In the single-labeler design every human label comes from the person who knows the
   hypothesis; nobody blind to it checks them. Self-consistency on 20 repeats after one hour shows
   that the annotator repeats their own labels, which memory alone can produce, and says nothing
   about bias. Items 2 and 5 above describe the older two-labeler design; read them with n = 38
   gate items and one annotator. The LLM annotator is a model, not a person, and its agreement
   with the author cannot stand in for a blind human. The brief asked the paper to stress blind
   labelling (BRIEF §10); in this design it cannot, and the header's wording rule says so.
7. **[R4] Results can be seen before the gate is final (§6.5).** The PROVISIONAL state lets
   real-rank results exist before the second pass is made by the person who knows the hypothesis.
   The second pass cannot change an estimate, but it decides whether the gate is final.
8. **[R4] Twelve items for N2 (§6.6).** The N2 check cannot tell an adequate scorer from a good one,
   says nothing per generator or per cell, and includes Qwen text scored by Qwen. A pass is weak
   evidence; a miss is not evidence against the scorer.
9. **[R4] The second scorer does not re-estimate the main result unless a later vote pays for it
   (§8).** As it stands A4 shows whether two scorers agree with each other and with the labels, not
   whether `beta_E` survives a change of scorer.
10. **[R4] The agreement cut-off was changed twice before any label existed** (0.60 inter-rater on
    20, then 0.40 inter-rater on 30, then 0.60 self-consistency on 20, with 0.40 inter-rater on 50
    if a volunteer labels). Each change was the human's and was made blind to labels, but a reader
    is entitled to know the sequence; the Replan log gives it.

**[R5]** Items 2, 3, 6, 7, 8 and 10 above describe superseded R4 designs and are kept as history. The five
weakest choices of R5:

11. **[R5] Step 2 validates presence, not hiding.** The only clean participant signal says whether the group
    disagrees on the question's one axis; it says nothing about statements and mismatches the crux construct
    (cruxes can lie within one side), which depresses specificity. Hence the scoped wording of §6.R5.6.
12. **[R5] The 0.60 point bar and the usability minimums (200/100, 50/25, 1%) are judgement calls.** The
    point bar decides PASS vs WEAK and was not derived; P(PASS) is about one half at a true BA2 of 0.60.
13. **[R5] Step 3 is small, single, hypothesis-aware and unit-mismatched**, with no second pass and a 30-minute
    time-out (D51) that may leave it NOT DONE; an adequate scorer is more likely INCONCLUSIVE or UNUSABLE than
    SUPPORTED at n ≤ 15 (§6.R5.3).
14. **[R5] The panel is three models that each failed the scorer's format bar on another task**, judged on a
    new bar; LLM errors are correlated, and P1 shares its inputs with the author. gpt-oss is excluded to avoid
    self-evaluation.
15. **[R5] The status logic is a judgement:** step-2 FAIL dominates a step-3 SUPPORTED; step 3 can never fail
    the gate but CONTRADICTED downgrades every `E`-based result; usable-but-unsupportive outcomes go to
    EXPLORATORY (stricter than D49 item 5); N2 loses any path to `N2_VALIDATED`; and the D51 rule that a file
    incomplete at `T_cut` counts as not submitted is the orchestrator's reading.

---

## Replan log

### R1 — 2026-11-15, decisions.md D21 (planning room; no label file existed; file not frozen)

**Trigger.** Development probe, scorer 1, opinions and statements only: `E` varied within the
round in 3 of 34 evaluable rounds (13 of 34 under A2e); 186 of 216 crux labels were `SIDED`
(`analysis\council\SCORER_vote_methodologist.md`). The A2 coefficient may have very little
identifying variation. The E1 v2 fix (silence is not opposition) changes how many cruxes a round
has; it is not expected to add within-round variation.

**Blindness.** Read for this replan: BRIEF, this file, EXPERIMENTS, PLAN, decisions D17-D20, the
three scorer-council votes, `N2_ANALYSIS_SPEC.md`, `ALIGNMENT.md`, the E1 prompt file. Not opened:
any ranking, rating or label, any output of a rank analysis on real data, the score files
themselves. Every threshold below was set without knowing `K_inf` for the full set.

| # | Section | Change | Kind |
|---|---|---|---|
| 1 | §1 | A2 `beta_E` stays the single confirmatory test; claims depend on the §7.1 tier. Expected outcome (LOW-POWER or NOT MEASURABLE) stated in advance. | Added |
| 2 | §3, §4, App. A | E1 v2 side-membership rule and empty-side parse rule recorded; gate-sample disclosure; v1 gate accuracy to be printed. (Prompt text and the §4 row were edited by the scorer runner under D18; this replan added the disclosure and the v1 comparison.) | Added |
| 3 | §6.3 | `ADJ.csv` column unified to `adj_label` (was `final_label` here, `adj_label` in §5). | Corrected |
| 4 | §6.4a | Gate-1 additions per D18: `BA_crux`, `BA_sh`, zero-crux share, binding wording rule, human-labelled prevalence `D1h`, scorer-v1 comparison; supplement not added. Pass rule unchanged. | Added |
| 5 | §7 | Interval method: selection rule after the failed coverage check (D19) written in; method name pending the stats coder's record. | Added |
| 6 | §7.1 | Informativeness tiers (INFORMATIVE: `K_inf ≥ 100` and `MDE80 ≤ 0.10`; LOW-POWER: `K_inf ≥ 50`; NOT MEASURABLE: `K_inf < 50`), blind MDE, `A2_TIER.json` written before unblinding, one-way downgrade. The old floor of 50 is kept as the lowest tier. | Added |
| 7 | §7.2 | Rulings on the alternatives: informative-only (A2i sensitivity), A2e (not promoted), graded score (rejected), N1 (not promoted), between-round (rejected), N2 as confirmatory (rejected). | Added |
| 8 | §7.3 | Paper lead by state; prevalence quantities pre-specified; N2 leads with prevalence when A2 is not INFORMATIVE. | Added |
| 9 | §7 sensitivity | A2e wording rule; new A2i. | Added |
| 10 | §8 | N1, A4, N4 inherit the tier wording; N1 reports rounds with `d_r ≠ 0`. | Added |
| 11 | §10, §12 | Descriptive class; N2 status and scorer wording aligned with its spec; two new §12 rows. | Added / corrected |

**Not changed.** BRIEF §4 and everything that implements it: the crux definition, the four labels,
hidden = `SIDED`, `BLENDED` or `OMITTED`, `E`, the 0.5 threshold, the 60-item sample of record, the
kappa cut-off, the gate pass rule. The A2 model, controls, estimand and test. The Tier-2 family.

**Open at the time of writing.** (a) Interval method name (§7) — closed by R2. (b) `scorer.py` did not yet
contain the empty-side parse rule of §3. (c) `a2_informativeness.py` and the `A2_TIER.json` guard
are to be written. (d) `gate1.py` must compute §6.4a and accept only `adj_label`.
(b), (c) and (d) were reported done in decisions.md D22 (scorer runner) and D24.

### R2 — 2026-11-16, decisions.md D25 (planning room; `labels\` empty and file not read-only, checked immediately before the edit)

**Trigger.** decisions.md D24 and `analysis\ALIGNMENT.md` recorded the interval method chosen by
the R1 selection rule. D24 asked for the p-value formula to be rewritten before freeze.

**Blindness.** The selection run used within-rater shuffled ranks and a dummy `E`. Read for R2:
ALIGNMENT.md, decisions D21-D24, `analysis\eval\METHODS_EVAL.md`, `common.py` (interval code).
No ranking-versus-erasure output, rating or label was opened.

| # | Section | Change | Kind |
|---|---|---|---|
| 1 | §7 Uncertainty | Percentile interval superseded by the method of record; clusters, B = 10,000, seed and z-scoring unchanged. | Changed |
| 2 | §7 new row | Interval method of record = wild cluster bootstrap-t (Rademacher, launch clusters, unrestricted residuals, CR1 SE), equal-tailed bootstrap-t interval; coverage 386/400 at B = 2,000; applies to every launch-clustered interval; limitation that only A2's coverage was checked. | Added |
| 3 | §7 R1 row | "Not yet recorded" placeholder replaced by a pointer to the new row. | Filled |
| 4 | §7 Primary estimand and test | p-value rewritten for bootstrap-t: two-sided symmetric `(#{|t*| ≥ |t_obs|} + 1) / (B + 1)`. The interval still decides "detected"; disagreement between interval and p is printed and called borderline. | Changed |
| 5 | §8 | Note that every "launch bootstrap" or "percentile" cell uses the method of record; N1 printed beside its length and clarity differences and never called a replication. | Added |

**Not changed.** Estimands, models, tests, seeds, B for the analyses of record, the §7.1 tier
thresholds, the Holm family, gate 1 and all of its item-level percentile bootstraps (§6.2, §6.4,
§6.4a), every definition under BRIEF §4.

**Stated plainly.** B = 2,000 is the setting of the coverage check. The analyses of record keep
B = 10,000, which is also the code default (`common.DEFAULTS`). The interval is equal-tailed and
the p-value symmetric because that is what the checked code computes; the interval is the one
whose coverage was measured.

**METHODS_EVAL.md placeholders.** That file still contains `__COVERAGE__`, `__N1LEN__` and
`__N1TIES__`. They are missing evidence inside the evaluator's own report, not blanks in this
file, and the planning room does not write an evaluator's numbers. What they bear on here:
coverage is now settled by row 2 from the stats coder's logged run; the N1 length point is met
by the wording in row 5. Not adopted, for lack of the evaluator's numbers and of tested code: a
residualised N1, a spline length control (A5), a tied-winner N1 variant (N1b), and the G2
sentence on kappa power at n = 20. (The N1 length point and G2 were taken up in R3, once the
evaluator's numbers were in its report.)

### R3 — 2026-11-16, decisions.md D29 (planning room; `labels\` empty, file not read-only, no `FREEZE.json`, checked immediately before the edit)

**Trigger.** decisions.md D28: the methodologist's evaluation, with its evidence now filled in
(`analysis\eval\METHODS_EVAL.md` N1a and G2).

**Blindness.** Both findings come from synthetic data (`cov_hard_len_new.json`, `gate1_sim.json`).
Read for R3: METHODS_EVAL.md, D26-D28, `n1_winner_vs_mean.py`. No ranking-versus-erasure output,
rating or label was opened.

| # | Section | Change | Kind |
|---|---|---|---|
| 1 | §8 N1 row and new "N1 adjustment" table | N1's family test is now `alpha`, the intercept of `d_r = alpha + g_L·dLen_r + g_C·dClar_r + u_r`, with `dLen_r`, `dClar_r` the winner-minus-round-mean differences in A2's own `zLen` and `zClar`. Same seed, B, clusters and interval method. Unadjusted N1u and length-only N1h printed beside it. | Changed |
| 2 | §8 same table | Check on the synthetic length-confound design before real ranks; if coverage is below 93% or the check is missing, N1 leaves the Holm family and is descriptive only. | Added |
| 3 | §6.2 new row, §12 first row | Kappa-step power stated in advance: two 90%-accurate labelers pass kappa ≥ 0.60 in about 34% of samples of 20 (95%-accurate: about 67%). Cut-off, n and consequence unchanged; FAIL wording fixed. | Added |
| 4 | §8 R2 note | Sentence "N1 has no length or clarity control" superseded. | Corrected |

**Not changed.** BRIEF §4: n = 20 shared items, kappa cut-off 0.60, the pass rule, FAIL → "not yet
measurable". The definition of the winner and of `d_r`. The Holm family's membership rule (§9),
except the conditional removal of N1 in row 2. A2 and everything in §7.

**Choices made here that go beyond the request, stated so they can be reversed before freeze.**
(a) The request named length; clarity is controlled as well, because A2 controls both and the
evaluator's finding names both. The length-only version is printed as N1h. (b) The unadjusted
mean stays in the paper as N1u because it is the brief's literal N1. (c) The adjustment is an
intercept regression across rounds, not a residualisation of `E` within round: with four
candidates per round a within-round residualisation would be fitted on four points.

**Open.** `n1_winner_vs_mean.py` still computes the unadjusted mean only and its docstring still
says "percentile". The stats coder was stopped (decisions.md D26); the adjusted model, N1h and
the row-2 check need an author and a fresh-context reviewer. Until then row 2's fallback applies.
(Reported done in decisions.md D30.)

### R4 — 2026-11-15 UTC, decisions.md D31, D34, D36, D37 and the planning room's own entry (planning room; consolidated)

**Written** between 2026-11-15T19:06Z and 2026-11-15T19:25Z. `labels\` had 0 files, this file was
not read-only and `gate1\FREEZE.json` did not exist at 19:06Z, 19:14Z, 19:16Z and 19:24Z (checked
each time new instructions arrived and before the last edits).

**Authority.** D31 (19:06Z), D34 (19:10Z) and D37 (19:16Z) are HUMAN-authored and binding; they
change BRIEF §3.1 and §4, which the human owns. D36 (about 19:15Z) is the experiment council's model
choice, 3 of 3 approve with conditions. Everything marked "planning room" below is a choice made to
turn those edits into exact rules; each can be reversed by the human before the first label file.

**Blindness.** Read for R4: BRIEF, decisions.md D1 to D37, this file, EXPERIMENTS, PLAN,
`analysis\eval\METHODS_EVAL.md`, `gate1_sim.py` and its JSON and log (synthetic), `labels_build\README.md`,
`analysis\N2_ANALYSIS_SPEC.md` (with Amendment 2), the first 80 and lines 190 to 250 of `gate1.py`,
names and sizes of files in `gate1\`, `analysis\eval\`, `analysis\council\`, `labels_build\`.
Not opened: any ranking, rating or label; any score file; `gate1\sample.json`, `item_key.csv`,
`A2_TIER.json`; any packet; `pilots\T3_1\features.parquet` (sealed, D33); any real-rank output.
Counts of informative launches (168 all, 144 outside development) were read in decisions.md D32
and D35; they come from scorer output and shuffled ranks.

**The six human edits of D31, what D34 / D37 did to each, and where each is written.**

| # | D31 edit (19:06Z) | Status after D34 (19:10Z) and D37 (19:16Z) | Rule now, and where | Reason |
|---|---|---|---|---|
| 1 | Kappa cut-off 0.60 → 0.40; packets 30 shared + 15 unique per labeler + duplicates; kappa with CI; Gwet's AC1 beside it. | **Replaced by D34 items 1 and 2**, then **extended by D37**. The 30 + 15 + 15 design was never built. | Single-labeler design: one hypothesis-aware labeler, 50 items (38 originals + 12 N2), 20 repeated at least one hour later, self-consistency kappa ≥ 0.60. Two-human design, if `volunteer_pass1.csv` exists at gate time: inter-rater kappa ≥ 0.40 on the 50 items. CI and AC1 in both. §5, §6.0, §6.1, §6.2, §6.1b. | Human, D31: the power check showed about a 34% pass rate for good labelers at n = 20. D34: one labeler is available. D37: a blind volunteer may become available. |
| 2 | 12 N2 statements in the packets, model and condition hidden; separate scorer check; N2 VALIDATED only if it passes, else EXPLORATORY. | **Kept** (D34 items 1 and 3; D36 fixes 3, 3, 2, 2, 2 over five generators and the pooled claim). | §6.1a (items, seeded allocation), §6.6 (statistic, pass rule: one-sided Fisher exact p ≤ 0.05 on the pooled 12, what it can and cannot show), §7.3 note (b), §10. | Human: the scorer was validated on original statements only; N2 text is different text. |
| 3 | A4 scorer from a family different from every N2 generator; all N2 results split by generator. | **Kept** (D34 item 5). Model chosen by D36. | Scorer 2 = granite-4.2-30b, fallback granite-4.2-8B; validity bar and scope in §6.9; §4 family rule; §8 A4; §10 N2 row. | Human: Gemma was both the second scorer and an N2 generator. |
| 4 | Headline = hide-rate in the human-labelled sample, with CI; scorer rate secondary. | **Kept** (D34 item 7); sample is now the 38 originals, labels of record depend on the design. | §6.7 (estimator, `UNSURE` handling and bounds, Wilson interval, what it estimates, wording); §7.3 note (a); §10. | Human: the headline should not rest on the instrument under test. |
| 5 | N2: 2 or 3 more generator families, council-approved, same prompts and rounds, length control. | **Kept** (D34 item 7). D36: Ministral-3-14B, phi-4, Llama-3.1-8B-Instruct. | §10 N2 row; spec of record with Amendment 2, SHA-256 `126787ad…c60b`; §7.3 note (c). | Human: two generators, one of them the scorer's own family, are too few to speak of "models". |
| 6 | Old pilot answers in writing whether it touched real rankings; confirm development rounds are excluded from confirmatory tests. | **Kept** (D34 item 8). Pilot answer: decisions.md D33. | §2 "Analysis set": the confirmatory set is the 721 non-development launches; A2, its tier, the Tier-2 family tests, the gate, the N2 check and the headline use it; all-launch A2 is sensitivity A2d only. §7 "Data", §7.1 "Counts", §8 note, §9, §10 confirmation row. | Human edit 6. Before R4, §2 made the all-launch A2 primary, so the exclusion was **not** guaranteed for A2 or Tier 2; the orchestrator asked that the conflict be resolved in favour of the human edit. |

**New with D34 (not in D31).**

| D34 item | Rule now, and where |
|---|---|
| 1. One labeler, the author; consultant removed | §5 "Labeler". |
| 3. Gate 1 = balanced-accuracy lower bound > 0.5 against FIRST-PASS labels | §6.3, §6.4 (gate set = 38 originals). |
| 4. Independent LLM annotator, supplementary, never called human | §6.8 (gpt-oss-120b per D36; temperature 0, seed 0; volunteer-version instructions verbatim plus one format line; kappa and AC1 with CI). |
| 9. Label "validated against a single hypothesis-aware human annotator" | Header "Validation label"; §6.7 wording. |
| Process: start on first-pass arrival; first-pass labels frozen; PROVISIONAL until self-consistency is recorded | §5 "First-pass labels are frozen on arrival"; §6.4 "Pass"; §6.5 PROVISIONAL table; §12. |
| File names `author_pass1.csv`, `author_pass2.csv`; one-hour check from time stamps and a self-reported column | §5 schema (`pass_started_utc`); §6.2 "One-hour rule". |

**New with D37.** The switch (§6.0); volunteer packet and file (§5); inter-rater statistic and cut-off
(§6.2); adjudication in the two-human design only (§6.3); two-human validation wording (header);
freeze on the first label file of any kind (first line of this file).

**New with D36.** Scorer 2 and its bar (§4, §6.9, §8 A4); LLM annotator model (§6.8); five
generators and the 12-item allocation (§6.1a, §10).

**Planning-room choices inside R4 (each reversible by the human before freeze).**

| # | Choice | Why |
|---|---|---|
| a | The 38 originals are `L[0:38]` of the existing sample; `L[38:60]` are an unused reserve. | No redraw, no new scoring, no information about the items used. |
| b | Second pass = 15 originals + 5 N2 items, seed 20261131. | Proportional to 38 : 12. |
| c | N2 items: outside development launches and outside the 60 sampled launches; allocation formula written out for the spec's seed 20261116. | Independence of items; one realisation of the spec's rule. |
| d | N2 pass rule = one-sided Fisher exact p ≤ 0.05 on the pooled 12, gate 1 must also pass. | Exact at any n; chosen over the bootstrap rule and over p ≤ 0.025 on synthetic simulations only. |
| e | `N2_VALIDATED` only for scorer-1 estimates without the 45 development-launch rounds. | Goes beyond the literal edit, which names "confirmatory tests"; the more careful reading. It labels estimates the spec already computes and changes no computation in the spec. |
| f | Headline interval = Wilson; `UNSURE` excluded with both bounds printed. | One item per round and launch, so no clustering to model. |
| g | AC1 kept beside every kappa although D34 and D37 do not repeat D31's request for it. | Kappa falls when one label dominates. |
| h | One-hour rule: a pass-2 file that misses it is not scored; it may be replaced only before kappa exists. | A clock mistake should not decide the paper, and no kappa is ever recomputed after being seen. |
| i | Gate time = the first poll at which `author_pass1.csv` is complete; an incomplete volunteer file keeps the two-human design; a late one is descriptive only. | Leaves no moment at which the design could be chosen. |
| j | Two-human design has no PROVISIONAL state. | Adjudicators must not have seen results. |
| k | The volunteer and the LLM annotator get the instruction text without the second-pass sentences. | They have no second pass; steps 1 to 4 are identical for all. |
| l | LLM-annotator labels live in `gate1\llm_annotator\`, never in `labels\`, and are hidden from the humans until their files are in. | They are not labels in the sense of BRIEF §3.1 and must not influence the humans. |
| m | Scorer-2 bar: V1 (≤ 5% statements without `E` on a development smoke) decides the fallback; V2 (own gate lower bound > 0.5) decides "validated"; V3 (kappa with scorer 1 ≥ 0.40) changes wording only. | Dropping a second scorer for disagreeing with the first would select on agreement. |
| n | A4's `beta_E` is a family test only if the council approves the full scorer-2 run before real ranks can be read. | The decision to pay for the refit must not follow a look at the result. |
| o | Tier of record recomputed on the confirmatory set; thresholds 50, 100 and 0.10 untouched. | Follows from edit 6. The count for that set (144 launches) was already logged (D35) when this was written; said openly. |

**Design calculations (synthetic labels only; seed 777; runs of record 2026-11-15T19:12Z to 19:19Z, times inside each JSON).**
`analysis\planning\r4_power.py` (SHA-256 `ab5cd55b…2942`) → `r4_power.json` (`835bb65b…a104`):
superseded D31 design (n = 30, cut-off 0.40) and the N2 check rules at n = 12 and 24.
`analysis\planning\r4_selfconsistency.py` (`463153b2…69ea`) → `r4_selfconsistency.json` (`c2c63d91…0f76`):
self-consistency kappa at n = 20, cut-off 0.60, and the balanced-accuracy rule at n = 38.
`analysis\planning\r4_twohuman.py` (`9faa82cd…8a14`) → `r4_twohuman.json` (`a2480ef1…b979`):
inter-rater kappa at n = 50, cut-off 0.40. Logs beside each. All three import `gate1.kappa` and
reproduce the `gate1.ba` rule; the n = 20, cut-off 0.60 cell (0.3435) agrees with
`analysis\eval\gate1_sim.json` (0.3445) as a re-draw of the same design. Numbers are in §6.1b and §6.6.
A first run of `r4_power.py` was stopped because its bootstrap loop was slow; the bootstrap was
vectorised (checked equal to `gate1.ba`) and the script re-run; only the complete run was used.

**Not changed by R4.** The crux definition; the four statement labels; hidden = `SIDED`, `BLENDED`
or `OMITTED`; `E`; the 0.5 threshold on both sides; the prompts E1, L1, C1; scorer 1 and its
decoding; steps 1 to 4 of the labelling instructions and the four label tokens; the
balanced-accuracy statistic, its bootstrap, seed and the "> 0.5" rule; the A2 model, controls,
estimand, test and interval method; the tier thresholds; the N1 adjustment; Holm at 0.05.

**Superseded files and code that must change before any label (owners in EXPERIMENTS.md "R4").**
`labels_build\packet_L*`, `TEMPLATE_L*`, `LABELER_INSTRUCTIONS_L*`, `key.json`, `READY.md`, `README.md`
and `gate1\item_key.csv` describe the 44-row two-labeler packets and are void. `gate1.py` still has
`CUT = 0.60` on 20 shared items of two labelers, `N_ROWS = 44`, `N_GATE = 60`, requires `ADJ.csv`,
and knows neither the design switch, the PROVISIONAL status, AC1, the N2 check, the one-hour rule
nor the 38-item gate set. `common.check_kind` does not know `PROVISIONAL_PASS`. The poller watches
`L1.csv` / `L2.csv`. `build_analysis_set.py`, `a2_within_round.py`, the Tier-2 scripts,
`a2_informativeness.py` and `prevalence.py` default to all launches. Until these are changed and
tested on dummy data, no packet is released.

**Open for the human (none blocks the pipeline).** (1) Twelve N2 items give the N2 check little
power (§6.6); 24 would roughly double it. (2) In the single-labeler design no hypothesis-blind human
sees any item; the volunteer option (D37) is the only remedy in the rules. (3) The granite and
gpt-oss repository revisions are not in D36 and are pinned by the runners in the manifests.
(4) Choice e above narrows what may be called validated in N2.

### R4a — 2026-11-15T20:18Z to 20:21Z UTC, decisions.md D44 (planning room; `labels\` had 0 files, file not read-only, no `FREEZE.json`, checked at 20:18Z and 20:19Z). Rows marked **[R4a]**.

**Trigger.** D44: both Granite models missed the V1 technical bar on development launches (75.4%
and 57.5% of statements without `E`; bar 5%). The orchestrator allowed one more attempt under a
closed list, and asked for the V3 interval in `analysis\a4_bar.py` to be confirmed.

**Blindness.** Read: D44, the docstring and V3 lines of `a4_bar.py`, `serving\endpoints.json`, three
public model cards. No ranking, rating, label, score or smoke output was opened; the two failure
rates are quoted from D44.

| # | Section | Change | Reason |
|---|---|---|---|
| 1 | §6.9 new row, §4 scorer-2 row | Ordered, closed fallback list for scorer 2: (1) `tiiuae/Falcon-H1-34B-Instruct`, (2) `CohereLabs/c4ai-command-r7b-12-2024`. Same V1 bar, same frozen prompts, decoding and parser, no change to help a model pass; first to meet V1 is scorer 2; cap $2 each. | D44. Families (TII, Cohere) differ from the five generators, the Qwen scorer and the OpenAI annotator; cards show no base or teacher from those families. Not verified beyond the cards: training-data provenance. |
| 2 | §6.9 same row | If neither meets V1 before the freeze: no scorer 2; A4 "not run: no candidate passed the pre-registered technical bar"; out of the Holm family; all four smoke results printed; no further candidate. | D44. A closed list stops a search for a scorer that happens to work. |
| 3 | §6.9 V3 row | Interval of record for V3 = launch-cluster percentile bootstrap, B = 10,000, seed 20261121, as coded in `a4_bar.py`. Confirmed, not replaced. R4's pointer to the §7 method was an error (that method needs a regression coefficient). Descriptive; coverage unchecked; no rule reads it. | D44. |

**Not changed.** V1's 5% line, V2, V3's 0.40 reference line and its wording-only role, the A4
family-membership rule of §8, every prompt and the parser.

**Open.** Command R7B is gated on the hub; accepting its terms is a human step, and without it
the candidate counts as not deployable. Whether the vendored serving image runs Falcon-H1's hybrid
architecture (its card asks for vLLM 0.9.0 or later) is for the scorer runner to establish; an
image change is a serving setting and is logged. If scorer 2 ends up being neither Granite model,
`N2_ANALYSIS_SPEC.md` (which names Granite as A4) needs an amendment and a new hash from the code
owner before any N2 scoring.

### R5 — 2026-11-16 UTC, decisions.md D49, D49a–c, D50, D50a, D51 (planning room; `labels\` had 0 files and no `gate1\FREEZE.json`, checked 2026-11-16T01:17:05Z immediately before the edit; file not read-only)

**Trigger.** Human labelling redesign (D49, 00:50Z): no volunteer, full labelling too heavy. Step-1 inventory
(D49a), packet spec (D49b, D49c), proposal `analysis\council\R5_PROPOSAL.md` (SHA-256 `9eb7f7c5…71aa46`),
council 3/3 APPROVE-WITH-CONDITIONS (D50; `analysis\council\R5_vote_statistician.md`, `R5_vote_skeptic.md`,
`R5_vote_editor.md`), human time-out instruction (D51, 01:09Z).

**Adopted.** The proposal with every statistician condition (1–9), every skeptic condition (1–9) and editor
conditions 1–4, 6, 7; the D50 settlements of the eight open questions; D51.
**Rejected.** Editor condition 5 (sealed early N2 scoring): conflicts with the human's standing instruction;
N2 scoring waits for the recorded gate.

**Rows added or changed.** Header (freeze trigger; R5 paragraph; R4 validation-label paragraph superseded);
§5 superseded; §6.R5 (new: steps 1–5, D51 time-out, statuses, wording, rates, N2, frames, disclosure);
§6.0, §6.1b, §6.2, §6.3, §6.4, §6.4a, §6.6, §6.7, §6.8 superseded and §6.1, §6.1a, §6.5 partly superseded
(markers only; text unchanged); §7.3 R5 reading and corrected N2 hash in (c); §10 N2 row (spec hash
corrected, items (5) and (8) re-read); §12 R5 note; Known weaknesses 11–15. Unchanged: §1–§4, §6.9
(A4 not run, D47/D48), §7, §7.1, §8, §9, §11, §13, Appendix A.

**Differences from the proposal, all from D50/D51.** Step-2 class minimum raised from 30 rounds / 15 launches
to 50 / 25; single-class resamples > 1% → UNUSABLE; question-cluster bootstrap, smaller lower bound decides;
added reported figures; CONTRADICTED reworded and now downgrades every `E`-based result to
EXPLORATORY_UNVALIDATED; VALIDATED_PRESENCE no longer "confirmatory"; P2 dropped; no PROVISIONAL state;
"no panel" if fewer than 2 models pass; step-3 bootstrap seed 20261144 and panel seed 20261145 (the
proposal's 20261142/20261143 would have collided with the question bootstrap); survey and critique analyses
not run; the human-declared "no file will come" route replaced by the D51 time-out.

**Computations for R5 (none read a score, rank, rating value or label).**
`analysis\planning\r5_feasibility.py` (counts of rated members by presence only) → `r5_feasibility.json`;
`analysis\planning\r5_step3_power.py` (synthetic, seed 777) → `r5_step3_power.json` and, with `--usable`,
`r5_step3_power_usable.json` (SHA-256 `5f9ab421…e2d50d`); the statistician's `r5_stat_council_sim*.py`
(synthetic, seeds 4242/4243).

**Not changed.** BRIEF hard rules 1 and 3; the scorer, prompts, parser and decoding; A2's model and
estimand; the sample of record (`sample.json`, `n2_items.json`) as the frame of the 25 packet items.
