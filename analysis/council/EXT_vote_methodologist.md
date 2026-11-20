# EXT vote: methodologist (N2 extension: 3 generators, A4 scorer, LLM annotator)

Written blind: I did not read EXT_vote_costcutter.md or any other member's vote on this item. Read: BRIEF.md §5, §8-9, §11; decisions.md D20, D31-D34; FROZEN_RULES.md §1-§7.3; N2_EXTENSION_COUNCIL_PACKET.md; N2_EXTENSION_PROPOSED_DIFF.md; N2_ANALYSIS_SPEC.md (incl. Amendment 1); n2_grid.py.
Measured by me (form counters only; no score, rank, rating or label opened): prompt and output token counts from `n2_runs/full_k1/gens_*.jsonl` `usage` fields and `n_words`. `labels/` exists and is empty (0 files), so FROZEN_RULES is not frozen yet.

## Measured facts used below

| fact | value | source |
|---|---|---|
| N2 prompt length (system + user, as tokenized by the server) | max 740 tokens (gemma), 735 (qwen); median ~465; p99 ~710 | `full_k1/gens_*.jsonl` field `usage.in`, 1,250 rows each |
| N2 completion length | max 181 tokens (gemma), 246 (qwen); 0 truncated; all `finish_reason=stop` | same files |
| Over 150-word cap | gemma 0% in all cells; qwen 27.2-41.2% per cell, max 185 words | same files, `n_words`; matches `overcap_report.json` |
| Prompts are model-independent | `build_messages(g, cell, seed)` uses only round, cell, seed; opinion order seeded by round | `n2_grid.py:189-195` |
| Per-job seed includes the model alias | `sub_seed(seed, jid)`, `jid = model|round|cell|sample` | `n2_grid.py:227-230` |
| Spec text still says k=2 averaged; run was k=1 | spec §1 vs D20 (k=1 fallback approved) | `N2_ANALYSIS_SPEC.md:14`, decisions.md D20 |
| Spec's primary read is cross-scoring with Gemma as scorer 2 | "PRIMARY read: cross-scored cells (qwen text by scorer 2, gemma text by scorer 1)" | `N2_ANALYSIS_SPEC.md:42-45` |
| Spec multiplicity family | 5 contrasts x 2 models = 10 tests, Holm | `N2_ANALYSIS_SPEC.md:34` |
| Primary scorer parse record | 3 extraction failures; 123 label parse failures on 7,840 statements | decisions.md D32 |
| Packet claims about the same scorer | "0 parse failures in scorer v2" | packet line 31 |

## Critique (flaw / evidence / severity / cheapest fix)

**M1. The hashed analysis spec does not describe the extended design; its primary read is now impossible.**
Evidence: spec §4 names Gemma as scorer 2 and makes cross-scoring (Qwen text by Gemma, Gemma text by Qwen) the primary read (`N2_ANALYSIS_SPEC.md:42-45`). D31 edit 3 / D34 item 5 remove Gemma as A4 scorer. With Granite as A4, Qwen-generated text is scored by Qwen (self) under the only gate-validated scorer, and by Granite (cross) under an unvalidated one. Spec §3, §7 say "2 models".
Severity: HIGH (blocks honest analysis; any rule chosen after N2 scores exist is a forking path).
Fix: Amendment 2 to the spec, hashed in decisions.md BEFORE the extension generation runs (at the latest before any N2 scoring). It must fix: (a) primary scorer = Qwen (scorer 1) for all 5 generators; the Qwen-generator column is labelled "self-scored" everywhere; (b) Granite = A4 robustness read on all 5 generators, generator x scorer interaction reported; a contrast that holds only under Qwen on Qwen text is labelled as such; (c) k=1 (correct the stale k=2 text); (d) claim scope "five open-weight instruction-tuned models, 12-32B" (no "current models", no family claims).

**M2. Multiplicity is undefined for 5 generators.**
Evidence: family = 10 tests over 2 models (spec:34). Naively extending to 25 tests: at n=250 paired, d_z 0.20, ncp = 0.20 x sqrt(250) = 3.16; the strictest Holm step (alpha 0.002, z 3.09) gives power about 0.53 (normal approximation; my arithmetic, not a run).
Severity: HIGH.
Fix (pre-registration-preserving): keep the hashed 10-test family for Gemma and Qwen unchanged; declare the 3 new generators a SECOND family of 15 tests (C1, C2, C3, C4a, C4b x 3), Holm within it; the pooled-over-5 estimates are descriptive, not tested. Per-generator nulls are worded "not detected; MDE at effective n = ..." per spec §6. Do not let any per-generator result be promoted by being the one that survives.

**M3. Generator is confounded with family, size, release date, and with fit to the shared decoding.**
Evidence: 12B, 27B, 14B, 14.7B, 32B; Phi-4 Dec 2024 vs Granite Aug 2026 (packet table and line 25). The shared temperature 0.7 / top_p 1.0 (`n2_grid.py:89-90`) is off the vendor default for some of these models (vendor recommendations not verified here: UNKNOWN), so "generator" also absorbs decoding mismatch. Qwen already breaks the length instruction in 27-41% of outputs; new models may break it more or less.
Severity: MEDIUM.
Fix: keep decoding identical (this is the right choice for a within-generator manipulation); state in the spec that between-generator differences in E levels are descriptive only and never attributed to family or size; report over-cap rate per generator-cell and run each contrast on the all-cells-under-cap subset (already Amendment 1; extend to all 5). Length covariate centred within generator (Amendment 1 wording generalises; say so explicitly).

**M4. "Same design" is asserted, not checked.**
Evidence: same prompts are guaranteed by code (`n2_grid.py:189-195`), but the extension runs under a new design hash and plan (proposed diff §3), and chat templates differ per model (Ministral is served as a multimodal architecture with `--language-model-only`, no `--tokenizer-mode` set; Olmo injects a default system prompt only when none is given; Granite thinking default on). `msg_sha256` hashes the message list, not the rendered prompt.
Severity: MEDIUM.
Fix: before the full run, a script check that (i) `round_ids_sha256` of the extension plan equals full_k1's; (ii) the set of `msg_sha256` per (round, cell) is identical across all 5 generators; (iii) one rendered prompt per model per cell (vLLM `/tokenize` or the template rendered offline) is saved and shows the system prompt in the system slot, no injected vendor system prompt, no think block. Fail -> stop, no "fix" that touches prompt text. Serving-only fixes are logged as fix-and-resmoke (`n2_grid.py:99`).

**M5. Phi-4 16k context is not a constraint for N2; the packet overstates prompt size.**
Evidence: packet line 25 says prompts are "about 2k tokens"; measured max is 740 tokens (above). `max_tokens` 400 leaves >15k headroom on all 16,384-token servers. Scorer extraction prompts include the same opinions plus E1 instructions; they will also be far below 16k, but this was not measured for Granite's tokenizer.
Severity: LOW.
Fix: none needed for generation. For Granite, log max extraction prompt tokens in the A4 smoke; FROZEN §3 drop-and-count rule applies if any round exceeds.

**M6. Missing-data rules give different round sets per generator.**
Evidence: spec §5 drops a failed round "in ALL cells for that model" and zero-crux rounds per scorer; with 5 generators and 2 scorers, the effective rounds differ by generator and scorer.
Severity: LOW-MEDIUM (pooled estimates mix different rounds).
Fix: per-generator estimates on their own complete rounds (as now); pooled descriptive estimates on the intersection of rounds complete for all generators under that scorer; report both n's.

**M7. A4 (Granite) has no validity requirement except parse success, and the parse bar is internally inconsistent.**
Evidence: packet line 31 requires 0 parse failures and cites "0 parse failures in scorer v2", but D32 records 123 label parse failures and 3 extraction failures for scorer v2. A JSON-following criterion is also not a validity criterion.
Severity: HIGH (A4 would be reported as a robustness check with no evidence it measures the construct).
Fix: pre-specify, before freeze (labels/ is empty, so FROZEN §4 "Scorer 2" row can still be edited with a decisions.md entry), all of:
1. Manifest version bump: Granite repo + revision, E1/L1 byte-identical to Appendix A (hash match), temperature 0, seed 0, max_tokens 700/300, thinking off; record the actual thinking state from the smoke (`reasoning_content` empty, no think tags, `content` non-empty in 100% of smoke calls; the `nemotron_v3` parser must not move the answer out of `content`).
2. Format bar = parity, not zero: per-step parse-failure rate on the development smoke no worse than scorer 1's (extraction 3/1,960; labelling 123/7,840 = 1.6%) plus one retry with seed 1 as FROZEN §4. Fail -> A4 dropped and reported; no prompt edits for Granite.
3. Human validity, reported with no rescue: Granite balanced accuracy vs the author's first-pass labels on the gate set with the same bootstrap and seed (FROZEN §6.4 "the same for scorer 2"), plus the BA_crux/BA_sh rows of §6.4a. Pre-registered consequence: if Granite's gate LB <= 0.5, every Granite-scored number is labelled "second scorer not validated against the human labels" and cannot support or contradict a claim.
4. Agreement with scorer 1: kappa on the binary call (E >= 0.5) and Spearman of E, on the gate items, the 12 N2 items, and on N2 text per generator (packet line 91 already asks per generator; make it binding).
5. Zero-crux rate and label shares per generator-cell for both scorers, reported side by side (a scorer that finds no cruxes cannot register hiding).

**M8. LLM annotator protocol is under-specified in exactly the places that allow tuning.**
Evidence: proposed diff §5 says reasoning effort "low"/"medium" "if needed"; no temperature or seed; packet line 61 adds a "12-item check first" without saying what it checks. gpt-oss cannot switch reasoning off (packet line 27).
Severity: MEDIUM-HIGH (if the 12-item check compares against the author's labels and settings are then chosen, the supplementary agreement is tuned on the outcome).
Fix, fixed in writing before the annotator's first call:
1. Inputs identical to the human packet: the verbatim FROZEN §5 instructions (the D34 single-labeler version), `item_id`, question, numbered opinions, one statement. Never: scores, crux lists, the author's labels or `main_disagreement`, model, cell, provenance.
2. One item per call, fresh context (no packet-level batching; otherwise it sees other candidates).
3. Fixed settings: reasoning_effort "medium", temperature 0, seed 0, max_tokens 4096; answer read from `content` only. If the format check shows looping or truncation at temperature 0, the pre-registered fallback is temperature 1.0, seed 0. Nothing else may change.
4. The 12-item pre-check is format-only (parse rate, truncation); it is not compared with any human label.
5. Labels parsed with the FROZEN §5 exact-token rule; an invalid answer gets one retry (seed 1), then is recorded INVALID and counted; never coerced.
6. Repeats: the 20 repeated items are sent again as fresh calls with seed 1; LLM self-agreement is reported but never placed beside the human self-consistency kappa as if comparable.
7. Comparison: Cohen's kappa, three categories (HIDES / NOT_HIDING / UNSURE) as FROZEN §6.2, author first-pass vs annotator on the 50 unique items, bootstrap 95% CI (seed 20261116); plus the 4x4 table; plus the annotator's BA against the scorer as a third view. Labelled "LLM annotator, supplementary; not a human label". It never enters the gate, never adjudicates, never replaces or breaks a tie.
8. Sealing: the author is the only human and still owes pass 2. Annotator outputs stay sealed (not opened by anyone who will show them to the author) until `author_pass2.csv` exists; otherwise the self-consistency check is contaminated.

**M9. The 12 N2 packet items cannot be balanced across 25 generator x cell combinations, and they validate nothing per generator.**
Evidence: 5 x 5 = 25 > 12 (D31 edit 2, D34 item 1). With 2-3 items per generator, a per-generator validity statement has no support; the pooled 12-item BA rule (D34 item 3) can pass only if almost every item is right.
Severity: MEDIUM (the rule is the human's; the risk is over-claiming).
Fix: a seeded, outcome-blind allocation written before the extension outputs exist: generators get 3,3,2,2,2 items (which get 3 decided by the seed); cells get 3,3,2,2,2 the same way; no generator-cell pair repeats (a cyclic Latin-style assignment); each item from a distinct round and a distinct launch, outside the gate sample, the 150 development launches and the smoke rounds; within a slot the round is drawn by seed, not by any score or flag. A dropped generator: its slots are redistributed by the same seeded rule. Binding wording: "N2 validated on 12 items pooled over generators (2-3 per generator)"; no generator- or cell-level validity claim. Also disclose that the 12 items include Qwen-generated text scored by Qwen (self-scoring in the check). Note for the limitations: the author can probably tell N2 text from Habermas text by style (qwen over-cap in up to 41%), so "model/condition hidden" does not mean "provenance hidden".

**M10. "Different family" is not "independent".**
Evidence: Phi-4 was trained with large amounts of synthetic data from OpenAI models (public Phi-4 report; not verified here) and the annotator is OpenAI's gpt-oss; Olmo post-training may include traces from other open models (UNKNOWN, not checked).
Severity: LOW.
Fix: one limitations sentence; report annotator-vs-author agreement split by provenance (Habermas vs N2) only descriptively.

## Missing ablations / checks (cheap, all outcome-blind)
1. Per-generator manipulation check (spec §2) applies to each of the 5; a generator failing it is reported as such and excluded from interpretation.
2. Over-cap and truncation per generator-cell; under-cap subset analysis for all 5.
3. Rendered-prompt check per model (M4).
4. Scorer x generator table (2 scorers x 5 generators) of zero-crux rate, parse failures, E distribution, before any contrast is read.

## Reproducibility checklist
- [ ] Spec Amendment 2 written and its sha256 in decisions.md before the extension generation (M1, M2, M6).
- [ ] Extension plan.json: same seed 20261115, `round_ids_sha256` equal to full_k1; new design hash; approval file `council/N2_EXT_APPROVAL.json`.
- [ ] Pinned revisions (40-hex) for all 5 models in serve_vllm.py; endpoints.json resource fields match; vLLM image v0.32.0 recorded.
- [ ] msg_sha256 identical across generators per (round, cell); rendered prompt per model per cell saved.
- [ ] Decoding: temperature 0.7, top_p 1.0, top_k -1, max_tokens 400, thinking off, `--generation-config vllm`, per-job seeds as `sub_seed`; same for all 5.
- [ ] Smoke on the out-of-sample smoke rounds only; drop/stop rules as packet §4; serving-only fixes logged.
- [ ] scorer_manifest version bump for Granite before FROZEN_RULES freezes; FROZEN §4 scorer-2 row edited with a decisions.md entry.
- [ ] Annotator protocol (M8) written and hashed before its first call.
- [ ] 12-item allocation seed and rule written before extension outputs exist (M9).

## Falsifiers (any one stops or downgrades the extension)
1. Design falsifier: if `round_ids_sha256` differs from full_k1, or any (round, cell) has a different `msg_sha256` across generators, the extension is not the same experiment -> stop, no merge with the existing run.
2. Generator falsifier: a generator failing the per-generator manipulation check (spec §2) is "instrument does not register the construct" for that generator; if 2 or more of the 3 new generators fail, the paper may not say the instruction effect generalises across models.
3. A4 falsifier: Granite format parity fails, or Granite gate LB <= 0.5 -> A4 is reported as "not validated" and cannot carry or contradict any claim (M7).
4. Annotator falsifier: if any annotator setting is changed after the annotator's labels are compared with the author's, the annotator result is withdrawn.

## Verdict
The extension is methodologically sound in its core (same rounds, same byte-identical prompts, same decoding, form-only stop rules, out-of-sample smokes), and Phi-4's context is not a problem (measured max prompt 740 tokens). It is not runnable as specified because the hashed analysis spec still assumes two generators and Gemma as scorer 2, A4 has no validity bar, and the annotator protocol leaves tunable settings open.

VOTE: APPROVE-WITH-CONDITIONS: (1) Spec Amendment 2 hashed before extension generation: Qwen primary for all generators with the Qwen column labelled self-scored, Granite as A4 robustness with generator x scorer reported, k=1, original 10-test Holm family kept and a separate 15-test Holm family for the 3 new generators, pooled-over-5 descriptive only, length covariate centred within generator, intersection rule for pooled rounds, claim scope "five open-weight models" (M1, M2, M3, M6). (2) Design-identity check (round hash, msg_sha256 across generators, rendered prompts) passes before the full runs (M4). (3) A4 bar per M7: manifest bump before freeze, format parity with scorer 1 (not "0 failures"), Granite gate BA reported with the pre-registered "not validated" consequence, per-generator agreement with scorer 1. (4) Annotator protocol per M8 fixed in writing before its first call, including temperature 0 / seed 0 / reasoning medium, one item per call, format-only pre-check, sealed until author_pass2 exists, supplementary only. (5) 12-item seeded Latin-style allocation per M9 written before extension outputs exist, with pooled-only validity wording.
