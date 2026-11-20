# N2 extension council: SKEPTIC vote

Reviewer: skeptic (fresh context, not the author, does not edit the work). Date 2026-11-16.
Read: BRIEF.md 3-5, 8-9; decisions.md D31, D33, D34; analysis/N2_EXTENSION_COUNCIL_PACKET.md;
analysis/N2_EXTENSION_PROPOSED_DIFF.md; analysis/N2_ANALYSIS_SPEC.md (incl. amendment 1);
analysis/council/N2_vote_*.md; FROZEN_RULES.md (scorer rows, A4 row). External evidence read today:
HF model cards for Olmo-3.1-32B-Instruct, phi-4, granite-4.2-30b, Ministral-3-14B-Instruct-2512-BF16;
HF dataset cards allenai/Dolci-Instruct-DPO and allenai/Dolci-Instruct-SFT; arXiv 2412.08905 abstract.
I did not verify vLLM 0.32 registry support or any throughput figure; nothing was run.

Format per BRIEF 9: flaw, evidence, severity, cheapest fix.

## F1. Olmo-3.1-32B-Instruct is partly Qwen-distilled and partly gpt-oss-distilled
- Evidence: the Olmo-3.1-32B-Instruct card lists Dolci-Instruct-DPO as its DPO data. The
  Dolci-Instruct-DPO card describes "125,000 pairs created with the preference heuristic described in
  Delta Learning"; the visible rows are `qwen3-no_reasoning-32b` chosen vs `qwen3-no_reasoning-0.6b`
  rejected. Other chosen models include `qwen3-no_reasoning-14b/4b/1.7b`, `qwq-32b`,
  `qwen3-coder-no_reasoning-30b-3a` and `gpt-120b`. Dolci-Instruct-SFT includes "WildChat with upgraded
  responses from GPT-4.1". So Olmo's preference tuning pushed it toward Qwen3 outputs, and toward
  gpt-oss-120b outputs (I read `gpt-120b` as gpt-oss-120b; the dataset card does not expand the name).
  Qwen is the primary scorer and gpt-oss-120b is the proposed annotator. This is the self-preference
  route that D34 ("no judge shares a family with any generator") and my N2 F1 were meant to close. The
  packet's "all different families" rests on vendor names, not on model lineage.
- Severity: HIGH for the claim that the generators are independent of the judges. Low cost impact.
- Cheapest fix: replace Olmo with Llama-3.1-8B-Instruct, which is already in the packet's alternatives
  (Meta, token has access, L40S, worst $0.78 against Olmo's $2.66). That also removes the riskiest
  deployment (H200, about 7 GB KV headroom on H100). Fallback if the council keeps Olmo for size
  coverage: label it "Qwen-/gpt-oss-distilled at DPO" in every table, make the Granite A4 score the
  primary read for Olmo outputs (primary-scorer read beside it), and exclude Olmo items from the
  author-vs-LLM agreement figure (or report that figure with and without them).

## F2. Phi-4 has OpenAI-teacher lineage, and the annotator is OpenAI
- Evidence: arXiv 2412.08905 says earlier Phi models "largely distill the capabilities of a teacher
  model (specifically GPT-4)" and that phi-4 "surpasses its teacher model". The phi-4 card does not
  name the model that generated its synthetic data. gpt-oss-120b is a separately trained OpenAI model,
  so the lineage overlap is weaker than in F1.
- Severity: LOW-MEDIUM. Only about 2-3 of the 12 N2 packet items will be Phi-4 outputs, and the
  annotator check is supplementary.
- Cheapest fix ($0): keep Phi-4. Report author-vs-LLM agreement with and without Phi-4 (and Olmo, if
  kept) items, and disclose the teacher lineage in the limitations.

## F3. Granite's JSON reliability: the proposed reasoning-parser setup is the main risk, and the test is too small
- Evidence: the granite-4.2-30b card says thinking is on by default, recommends a custom
  `granite_thinking_parser` (vLLM v0.20+), and says `nemotron_v3` "works". The proposed diff turns on
  `--reasoning-parser nemotron_v3` and also sends `enable_thinking=False`, so the template closes the
  think block inside the prompt. With a reasoning parser on and no end-of-think token in the output,
  vLLM can route the whole completion to `reasoning_content` and leave `content` empty, or apply the
  `json_object` constraint late. Either way every call would come back as a parse failure. The card
  reports no JSON or IFEval score; IFBench is 77.17.
  The acceptance test is "0 parse failures on 60 + 12 items". 0/72 still allows a true failure rate of
  up to about 4% (rule of three). The primary scorer had 0 failures on its validation set but 123
  label failures in 7,840 statements in full A2 (D32). `json_object` checks JSON syntax, not schema;
  missing crux IDs pass it.
  The packet's fallback scorer (Phi-4) is now a generator, so there is no pre-agreed fallback.
- Severity: HIGH. If Granite fails, A4 is useless and there is no plan B.
- Cheapest fix: (a) deploy the scorer WITHOUT a reasoning parser (thinking off needs none); test the
  parser variant only if the plain variant leaks think text. (b) Run the smoke on development-launch
  rounds: at least 200 label calls plus their extractions, from rounds excluded from gate 1 and from N2.
  Accept if the schema-valid rate (every extracted crux labelled, allowed labels only) is at or below
  the primary scorer's A2 failure rate plus 1 percentage point, and no think text appears in `content`.
  (c) Pre-name a fallback: Granite-4.2-8B (same family, still distinct from every generator). Its
  weaker scores are a reported limitation, not grounds to change family.

## F4. A4's main job, A2 refit with scorer 2, is not costed
- Evidence: FROZEN_RULES (A4 row) defines A4 as "A2 refitted with scorer 2's own E (own cruxes, own
  labels)" on the A2 rounds. A2c also uses scorer 2 for clarity ratings. The packet costs Granite only
  on N2 statements and the gate set. A2 with Qwen on H100 cost $2.453 for 7,993 calls (worst $5.154).
  At the packet's assumed 0.244 s/call that scales to about $2.8 expected, worst about $5.9. A single
  job worst case above $5 needs a council vote (BRIEF 8). FROZEN_RULES line 78 still names Gemma as
  scorer 2.
- Severity: MEDIUM. This is a process gap, and the set total is understated by about $6.
- Cheapest fix ($0 now): amend the FROZEN_RULES scorer-2 row (Gemma -> granite4.2-30b with pinned
  revision) BEFORE the first-pass label file arrives, and log it in decisions.md. Note that FROZEN_RULES
  line 3 still names L1.csv/L2.csv as the freeze trigger, while D34 uses labels/author_pass1.csv; fix the
  trigger name in the same edit. Bring the A2-refit A4 job, with its own plan hash, to the council
  after the Granite smoke has measured s/call.

## F5. Blinding and the "no N2 scoring before gate 1" rule are not sequenced in the packet
- Evidence: the packet lists A4 on about 2,600 existing N2 statements, A4 on all 5 generators, and
  "Qwen on 3,750 new statements" with costs but no timing. The only order it states is "Granite passes
  the gate items before any N2 scoring", which is a scorer-reliability condition, not the gate-1 rule.
  The Granite smoke ("40 gens equivalent") has no input set named. If it runs on N2 outputs, that is N2
  scoring before gate 1.
  Scoring the 60 + 12 gate items with Granite before labels exist is allowed as measurement (D31). But
  the scores must not reach the author-labeler, who is hypothesis-aware (D34).
- Severity: MEDIUM. It is a rule breach waiting to happen; the fix is cheap.
- Cheapest fix ($0): (a) no scorer (Qwen or Granite) runs on any N2 statement other than the 12 packet
  items until GATE1_RESULT.json records PASS; (b) Granite smoke inputs come only from development
  launches; (c) Granite's gate-item outputs are written to a sealed path, and nothing is printed to
  chat or logs the author reads, until pass1 is frozen; (d) N2 generation format checks stay automated
  counters only (as in my N2 condition 3).

## F6. Generator effects are confounded with size, vintage and recipe; per-generator validity is unmeasurable
- Evidence: the generators are Gemma 12B, Ministral 14B (a vision-language model run text-only), Phi-4
  14B (Dec 2024), Qwen 27B and Olmo 32B. The roughly 2.7x size spread is moderate, but five points
  cannot separate family, size, release date and post-training recipe.
  The 12 N2 packet items spread over 5 generators x 4 cells give about 2-3 items per generator. So
  "N2 VALIDATED" (D31 edit 2) can only be a pooled statement; scorer validity on Ministral, Phi or
  Olmo text is not tested per generator.
  The packet says "60 gate-1 statements"; D34 says 38 original + 12 N2 = 50 unique. One of the two is
  stale.
- Severity: MEDIUM for wording, LOW for running.
- Cheapest fix ($0): call each one a "generator" (never a "family effect" or "size effect"), report
  parameters and release date beside each per-generator row, make no regression on size, and say
  "scorer validity on N2 text was checked pooled over generators (n=12), not per generator".
  Reconcile 50 vs 60 before the A4 smoke uses the count.

## F7. Budget bucket for the primary-scorer cost is ambiguous; the N2 cap can be breached
- Evidence: N2 cap $10, $2.305 already spent. Generators worst $4.59 plus smokes $1.58 = $8.48. The
  primary scorer on the new statements (worst $2.64) is called "not an A4 cost" but is assigned to no
  line. If it is charged to N2, the total is $11.12, above the cap. A repeated smoke (the packet's own
  scenario) also exceeds it.
- Severity: LOW-MEDIUM. The global budget is ample; the risk is a launch refusal or an improvised cap
  change mid-run.
- Cheapest fix ($0): assign every job a ledger line before approval. Ask the human now for an N2 cap of
  $15; with the F1 Llama swap, worst-case generation falls by about $1.9, which also helps. The
  approval file binds each plan hash at its stated worst case (my N2 condition 1 carries over).

## F8. gpt-oss-120b is an acceptable annotator only with fixed settings
- Evidence: reasoning cannot be turned off (packet). `max_tokens >= 4096` and reasoning tokens share
  that limit, so a long-opinion item can return empty `content`. D34 requires "same instructions and
  blinding" and a fresh context. Lineage overlaps are covered in F1/F2.
- Severity: LOW.
- Cheapest fix ($0): fix `reasoning_effort` (state "medium") and `max_tokens` (8192) in advance. Make
  one call per item, with no shared context, and run the 20 repeats as separate calls in shuffled order
  so the LLM's own self-consistency is reported too. Count an empty `content` as missing, never retry
  it with a different setting. Never call it a human label.

## What holds up
Ministral-3-14B (Mistral base; the card names no external teacher) and Granite-4.2-30B (dense
GraniteForCausalLM; the card cites only "internally generated synthetic data") pass the lineage check
as far as their public cards go. Cost is not the issue: about $23 worst case including the A2-refit A4
against about $192 remaining.

VOTE: APPROVE-WITH-CONDITIONS: approve Ministral-3-14B, phi-4, granite-4.2-30b (A4) and gpt-oss-120b
(annotator); do NOT approve Olmo-3.1-32B-Instruct as an independent generator. Conditions:
(1) replace Olmo with Llama-3.1-8B-Instruct (or keep Olmo only under the F1 fallback: lineage
disclosed, A4 as its primary read, and excluded from the annotator-agreement figure);
(2) Granite is deployed without a reasoning parser and passes a development-launch smoke of at least
200 label calls (schema-valid rate within 1 pp of the primary's A2 rate, no think text in content);
Granite-4.2-8B is the pre-named fallback;
(3) the FROZEN_RULES scorer-2 row and freeze-trigger file name are amended and logged before
author_pass1.csv arrives;
(4) no scorer touches any N2 statement other than the 12 packet items before GATE1_RESULT.json records
PASS; smoke inputs come from development launches only; Granite gate-item outputs stay sealed from the
author;
(5) every job has a ledger bucket; ask the human for an N2 cap of $15; the A2-refit A4 job comes back
to council with its own plan hash;
(6) wording: say "generator", not "family" or "size" effects; N2 validity is pooled over n=12;
Phi-4's and Olmo's lineage go in the limitations; gpt-oss settings are fixed in advance, one call per
item.
