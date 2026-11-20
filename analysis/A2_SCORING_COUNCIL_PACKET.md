# A2 full-dataset scoring: experiment-council packet (skeptic, methodologist, cost cutter)

Status: REQUEST FOR APPROVAL. NOT launched. Needed because the job cap ($5.20, EXPERIMENTS A2) exceeds $5 (BRIEF 8).
Runner: `analysis/scorer.py all --confirm-launch --approval-file <file>`. No ranking or rating is read.

## 1. Claim supported
Scorer 1 gives every one of the 1,960 eligible rounds' 4 candidates a crux erasure score E (FROZEN_RULES 3-4), the single input A2 (confirmatory beta_E), N1, N4 need. Scores are inputs only; A2/N1 may not touch real ranks until GATE1_RESULT.json exists (FR 6.5). Scoring itself reads opinions and statements only, so running it before gate 1 breaks no rule. If gate 1 fails, the scores are used only in the appendix as "unvalidated instrument".

## 2. Prior-work check
The construct delta vs Mahajan et al. (arXiv 2611.05135, via scout notes, D4) and Tessler et al. 2024 is in N2_COUNCIL_PACKET section 2 and decisions.md D4/D5; this job is measurement infrastructure and claims nothing new alone. The citation verifier must open those papers before any sentence relies on them.

## 3. Cost (from measurement, not assumption)
Two measured runs on Qwen3.8-27B/H100 (probe 184 calls, gate 160 calls): cold start 93-109 s; extraction 0.73 s per round, labelling 0.14 s per call at 32-way; list-price sessions $0.398 and $0.383. Extrapolated to 1,960 extractions + 4 labels x ~85% non-zero-crux rounds, using the slower measured extraction rate (0.89 s/round, probe; the gate run gave 0.73): wall about 2,780 s, expected $3.92 (range $3.5 to $3.9 across the two rates). The extrapolation is 10x beyond the largest measured run, so throughput at scale is still unmeasured. The earlier formula plan in scorer_manifest.json (`cost_plans.all`, 4,020 s, $5.58) used assumed throughput and is superseded by the measured plan (`all_measured`); the 3,700 s timeout is 1.33x the measured-rate wall, and a run slower than that is cut off by design (see section 5), not extended.
Worst case = reservation for the timeout: (3,700 + 135) s x $0.001344/s = $5.15, within the $5.20 line. GPU: H100 (Qwen 55.6 GB weights; L40S cannot hold it; A100-80 saves per-second price but loses bandwidth, per cost-cutter N2 flaw 7).
Scorer-2 pass (A4, gemma4-12b) is separate: not requested here; its measured-free estimate is about $2-3 and is a separate packet.

## 4. Design and controls
- Launches in `random.Random(20261125)` order, all rounds of a launch together (random-prefix rule), so a stop leaves a random subset; the count is reported.
- One extraction per round, one label call per statement, seed 0, retry seed 1; parse failures counted per step (probe: 0/40 extraction, 4/140 label = 2.9%).
- Gate-1 diagnostic already shows the main risk: 49/50 scored gate statements have E >= 0.5 and 10/60 are in zero-crux rounds. Little within-round variation in E is likely; FR 7 interpretability floor handles it. That is a result to report, not a reason to change the definition.
- Output written per run; resumable through the harness cache.

## 5. Stop condition, timeout, resume
- Modal `max_seconds` 3,700 for one session (client-enforced; each chunk is also wrapped in `asyncio.wait_for` with the remaining time). Ledger estimate + timeout row before launch, ACTUAL row after.
- Incremental output (fix of cost-cutter flaw 2): launches are processed in the random-prefix order in chunks of 100 rounds; each finished chunk is appended to `scorer_runs/all/scores.jsonl` and `extractions.jsonl`. A timeout or budget stop therefore keeps every finished chunk; an unfinished chunk's calls stay in the harness cache. A re-run skips finished statements. Resuming costs a new session (cold start + tail, about $0.32) and needs its own approval if the total would exceed the $5.20 line; the analysed set is otherwise the finished prefix, with its count reported.
- Stop on evidence only: cap hit; parse-failure rate above 20% in the first 200 calls (N2 rule); council rejection. Never for the clock.
- Shutdown (fix of flaw 4): after the session closes the runner polls `modal container list` every 15 s for up to 300 s until no container of the scorer's own app remains (other apps' containers are counted, never touched); if one is still alive it is stopped by id and the list re-checked once. The result (waited_s, own_rows_final, stopped_by_id) is written to `container_check.json`, the summary and the ledger ACTUAL row; the human or orchestrator records it in decisions.md and cross-checks `modal billing report`.
- Re-plan needing a worst case above $5.20 returns to the council.

## 6. Requested decision
APPROVE a single session, scorer 1, 1,960 rounds, timeout 3,700 s, worst case $5.15, expected about $3.9. The orchestrator writes an approval file with `approved: true, approved_by, max_usd >= 5.154` per the runner's check.
