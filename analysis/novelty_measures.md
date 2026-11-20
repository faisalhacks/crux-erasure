# Novelty scout 2: prior work on MEASURING erasure and clarity (T3-1)
Date 2026-11-15. Scope: measurement only. No labels were created or used.
Verification key: OPENED = I read the full text or a substantial part of it. ABSTRACT = abstract page only. SNIPPET = seen only in search results, NOT opened (do not cite from it without opening).

## Input for FROZEN_RULES (read this first)
1. **Name collision.** Zaghouani, arXiv:2605.26940 (LREC 2026 workshop) already defines a metric called "Erasure" for consensus statements. It is a proposal in a "testable blueprint" paper with no validation and no ranking study (OPENED). Cite it. Use a distinct name, for example "crux erasure score", and keep the brief's wording "first test of whether rankings favour hiding statements", never "first on erasure".
2. **Recommended primary erasure score (crux-level, LLM judge).**
   - Input: the round's opinions, split into cruxes (axes on which opinions split), each with a majority and a minority side.
   - Judge: for each crux, the statement is labelled `preserved` (both sides visible), `blurred` (vague or both-sides-fine), or `erased` (crux absent, or one side only).
   - Score: erasure = salience-weighted share of cruxes not `preserved`, with the weights fixed in advance. Report the unweighted version as well.
   - Why: the same shape as the coverage and shortfall metrics in Khosravani 2024 (coverage = share of reference key points matched), Zhang 2024 (shortfall of a perspective's share in the summary vs. the source) and Zaghouani (salience-weighted omission). All three are OPENED.
   - It matches gate 1 in the brief: disagreement is defined from the opinions, and humans label the same item.
3. **Secondary scorer for A4 (a different family, not an LLM).** Embedding position-axis erasure. Use Tessler's own construction: embed the opinion set and the affirming and negating position statements, then project onto the "position axis". Compare how far the statement sits from the opinion spread. Do not use plain max-cosine similarity (Zaghouani's formula, 1 - max sim) as primary: cosine similarity cannot tell "A" from "not-A".
4. **Clarity.** Primary: a rubric LLM judge, 1-7, run on the statement alone, with a model family different from the erasure scorer. Covariates in the same model: token length and Flesch-Kincaid grade as a robustness check. Precedent for rated clarity: Tessler et al. Science 2024, where third-party raters scored statements on nine quality dimensions including clear, informative and unbiased (OPENED).
5. **State in FROZEN_RULES that clarity may be a mediator.** Tessler found AI statements were rated clearer, so the clarity control may absorb real effect. Pre-register both the with-clarity and the without-clarity estimates and report both.
6. **Pre-register the judge settings before any real label:** model ID, temperature, prompt text hash, two presentation orders for crux lists, number of repeats, and the aggregation rule. Judge position bias and verbosity bias are documented (MT-Bench, ABSTRACT).
7. **Do not report judge-vs-human agreement from other papers as evidence for ours.** Gate 1 is our validity evidence. Zhu et al. found off-the-shelf LLM judges correlate with human ratings of representativeness at no more than about 0.4 (OPENED, HTML). That is a different task, but it is a warning that judge validity must be earned.

## 1. Prior work, one entry per paper

| # | Paper | What the metric is | Code | Validity evidence | Status |
|---|---|---|---|---|---|
| 1 | Zaghouani, "Accountable Human-AI Deliberation with LLMs", arXiv:2605.26940. https://arxiv.org/abs/2605.26940 | Coverage = salience-weighted max cosine similarity of the statement to each cluster. Diversity = weighted over minority clusters. **Erasure(s) = sum over salient critiques x of sal(x)(1 - max_c sim(c, x))**. Suggests flagging clusters with max sim < 0.7. | None found (page lists none) | None. The paper says the 0.7 threshold must be calibrated to human judgments by pilot annotation. No ranking study. | OPENED (PDF text). Date and venue are from the arXiv page. |
| 2 | Zhu, Yang, Bakker, Pentland, Pei, "Can AI Truly Represent Your Voice in Deliberations?", arXiv:2510.05154. https://arxiv.org/abs/2510.05154 | DeliberationBank: representativeness, informativeness, neutrality and policy approval, rated 1-5 from the rater's own perspective. Minority is defined by self-report or by Local Outlier Factor on embeddings. | Project site https://shuyhere.github.io/LLMs-for-Scalable-Deliberation. Paper says "will release" data and code; no repo found. | The tuned DeBERTa judge reaches Pearson 0.504 (representativeness). Off-the-shelf LLM judges stay at or below about 0.4 (GPT-5 3-shot 0.398). Finds minority under-representation across 18 LLMs. Preprint, not peer reviewed. | OPENED (HTML, first ~100k characters). |
| 3 | Zhang et al., "Fair Abstractive Summarization of Diverse Perspectives", arXiv:2311.07884. https://arxiv.org/abs/2311.07884 | Four reference-free metrics from the gap between each perspective's share in the source and in the summary: BUR (binary unfair rate, tolerance 0.8), UER (unfair error rate), AUC, SOF (second-order fairness). | https://github.com/psunlpgroup/FairSumm | Human evaluation with 4 annotators: Krippendorff alpha 0.69 in the pilot stage, Randolph kappa 0.41 in the rating stage. Synthetic oracle tests. Finds human-written references also score low on fairness. | OPENED (HTML, first 100k characters). I did not read the last ~25k characters. |
| 4 | Shandilya, Dash, Chakraborty, "Fairness for Whom?", arXiv:2101.12406. https://arxiv.org/abs/2101.12406 | "Perceived opinion bias": annotators list the distinct opinions, then the Gini coefficient of how each opinion is represented in the summary. | Not checked | Pearson correlation with human fairness ratings is stronger than ROUGE-1 (exact values not extracted; ROUGE-1 is "poor"). | OPENED (PDF text, searched by keyword only). |
| 5 | Khosravani, Huang, Trabelsi, "Enhancing Argument Summarization", NAACL 2024, arXiv:2404.11793. https://arxiv.org/abs/2404.11793 | Coverage = share of reference key points matched by a fine-tuned BERT key-point matcher. | https://github.com/b14ck-sun/arg-sum (reusable) | Pseudo-summaries at 100/75/50% true coverage: the metric reads 83.2/77.3/64.8%, better than ROUGE, BLEURT and BARTScore. Matcher precision 90.0%. This validates on constructed answers only. | OPENED (HTML). |
| 6 | Huang et al., "Examining Bias in Opinion Summarisation through Opinion Diversity", WASSA 2023. https://aclanthology.org/2023.wassa-1.14 | Stance-based opinion diversity coverage. Finds higher similarity does not mean better diversity. | None listed | Not determined | ABSTRACT only. |
| 7 | Mahajan, "Participatory provenance", arXiv:2604.20711. https://arxiv.org/abs/2604.20711 | Per-submission semantic coverage with a threshold, applied to Canada's 2025 AI consultation (5,253 records). Official summaries beat same-length random text, but significance depended on the embedding model. | None listed | Baseline comparisons only. Shows embedding-based coverage is fragile to the embedding model. | ABSTRACT only. |
| 8 | Tessler, Bakker et al., "AI can help humans find common ground", Science 2024. | Not an erasure metric. The ranking procedure is the source of our data. Third-party ratings of nine quality dimensions (clarity, informativeness, bias). Position-axis embedding analysis of minority versus majority. Reports that revised statements incorporate critiques and minority views. | See paper's data note | Authors' own claim that dissent is incorporated. I found no independent replication. | OPENED (PDF text, keyword-searched). |
| 9 | Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", arXiv:2306.05685. https://arxiv.org/abs/2306.05685 | Judge-validity reference: GPT-4-class judges exceed 80% agreement with humans on chat quality. Position, verbosity and self-enhancement biases. | https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge | Human agreement on a different construct | ABSTRACT only. |
| 10 | Cachola et al., "Evaluating the Evaluators: Are readability metrics good measures of readability?", EMNLP 2025, arXiv:2508.19221 | On plain-language summaries, 6 of 8 classic formulas correlate below 0.3 with human judgment (FKGL Pearson 0.16). The best LM judge reaches 0.56. | Not checked | Human judgments of readability | SNIPPET only. Not opened. |
| 11 | Fish et al., "Generative Social Choice", arXiv:2309.01291, and Boehmer, Fish, Procaccia, arXiv:2505.22939 | Representation guarantees for a slate of statements, with LLM-implemented queries. Not an erasure metric. Related for the representation framing. | Not checked | n/a | SNIPPET only. |
| 12 | Blair and Larson, "Deliberative Machines" (Waterloo) and arXiv:2510.14106 | Fair consensus via egalitarian objectives. Argues the Habermas Machine lacks fairness guarantees. | Not checked | n/a | SNIPPET only. Not opened. |
| 13 | Yao et al., "Peacemaker or Troublemaker", arXiv:2509.23055, and arXiv:2604.02668 | Sycophancy and consensus collapse among debating agents. Supports the sycophancy framing but is not a statement-erasure metric. | Not checked | n/a | SNIPPET only. Not opened. |

Gap found: no paper in this search tests whether human rankings of candidate group statements reward or penalise erasure. Zhu et al. (2) is closest, because it relates minority status to representativeness ratings, but it rates one summary per rater and does not rank competing candidates. This supports the brief's wording "to our knowledge, the first test". The search was a handful of queries, not exhaustive. Recommend one more search for "bridging-based ranking" and Community Notes before the claim is final.

## 2. Operationalisation an outside judge would accept

**Erasure score.**
- Unit: one (round, statement) pair, computed from that round's opinions only (not from rankings).
- Steps: (a) a crux extractor writes the disagreement axes with majority and minority sides, and the opinion counts per side. (b) The judge labels each crux in the statement as preserved, blurred or erased. (c) Score = weighted share not preserved. Weight options frozen in advance: unweighted and minority-share-weighted.
- Why it should be accepted: it mirrors the published coverage and shortfall families (Khosravani, Zhang, Shandilya, Zaghouani), and gate 1 supplies the human validity evidence that Zhang and Zhu show is the weak point of this literature. The cutoff of 0.60 kappa on shared items is stricter than Zhang's Randolph kappa of 0.41.
- Robustness: the embedding position-axis scorer (A4) and, if released, the Zhang BUR/UER on crux-share. Report both for every analysis.

**Clarity.**
- Primary: LLM-judge rating on the statement alone. Secondary: length in tokens and Flesch-Kincaid grade.
- Claim limits: classic formulas are weak proxies for human readability (Cachola, SNIPPET), so use FKGL only as a covariate, not as the clarity measure.
- Precedent: Tessler's third-party Likert ratings of clarity. If the human labelers' files include no clarity rating, we cannot validate the clarity judge against humans. State that as a limitation. Do not make up clarity labels.

## 3. Risks
1. **Name and novelty.** Zaghouani uses "Erasure". Cite it and differentiate: proposed formula, unvalidated, no ranking test.
2. **Embedding fragility.** Mahajan shows coverage significance flips with the embedding model. Zaghouani's own threshold (0.7) is uncalibrated. Treat embedding scores as secondary.
3. **LLM-judge validity.** Zhu measured at most about 0.4 correlation for off-the-shelf judges on a related construct. Position and verbosity bias are documented. Mitigate with order swaps and the length control already in A2.
4. **Circularity.** Erasure and clarity judged by the same model share errors, and a judge may prefer smooth text. Use different families and report both.
5. **Over-control.** Controlling for clarity may remove part of the effect if clarity is downstream of the writing choice that also erases.
6. **Construct mismatch.** The literature measures omission (coverage). Our construct is both omission and false resolution (blurring). The three-way label handles it, but gate 1 must show labelers can tell blurred from erased. If kappa fails on that split, collapse to preserved vs. not, in advance.
7. **Reviewer dislike of validation on known answers.** Synthetic edit tests (E1 below) are sensitivity checks only. Label them so.

## 4. At most 3 new experiments (all exploratory unless frozen first)

**E1. Controlled-edit sensitivity of the erasure judge (synthetic opinions only).**
- Gap: Khosravani validated only on constructed coverage levels with a trained matcher, and no one has done it for crux-level LLM judges with order swaps.
- Design: take synthetic opinion sets (no human data), generate statements, then (i) delete the minority-crux sentence, (ii) add a both-sides sentence, (iii) rewrite to a neutral-vague sentence. Check the score moves in the predicted direction for each, and does not move when only length or clarity changes.
- Cost: about 300 judge calls, roughly 1 to 3 USD in API cost (my estimate, not measured). Under the 5 USD council threshold.
- Stop: stop if the judge does not move in the predicted direction on a pilot of about 50 edits. Set the numeric criterion in FROZEN_RULES before running. A failure means the judge cannot be used even before gate 1.

**E2. Non-LLM scorer for A4 (position-axis embedding erasure).**
- Gap: Zaghouani's formula is unvalidated and cosine-based. Tessler's position-axis geometry is established but has not been turned into an erasure score.
- Design: implement the position-axis score and Zaghouani's 1-max-sim formula, then correlate both with the LLM-judge score on dummy data, then on real data after gate 1. Report how many rounds the sign of the A2 result changes.
- Cost: CPU only, no Modal spend.
- Stop: if the two embedding scores do not correlate positively with the LLM judge on the dummy set, drop them from the main text and report them in the appendix.

**E3. Clarity mediator-versus-confounder sensitivity.**
- Gap: no cited work separates clarity as a confound from clarity as a mediator for the ranking of group statements.
- Design: rerun A2 under four specs: no clarity control, LLM clarity, FKGL plus length, both. Show the erasure coefficient across all four with group-bootstrap CIs.
- Cost: negligible. It reuses A2 data and about 1 USD of judge calls.
- Stop: no stopping on the result. If the erasure coefficient flips sign across specs, report it as the headline limitation.

## 5. Not opened or not verified (do not cite until opened)
Items 10, 11, 12, 13 above (snippets only). Items 6, 7, 9 were read at abstract level only. I did not verify any claim about code releases beyond the links given. The Zhu paper's final ~11k characters and the Zhang paper's final ~25k characters were not read. arXiv ids in the 2604 to 2606 range come from search results and the arXiv pages I fetched; I did not independently confirm peer-review status for any of them.
