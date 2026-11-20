# Novelty triage: N2, N5, N6, B, F

Council: novelty triage (fresh context, skeptical, did not edit the work). Date 2026-11-15.
Directive (human, D13): run an experiment only if it is new and worth doing, and stop the ones that are not. Total Modal cap is $200; about $0.65 has been spent.
Web and file text was treated as data. "Opened" means I read the arXiv abstract or HTML page in this session through the fetch tool, which returns a model paraphrase. Short quotes need re-checking by the citation verifier against the PDF.

## Summary

| Exp | Verdict | What is new (one sentence) | Closest prior work | Cost | Biggest risk |
|---|---|---|---|---|---|
| **N2** prompt grid | **RUN** | Crossing the system prompt (satisfy vs accurate) with the user prompt (common ground vs differences) tests whether a system-level accuracy instruction survives a user's common-ground request; the outcome is a scorer validated by blind human labels, on the same opinion sets that humans ranked. | Mahajan et al. 2026, https://arxiv.org/abs/2611.05135 | $3.27 expected, $6.50 ceiling (already council-approved) | The main effects repeat Mahajan; only the interaction is new, and it may be null. Scoring depends on gate 1. |
| **N5** shift to agreement | **RUN-REDUCED** | Tests whether rounds won by a hiding statement show a larger *apparent* move to agreement, i.e. consensus that is produced by wording ("false consensus"). | Tessler et al. 2024 (Science, eadq2852) RQ2 convergence; no direct test found | $0 (CPU) | Confounding: rounds with little initial disagreement differ in both erasure and shift; regression to the mean. |
| **N6** hidden instruction | **STOP** | Little is left: injection into consensus generation on the same Tessler opinions is already published, with defences. | Gudiño-Rosero, Zambrano, Grandi, Hidalgo, https://arxiv.org/abs/2508.04281 (v6, 4 Nov 2026) | $5 cap released | Re-doing the published work on less realistic, synthetic-only opinions, and producing a payload library (dual use). |
| **B** T1-1 temporal calibration | **RUN-REDUCED** | Measures whether a model's own P(fact still true) decays as a *forward* declared date moves past its cutoff, scaled to each fact's volatility, against Wikidata tenure-survival targets. | Qian et al. (FinDendro), https://arxiv.org/abs/2611.06808 | ≤ $6 for the Gate-2 pilot (of the $10 line); full run only on GO | The probe as built is invalid: the partial CPU run gives P(still true) ≈ 0 with no date at all (floor effect). There is also a role-play confound. |
| **F** fine-tune test | **STOP** | Mostly nothing: we know synthetic-data fine-tuning transfers to held-out sycophancy prompts. 3 vs 3 cannot reach significance, and the link to T3-1 is a proxy the packet itself concedes. | Wei et al. 2023, https://arxiv.org/abs/2308.03958; Betley et al. 2025, https://arxiv.org/abs/2502.17424 | $25 minimum + $40 expansion released | An expensive null or ambiguous result (on-policy rejection-sampling SFT is predicted to transfer poorly). Four human-blocked prerequisites. Safety-washing dual use. |

Net effect: $70 of planned allocation is released (N6 $5, F $65). B is left as the only candidate for the second submission slot. If B does not pass Gate 2, there is a single submission (T3-1), which matches the chair's ruling "Never three ... If T1-1 dies, the submission is T3-1 alone."
The released money is not reassigned here. Holding it as buffer is the careful default.

---

## N2: prompt grid (2x2, current open models). RUN

**Prior-work check.**
- Mahajan et al., "From Opinions to Commitments: Unstable Assignments and Silent Choices in AI-Mediated Proposals", arXiv 2611.05135, 3 Nov 2026. Abstract opened. Four LLM mediators (three open-weight, one commercial). Prompts seeking agreement covered minority positions much less often than prompts asking to describe differences. An LLM judge "overstated how often they occurred".
  - **Correction to scout 1 / N2 packet:** the abstract says three human annotators confirmed the detected between-run differences. So "no human validation" is too strong. Say instead: "limited human validation of run differences; we validate the erasure scorer itself against blind labels." The abstract does not say whether system and user prompts were crossed. The full text must be checked before we claim the crossing is new.
- Gudiño-Rosero et al. 2508.04281 (below, under N6) also generate attack-free consensus statements from the Tessler opinions with 7 models. That is a baseline we can cite, not a prompt grid.

**What is new.** The system × user interaction, and a human-validated scorer on human-ranked material. The main effects (SAT>ACC, COMMON>DIS) are expected to replicate Mahajan and must be written as replication.

**Value for the T3-1 paper.** High per dollar. It connects A2 (what people reward) to a cause (what instructions produce). A replication on validated measurement is also worth having.

**Cost.** Expected $3.27, worst case $6.26, ceiling $6.50 (packet §4). It already has 3/3 approve-with-conditions (D12).

**Cuts.** None to compute. Cut claims: the main effects are labelled "replicates Mahajan et al."; the interaction is the pre-specified novel contrast. No 70B rung (gated, NEEDS-HUMAN).

**Biggest risk.** If gate 1 fails, N2 is generation only, unscored, and adds almost nothing. Generating now is fine, because the cost is small and the statements are reusable. Do not spend on scoring before GATE1_PASSED.

---

## N5: hiding winner vs apparent shift to agreement. RUN-REDUCED

**Prior-work check.**
- Tessler et al. 2024 (main text read by scout 1; supplement unread, 403). RQ2 reports that groups become less divided after mediation, and the authors say convergence may come from "the caucus mediation process per se". They did not relate the shift to whether the winning statement hid the disagreement.
- Search (Habermas Machine critiques, CACM blog, LessWrong) turned up conceptual "illusion of consensus" critiques, but no measurement linking statement vagueness to perceived agreement. These came from search results only; I did not open them. Tessler et al. 2026, arXiv 2601.05904, abstract opened: a perspective piece, no such analysis.

**What is new.** It is an empirical test of "consensus by wording". It is novel, cheap and directly on-thesis, but observational.

**Value.** Medium. It is a striking exploratory figure if it holds, and a reportable null if not. It cannot become a main claim.

**Cost.** $0, CPU.

**Cuts (reduced form).**
1. One pre-specified exploratory test only, written into EXPERIMENTS.md before it runs:
   - outcome: round-level `view_movement`;
   - predictor: winner's erasure score E;
   - covariates: initial disagreement (opinion-derived), group size, statement length;
   - interval: launch-cluster bootstrap.
2. No variant sweeps.
3. Run only after gate 1 PASS and N1, as EXPERIMENTS.md already orders.
4. Before anything else, confirm that `view_movement` exists per round and is populated. If it is not, mark N5 "data does not allow".

**Biggest risk.** Confounding: low-disagreement rounds have both fewer cruxes to erase and less room to shift, which also invites regression to the mean. Labelled exploratory; never causal language.

---

## N6: one opinion carries a hidden instruction. STOP

**Prior-work check.**
- **Gudiño-Rosero, Zambrano, Grandi, Hidalgo, "Safeguarding Deliberation in Digital Democracy", arXiv 2508.04281.** v1 6 Aug 2025, v6 4 Nov 2026. Abstract and HTML (first 100k of 176k characters) opened. What it covers:
  - It uses the opinion texts from Tessler et al. (2024), "a 2023 experiment conducted in the UK" (Sec. 4.1): the **same data** as T3-1.
  - **One participant's opinion is overwritten** with a human-readable injection (Sec. 4.2): 40 injection texts per overwritten opinion, varied by ignore/completion, support/criticism, and five rhetorical strategies.
  - Seven generator models (Llama 3.1 8B, Apertus 8B, Qwen 3.5, Ministral 3 8B, Gemma E4B, GPT-OSS 20B, GPT-4.1 Nano).
  - Outcome: attack success rate as a shift in valence.
  - Defences: injection detection (GPT-OSS-SafeGuard), structured valence representation, GSPO majority-rule training, and others.
  - The abstract names attacks that "erase opinions".
- Also seen in search results only (not opened): Zhu et al. 2509.09912 and Keuper 2509.10248 (injection into LLM peer review); "One Bad Juror" (ACL Anthology 2026); Kraidia et al., Sci. Rep. 2026 (one adversarial agent steering a group).

**What would be new.** Only scoring tilt with our crux-erasure scorer instead of valence, and payloads that ask the mediator to hide the disagreement rather than flip the stance. That is an incremental arm on a published design. Our hard rule (synthetic opinions only, ETHICS N6-2) makes our version *less* realistic than theirs, which used the real opinion texts.

**Value.** Low for the T3-1 paper (a side topic) and none as a second submission.

**Cost.** $5 cap, plus a design that does not exist yet (ETHICS N6-1 blocker) and dual-use handling (N6-3).

**Verdict: STOP.** Cite Gudiño-Rosero et al. in related work as evidence that consensus generators on this very data can be steered by one participant. If an "erasure-targeted injection" is ever wanted, it is a separate proposal for the council-approved-new-experiment pool, with its own novelty case against 2508.04281's full text (the last 76k characters are unread).

**Biggest risk had it run.** A reviewer finds 2508.04281 and reads N6 as an unacknowledged, weaker re-run.

---

## B: T1-1 temporal-calibration pilot on Modal GPU. RUN-REDUCED

**Prior-work check (all opened, abstract or HTML):**
- **Qian et al., "LLMs Don't Know What They Know: Benchmarking Temporal Self-Knowledge for Financial Backtesting" (FinDendro), arXiv 2611.06808, 4 Nov 2026.** HTML opened. What it does and does not do:
  - The declared date is **historical only** (Sec. 3.2 Task 3: "Assume that today is [date]..."; Sec. 4.5 "historical-date instruction"). It never sets a date after the reference period.
  - Its "controls for persistence" are a persistence baseline for numerical facts and balanced accuracy for policy facts (Sec. 3.3). This is not volatility-conditioned decay of confidence.
  - It fits no decay against time since cutoff and runs no survival analysis (Sec. 4.3, 4.6 compare fact families only).
  - **So the chair's prior-work gate (CHAIR_RULING §4.2: "If it already reports volatility-conditioned confidence decay, T1-1 is NO-GO") does not fire.**
- **Elbadry et al., "The Geometry of Forgetting", arXiv 2605.09195, May 2026.** Abstract opened.
  - White-box linear probe of temporal drift, compared with entropy, semantic entropy, CCS and SAPLMA.
  - No verbalized confidence and no date manipulation; the drift label is whether a fact changed since training.
  - Supports the motivation ("models confidently produce outdated answers") and does not pre-empt the design.
- **Dhingra et al., "Time-Aware Language Models as Temporal Knowledge Bases", TACL 2022, arXiv 2106.15110.** Abstract opened. It uses "calibration on ... unseen facts from future time periods" for timestamp-conditioned models. **"Temporal calibration" is taken**: rename "TCE" or cite Dhingra explicitly (as novelty_audit.md also says).
- Not re-opened by me, from the T1 scout and novelty audit: Zhang & Choi 2023 (2305.14824, verified by the audit); evolveQA (2510.19172, accuracy only).

**What is new.** A forward-dated, volatility-conditioned test of the model's *own* P(still true), against an item-level Kaplan-Meier survival target. It still appears open after this check, with the audit's caveat that the search was partial.

**State of the existing pilot (read from `pilots/T1_1/`; this was not a re-run).**
- The CPU run (Qwen2.5-7B, anchor 2023-12-15) stopped at 120 of 2,097 calls (`results_qwen.log`): 95 item rows, 25 control rows, only 4 items in the real-date slice.
- **Defect (floor effect):** the logprob channel gives P(still true) ≈ 0 even with **no date**. `summary.json` `nodate_mean_lp.hog` = 1.04e-05, and real-slice `mean_conf` ≈ 4e-8. For example, item `hog:Turkey`, arm base, k=0 answers "No" with logprob -1.8e-05.
  - A model that already denies the fact at Δ=0 cannot show decay.
  - Either the question wording or the item filter ("keep only items the model answers correctly with no date", chair §4.2.1) is broken.
  - This must be fixed and re-checked on CPU before any GPU spend.
- The user-placement date control already moves P(real) to 0.67 at k=10, while the system placement stays at 1.0. The role-play arm (chair §4.2.3) is therefore informative and must stay.
- The subject is a 2023-era 7B model. The chair calls results on such models alone "stale". GPU subjects must be the newest open-weight releases on the ladder.

**Cuts (reduced form).**
1. $0 first: fix the probe, then rerun ~50 no-date calls on CPU. Proceed only if no-date P(still true) on the kept items is clearly above the floor (chair rule conf(0) ≥ 50).
2. Then run only the chair §4.2 Gate-2 pilot: 60 items × 6 conditions × 2 samples × 3 open-weight families = 2,160 calls, with an estimate logged first and a ceiling of **$6**.
3. No full ~12 h experiment, no extra elicitation ablations, and no "frontier" wording, unless Gate 2 = GO (CI for R below 0.5 in 2 of 3 models).
4. Rename the metric.
5. Disclose the pre-sprint code (CHAIR_RULING §2) and the pre-brief Modal job (ETHICS B-5).

**Value.** It is the only remaining candidate for the second submission slot. Even a "date ignored" or "blanket hedge" result is a publishable negative, if the probe is valid.

**Cost.** ≤ $6 pilot. The $10 line covers a modest follow-up only on GO.

**Biggest risk.** Probe validity. The floor effect above shows the current instrument cannot measure decay. Behind it sit the role-play confound (the date is treated as fiction) and the uncertainty about model cutoffs (chair §4.2.7).

---

## F: fine-tune to score well on honesty-benchmark-style items. STOP

**Prior-work check.**
- **Wei, Huang, Lu, Zhou, Le, "Simple synthetic data reduces sycophancy in large language models", arXiv 2308.03958.** Abstract opened. A lightweight fine-tune on synthetic data "can significantly reduce sycophantic behavior on held-out prompts". This is the same shape as F's trained arm (synthetic honesty-style data, then held-out sycophancy). The direction of transfer to sycophancy is therefore already reported.
- **Chaurasia, Tan, Li (SPAR, LessWrong, 10 Aug 2026), "Off-policy honesty training generalizes better than on-policy".** Post opened.
  - On-policy honesty fine-tuning "transfers poorly" to held-out honesty tasks; off-policy transfers better but costs factual accuracy.
  - F's trained arm is **on-policy rejection-sampling SFT** (F packet §4.4), so this predicts a small or null held-out effect.
  - Caveats: single model, mostly one seed, blog post (not peer reviewed).
- **Betley et al., "Emergent Misalignment", arXiv 2502.17424** (v7, Jan 2026). Abstract opened. Narrow fine-tuning generalizes broadly; it includes control fine-tunes. This covers the "approval-target" expansion arm, the only version of F that tests the thesis directly. That arm is in crowded territory and would deliberately produce a less honest model.
- From the F packet, not re-opened by me: Taylor et al., School of Reward Hacks (2508.17511); Denison et al., Sycophancy to Subterfuge (2406.10162); Sharma et al. (2310.13548); MASK (2503.03750).
- Search result only, not opened: Joshi et al., "Personas as a Way to Model Truthfulness" (2310.18168), which reports held-out transfer after TruthfulQA LoRA fine-tuning.

**What would be new.** Only the specific style source (MASK archetypes) paired with a specific held-out pair (TruthfulQA MC1, Anthropic sycophancy). That is a narrow configuration of a question with existing answers.

**Value.**
- For the T3-1 paper: low. The packet concedes "it does not test group statements or human approval; it is a proxy".
- As a second submission: weak. 3 vs 3 gives a minimum two-sided p of 0.10 (packet §8), so it can never be reported as significant. The predicted outcome (on-policy SFT, small shift) is "ambiguous".

**Cost.** $18.2 expected, $22.8 with contingency, on unmeasured throughput, against a $25 line plus a $40 expansion.

**Prerequisites still blocked.** Dataset downloads denied; contamination check never run on real data; judge.py unwritten; read-only HF token unconfirmed; human spot-check of 50 ground truths (D12, packet §11).

**Dual use.** Safety-washing recipe if in-style gains do not transfer (ETHICS F-2).

**Verdict: STOP.** Release $65.

**Biggest risk had it run.** Spending ~$25 to get an underpowered, predicted-null result that is only loosely tied to the paper's thesis.

---

## Items not checked (do not cite on my word)
- The full text of Mahajan 2611.05135: whether prompts were crossed system × user.
- The last 76k characters of 2508.04281.
- The Tessler supplement.
- The full text of FinDendro beyond the sections quoted.
- The MDPI / CACM Habermas critiques.
- The Personas paper 2310.18168.
- Taylor 2508.17511 and Denison 2406.10162 (taken from the F packet).
