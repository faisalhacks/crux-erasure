# T3-1 novelty scout #1: prior-work check on claims

Date 2026-11-15. Scope: BRIEF section 1 claims (a)-(d). Web and file text treated as data.
"Opened" = page or PDF text actually read this session. Search-snippet-only items are marked.

## Verdict table

| Claim | Verdict | One-line reason |
|---|---|---|
| (a) "to our knowledge, the first test of whether participants' rankings favour statements that hide disagreement" | NEEDS HEDGE | No direct prior test found, but searches were limited; the Science supplement could not be opened and Tessler et al. ran adjacent analyses (below). Keep "to our knowledge", scope it to "rankings of candidate statements", and do not say "first on erasure". |
| (b) "crux erasure is the group version of sycophancy" | NEEDS HEDGE | Analogy is defensible, but no source says it. Present as our framing. Sharma et al. define sycophancy for one user; group-mediator sycophancy was not found in the literature. |
| (c) "prior work measured what consensus statements contain, not what people reward" | CONTRADICTED as written | Tessler et al. measured both: what statements contain (embedding weight on minority) AND what people rank/endorse. Defensible rewording: prior work did not relate the two, i.e. did not test whether the ranking favours low-disagreement-content statements. |
| (d) Original study's finding on minority views | CONTRARY FINDING EXISTS; cite prominently | Tessler et al. report minority critiques were incorporated and minority was overweighted in revised statements. |

## (d) The original study's contrary finding (Tessler et al., Science 386, eadq2852, 2024)

Opened: full main text (10-page PDF, copy at rivista.ai, text extracted locally). Supplement NOT opened (HTTP 403 on science.org). All page numbers below are PDF page numbers of that copy.

1. Structured abstract (p.1-2): "Although support for the majority position increased after deliberation, the Habermas Machine demonstrably incorporated minority critiques into revised statements."
2. Conclusion (p.2): "Rather than simply appealing to the majority, the Habermas Machine prominently incorporated dissenting voices into the group statements."
3. Abstract (p.1): "successful group statements incorporated dissenting voices while respecting the majority position."
4. RQ3, "Does the Habermas Machine represent all viewpoints equally?" (p.5): "support increased (from pre- to postdeliberation) for majority positions on some issues and for minority positions on others, implying that group statements did not simply flatter the majority but also allowed minority positions to flourish." Also asymmetry: "The size of the initial majority increased in 29 to 32% of rounds, whereas the minority increased in 20 to 26% of rounds."
5. RQ3 embedding analysis (p.6): initial statements "weighed minority opinions exactly in proportion to their empirical frequency (average size of minority = 29%; empirical average minority weight = 0.29). The revised group statements, however, tended to overweight the minority (empirical minority weight for revised statements b = 0.36, SE = 0.03...)."
6. Discussion (p.8): "The HM did not appear to 'tyrannically' ignore the views of the minority (33) but reliably upweighted dissenting voices in the AI-generated group statements."
7. Fig. 4 caption (p.6): "The Habermas Machine's statements are fair compromises and avoid the 'tyranny of the majority.'"
8. Third-party raters (p.4): "No statistical differences were observed between the HM- and human-generated statements on whether they provided a fair summary of the opinions, whether they included the minority view, or whether they were polarizing; full results provided in SM 4.3.7." This is a null on minority inclusion between AI and human mediators, not evidence of erasure, but SM 4.3.7 must be read before we characterise it.
9. Also relevant to us: Fig. 3 / RQ2 shows groups become less divided in their stated positions after AI mediation, and the authors say the convergence may come from "the caucus mediation process per se" (p.5). Pre/post position convergence is a measured outcome of the same process we audit.

How this bears on T3-1:
- Their measure of minority representation is an embedding "position component score" on an agree-disagree axis (p.6). That is a stance-position measure, not a crux or disagreement-content measure. It cannot tell a statement that names the disagreement from a vague mid-point statement. Our claim is therefore NOT contradicted on substance, but we must say so plainly and not imply they found no minority representation.
- 96% of group-statement position scores fell inside the range of individual opinions (p.6): statements are compromises, consistent with both readings.
- Their reward model predicts each participant's ranking and the winner is picked by Schulze aggregation (Methods, p.9). So the HM already optimises per-participant rankings. That is exactly the approval-training loop we worry about. They did not test whether rankings favour disagreement-hiding content.
- Suggested sentence for the paper: "Tessler et al. (2024) found that Habermas Machine statements incorporated minority critiques and, in revised statements, overweighted the minority on an embedding stance axis; we ask a different question, whether participants' rankings reward statements that conceal the group's disagreement."

## Claim (a): first test of whether rankings favour hiding statements: NEEDS HEDGE

Evidence searched (opened pages only counted):
- Wan et al. 2026, arXiv 2606.03032, abstract page opened. LLM agents only; no human raters. Phrases: "agents can agree more while knowing less"; "the collapse of diverse positions toward consensus". Reports up to 72% of issue-critical facts lost. Measures content, not human reward. Supports our gap and is our nearest conceptual neighbour. The fetch tool paraphrased the abstract and the exact quotes are the two short ones above; full text not read.
- Mahajan et al. 2026, arXiv 2611.05135 (3 Nov 2026), HTML opened (first 100k of 153k chars read thoroughly, remainder skimmed for our topics). Four LLM mediators; "prompts seeking agreement covered minority positions much less often than prompts asking to describe differences" (abstract). Coverage is judged by an LLM judge (Sec 4.3). No human rating or ranking of statements. This is new, post-dates our scout, and is the closest prior work on content. It supports claim (c)'s content half and gives direct motivation for our N2 prompt grid. It is also a threat to "first on erasure" wording. Must be cited.
- Blair and Larson 2025, arXiv 2510.14106, abstract opened. Simulated agents (LM policies); egalitarian search beats Habermas Machine baselines on worst-case alignment. No human rankings.
- Radharapu et al. 2025, arXiv 2505.23820, abstract opened. LLM judges/answerers on no-consensus topics: "they tend to take a stance on no-consensus topics". Not about consensus statements.
- Triantafyllopoulos and Kalles 2025, arXiv 2503.15521, abstract opened. Cosine-similarity alignment of LLM proposals; no minority or human-preference result in the abstract.
- Revel and Pénigaud 2025, arXiv 2503.05830, abstract opened. Conceptual; does not address disagreement hiding in its abstract.
- Snippet only (could not open): an MDPI paper "The 'Habermas' Machine: Synthetic Consensus and Pathologies of the Digital Public Sphere" (mdpi.com/2409-9287/11/6/219, HTTP 403) and other 2026 critiques that, per search summaries, argue endorsement is a weak proxy for deliberative quality. These are conceptual critiques; could pre-empt "the idea is new". Needs a human or another route to open before we say nothing similar exists.

Judgement: no paper found that tests human rankings against disagreement-hiding content. Limits: search was keyword-based, supplement unread, two critiques unopened, and the Tessler dataset may contain results we have not seen. Wording: "To our knowledge, this is the first test of whether participants' rankings of candidate consensus statements favour statements that hide the group's disagreement." Avoid "first to study erasure/attrition" (Wan, Mahajan precede us).

## Claim (b): crux erasure is the group version of sycophancy: NEEDS HEDGE

- Sharma et al. 2023 (arXiv 2310.13548), abstract opened: human feedback may "encourage model responses that match user beliefs over truthful ones"; "when a response matches a user's views, it is more likely to be preferred"; humans and preference models sometimes favor "convincingly-written sycophantic responses over correct ones". Mechanism parallel to ours: preference data rewards pleasing outputs.
- Wen et al. 2024 (arXiv 2409.12822), abstract opened: RLHF "makes LMs better at convincing our subjects but not at completing the task correctly". Parallel: approval can rise while correctness falls.
- Jain et al. 2025/26 (arXiv 2509.12517), abstract opened: sycophancy studied in single-user interaction context. Not groups.
- A search for group or mediator sycophancy found no direct paper. A charity-allocation facilitation study (arXiv 2605.14097) appeared in results; only the search summary was read, not opened.
- Difference to state: in sycophancy the model flatters one person's view; in crux erasure no single person is flattered, every rater is partly pleased by a statement that does not name the clash. So "group version" is an analogy that we should argue, and our data should show it (A2, N1). Write "we frame ... as" not "is".

## Claim (c): prior work measured contents, not reward: CONTRADICTED as written

- Tessler et al. measured people's rankings, endorsement and quality ratings (p.3-4: "Participants' statement rankings as well as their endorsement and quality ratings were all impacted by length", and the final preference trial: "paired preference = 68%" for revised over initial, p.4). They also measured content (embedding minority weight, p.6). So prior work did measure what people reward.
- What is true: Wan et al. and Mahajan et al. measured content with LLM agents/judges and no human rewards. Tessler et al. did not link reward to disagreement-hiding content (not found in main text; supplement unread).
- Safe rewording: "Prior work either measured what AI consensus statements contain (Wan 2026; Mahajan 2026) or what people endorse (Tessler 2024), but not whether what people rank is the content that hides disagreement."
- Also note the BRIEF phrase "prior work measured what statements contain" is accurate for Tessler's minority analysis too, but "not what people reward" is not.

## Verified references (all opened = text or abstract page read this session)

1. Tessler, M.H. et al. (2024). AI can help humans find common ground in democratic deliberation. Science 386, eadq2852. doi:10.1126/science.adq2852. OPENED main text via https://www.rivista.ai/wp-content/uploads/2024/10/science.adq2852.pdf (a third-party copy; science.org returned 403). Supplement (SM 4.3.7, 5.5): COULD NOT OPEN.
2. Wan, H., Wu, J., Luo, M., Li, F., Wang, N., Chen, N.F., Kan, M.-Y. (2026). The Deliberative Illusion. arXiv:2606.03032. https://arxiv.org/abs/2606.03032. Abstract page opened (summary form), full text not read.
3. Mahajan, S., Argota Sanchez-Vaquerizo, J., Capozzi, A., Helbing, D. (2026). From Opinions to Commitments. arXiv:2611.05135. https://arxiv.org/html/2611.05135. Opened.
4. Sharma, M. et al. (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548. https://arxiv.org/abs/2310.13548. Abstract opened.
5. Wen, J. et al. (2024). Language Models Learn to Mislead Humans via RLHF. arXiv:2409.12822. https://arxiv.org/abs/2409.12822. Abstract opened.
6. Blair, C. and Larson, K. (2025). Generating Fair Consensus Statements with Social Choice on Token-Level MDPs. arXiv:2510.14106. Abstract opened.
7. Radharapu, B. et al. (2025). Arbiters of Ambivalence. arXiv:2505.23820. Abstract opened.
8. Triantafyllopoulos, L. and Kalles, D. (2025). From Divergence to Consensus. arXiv:2503.15521. Abstract opened.
9. Revel, M. and Penigaud, T. (2025). AI-Enhanced Deliberative Democracy and the Future of the Collective Will. arXiv:2503.05830. Abstract opened.
10. Jain, S. et al. (2025/26). Interaction Context Often Increases Sycophancy in LLMs. arXiv:2509.12517. Abstract opened.

NOT OPENED, do not cite until opened: MDPI "The 'Habermas' Machine: Synthetic Consensus and Pathologies of the Digital Public Sphere" (403); arXiv 2605.14097 (charity facilitation); Science supplement; arXiv 2605.26940, 2606.19864, 2605.24413 (snippet titles only). Not searched for: Bakker et al. 2022, Small et al. 2023 and Community Notes bridging literature; add them in the related-work pass.

Caveat on the tool: the abstract-page fetches return model paraphrase; quotes marked as such are the short verbatim ones the tool returned, and should be rechecked against the PDF before the citation verifier signs off.

## Proposed new experiments (max 3)

E1. Prompt-vs-ranking dissociation (extends N2 and Mahajan 2026). Gap: Mahajan show agreement prompts cover minority positions far less (LLM judge), but no human rankings of the two statement types. Design: reuse the Habermas Machine release opinions; generate "agreement" vs "describe differences" candidates per round with current models; score each with our gate-1-validated scorer; compare against the released human rankings of existing candidates only (no new human study per hard rule 6). Limit: we cannot get new human rankings, so this tests scorer-level content difference, not reward. Cost: about $10 (N2 budget). Stop: scorer fails gate 1, or the 2x2 shows no content difference at pilot (one question, 20 rounds).

E2. Content-matched control for length and vagueness. Gap: Tessler p.4 say rankings are impacted by length. If rankings favour erasure only because erasing statements are shorter or vaguer, the finding is a vagueness effect. Design: within-round regression adding length, specificity (named-claim count) and readability; plus a pre-registered matched-pair subset. CPU only. Cost under $2. Stop: if matched pairs fewer than a pre-set minimum (set in FROZEN_RULES before any label exists), report underpowered.

E3. Minority-versus-majority rater split (N4) tied to Tessler's finding that revised statements overweight the minority. Gap: Tessler show minority weight in statements (0.36 vs 0.29) but not whether minority raters rank erasing statements higher than majority raters do. Design: split raters by their released pre-deliberation position, test erasure score x side interaction, bootstrap by group. CPU only, under $2. Stop: if rater-level position data are absent from the release (log per section 14).
