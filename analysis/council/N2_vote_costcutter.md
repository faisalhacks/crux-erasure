# N2 experiment council: cost cutter

Reviewed: BRIEF 3 rule 5, 8, 11; COSTS.md; ledger.csv; N2_COUNCIL_PACKET.md; n2_grid.py; modal_serving/README.md and serve_vllm.py; pilot_harness budget.py and llm.py (ModalSession).
Checked: no spend yet. `analysis/n2_runs/smoke` and `full` hold only plan.json, with no gens files. ledger.csv shows $0.65 of infra spend and no N2 row.

## Arithmetic check (recomputed from n2_grid.py)
- gemma: 2000 x 250 / 450 x 1.15 = 1278 s decode, plus 104 s cold = 1382 s. Plus 135 s tail = 1517 s, at $0.000665/s = $1.01. Matches.
- qwen: 1437 s decode, plus 106 s cold = 1543 s. Plus tail = 1678 s, at $0.001344/s = $2.26. Matches.
- Worst case is rate x (2 x wall + tail) = $1.93 + $4.33 = $6.26. Matches.
- Smoke worst $0.74 plus full worst $6.26 is about $7.0, under the N2 cap of $10.
- Budget fit: spent $0.65, plus N2 ceiling $6.5, plus B $10, plus F-min $25 gives about $42 of the $150. The EXPERIMENT_CAPS_USD entries sum to exactly $150, so there is room.
- The estimate is sound and conservative. 400 tok/s aggregate for a 27B on an H100 at 32-way batch is far below the bandwidth ceiling. Real cost is probably below $3.27, and the $30 credit is ignored on top of that.

## Flaws

1. **Smoke cannot measure steady-state throughput.**
   - Evidence: smoke is 4 rounds x 4 cells x k=1, which is 16 requests per model. The harness runs 32 in flight. The smoke therefore measures batch-16 plus first-request JIT warm-up. The README's qwen first batch took 9.66 s for 4 short prompts.
   - Consequence: the number that feeds `--tok-per-s` is biased low. The re-plan then shows a spuriously high worst case, or the council is asked again for no reason.
   - Severity: medium.
   - Cheapest fix: smoke at 8 rounds (32 requests per model, one full wave), or take the throughput from the first 128-batch of the full run. Added cost is under $0.05.

2. **The re-plan step breaks the approval gate.**
   - Evidence: `plan_hash` includes `assumptions.tok_per_s_overrides`, so a re-plan with `--tok-per-s` gives a new `plan_sha256`. `check_gates` requires the hash in the approval file to equal the plan's hash whenever worst case exceeds $5. The packet's step (2), "re-plan, launch if within the ceiling", will be REFUSED, or someone hand-edits the approval file.
   - Severity: medium. It is a process hazard, not a money leak.
   - Cheapest fix: state in the approval that a re-plan is covered when sample, prompts and models are unchanged and worst case is at most $6.50. The orchestrator then writes the new hash into a copy of the approval file and logs it in decisions.md. If the measured speed is at least about 1.3x the assumption, worst case falls to $5 or less and no approval is needed.

3. **Nothing actively stops containers. Shutdown relies on the 120 s scaledown window.**
   - Evidence: `ModalSession.__aexit__` only settles the ledger. serve_vllm.py sets no `timeout` on the serving function (the only `timeout` is on the CPU download job). COSTS.md rule 2 says a Modal-side `timeout_s` is set. The session `max_seconds` is client-side only.
   - Bound: `max_containers=1`, proxy auth and `scaledown_window=120` make the leak bounded. A dead client leaves at most about 135 s of idle billing. But "guaranteed" is not shown. Nothing checks `modal container list` after a run.
   - Severity: low to medium.
   - Cheapest fix: a `finally` step, or a manual step, that runs `python -m modal container list`. If a container is listed, run `container stop <id>`. Also require this check after any abnormal exit.
   - Bonus: an explicit stop saves about $0.27 per session of real billing ($0.09 + $0.18 tail). The ledger still books the tail, so the ledger stays conservative.

4. **A separate smoke session roughly doubles the fixed cost.**
   - Evidence: each session pays cold start (104 s and 106 s) plus 135 s tail. Per the packet, the smoke is expected at $0.51, about 15% of the $3.27 expected full cost. The full run then pays cold start and tail again.
   - Severity: low. The smoke buys real information (truncation, thinking-off verification).
   - Cheapest fix (optional): make the first 128-request batch of the real run the gate, with auto-abort on more than 10% truncated or empty output. This saves about $0.45. If a separate smoke is kept, apply flaw 1.

5. **Batch barrier wastes GPU on drain.**
   - Evidence: batches of 128 with a 32-way semaphore. `run_many` must finish a batch before the next starts. Each batch ends with a partial wave. 2000 gens is about 16 batches. Waste is roughly 5 to 10% of decode time.
   - Severity: low.
   - Cheapest fix: a batch size of 512 or more, or a single run_many over the whole todo list with periodic error-rate checks. This needs no redeploy.

6. **Concurrency is capped at 32 by the harness, though decode is memory-bound.**
   - Evidence: vLLM defaults to 256 sequences. Qwen 27B (56 GB weights on an H100 at 3.35 TB/s) is far from its batch ceiling at 32.
   - Severity: low as a risk, since it makes the estimate conservative. It is the main lever if throughput proves poor.
   - Cheapest fix: do nothing now. Do not raise the cap unless the smoke measures qwen below 400 tok/s.

7. **GPU choice.**
   - gemma on an L40S is the cheapest GPU that fits 24 GB of bf16 weights with KV cache. An L4 and an A10 (24 GB) cannot hold them. This is fine.
   - qwen on an H100: an A100-80GB is 37% cheaper per second but about 0.6x the bandwidth. That makes cost per token about equal, with only about 9 GB of KV headroom after the 55.6 GB of weights. Not worth the risk. Quantising to fit an L40S would change the measured model. This is fine.
   - About 18% of each container-second is CPU and RAM (4 cores and 32 GiB, or 8 cores and 64 GiB). Halving them would save about $0.3 in total but needs a redeploy and risks weight-load OOM. Skip.
   - Severity: none.

8. **ledger.csv "actual" is manual.**
   - Evidence: the estimate row is written before launch, but "actual to be filled after settle" has no automated writer. The ledger.csv rows (and the cumulative column) go stale. The authoritative number is the harness ledger.jsonl.
   - Severity: low.
   - Cheapest fix: after each stage, append the actual from `summary.json` (`harness_spent_usd`) and cross-check `modal billing report --for today --show-resources`.

9. **Timeout margin is thin if throughput is much lower.**
   - Evidence: the timeout is 2x the expected wall. If real tok/s is at most about 0.45x the assumption, the session hits `max_seconds` before the run finishes. Output is resumable from cache, but a second cold start plus tail is paid.
   - Severity: low. The cost is bounded by the $6.26 reservation, and the stop rule says return to the council.

10. **Shared workspace.**
    - Evidence: COSTS.md open item. The Modal workspace shows $17.61 metered this month from other projects. The harness ledger does not see it.
    - Severity: low. It does not change the N2 decision, but it makes "$150" ambiguous. Confirm with the human before F-exp.

## Checks that pass
- Every job has a timeout. `check_gates` refuses a missing one, and the `ModalSession` max_seconds is enforced.
- The harness refuses beyond the cap. A pilot cap and a global cap are checked at reserve. The N2 committed amount plus the worst case is checked before launch.
- Launch is refused without `--confirm-launch`. Above $5 it is also refused without an approval file bound to the plan hash.
- Open reservations after a crash are charged at estimate by `--settle-stale`, so the ledger is pessimistic.

## Conditions (all cheap)
1. Smoke must be at least 32 requests per model, or the throughput must come from a full 128-request batch. Smoke must also report the truncation rate and confirm thinking is off in the output.
2. After every Modal stage (smoke and each model), confirm `modal container list` is empty. Run `container stop` otherwise. Record the check in decisions.md.
3. Any re-plan after the smoke needs a new approval file for its new hash, issued by the orchestrator under this vote, or a worst case of $5 or less. Worst case must not exceed $6.50.
4. After each stage, write the actual spend into ledger.csv, cross-checked against `modal billing report`.
5. If the smoke-measured throughput puts worst case above $6.50, stop and return to the council. Do not raise the timeout.

VOTE: APPROVE-WITH-CONDITIONS: (1) smoke at least 32 requests per model, or throughput from a full 128-request batch, and report truncation with thinking confirmed off; (2) confirm `modal container list` empty after every stage, with `container stop` otherwise; (3) a re-plan needs a re-issued approval for its new hash, or a worst case of $5 or less, and never above $6.50; (4) record actual spend in ledger.csv and cross-check against Modal billing; (5) return to the council if re-planned worst case exceeds $6.50.
