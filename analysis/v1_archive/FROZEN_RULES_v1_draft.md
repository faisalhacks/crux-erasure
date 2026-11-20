# FROZEN_RULES.md — T3-1 crux erasure pre-registration

**DRAFT — freezes (read-only) when P\labels\L1.csv or L2.csv first exists.**

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

---

## 1. Question, hypothesis, primary estimand

| Item | Rule | Why |
|---|---|---|
| Question | Within a round, do participants rank statements that hide the group's real disagreement better than statements that show it? | BRIEF §1. |
| Hypothesis direction | None fixed. The test is two-sided. | The original study reports that statements incorporated minority views; either sign is a result. |
| Single confirmatory estimand | `beta_E` in the A2 model (§7), scorer 1, per-rater ranks. | One primary estimand (statistician rule 2). |
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
| Development set | The 150 launches in `pilots\T3_1\pilot_groups.jsonl` (file SHA-256 recorded in `P\analysis\scorer_manifest.json`). Prompts may be tried on these, using opinions and statements only. | Prompt development must not touch the gate-1 sample. |
| Analysis set | All eligible rounds. A2 is reported on all launches (primary) and again without the 150 development launches. | Chair ruling §4.1: report with and without pilot groups. |
| Rank direction | `numerical_ranks` 0 = best. Must be confirmed in experiment 0 from the repo's `analysis/types.py` and by the sign of the within-rater association between rank and the rater's own `ratings.agreement`. If it cannot be confirmed, A2 and N1 do not run. | The one sampled example suggests 0 = best; one example is not confirmation. This check uses no erasure score. |
| Ties in ranks | Kept, as mid-ranks. A rater whose 4 ranks are all equal carries no information and is dropped and counted. | Ties exist in the data (`exp0_rank_unit.json`); dropping tied raters would discard real responses. |

## 3. The group's real disagreement (cruxes), from the opinions only

| Item | Rule | Why |
|---|---|---|
| Definition | A **crux** is a specific point on which at least one member asserts or prioritises something that at least one other member denies, rejects or weighs very differently. Points everyone agrees on, and differences only of wording, emphasis or example, are not cruxes. | BRIEF §4: disagreement is defined from the opinions, not the rankings. |
| Inputs to crux derivation | The question text and the members' opinion texts. Nothing else. The extractor never receives candidate statements, rankings, ratings, critiques, cohort or any outcome. `score_erasure.py` must build the extraction prompt from a table that contains only these columns (asserted in a unit test). | Keeps the predictor free of outcome information. |
| Opinion order | Opinions sorted by `participant_id`, numbered from 1, untruncated. A round whose prompt exceeds the served context length is dropped and counted. | Deterministic; an outside judge can rebuild the prompt. |
| Extraction | One call per round, prompt E1 (Appendix A), 0 to 4 cruxes, most important first, each with the member numbers on side A and side B. | Cap of 4 as in the pilot; member lists are needed for N4. |
| Zero cruxes | The round has no measurable disagreement. Its erasure score is undefined for A2/N1 (round excluded and counted). For gate 1 see §6. | A statement cannot hide what is not there. |
| Human counterpart | Labelers derive the disagreement themselves from the same opinions (§5). They never see the AI's crux list. | Gate 1 then tests the whole instrument end to end, not just the last step. |

## 4. The erasure score

| Item | Rule | Why |
|---|---|---|
| Scorer 1 (primary) | `Qwen/Qwen3.8-27B`, revision `37561816e66b5b9153b1b64c10968c18c1e6f4a0`, served by `modal_serving\serve_vllm.py` alias `qwen3.8-27b`. | Largest deployed and smoke-tested rung; revision pinned. |
| Scorer 2 (A4) | `google/gemma-4-12B-it`, revision `43c9d014b231474fa7212dbb48a762566c2b255d`, alias `gemma4-12b`. Runs both steps (extraction and labelling) itself. | Different model family, deployed and smoke-tested. The 70B rung is undeployed and unpriced. |
| Decoding | temperature 0, seed 0, JSON output; `max_tokens` 700 (extraction), 300 (labelling). Reasoning/thinking mode off if the served template supports it; the setting actually used is written to `scorer_manifest.json` before freeze and does not change after. | Deterministic and auditable. The thinking switch is unverified today, so it is recorded rather than assumed. |
| Prompt location | Text of record: Appendix A of this file. Working copies: `P\analysis\prompts\E1_extract.txt`, `L1_label.txt`, `C1_clarity.txt`, byte-identical to Appendix A; their SHA-256 values go in `scorer_manifest.json`. | The frozen file carries the prompts, so freezing it freezes them. |
| Labelling | One call per statement (not four statements per call). Per crux, exactly one of `VISIBLE`, `SIDED`, `BLENDED`, `OMITTED`. | Scoring statements separately avoids contrast effects between candidates. |
| Hidden | A crux is **hidden** by a statement if its label is `SIDED`, `BLENDED` or `OMITTED`. It is **shown** only if `VISIBLE`. | The construct is "hides the disagreement": a reader of a one-sided statement does not learn that anyone disagreed. |
| Score and scale | `E(s) = (number of hidden cruxes) / (number of cruxes)`, in [0, 1]; 0 = shows every crux, 1 = hides every crux. | Continuous share; simple to recompute by hand. |
| Parse failure | One retry with seed 1. If it still fails, `E` is missing. In A2/N1 a round with any missing `E` is dropped and counted. In gate 1 a missing `E` counts as a wrong prediction. Parse-failure rates are reported per scorer and step. | Failures are kept and counted, never silently dropped (methodologist checklist). |
| Weighting | Unweighted. A member-weighted variant is reported as sensitivity model A2g (§7). | No validated salience weights exist; an unweighted share can be checked by hand. |
| Order check (diagnostic, no rule) | On the 60 gate items only, labelling is repeated once with the crux list reversed and sides A/B swapped. The share of items whose binary call changes is reported. The score of record is the original order. | Judge position bias is documented; one deterministic pass stays the instrument so the score is reproducible. |
| Pre-freeze prompt changes | Allowed only to fix output-format or parse problems seen on the development set, at most one revision, logged in decisions.md. No change after freeze, for any reason. | BRIEF §4: never change definitions. |

## 5. Gate-1 labelling instrument

| Item | Rule | Why |
|---|---|---|
| Labelers | L1: consultant, not told the hypothesis. L2: author, knows the hypothesis. Files `P\labels\L1.csv`, `P\labels\L2.csv`, written only by those humans. | BRIEF §3.1. |
| Item | One statement with its round's question and all members' opinions. | BRIEF §4: opinions beside the statement. |
| Labelers see | `item_id` (random, opaque), question, numbered opinions, the one statement, the instructions below. | Minimum needed to judge. |
| Labelers do not see | Rankings, ratings, any AI score or AI crux list, the other three candidates, cohort, launch or round IDs, statement provenance, which statement won, the other labeler's labels. The instructions do not contain the words "crux erasure", "sycophancy" or the hypothesis. | BRIEF §4; keeps L1 blind to the hypothesis. |
| Label options | `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`. | "Unsure" is required by BRIEF §4; `NO_DISAGREEMENT` stops labelers forcing a label when there is nothing to hide. |
| Packet | `P\gate1\packets\L1_packet.csv` and `L2_packet.csv` with columns `item_id, question, opinions, statement, label, main_disagreement, comment`. Packets are built by `g1_packets.py`, which may read only the sample file and the opinion and statement text. | Packets live outside `labels\` so that building them cannot trigger the freeze. |
| Label file schema | `P\labels\L1.csv` and `P\labels\L2.csv`: UTF-8 CSV with a header row and exactly the columns `item_id,label,main_disagreement,comment`, one row per packet row (44). `item_id` is copied unchanged from the packet. `label` is one of `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`; case and surrounding spaces are ignored; no other token or synonym is accepted. | One exact schema, so no label is ever interpreted. The stats coder's looser token list in `gate1.py` must be narrowed to this. |
| Item IDs | A shared item has the same `item_id` in both packets. A duplicate-check row has a fresh `item_id`. The mapping (`item_id, labeler, launch_id, round_id, cand, role, dup_of`, role = shared / unique / duplicate) is in `P\gate1\item_key.csv`, which labelers never see. Label files carry no `dup_of` column. | A visible `dup_of` would tell the labeler which rows repeat. |
| Adjudication file schema | `P\labels\ADJ.csv`: columns `item_id,adj_label,reason`, one row per shared item sent to adjudication, `adj_label` from the same four tokens. | Same tokens, so the merge is mechanical. |
| Incomplete files | A blank or invalid label, a missing or unknown `item_id`, or a repeated `item_id` means the file is incomplete; the pipeline reports the rows and waits. It never fills, guesses or corrects a label. | BRIEF §3.1. |
| Packets released | Only after `scorer_manifest.json` exists (prompts hashed, decoding fixed, smoke test on the development set logged). | The scorer must be fixed before any label can exist. |

**Instructions given to both labelers (verbatim):**

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
> Judge only what is written. Do not judge whether the statement is good, fair or well written, or whether you agree with it. Do not look anything up and do not use any AI tool. Do not discuss rows with the other labeler until you are told both files are in. Some rows may look familiar; label each row on its own without looking back. Do not leave `label` blank.

## 6. Gate 1: sample, kappa, adjudication, pass rule

### 6.1 Sample design

| Item | Rule | Why |
|---|---|---|
| Population | Eligible rounds (§2) whose launch is not in the development set. | No validation on items the prompt was developed on. |
| Size | 60 distinct statements: 20 shared, 20 unique to L1, 20 unique to L2. | BRIEF §4. |
| Independence | One statement per round, one round per launch: 60 launches. | Each item is its own cluster, so the bootstrap can resample items directly. |
| Sampling | Simple random, not stratified by any AI score. `g1_sample.py`: `rng = random.Random(20261115)`; `L = rng.sample(sorted(launch_ids), 60)`; for each launch in order, `round = rng.choice(sorted(eligible round_ids))`, then `cand = rng.randrange(4)`. `L[0:20]` shared, `L[20:40]` L1-unique, `L[40:60]` L2-unique. | Random sampling gives unbiased sensitivity and specificity; stratifying on the AI score would bias both unless reweighted. |
| Sample of record | `P\gate1\sample.json` (with its SHA-256 and the Python version in the manifest). Once written it is never redrawn. | The realised list, not the code, is what the gate used. |
| Duplicate checks | Per labeler 4 repeated rows **(J)**: `rng.sample` of 2 from the shared 20 and 2 from that labeler's unique 20, drawn after the main sample from the same `rng`, L1 first. Each packet therefore has 44 rows. | BRIEF §4 asks for duplicate checks; 4 keeps the added reading near 10%. |
| Row order | Per labeler, the 40 rows are shuffled with `random.Random(20261117)` (L1) and `random.Random(20261118)` (L2); each duplicate is inserted at least 10 rows after its first appearance. Duplicates get fresh `item_id`s. | Stops order effects lining up across labelers and hides the repeats. |
| Use of duplicates | The first appearance is the label of record. Repeats are used only for intra-labeler agreement (count of matching pairs out of 4, reported per labeler). No pass/fail rule attaches to it. | The brief sets no rule for it; it is reported so readers can judge. |

### 6.2 Step 1: agreement (before adjudication)

| Item | Rule | Why |
|---|---|---|
| Statistic | Cohen's kappa, unweighted, on the 20 shared items, labels of record, three categories: `HIDES`, `NOT_HIDING` (= `SHOWS` or `NO_DISAGREEMENT`), `UNSURE`. All 20 items are used; `UNSURE` is a category, not an exclusion. | The gate target is HIDES vs not. Keeping `UNSURE` in counts it as disagreement, the stricter reading. |
| Cut-off | Point estimate ≥ 0.60 passes step 1, compared at full precision with no rounding. Below 0.60, or undefined (a labeler used one category for all 20), fails gate 1. | BRIEF §4; the cut-off is not changed. |
| Borderline results | The point estimate alone decides. A pass whose bootstrap interval reaches below 0.60 is still a pass, but the paper must print the interval beside the kappa and say that agreement is not established with precision at n = 20. A fail whose interval reaches above 0.60 is still a fail. No items are added, relabelled or dropped after kappa is seen. | With 20 items almost any interval will straddle 0.60; the honest handling is to report it, not to move the line. |
| Also reported, no rule | Four-category kappa; kappa on items where both gave a definite label; a percentile bootstrap 95% CI over the 20 items (B = 10,000, seed 20261116); the full 4×4 table. | With 20 items the kappa is imprecise; the reader should see that. |
| Order of operations | `g1_kappa.py` writes `P\gate1\KAPPA.json` before `g1_adjudication_sheet.py` will run. | "Before adjudication" is enforced by the code, not by intention. |

### 6.3 Step 2: adjudication (humans only)

| Item | Rule | Why |
|---|---|---|
| Which items | Shared items where the two labels of record differ in the three-category scheme (including one `UNSURE` against a definite label). | Only disagreements need resolving. |
| Sheet | `g1_adjudication_sheet.py` writes `P\gate1\adjudication_sheet.csv`: `item_id`, question, opinions, statement, both labels and both `main_disagreement` notes. The script may not import or read any score, ranking or rating file (asserted in a unit test). | BRIEF §4: adjudication blind to AI scores. |
| Who and how | L1 and L2 discuss each listed item and agree one final label from the same four options. If they cannot agree, the final label is `UNSURE`. They write `P\labels\ADJ.csv` (`item_id, final_label, reason`). The pipeline never writes this file. | The brief says humans adjudicate; a third file is needed to hold the result. Logged as an interpretation of BRIEF §3.1. |
| Adjudicated label per item | Shared, labels agree: that label. Shared, labels differ: `ADJ.csv`. Unique items: the single labeler's label of record. | A deterministic merge; no label is created by the pipeline. |

### 6.4 Step 3: scorer validity

| Item | Rule | Why |
|---|---|---|
| Gate set | The 60 sampled statements, minus items whose adjudicated label is `UNSURE` (excluded, counted and listed). | BRIEF §4. |
| Human binary | Positive = `HIDES`. Negative = `SHOWS` or `NO_DISAGREEMENT`. | Matches the three-category scheme used for kappa. |
| AI binary (fixed now) | Scorer 1. Positive if `E ≥ 0.5`. Negative if `E < 0.5` or the extractor found zero cruxes. Missing `E` (parse failure) = wrong prediction. | 0.5 mirrors the labelers' "half or more not shown" rule, so both sides use one threshold. No threshold is tuned on labels. |
| Statistic | Balanced accuracy = (sensitivity + specificity) / 2. | BRIEF §4; insensitive to class imbalance. |
| Bootstrap | Resample the gate-set items with replacement, B = 10,000, `numpy.random.default_rng(20261116)`. A resample with no positives or no negatives scores 0.5. Lower bound = 2.5th percentile (lower end of the two-sided 95% interval). | The brief's "95% lower bound" could mean the 5th or the 2.5th percentile; the stricter one is used. A one-class resample carries no evidence of skill, so it is scored as chance. |
| Pass | Step 1 passed **and** lower bound > 0.5. | BRIEF §4. |
| Record | `gate1.py` writes `P\gate1\gate1_computed.json`: computed status (`PASS` / `FAIL` / `INCOMPLETE`), kappa, balanced accuracy, bounds, confusion table, exclusions, hashes of both label files, `ADJ.csv`, sample, scores, this file. An Opus reviewer re-derives it from the raw files. Only then does the planning room (Fable, BRIEF §6 "gate decisions") write `P\gate1\GATE1_RESULT.json` and the decisions.md entry. The planning room may not record a status different from the computed one. | Hard rule 3 turns on this record, so it is written once, after an independent check, and never by the analysis script itself. |
| Also reported, no rule | Balanced accuracy on L1's 40 items only, using L1's own labels (the fully blind labeler); the same for scorer 2; Spearman correlation between `E` and the human binary; agreement on "is there any disagreement" (human `NO_DISAGREEMENT` vs AI zero cruxes). | Reviewers want the blind-labeler number; none of these can rescue or sink the gate. |

### 6.5 Before the gate is recorded

`a2_within_round.py`, `n1_winner_vs_mean.py` and every Tier-2 script refuse to read real ranks or
ratings unless `GATE1_RESULT.json` exists. Until then they run only on (a) within-rater shuffled ranks
(each rater's 4 ranks permuted across the 4 statements, `random.Random(424242)`), or
(b) synthetic dummy data from `make_dummy.py`. Why: BRIEF §3.3.

## 7. A2: within-round rank vs erasure (confirmatory)

| Item | Rule | Why |
|---|---|---|
| Outcome | Per rater and round, ranks converted to mid-ranks 1..4 (1 = best) and then to `y = (4 − midrank) / 3`, so 1 = ranked best, 0 = ranked worst. | Outcome is rank within round (BRIEF §5); mid-ranks keep ties; the 0-1 scale gives a readable coefficient. |
| Predictor | `E` from scorer 1, raw 0-1 scale. | A coefficient per unit of `E` is the gap between a fully hiding and a fully showing statement. |
| Control: length | `log(word count)`, words = matches of `[A-Za-z0-9']+`; z-scored over all statements in the analysis set. | Longer statements can show more and may be ranked differently for length alone. |
| Control: clarity | Flesch Reading Ease, `206.835 − 1.015·(words/sentences) − 84.6·(syllables/words)`. Sentences = number of non-empty pieces after splitting on `[.!?]+`, minimum 1. Syllables per word = number of `[aeiouy]+` groups in the lower-cased word, minus 1 if the word ends in "e" but not "le" and the count is above 1, minimum 1. Z-scored like length. | Deterministic, no model and no package version; an outside judge can recompute it with a regex. |
| Model | `y_irs = a_ir + beta_E·E_s + beta_L·zLen_s + beta_C·zClar_s + e_irs`, with a fixed effect `a_ir` for each (rater, round). Fitted by OLS after demeaning within (rater, round). Every rater-round has equal weight. | The fixed effect makes it a within-round comparison only. A linear model on ranks is simple and handles ties. |
| Rounds with no variation in `E` | Kept (they inform the controls) and counted. They add nothing to `beta_E`. | Dropping them would change nothing for `beta_E` and would hide how often the scorer cannot separate candidates. |
| Uncertainty | Cluster bootstrap over `launch_id`: resample launches with replacement, keep all their rounds and raters, refit. B = 10,000, `numpy.random.default_rng(20261119)`, percentile 95% interval. Z-scoring constants are computed once on the full set. | Bootstrap by group (BRIEF §5). |
| Interval method check (pre-freeze only) | Coverage of the percentile interval is checked on ≥ 200 null reshuffles of shuffled or dummy data. If coverage is below 93% **(J)**, the method is changed to a more conservative one in this row, with a decisions.md entry, before freeze. After freeze the method written here is fixed. | decisions.md D8 saw 36 of 40; that is within noise but must be settled before real data, not after. |
| Primary estimand and test | `beta_E`. Two-sided, alpha = 0.05. The association is called detected if the 95% interval excludes 0. Bootstrap p = `2·min(#{b ≤ 0}+1, #{b ≥ 0}+1) / (B+1)`, reported. | One estimand, one test. |
| Sign reading | `beta_E > 0`: hiding statements are ranked better. `beta_E < 0`: showing statements are ranked better. | Stated before the data are seen. |
| If the interval includes 0 | Reported as "no association detected at this precision", with the interval. No claim of "no effect", no rebuttal of prior work: no equivalence margin was set that we could justify. | Statistician rule 3; a noisy scorer biases `beta_E` toward 0. |
| Interpretability floor **(J)** | If fewer than 50 launches have at least one round with within-round variation in `E`, `beta_E` is still reported, but the paper says the rank question was not measurable at this sample and makes no directional claim. | A cluster bootstrap on a few dozen informative clusters is not trustworthy. |

**Pre-specified sensitivity models (reported beside A2; they never replace it):**

| Model | Change from A2 | Why |
|---|---|---|
| A2b | Adds rater-level `zOwnSim` = cosine similarity between the statement and that rater's own opinion, `sentence-transformers/all-MiniLM-L6-v2`, z-scored. | The methodologist's self-interest confound. The brief fixes A2's controls as length and clarity, so this is a sensitivity model. **Binding wording rule:** if `beta_E` in A2b has the opposite sign or its 95% interval includes 0, the abstract and discussion must say the association cannot be separated from raters preferring statements close to their own view. |
| A2c | Replaces Flesch clarity with a 1-5 clarity rating from scorer 2 (prompt C1), z-scored. Runs only if the A4 cost cap allows after scorer-2 erasure scoring. | Readability is a narrow proxy for clarity; a different model than scorer 1 avoids shared error with `E`. |
| A2d | A2 without the 150 development launches. | Chair ruling §4.1. |
| A2e | Alternative score `E_pos` in which `SIDED` counts as shown (the pilot PREREG's "retention" definition). | Shows how much the result depends on the one-sided-statement choice in §4. |
| A2f | Adds `zVague` = count of vague terms per 100 words, z-scored. Fixed list **(J)**, whole-word, case-insensitive: some, many, various, several, certain, often, sometimes, generally, may, might, could, perhaps, possibly, balance, balanced, appropriate, reasonable, important, consider, considered, factors, issues, aspects, range, complex. | Novelty scout 1 asked for a vagueness control. It is a sensitivity model, not a primary control: the brief fixes the controls, and vagueness is partly the construct itself (`BLENDED`), so controlling for it in the main model would remove real effect. |
| A2g | `E_w`: each crux weighted by the share of members named on either side of it. | Scout 2's salience weighting, with weights that come from the opinions and are fixed in advance. |
| A2h | A2 without the clarity control (length only). | Clarity may be a mediator: the writing choice that hides a crux may also make text read more smoothly, so the clarity control can absorb real effect. Both estimates are always printed side by side. If they differ in sign or in whether the interval excludes 0, the results section must say so. The primary stays with clarity because the brief names it. |

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

| Exp | Definition | Family test | Why |
|---|---|---|---|
| N1 | Winner of a round = the statement with the lowest mean mid-rank over the round's eligible raters. Rounds with a tie for winner are excluded and counted. `d_r = E(winner) − mean E of all 4 candidates in the round`. | Mean of `d_r` over rounds; launch-cluster bootstrap, B = 10,000, seed 20261120, 95% percentile interval, two-sided. | Mean-rank winner is deterministic and needs no tie-break RNG. "Average candidate" is read literally as all 4; the gap to the other 3 is `d_r·4/3`. Sensitivity: Schulze winner from the repo's `schulze_method.py`. |
| A4 | A2 refitted with scorer 2's own `E` (own cruxes, own labels). | `beta_E` under scorer 2, same bootstrap (seed 20261121). | A fully independent second instrument. Also reported: Spearman correlation and binarised kappa between the two scorers' `E`, with launch-bootstrap intervals. |
| A3 | Runs only if ≥ 30 launches **(J)** have a round that otherwise passes §2 but contains at least one `HUMAN_MEDIATOR` and at least one `MODEL_MEDIATOR` candidate. Counted by `build_analysis_set.py` before any score exists. | Mean within-round difference `E(AI-written) − E(human-written)`; launch bootstrap, seed 20261122. | "If data allows" is decided by a count fixed in advance, not by the result. The A2 slope inside these rounds is reported descriptively. |
| N3 | For eligible rounds that also have `iteration_index == 1` candidates: cruxes stay those derived from the opinions; iteration-1 candidates are labelled with the same prompt. Runs only if ≥ 30 launches **(J)** qualify. | Mean within-round difference `mean E(iteration 1) − mean E(iteration 0)`; launch bootstrap, seed 20261123. | Disagreement is defined from opinions, so the cruxes must not change between drafts. |
| N4 | Per-rater ranks only. A rater's side is taken from the first-listed crux: minority = the side with fewer members. Rounds with equal sides, and raters on neither side, are excluded and counted. Model = A2 plus `E × minority`. | The interaction coefficient; launch bootstrap, seed 20261124. | Uses the extractor's member lists, which come from opinions only. Skipped under the per-group fallback (BRIEF §14). |

## 9. Multiple comparisons

| Item | Rule | Why |
|---|---|---|
| A2 | Tested alone at two-sided alpha = 0.05, no correction. | It is the single confirmatory test. |
| Tier 2 family | The family tests of N1, A4, A3, N3, N4 that actually run (at most 5). Holm step-down at family-wise alpha = 0.05. Raw and Holm-adjusted p-values are both reported; intervals stay unadjusted 95% and are marked as such. | Holm controls family-wise error with no independence assumption. Family size depends only on the data-availability counts in §8, never on results. |
| Sensitivity models A2b-A2h | Not tested for significance on their own; reported as estimates with intervals. | They qualify A2; they are not extra chances to find an effect. |
| Everything else | Exploratory; reported with intervals, no significance language. | BRIEF §3.10. |

## 10. Confirmatory, secondary, exploratory

| Label | What |
|---|---|
| Confirmatory | Gate 1 (§6). A2 `beta_E`, scorer 1 (§7). |
| Pre-specified secondary | A2b-A2h; N1, A4, A3, N3, N4 with the Holm family. Never described as confirming the main claim. |
| Exploratory | N2, N5, N6, B, F as far as they bear on this paper. N2 statements are scored only with scorer 1 and only after gate 1 is recorded as PASS, so that N2 adds a human-validated scorer and a system-by-user prompt grid to what Mahajan et al. (arXiv:2611.05135) already report. Also exploratory: an embedding position-axis score; any analysis with `ratings.agreement` or `ratings.quality` as the outcome; reliability-corrected coefficients; iteration-1 replications of A2; rounds excluded by the bot filter; a 70B or closed-model third scorer; the pilot's lexical and embedding measures; anything not written here. |
| Pre-brief pilot | Anything the pilot computed on real rankings before this file existed is labelled "pre-gate exploratory, executed before frozen rules existed" (decisions.md D1) and is not evidence for any claim. |

## 11. Per-group fallback (BRIEF §14)

| Item | Rule | Why |
|---|---|---|
| Decision rule for experiment 0 | Ranks are **per rater** if (i) `rankings.metadata.participant_id` equals the row's own participant in ≥ 99% of human rank rows **(J)** and (ii) among round-iterations with ≥ 2 human raters, fewer than 50% **(J)** have identical rank vectors for all raters. Otherwise **per group**. | A written, checkable rule. The pilot's `exp0_rank_unit.json` reports 100% for (i) and 234 of 7,871 for (ii). The baseline's independent check (decisions.md D6, `analysis\EXP0_rank_unit.md`) reports 100% and 8,131 of 8,268 multi-rater groups with differing rankings: **per rater; fallback not triggered.** The rule stays here in case a later check contradicts that. |
| If per group | Log in decisions.md. A2 uses one rank vector per round: `y_rs = a_r + beta_E·E_s + beta_L·zLen_s + beta_C·zClar_s + e_rs`, round fixed effect, same bootstrap. N1 uses the group's top-ranked statement as winner. A2b uses the mean similarity to all members' opinions. N4 is skipped. | BRIEF §14. |
| Reporting | The paper states that the outcome is a group aggregate, that the data points are fewer, and that individual preference cannot be separated from the aggregation rule. More effort moves to F and B. | BRIEF §14: "stated as a limitation". |

## 12. "Not yet measurable" write-up

| Trigger | Consequence | Why |
|---|---|---|
| Kappa < 0.60 or undefined | Gate 1 = FAIL. The paper is the "not yet measurable" version: the humans could not agree on the construct at this instrument. | BRIEF §4. |
| Balanced-accuracy lower bound ≤ 0.5 | Gate 1 = FAIL. The paper is the "not yet measurable" version: the scorer is not shown to beat chance. | BRIEF §4. |
| After a FAIL | No definition, prompt, threshold, sample or label option is changed and no re-labelling is requested. A2 and Tier 2 may be run on real ranks only as "exploratory, unvalidated instrument", in an appendix, never in the abstract or as a finding. The write-up reports kappa, the confusion table, the unsure items and what a better instrument would need. | "Never change definitions." Hard rule 10: every run is reported. |
| Labels incomplete or absent at handover | Gate 1 = NOT EVALUATED. This is reported as such and is not a fail. No real-rank analysis is run. | Hard rules 1 and 3; unfinished work reported honestly. |
| Gate passes but the §7 interpretability floor fires | Gate 1 is reported as passed; the rank question is reported as not measurable at this sample. | The instrument can be valid and still not vary within rounds. |

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
that are only wording, emphasis or examples. Do not invent disagreements. List between 0 and
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
   not fix it.
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
