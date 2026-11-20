# EXP0: is the ranking unit per rater or per group?

**VERDICT: PER-RATER.** Each row of `hm_all_candidate_comparisons.parquet` holds one participant's own ranking of the candidates. The group-level ranking (social choice) is a separate, derived field. Section 14 fallback is not triggered.

Independent check. Script: `t3_1/analysis/exp0_check.py` (reads only ID, provenance and rank columns; no erasure score and no outcome analysis). Output: `t3_1/analysis/exp0_check.json`. No seed (deterministic). Input sha256 `7cf8d5ce3fce8853b36f0ffe1158424f7813867e422e313db4df0a5f9e03e4a4`.

## Schema fields (parquet, 39,955 rows)
- Unit keys: `launch_id` (group of participants), `round_id`, `iteration_index` (0 = opinion round, 1 = post-critique), `worker_id`.
- Per-rater: `rankings.metadata.participant_id`, `rankings.metadata.id`, `rankings.candidate_ids` (list), `rankings.numerical_ranks` (list of int, lower is better, rank 0 = best), `rankings.metadata.provenance` (HUMAN_CITIZEN 35,489 / BOT_CITIZEN 4,466), `ratings.agreement`, `own_opinion.metadata.participant_id`.
- Per-group (derived): `top_candidate.*`, `candidates.reward_data.welfare_or_rank`, `candidates.all_welfare_or_rank`, `top_candidate.reward_data.welfare_or_rank`.

## Evidence from the data
1. `rankings.metadata.participant_id` == `own_opinion.metadata.participant_id` in 100.0% of rows. The ranker is the person whose opinion is on the row.
2. `rankings.metadata.id` is unique in every row (share 1.0); 7,189 distinct ranker ids.
3. Per (launch_id, round_id, iteration_index): 8,274 groups, rows per group = 5 (7,537), 4 (401), 2 (330), 1 (6). Rows == distinct participant ids in 100% of groups.
4. Of 8,268 groups with >=2 raters, 8,131 contain more than one distinct ranking vector; only 137 are all identical.
5. In all 8,268 multi-rater groups every rater ranks the identical candidate-id list (a shared candidate set, individual orderings).
6. The final-preferences file `hm_all_final_preference_rankings.parquet` is also one row per `metadata.participant_id` with its own `numerical_ranks`.

## Three example rows (one group, iteration 0, ids truncated)
| launch/round | worker_id | rankings.metadata.participant_id | own_opinion...participant_id | rankings.candidate_ids | rankings.numerical_ranks |
|---|---|---|---|---|---|
| 00295a73/49e3bcc2 | 69ccc530 | 604c0f5c35 | 604c0f5c35 | c54c39,26653c,f482b0,e98a7f | [2,3,1,0] |
| same | 4e65aed2 | 7c9df9b7ee | 7c9df9b7ee | same list | [0,1,3,2] |
| same | 32dee0e9 | 83936534f9 | 83936534f9 | same list | [1,0,2,3] |

## Repo code that defines it (`data/habermas_repo/src`, git 7923b71)
- `analysis/serialise.py:50-58`: `RANKINGS_CANDIDATE_IDS`, `RANKINGS_NUMERICAL_RANKS`, `RANKINGS_PARTICIPANT_ID = 'rankings.metadata.participant_id'` are a per-participant ranking record (`self.RANKINGS`, lines 315-324).
- `analysis/serialise.py:37`: `COMPARISON_PARTICIPANT_ID = 'metadata.participant_id'`.
- `habermas_machine/machine.py:125-156` `_get_rankings`: "Gets rankings over all candidates for each citizen"; loops `for i in range(self._num_citizens)`, one ranking per citizen opinion, returns an array [citizens x candidates].
- `habermas_machine/machine.py:214-217`: `social_choice_method.aggregate(all_rankings, ...)` turns the per-citizen rankings into the group (social) ranking. This is the only per-group ranking and it is derived, stored in the `*.welfare_or_rank` fields.
- `habermas_machine/reward_model/base_model.py:67` and `social_choice/base_method.py:59`: "lower is better and the best candidate is thus given rank 0".
- `analysis/live_loading.py:393-414` `filter_out_mock_rankings`: rows with `RANKING_MOCK = -1` come from worker bots.

## Caveats
- Bot rows exist (4,466 BOT_CITIZEN); restrict to HUMAN_CITIZEN (the pilot's s03_prep already does).
- Groups often have 5 raters but some have 1-2 (small groups); eligibility needs >=3 raters.
- Rater rankings within a launch share opinions and candidates, so they are dependent: resample by launch_id.
- Ties/duplicate ranks: ranks are dense ints; number of ties not checked here.
- Agreement with the pilot's own `pilots/T3_1/exp0_rank_unit.json` (same sha256, pid equality 1.0) is consistent; my numbers use all rows including bots, so counts differ by design.
