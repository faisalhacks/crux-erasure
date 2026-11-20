# ETHICS_REVIEW.md: ethics and dual-use review, T3-1 (all BRIEF section 5 experiments)

Reviewer: ethics and dual-use evaluator. I did not write any of this project's work and started with fresh context. Date: 2026-11-15.
Protocol (BRIEF section 9): each finding gives the flaw, the evidence, the severity and the cheapest fix. The review contains no praise. I edited none of the work.
Severity scale: **BLOCKER** (a hard rule would break, or the result cannot be published as is), **HIGH**, **MEDIUM**, **LOW**.

## 0. Inputs read, and what was missing

- Read: BRIEF.md (all of it, section 3 rule 6 in particular), decisions.md (D0-D7), status.md, INVENTORY.md, COSTS.md, ../epistemics/data_gates.md, data/habermas_repo/src/README.md, report/limitations_dualuse_draft.md, report/methods_draft.md (grep only), f_finetune/config.py, and pilots/T1_1/run_pilot.py (header only).
- **Missing: `FROZEN_RULES.md` and `EXPERIMENTS.md` do not exist in P.** BRIEF section 2 requires both. No design document exists for N2, N6, F or B beyond BRIEF section 5 and f_finetune/config.py, so I reviewed the designs as BRIEF section 5 states them.
  - **Consequence:** I **cannot confirm** that N6 uses only synthetic opinions. No N6 design exists to check (see N6-1).

### Measured evidence (my own read-only scans; no data modified)

The scan scripts are in my session scratchpad: `pii_scan.py` and `wid.py`. Both were run with `python -I` on `hm_all_candidate_comparisons.parquet` (sha256 `7cf8d5ce…`, per INVENTORY.md).

**Columns**
- 104 columns.
- **No demographic columns.** A name search for age, gender, sex, ethnicity, region, education, income, politics, location, country, email and name found only model-template-name columns.

**Identifiers**
- `worker_id` holds 8-character hex codes and is `None` in 9,744 of 39,955 rows.
- `own_opinion.metadata.participant_id` holds 10-character hex codes in all rows.
- **Both are pseudonyms.** No 24-character hex Prolific-style IDs appear in any free text.

**Free text**
- The scan covered `own_opinion.text` (19,395 unique texts), `critique.text` (16,018 unique) and `rankings.explanation` (1,745 unique).
- **Zero hits** for email addresses, URLs, phone numbers, UK postcodes, "my name is", or self-disclosed health or sexuality.
- **A handful of quasi-identifiers do occur:**
  - 6 unique opinions state the writer's own age; one of them is "as a 30 year old Londoner".
  - 18 opinions say "I live in / I'm from" a place.
  - Critiques: 1 states religion ("I am catholic"), 1 states an occupation ("I worked as a teacher"), and 1 gives a place of residence.
- **The topics are political opinions** (for example, opting out of sex education).
- **This regex scan is a lower bound, not a clearance.** It cannot catch, for example, a named relative or a rare life event.

**Licence and terms**
- The repo README grants CC-BY 4.0 for materials and Apache 2.0 for code. It contains "This is not an official Google product".
- The README states **no further terms of use, no restriction on research use, and nothing about consent or ethics approval.**
- I did **not** open the Science paper or its supplement; the supplement returned a 403 for an earlier agent (D4). So nothing in our paper may say what participants consented to until the citation verifier opens it.

**Labelling error in data_gates.md**
- data_gates.md calls `35a875f9b5` a "worker". It is a `participant_id`: it is not in `worker_id`, and it is in `own_opinion.metadata.participant_id` in 6 rows.
- This is LOW. It is a labelling error, not a fabrication, but anything quoting that file should be corrected.

---

## 1. Re-analysis of the Habermas Machine release (A1, A2, N1, A3, A4, N3, N4, N5)

| # | Flaw / risk | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| D-1 | **Verbatim quotes can re-identify writers, and they show political opinions.** Under UK GDPR, political opinions are special-category data if the data count as personal. The release is pseudonymous, but a writer or someone who knows them can recognise a distinctive verbatim opinion. | Quasi-identifier hits listed above (age plus city, religion, occupation). data_gates.md already quotes three opinions next to their participant IDs. | MEDIUM | **Quoting policy for the paper and figures:** (i) never print `worker_id` or `participant_id`; (ii) quote at most 1-2 sentences per opinion, and only from opinions with no self-disclosed age, place, religion, occupation, health or family detail; (iii) prefer quoting the *AI-written candidate statements*, which are not personal data, over participant opinions; (iv) paraphrase when in doubt and mark it as a paraphrase. |
| D-2 | **CC-BY 4.0 attribution is not yet in the paper.** CC-BY requires the creator's name, a copyright notice, a licence link, and an indication of any changes. Filtering, scoring and excerpting are changes. | methods_draft.md line 6 has `[CITE:tessler2024] (PENDING VERIFICATION)` and no "changes made" statement. | MEDIUM (licence compliance, cheap) | Add the attribution sentence from the appendix draft: Tessler et al. 2024, © 2024 DeepMind Technologies Limited, CC-BY 4.0 with link, "we filtered cohorts, scored statements and quote excerpts; no data were altered". |
| D-3 | **Consent and ethics approval of the original study are unverified,** and the draft appendix risks stating them. | The README is silent; the supplement is unopened (D4). limitations_dualuse_draft.md line 19 says "data are CC-BY 4.0 public and unchanged; no human subjects added [confirm]". | MEDIUM (fabrication risk under hard rule 4) | Write nothing about the original consent or IRB unless the citation verifier has opened the paper's ethics statement. Until then, write "collected by the original authors; see their ethics statement". "Unchanged" is also inaccurate for a filtered subset: say "not modified; we analyse a filtered subset". |
| D-4 | **Redistribution of derived files.** Any later code or data release (a human decision) could carry per-participant tables. Examples: `features.parquet` and `all_groups.jsonl` in pilots/T3_1, and future label packets. These link a pseudonymous ID to an erasure score and rankings. | INVENTORY.md lists features.parquet "per (rater, candidate)". CC-BY permits redistribution, but adding linkage raises re-identification risk slightly. | LOW | If a release happens: drop or re-hash participant and worker IDs with a secret salt; keep only round-level keys; attach the CC-BY notice. This is NEEDS-HUMAN; log it and do not do it now. |
| D-5 | **Free-text opinions go to third-party model providers.** pilot_harness supports openai, anthropic and openrouter. If A4 or the scorer is pointed at an external API, participant text leaves the machine. | INVENTORY.md (llm.py providers). s04 currently uses local Ollama; the A4 plan in COSTS.md uses Modal (own containers). | LOW | Prefer Ollama or our own Modal containers. If an external API is used, log the provider in decisions.md and use only its no-training/zero-retention API tier. CC-BY does not forbid this. It is a data-minimisation choice. |
| D-6 | **Annotator exposure (gate-1 labelers L1 and L2).** Labelers read political, sometimes heated, opinions. L1 is an external consultant. This is not a "human study": the labelers are workers producing labels, not subjects. But it must not grow into one. For example, it must not ask labelers about their own views or record labeler reactions as data. | BRIEF section 4; hard rule 6 ("Never run a human study"). | LOW | The packet instructions should (a) collect only the label fields defined in FROZEN_RULES.md, (b) not record labeler demographics or opinions, and (c) let the labeler skip an item as "unsure". |
| D-7 | **Dual-use of the main finding.** If participants' rankings reward erasure, a developer of a deliberation or polling product learns that hiding disagreement *wins approval*. A crux-erasure scorer is a ready-made reward or filter to optimise for that. | BRIEF section 1 says "any system trained on approval learns to hide disagreement". That is the same fact read from the attacker's side. | MEDIUM (low marginal uplift: approval-trained mediators already get this signal for free; the novel artefact is the *scorer*) | State the misuse path plainly in the appendix. Recommend that a released scorer be framed and documented as an audit tool. Release of the scorer and its prompts is a human decision (NEEDS-HUMAN). |
| D-8 | **Misreading risk.** "Rankings favour erasure" can be over-read as "people want to be lied to" or "AI deliberation is manipulative", and used to discredit deliberation tools wholesale. | BRIEF section 10 requires citing Tessler et al.'s contrary finding prominently. | LOW | The appendix must say: these are associations in one 2023 UK online sample with model-written candidates. It must also restate the contrary finding. |

---

## 2. N2: current models write statements (2x2 prompt grid)

| # | Flaw / risk | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| N2-1 | **Real participant opinions go into new models.** The privacy issue is the same as D-5. | COSTS.md: N2 runs on our own Modal vLLM (Gemma-4-12B / Qwen3.8-27B). | LOW | Keep N2 on our own Modal or local models. If API models are added, follow D-5. |
| N2-2 | **The "keep everyone satisfied" × "find common ground" cell is a recipe for consensus-washing.** Publishing which prompt pair maximises erasure tells an operator how to produce smoother-looking statements. | BRIEF section 5, N2 grid. | LOW (the prompts are ordinary; Mahajan et al. 2611.05135 already report a similar effect, D4) | Publish the prompts, since reproducibility outweighs the small uplift. In the appendix, frame the high-erasure cell as a *failure mode to test for*. |
| N2-3 | **Generated statements could be mistaken for, or released as, human or original-study data.** | N2 output files will sit next to real candidates. | LOW | Tag every N2 row `source=model:<id>@<revision>`. Never merge N2 rows into a file that also holds real candidates without that tag. |
| N2-4 | **Any plan to have people rank the N2 statements would be a human study.** | Hard rule 6. BRIEF section 5 already forbids the "rewrite test". | BLOCKER if attempted; not currently planned | N2 is scored by the AI scorer only. Write that sentence into EXPERIMENTS.md so no agent "closes the loop" with crowd raters. |
| N2-5 | **Model licences** (Gemma terms, Qwen licence) govern use of the outputs. | modal_serving README pins the models. Licence text was not opened in this review. | LOW | The citation verifier records each model's licence and the HF revision in methods. Neither the Gemma nor the Qwen terms bar research generation, *as far as known*; verify before stating it. |

---

## 3. N6: hidden-instruction injection (Tier 4, council approval required)

| # | Flaw / risk | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| N6-1 | **No N6 design exists, so "synthetic opinions only" cannot be confirmed.** | No EXPERIMENTS.md, no N6 script, no council record in decisions.md. | **BLOCKER for launch** (not a breach yet) | The council must not approve N6 without a written design that meets N6-2 to N6-5. |
| N6-2 | **"Synthetic only" is ambiguous, and the cheap design breaks it.** The obvious cheap design takes a real Habermas round and swaps one participant's opinion for an injected one. The other opinions in the prompt would then be real people's words in an attack experiment, and real participants' views would be the target of manipulation. Rule 6 says "Injection tests use synthetic opinions only". | BRIEF section 3 rule 6. Section 14 says choose the more careful option. | **BLOCKER if the hybrid design is used** | Every opinion in an N6 prompt, clean and injected, is model-generated or author-written on the *question text* alone. Question texts are research prompts, not participant data, so reusing them is allowed. No real `own_opinion` or `other_opinions` text is ever used. Log this interpretation in decisions.md. |
| N6-3 | **Payload library as an artefact.** A ranked list of verbatim injection strings, with measured tilt per string, against a named open-source mediator (google-deepmind/habermas_machine, which anyone can pip-install) gives specific uplift to anyone attacking a real deliberation deployment. | README: "pip install … habermas_machine". | MEDIUM | In the paper, report *categories* of payload (for example "imperative to the mediator", "fake consensus claim", "format hijack") and aggregate tilt with CIs. Do not print the top-k most effective verbatim strings. Keep the full payload file in the project directory only; whether it is ever released is NEEDS-HUMAN. |
| N6-4 | **Targets.** Never test against a live or shared deliberation deployment, a public demo used by others, or any system where real participants could see the output. Never post or submit an injected opinion to any real platform (Polis, Remesh, Talk to the City, a citizens'-assembly tool, the Habermas colab with other users). Doing so would be both an attack on a real system and a human study. | Hard rule 6 (no human study; no publishing). Hard rule 8 (stay in the project). | **BLOCKER if done** | Run only on our own Modal or local models, offline, using the prompted Habermas Machine code (or our own N2 prompts) with no network side effects. Put the target model list in the design. |
| N6-5 | **Injection text inside real data.** Real opinions might already contain instruction-like text. If so, the N2 and scorer pipelines are themselves being "injected" by participants, which both confounds results and is a hard-rule-7 matter (text is data). | Not scanned for. | LOW | One regex pass over the opinions for imperative addresses to the AI ("ignore", "as the mediator", "you must write"). Report the count. |
| N6-6 | **Defensive value not stated.** Without a defence or detection result, the N6 section reads as attack-only. | None in plan. | LOW | Add one cheap defence arm, for example opinion delimiting plus an instruction-hierarchy system prompt, and report tilt with and without it. |

**What must never be done in N6:**
- no real participant text in any N6 prompt;
- no real platform, live demo or other people in the loop;
- no publication of the top verbatim payloads;
- no run before council approval;
- nothing beyond the $5 N6 cap.

---

## 4. F: fine-tune on honesty-benchmark-style items

The design reviewed is f_finetune/config.py:
- LoRA on Llama-3.1-8B-Instruct;
- 2,000 synthetic items in the style of MASK;
- held-out sets TruthfulQA MC and Anthropic sycophancy evals;
- a neutral control on Dolly-15k.

| # | Flaw / risk | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| F-1 | **LoRA adapters are weights. "Never release fine-tuned weights" covers adapters, checkpoints and merged models,** but no runner yet exists to enforce it. Risky defaults in HF Trainer and TRL: `push_to_hub`, `hub_model_id`, report_to=wandb with artefact upload. | config.py: no runner, no output_dir policy. A grep of the sprint dirs found no push_to_hub yet. | HIGH (preventive; a one-line default can breach rule 6) | In the runner: `push_to_hub=False`, `report_to="none"`, and output_dir on a *private* Modal volume or local disk inside P. A unit test asserts that no `push_to_hub`, `upload_folder` or `create_repo` call exists in f_finetune/. Use a **read-only** HF token in the Modal secret, so a push fails even if attempted. Any human code release must exclude `*.safetensors` and `adapter_*`. |
| F-2 | **Dual-use of the finding.** The pre-registered contrast is in-style MASK gain versus held-out transfer. **If MASK rises and held-out does not:** the paper publishes a cheap, contamination-free recipe for *raising a headline honesty score without becoming more honest*. That is safety-washing: a developer could report an inflated MASK number. **If it transfers:** the recipe is a cheap honesty improvement, which is benign. | config.py BENCH roles. MASK is a public honesty leaderboard benchmark. | MEDIUM (generic "train in the style of the test" is well known; the marginal uplift is the measured size of the gap for a named benchmark) | Frame the result for evaluators: "in-style gains do not certify honesty; require held-out batteries". Report the *gap*, not a how-to. Do not release the 2,000 generated items or the generator prompt verbatim without a human decision. If items are ever released, embed a canary GUID so they can be filtered from future training corpora. |
| F-3 | **Benchmark contamination through style mimicry.** A generator asked for "MASK-style" items may reproduce memorised MASK test items. The paper would then misreport an in-style gain as generalisation. If the items are released, they would also pollute the public benchmark. | CONTAM sets the n-gram threshold at 8 with Jaccard ≤0.2 and the embedding threshold at cos ≤0.85 against MASK. No contamination check is configured against **TruthfulQA or the sycophancy sets**. | MEDIUM (validity plus a commons harm) | Run the same CONTAM check against both held-out sets as well as MASK. Log the drop counts. Never release items without the canary (F-2). |
| F-4 | **Licence bookkeeping is incomplete.** MASK (`cais/MASK`) has no licence or terms recorded in config.py. Some benchmark cards ask that the data not be used for training. Using its *test items* only for the contamination check is fine. Dolly-15k is CC-BY-SA-3.0: **if** adapters trained on it were ever distributed, share-alike would attach (moot under F-1). The Llama 3.1 licence requires "Built with Llama" and AUP compliance on any distribution (also moot). | config.py lines 29-31, 42, 8. | LOW | The citation verifier opens the MASK HF card and records its licence and any no-train clause in config.py and the methods. If the card forbids training *on derivatives*, the style-mimic design needs a human ruling (NEEDS-HUMAN). |
| F-5 | **The generated "disinformation" and "doubling-down" style items contain pressure-to-lie prompts.** The 2,000 training prompts will include requests to state falsehoods or write disinformation. The *responses* are honest refusals or corrections, but the prompt file is a small corpus of disinformation requests. | config.py MASK configs: `disinformation`, `doubling_down_known_facts`. | LOW | Keep the item files in P. Do not print example disinformation prompts in the paper beyond one benign, sanitised example. |
| F-6 | **The adapters must not live on after the sprint without an owner.** | No retention policy. | LOW | After eval: either delete them from the Modal volume, or keep them private with a README "not for release (BRIEF 3.6)". Log the choice in decisions.md. |

---

## 5. B: T1-1 temporal-calibration pilot on Modal GPU

The design reviewed is pilots/T1_1/run_pilot.py:
- items: Wikidata tenure records for heads of government, monarchs and CEOs;
- date-shift prompts;
- logprob and verbal confidence.

| # | Flaw / risk | Evidence | Severity | Cheapest fix |
|---|---|---|---|---|
| B-1 | **Claims about real, living people.** Items assert who holds an office, for example "Q145 Andy Burnham, 2026-07-20 to (open)". data_gates.md says these rows were "not checked against other sources". If the paper prints a model's or our own claim that a named person does or does not hold an office, an error is a factual statement about a real person. | data_gates.md, Gate C. ceo.csv includes private-company CEOs (for example Capgemini, 1. FC Köln). | LOW | In the paper, report aggregates only. Any named example must be cited as "per Wikidata, retrieved 2026-11-15" and spot-checked against a primary source. Prefer named examples about heads of government (public office) over CEOs. |
| B-2 | **Dual-use: a date-injection lever.** The finding "asserting a later date in the system or user prompt shifts the model's confidence in true current facts" is a lever for "temporal gaslighting". An attacker can make a model doubt a correct present fact or assert a stale one. | run_pilot.py has arms `real` and `base` with sys/user placement × k. | LOW (date-in-prompt sensitivity is widely known; the uplift is small) | One appendix sentence: name the lever and the defence (trusted date from the system or tool, not from user text). |
| B-3 | **Data licence.** I believe Wikidata's structured data is CC0, but **I did not open the licence page in this review.** | — | LOW | The citation verifier confirms this before the appendix states it. |
| B-4 | **Gated model.** Llama-3.3-70B returns a 403 on the HF token (INVENTORY.md). Any workaround, such as a different account, a mirror repo or an ungated re-upload, would sidestep the licence gate. | INVENTORY.md: "NEEDS-HUMAN". | MEDIUM if attempted | Do not use mirrors or re-uploads of gated weights. Wait for the human to accept the licence, or use an ungated model. |
| B-5 | **The process is already out of order.** B is Tier 4 and >$5, and needs council approval. A pre-brief Modal run happened (D1.2). | decisions.md D1.2. | LOW (disclosed) | The appendix and methods say the first T1-1 job predates the council. Its cost is in the ledger. |

---

## 6. Planned or recorded steps that would break, or are near, a hard rule

| # | Step | Rule | Status | Fix |
|---|---|---|---|---|
| H-1 | An N6 hybrid design (real round plus one injected opinion) | 3.6 synthetic only | Not yet planned, but it is the cheapest design | Decide and log the all-synthetic interpretation now (N6-2). |
| H-2 | An F runner with HF Trainer and TRL defaults or a write-scope token | 3.6 never release weights | Runner not written | F-1: no push, read-only token, test guard. |
| H-3 | People ranking N2 statements, or any "validation with raters" beyond the L1/L2 labellers | 3.6 never run a human study | Not planned | Write the prohibition into EXPERIMENTS.md (N2-4). |
| H-4 | **Writes outside the project directory.** The cost cutter edited `../pilot_harness/budget.py`, `test_smoke.py` and `test_modal_session.py` (D7). Agents also read `../data` and `../pilots`. | 3.8 stay in the project directory | **Already happened (writes).** Reads are arguably needed, because the data lives in ../data. | The orchestrator logs in decisions.md the interpretation that the project directory is `_apart_intel/` for shared infrastructure, or else stops further edits outside P and copies the harness into P. A human should ratify either choice. |
| H-5 | Using a mirror of a gated model to get around the 403 | Licence; never-inflate spirit | Not attempted | B-4. |
| H-6 | The appendix draft asserts "data … unchanged; no human subjects added [confirm]" | 3.4 no invented claims | Draft text | D-3: rewrite as in dualuse_appendix_draft.md. |
| H-7 | **FROZEN_RULES.md and EXPERIMENTS.md are absent.** `labels/` exists but is empty, so the freeze trigger has not fired. | 3.2, section 2 | Open | They must exist before the first label lands. Otherwise there is nothing to freeze, and rule 3.2 is vacuous. |
| H-8 | Submission or publishing of the PDF, a code release, scorer release, payload release or item release | 3.6 never publish | Human-only | All are NEEDS-HUMAN. dualuse_appendix_draft.md marks each release as a human decision. |

## 7. Required actions, cheapest first

1. Make the N6 all-synthetic interpretation a decisions.md entry (N6-2).
2. Write the F runner guards: no push, read-only token, a grep test (F-1).
3. Adopt the quoting policy (D-1) and the CC-BY attribution sentence (D-2).
4. Remove "unchanged" and any consent or IRB claim from the appendix until the paper's ethics statement has been opened (D-3).
5. Extend CONTAM to both held-out sets (F-3).
6. Record the MASK licence (F-4).
7. Have a human ratify the out-of-directory edits (H-4).
8. Write EXPERIMENTS.md with N2-4 and N6-2 to N6-5 as constraints.

Replacement appendix text: `report/dualuse_appendix_draft.md`. The existing author skeleton `report/limitations_dualuse_draft.md` is untouched, because critics do not edit. The author merges.
