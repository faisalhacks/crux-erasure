# N2 experiment-council packet (skeptic, methodologist, cost cutter)

## REVISION 2 (2026-11-15, after 3/3 approve-with-conditions and the smoke). This section SUPERSEDES sections 1, 3, 4 and 8 below where they differ.
- Claim scope: "two open-weight models". COMMON vs DIS is a manipulation and instrument check (Mahajan et al. credited), not a finding.
  Contrasts of interest: override SAT-DIS vs ACC-DIS, SAT-COMMON vs ACC-COMMON, the interaction, and each against a NEUTRAL arm (COMMON only).
  Cross-scored cells (qwen text by scorer 2, gemma text by scorer 1) are primary. Habermas Machine iteration-0 candidates are the free baseline.
  Scorer validity on N2 text is assumed, not tested. Full spec: `analysis/N2_ANALYSIS_SPEC.md`, sha256 3875c61e6708c6e1d43500575c694e0cdd8fd1b060eb4879ebcac02ec929c8f3, logged in decisions.md D13.
- Design now 5 cells (2x2 + NEU-COMMON) x 250 rounds (231 launches) x k=2 x 2 models = 5,000 statements. `design_sha256` f5159058a369737d20eb86378e93a520e42b5626f43ae29d86c8a57916e8c46e.
- SMOKE DONE (outside the N2 sample; 8 rounds x 5 cells x 1 = 40 requests per model; excluded from analysis; summaries in `n2_runs/smoke_gemma`, `smoke_qwen`):
  measured end-to-end 193 tok/s (gemma, mean 145 output tokens) and 222 tok/s (qwen, mean 176 tokens), well below the 450/400 assumed.
  Cold start 109 s and 120 s. Actual cost $0.1823 + $0.3854 = $0.568 (list price). Errors 0; truncated 0; think-tag leaks 0;
  reasoning_content present 0; refusals 0; preambles 0 in every cell; near-duplicate rounds 0%. Qwen exceeded the 150-word cap in 19 of 40 outputs
  (max 175 words); gemma 0 of 40. Length is reported per cell and as a residualised sensitivity (spec 5).
  Caveat: one 40-request run is two waves incl. warm-up, so the measured rate is a lower bound.
- RE-PLAN from measured throughput (out 200 tok, no extra prefill factor, timeout = 1.5 x expected wall): expected $5.23, **worst case $7.71**, 5,323 GPU-s.
  `plan_sha256` 47a2305b58c23e51f9daa438d0b89e73f74cbb7f1717a96243bb9f8f52a849fc. Worst case is above the $6.50 originally approved, so a new ceiling (>= $7.75) is needed.
  Fallback if the council prefers: k=1 (1,250 statements per model), expected $2.86, worst case $5.45, design_sha256 bac7604e..., plan_sha256 1c0f2d7c....
- Approval is bound to design_sha256 (and plan_sha256 if the approval file names it) and max_usd >= worst case. The runner refuses anything else.
- Code guards: `--mode score` refuses unless analysis/GATE1_PASSED.json exists and its scorer_manifest_sha256 matches analysis/scorer_manifest.json; smoke/launch refuse unless the spec's sha256 is in decisions.md.

Status: REQUEST FOR APPROVAL. No paid run has been made. Nothing was launched on Modal. The only
execution was the $0 mock dry-run. Approval needed because worst-case cost exceeds $5 (BRIEF 8).
Runner: `analysis/n2_grid.py`. Plan: `analysis/n2_runs/plan_default/plan.json`
(plan_sha256 `a27be1f49e25a00d...`; full hash in the file; the approval file must quote it).

## 1. Claim supported
H-N2: when current open models write a group statement from the same Habermas opinion sets, the
erasure score of the statement depends on what the model is asked to do, in a 2x2:
system prompt {SAT: keep everyone satisfied | ACC: be accurate about differences} x user prompt
{COMMON: find common ground | DIS: show where they disagree}.
Pre-specified contrasts, within round (paired): system main effect (SAT - ACC), user main effect
(COMMON - DIS), and interaction. Direction predicted: SAT and COMMON give higher erasure.
Support for the project: it shows that a satisfaction-seeking instruction produces hiding statements
in today's models, which links the ranking finding (A2) to a cause. It does NOT show that
participants reward such statements; that is A2. A flat result is reported as a flat result.
The outcome is the erasure score from the scorer to be frozen in FROZEN_RULES.md. Generation here is
independent of scoring: this script reads no rankings and no labels.
Scoring N2 outputs on real data is allowed only after gate 1 passes the scorer (BRIEF 3.3, 4).
Before then, outputs are inspected for format only (length, truncation), not scored.

## 2. Prior-work check (delta vs Mahajan et al., arXiv 2611.05135, 3 Nov 2026; decisions.md D4)
Mahajan et al. (as recorded by novelty scout 1) is LLM-judged, uses no human ratings, and finds that
agreement-oriented prompts cover minority positions less. That overlaps N2 directly. N2 is therefore
NOT claimed as first. Our additions:
1. A 2x2 crossing system and user prompt, which separates "the system was told to please everyone"
   from "the user asked for common ground". An agreement-vs-neutral contrast cannot do that.
2. The outcome is the project's scorer, which is validated against blind human labels (gate 1;
   Cohen's kappa >= 0.60 on the shared items, bootstrap lower bound of balanced accuracy > 0.5). Mahajan
   et al. use LLM judgement without human validation. If the gate fails, N2 is reported as
   "not yet measurable" and is not interpreted.
3. Same opinion sets as the human-ranked study (Habermas Machine data), so N2 results can be set
   beside A2/N1 on matched material.
4. Open models spanning two scales (12B, 27B) on current weights, full precision, seeds and prompts logged.
Caveat to state in the paper: Mahajan et al. was read via scout notes (decisions.md D4). The citation
verifier must open the paper and re-check the above before any sentence about it is used.
Also cite Zaghouani 2605.26940 (name collision on "erasure") and Tessler et al. 2024 (contrary finding).

## 3. Sample design
- Rounds: 250 rounds from the 1,960 eligible rounds (`pilots/T3_1/all_groups.jsonl`, sha256 in plan.json),
  drawn with seed 20261115, **one round per distinct question** (no clustering on question), chosen before
  any outcome exists. 250 distinct questions exist among 1,476. 4 of the 250 also sit in the pre-brief
  reference sample (informational; harmless because N2 reads no labels).
- Models: `gemma4-12b` (L40S) and `qwen3.8-27b` (H100); both deployed and smoke-tested. Same rounds and
  same opinion order (seeded per round) in all 4 cells, so the design is paired.
- n per cell: 250 rounds x k=2 samples (temperature 0.7, distinct seeds) per model = 500 statements per
  cell per model, 2,000 per model, 4,000 total. The two samples are averaged within a round-cell before
  the paired test, so the analysis unit is the round.
- Optional 70B rung: `llama3.3-70b` is gated (HF token gets 403, NEEDS-HUMAN) and untested; R1-Distill-70B is a
  reasoning model and would change what is being measured. NOT in the base request. With
  100 rounds x k=1 it adds ~$3.8 expected, ~$7.2 worst case, and pushes the package to $10.64 worst
  case, which the script refuses. Ask separately after a human gets the access.
- Prompt text is fixed in the script and hashed into the plan. Format instruction (<= 150 words, no
  preamble) is identical across cells. Thinking is disabled so the output is the statement.

### Power note (paired design, two-sided t test on the round-level contrast, computed with scipy noncentral t)
| n rounds | d_z=0.20 | d_z=0.25 | d_z=0.30 |
|---|---|---|---|
| 150 | 0.68 | 0.86 | 0.96 |
| 200 | 0.80 | 0.94 | 0.99 |
| 250 (planned) | 0.88 | 0.98 | 1.00 |
(alpha 0.05, all computed.) With a Bonferroni split over 2 models x 3 contrasts (alpha 0.0083), n=250
gives 0.69 at d_z=0.20, 0.90 at d_z=0.25 and 0.98 at d_z=0.30. So the planned n detects a standardised
paired effect of about 0.25 at corrected alpha and about 0.2 uncorrected. Smaller effects are not
resolved, and a null should be read as "no effect larger than ~0.25 SD", not as "no effect".
d_z is the mean round-level difference over its SD. The true SD is unknown until the scorer exists, so this
is a sensitivity statement, not a forecast. The second sample per cell lowers generation noise, so
the real d_z for a fixed true effect is likely at least as large as with k=1. Analysis: bootstrap over
rounds (B=2000, seed 20261115), report all contrasts with CIs, including flat ones.

## 4. Cost estimate (logged before launch; recomputable with `--mode plan`)
Prices: modal.com/pricing list prices via `pilot_harness/prices.py`; the $30/month credit is ignored, so
real spend is lower. Throughput and tokens are ASSUMPTIONS (steady state never measured): output 250
tokens per statement (150-word cap; hard max_tokens 400), 1.15x for prefill, 450 tok/s (gemma) and
400 tok/s (qwen) aggregate. Cold starts are measured (104 s, 106 s). Idle tail 135 s per session.

| model | gens | container | $/s | expected wall | expected GPU-s (incl. tail) | expected $ | session timeout | worst case $ (reservation) |
|---|---|---|---|---|---|---|---|---|
| gemma4-12b | 2,000 | 1x L40S | 0.000665 | 1,382 s | 1,517 | 1.01 | 2,764 s | 1.93 |
| qwen3.8-27b | 2,000 | 1x H100 | 0.001344 | 1,544 s | 1,678 | 2.26 | 3,087 s | 4.33 |
| **total** | 4,000 | | | | **3,195** | **3.27** | | **6.26** |

Worst case = the session reservation, rate x (timeout + tail), with the timeout set to 2x the expected wall time.
Expected is under $5; worst case is $6.26, so the council is asked to approve a ceiling of **$6.50**
(N2 cap is $10; the plan is refused if its worst case exceeds $10).
Two-step approach: (1) smoke (`--mode smoke --confirm-launch`, 4 rounds x 4 cells x 1 sample per model,
expected $0.51, worst case $0.74, below the council threshold) to measure real tok/s and cold start;
(2) re-plan with `--tok-per-s` from the smoke and, if the new worst case is still within the approved
ceiling, launch. If measured throughput is lower such that worst case exceeds $6.50, come back to the council.
Optimizer levers already in the script: JSONL cache plus per-model result file (resume without re-paying),
batches of 128 with a batch timeout, 32 in-flight requests per model, `--max-parallel-models` (distinct
apps run concurrently; each app is max_containers=1, so more throughput per model would need a redeploy
with more containers, which leaves GPU-seconds roughly equal but adds a cold start per container). Removing
`--enforce-eager` could raise decode throughput; not done, untested.
Each launch writes a `ledger.csv` estimate row (estimate, timeout, approver) before any GPU starts.

## 5. Stop conditions and timeout
Stop only on evidence (BRIEF 5), never the clock:
- N2 cap reached ($10 ledger-wide for N2) or global $150: harness raises BudgetExceeded; the script stops that model.
- Session timeout (`max_seconds` = 2x expected wall; ceiling 5,400 s): the harness refuses further calls.
- Batch error rate above 20% (default) stops the model and keeps finished outputs.
- Batch timeout 900 s; per-request timeout 180 s with harness retries.
- Output sanity: if more than 10% of statements are truncated (finish_reason=length) or empty in the smoke,
  fix the prompt format and re-smoke before the full run.
- Not a stop condition: the observed effect size or direction.
- Pilot-shows-no-signal rule does not apply, because N2 is a measured 2x2 whose null is reportable.

## 6. Risks and limits
- Throughput assumption could be wrong in either direction; the smoke measures it before the full spend.
- Two Modal apps stay deployed at 0 tasks (human to stop; no idle billing).
- Statements are model-written; no human participants, no private data, no secrets. Prompts quote opinions
  already in the public Habermas data. No weights are released.
- Mock dry-run proves the pipeline (sampling, pairing, caching, resume, refusals), not model behaviour.
- Interpretation of N2 depends on gate 1. Without it, N2 text is generated but unscored.

## 7. Verification already done ($0)
- `--mode dry-run` (mock provider, temp ledger and cache): 12 rounds x 4 cells x 2 models = 96 generations,
  0 errors; rerun produced 0 new calls (resume works). Logged in `analysis/RUNS.md` as kind `dummy`.
- Refusals checked: smoke or launch without `--confirm-launch`; launch without approval file when worst case
  > $5; plans above the $10 cap (600 rounds x k=3; and the 70B variant at $10.64).

## 8. Requested decision
Approve: gemma4-12b + qwen3.8-27b, 250 rounds, k=2, smoke first, ceiling $6.50 worst case,
under the stop conditions above. Approval file format (written by the council, not by this runner):
`{"approved": true, "plan_sha256": "<from plan.json>", "max_usd": 6.5, "approved_by": "experiment council: <votes>"}`.
Two of three votes; a tie is no.
