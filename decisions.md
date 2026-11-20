# decisions.md — T3-1 crux erasure

Each entry: time (UTC, approximate where marked), decision, why, who.

## D0 — brief adopted
- BRIEF.md (human-authored) is binding from this point. Project dir: `_apart_intel/t3_1/`.
- Project dir did not contain FROZEN_RULES.md, EXPERIMENTS.md or feedback/ when the brief arrived. Orchestrator is creating them; FROZEN_RULES.md is a DRAFT until the human approves it, and becomes read-only when the first label exists.

## D1 — pre-brief deviations (disclosed, not hidden)
1. **T3-1 $0 pilot** (`_apart_intel/pilots/T3_1/`, scripts s01–s07, PREREG.md) was launched BEFORE the brief, with instructions that included testing erasure vs. real human rankings. That would violate hard rule 3 (main analysis only on shuffled/dummy data before gate 1). On receipt of the brief the orchestrator ordered it to stop any real-ranking analysis. Any real-ranking result already computed is to be labelled "pre-gate exploratory, executed before frozen rules existed, not confirmatory" and must not shape FROZEN_RULES.md definitions. Status of whether it ran: UNKNOWN until the pilot reports — to be filled in.
2. **T1-1 pilot** was redirected by the orchestrator to Modal (cap $8) before the brief. Under the brief that is Tier 4 experiment B and >$5, so it needs experiment-council approval. Ordered to launch no new Modal jobs; in-flight job allowed to finish or be stopped if projected >$5. Spend to date to be reconciled into ledger.csv.
3. Prior Modal setup spend: $0.650 (harness ledger) vs $0.597 (Modal billing), modal_serving setup. Counted against the $150 cap.

## D2 — concurrency
- Free RAM at brief receipt: ~2.1 GB (rule 9 threshold 2 GB). Running ≤3 new agents at a time until RAM is re-checked.

## D3 — section 14 adopted; no waiting on the human
- Human added section 14: never wait for replies. Consequence: FROZEN_RULES.md will be written by the planning room (Fable + orchestrator) from BRIEF.md + the pre-brief PREREG.md only — never informed by any real-ranking result — and frozen (read-only) the moment labels/L1.csv or labels/L2.csv first exists. The human may still edit it before that moment.
- Human reports RAM is free; concurrency raised: launching baseline, planning, past-papers, feedback, novelty x2, stats coder, cost cutter in parallel.

## D4 — novelty scout 1 verdicts (analysis/novelty_claims.md)
- Claim (c) "prior work measured what statements contain, not what people reward" is CONTRADICTED as written: Tessler et al. 2024 also measured rankings/endorsement. Adopted wording: "prior work did not link what participants reward to disagreement-hiding content."
- Claims (a), (b) keep hedges: "to our knowledge, the first test of whether participants' rankings of candidate statements favour hiding disagreement"; sycophancy link presented as OUR framing.
- Contrary finding to cite prominently (BRIEF §10): Tessler et al. — revised statements "demonstrably incorporated minority critiques"; minority overweighted 0.36 vs 0.29 (embedding stance axis, not cruxes).
- New prior work to cite: Mahajan et al., arXiv 2611.05135 (3 Nov 2026) — LLM-judged, no human ratings, agreement prompts cover minority positions less. Overlaps N2; reinforces "never first on erasure".
- Scout's proposed E1 (prompt grid) = existing N2; E3 (minority vs majority raters) = existing N4; E2 (length/vagueness control) folded into A2 controls — passed to planning room, no new experiment opened.
- Unopened: Science supplement (403), MDPI critique. Citation verifier must retry before any reference is used.

## D5 — novelty scout 2 (analysis/novelty_measures.md)
- Name collision: Zaghouani arXiv:2605.26940 defines an "Erasure" metric (embedding formula, unvalidated, no ranking test). Cite; reinforces "never first on erasure".
- Closest measurement prior: Zhu et al. arXiv:2510.05154 (minority under-representation; no ranking test; code not released).
- Recommended for planning room (not adopted until FROZEN_RULES): per-crux LLM-judge label {preserved, blurred, erased} weighted by salience as primary scorer; embedding position-axis score as the A4 second scorer; clarity = LLM-judge rating + length + Flesch-Kincaid as covariates; note clarity may be a mediator (pre-register the handling).
- Brownfield code candidates: FairSumm, arg-sum.
- Unopened (do not cite yet): Cachola, Fish, Blair, Yao.

## D6 — baseline results and inconsistencies
- EXPERIMENT 0 = PER-RATER (independent check, analysis/EXP0_rank_unit.md + exp0_check.py): rankings.metadata.participant_id == own_opinion participant_id in 100% of rows; 8,131 of 8,268 multi-rater groups have differing rankings over identical candidate lists; repo machine.py:125-156 makes one ranking per citizen, :214 derives the group ranking. Section 14 per-group fallback NOT triggered. N4 stays in.
- Label files: the pre-brief pilot made pilots/T3_1/HUMAN_LABEL_SHEET.csv (label columns EMPTY — no labels created, checked). It is SUPERSEDED: its sample was drawn before FROZEN_RULES existed. Gate-1 labels come only from labels/L1.csv and labels/L2.csv, built from packets defined in FROZEN_RULES.md. Careful option per §14.
- Harness cap $50 vs brief $150: cost cutter is raising the harness global cap to $150 with §11 per-experiment caps.
- Pilot scripts s08–s10 were written after the brief (exp 0 check, scorer descriptives, blank label sheet) — consistent with the redirect order; none relates erasure to real rankings per their descriptions. To be confirmed by the pilot's own report.
- Baseline's Write of skills/report_layout.md was refused by the permission system; saved as skills/layout_apart_template.md instead. Orchestrator will NOT rename it to work around the refusal; the filename is immaterial. Surfaced to the human.

## D7 — cost cutter results
- Harness GLOBAL_CAP_USD raised 50 -> 150; EXPERIMENT_CAPS_USD added per BRIEF §11. Tests 30/30 + 11/11 pass (three cap-tied asserts updated to $150; one refusal test re-pointed so it still exercises a refusal).
- Scope of the $150 cap (unclear; careful option per §14): counts ALL Modal spend from this sprint's work (T3-1 + experiment B T1-1 + infra), measured from the harness ledger at list price (which over-counts vs Modal billing). Other projects sharing the Modal workspace (~$15.7 this month) are excluded from the cap but must not be touched.
- Two deployed pilot-vllm apps remain deployed at 0 tasks (scale-to-zero, no idle cost). `modal app stop` was denied by the permission classifier; orchestrator will NOT retry or work around it. Surfaced to human.

## D8 — stats coder build (analysis/, RUNS.md 30 rows incl. failures)
- Recovery: planted A2 +0.52 [0.49,0.55]; N1 CI excludes 0; length confound removed by control. Shuffled real covariates: CIs cover 0 (36/40 reshuffles). Synthetic nulls: A2 56/60, N1 57/60.
- Orchestrator critique (logged, not yet resolved): reshuffle coverage 36/40 = 90% vs nominal 95% — within binomial noise at n=40 (expected 38, sd ~1.4) but could indicate a slightly anti-conservative bootstrap. Action: methodologist evaluator to check with ≥200 reshuffles before gate 1; if coverage <93%, switch to a more conservative interval (e.g. BCa or wild cluster bootstrap) and log.
- DUMMY "good" gate-1 fixture was tuned (0.93 -> 0.98 accuracy) after failing on kappa — test fixtures only, never in labels/. Confirms kappa at n=20 is noisy.
- Assumptions to be pinned by FROZEN_RULES (sent to planning room): label CSV schema, unsure in kappa, AI-score binarization threshold, kappa CI reporting.

## D9 — planning room: FROZEN_RULES.md (draft), EXPERIMENTS.md, PLAN.md written
Written blind: no output relating an erasure measure to real rankings was opened (files read are listed at the top of FROZEN_RULES.md). FROZEN_RULES is a DRAFT until labels/L1.csv or L2.csv first exists.
- **Construct.** Cruxes are extracted from question + opinions only. A crux counts as hidden unless the statement makes the disagreement VISIBLE; a one-sided statement (SIDED) counts as hiding. This departs from the pilot PREREG (RESOLVED counted as retained); the pilot definition is kept as sensitivity A2e. Why: the brief's construct is "hide the disagreement". Weakest choice in the file; flagged for the human.
- **Scorer.** Scorer 1 = Qwen3.8-27B (pinned revision), scorer 2 (A4) = Gemma-4-12B, end to end and independent. One statement per call, temperature 0. Prompts of record are Appendix A of FROZEN_RULES. Score E = share of cruxes hidden, 0-1, unweighted. Name: "crux erasure score" (Zaghouani collision, D5).
- **Gate 1.** 60 statements, one per launch, simple random (seed 20261115), development launches excluded; 20 shared + 20 + 20, plus 4 duplicate rows per labeler (44 rows each). Labels: HIDES / SHOWS / NO_DISAGREEMENT / UNSURE, exact tokens; schema `item_id,label,main_disagreement,comment`; `labels/ADJ.csv` = `item_id,adj_label,reason`, human-written. Kappa: 3 categories with UNSURE kept as a category (stricter), cut-off 0.60 on the unrounded point estimate; bootstrap CI reported; borderline = point estimate decides, interval printed, nothing relabelled. AI binarised at E >= 0.5 (mirrors the labelers' "half or more" rule); zero cruxes = negative; parse failure = wrong. Pass = kappa step passed and 2.5th-percentile bootstrap bound of balanced accuracy > 0.5 (B = 10,000, seed 20261116; one-class resample scored 0.5).
- **Gate recording.** gate1.py writes gate1_computed.json; Opus re-derives; only then the planning room writes GATE1_RESULT.json, with the computed status and no other. Real-rank scripts refuse to run without it.
- **A2.** Mid-rank outcome on 0-1, (rater, round) fixed effect, E raw, controls log word count and Flesch Reading Ease (regex-defined), launch-cluster bootstrap B = 10,000 seed 20261119, two-sided alpha 0.05, estimand beta_E. Own-opinion similarity is sensitivity A2b with a binding wording rule, because the brief fixes the controls as length and clarity. No equivalence claim on a null.
- **Scout inputs (D4, D5).** Vagueness control: sensitivity A2f only (vagueness overlaps the construct). Salience weighting: A2g only. Embedding position-axis scorer: rejected for A4, exploratory. LLM clarity: A2c, not primary (must not depend on a capped job or an unvalidated judge). Clarity-as-mediator: A2h (without clarity) always printed beside A2. N2 must add the human-validated scorer and the system x user split beyond Mahajan et al.; scored only after a gate PASS.
- **Tier 2.** One family test each for N1, A4, A3, N3, N4; Holm at 0.05 over those that run; "if data allows" = at least 30 qualifying launches, counted before scoring.
- **Fallback.** Per-group rule written (FR §11) but not triggered (D6).
- **Budget.** Core $10 split: A1 1.00, A2 scoring 5.20 (over $5, needs experiment council), A4 2.00, A3/N3 1.80. Throughput on long prompts is unmeasured, so every Modal job starts with a 200-call probe and scores launches in a fixed random order (a capped job leaves a random subset).
- **Action for stats coder.** Existing gate1.py / a2_within_round.py / n1_winner_vs_mean.py differ from FR in: label tokens and schema, dup_of handling, output file name, A2 scaling of E, seeds. Align before freeze; list at the top of EXPERIMENTS.md.
- **Action for methodologist.** Coverage check on >= 200 null reshuffles (D8) must finish, and any change of interval method must be written into FR §7, before the first label exists.
- **Not done by the planning room.** No script was run; rank direction (0 = best) is still unconfirmed; packets are not built; agent system prompts in agents/ are not written.

## D9 — ethics review (analysis/ETHICS_REVIEW.md)
- Data: no names/contacts/postcodes found by pattern scan; some opinions combine age + town/religion/job. Decision: no verbatim opinion text in the paper or figures except short, scrubbed excerpts checked by hand; examples in the appendix paraphrased. Licence CC-BY 4.0 (+ Apache 2.0 code); attribution required.
- N6: no design exists. Condition: every opinion in N6 rounds is synthetic, including the non-injected ones; never splice an injected opinion into a real round. N6 stays Tier 4 (council needed).
- F: LoRA adapters are weights. Conditions sent to F designer: push_to_hub=False, read-only HF token, grep test, contamination check on both held-out test sets.
- Appendix skeleton claims "unchanged" data and has a consent placeholder; both unverified. Report council must verify or remove them; no consent claim unless the original paper's consent text is opened and quoted.
- Rule 8 finding: D7 edited ../pilot_harness (outside the project dir) — raising the global cap 50->150 and test asserts. Careful option: NOT reverting (a revert is another out-of-dir edit and would break $150 enforcement); freezing all further edits outside P; surfaced to human for approval. Read-only use of ../pilot_harness and ../modal_serving continues.

## D10 — FROZEN_RULES draft received (planning room); numbering note
- Planning room appended its own entry labelled D9; orchestrator's ethics entry is also D9. Both kept; read by content.
- Weakest choice flagged by planning room: a one-sided statement counts as hiding (departs from pilot PREREG; kept as sensitivity A2e). No human will answer (§14). Careful option: keep the draft's primary definition AND pre-registered sensitivity A2e; the paper reports both, and claims only what holds under both. Human may edit FROZEN_RULES.md before labels/L1.csv or L2.csv exists.
- Rank direction (0 = best?) unconfirmed -> A2/N1 blocked until confirmed from repo code/schema (assigned to stats coder; never from results).
- Interval method must be settled before freeze: methodologist coverage check (D8) still running.
- Launched: label packet builder, scorer runner (gate-1 scoring ≤$5 allowed; full A2 scoring $5.20 needs council), agent system prompts.

## D11 — N2 council (2 of 3 votes in)
- Cost cutter: APPROVE-WITH-CONDITIONS (smoke ≥32 req/model; container list empty after each stage; re-plan changes plan hash -> needs re-approval unless worst case ≤$5; ledger actuals after each stage; >$6.50 back to council).
- Skeptic: APPROVE-WITH-CONDITIONS (generators are also the frozen scorers -> cross-scored cells primary; the novel contrast vs Mahajan is the off-diagonal cells / interaction; Habermas candidates as free baseline; no scoring until scorer manifest + gate 1; flag refusals and think-tag leaks per cell).
- Orchestrator: majority already favours approval, but the full run waits for the methodologist vote so its conditions can be merged (careful option). Smoke stage (<$5, needs no approval) authorised now; no scoring.

## D12 — N2 council complete; F design received
- N2: methodologist APPROVE-WITH-CONDITIONS -> 3/3 approve-with-conditions. Conditions merged and sent to the runner (neutral system-prompt arm or stated reason; COMMON vs DIS = manipulation check; hashed analysis spec with model as factor + clustering by question/launch; full decoding/revision logging; RUNS.md for paid runs; code-enforced no-scoring-before-GATE1_PASSED.json). Approval file N2_APPROVAL.json will be written by the orchestrator only for the final re-planned plan hash after the condition checklist is verified.
- F: design + mock tests done ($0). Llama-3.1-8B LoRA, MASK-style training items, held-out TruthfulQA MC1 + Anthropic sycophancy set, length-matched dolly-15k control, seeds 11/12/13; est. $18.2 ($22.8 w/ contingency) of $25 cap. With 3 vs 3 the minimum exact two-sided p is 0.10 — F can only ever be reported as a direction/effect size with that limitation, never as significant.
- F BLOCKED: dataset downloads were denied by the permission system -> contamination check has never run on real data; judge.py unwritten; read-only HF token unconfirmed. Per §14 the orchestrator does not work around the denial. F does not go to council until these clear. Surfaced to human.

## D13 — human directives: cap $200; decide fast; stop non-novel experiments
- Human: "real cap 200 ... take quicker decisions, don't wait for me, you have councils". Harness GLOBAL_CAP_USD 150 -> 200 (budget.py + test_smoke.py asserts); tests 30/30 + 11/11 pass. This also ratifies the earlier out-of-dir harness edit (D9 rule-8 item closed).
- Budget re-split (orchestrator): §11 lines unchanged; the extra $50 goes to "council-approved new experiment" pool.
- Human: experiments only if worth doing; stop the ones that are not novel. Orchestrator decides from councils without waiting; launching a novelty-triage review over N2, N5, N6, B, F.
- Past-papers council done (PAPER_CHECKLIST.md): Execution = 61% of review sentences; small n is the top criticism; winners praised for controls and honest negatives; median body 8 pages both groups; figure/table counts don't separate. Caveat: 20 vs 15 projects, non-random.

## D14 — agent role prompts
- 19 role prompts + INDEX.md in agents/. The report-council role prompt was refused twice by the write tool ("subagents should not write report files"). The orchestrator will not write it on the subagent's behalf (no working around a refusal); the report council's instructions are BRIEF §8 verbatim, which agents read directly. Surfaced to human.

## D13 - N2 analysis spec hashed; deviations from EXPERIMENTS.md logged (runner agent, 2026-11-15)
- analysis/N2_ANALYSIS_SPEC.md sha256 = 3875c61e6708c6e1d43500575c694e0cdd8fd1b060eb4879ebcac02ec929c8f3 (written before any paid N2 call; n2_grid.py refuses smoke and launch unless this hash is in this file). Any change needs a new council vote and a new hash.
- Council conditions incorporated (skeptic, cost cutter, methodologist): NEUTRAL system arm under COMMON (5 cells); COMMON-DIS = manipulation check; C1 override (SAT-DIS vs ACC-DIS), C2, C3 interaction and neutral contrasts = family (Holm, 10 tests); cross-scored cells primary; HM iteration-0 candidates = free baseline; launch-cluster bootstrap over 231 launches; model as factor; top_p 1.0, top_k -1, revisions and serving config logged; paid runs logged in RUNS.md; scoring refused in code unless analysis/GATE1_PASSED.json exists with matching scorer manifest hash; smoke rounds drawn outside the N2 sample and excluded.
- Deviations from EXPERIMENTS.md N2 (lines 76-81), each with reason: (1) 250 rounds, one per question, seed 20261115 instead of 100 launches, seed 20261126 (power at d_z 0.2-0.25 needs more than 100; 231 launches); (2) 5 cells x k=2 = 5,000 statements instead of 800 (power; neutral arm); (3) prompts inline in n2_grid.py and hashed in plan.json instead of analysis/prompts/N2_*.txt; (4) 8-round smoke outside the sample instead of a 20-launch pilot (the smoke measures throughput and format only; stop rules are the format flags and near-duplicate share, not a parse-failure rate because no scorer is run). 45 of the 250 rounds come from development launches: N2 is reported with and without them.

## D15 — novelty triage adopted (analysis/council/NOVELTY_TRIAGE.md)
- N2: RUN (council conditions D12 stand). Primary contribution = system x user interaction; main effects framed as replication of Mahajan 2611.05135.
- N5: RUN-REDUCED — one exploratory test after gate 1 and N1, controlling for initial disagreement; $0.
- N6: STOP — Gudiño-Rosero et al. arXiv 2508.04281 already injected a participant opinion into consensus generation on the same Tessler data, with defences. Not novel.
- F: STOP — prior work (Wei et al. 2023) already shows this transfer; 3 vs 3 cannot reach significance. Not worth $25.
- B (T1-1): RUN-REDUCED — idea still open (FinDendro uses past dates only), but existing probe is broken (P(still true) ≈ 0 with no date). Fix on CPU first, then pilot capped at $5 (stays under the council threshold; anything more goes to council). B is now the only second-submission candidate.
- Freed $70 (N6 $5 + F $65) goes to reserve; no new allocation until a council-approved proposal.
- Old T1-1 pilot ordered to stop and report; new T1-1 runner takes over its code.

## D16 — citation verification (report/references_verified.md)
- 61 refs: 51 VERIFIED, 5 CLAIM-MISMATCH, 3 METADATA-MISMATCH, 2 COULD-NOT-OPEN. refs.bib = 50 VERIFIED (Costello 2024 held out: 2026 Science expression of concern).
- Tessler main-text minority weight 0.29 -> 0.36 verified (p.6). Supplement still unreachable (403) — will not be cited; human may fetch it.
- Wen et al. verified but contested (ICLR 2026 rebuttal) -> hedge.
- Author (drafter) instructed to apply the section-A fix list, drop unverified claims, and align methods to FROZEN_RULES.

## D17 — scorer built; gate-1 AI scores skewed; packets held
- Scorer + manifest done; dev probe 184 calls $0.398 (4/140 label calls failed after retry); gate-1 scoring 60 statements $0.383, no parse failures. Containers empty after.
- Problem: 49/50 scored gate-1 statements E ≥ 0.5; 10/60 in zero-crux rounds. Risks: too few negatives for balanced accuracy; possibly degenerate scorer; possibly low within-round variance for A2.
- No labels exist, so scorer/sample/threshold may still change without breaking rule 2 — any change must be justified on construct validity, logged, re-frozen, and the probe + packets rebuilt. Change must never be motivated by relating E to rankings (not looked at).
- Scorer council convened (skeptic, methodologist, cost cutter) on Q1 (fix) and Q2 (A2 full scoring $3.5/$5.15). Packets stay held until Q1 is decided.

## D18 — scorer council outcome; orchestrator decision (split vote)
Votes: skeptic Q1=(b) fix E1 extraction (silence treated as opposition -> invented cruxes, 4/11 inspected positives), reject restratifying; methodologist Q1=(d) keep prompts/E/0.5 threshold, keep 60-item gate, add balanced accuracy restricted to rounds with disagreement + wording rules, optional blind supplement of AI-VISIBLE statements; cost cutter Q1 = costs only (~$0.75 re-run). Q2: skeptic + cost cutter APPROVE-AFTER-Q1, methodologist APPROVE (conditional on no prompt change).
Orchestrator decision (§9: decide and log):
1. ADOPT the skeptic's E1 fix. Reason: "silence = opposition" is a construct-validity error in how disagreement is derived from opinions (BRIEF §4 requires disagreement defined from opinions); fixing it pre-label is allowed and is not outcome-driven (rankings never viewed). One change only, verified on the dev set only; gate items re-scored once; old-scorer gate result also reported.
2. ALSO ADOPT the methodologist's reporting rules: gate-1 balanced accuracy additionally reported on rounds with ≥1 crux (because 10/11 AI negatives were zero-crux rounds, gate 1 could otherwise pass on "any disagreement" alone), with binding wording; record launch count before freeze. Primary gate-1 pass rule (BRIEF §4) unchanged.
3. Blind supplement of AI-VISIBLE statements: deferred — it asks humans for extra labels; offered to the human as optional, not required.
4. Q2: full A2 scoring runs AFTER the fix (2 of 3).
5. Within-round E variance is the larger threat (3/34 dev rounds vary; 13/34 under A2e). Planning room replan convened on A2 design before freeze; decision must not use rankings.

## D19 — stats alignment; interval rule triggered
- Scripts aligned to FROZEN_RULES draft (analysis/ALIGNMENT.md). New: a3_ai_vs_human.py, n3_draft_vs_revised.py, n4_minority.py, tier2_holm.py. Planted effects recovered for A2, N1, A3, N3, N4; nulls cover 0; gate1 refuses real-rank mode without GATE1_RESULT.json.
- Rank direction: 0 = best (repo code: base_method.py:59-60, schulze_method.py:41-42, reward_model/base_model.py:67, analysis/types.py:25). Sign check vs ratings.agreement assigned.
- FR §7 interval coverage: A2 185/200 = 92.5% < 93% threshold. Decision: obey the rule (change method pre-freeze), not re-run at larger B to pass. Candidates: cluster BCa, wild cluster bootstrap; ≥400 reshuffles, B=2000; pick ≥93% closest to 95%; else most conservative + limitation.
- Open: ADJ.csv column named differently in FR §5 vs §6.3 (gate1.py accepts both) -> planning room to unify in the replan.

## D20 — N2 smoke done; k=1 plan approved for generation
- Smoke: 40 req/model outside the N2 sample, $0.568, 0 errors/truncations/refusals/think leaks. Qwen over the 150-word cap 19/40 (max 175), gemma 0/40. Measured throughput gemma 193, qwen 222 tok/s (below planning assumptions).
- Re-plan k=2 (5 cells incl. neutral arm): worst $7.71 > council ceiling $6.50 -> NOT approved (cost-cutter condition 5). Orchestrator approved the k=1 fallback (worst $5.45, plan_sha256 1c0f2d7c…) within the ceiling — no new vote needed since it is inside the approved envelope. Approval file analysis/council/N2_APPROVAL.json, generation only.
- Length covariate added to N2 analysis spec (amendment, new hash, before any scoring).
- Note: N2 runner also wrote a decisions entry numbered D13; numbering collision, read by content.

## D21 — planning room REPLAN R1: A2 identifying variation (FROZEN_RULES, EXPERIMENTS, PLAN edited; no label file existed)
- Trigger (D18 item 5): dev probe, E varies within the round in 3/34 rounds (13/34 under A2e); SIDED 186/216 labels. Blind: read BRIEF, FR, EXPERIMENTS, PLAN, D17-D20, the three SCORER votes, N2_ANALYSIS_SPEC.md, ALIGNMENT.md, the E1 prompt file. No ranking, rating, label, score file or real-rank output opened. `analysis/eval/METHODS_EVAL.md` does not exist. labels/ empty and FR not read-only, checked before and after the edits.
- **Primary confirmatory test: unchanged, A2 beta_E (scorer 1).** Reasons for not promoting anything else (FR §7.2): A2e = SIDED counted as shown measures omission/blurring, not hiding, so promoting it because it varies more would change the construct to fit the data; N1 has the same identification (d_r = 0 wherever E does not vary) with less data and no controls; a between-round design adds no variation (a round's mean E differs from 1 only in the rounds A2 already uses) and adds question/group confounds, and ranks carry no between-round information; a graded per-crux score needs invented weights with no labels to validate them; restricting to informative rounds changes almost nothing under the fixed effect, so it is sensitivity A2i.
- **Decision rule, fixed now (FR §7.1).** K_inf = launches with at least one round whose 4 candidates take ≥ 2 distinct E; MDE80 = 2.80 x SD(beta_E) over 400 within-rater reshuffles of real ranks with real E (seeds 430000+i). INFORMATIVE: K_inf ≥ 100 and MDE80 ≤ 0.10 (0.3 rank position) -> A2 leads, directional claim allowed. LOW-POWER: K_inf ≥ 50 otherwise -> A2 reported with R_inf, K_inf, MDE80; a detected association is worded "small selected subset, likely overstated, needs replication"; an interval including 0 is "not measurable", never "no association". NOT MEASURABLE: K_inf < 50 (the old floor) -> no directional claim. Written to gate1/A2_TIER.json before real ranks can be read; one-way downgrade if 2.80 x real bootstrap SE > 0.10 (looks at SE only). 100 and 0.10 are judgement calls (J), not from a power analysis on outcomes; not moved once K_inf is known.
- **Expected outcome pre-registered (FR §1):** LOW-POWER or NOT MEASURABLE is more likely than INFORMATIVE. Rough planning arithmetic only (methodologist F5 projection, independence assumed): about 57 to 390 launches, point about 160, before the E1 fix removes some rounds.
- **N2:** not confirmatory (its statements are never ranked by participants), but it becomes the lead result together with the pre-specified prevalence quantities when gate 1 is PASS and the tier is not INFORMATIVE (FR §7.3), only if its manipulation check passes. N2 keeps its own hashed spec; FR does not alter it. Title and abstract then make no claim about what rankings favour. Novelty sentence stays "first test"; the paper says plainly that the test was not informative and why.
- **Gate-1 additions per D18 (FR §6.4a), pass rule unchanged:** BA_crux (items with ≥ 1 AI crux), BA_sh (those with human HIDES or SHOWS), zero-crux share of correct negatives, human-labelled prevalence D1h (Wilson), scorer-v1 gate accuracy in the appendix. Binding wording: if BA_sh has < 5 human SHOWS or its lower bound ≤ 0.5, every statement that gate 1 passed says the scorer is validated for detecting whether disagreement is present, not whether a statement hides it; every beta_E carries the unvalidated-contrast clause; no directional rank claim in title or abstract. Expected to fire with an unstratified sample of 60.
- AI-VISIBLE supplement (D18 item 3): not added to the pipeline. BRIEF §3.1 names only L1.csv and L2.csv, schema fixed at 44 rows, packets built. Left to the human as an optional pre-freeze edit; otherwise a stated limitation. Careful option.
- Orchestrator add-ons: (1) ADJ.csv column unified to `adj_label` (FR §6.3 corrected; gate1.py must stop accepting `final_label`). (2) Interval method: the D19 selection rule (cluster BCa vs wild cluster bootstrap, ≥ 400 reshuffles, B = 2000, coverage ≥ 93% closest to 95%, else the higher one plus a limitation) is now in FR §7. **Method name not yet recorded in ALIGNMENT.md when this was written; the FR cell says so.** Planning room must copy the name in once recorded. If the file freezes first, the frozen selection rule plus the ALIGNMENT.md record stand.
- Also corrected: FR §10 said N2 is scored "only with scorer 1", which contradicted the hashed N2 spec (cross-scored cells primary).
- Concurrent edit noted: the scorer runner edited the FR §4 prompt-change row and Appendix A (E1 v2) while this replan was being written; both sets of edits are in the file; Appendix A matches analysis/prompts/E1_extract.txt (checked, line endings normalised).
- Open code work (EXPERIMENTS "Replan log"): a2_informativeness.py + A2_TIER guard; A2i; gate1.py §6.4a outputs; **scorer.py has no empty-side crux drop yet (FR §3 requires it before the full scoring run)**; prevalence.py; N1 non-zero count.
- Weakest points of this replan: the tier thresholds are judgement calls; the blind MDE is optimistic because shuffling removes agreement between raters; INFORMATIVE still rests on AI "shown" calls that humans check only inside the random sample.

## D22 — experiment B (T1-1) inconclusive; no second submission
- Probe bug found and fixed: the past-tense "was ... still ... today?" wording drove P(Yes)≈0 for dynamic facts; a present-tense claim + "Is this claim true today?" passes 20 sanity anchors. Yes+No mass 1.000 throughout (extraction was fine).
- Pilot (Gemma-4-12B, Qwen3.8-27B; 55 items, 2,237 calls each, 0 errors; $1.015 of $5): INCONCLUSIVE under the corrected kill rule. Gemma treats the stated date as hypothetical in every placement (P(Real) 0.05–0.11, even for the real date); its GO-like R=0.17 occurs only in its most fictional placement. Qwen's only non-fiction placement gives R=0.28 [0.24,0.33]. Re-anchoring the cutoff shifts R by more than the CI width.
- Decision: B is NOT a second-submission candidate on this evidence (F was stopped in D15). Per BRIEF §5 the second slot goes to whichever has a stronger verified result — neither does, so there is no second submission. B results kept as exploratory (b_t1_1/B_PILOT_REPORT.md). No further B spend.
- The "models read stated dates as fiction" observation is logged as a possible future direction only; not claimed as novel without a prior-work check.

## D22 - scorer v2 fix round executed (scorer runner)
- E1 revised once (inserted passage: crux needs explicit opposing positions; silence is not opposition). FR Appendix A + row 4 updated, prompt file regenerated byte-identical, E1 sha be662ca7.. (v1 65450760..). scorer.py also drops empty-side cruxes (D21/FR R1); 0 such cruxes occurred in dev v1/v2 or gate v1/v2, so the rule is a no-op on these data and no extra re-run was needed. container_wait_empty no longer stops containers that pre-existed the launch (it was about to stop another session's qwen container).
- Dev (40 rounds, same rounds as v1): zero-crux 5 -> 11 (27.5%, under the 40% line), cruxes 55 -> 41, one-vs-3+ cruxes 23 -> 18, label parse failures 4 -> 0, E within-round variation 3/35 -> 2/29 (E_pos 13/35 -> 11/29). 13 rounds fewer cruxes, 1 more.
- Gate (re-scored once, final): zero-crux 10 -> 15, cruxes 81 -> 55, AI binary 49/11 -> 40/18 (+2 missing from label parse failure), 7 pos->neg, 0 neg->pos. v1 scores kept in gate1_scores_v1.jsonl for the appendix.
- Skeptic examples (inspected AFTER the single gate re-score, not used to tune): items 41 and 52 fixed (0 cruxes); item 16 reframed but still assigns all 5 members; item 11 unchanged (OP4 vs 1,2,3,5 on permanence). Residual silence-inferred sides remain (also in dev rounds 0 and 27); v2 is not a complete fix. No further revision (one-revision rule).
- Spend this round $0.7386 (probe 0.3126 + gate 0.426) of $2 cap.

## D23 — scorer v2 accepted; full A2 scoring launched; packets released for verification
- v2 (silence ≠ opposition; empty-side crux drop — the latter changed nothing). Dev 40 rounds: zero-crux 5 -> 11; label parse failures 4 -> 0; within-round E varies in 2/29 rounds (v1 3/35); E_pos variant 11/29. Gate re-scored once: AI positives 49 -> 40, negatives 11 -> 18, zero-crux 10 -> 15; 2 rounds lost label parse (counted per parse rule). v1 gate scores kept for reporting. Spend $0.74.
- Implication: A2 will very likely fall in the pre-registered NOT MEASURABLE tier (FR §7.1); confirmed only by a2_informativeness.py on shuffled ranks.
- Full A2 scoring approved (2/3 APPROVE-AFTER-Q1; methodologist's conditional approval void after the prompt change) and launched.
- Risk logged: the gate re-score stopped a Modal container by id it could not confirm as its own — possibly N2's. N2 runner asked to check and resume from cache. Scorer stop logic fixed to skip pre-existing containers.
- Packets: manifest final -> packet builder re-verifies against FROZEN_RULES R1 and writes READY.md.

## D24 — interval method of record; rank direction confirmed
- Interval: wild cluster bootstrap-t (Rademacher, launch clusters). Coverage on 400 within-rater reshuffles, B=2000: wild 386/400 = 96.5%; BCa 387/400 = 96.75%; old percentile 387/400. Both candidates ≥93%; wild chosen as closest to 95% per the D19 rule (one-reshuffle difference — mechanical choice, stated as such). Earlier 92.5% attributed to Monte Carlo noise at B=500 / 200 reshuffles. Default for A2, N1, A3, N3, N4 (only A2 coverage-checked — limitation).
- Rank direction 0 = best confirmed: within-rater slope of agreement rating on rank -0.576 [-0.594, -0.557], 871 launches; no erasure scores used.
- a2_informativeness.py and gate1 §6.4a additions written and tested on dummy/synthetic data. Real A2 requires gate1/A2_TIER.json.
- FR §7 p-value formula must be updated for bootstrap-t before freeze -> planning room.

## D25 — planning room REPLAN R2: interval method and p-value written into FROZEN_RULES (pre-freeze)
- Checked immediately before editing: labels/ has 0 files, FROZEN_RULES.md not read-only, no gate1/FREEZE.json. Blind: read ALIGNMENT.md, D21-D24, analysis/eval/METHODS_EVAL.md, common.py interval code; no rank-vs-erasure output, rating or label.
- FR §7: interval method of record = wild cluster bootstrap-t (Rademacher weights per launch, unrestricted residuals, CR1 SE), per ALIGNMENT.md and D24. Interval as coded and coverage-checked: equal-tailed bootstrap-t, [est - se*q0.975(t*), est - se*q0.025(t*)]. Selection numbers copied from ALIGNMENT.md (wild 386/400, BCa 387/400, percentile 387/400; B=2000, 400 reshuffles, dummy E).
- FR §7 p-value: percentile formula replaced by the two-sided symmetric bootstrap-t p = (#{|t*| >= |t_obs|}+1)/(B+1), t_obs = est/se. "Detected" is still decided by the interval. Interval is equal-tailed, p is symmetric, so they can disagree near 0.05: both printed, interval decides, called borderline.
- **Deviation from the orchestrator's wording, flagged:** the request said "B=2000". B=2000 is the coverage-check setting in ALIGNMENT.md/D24. FR §7/§8 already fix B=10,000 for the analyses of record, the code default is 10,000 (common.DEFAULTS), and neither D24 nor ALIGNMENT.md says the analysis B changes. Careful option: B of record left at 10,000; FR says so explicitly. If B=2000 is really intended for the real runs, FR §7 [R2] row and common.DEFAULTS must both be changed before the first label file.
- Limitation written into FR: only A2's coverage was checked (dummy E, shuffled ranks); N1, A3, N3, N4 and the prevalence shares use the same method unchecked; coverage with few informative launches may differ.
- FR §8: every "launch bootstrap"/"percentile" cell now points to the method of record; N1 is printed beside its length and clarity differences and never called a replication (METHODS_EVAL N1a, N1c).
- METHODS_EVAL.md placeholders: three, not two (`__COVERAGE__`, `__N1LEN__`, `__N1TIES__`). They are unfilled evidence in the methodologist's own report, not blanks in FROZEN_RULES; not filled by the planning room (an evaluator's numbers are not written by someone else; never fabricate). The one real FR placeholder ("Method selected: NOT YET RECORDED") is filled. Methodologist should fill its own three.
- Not adopted pre-freeze (no evaluator numbers, no tested code): residualised N1, spline length control (A5), tied-winner N1 variant (N1b), G2 sentence on kappa power at n=20. Still open in code per METHODS_EVAL and not confirmed fixed: G1 (KAPPA.json overwrite / no hash comparison in validity), G5, A1 (source-parquet hash check), A3 (gate status not read by the real-run lock).

## D26 — stats coder stopped
- The finished stats-coder agent re-sent the same completion report 5 times while reporting "waiting on its own background work" (it says no jobs of its own were running). Stopped via TaskStop to avoid wasting usage. Its outputs (analysis/*.py, ALIGNMENT.md, RUNS.md) are complete and unaffected.

## D14 - N2 generation complete; spec amendment 1 (runner agent, 2026-11-16)
- N2 generation under plan_sha256 1c0f2d7cbb0cdbc154319d7451b823334f5f78196ec272ffd5b351b84fac0b91 (k=1, 5 cells, 250 rounds, gemma4-12b + qwen3.8-27b): 2,500 statements in analysis/n2_runs/full_k1. The qwen session was interrupted once at 684 of 1,250 by an external container stop (84 provider errors); resumed from the file cache with the same plan hash, no finished item regenerated. No output scored or read beyond form counters.
- N2_ANALYSIS_SPEC.md amended (section 9, length covariate; qwen over cap in 27-41% of outputs). New sha256 = 707c7fa2445051d1da64082d163c46bfbd6fde3ef2896dad2961ce03ffbd1146. Supersedes 3875c61e... for analysis; it was in force at generation time.

## D27 — N2 generation complete
- 2,500 statements (2 models x 5 cells x 250 rounds, k=1), plan 1c0f2d7c…; $1.737 actual vs $5.445 worst. Qwen interrupted at 684/1250 (84 provider errors, consistent with the external container stop in D23; cause unconfirmed) and resumed from cache with the same plan hash — no regeneration.
- Format: 0 truncated/empty/think/refusal/preamble; 0% near-duplicate rounds. Qwen over the 150-word cap 27–41% per cell, gemma 0% -> length covariate added to every primary N2 model; spec amended to 707c7fa2… before any scoring (generation was under 3875c61e…; amendment logged, not outcome-informed).
- Remaining qwen container is the concurrent A2 scoring session (started 18:38).
- N2 scoring stays blocked until GATE1_PASSED.json.

## D28 — methodologist evaluation (analysis/eval/METHODS_EVAL.md)
- Coverage confirmed: A2 percentile 949/1000 = 94.9% [93.4, 96.2]; wild bootstrap-t 573/600 = 95.5%; hard synthetic nulls (incl. length confound) ~95%. The 185/200 that triggered D19 was noise (p=0.078 at true 95%). Wild stays; no fix.
- Fixes ordered (code, author role -> new fixer agent): G1 KAPPA.json write-once + validity step must verify it uses exactly the labels kappa saw (hash); A1 check source-data hash on every real run; A3 real-run lock must check gate status; L3 outputs hashed and never silently overwritten.
- N1a: N1 falsely rejects 26.5% under a pure length confound -> N1 must control for length. labels/ still empty, so FROZEN_RULES amended pre-freeze ([R3], planning room). Not outcome-informed.
- G2 (design limitation, BRIEF definition unchanged): with n=20 shared items, two 90%-accurate labelers pass the kappa ≥ 0.60 step only ~34% of the time. The BRIEF cut-off stays (§4: never change definitions). Consequence stated in advance: a kappa fail is likely even with good labelers and leads to the "not yet measurable" write-up; reported with its CI.
- L1: D8's numbers cannot be traced to code that still exists -> D8 numbers are superseded and must not appear in the paper; only RUNS.md-traceable numbers are used.

## D29 — planning room REPLAN R3: N1 length/clarity control and kappa-power note written into FROZEN_RULES (pre-freeze)
- Checked immediately before and after editing: labels/ has 0 files, FROZEN_RULES.md not read-only, no gate1/FREEZE.json. Both findings rest on synthetic data only (eval/cov_hard_len_new.json, eval/gate1_sim.json); numbers checked against METHODS_EVAL.md before being copied: N1 covers 0 in 147/200 (false rejection 26.5%), A2 controlled 190/200; kappa pass rate 0.344 (two 90%-accurate labelers, n=20, 2000 sims, seed 777), 0.672 at 95%. No rank-vs-erasure output, rating or label opened.
- **N1 (FR §8, new "N1 adjustment [R3]" table).** Family test is now alpha, the intercept of an OLS across rounds: d_r = alpha + g_L*dLen_r + g_C*dClar_r + u_r, where dLen_r and dClar_r are winner minus round mean of A2's own zLen (log word count) and zClar (Flesch), same z-score constants. Wild cluster bootstrap-t, launch clusters, B=10,000, seed 20261120 (unchanged). Printed beside it, not tested: N1u (unadjusted mean, the brief's literal N1), N1h (length only), g_L, g_C, count of rounds with d_r != 0.
- Reasons for the form: (i) winner-minus-round-mean is the round-level counterpart of A2's within-round demeaning on the same covariates; (ii) a within-round residualisation of E would be fitted on 4 points per round; (iii) alpha is unchanged by rescaling the covariates.
- **Beyond the literal request, reversible before freeze:** clarity is controlled as well as length (A2 controls both; N1a names both); length-only is N1h.
- **Guard (J):** the adjusted test must be run on the evaluator's synthetic length-confound design (>= 200 datasets) before real ranks; coverage < 93% or check missing -> N1 leaves the Holm family and is descriptive only. No other repair.
- **G2 (FR §6.2 new row, §12 first row).** Stated in advance: at n=20 two 90%-accurate labelers pass kappa >= 0.60 about 34% of the time (95%-accurate: about 67%). BRIEF §4 cut-off, n and consequence unchanged; a FAIL -> "not yet measurable", worded "agreement was not established at n = 20", printed with the kappa interval and the simulated pass rates. Placed in §6.2 and §12 (the request said §4/§6; FR §4 is the erasure score, the kappa step is §6.2).
- **Open, needs an owner:** n1_winner_vs_mean.py still computes only the unadjusted mean (docstring still says percentile). The stats coder was stopped (D26). Adjusted model + N1h + synthetic check + a tier2_holm.py flag are unwritten; until they exist and pass, the guard above applies. EXPERIMENTS.md "Replan log" lists the work (R2 and R3 notes added there). PLAN.md not changed by R2/R3: sequencing is unaffected.

## D30 — methodologist fixes done (analysis/eval/FIXES.md)
- G1 write-once KAPPA.json + row hashes; A1 manifest + source-parquet hash required on real runs; A3 lock reads gate status (PASS -> VALIDATED; FAIL/NOT_YET_MEASURABLE -> EXPLORATORY_UNVALIDATED; else refused); L3 versioned outputs with sha256 sidecars; N1a per [R3].
- N1 [R3] guard met: adjusted alpha covers 0 in 192/200 (96.0%) under a pure length confound vs unadjusted N1u 147/200 (73.5%). N1 stays in the Holm family.
- Tests: test_fixes 33, test_all 27 gating, test_r1 — all pass on dummy/synthetic data; no failed runs.

## D31 — human rule edits R4 (2026-11-15T19:06Z); labels/ verified empty
Human-authored edits (binding; the human owns BRIEF definitions):
1. Gate-1 kappa cut-off 0.60 -> 0.40. Reason (human): power check showed ~34% pass rate for good labelers at n=20. Packets rebuilt: 30 shared + 15 unique per labeler + duplicate checks. Report kappa with CI and Gwet's AC1 beside it.
2. Add 12 N2 statements to the packets, spread across models and conditions, model/condition hidden; separate scorer check on N2 text. N2 results count as VALIDATED only if this check passes; else EXPLORATORY.
3. A4 second scorer must be from a different model family than every N2 generator. All N2 results reported split by generator.
4. Headline rate = share of statements that hide disagreement in the HUMAN-labeled sample, with CI. Scorer rate secondary.
5. N2: add 2-3 generator models from different families, same prompts and rounds; experiment council approves the choice; length stays a control.
6. Old T3-1 pilot must answer in writing whether it touched real rankings; if yes, record exactly what and add to limitations. Confirm development rounds are excluded from confirmatory tests.
Unchanged: no N2 scoring and no real-data analyses before gate 1.
Orchestrator implementation decisions:
- The 12 N2 validation statements are gate-1 measurement items: they are scored with the frozen primary scorer exactly like the other gate items and stored separately. No N2 results are computed from them. This is not "scoring N2" in the sense of the rule (no N2 analysis).
- To spread the 12 N2 items across ALL generators, packets are rebuilt after the extended N2 generation finishes. A generator that fails to deploy is dropped from N2 and logged; packets then use the generators that exist.
- Gemma-4-12B was the A4 scorer and is also an N2 generator -> A4 scorer must change to a new family (edit 3). Chosen by the council together with the new generators.

## D32 — full A2 scoring done (scorer v2)
- 1,960 rounds / 871 launches / 7,840 statements; $2.4534 (worst $5.154). 3 extraction failures; 123 label parse failures (135 statements without E; 67 rounds partially missing); 19 empty-side cruxes dropped; 481 zero-crux rounds (24.5%). No rankings/ratings/labels read.
- Within-round E variation (counts only): 176/1,409 evaluable rounds across 166 launches (clears the ≥100-launch count for INFORMATIVE; the tier also needs MDE80 ≤ 0.10, computed on SHUFFLED ranks by a2_informativeness.py). E_pos: 529 rounds / 431 launches.
- Next: run a2_informativeness.py now (shuffled ranks only, allowed pre-gate per FR §7.1) to write gate1/A2_TIER.json before unblinding.

## D33 — old T3-1 pilot written answer (pilots/T3_1/TOUCHED_RANKINGS.md); container stop denied
- Real rankings were NEVER modelled, plotted or summarised against erasure scores: s06_analyze.py never ran; none of its outputs exist. The v2 crux labels were never joined to rankings.
- BUT pilots/T3_1/features.parquet (s05_features.py, all 1,960 eligible rounds) stores each rater's real rank + agreement in the same rows as two cheap erasure proxies (markers, min_cov). Only per-display-position means were printed (no rank used). Decision: features.parquet is SEALED — no agent may open, read or load it; it is not used anywhere in T3-1. Disclosed in limitations ([PILOT-DISCLOSURE] slot) exactly as above.
- The pilot's 150 rounds/launches are the development set already excluded from gate-1 sampling and all confirmatory tests (ids listed in TOUCHED_RANKINGS.md); [R4] item 6 confirms in FROZEN_RULES.
- Pilot also confirmed experiment 0 independently (per-rater, 100% of 35,489 rows; rank 0 = best; ties allowed; -1 = mock) and found no newer Habermas data release (clone 7923b71, 2025-01-21).
- An idle Modal qwen container (ta-01M7G7WHWRPZAMKJA95T9T9BBR) persisted after all jobs ended; orchestrator's `modal container stop` was denied by the permission classifier. Not worked around; surfaced to the human.

## D34 — human rule edits R5 (2026-11-15T19:10Z); supersede conflicting parts of D31/R4; labels/ verified empty
Human-authored (binding):
1. ONE human labeler: the author (hypothesis-aware). "Consultant (blind)" removed. One packet: 50 unique items (38 original statements + 12 N2 statements spread across models and conditions) + 20 of them repeated in shuffled order as a second pass, labeled ≥1 hour after the first. Scores, rankings, model and condition hidden.
2. Agreement = self-consistency kappa on the 20 repeated items, cut-off 0.60, with CI. (Replaces D31 edit 1: inter-rater kappa 0.40 / 30+15 design.)
3. Gate 1: bootstrap 95% LB of balanced accuracy (scorer vs author's FIRST-PASS labels) > 0.5. The 12 N2 items checked separately; N2 results VALIDATED only if that check passes.
4. Independent LLM annotator: fresh context, family different from the scorer and all N2 generators, same instructions and blinding. Author–LLM agreement reported as a supplementary check; never called human.
5–7. As D31: A4 from a family different from every N2 generator; N2 split by generator; headline hide-rate from the human-labeled sample with CI (scorer rate secondary); N2 +2–3 generator families, council-approved, length control.
8. Old pilot answered (D33). Development rounds excluded from confirmatory tests — implemented as excluding all 150 development launches (a superset of the 29 dev-probe rounds).
9. Everything validated this way is labeled "validated against a single hypothesis-aware human annotator".
Process: pipeline may start when the first-pass label file arrives; first-pass labels frozen on arrival; results PROVISIONAL until the self-consistency check is recorded.
Orchestrator implementation choices:
- File names: labels/author_pass1.csv (first pass; its arrival freezes FROZEN_RULES and the first-pass labels) and labels/author_pass2.csv (second pass, 20 repeats; must be saved ≥1 h after pass1 — checked from file timestamps and a self-reported time column).
- Model families: new N2 generators, the A4 scorer and the LLM annotator must ALL be distinct families from each other and from Qwen (primary scorer + generator) and Gemma (generator) — careful option so no judge shares a family with any generator.
- The 12 N2 packet items are gate measurement items (scored by the frozen primary scorer like other gate items); no N2 analysis before gate 1.

## D35 — A2 informativeness tier = INFORMATIVE (shuffled ranks only)
- gate1/A2_TIER.json (sha256 41cb1af9…): K_inf = 168 launches with within-round E variation (178 rounds); 144 launches excluding the 150 development launches. MDE80 = 0.0509 (null SD 0.0182; 400 shuffled fits, seeds 430000–430399). Both FR §7.1 criteria met (≥100 launches, MDE80 ≤ 0.10).
- No real ranks used (ranks pre-shuffled in analysis/scores/a2_long_shuffled.parquet via build_a2_long_shuffled.py).
- Because [R4] makes the confirmatory A2 exclude development launches, the tier must be recomputed on the dev-excluded set (144 launches) once [R4] lands, before unblinding; that recomputation is the tier of record.
- Implication: A2 is back as a real confirmatory test (previous expectation "not measurable" was based on the dev probe only).

## D36 — N2 extension council 3/3 APPROVE-WITH-CONDITIONS; orchestrator decision
- Generators added: Ministral-3-14B (Mistral), phi-4 (Microsoft), Llama-3.1-8B-Instruct (Meta) — Olmo-3.1-32B REJECTED (skeptic: its DPO data favours Qwen3 and gpt-oss-120b outputs -> shares lineage with scorer and annotator). Same 250 rounds, 5 cells, k=1, prompts, decoding; length covariate.
- A4 scorer: granite-4.2-30b (IBM), no reasoning parser; smoke ≥200 calls on DEVELOPMENT launches only; validity bar to be fixed in FROZEN_RULES before use (planning room); fallback granite-4.2-8B. Scope now: gate items + a seeded ~1,000-statement sample (cost cutter). A full A4 refit of A2 (~$5.9 worst) is DEFERRED to a separate council vote after gate 1.
- LLM annotator: gpt-oss-120b (OpenAI); settings (temperature, prompt = verbatim labeler instructions, blinding identical to the human packet) fixed in FROZEN_RULES before use. Supplementary only; never called human.
- 12 N2 packet items: seeded allocation 3,3,2,2,2 across the 5 generators, balanced over cells as far as possible; N2 validity claimed only for the pooled 12.
- Budget: N2 cap $10 -> $15 from the D15 reserve ($70 -> $65). A4 + annotator from the "council-approved new experiment" pool.
- Rule 8: serve_vllm.py vendored into P/serving/; no further edits to ../modal_serving. Every new app: scale-to-zero, short scaledown, one app at a time, container list empty after each; ≥32-request smoke per generator.
- N2 spec must be re-hashed for 5 generators, granite as A4, and the enlarged Holm family before any N2 scoring (methodologist blocker). No N2 scoring before gate-1 PASS.
- Methodologist note: D32's 123 label parse failures for scorer v2 contradict the scout packet's "0 parse failures" claim — the packet was wrong; D32 stands.

## D37 — human edit: optional volunteer second labeler (2026-11-15T19:16Z); labels/ verified empty
Human-authored (binding):
1. Volunteer packet: the same 50 first-pass items, different shuffled order, one spreadsheet-friendly file + one instructions .md. No scores, rankings, model names, conditions, hypothesis or project notes anywhere.
2. SHARE.md: exact full paths safe to send; files never to share (rules, scores, drafts, decisions, results); exact returned filename + columns; exact path where the author saves it.
3. Pre-specified switch: if the volunteer file is PRESENT when gate 1 runs -> primary agreement = two-human Cohen's kappa on the 50 shared items, cut-off 0.40, with CI; gate 1 uses labels adjudicated blind to scores. If ABSENT -> single-labeler design (D34). File presence at gate time decides, nothing else.
4. Author's second pass and the LLM annotator unchanged in both cases.
5. Paper: volunteer described as a "hypothesis-blind human annotator".
Orchestrator implementation choices:
- Returned file: labels/volunteer_pass1.csv (same columns as the author's file, item ids mapped by key held only in labels_build/).
- Freeze trigger stays the FIRST label file of any kind in labels/.
- "Gate time" = the moment gate1.py is first run on real labels; its output records which design applied and the file hashes it saw.
- Adjudication (two-human case): author and volunteer resolve disagreements together without seeing AI scores, rankings, model or condition; recorded in labels/ADJ.csv (adj_label).

## D37 - N2 analysis spec Amendment 2 (runner agent, 2026-11-16)
- N2_ANALYSIS_SPEC.md amended (section 10: 5 generators, Granite as A4, scorer 1 primary, second Holm family of 15, per-generator reporting, design-identity check, 12-item allocation rule, claim scope). New sha256 = 126787ad8c4932a3b4c9776f274e87b2e27787cd9cc7215cfe54e9f42c0dc60b. Supersedes 707c7fa2445051d1da64082d163c46bfbd6fde3ef2896dad2961ce03ffbd1146 for analysis; no N2 output has been scored.
- P/serving vendored (see P/serving/VENDORED.md): original serve_vllm.py sha256 32adf17d..., endpoints.json 667d86b0...; additive entries ministral3-14b, phi4-14b, granite4.2-30b (no reasoning parser), gptoss-120b. n2_grid.py now reads P/serving/endpoints.json (MODAL_ENDPOINTS), N2_CAP = 15 (budget.py dict still says 10; enforced through pilot_cap in n2_grid.py).

## D38 — planning room REPLAN R4 (consolidated): human edits D31 + D34 + D37 and council D36 written into FROZEN_RULES, EXPERIMENTS, PLAN (2026-11-15T19:06Z–19:27Z; pre-freeze)
- Checked at 19:06Z, 19:14Z, 19:16Z, 19:24Z and 19:27Z: labels/ has 0 files, FROZEN_RULES.md not read-only, no gate1/FREEZE.json. Blind: no ranking, rating, label, score file, sample.json, item_key.csv, A2_TIER.json, packet or real-rank output opened; features.parquet (sealed, D33) not touched. The informative-launch counts 168 / 144 were read in D32 and D35 (scorer output and shuffled ranks). The instructions changed three times while this was being written (D34, D36, D37 superseding or extending D31); the file holds the final consolidated state under one tag, [R4]. FR SHA-256 after R4: cf4a71ef8ca7dd485724a44c4c4401596319dfd839a11fef3546aebd074ebff1 (changes again with any later pre-freeze edit).
- **These edits change BRIEF §3.1 and §4** (who labels, agreement statistic, packet, file names). Authority: the human (D31, D34, D37). FR header says so and tells the reader that older "BRIEF §4 unchanged" sentences are superseded.
- **D31 edit 1 (kappa 0.40, 30+15+15): REPLACED by D34, extended by D37.** FR §5, §6.0–§6.2: single-labeler design = author (hypothesis-aware), labels/author_pass1.csv (50 rows: 38 originals + 12 N2) and author_pass2.csv (20 repeats = 15 + 5, seed 20261131, ≥ 1 h later, checked from mtime and a self-reported `pass_started_utc`), self-consistency kappa ≥ 0.60 with bootstrap CI and Gwet's AC1. Two-human design, only if labels/volunteer_pass1.csv EXISTS at gate time (= first poll at which author_pass1.csv is complete; written once to gate1/DESIGN.json): inter-rater kappa ≥ 0.40 on the 50 items, adjudication blind to scores in labels/ADJ.csv. Incomplete volunteer file at gate time keeps the two-human design; a late one is descriptive only. Freeze = first label file of any kind.
- **D31 edit 2 (12 N2 items): KEPT.** FR §6.1a, §6.6. Allocation = the N2 spec Amendment 2 rule (seed 20261116; 3,3,2,2,2 over generators and cells; no repeated pair) written out as exact code; items from outside development launches and outside the 60 sampled launches; scored by scorer 1 as gate items into gate1/n2check_scores.jsonl. Pass rule fixed: one-sided Fisher exact p ≤ 0.05 on the pooled 12, and gate 1 passed → N2_VALIDATED; else EXPLORATORY. Stated in advance that 12 items is very few: a scorer right on 80% of N2 items passes only 32–47% of the time (90%: 65–84%; chance about 1%); a PASS shows better-than-chance agreement pooled over generators and nothing per generator, per cell, or about the size of the accuracy.
- **D31 edit 3 (A4 family; N2 split by generator): KEPT.** Scorer 2 = granite-4.2-30b, fallback granite-4.2-8B (D36). FR §6.9 bar before use: V1 ≤ 5% statements without E on a ≥ 200-call development smoke (the only thing that can trigger the fallback); V2 own balanced-accuracy lower bound > 0.5 on the 38 gate items; V3 kappa with scorer 1 on a seeded 1,000-statement sample (250 rounds, seed 20261133), reference line 0.40. V3 changes the wording of scorer-1 results and never removes scorer 2 (dropping a robustness scorer for disagreeing would select on agreement). A4's beta_E is a Holm family test only if the council approves the full scorer-2 run before the first real-rank run and V1, V2 hold; otherwise exploratory.
- **D31 edit 4 (headline): KEPT.** FR §6.7: H = HIDES / definite labels on the 38 originals, labels of record (author first pass, or adjudicated); UNSURE excluded with both bounds printed; Wilson 95% (one item per round and launch, so no clustering); scorer rate secondary, printed beside it. About ±15 points at n = 38.
- **D31 edit 5 (N2 +families): KEPT.** Five generators (D36), same rounds / cells / k / prompts / decoding, length covariate, split by generator; spec of record = N2_ANALYSIS_SPEC.md with Amendment 2, sha256 126787ad…c60b (FR §7.3 note c, §10). N2_VALIDATED attaches only to scorer-1 estimates without the 45 development-launch rounds (planning-room choice beyond the literal edit; flagged, reversible pre-freeze; it changes no computation in the hashed spec).
- **D31 edit 6 (development exclusion): KEPT and now guaranteed.** Before R4, FR §2 made the all-launch A2 primary, so the exclusion was NOT guaranteed for A2 or Tier 2. Now the confirmatory set is the 721 non-development launches for gate 1, the N2 check, the headline, A2, the tier, N1, A4, A3, N3, N4 and prevalence; all-launch A2 = sensitivity A2d only (FR §2, §7, §7.1, §8, §9, §10 confirmation row). The 150 launches cover the 40 development-probe rounds (29–35 evaluable). The A2 tier of record must be re-run on that set with shuffled ranks before unblinding (D35 already says so); thresholds 50 / 100 / 0.10 untouched; disclosed that the 144 count was already logged.
- **D34 additions.** Gate-1 balanced accuracy against FIRST-PASS labels on the 38 originals (FR §6.4); PROVISIONAL_PASS state with stamps, one-way resolution and the weakness that results can exist before pass 2 (FR §6.5; N2 scoring still waits for the final PASS, per the spec and D36); LLM annotator gpt-oss-120b, temperature 0, seed 0, fresh call per item, volunteer-version instructions verbatim plus one format line, labels in gate1/llm_annotator/ (never labels/), hidden from the humans until their files are in, author–LLM kappa + AC1 with CI, supplementary and never called human (FR §6.8); wording "validated against a single hypothesis-aware human annotator" or the two-human form, volunteer = "hypothesis-blind human annotator" (FR header).
- **Sample-size consequences (synthetic labels only, seed 777; analysis/planning/r4_power.py, r4_selfconsistency.py, r4_twohuman.py with JSON + logs; gate1.kappa and the gate1.ba rule unchanged; same generating design as METHODS_EVAL G2).** Self-consistency kappa ≥ 0.60 at n = 20: 34% pass for per-pass repeatability 0.90, 70% at 0.95, 85% at 0.975, 16% at 0.85 (23% / 51% / 70% / 9% when three quarters of items are HIDES); memory not modelled. Two-human kappa ≥ 0.40 at n = 50: 88% (90%-accurate labelers), 52% (85%), 18% (80%), 5% (75%). BA rule at n = 38: chance 2.6–3.5%, true BA 0.70 → 55–70%, 0.80 → 88–98%. For the record, the superseded D31 design (kappa ≥ 0.40, n = 30): 82% at 90% accuracy, 49% at 85%, 22% at 80%, 5% at 70%. Output hashes: r4_power.json 835bb65b…a104, r4_selfconsistency.json c2c63d91…0f76, r4_twohuman.json a2480ef1…b979.
- **Not done / open.** No code changed: gate1.py (still 0.60 on 20 shared, 44 rows, 60 items, ADJ required), common.check_kind, the poller, build_analysis_set.py and the real-rank scripts' default set, the packet builder, a new llm_annotate.py — list in EXPERIMENTS "R4". The 44-row packets in labels_build/ and gate1/item_key.csv are void and must not be released. Granite and gpt-oss repository revisions are not in D36; runners pin them in the manifests. METHODS_EVAL.md, labels_build/README.md and N2_ANALYSIS_SPEC.md were read, not edited.
- **Weakest points of R4.** In the single-labeler design no hypothesis-blind human sees any item, and self-consistency cannot detect bias; the PROVISIONAL state lets results exist before the gate is final; 12 N2 items cannot separate an adequate scorer from a good one; A4 no longer re-estimates beta_E unless a later vote pays for it; the agreement rule changed three times in twenty minutes, each time by the human and blind to labels, and the paper must say so.

## D38 - N2 extension: generator smokes, 12 packet texts, re-plan (runner agent, 2026-11-16)
- Smokes (8 rounds x 5 cells = 40 requests, outside the N2 sample, list-price actual): ministral3-14b $0.170, phi4-14b $0.151, llama3.1-8b $0.224; containers of these apps confirmed empty after each stage. Ministral: 2 of 8 ACC-COMMON outputs open with "Here is/Here's" (cell preamble 25% > 10% flag; 2/40 overall) and over-cap rates 38-75% per cell; no prompt change made (council vote needed). RE_PREAMBLE regex corrected for the curly apostrophe (bug fix, not a threshold change).
- Packet selection: P/labels_build/n2_packet_selection.json (seed 20261116, ids only) written before any extension text existed; the 7 new-generator items generated first (priority mode, $0.496 actual); all 12 texts exist; none read or scored.
- P/serving: ministral3-14b, phi4-14b, llama3.1-8b deployed (scale-to-zero); granite4.2-30b and gptoss-120b defined only, not deployed.

## D39 — R4 packets built and verified; SHARE.md ready
- labels_build/r4/: author pass1 (50 = 38 original + 12 N2) and pass2 (20 repeats = 15 original + 5 N2); volunteer packet (same 50, different order, v-ids) as one CSV + one instructions .md; r4_verify.py passes (no dev launches; same 50 items; no leakage terms). Pre-R4 44-row packets archived as void.
- Orchestrator spot-check of VOLUNTEER_INSTRUCTIONS.md: no hypothesis/model/score/rank/project terms found.
- Id seeds 20261140–42 chosen by builder (not fixed in FROZEN) — implementation choice.
- Known blinding limitation (disclosed, not fixed — FROZEN 6.1a forbids editing text): 2 of the 12 N2 statements contain markdown **bold**, which no original statement has; this can reveal they are model-generated.
- Consequence of the D37 rule made explicit in SHARE.md: the volunteer file must be in labels/ before or together with author_pass1.csv, because gate 1 runs when the first-pass file arrives.

## D40 — R4 code implemented
- gate1.py rewritten (both designs; DESIGN.json write-once; PROVISIONAL_PASS; ≥1 h pass-2 rule; Fisher N2 check; headline Wilson; LLM supplementary). test_r4 (61), test_all, test_r1, test_fixes pass on dummy data.
- Dev launches excluded by default from A2, N1, N4, A3, N3; include_dev only for the A2d sensitivity run.
- Tier of record gate1/A2_TIER_R4.json (shuffled ranks, dev-excluded, 721 launches): K_inf=144, R_inf=152, MDE80=0.0563 -> INFORMATIVE. A2 is a confirmatory test.
- Not built yet: adjudication-sheet script, freeze writer, A4 (granite) validity bars + smoke, annotator smoke -> assigned.

## D41 — freeze + adjudication scripts built
- analysis/freeze.py, make_adjudication_sheet.py, test_freeze_adj.py (20/20 on dummy temp dirs). Real FROZEN_RULES and labels/ untouched.
- Path decision: FROZEN_RULES and gate1.py read gate1/FREEZE.json, so freeze.py is always run with `--out gate1\FREEZE.json` (FROZEN path wins over the brief's ad-hoc P\FREEZE.json).
- Procedure on label arrival (orchestrator): label-watcher fires -> run `python -I analysis/freeze.py --out gate1\FREEZE.json` immediately -> then gate1.py.

## D42 — N2 extension complete; Ministral preambles
- 3,750 statements (ministral3-14b, phi4-14b, llama3.1-8b x 250 rounds x 5 cells, k=1), plan 2d50922f…, $1.08 (worst $2.58). 0 errors/truncations/empty/think leaks/refusals; no near-duplicates. Cumulative ledger $9.47 of $200.
- Ministral preambles ("Here is…") per 250: ACC-COMMON 16, NEU-COMMON 63, SAT-COMMON 18, SAT-DIS 12, ACC-DIS 0; phi-4/llama 0. Over-cap: ministral 40–72%, phi-4 2–17%, llama ~0%.
- Decision: NO regeneration and NO prompt change (would break the identical-design rule across generators). Handle in analysis, fixed BEFORE any scoring: preamble flag as a pre-registered covariate plus a sensitivity analysis excluding preambled statements; length covariate already in place; generator-split reporting will show Ministral's cells separately. N2 spec amendment 3 (new hash) assigned to the N2 code owner.

## D43 - N2 analysis spec Amendment 3, preamble flag (runner agent, 2026-11-16)
- N2_ANALYSIS_SPEC.md section 11: per-statement preamble flag (rule = RE_PREAMBLE, applied to first 80 chars), covariate in every primary model, pre-registered sensitivity excluding preambled statements, scorer scores statements as stored, generator-split reporting kept. New sha256 = 9a966d5766d41c676fd3255ea5559fd08f524709a48614b45e93700094c81c0d. Supersedes 126787ad8c4932a3b4c9776f274e87b2e27787cd9cc7215cfe54e9f42c0dc60b. n2_grid.py sha256 at amendment = 01690939de350b0825111b7064786ddc2dc724176115d8ba6b3134bb2b65c70e. No N2 output scored.

## D41 - A4 scorer-2 V1 smoke and LLM-annotator format try-out (scorer runner, dev launches only)
- granite-4.2-30b (rev 9e668ce1.., no reasoning parser, thinking off): 70 dev rounds, 487 calls, 211/280 statements without E = 75.4% (bar 5%): V1 MISSED. Extraction 2/70 failed after retry; no think text, no empty content. Failure is systematic: for a round with ONE crux the model returns TWO labels (length mismatch, parse failure by the frozen rule); 2-crux rounds parse. Likely driven by the L1 output template with its trailing "..." (hypothesis, not tested: prompts are frozen).
- Fallback granite-4.2-8b (rev a7042144.., added to P/serving additively): same smoke, 483 calls, 161/280 = 57.5%: V1 MISSED, same cause. By FR 6.9: no scorer 2; A4 reported as "not run: no second scorer met the technical bar" and leaves the Holm family. No gate or N2 item was scored by either model.
- gpt-oss-120b annotator format try-out: 10 dev items, 10/10 valid on first attempt, no format-line revision used. Packet items not touched; annotator_manifest.json not yet written (to be written before the first packet call).
- Code: analysis/a4_bar.py (v1 run; draw, v2, v3 tested on synthetic or scorer-1-vs-itself data only). V3 interval is a launch-cluster percentile bootstrap (the section 7 method of record is regression-only): flagged for the planning room.
- Spend about $1.1 (granite30 0.39 + granite8 0.16 + gptoss 0.49 + CPU downloads ~0.05).

## D44 — A4 scorer candidates fail the technical bar; annotator passes
- granite-4.2-30b: 75.4% of dev statements without E (bar 5%); granite-4.2-8b fallback: 57.5%. Failure mode: on 1-crux rounds the model returns two labels, rejected by the frozen parser. Prompt untouched. ~$1.1 spent.
- gpt-oss-120b annotator: valid labels on 10/10 development items. annotator_manifest.json to be written before it runs on packet items.
- Decision (labels/ still empty, so pre-freeze changes allowed): one more attempt — planning room adds an ordered fallback list of ≤2 candidate A4 models from families distinct from every generator, the scorer and the annotator (e.g. TII Falcon-H1, Cohere Command), each smoked under the same bar (≤$2 each). If none passes before the rules freeze, A4 is reported as "not run: no candidate passed the pre-registered technical bar" — no parser or prompt change to make a model pass.
- Planning room also to confirm a4_bar.py's v3 interval (launch-cluster percentile bootstrap) since the method of record covers regression coefficients only.

## D45 — planning room R4a: A4 fallback list and V3 interval written into FROZEN_RULES (2026-11-15T20:18Z–20:21Z; pre-freeze)
- Checked at 20:18Z and 20:19Z: labels/ has 0 files, FROZEN_RULES.md not read-only, no gate1/FREEZE.json. No ranking, rating, label, score or smoke output opened; Granite failure rates quoted from D44.
- FR §6.9 [R4a]: closed, ordered fallback list for scorer 2 — (1) tiiuae/Falcon-H1-34B-Instruct (TII), (2) CohereLabs/c4ai-command-r7b-12-2024 (Cohere). Same V1 bar (≥ 200 development-launch calls, ≤ 5% statements without E after the one retry), same frozen prompts, decoding and parser; nothing changed to help a model pass; first to meet V1 is scorer 2; second tried only if the first fails or cannot be deployed; $2 each. If neither passes before freeze: A4 = "not run: no candidate passed the pre-registered technical bar", out of the Holm family, all four smoke results printed, no further candidate.
- Lineage check from the model cards (opened 2026-11-15): Falcon-H1 is TII's hybrid Transformer + Mamba architecture, base = TII's own Falcon-H1-34B-Base; Command R7B lists no base model (Cohere pretraining + SFT + preference training). Neither names Qwen, Llama, Mistral, Gemma, Phi, Granite or an OpenAI model as base or teacher. NOT verified: neither card says "trained from scratch" or lists training data, so synthetic data from other families is not ruled out, only not indicated. Why Falcon first: closest in size to scorer 1 and not shown as gated.
- NEEDS-HUMAN if candidate 2 is reached: Command R7B is gated (terms accepted on the hub by the account holder) and CC-BY-NC. Without that step it counts as not deployable.
- V3 interval CONFIRMED, not replaced: launch-cluster percentile bootstrap, B = 10,000, default_rng(20261121), as in analysis/a4_bar.py. My R4 text pointed V3 at the §7 wild bootstrap-t; that was an error (needs a regression coefficient and a cluster-robust SE) and is corrected. Descriptive only: coverage unchecked, the 0.40 line is read on the point estimate, no rule reads the interval.
- Follow-up for the code owner: N2_ANALYSIS_SPEC.md names Granite as A4; if scorer 2 becomes Falcon or Command, or there is none, the spec needs an amendment and a new hash before any N2 scoring. Serving-image suitability for Falcon-H1 (card asks vLLM ≥ 0.9.0) is the scorer runner's to establish and log.

## D44 - N2 analysis spec Amendment 4, A4 scorer identity (runner agent, 2026-11-16)
- N2_ANALYSIS_SPEC.md section 12: Granite replaced by "the A4 scorer selected under FROZEN_RULES 6.9 (R4a), or none" (Falcon-H1-34B, then Command R7B; if none passes, N2 A4 reads are dropped). No other change. New sha256 = 4085b78d6e99e4620edcc19237c79d6b865e2b6f2b3a09d5e37643201677ba91. Supersedes 9a966d5766d41c676fd3255ea5559fd08f524709a48614b45e93700094c81c0d. No N2 output scored.

## D46 - A4 fallbacks smoked (scorer runner)
- Falcon-H1-34B-Instruct (rev 6e6890e2.., vLLM v0.32.0 loaded it, 1x H200, no extra args): 70 dev rounds, 299 calls, 15 of 280 statements without E after the retry = 5.36% against a bar of 5%: V1 MISSED (extraction 1/70, labels 11 failed). Not rounded; no re-run. $1.05.
- Command R7B (rev 4f3d0aa6..): gated=auto; download with the pilot HF secret returned 403 GatedRepoError ("not in the authorized list"): NOT DEPLOYABLE, counts as missing V1 (FR 6.9 R4a). Access not requested (NEEDS-HUMAN if wanted).
- All four candidates failed: granite-30b 75.4%, granite-8b 57.5%, Falcon-H1-34B 5.36%, Command R7B not deployable. By FR 6.9 R4a: no scorer 2, A4 not run.

## D47 — A4: all fallbacks fail or undeployable
- Falcon-H1-34B: 15/280 statements without E = 5.36% vs bar 5% -> FAIL (by 0.36 points). Not re-run; no prompt/parser change; the bar is not relaxed after seeing the result.
- Command R7B: gated (403); not deployable unless the human accepts its licence.
- Decision: under FR §6.9 R4a, A4 = NOT RUN ("no candidate passed the pre-registered technical bar"), leaves the Holm family; N2 reported with scorer 1 only, split by generator. Single exception already allowed by R4a: if the human grants Command R7B access BEFORE the first label file arrives, it is smoked under the same bar. After freeze, no change.
- Limitation to report: a single LLM scorer (Qwen3.8-27B), which is also one of the five N2 generators; its own-generator cell is flagged in generator-split results.

## D48 — A4 candidate 2 (Command R7B) smoked after licence acceptance: V1 MISSED; A4 stays NOT RUN (scorer runner, 2026-11-16)
- Preconditions: labels/ had 0 files when checked at the start and again immediately before the GPU launch; no gate1/FREEZE.json. This is the single exception D47 allowed.
- Licence accepted on the hub by the account holder (2026-11-16). CPU download with the pilot HF secret now succeeded (11 files, rev 4f3d0aa6856e322f2f4480fe65420d5d53d297b8, $0.013).
- Smoke under FR 6.9 [R4a], same as Falcon (D46): `scorer.py probe --scorer command-r7b --probe-rounds 70 --cold-start-s 300`, 70 dev rounds only, frozen E1/L1 (sha256 unchanged), temperature 0, seed 0, one retry with seed 1, response_format json_object, thinking-off kwarg, frozen parser. Served by serve_vllm.py as registered (1x L40S, vLLM v0.32.0, chat template as shipped, no extra load args). The only code change was registering the alias in scorer.py SCORERS and the deployed URL in serving/endpoints.json.
- Result: 427 calls (bar >= 200: met); 78 of 280 statements without E after the retry = 27.857% (bar <= 5%): **V1 MISSED**. Extraction 0/70 failed; all 78 are label calls that still failed to parse after the retry (by crux count: 1-crux 12, 2-crux 18, 3-crux 47, 4-crux 1); 1 truncated call. Not rounded for the decision, not re-run, nothing changed. Cost $0.1877 session + $0.013 download = $0.20 (cap $2).
- Decision: by FR 6.9 [R4a] neither listed candidate met V1, the list is closed, so there is **no scorer 2**: A4 = "not run: no candidate passed the pre-registered technical bar", out of the Holm family; N2 has no robustness scorer and says so. N2_ANALYSIS_SPEC.md §12 already provides for "or none", so no spec change.
- All smoke results to print (statements without E after the retry, bar 5%): granite-4.2-30b 75.4% (211/280); granite-4.2-8b 57.5% (161/280); Falcon-H1-34B 5.36% (15/280); Command R7B first attempt not deployable (403 gated); Command R7B after licence acceptance 27.857% (78/280).
- Defect noted: scorer.py's post-run container check returned empty output (UnicodeDecodeError in its subprocess reader because the run used `python -X utf8`), so summary.json/ledger say "0 rows, waited 2 s". A manual bounded poll showed our container ta-01M7GWBFVMHDT68F7D8Z7MPCER alive for ~113 s more, then scaled to zero by itself; nothing stopped (container_check_manual.json; ledger correction row). The deployed app pilot-vllm-command-r7b stays deployed at min_containers=0 (no idle cost), like the other A4 apps.

## D49 — Labelling redesign by the human (2026-11-16T00:50Z; supersedes the R4 labelling design, D34/D37)
- Human instruction (verbatim intent): no volunteer; full labelling proved too heavy. (1) Inventory the existing human signals in the dataset; (2) if any exist, pre-specify a human-derived reference for "hidden disagreement" from them BEFORE any comparison with the scorer, and use it as the primary validation, worded "validated against participants' own responses"; (3) a 25-item verification packet (19 original, 6 N2): an LLM from a family different from the scorer extracts the two most conflicting opinion quotes; the author answers "Do these quotes disagree?" and "Does the statement acknowledge it?"; scores, rankings, model and condition hidden; worded "human verification of LLM-extracted evidence by a hypothesis-aware author"; (4) a three-model LLM annotator panel of different families as a supplementary check, never called human; (5) if neither (2) nor (3) yields usable data, every result is exploratory and not human-validated, and all claims are adjusted. Log here and update FROZEN_RULES.md.
- Partial labels: `labels\` checked at 2026-11-16T00:49:53Z (directory listing only): 0 files. No partial author labels existed, so none were read, used or discarded. FROZEN_RULES is not frozen (no label file, no gate1\FREEZE.json) and may be amended (as R5).
- R4 packets in labels_build\r4\ are VOID (never shown to a labeller as far as the project knows; not sent). READY.md replaced with a "do not label" notice.
- Step 1 done: analysis/inspect_human_signals.py (schema and levels only; no join with scores or ranks) -> analysis/human_signals_inventory.json. Findings below in D49a.
- Wording frozen now: primary validation "validated against participants' own responses" (only if step 2 yields usable data); packet "human verification of LLM-extracted evidence by a hypothesis-aware author"; panel "LLM annotator panel (supplementary; not human)". The old "validated against a single hypothesis-aware human annotator" wording is withdrawn.

## D49a — Step 1 result: existing human signals (analysis/human_signals_levels.json; counts only, no scores loaded, no ranks read)
Human-citizen rows only. Levels:
1. Pre/post position ratings (hm_all_position_statement_ratings): per PARTICIPANT x question, 7-point agreement with the question itself, before (rating_index 0: 21,178) and after (1: 18,993) deliberation; 6,869 participants, 1,514 launches. A human measure of whether the GROUP really disagrees, independent of any candidate statement.
2. Per-candidate agreement and quality ratings (candidate_comparisons ratings.agreement / ratings.quality): per RATER x CANDIDATE, 7-point, in every round (mostly 4 candidates). Collected alongside the rankings and strongly tied to rank (Experiment 0 slope -0.576), so circular for any validation of a rank-related hypothesis.
3. Critiques (critique.text): per PARTICIPANT, written on the iteration-0 WINNING statement only (they appear only on iteration-1 rows): 15,754 completed, 3,770 rounds, 1,274 launches. Free text: needs coding.
4. Ranking explanations: 1,750 free-text, iteration 0, some cohorts only.
5. Round survey (hm_all_round_survey_responses): per PARTICIPANT x round about the displayed final statement: best_expression (FINAL_CONSENSUS 11,703 / OWN_OPINION 7,082), own_influence (YES 12,150 / NO 6,635), unwanted_pressure, view_change, view_movement, view_explanation (11,592 free text).
6. Outside-judge ratings: NONE in the four released files.
No human signal says directly whether a given statement acknowledges the group's disagreement. The step-2 reference has to be built from (1) for "disagreement exists" plus a participant-level signal about a statement (2, 3 or 5), each with a known problem (circular; winner-only; needs coding). Decided by the planning room + council (D50) BEFORE any reference value is computed or compared with the scorer.

## D49b — Step 3 packet spec (orchestrator, fixed before any item is built)
- Items: subset of the R4 author pass-1 sample (already drawn under FR 6.1, dev launches excluded): 19 of its 38 original items by simple random draw, plus 6 of its 12 N2 items = 1 per generator (qwen3.8-27b, gemma4-12b, ministral3-14b, phi4-14b, llama3.1-8b) + 1 drawn from the remaining N2. Excluded beforehand: N2 items containing markdown (`**`, `#`, list bullets) because they reveal the condition. Seed 20261116. Ordered reserve list drawn the same way for replacements.
- Evidence extraction: gpt-oss-120b (OpenAI family; differs from the scorer Qwen and all five generators; format smoke passed D41). Input: question + the round's opinions (never the statement, scores or ranks). Output: the two most conflicting quotes, each an exact substring of a DIFFERENT participant's opinion, verified by code; one retry with seed 1; still invalid -> item replaced from the reserve in order, logged.
- Author sees per item: question, quote A, quote B, statement. Hidden: scores, rankings, model, condition, original/N2, participant ids. Answers: Q1 "Do these quotes disagree?" yes/no; Q2 "Does the statement acknowledge this disagreement?" yes/no (always answered). Optional comment.
- Save path: labels\author_verification.csv. Saving it freezes FROZEN_RULES (as before: first label file of any kind).

## D49c — Packet: ministral slot (orchestrator, 2026-11-16 ~01:00Z; before any extraction or draw output)
- Problem (packet builder): both ministral3-14b items in the R4 pass-1 sample contain markdown bold, so D49b's "1 per generator, markdown excluded" cannot be met inside that sample.
- Decision: option (a). The ministral slot is drawn from the N2 full_ext ministral3-14b generations using the same eligibility as labels_build\n2_packet_selection.json (non-dev launch, round not in the gate-1 sample), markdown-free, seed 20261116, with an ordered reserve. Rejected: (b), because it loses the per-generator coverage that a 6-item N2 set exists for; and (c), because it edits stimulus text (FR 6.1a).
- Disclosure: the ministral item shown is, by construction, a markdown-free ministral output and may be less typical of that generator; the share of ministral outputs with markdown is reported (count only).

## D49d — Report draft complete on dummy data (drafter, 2026-11-16 ~01:10Z); follow-ups fixed by the orchestrator
- report\build\out\DRAFT_layout.pdf: every section written, results are slots, every page stamped DUMMY / NOT RESULTS. Body is 8 pages with one outcome branch per group (at the cap). 74 markers remain (DRAFT_STATUS.md). The D49 validation text is still a slot.
- Decided now:
  (1) The ethics line "opinion texts processed only on self-hosted models" is FALSE as written: Claude agents (Anthropic API) read opinion and statement texts (e.g. D22 skeptic examples, packet checks). The draft must say so plainly; the dataset is public CC-BY 4.0.
  (2) Evaluable-round counts (D32 1,409 vs A2_TIER_R4 1,464 all / 1,211 confirmatory) must be reconciled by script before any number is quoted; the results room owns it.
  (3) The FROZEN_RULES §7.3(c)/§10 stale N2 spec hash (126787ad…) is to be corrected in R5 to the hash of record 4085b78d… (Amendment 4) or its successor.
  (4) Dev-launch wording: "excluded from all confirmatory tests; reported only in labelled sensitivity analyses and side counts" (covers FR's side figures).
  (5) No blind-labelling claim anywhere (BRIEF §10 cannot be met; disclosed as a limitation).
  (6) Milli et al. 2024: drop the sentence unless the verifier rechecks and adds it to refs.bib.
  (7) figures\dummy_out\captions.md "blind human labels" caption is not to be reused.

## D50 — R5 council: 3/3 APPROVE-WITH-CONDITIONS (R5_vote_statistician.md, R5_vote_skeptic.md, R5_vote_editor.md); orchestrator synthesis
- Adopted: analysis\council\R5_PROPOSAL.md (sha 9eb7f7c5…71aa46) with ALL conditions of the statistician (1–9) and the skeptic (1–9), and editor conditions 1–4, 6 and 7.
- REJECTED: editor condition 5 (score N2 now with sealed outputs). It conflicts with the human's standing instruction "Do not score N2 or run real-data analyses before gate 1". N2 scoring waits for the recorded gate.
- Open questions settled: (1) scoped wording only: "the scorer's detection of disagreement was validated against participants' own pre-deliberation position ratings"; the bare D49 phrase is never used; (2) step 2 kept, as a PRESENCE check only; (3) keep the 0.60 point bar plus a lower bound > 0.5, with each Hsplit class ≥ 50 rounds from ≥ 25 launches, and UNUSABLE if > 1% of resamples are single-class; question-cluster bootstrap too, the smaller lower bound decides; (4) panel = Falcon-H1-34B, Command R7B, granite-4.2-30b; gpt-oss-120b excluded (it extracts the quotes); format bar ≥ 20 calls and ≥ 95% valid after one retry per model; fewer than 2 passing = "no panel"; P2 dropped; (5) yes: usable but unsupported -> exploratory (stricter than D49 item 5); (6) step 3 CONTRADICTED does not fail the gate but makes every E-based result EXPLORATORY_UNVALIDATED; (7) N2 is never "validated"; N2 spec Amendment 5 with a new hash; (8) survey and critique analyses are NOT run (cut for time; no pre-stated estimand).
- Under VALIDATED_PRESENCE, A2 stays the pre-registered test (Holm family), but its hiding measure is reported as "not human-validated"; no confirmatory claim about hiding.
- Also into R5: correct the stale N2 hash in FR §7.3(c)/§10 (D49d item 3).

## D51 — Human instruction: time-out for the author's verification file (2026-11-16T01:09Z)
- Human (verbatim intent): if the author has not submitted the verification answers within 30 minutes after READY.md is published, use "option c": different models do it instead.
- Implementation (orchestrator's reading, logged; careful option per BRIEF §14):
  1. Clock: T_ready = the UTC time READY.md is rewritten as ready (logged here when it happens). T_cut = T_ready + 30 min.
  2. If labels\author_verification.csv is absent at T_cut: step 3 is recorded as "NOT DONE (no author file by T_cut)". The R5 panel (three LLMs from different families: Falcon-H1-34B, Command R7B, granite-4.2-30b) answers the same two packet questions on the same 25 items. This is reported ONLY as "LLM verification of LLM-extracted evidence (supplementary; not human)". It never counts as step 3, is never called human, and never contributes a human label (BRIEF rule 1 holds: no human label is created or simulated).
  3. The gate is then recorded from step 2 alone (the participant presence check). Its validation status can be at most VALIDATED_PRESENCE. The hiding measure is "not human-validated"; with step 2 also unusable or failing, everything is EXPLORATORY_UNVALIDATED (D49 item 5).
  4. The freeze happens before the step-2 reference is computed (gate1\FREEZE.json), as in R5.
  5. An author file arriving after T_cut is not used for the gate. It is reported as a labelled post-gate check, with its arrival time.

## D49e — Packet fix before release (orchestrator review, 2026-11-16T01:16Z; packet never shown to the author)
- Orchestrator read-through of packet_verification.html (sha 0ef08cad…): the ministral3-14b item (v5-02, full_ext b581bf2c… ACC-COMMON) contains single-asterisk markdown italics (4 spans). D49b's rule "markdown excluded" was implemented as `**`/`#`/bullets only, so italics slipped through. This is a filter defect, not a judgement on content.
- Fix: the markdown filter becomes: any `*x*`, `**x**`, `_x_`, backtick, heading `#`, bullet or numbered-list line. Re-apply it to ALL six N2 slots (the other five currently pass) and redraw the ministral slot by walking the existing ordered ministral reserve (seed 20261116), taking the first item that passes. Extract quotes for that item only (same X1, seeds 0/1), rebuild the packet, re-verify, and report the corrected count of markdown-containing ministral full_ext outputs. Nothing else changes; the order seed is unchanged.
- Non-ASCII typographic characters (curly quotes, dashes) also occur in original items (v5-10, v5-11, v5-23), so they are not a condition tell; left as is.

## D50a — R5 applied to FROZEN_RULES.md; N2 spec Amendment 5; R5 gate code (planning room, 2026-11-16)
- Pre-edit check, directory listing only, at 2026-11-16T01:17:05Z: `labels\` 0 files; `gate1\FREEZE.json` absent; FROZEN_RULES.md writable, sha256 2ff8d6f6…de99. Re-checked after the edits: unchanged (0 files, no FREEZE.json).
- FROZEN_RULES.md (R5 = R5_PROPOSAL + every D50-adopted condition + D50 settlements + D51 time-out; §5 and §6.0–6.8 marked superseded, text kept; freeze trigger in the header; new §6.R5; §7.3 R5 reading; §12 R5 note; Known weaknesses 11–15; Replan log "R5"; stale N2 hash in §7.3(c) and §10 corrected). New sha256 = 66b49163626f771a778cd7d7528220236ddfd42b1797b6c266b47942fc8fb5a3 (supersedes 2ff8d6f6168ec2db36bd064408e3789d130b5c214b4ddf4625d3db354c1cde99).
- N2_ANALYSIS_SPEC.md Amendment 5 (§13: N2 never "validated"; validation wording follows the R5 status; no N2 scoring beyond the packet items before an R5 status is recorded; gpt-oss annotator role replaced). New sha256 = afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0 (supersedes 4085b78d6e99e4620edcc19237c79d6b865e2b6f2b3a09d5e37643201677ba91). D50 approved the Amendment-5 path; this hash is the spec of record cited in FR §7.3(c)/§10.
- Code (synthetic tests only; nothing run on real data): analysis/step2_reference.py 47486cf0…3f76; analysis/verification_eval.py a964ab53…f138; analysis/gate1_r5.py 9e640041…3ce1 (D51 time-out: reads gate1\T_READY.txt; T_cut = T_ready + 30 min); analysis/freeze.py 28376f98…7f74 (adds `--trigger step2`, R5 tracked files, `gate1\R5_FREEZE_MANIFEST.json` hook; default behaviour unchanged); analysis/common.py 98af4bee…dda3 (check_kind accepts GATE1_RESULT.json with "rules": "R5"); analysis/test_r5.py 29e38b96…9879.
- Tests: test_r5 105/105 PASS (incl. "only BA2 decides", D51 author file before T_cut / absent at T_cut / after T_cut / incomplete at T_cut); test_all, test_r1, test_fixes, test_r4, test_freeze_adj all PASS.
- Design calculation re-run per statistician condition 7: analysis/planning/r5_step3_power.py --usable -> r5_step3_power_usable.json (5f9ab42118693e95c0043ffb303b1c2d70d2f9d6c138e0adf088a31e41d2e50d), synthetic, seed 777; figures printed in FR §6.R5.3.
- Choices made in applying (logged as orchestrator-readable judgement): step-3 bootstrap seed 20261144 and panel seed 20261145 (proposal seeds would have collided with the step-2 question bootstrap 20261142); an author file present but INCOMPLETE at T_cut counts as not submitted (reading of D51, careful option); a file completed or corrected after T_cut is LATE.
- Follow-ups: packet builder writes gate1\R5_FREEZE_MANIFEST.json (packet, key, quotes, 25-item scorer outputs) before release; orchestrator writes gate1\T_READY.txt at READY.md publication; author-exposure entry (skeptic 5) before the author file is hashed; draft frames per status (editor 2); panel smokes on dev launches only.
- D51 clock: READY.md published as ready at 2026-11-16T01:23Z (packet sha 5371023f…, verify.py 34/34 PASS, orchestrator re-ran verify and read the fixed item v5-02). T_ready = 01:23Z, T_cut = 01:53Z. Written to gate1\T_READY.txt.
- **Superseding update (planning room, after the orchestrator's 01:23Z message; re-check at 2026-11-16T01:23:56Z: `labels\` 0 files, no FREEZE.json).** Step-3 file columns aligned to the final packet (`item_id,q1_quotes_disagree,q2_statement_acknowledges,comment,pass_started_utc`, tokens yes/no, case-insensitive); item ids and kind read from `labels_build\v5\key_verification.csv` (mismatch with the scores file stops step 3); FR §6.R5.2 records T_READY 01:23Z / T_cut 01:53Z. **Hashes of record (these replace the FR and code hashes in the bullets above):** FROZEN_RULES.md = ea9b7a97256eb3bca95ccb0c1135a7ff32d3d520eeb6f484c9c8898f996f94ae (supersedes 66b49163… and 2ff8d6f6…); N2_ANALYSIS_SPEC.md = afada11746b1dc787888cd421aeaca9997204fb96f13def823ef2c59575091c0 (unchanged); step2_reference.py 47486cf0…3f76; verification_eval.py 2e22b2a0e411153305d028fa8bfad8a6ac5c2da760c04b7359d55a920fa339af; gate1_r5.py 9e640041…3ce1; freeze.py 28376f98…7f74; common.py 98af4bee…dda3; test_r5.py fcc786c0389ae25bdadb1a790cec00ccc592b59dce8b2aefcf1e9d3aad2b0791. test_r5 110/110 PASS (adds key checks, template-header match, T_READY "HH:MMZ" format).
- **OPEN, blocking step 3:** `verification_eval.py --scores` needs a jsonl of scorer-1 outputs for the 25 packet items (item_id, kind, E, n_cruxes, ok), built from the existing gate1 scores for the 19 originals and a scorer-1 run on the 6 N2 packet items, listed in gate1\R5_FREEZE_MANIFEST.json and hashed BEFORE the author file is read. No such file exists yet; nobody has built it.

## D50b — Step-3 inputs fixed before the author file exists (orchestrator, 2026-11-16T01:40Z; labels\ empty)
- analysis\scores\packet_v5_scores.jsonl (sha b8e92c31…f936): 25 rows, 24 ok (1 original whose v2 label parse had already failed, counted per the parse rule). 19 originals reused from v2 gate1 scores (identical in a2_scores_v2); 6 N2 packet items scored once with frozen scorer v2 as gate measurement items (D34), 14 calls, 0 parse failures, $0.3657. No other N2 text scored.
- gate1\R5_FREEZE_MANIFEST.json written by the orchestrator (the packet builder had not written it): packet, key, quotes, selection, scores file, gate scripts, scorer + manifest, N2 spec, T_READY.
- Caveat: scorer.py sha now 1413ad6a… vs manifest script_sha256 56e46042…; the edits after the manifest only registered A4 aliases (D44–D48 runner reports); E1/L1 prompt hashes match the manifest. Not diffed (no saved copy of the old script): disclosed as is.
- Author exposure (skeptic condition 5), logged before the author file is hashed: the 19 originals and the qwen/gemma/phi/llama N2 items are a subset of the R4 author pass-1 packet (labels_build\r4\packet_author_pass1.html), which existed from 2026-11-15 ~23:30Z until voided at 2026-11-16T00:52Z. Whether the author opened it is unknown to the project; the author is asked to state it. The ministral item (full_ext) was never in any earlier packet. The author is hypothesis-aware in any case.

## D52 — Step 4 panel run (panel runner, 2026-11-16 ~01:30–01:45Z; before T_cut, nothing compared with author or scorer)
- PANEL formed: Falcon-H1-34B, Command R7B, granite-4.2-30b each 20/20 on the format bar (20 dev-launch items built with the X1 prompt, seed 20261146) and 25/25 valid on the packet, no retries. P1_prompt.md sha 9040afed…; decoding identical across models. Spend $1.4991 (incl. $0.4619 gpt-oss dev-item extraction).
- Majority answers: Q1 yes 21 / no 4; Q2 yes 12 / no 13. Inter-model Q1 Fleiss 0.649 [0.143, 0.921] (AC1 0.847); Q2 Fleiss 0.570 [0.297, 0.787] (AC1 0.577). n = 25.
- Deviations accepted by the orchestrator: (1) format-bar items had to be built (none existed), with a new seed; (2) prompt written by the runner, hashed before any call; (3) outputs in analysis\panel\ with identical copies + manifest in gate1\llm_panel\ (FR path).
- Panel outputs to be added to the freeze manifest.

## D53 — T_cut passed with no author file (2026-11-16T01:53:37Z)
- labels\ listed at 01:53:37Z and 01:53:41Z: 0 files. Per D51 and FR §6.R5: step 3 = NOT DONE (no author file by T_cut). The panel (D52) is reported only as "LLM verification of LLM-extracted evidence (supplementary; not human)". The gate is recorded from step 2 alone (at most VALIDATED_PRESENCE). A later author file = a labelled post-gate check.
- Next, in order: step2_reference.py --kind real (writes gate1\FREEZE.json first, trigger step2), then gate1_r5.py.

## D54 — Step 2 computed; gate status computed (not yet recorded)
- 01:53:53Z FREEZE.json written by step2_reference.py (trigger step2; labels\ empty; 0 missing tracked; 21 manifest files hashed); FROZEN_RULES.md now read-only.
- Step 2 (gate1\STEP2_computed__20261116T015355Z.json): 1,622 usable rounds / 721 launches; Hsplit classes 614 rounds (437 launches) vs 1,008 (605); BA2 = 0.6918, launch-cluster 95% [0.6690, 0.7140], question-cluster [0.6699, 0.7134], 0 single-class resamples -> PASS (lower bound > 0.5 and point >= 0.60). Sensitivity 0.900, specificity 0.484: the scorer finds a crux in about half of the groups whose members did NOT split on the question. To be reported in the main text (statistician condition 9).
- gate1_r5.py: computed status VALIDATED_PRESENCE (step 2 PASS; step 3 NOT DONE by D51). Awaiting the independent Opus re-derivation (§6.R5.6) before GATE1_RESULT.json is written.

## D55 — GATE 1 RECORDED: VALIDATED_PRESENCE (2026-11-16T02:05Z)
- Independent Opus re-derivation (analysis\review\GATE_REVIEW.md): AGREE; every step-2 number reproduced exactly; freeze preceded step 2; all 29 FREEZE hashes match; T_cut logic correct. Minor defects (no status effect): a2_extractions_v2.jsonl not in the freeze hashes (its hash is in the review); the strong-split variant handles missing extractions inconsistently; appendix Spearman differs by 7.9e-6 (ties).
- gate1\GATE1_RESULT.json written with "rules": "R5", status VALIDATED_PRESENCE (output tag HIDE_NOT_HUMAN_VALIDATED). Real-rank analyses unblocked under the §6.R5.6 wording limits; N2 scoring unblocked, always EXPLORATORY (§6.R5.7).

## D56 — N2 scoring unblocked under R5 (orchestrator, 2026-11-16T02:08Z)
- n2_grid.assert_scoring_allowed() accepts only status "PASS" (an R4-era guard). Writing "PASS" would misstate the gate. Decision: analysis\GATE1_PASSED.json records rules R5 / status VALIDATED_PRESENCE with the scorer-manifest hash (ed64b540…), and the guard is minimally edited to also accept a record with "rules": "R5" and a status in {VALIDATED_BOTH, VALIDATED_PRESENCE, VALIDATED_HIDE_EVIDENCE, EXPLORATORY_UNVALIDATED} (FR 6.R5.6). Logged code change after the freeze; it changes no analysis rule. N2 outputs are stamped EXPLORATORY.
- analysis\council\N2_SCORING_APPROVAL.json: max $5 (A2 full scoring basis: 7,840 statements = $2.45).

## D57 — Real-data results in (analysis\results\RESULTS_MAIN.md sha dc236afc…); N3 scoring approved
- A2 beta_E = +0.0511 [+0.0076, +0.0952], p = 0.024, 1,166 rounds / 642 launches; pre-registered sign reading (FR §7): > 0 = statements scored as hiding are ranked better. Status wording: "pre-registered test; the predictor's hide/show contrast is not human-validated". Tier INFORMATIVE (one-way check 0.061 ≤ 0.10).
- N1 +0.0084 [-0.0021, +0.0189] (Holm 0.115 / 0.231 conservative); N4 E x minority -0.1466 [-0.2522, -0.0406] (Holm 0.0156 / 0.0234 conservative). A2e (E_pos) -0.0228 [-0.0519, +0.0056].
- Count defect in a2_informativeness.py (rounds with partly missing E counted): corrected R_inf 150 / K_inf 142; the tier does not change (stated in the paper).
- N3 (iteration 1 vs 0) is in the Tier-2 family (FR §9) and qualifies (713 launches); its iteration-1 statements are unscored. Decision: score them with frozen scorer v2 (cap $3; A2 basis $2.45 for 7,840 statements), run serially AFTER the N2 scoring run ends (same app; avoids container conflicts), then compute N3 and the final Holm. If it cannot finish by 06:30Z, N3 is reported "not run: not scored in time" and the conservative Holm (N3 at p = 1) is the one of record.

## D58 — Red team (analysis\redteam\REDTEAM.md): no blockers; 7 MAJOR; orchestrator rulings
- Independent refit of A2 reproduces beta_E = +0.051085 (SE 0.021802). Analysis set, JSON-vs-table, pre-freeze rank access and the tier all check out.
- Rulings (the pre-registered estimates are unchanged; nothing is re-specified):
  1. Length dependence: the primary model stands as registered. The paper reports it in the main results (not only an appendix): without the length control the sign flips (-0.074); with flexible length controls (cubic, deciles, rank, raw words) |t| = 1.35–1.98. Labelled exploratory robustness (red-team scripts cited). The abstract describes A2 as "small and sensitive to how statement length is controlled".
  2. SIDED vs BLENDED/OMITTED split and majority (+0.10) vs minority (-0.05) raters: reported as exploratory; the paper says the data cannot separate "hides disagreement" from "states my side" (consistent with the A2b similarity sensitivity and with N4).
  3. A2b: the seed of record (20261119) decides; LB +0.0002 > 0, so the binding rule does not fire; the paper adds that the LB is <= 0 under 7 of 40 other seeds (i.e. a borderline result).
  4. Step-2 numbers (BA2, CI, sensitivity 0.90, specificity 0.48, class counts) go into the main results; plus "39 of the 150 informative A2 rounds come from groups whose members did not split".
  5. N4: add the minority rater-round counts (151 informative minority rater-rounds) and the FR §8 informative counts.
  6. Sealed features.parquet: VERIFIED (common.load_habermas_shuffled): the shuffled-data test mode read it programmatically, permuted ranks in memory before any fit, used a dummy E proxy, and wrote only shuffled-rank outputs (RUNS rows 360–362, 389–391, 468–470). No unshuffled rank statistic was computed or shown. D33/D38's "not touched" is CORRECTED to this; the paper's disclosure is rewritten to say exactly this.
  7. Draft wording: fixed during report filling (no "confirmatory", no bare D49 phrase, corrected 150/142 counts, VALIDATED_PRESENCE frame).

## D59 — N3 blocked by infrastructure; report draft filled (2026-11-16 ~02:50Z)
- N3: the qwen3.8-27b scorer app returned 503 "no upstreams" after the N2 run; 3 launch attempts, $0 spent. Ruling: one relaunch now and one at 04:00Z; if nothing is scored by 06:00Z, N3 = "NOT RUN: scorer app did not start (infrastructure), not a data decision", and the conservative Holm (N3 at p = 1: N1 0.2308, N4 0.0234) is the one of record.
- RESULTS_MAIN regenerated (sha 7f6ccdb5…) with the D58 items; red-team scripts re-run from copies reproduce exactly; informative rounds from non-split groups: 39 of 150.
- Report filled (VALIDATED_PRESENCE frame), body 8 pages. Orchestrator review of p.1: the abstract's "96% hid every point" is the pre-specified FR §7.3 descriptive (0.9613 [0.9551, 0.9674], 4,780 statements) but must say that most hiding is SIDED (82.8% of crux labels), given D58.2; and the abstract must carry one exploratory N2 sentence. Disclosed deviation: the per-status frames were not written before the gate (editor condition 2 missed); stated in Appendix A item 13.

## D60 — Report council (review_hostile.md 4/10; review_editor.md 15 edits): orchestrator rulings
- Apply all editor edits (new abstract with the SIDED clause and the N2 sentence; captions; intro), subject to the rulings below.
- A1: keep the computed confusion table (FR rule: failures count as wrong) and footnote it: "includes 3 extraction failures counted as wrong". Report 0.753 vs 0.755 consistently with that footnote.
- A2: "three families" (Granite x2) fixed. B2: the §6.R5.6 stamp goes next to every 96% mention. B3: the Methods pilot sentence corrected to all 1,960 rounds (per D33 and App. A item 9). B4: Zhu et al. claims trimmed to what references_verified.md supports.
- Panel vs scorer: not pre-specified to run without an author file, but it is evidence about the scorer and leaving it out would flatter the paper. Compute by script (analysis\panel_vs_scorer.py: panel-majority Q2 vs the scorer's E binarised at 0.5 on items where the panel-majority Q1 = yes; agreement, kappa with CI, n), report as EXPLORATORY "LLM-vs-LLM; not human" in Results (one sentence) + an appendix table.
- AI disclosure: orchestrator Claude Opus 5.5 (claude-opus-5-5) in Claude Code; subagent models per .claude/agents definitions (opus / sonnet / fable by role; general-purpose agents inherit Opus 5.5).

## D61 — N3 final: NOT RUN (infrastructure) (orchestrator, 2026-11-16T07:50Z)
- Four launch attempts 02:18–03:03Z; the Modal scorer app never started a container (503 "no upstreams"); $0 spent. The runner agent died at ~03:xx Z from a network error (API ENOTFOUND) before the 04:00Z retry, so the retry never ran. The D59 cut-off (06:00Z) has passed.
- Ruling per D59: N3 = "NOT RUN: the scorer app did not start (infrastructure), not a data decision". Holm of record = the conservative bound with N3 at p = 1: N1 Holm p 0.2308, N4 Holm p 0.0234.
- Also: the label watcher (15-min poll) was stopped by Claude Code for low system memory; not restarted (hard rule 9). labels\ was empty at 07:49Z.

## D62 — Human asks to do the verification now and extend it to 50 items (2026-11-16T08:39Z; post-gate, results known)
- Human: "25-item check now ... add more labels up to 50". Logged BEFORE any answer exists (labels\ empty at 08:26Z).
- Status: everything from this is a POST-GATE check (D51 item 5). It cannot change GATE1_RESULT.json (VALIDATED_PRESENCE) or any status. The author is hypothesis-aware AND had seen the results (A2, N2, the panel figures) before answering; the paper must say this in the same sentence as any number.
- Part 1 (items v5-01..25, packet already frozen in FREEZE.json): answers saved as labels\author_verification.csv; analysed with the frozen analysis\verification_eval.py exactly as R5 step 3 specifies (Q1 rate; scorer E>=0.5 vs Q2 on Q1-yes items; one-sided conditional Fisher; Wilson CIs; usable rule), reported as "post-gate, results-aware human verification of LLM-extracted evidence by a hypothesis-aware author".
- Part 2 (items v5b-26..50, new): 25 more items built by the same procedure (D49b–e): the 19 R4 pass-1 reserve originals in their existing reserve order, plus 6 N2 (1 per generator + 1 extra) from the existing ordered N2/ministral reserves, strict markdown filter, gpt-oss-120b X1 quotes (same prompt, seeds 0/1), same blind packet format. Scorer E for these comes from the EXISTING v2 scores (a2_scores_v2 / gate1_scores for originals; n2_scores_v2 for N2); no new scoring. Answers saved as labels\author_verification_b.csv. Analysed with the same script, reported separately for Part 2 and pooled (n up to 50), all labelled exploratory, post-gate, results-aware.
- If Part 2 cannot be built and verified by 09:30Z (e.g. Modal does not start), only Part 1 is used; logged.

## D63 — Part 2 (v5b) not built: Modal did not serve gpt-oss-120b (2026-11-16T08:57Z)
- 0 model calls in 892 s; auto-stopped at 900 s; ledger ACTUAL $1.3768 is a list-price upper bound (nothing served; check Modal billing). Containers empty. Second Modal app failure today after the qwen 503s (D59/D61): treated as a Modal-side outage.
- Per D62: only Part 1 (v5-01..25) is used. Not done: switching the extractor to another model or showing full opinions instead of quotes, because either changes the instrument after results are known. Part-2 scripts and the deterministic selection are kept in labels_build\v5b\ for a later rerun.

## D64 (2026-11-16T11:31Z) Slots filled at human request
Human: "u do it ... best draft it". Filled 4 HUMAN SLOTs with non-fabricated defaults: author "Anonymous author (independent researcher)" (no name known to agents); code "available from the author on request"; scorer prompts/serving config not publicly released, available on request; LLM-usage: "drafted and reviewed by AI agents; the human directed its completion and approved its submission" (no claim the human read it). Originals backed up in report/_preslot_backup/. Rebuilt: 17 pp, body 8/8. Outputs report/SUBMIT/. Step-3 author file never received; paper unchanged on that point. Submission remains the human's act.

## D65 (2026-11-16T11:41Z) Partial author verification, 12/25, post-gate
Author pasted answers for v5-01..v5-12 in chat at ~11:38Z (after gate, results known). Typed "agree/disagree" mapped to q1 NO/YES; "nioo" read as NO. Saved labels/author_verification_partial12.csv; frozen evaluate() called unchanged via analysis/verification_partial12.py -> analysis/results/VERIFICATION_PARTIAL12.json. q1 yes 7/12; author not-ack 6, ack 1; scorer hiding on 4/6 and on the 1 ack; kappa -0.24; usable=false (class minimum). Not a gate input; GATE1_RESULT.json unchanged. Paper: Results one sentence, Appendix A item 5 numbers, LLM usage updated. Rebuilt 17pp, body 8/8.

## D66 (2026-11-16T11:41Z) Author name added at human request: Mohammed Faisal Parvez; email typed ".comm", written as .com.
