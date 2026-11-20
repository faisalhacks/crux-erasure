# SCORER council vote: cost cutter

Inputs read: BRIEF rule 5, section 8, section 11; decisions D13 (cap now $200; BRIEF text still says $150); ledger.csv; COSTS.md; A2_SCORING_COUNCIL_PACKET.md; scorer_manifest.json; scorer.py; harness llm.py (ModalSession, cache key).
Spend so far: ledger cumulative $1.613 (+ N2 smoke_qwen estimate row $0.544 with no ACTUAL yet). Cap is not the constraint; waste and re-runs are.

## Arithmetic check of the packet estimate

- Rate: $0.00134388/s (H100 + CPU + RAM, from harness). Probe check: 296.2 s billed x 0.00134388 = $0.398. Matches ledger. The rate is credible and slightly conservative (Modal billing came in about 8% under harness list price, COSTS.md).
- Expected: wall = 106 + 0.73 x 1960 + 0.14 x 4 x 1960 x 0.85 = about 2,470 s; (2,470 + 135) x rate = $3.50. Arithmetic is right.
- Worst: (3,700 + 135) x rate = $5.154. Right, and it is below the $5.20 job cap.

## Critique

1. Flaw: the $3.50 is a 10x extrapolation of two ~180-call runs; the packet's own formula plan disagrees.
   Evidence: scorer_manifest.json cost_plans.all gives expected_wall 4,020 s and expected $5.58, which is MORE than the 3,700 s timeout. all_measured assumes 0.73 s/round and 0.14 s/label stay flat at 32-way concurrency. Probe measured 35.5 s / 40 extractions = 0.89 s/round, not 0.73. Margin between expected (2,470 s) and timeout (3,700 s) is only 1.5x.
   Severity: medium. Cheapest fix: none needed for the vote, but treat $5.15 as plausible, not a tail. Pre-register that the true expected is $3.5 to $5.2.

2. Flaw: a timeout throws away everything not already in the harness cache.
   Evidence: scorer.py execute(): `recs, ext = await asyncio.wait_for(score_statements(...), timeout=max_s)`; scores.jsonl and extractions.jsonl are written only after it returns. score_statements does all extraction, then all labels, then builds records. A timeout at 3,700 s leaves no score file (random-prefix claim in packet section 4 is not true of the output file). Only per-call cache entries survive.
   Severity: medium-high (a $5.15 run that yields nothing). Cheapest fix: catch TimeoutError/BudgetExceeded and rebuild records from the cache on resume, or process in 4 chunks of launches inside the one session and write after each chunk. Roughly 15 lines.

3. Flaw: the packet says "resumable through the harness cache" but a re-run still pays a full session.
   Evidence: llm.py cache key = sha256 of the full request (model, messages, seed, extra). Same prompt + seed means hit at $0. But ModalSession still books cold start (about 106 s) plus 135 s tail = about $0.32 minimum per session even if every call hits cache, and reserves (max_seconds+135) x rate against pilot_cap 10.
   Severity: low. Cheapest fix: if the cache fully covers the request set, skip the Modal session and score offline (call_all with provider modal only needs a session for uncached calls).

4. Flaw: container shutdown is checked but not enforced.
   Evidence: scorer.py runs `modal container list` immediately after the session; ledger notes for both prior runs record "container rows after run 2" and "after run 1", i.e. a live container during the 120 s scaledown window. The packet's "must be empty" is therefore unreachable at that moment. The booked tail (135 s = $0.18) is 45% of a probe or gate1 run and 5% of the full run.
   Severity: low for A2, medium for the many small runs. Cheapest fix: set scorer-session scaledown_s to about 30 s in modal_endpoints for scorer runs, or `modal container stop <id>` at session exit. Saves about $0.14 per session. Re-check the list once after 150 s.

5. Flaw: gate-1 and probe each pay a separate cold start for no reason.
   Evidence: ledger rows 6/8 and 10/11: cold start 93-109 s plus 135 s tail = about $0.33 of each ~$0.39 run.
   Severity: low. Cheapest fix: one session that runs probe then gate1 (a combined mode). Saves about $0.33.

## Q1: cost to re-run dev probe + gate-1 after a scorer fix

The 49/50 and 135/136 E >= 0.5 (mean E 0.985 on the dev probe) points at the labelling step, not extraction: almost nothing is labelled VISIBLE. A fix there changes prompt L1 only (an Appendix A / FROZEN_RULES change needing its own sign-off); the E1 extraction prompt and its cache stay valid.

- Probe: actual was $0.398 (296 s billed). Re-run with extractions cached: about $0.35 (cold start + 140 new labels + tail). If E1 also changes: $0.40. Reservation/worst case $0.85.
- Gate-1: actual was $0.383. Re-run with extractions cached: about $0.34. Reservation $0.99. (Order-check swapped labels are new calls too.)
- Total: about $0.75 as two sessions ($0.70 to $0.80), about $0.43 as one combined session (fix 5). Worst-case reservation $1.84.
- If only the gate-1 SAMPLE changes (scorer untouched): gate1 only, about $0.25 to $0.38, and A2 is unaffected.
- If only post-processing (threshold or E definition) changes: $0, rescoring from stored labels.

## Q2: full A2 job now or after Q1

Paying now risks paying twice. If the fix is in L1, all 6,664 label calls (about 930 s, about $1.25 plus a second session overhead of about $0.3) are wasted, so re-doing A2 costs about $1.6 extra; if E1 changes, the whole $3.5 is wasted. If only the gate-1 sample changes or the fix is post-processing, nothing is wasted either way, but nothing is gained by launching first. Waiting costs only clock time; the cap is $200 and $1.6 is spent. D13's "decide fast" is met by running Q1 now (about 6 minutes of Modal time, under $0.8). Also fix flaw 2 (partial write on timeout) before the big run regardless of the outcome.

Conditions on a later approval: flaw 2 patched; timeout stays 3,700 s; approval file max_usd >= 5.154; expected $3.5 to $5.2 recorded in the ledger estimate row.

Q1: about $0.75 (range $0.43 combined session to $0.80; worst-case reservation $1.84)
Q2: APPROVE-AFTER-Q1
