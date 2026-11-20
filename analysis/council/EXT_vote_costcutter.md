# EXT council: cost cutter vote (N2 extension: 3 generators, Granite A4 scorer, gpt-oss annotator)

Read: BRIEF section 3 rules 5 and 8, sections 8 and 11, D13, D15, D31, D34, ledger.csv, COSTS.md, the packet, the proposed diff, serve_vllm.py header, N2_vote_costcutter.md. No paid runs, no edits outside this file.

## Arithmetic check

Prices re-derived from the packet's container rates (L40S 0.000665/s, H100 0.001344/s, H200 0.001508/s), worst = (timeout + 135 s tail) x rate:
- ministral 1,429 s x 0.000665 = 0.95. OK.
- olmo 1,761 s x 0.001508 = 2.66. OK.
- phi4 1,477 s x 0.000665 = 0.98. OK.
- A4 all five generators 3,544 s x 0.001344 = 4.76. OK. A4 gate set 536 s = 0.72. OK.
- Worst components sum to 17.09, matching the packet's $17.1. Packet is arithmetically sound.
- Global: ledger 7.944 + 17.1 = 25.0 of $200 (D13). Fine. Rule 5 text in BRIEF still says $150 and COSTS.md still says $150; D13 ratified $200. Fix COSTS.md (below).
- Anchors: measured Gemma-12B 1,250 gens cost $0.3645 and measured Qwen scorer 7,993 calls cost $2.453; the packet's expected figures for the new models ($0.52, $0.54) sit above the Gemma anchor, so they are not optimistic. Granite scorer 0.244 s/call vs Qwen measured 0.212 s/call is plausible.

## Flaws

1. **A4 on all 6,250 statements is not needed for any frozen claim.**
   - Evidence: D34 item 5: headline is the human-labeled sample; scorer rate is secondary. A4's job (D31 edit 3) is a family-independent check. The packet's own table has the full-scope A4 at worst $4.76 and expected $2.47, the biggest single item after generators.
   - Severity: medium (about $4.5 of the $17.1 worst).
   - Cheapest fix: run A4 on the gate set (72 items, worst 0.72) plus a stratified sample of about 1,000 statements (200 per generator incl. Qwen and Gemma, round-matched). Calls about 1,250, worst about (610+135) x 0.001344 = $1.00. Saves about $3.8 worst, about $1.9 expected. Per-generator agreement stays estimable. Full-scope A4 only if the sample shows a per-generator disagreement worth chasing (then a new ask).

2. **A4 smoke duplicates the gate-set run.**
   - Evidence: smoke row $0.75 (40 gens equivalent), gate-set row $0.72; both are cold start plus a few hundred calls on the same H100 app.
   - Severity: low ($0.75).
   - Cheapest fix: make the 72-item gate-set run the smoke. Pass criteria are already stated (0 parse failures on 60 + 12 items). Stop there if it fails.

3. **N2 cap margin is $1.5 and the packet leaves the cap question open.**
   - Evidence: N2 cap $10 (budget.py, section 11); spent 2.305; generators 4.59 + smokes 1.58 = 6.17; total 8.48. The packet also puts Qwen scoring of new statements ($2.64 worst) and A4 into the same extension, which is not counted against that margin. One repeated smoke or the Qwen scoring alone exceeds $10.
   - Severity: high (the harness refuses launch past the cap, or the agent is tempted to raise it ad hoc).
   - Cheapest fix: re-allocate now, exact numbers below.

4. **Olmo-3.1-32B on H200 is the single most expensive and least certain generator.**
   - Evidence: worst 2.66 + smoke 0.84 = 3.50 (57% of the generator worst) for one model; the packet says 7 GB KV on H100, fit unmeasured. A100-80 ($0.000694 GPU) is slower by roughly the bandwidth ratio, so $/run is about equal; FP8 on L40S (32 GB weights) changes the model and throughput is unknown. I found no GPU that is clearly cheaper and adequate.
   - Severity: medium.
   - Cheapest fix: keep H200, but smoke it last and only if Ministral and Phi-4 pass; cap the smoke at 32 gens with timeout 300 s (worst $0.6 instead of 0.84). If the council wants to cut, Olmo-3-7B-Instruct on L40S (packet: about $0.4) saves about $3 worst but changes the size confound; require a note in the limitations. Not a condition, an option.

5. **GPU choice for the others is adequate.**
   - Evidence: Ministral and Phi-4 bf16 are 28 and 29 GB, so L4/A10 (24 GB) do not fit; L40S at 48 GB is the cheapest fit. Granite 58.6 GB and gpt-oss 65 GB need 80 GB; H100 is the cheapest 80 GB card the harness prices (A100-80 is cheaper per hour but unmeasured with this vLLM image, and gpt-oss MXFP4 kernels are Hopper-oriented). Phi-4 as scorer on L40S is cheaper (packet: worst $3.84 vs $4.76) but removes it as generator.
   - Severity: none.
   - Cheapest fix: none; keep as proposed.

6. **Throughput is assumed for every model; the only protection is the smoke.**
   - Evidence: packet section 3 and 7. The N2 council condition 1 (at least 32 requests, report truncation) is the precedent.
   - Severity: medium.
   - Cheapest fix: carry over N2 conditions 1-5 verbatim to each new model (smoke >= 32 requests, replace assumed tok/s with measured, re-plan if below 60%, ceiling per stage). Replace each assumed `tok_per_s` in `MODELS` before the full run, and write a new design hash and approval file (the existing hash covers `models`).

7. **Timeouts: fine, but cold start is the unbounded part.**
   - Evidence: `startup_timeout=20*MINUTES` in serve_vllm.py. An unsupported architecture or a crash-looping vLLM can bill up to 20 min per attempt: 1,200 s x 0.001508 = $1.81 (H200), $1.61 (H100), $0.80 (L40S) per retry, which the session `max_seconds` may not cover if the server restarts the container. The packet admits none of the five architectures was verified in v0.32.0.
   - Severity: medium.
   - Cheapest fix: do a CPU-only or `--help`/registry check first if possible; otherwise smoke with `startup_timeout` 600 s on every new alias, and abort the stage on the first failed health check. Ledger the smoke worst case with one failed start included for Olmo (adds about $0.9).

8. **Container shutdown risk (precedent D33 / COSTS.md open items).**
   - Evidence: `modal container stop` was denied by the classifier; two `pilot-vllm-*` apps remain deployed. serve_vllm.py already sets `scaledown_window` 2 min, `min_containers=0`, max_containers=1, which is correct; the proposed endpoints.json rows repeat scaledown 120. Five new apps increase the number of H100/H200 containers that could linger. An idle H200 container for one hour is $5.43.
   - Severity: high if it happens (worst plausible, 5 apps lingering, is a few dollars per hour), low probability.
   - Cheapest fix: (a) every new alias must use the existing registry unchanged on scale-to-zero (`min_containers=0`, `scaledown_window<=120`, `max_containers=1`; reject any entry that deviates); (b) the run script ends with `modal container list` and a recorded result in decisions.md; (c) ask the human once, before launch, to allow `modal app stop pilot-vllm-<alias>` / `modal container stop` for these app names in the permission settings, since the classifier denied it before and the orchestrator must not work around that; (d) deploy and run one app at a time, stop it, then deploy the next (also keeps cold-start and spend attributable); (e) after the last stage, list deployed apps; undeployed or zero-container apps bill nothing.

9. **Rule 8: the serving diff edits ..\modal_serving, outside the project directory.**
   - Evidence: BRIEF rule 8 "Stay in the project directory"; the packet marks the edit NOT APPLIED. D13 only ratified the earlier harness edit, not new ones.
   - Severity: high (hard-rule breach if applied as drawn).
   - Cheapest fix: vendor. Copy serve_vllm.py and endpoints.json to `t3_1\serving\`, add the five entries there (additive only), record the SHA-256 of the original and the diff in decisions.md, and deploy from the copy (app names `pilot-vllm-<alias>` do not collide with the existing two). Needs a small harness switch (path to serving dir, `serving_info()` regex already parses the file text), so the harness change must also stay inside t3_1 (a vendored `serving_info` path argument, not an edit to `pilot_harness` outside). If the harness itself lives outside t3_1, the human must authorise that one edit as in D13, and the council should say so rather than bypass it. Do not touch the originals.

10. **The "$22 reserve" is a second buffer on top of worst-case reservations.**
    - Evidence: each worst figure is already 2x timeout plus tail; the packet then adds 30% (about $22). The harness charges worst case against the cap at reserve.
    - Severity: low (a planning figure, not spend).
    - Cheapest fix: ask for allocation of the worst case only (below); do not pre-book the extra $5.

11. **Annotator is fine on cost.**
    - Evidence: about 70 items, worst $1.19 plus 12-item check $0.70 = $1.9; the gpt-oss-20b fallback is in the same family as 120b only, so it is acceptable as annotator if A4 and generators exclude OpenAI, but it is weaker.
    - Severity: low.
    - Cheapest fix: run the 12-item check as the real first batch (not a throwaway) so its labels count if they pass; saves up to $0.7 worst. Require `max_tokens >= 4096` and a hard session timeout 750 s as stated.

12. **Stale documentation of the cap.**
    - Evidence: COSTS.md still says "$150 / It was $50" and the per-experiment table with 150.
    - Severity: low.
    - Cheapest fix: update the Caps section to $200 and the revised N2 cap below when the allocation is recorded.

## Revised worst case with fixes 1, 2, 4, 10

| item | packet worst | revised worst |
|---|---|---|
| generators (3 full runs) | 4.59 | 4.59 |
| generator smokes | 1.58 | 1.35 (Olmo smoke 32 gens, 300 s) |
| Qwen primary on 3,750 new statements | 2.64 | 2.64 |
| A4 gate set (acts as smoke) | 0.72 + 0.75 | 0.72 |
| A4 stratified sample ~1,000 | 4.76 | 1.00 |
| annotator | 1.9 | 1.9 (12-item check counts) |
| misc/downloads | 0.15 | 0.15 |
| total | 17.1 | about 12.4 |

Expected about $6.5 (packet expected 9.5 less about 1.9 for A4 scope, 0.75 smoke, rest rounding).

## Cap re-allocation (exact numbers, from the $70 reserve of D15; D13 puts the extra $50 into the "council-approved new experiment" pool, so either source is permitted, the reserve is cleaner)

N2 line (generators, N2 smokes, Qwen scoring of new statements, A4, misc), revised: 4.59 + 1.35 + 2.64 + 0.72 + 1.00 + 0.15 = **10.45** worst. Plus already spent 2.305 = 12.76.
- Recommended: raise the N2 cap from $10 to **$14** (+$4.00); reserve $70.00 to **$66.00**. Margin $1.24 over worst. The annotator ($1.9 worst) goes on the core/A1 line, whose cap is $10 and whose spend is 2.17 so far (A1 0.809, probe 0.711, infra 0.651); no transfer needed.
- If the council keeps the packet scope unchanged (full A4, separate smoke): N2 worst 15.35 + 2.305 = 17.66; raise the N2 cap to **$18** (+$8.00); reserve to **$62.00**; annotator still on the core line.
- Either way: write the change in decisions.md as a new D-entry and in `EXPERIMENT_CAPS_USD` in budget.py (a project file), update COSTS.md. Global $200 is not affected: projected cumulative about 7.944 + 12.4 = 20.3.
- Kill switch from the packet stays: abort the whole extension at $40 cumulative (about double the revised worst); any single stage over its worst reservation returns to the council. Do not add a stage cap above the numbers here.

## Verdict

The packet's costs are honestly computed, conservative, and the models are the cheapest adequate hardware I can substantiate. Approve with the cap moved, A4 scoped down, the serving diff vendored into the project, and shutdown handled before launch.

VOTE: APPROVE-WITH-CONDITIONS: (1) vendor serve_vllm.py and endpoints.json into t3_1\serving\ and do not edit ..\modal_serving (rule 8), logging the original hash and the additive diff; any harness change stays inside t3_1 or gets an explicit human OK as in D13; (2) raise the N2 cap from $10 to $14 (reserve $70 to $66) for the revised scope, or to $18 (reserve $62) if full A4 is kept, recorded as a decisions.md entry and in budget.py before any launch; annotator ($1.9 worst) booked to the core/A1 line; (3) restrict A4 to the 72-item gate set (acts as the smoke) plus a stratified ~1,000-statement sample; full-scope A4 needs a separate request; (4) every new alias deploys with min_containers=0, scaledown_window<=120 s, max_containers=1; a ledger row with estimate, timeout_s and approver before each launch; smokes of >=32 requests per model with startup_timeout 600 s, truncation and thinking-off reported, measured tok/s written back, re-plan below 60% of assumed, new approval hash for any re-plan, return to council if a stage worst case rises 50%; (5) one app at a time, stop it afterwards, `modal container list` empty and recorded in decisions.md after each stage, and the human asked once beforehand to allow `modal app stop` and `modal container stop` for pilot-vllm-* (the orchestrator does not work around a denial); (6) order smokes Ministral, Phi-4, Granite gate set, then Olmo (32 gens, 300 s timeout) last, dropping any model that fails the packet's stop rules; abort the whole extension at $40 cumulative; (7) update COSTS.md to the $200 cap.
