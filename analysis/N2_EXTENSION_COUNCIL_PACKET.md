# N2 extension: council packet (generators, A4 scorer, LLM annotator)

Prepared 2026-11-16 by the model scout. No paid runs were made. Basis: decisions.md D31 edits 3 and 5, D34 item 4 (as relayed by the coordinator); COSTS.md; modal_serving README and serve_vllm.py; n2_grid.py; scorer.py and scorer_manifest.json. HF metadata was read with the existing token (never printed). Proposed code is in `N2_EXTENSION_PROPOSED_DIFF.md`; nothing outside t3_1 was edited.

## 1. Budget position

* Global cap $200 (budget.py). Ledger.csv, sum of actual rows: **$7.944** (N2 $2.305, A2 $2.453, B $1.015, A1 $0.809, A1/A2 probe $0.711, infra $0.651). Remaining about **$192.06**. (COSTS.md still says $150; stale.)
* Per-experiment cap N2 is $10 (budget.py). N2 has spent $2.305.

## 2. Proposed set (all different families from each other and from Qwen and Gemma)

| role | alias | HF repo @ revision | family | licence | gated / token access | size | Modal GPU |
|---|---|---|---|---|---|---|---|
| N2 gen 1 | ministral3-14b | mistralai/Ministral-3-14B-Instruct-2512-BF16 @ 3cea74c1ebaf | Mistral | Apache-2.0 | not gated; config fetch 200 | 13.9B, ~28 GB bf16 | L40S ($2.40/h container) |
| N2 gen 2 | olmo3.1-32b | allenai/Olmo-3.1-32B-Instruct @ ac0587e4a774 | AI2 OLMo | Apache-2.0 | not gated; 200 | 32.2B, ~64.5 GB | H200 ($5.43/h) |
| N2 gen 3 | phi4-14b | microsoft/phi-4 @ 2db69c1c3e91 | Microsoft Phi | MIT | not gated; 200 | 14.7B, ~29 GB | L40S |
| A4 scorer | granite4.2-30b | ibm-granite/granite-4.2-30b @ 9e668ce1c538 | IBM Granite | Apache-2.0 | not gated; 200 | 29.3B dense, ~58.6 GB | H100 ($4.84/h) |
| LLM annotator | gptoss-120b | openai/gpt-oss-120b @ b5c939de8f75 | OpenAI gpt-oss | Apache-2.0 | not gated; 200 | 117B MoE, 5.1B active, MXFP4 ~65 GB | H100 |

Container $/h = GPU + CPU + memory as the harness prices it (L40S 0.000665/s, H100 0.001344/s, H200 0.001508/s).

Why these:
* **Ministral-3-14B** is the same size class as Gemma-4-12B and the newest Mistral model of that size on HF (Nov 2025). The plain repo is FP8 (a mixed-precision file); use the `-BF16` repo for full weights, as for the other models. Newer Mistral releases are not usable: Mistral-Small-4 is 119B, Medium-3.5 is 128B, Large-4 is about 1T.
* **Olmo-3.1-32B-Instruct** is the closest dense match to Qwen3.8-27B and is fully open. It needs an H200: 64.5 GB of weights leave about 7 GB for KV cache on an 80 GB card. Fallback on H100 with `--max-model-len 8192` is possible but unmeasured. Budget alternative: Olmo-3-7B-Instruct on L40S (~$0.4).
* **Phi-4** is older (Dec 2024) but strong at 14B, ungated and MIT. Its context is a hard 16,384 tokens, which is enough for N2 generation (prompts about 2k tokens).
* **Granite-4.2-30B** (Aug 2026) is the newest model in the set and was chosen as scorer because a scorer needs the strongest JSON follower of the non-generator families. Thinking is on by default in its template; the harness already sends `enable_thinking=False`, which makes the template close the think block, so output is plain. Context 128K.
* **gpt-oss-120b** as annotator: independent family, strong reasoner, one H100. It cannot switch reasoning off; for labeling that is a benefit, but calls need `max_tokens >= 4096` and the answer is read from `content`.

vLLM support: all architectures (Mistral3ForConditionalGeneration, Olmo3ForCausalLM, Phi3ForCausalLM, GraniteForCausalLM, GptOssForCausalLM) are in the vLLM registry in recent versions, and IBM documents Granite-4.2 serving with vLLM (needs 0.20+; image is 0.32.0). **Not verified inside the v0.32.0 image**; the first smoke is the test.

JSON and chat template (scorer): Granite and Phi-4 ship chat templates with a system role. Granite template is `chat_template.jinja` (9 KB, supports `enable_thinking`). `response_format={"type":"json_object"}` is the same vLLM guided-decoding path that already worked for Qwen (0 parse failures in scorer v2). Granite as scorer must pass 0 parse failures on the 60 gate-1 statements plus the 12 N2 validation statements before any N2 scoring.

## 3. Throughput evidence and cost

Measured on the existing models (n2_runs summaries, ledger): Gemma-4-12B on L40S 1,250 gens billed 547.8 s, $0.3645; Qwen3.8-27B on H100 566 gens in 353 s (275 tok/s, 172 mean out tokens, 32 in flight), 489.5 s billed, $0.658. Scorer on H100: 7,993 calls in 1,695 s (0.212 s/call), $2.453. **New-model throughputs are assumptions** scaled from those: Ministral 440 tok/s, Phi-4 420, Olmo on H200 330, Granite 250 (scorer 0.244 s/call). 175 mean output tokens, cold start 150 s, 135 s tail, timeout = 2x expected wall (the n2_grid rule).

N2 generation, 1,250 generations each (250 rounds x 5 cells x k=1):

| model | expected wall | timeout_s | expected $ | worst case $ (reservation) | smoke 40 gens, worst $ |
|---|---|---|---|---|---|
| ministral3-14b (L40S) | 647 s | 1,294 | 0.52 | 0.95 | 0.37 |
| olmo3.1-32b (H200) | 813 s | 1,626 | 1.43 | 2.66 | 0.84 |
| phi4-14b (L40S) | 671 s | 1,342 | 0.54 | 0.98 | 0.37 |
| **generators total** | | | **2.49** | **4.59** | **1.58** |

Fits the N2 cap: $2.305 spent + 4.59 + 1.58 = $8.48 <= $10, but the margin is $1.5. If a smoke fails and is repeated, ask the human to raise the N2 cap rather than starting a new experiment line.

A4 scorer (Granite-4.2-30B on H100), calls = 250 extraction rounds + one label call per statement:

| scope | calls | expected $ | worst $ | timeout_s |
|---|---|---|---|---|
| the ~2,600 existing N2 statements (Qwen + Gemma + 12 validation) | 2,750 | 1.24 | 2.31 | 1,581 |
| all 5 generators (6,250 statements) | 6,500 | 2.47 | 4.76 | 3,409 |
| gate-1 60 + 12 N2 validation items, for agreement with the primary scorer | 330 | 0.45 | 0.72 | 401 |
| smoke before any of the above (40 gens equivalent) | | | 0.75 | |

Cheaper alternative scorer: Phi-4 on L40S, 6,500 calls expected $1.97, worst $3.84 (but then Phi-4 cannot be a generator).

Primary scorer (Qwen) on the 3,750 new generator statements, a consequence of the extension, not an A4 cost: 3,750 calls, expected $1.41, worst $2.64. Extraction is shared per round, so it is not repeated.

LLM annotator (gpt-oss-120b, H100), about 70 items incl. repeats, 2,500 reasoning plus answer tokens each, 32 in flight (aggregate about 1,200 tok/s assumed, MoE with 5.1B active): cold start about 200 s (65 GB weights), generation about 150 s. Expected $0.69, worst $1.19 (timeout 750 s). Add a 12-item check first: worst $0.70. Annotator total worst **$1.9**. Fallback gpt-oss-20b on L40S: worst about $0.5.

**Worst case, all of it:** generators 4.59 + gen smokes 1.58 + A4 on all 5 generators 4.76 + A4 gate set 0.72 + A4 smoke 0.75 + Qwen on new statements 2.64 + annotator 1.9 + weight downloads and misc 0.15 = **$17.1**. Expected about $9.5. Reserve **$22** (about 30% for unmeasured cold starts and one repeated smoke). Against $192.06 remaining that leaves about $170. If only the 2,600 existing statements go to A4: worst $14.6.

## 4. Stop conditions and timeouts

* Every job: one ledger row (estimate, timeout_s, approver) before launch; session `max_seconds` = timeout_s above; `--confirm-launch`; approval file bound to design and plan hashes (n2_grid already refuses otherwise). Jobs over $5 need council; none here exceeds $5 individually, but the approval is for the set.
* Per generator smoke (40 gens, rounds outside the N2 sample): stop and drop the model if error rate > 20% in a batch, any cell has > 10% empty/truncated/think-leak/refusal/preamble outputs, near-duplicate rounds > 50%, deploy fails, or vLLM rejects the architecture. A dropped generator is logged and packets use the generators that exist (D31).
* Measured throughput replaces the assumption: if a model runs below 60% of the assumed tok/s, re-plan before the full run; if the re-planned worst case exceeds the table by 50%, ask the council again.
* Abort the whole extension if cumulative ledger spend reaches $40, or any single session passes its timeout. Hard stop for the project stays at the cap.
* After each session run `modal container list`; the earlier idle qwen container was not stoppable by the orchestrator (D33), so a human may need to stop leftovers.

## 5. Serving changes needed (details in N2_EXTENSION_PROPOSED_DIFF.md)

1. Five new `MODELS` entries in serve_vllm.py, with pinned revisions and the parser flags shown (`--language-model-only` for Ministral, `nemotron_v3` for Granite, `openai_gptoss` for gpt-oss). No image change.
2. Five rows in endpoints.json (resource fields must match, they set the booked price); `modal run ::download` then `modal deploy` per alias, then paste the URL.
3. n2_grid.py: three entries in `MODELS` (assumed throughput), separate `--tag`, new design hash and approval file. The scorer needs its own alias list for Granite and for the annotator; the frozen scorer manifest names Gemma as `scorer2`, so the A4 change must be recorded as a manifest version bump decided by the council (it does not alter the v2 primary scorer hash).
4. Harness: `chat_template_kwargs.enable_thinking=False` is sent to every model; Mistral, Phi, Olmo ignore it, but confirm no HTTP 400 in the smoke. The annotator needs `max_tokens >= 4096`.
5. Deployment for a gated Llama is not needed.

## 6. Alternatives

* Generators: Llama-3.1-8B-Instruct (Meta; gated but the token has access, config fetch 200; L40S, expected $0.43, worst $0.78; old, 8B, Llama licence terms). Granite-4.2-8B (L40S, about $0.5; use if Granite is made a generator and Phi-4 the scorer). Mistral-Small-3.2-24B (H100, 48 GB weights do not fit an L40S). Olmo-3-7B-Instruct (L40S, cheap). Apertus-v1.5-8B (Swiss AI; gated "auto", **token gets 403** until terms are accepted on HF: NEEDS-HUMAN). Llama-3.3-70B still 403. gpt-oss-20b as generator is not advised: reasoning cannot be turned off, so the N2 prompts differ from the other models.
* Scorer: Phi-4 (swap with Granite roles), or Llama-3.1-8B (cheap, weaker JSON follower).
* Annotator: gpt-oss-20b on L40S (cheaper, weaker). Do not use Llama-3.1-8B as annotator if it is also a generator.

## 7. Trade-offs and risks

* Everything about the new models' speed, cold start, VRAM fit and parse behaviour is an assumption until their smoke runs. Olmo-32B on H200 and gpt-oss on H100 are the least certain (memory and MXFP4 kernel support).
* Generator sizes are mixed (14B, 14B, 32B) against 12B and 27B, so "generator" is confounded with family; the split-by-generator reporting in D31 edit 3 already handles this.
* A weaker or differently calibrated A4 scorer changes agreement with the primary scorer by itself; report agreement per generator.
* Phi-4's 16k context limit also applies to the scorer if it is reused.
* The N2 cap margin is small; the cap, not the global budget, is the binding constraint.
