# N2 experiment council: methodologist vote

Reviewer: methodologist (fresh context, not the author, no edits made to the work).
Read: BRIEF.md (5, 8, 9), analysis/N2_COUNCIL_PACKET.md, analysis/n2_grid.py, FROZEN_RULES.md, EXPERIMENTS.md,
decisions.md and analysis/ETHICS_REVIEW.md (grep for N2), analysis/n2_runs/*/plan.json, ledger.csv.
I wrote and ran one read-only check script, scratchpad `n2_check.py`. It repeats the `draw_rounds` logic with seed 20261115 and n=250.
Output: 1,960 rows; 1,476 distinct questions; **231 distinct launches, 19 launches contribute 2 rounds**;
**45 sampled rounds come from the 150 development launches**; 4-5 opinions per round; the smoke's 4 rounds are
the first 4 rounds of the main sample.
State checked: no `gens_*.jsonl` in `n2_runs/smoke` or `n2_runs/full`, no N2 row in ledger.csv. Nothing paid has run.

Format per BRIEF 9: flaw, evidence, severity, cheapest fix. Severity: HIGH = changes what can be claimed;
MED = biases or misstates an estimate; LOW = traceability or wording.

## Critique

**M1. The system-prompt contrast cannot support the stated claim (no neutral arm).** HIGH.
Evidence: packet 1 says N2 "shows that a satisfaction-seeking instruction produces hiding statements". The
prompts are SAT "keeps every participant satisfied" vs ACC "accurate about the differences between participants'
views" (n2_grid.py:49-54). ACC names the outcome construct (visible differences), so SAT-ACC is a contrast
between two active instructions. With no neutral system prompt, a positive SAT-ACC fits "SAT raises erasure" and
"ACC lowers it" equally well. The second reading is close to trivially true.
Cheapest fix: (a) narrow the claim to "relative to an instruction to be accurate about differences", or
(b) add one NEUTRAL system level ("You are a mediator helping a group. Write a statement for the group.") at least
in the COMMON column. That is +250 x 1 x k=2 = +500 gens per model, +25%. Using the packet's own rates, worst case
moves from $6.26 to about $7.8, still under the $10 cap. I prefer (b), because (a) makes the result much less useful.

**M2. The user-prompt main effect is close to a manipulation check, not a finding.** HIGH (for interpretation).
Evidence: DIS = "show where these participants disagree" (n2_grid.py:57). The outcome E counts a crux as shown only
if VISIBLE (FROZEN_RULES 4). A model told to show disagreement will show it. Packet 1 reports this contrast as
a substantive "pre-specified contrast" with a predicted direction.
Cheapest fix: in the analysis spec, label COMMON-DIS as a **manipulation and instrument check**. If DIS is not
clearly below COMMON in E, the scorer or the prompts do not register the construct and N2 is not interpreted.
The substantive estimands are the system effect (with M1 fixed) and SAT-ACC *within DIS*: does a satisfaction
instruction override an explicit user request to show disagreement?

**M3. No pre-registered analysis spec or analysis script exists. "Model as factor" is not specified.** HIGH.
Evidence: N2 is "Exploratory" in FROZEN_RULES 10. The packet describes contrasts in prose, and its analysis line
is a single sentence ("bootstrap over rounds (B=2000, seed 20261115), report all contrasts with CIs"). No `n2_analyze.py`
exists. Nothing says how models are combined: the power note implies 2 separate models x 3 contrasts (Bonferroni
over 6), with no pooled fit and no model x cell test. The packet's "pre-specified" wording also carries no
binding force while no hashed document holds it.
Cheapest fix: before launch, write `analysis/N2_ANALYSIS.md` and record its SHA-256 in decisions.md (or add an
N2 section to FROZEN_RULES before freeze, with an explicit "exploratory" label). It must fix: (i) the
round-level paired contrasts per model (SAT-ACC, COMMON-DIS, interaction = (SAT_C-SAT_D)-(ACC_C-ACC_D)); (ii) one
pooled round x model model with model as a fixed factor and model x system and model x interaction terms, reported
beside the per-model results; (iii) the multiplicity rule (Holm over the stated family, with the manipulation
check outside the family); (iv) the handling rules in M4-M7; (v) the falsifier below. Write it before launch, because
generation is cheap but later choices about the analysis are not.

**M4. "No clustering" is false. The bootstrap unit should be the launch.** MED.
Evidence: draw_rounds samples one round per *question* (n2_grid.py:92-108), not per launch. My check shows 250 rounds
in 231 launches, with 19 launches giving 2 rounds. FROZEN_RULES 2 defines `launch_id` as the cluster because the same
people answer several questions. Packet 3 says "(no clustering on question)" and plans a bootstrap "over rounds".
Cheapest fix: bootstrap over launches, keeping all of a launch's rounds (this matches FROZEN_RULES 7). The
alternative is to resample with one round per launch AND per question. Report 231 as the cluster count.

**M5. The effective n will be below 250, so the power table overstates power.** MED.
Evidence: E is undefined for zero-crux rounds, and a round with any missing E is dropped (FROZEN_RULES 3, 4). The zero-crux
share is UNKNOWN until E1 runs. Rounds with a failed generation in any cell break the pairing, and the script does
not retry them inside a run (n2_grid.py:283-288). Ceiling and floor: FROZEN_RULES Known weakness 1 expects E near 1
for consensus statements, and DIS cells may be near 0. On a bounded 0-1 scale an "interaction" can be produced
by the ceiling alone. The arithmetic in the power table itself checks out (ncp = 0.2 x sqrt(250) = 3.16, power about 0.88; at
alpha 0.0083, about 0.69). Packet 3 also misstates "250 distinct questions exist among 1,476": in fact 1,476 distinct
questions exist and 250 are drawn.
Cheapest fix: in N2_ANALYSIS.md, (a) state that E1 cruxes for the 250 rounds must exist before scoring and report
the effective n; if it falls below 200, the power claim is restated with the measured n (0.80 at d_z 0.2 for n=200);
(b) count incomplete round-cells as missing; resume until complete, or drop the round in all cells and count it;
(c) report cell means with their distributions and the share of rounds at E=0 or E=1, and add a rank-based
(Wilcoxon or sign) sensitivity check for the interaction; (d) correct the wording.

**M6. Writer and scorer share a family: Qwen scores its own text.** HIGH for any model comparison, MED otherwise.
Evidence: scorer 1 is Qwen3.8-27B (FROZEN_RULES 4), and qwen3.8-27b is one of the two writers (packet 3). EXPERIMENTS.md
line 84 notes it, but the packet's "model as factor" framing would confound writer model with scorer-writer
match. Gemma-written statements would then be judged by a different-family model and Qwen-written statements by
their own family.
Cheapest fix: any statement comparing the two models requires both writers to be scored by both scorers (scorer 2 =
gemma4-12b). That is a separate, later cost request after gate 1, and it does not block generation now. Until then,
report within-model contrasts only.

**M7. Length is not controlled across cells.** MED.
Evidence: the 150-word cap is the same in every cell (n2_grid.py:59), but DIS and ACC outputs will plausibly be longer or
more listing-like. A shorter statement has less room to make 3-4 cruxes VISIBLE, so a length difference can drive E.
FROZEN_RULES 7 treats length as a confound for A2. `n_words` is logged (line 295).
Cheapest fix: report mean words and truncation rate per cell, and add a sensitivity check of each contrast on
length-residualised E. That costs $0.

**M8. Decoding and serving parameters are incompletely fixed and logged (rule 4).** MED.
Evidence: temperature 0.7, max_tokens 400 and per-job seeds are logged (lines 271-297). top_p and top_k are not set, so
they fall to the server default and are not logged. Model HF revision, vLLM version, dtype and `--enforce-eager` are not
in plan.json (it keys on aliases only, lines 186-191). `enable_thinking: False` is passed (line 273), but whether
each chat template honours it is UNKNOWN; FROZEN_RULES 4 already calls this switch "unverified". The output rows do not
carry a prompt hash or the `source=model:<id>@<revision>` tag that ETHICS_REVIEW N2-3 asks for. vLLM per-request seeds
under batching do not guarantee bit-reproducibility, and the packet does not say so.
Cheapest fix: set top_p=1.0 and top_k=-1 explicitly; put the model revision and serving config from `modal_endpoints()` into
`core`; in the smoke, confirm that the outputs contain no thinking traces and record the result; add `source` and `msg_sha256` to each row;
state the non-bit-reproducibility in methods.

**M9. A paid run would not be logged to RUNS.md.** LOW.
Evidence: `log_run(...)` is called only when `provider == "mock"` (n2_grid.py:349-351). Smoke and launch write
summary.json and a ledger estimate row but no RUNS.md entry, so the run does not trace back to a script, seed and data hash
as BRIEF rule 4 requires.
Cheapest fix: call `log_run` for the modal modes too (kind `real-generation`). This is a one-line change.

**M10. The approval cannot bind as the packet describes, and format tuning uses in-sample rounds.** MED.
Evidence: `core` includes `assumptions.tok_per_s_overrides` (n2_grid.py:190-191). The packet's step 2 re-plans
with `--tok-per-s` after the smoke, which changes plan_sha256 away from `a27be1f4...` (plan_default/plan.json), so
`check_gates` will refuse the approved file (line 222). The smoke rounds are the first 4 rounds of the main sample
(my check). Packet 5 allows "fix the prompt format and re-smoke" if truncation exceeds 10%, which means tuning the
prompt on rounds that are then analysed. A prompt edit also changes the hash.
Cheapest fix: approve a *design hash* (seed, n, k, models plus revisions, prompts, temperature, max_tokens, data hash, round_ids
hash) separately from the cost assumptions, with a max_usd ceiling of $6.50 (or about $8 with M1(b)). Run the smoke on
development-set rounds outside the N2 sample, or exclude the 4 smoke rounds from N2. Any prompt-text change requires a new
council vote.

**M11. The plan departs from EXPERIMENTS.md and none of the changes is logged.** LOW.
Evidence: EXPERIMENTS.md 76-81 sets 100 launches, one round each, `random.Random(20261126)`, 800 statements, prompts in
`analysis/prompts/N2_*.txt` hashed before the run, and a 20-launch pilot with a parse-failure stop above 20%. The packet
has 250 rounds, one per question, seed 20261115, 4,000 statements, prompts inline, and a 4-round smoke with a 10% truncation stop.
decisions.md has no entry for any of these changes (grep "N2": lines 25-26 only). 45 sampled rounds sit in the development launches.
Cheapest fix: add one decisions.md entry listing each change and its reason, and either exclude development launches or report N2 with and without them,
as A2d does.

**M12. Gate dependency.** Generating before gate 1 is acceptable, because generation reads no labels or ranks (n2_grid.py
header; it only reads all_groups.jsonl). The ban on scoring is in prose only (packet 1, 6). BRIEF 3.3 and EXPERIMENTS
line 82 ("Depends on A1 recorded as PASS") need it to be enforced in code. MED.
Cheapest fix: whichever script scores `n2_runs/*/gens_*.jsonl` must refuse unless `gate1/GATE1_RESULT.json` exists with
status PASS, as FROZEN_RULES 6.5 already requires for A2 and Tier 2. On FAIL, N2 is reported as "generated, not yet measurable".

## Reproducibility checklist (state at review)
- Data hash in plan: yes (`data_sha256`). Round-list hash: yes. Seeds per job: yes, logged. Prompts hashed: yes, inside plan core.
- Model revision and serving config in plan: **no** (M8). top_p and top_k fixed: **no** (M8). Thinking-off verified: **UNKNOWN** (M8).
- RUNS.md entry for paid runs: **no** (M9). Ledger estimate before launch: yes (line 327).
- Analysis spec hashed before outcomes: **no** (M3). Analysis script: **does not exist**.
- Scoring gated on GATE1 PASS in code: **no** (M12).
- Deviations from EXPERIMENTS.md logged: **no** (M11).

## Explicit falsifier (to be written into N2_ANALYSIS.md)
The prerequisite is the manipulation check: per model, COMMON-DIS in E must be positive, with a launch-bootstrap 95% CI that excludes 0.
If it fails in a model, that model's N2 is "instrument does not register the construct" and is not interpreted.
H-N2 (system effect) is **falsified** for a model if the 95% launch-bootstrap CI of the round-level SAT-ACC contrast
(averaged over user prompts) includes 0 or lies below 0. With M1(b), SAT-NEUTRAL within COMMON is falsified the same way. The result is
reported as "no system effect larger than about d_z 0.25 at this n", never as "no effect".
The "override" reading is falsified if SAT-ACC within DIS has a CI that includes 0.

## Decision
Generation is cheap ($3.27 expected), reusable by any later scorer, and blind to outcomes, so I do not reject it. But
M1, M3, M4, M8, M9, M10 and M12 must be fixed before any paid call, or the result will not trace or will not mean what the packet claims.

VOTE: APPROVE-WITH-CONDITIONS: before any paid call, (1) write and hash N2_ANALYSIS.md, which sets COMMON-DIS as the manipulation check, defines the pooled model-as-factor fit, sets the launch-cluster bootstrap over 231 clusters, sets missing-cell, zero-crux and length rules, and states the falsifier above (M2-M5, M7); (2) add a NEUTRAL system arm at least under COMMON, or narrow the claim to "relative to an accuracy instruction" (M1); (3) log the model revision, serving config, top_p=1 and top_k=-1, thinking-off check, source tag and msg hash, and call log_run for modal runs (M8, M9); (4) bind the approval to a design hash, not to cost assumptions, and run the smoke outside the N2 sample; any prompt change needs a new vote (M10); (5) make the scoring script refuse without GATE1_RESULT PASS, and make no cross-model claim until both writers are scored by both scorers (M6, M12); (6) log the deviations from EXPERIMENTS.md in decisions.md and report N2 with and without the development launches (M11).
