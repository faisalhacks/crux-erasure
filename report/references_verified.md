# References verified: T3-1 citation verifier

Date 2026-11-15. Verifier: citation-verifier agent (evaluator, not an author of any input file).
Inputs: analysis/novelty_claims.md (NC), analysis/novelty_measures.md (NM), analysis/prior_bridging.md (PB, added by orchestrator mid-task), decisions.md D4/D5, ../epistemics/T3_scout.md (TS).
Web text was treated as data (BRIEF rule 7).

## Method and what "opened" means here
- **arXiv metadata** (title, full author list, first-version date, comment and journal_ref fields) came from the arXiv export API (`export.arxiv.org/api/query?id_list=...`) for all 48 arXiv IDs. Every ID resolved and none returned an error.
- **Verbatim quotes with page numbers:** the PDF was downloaded and converted locally with `pdftotext`, and phrases were located per page by `scratchpad/findq.py`. That was done for Tessler (third-party copy of the Science PDF), Mahajan 2611.05135, Zaghouani, Sharma, Wen, Wan, Cachola, Shandilya, Conlon & Schwardmann, and Turan & McKenzie. Page numbers are PDF page numbers.
- **Summarising fetch tool:** the remaining HTML, abstract pages, Crossref, Europe PMC and ACL Anthology pages were read through a fetch tool that paraphrases and caps quotes at 125 characters. Claims checked only this way are marked "(fetch)". Exact-string checks were requested where a quote is proposed.
- **Venue from secondary sources:** a few venue facts come only from web-search results that cite the publisher page. They are marked "(search)".
- **Tools that failed or were refused:** curl in the shell was refused by the permission system, and I did not work around it. DBLP refused automated access (Anubis bot block). science.org, mdpi.com and nature.com returned 403 or a login redirect.

Status key: **VERIFIED** means the metadata is correct and every claim attributed to the source was found in it. **CLAIM-MISMATCH** means the source was opened but an attributed claim, number or quote is absent or different. **METADATA-MISMATCH** means a title, author, venue or year as proposed is wrong. **COULD-NOT-OPEN** means no route to the text was found.

---

## A. Defects that must be fixed before drafting (flaw, evidence, severity, cheapest fix)

1. **Tessler supplement: COULD-NOT-OPEN (unchanged).**
   - Evidence: science.org main page and the supplement PDF (`/doi/suppl/10.1126/science.adq2852/suppl_file/science.adq2852_sm.pdf`) both return HTTP 403. Europe PMC lists the record with `hasSuppl: N`, `isOpenAccess: N` and no PMCID. The google-deepmind/habermas_machine README links neither the SM nor a preprint.
   - Severity: **high** for any sentence about SM 4.3.7 (third-party rating of minority inclusion) or SM 5.5 (minority-weight method).
   - Fix: a human downloads the SM through institutional access. Until then, cite only main-text claims, all of which are VERIFIED (B1).
2. **Wen et al. 2024 is now contested.**
   - Evidence: an ICLR 2026 Blog Track poster (Chandna, Fluri, Carroll, "Is the evidence in 'Language Models Learn to Mislead Humans via RLHF' valid?", iclr.cc/virtual/2026/poster/10012085) argues the results may stem largely from bugs in the RLHF setup. It also reports failing to find supporting evidence in a corrected experiment (fetch).
   - Severity: **medium**. Wen is one of two pillars for the sycophancy framing (claim b).
   - Fix: keep Wen as motivation only. Add the rebuttal in the same sentence, or lean on Sharma et al. alone.
3. **Costello et al. 2024 (Science) carries an Expression of Concern and an Erratum.**
   - Evidence (Europe PMC commentCorrectionList): Expression of concern in Science 392(6803):1131, 11 Jun 2026, doi:10.1126/science.aej2383. Erratum in Science 394(6822):eaem1178, 22 Oct 2026.
   - Severity: medium if cited. It is cited only in TS Idea 3, which is not pursued.
   - Fix: do not cite until a human reads the EoC. It is held out of refs.bib.
4. **Wan et al.: misquote in T3_scout.**
   - Evidence: TS writes "agents can come to agree while knowing less". The source (p.1, abstract) reads "agents can agree more while knowing less". NC has the correct wording.
   - Severity: low, but a misquote in a paper is a credibility hit.
   - Fix: use the NC wording.
5. **Yao et al. / arXiv 2604.02668: wrong authors.**
   - Evidence: NM row 13 lists "Yao et al., ... arXiv:2509.23055, and arXiv:2604.02668". 2604.02668 is Kasprova, Parulekar, AlRabah, Agaram, Garg, Jha, Bozdag, Hakkani-Tur, "Too Polite to Disagree: Understanding Sycophancy Propagation in Multi-Agent Systems", SIGDIAL 2026, pp. 795-814 (arXiv journal_ref).
   - Severity: low.
   - Fix: cite the two papers as separate entries.
6. **Blair "Deliberative Machines" thesis: claim not in the thesis abstract.**
   - Evidence: the thesis exists (Carter Blair, University of Waterloo, 2025-06-13, hdl:10012/21859; uwspace.uwaterloo.ca). Its abstract does not mention the Habermas Machine. The claim "HM lacks fairness guarantees" is supported instead by Blair & Larson arXiv 2510.14106 §1 (fetch).
   - Severity: low.
   - Fix: cite 2510.14106 for that claim and drop the thesis.
7. **Milli et al. 2024: venue imprecise.**
   - Evidence: PB says "NeurIPS 2024". The NeurIPS page says this is a poster in the **Pluralistic Alignment Workshop**, not the main conference. The exact title is "Bridging in Social Media Feeds Censors Controversial Topics". No arXiv version was found.
   - Severity: low to medium, because a reviewer may read it as a main-track claim.
   - Fix: cite it as a NeurIPS 2024 workshop paper (OpenReview id AylUTjJnoL).
8. **Huang et al. WASSA 2023: title wrong.**
   - Evidence: NM gives "Examining Bias in Opinion Summarisation through Opinion Diversity". The ACL Anthology title is "Examining Bias in Opinion Summarisation through the Perspective of Opinion Diversity" (Huang, Tian, Fayek, Zhang; WASSA 2023, pp. 149-161, doi:10.18653/v1/2023.wassa-1.14).
   - Fix: correct the title. The claim itself checks out against the abstract: "a higher degree of similarity of opinions did not indicate good diversity".
9. **Numbers misstated in T3_scout.**
   - Zhou et al. 2603.11245: the human User-Sim Index is **92.7**, not 92.9 (§1 and Table 1). The best simulator's 76.0 is correct.
   - Cui et al. 2409.00128: the abstract reports **156** experiments, not 154.
   - Fix: correct both numbers, or drop the references (both support Ideas 2 and 3, not T3-1).
10. **Unconfirmed sub-claims in T3_scout.**
    - Salvi et al.: the abstract confirms an 81.2% relative increase in odds with personalisation. It does not state the "no significant difference without personal data" result. The record also lists an erratum (Nat Hum Behav, 3 Sep 2026).
    - arXiv 2601.10660 (Labruna, Modzelewski, Satta, Da San Martino): the abstract describes no pairwise "pick the persuasive comment from the same thread" task.
    - Khan et al.: the abstract does not contain the consultancy claim ("judge accuracy fell as the consultant became more persuasive"). The full text was not checked.
    - Fix: read the full texts or drop these sub-claims.
11. **Zhu et al. 2510.05154: precision of wording.**
    - Numbers VERIFIED: 0.504 and 0.398 are representativeness **Pearson** values in Appendix G.2, Tables 9 and 10, of **v5** (20 Mar 2026). The main text reports something different: Spearman ρ = 0.60 for representativeness (Table 3), overall correlation "approximately 0.48" (§3.3), and "Overall, correlations never exceed 0.4" for off-the-shelf judges (§3.1).
    - "Finds minority under-representation across 18 LLMs" goes beyond the text. 18 LLMs are benchmarked overall, and Appendix B.1 says the minority bias is "consistent across all models" without stating how many models the minority analysis covered.
    - Fix: cite v5 with the table numbers, and write "benchmarks 18 LLMs and reports minority under-representation".
12. **Shandilya et al.: wording and comparison caveat.**
    - The paper calls ROUGE-1 correlations "moderate, in the range [0.5, 0.65]" (p.7) and says they "do not correlate well". It does not use the word "poor".
    - Perceived Opinion Bias correlations are 0.74-0.94 (Table II, p.8). However, they are computed against the "very unfair" approval fraction, while ROUGE is computed against the "very fair" fraction.
    - Fix: use the paper's own numbers and mention the asymmetry if the comparison is used.
13. **Farrow (MDPI) critique: unsupported attribution.**
    - Evidence: the full text is still 403. The Crossref record (abstract) opened. The NC attribution "argue endorsement is a weak proxy for deliberative quality" came from search summaries and is **not** in the abstract.
    - What the abstract supports: the HM "fails Habermas's own criteria for legitimate discourse in three specific respects", and AI-mediated consensus tools produce "a synthetic public opinion that displaces argued consensus while retaining its appearance".
    - Fix: cite Farrow only for the abstract-level claims.
    - Note for the novelty hedge: this is a conceptual critique, published 12 Nov 2026. It does not test rankings, so the hedged novelty claim stands.
14. **Mahajan 2611.05135: wording.**
    - Evidence: the scout's "no human rating or ranking of statements" is right for coverage, but three human annotators did check the **assignment** measures (330 judgments). In the paper's words: "They did not check coverage (RQ3)" (p.12).
    - Fix: write "minority coverage was judged by LLM judges only".
15. **Fish et al. 2309.01291: version and venue.**
    - Evidence: the current arXiv abstract reports 84 of 100 participants "excellently" or "exceptionally" represented. A search result says an intermediate version reported 93 of 100 "mostly"/"perfectly", which I did not open. The EC 2024 venue (p.985) comes from researchr (search); the ACM page was not opened.
    - Fix: cite the arXiv version and number you quote (v3), and confirm the EC'24 DOI before citing it as EC.

---

## B. Per-reference status

### B1. Core T3-1 references (NC, NM, D4, D5)

| # | Reference (verified metadata) | Proposed claim, and where it was found | Status |
|---|---|---|---|
| 1 | Tessler, M.H., Bakker, M.A., Jarrett, D., Sheahan, H., Chadwick, M.J., Koster, R., Evans, G., Campbell-Gillingham, L., Collins, T., Parkes, D.C., Botvinick, M., Summerfield, C. "AI can help humans find common ground in democratic deliberation." *Science* 386(6719):eadq2852, 18 Oct 2024. doi:10.1126/science.adq2852. PMID 39418380 (Europe PMC). No corrections are listed. Text read: third-party PDF copy (rivista.ai, stamped "Downloaded from https://www.science.org on October 27, 2024"). | "empirical average minority weight = 0.29 ... revised statements b = 0.36, SE = 0.03, t = 2.64; Fig. 4C" (p.6). Note that 0.29 is both the initial statements' minority weight and the average minority size (29%).<br>"the Habermas Machine demonstrably incorporated minority critiques into revised statements" (p.1).<br>"prominently incorporated dissenting voices" (p.1).<br>"incorporated dissenting voices while respecting the majority position" (p.2).<br>"allowed minority positions to flourish"; "29 to 32% of rounds ... 20 to 26% of rounds" (p.5).<br>"did not appear to 'tyrannically' ignore the views of the minority" (p.8).<br>"No statistical differences ... whether they included the minority view ... SM 4.3.7" (p.4).<br>"statement rankings as well as their endorsement and quality ratings were all impacted by length" (p.4).<br>"paired preference = 68%" (cohort 1, p.4).<br>"96% of scores ... within the range" (p.6).<br>"caucus mediation process per se" (p.5).<br>Schulze aggregation of predicted rankings (p.9).<br>N = 5734 (p.2). | **VERIFIED** (main text). Every NC and D4 claim was found. |
| 1s | Tessler et al. 2024, Supplementary Materials (SM 4.3.7, 4.4.5, 5.5) | Third-party minority-inclusion result; minority-weight method | **COULD-NOT-OPEN** (see A1) |
| 2 | Wan, H., Wu, J., Luo, M., Li, F., Wang, N., Chen, N.F., Kan, M.-Y. "The Deliberative Illusion: Diagnosing Factual Attrition and Stance Homogenization in Multi-Agent LLM Deliberation." arXiv:2606.03032, 2 Jun 2026. | "multi-agent discussion erases up to 72% of issue-critical facts"; "agents can agree more while knowing less"; "the collapse of diverse positions toward consensus" (p.1, PDF). LLM agents only, three LLM families. | **VERIFIED** (NC wording). The TS quote is a CLAIM-MISMATCH (A4). |
| 3 | Mahajan, S., Argota Sánchez-Vaquerizo, J., Capozzi, A., Helbing, D. "From Opinions to Commitments: Unstable Assignments and Silent Choices in AI-Mediated Proposals." arXiv:2611.05135, 3 Nov 2026. | "prompts seeking agreement covered minority positions much less often than prompts asking to describe differences" (p.1, abstract). LLM judge for coverage (§4.3, p.6). Four mediators: Qwen3 8B, Gemma 3 12B, Mistral Small 3.2 24B, GPT-5.6 Terra (fetch). Humans did not check coverage (p.12). | **VERIFIED** (see A14 on wording) |
| 4 | Blair, C., Larson, K. "Generating Fair Consensus Statements with Social Choice on Token-Level MDPs." arXiv:2510.14106, 15 Oct 2025. | Simulated LM-policy agents (Llama 3.1 8B). Egalitarian search beats prompted-HM baselines on egalitarian perplexity (§6.3.1, Table 10; fetch, and the fetch flagged inconsistent baseline labels in the paper). Claim that the HM is not fair by construction (§1, fetch). Not "no human data": §6.1 uses human Likert ratings from 42 participants. | **VERIFIED** (fetch level) |
| 5 | Radharapu, B., Revel, M., Ung, M., Ruder, S., Williams, A. "Arbiters of Ambivalence: Challenges of using LLMs in No-Consensus tasks." Findings of ACL 2025, pp. 4677-4731. doi:10.18653/v1/2025.findings-acl.243. arXiv:2505.23820. | "take a stance on no-consensus topics" (abstract) | **VERIFIED** |
| 6 | Triantafyllopoulos, L., Kalles, D. "From Divergence to Consensus: Evaluating the Role of Large Language Models in Facilitating Agreement through Adaptive Strategies." arXiv:2503.15521, 3 Feb 2025. | Three LLMs as facilitators, alignment of proposals with participants' views (abstract, fetch) | **VERIFIED** |
| 7 | Revel, M., Pénigaud, T. "AI-Enhanced Deliberative Democracy and the Future of the Collective Will." arXiv:2503.05830, 6 Mar 2025. | Conceptual paper (abstract) | **VERIFIED** |
| 8 | Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S.R., Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S.R., Kravec, S., Maxwell, T., McCandlish, S., Ndousse, K., Rausch, O., Schiefer, N., Yan, D., Zhang, M., Perez, E. "Towards Understanding Sycophancy in Language Models." ICLR 2024 (PDF header "Published as a conference paper at ICLR 2024"). arXiv:2310.13548. | "match user beliefs over truthful ones"; "when a response matches a user's views, it is more likely to be preferred"; "prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time" (all p.1, abstract) | **VERIFIED** |
| 9 | Wen, J., Zhong, R., Khan, A., Perez, E., Steinhardt, J., Huang, M., Bowman, S.R., He, H., Feng, S. "Language Models Learn to Mislead Humans via RLHF." ICLR 2025 (proceedings.iclr.cc; search). arXiv:2409.12822. | "RLHF makes LMs better at convincing our subjects but not at completing the task correctly" (p.1, abstract) | **VERIFIED**, with the rebuttal flag in A2 |
| 10 | Jain, S., Park, C., Viana, M., Wilson, A., Calacci, D. "Interaction Context Often Increases Sycophancy in LLMs." CHI 2026 (arXiv comment). arXiv:2509.12517. | Single-user interaction context, 38 users (abstract) | **VERIFIED** |
| 11 | Farrow, R. "The 'Habermas' Machine: Synthetic Consensus and Pathologies of the Digital Public Sphere." *Philosophies* 11(6):219, published 12 Nov 2026. doi:10.3390/philosophies11060219. CC BY 4.0. Read via Crossref; mdpi.com returned 403. | Abstract-level claims in A13 VERIFIED. The NC/TS claim "endorsement is a weak proxy" was not found. | **VERIFIED** for abstract claims only. The "weak proxy" attribution is a CLAIM-MISMATCH. |
| 12 | Parisi, A., Thain, N., Hallak, A., Tsai, V., Qian, C. "Real-Time Group Dynamics with LLM Facilitation: Evidence from a Charity Allocation Task." arXiv:2605.14097, 13 May 2026. doi:10.1145/3805689.3812253 (venue not resolved). | NC proposed no claim. Abstract: 879 participants; facilitation did not improve consensus, shifted allocations, and participants preferred it (fetch). | **VERIFIED** (abstract) |
| 13 | Sharoff, S. "The Almost Intelligent Revolution: Options for Scaling Up Deliberation and Empowering People with AI." arXiv:2606.19864, 2026. Chapter in *Handbook of Democracy in the Era of Artificial Intelligence* (eds. Pournaras et al.). | Snippet only in NC; no claim proposed | **VERIFIED** (metadata; there is nothing to cite it for yet) |
| 14 | Low, J., Duys, O., Formanek, C., Bakker, M., Hammond, L. "Habermolt: Delegating Deliberation to AI Representatives." arXiv:2605.24413, 23 May 2026. | No claim proposed | **VERIFIED** (metadata) |
| 15 | Zaghouani, W. "Accountable Human-AI Deliberation with LLMs: Scaling Collective Intelligence through Symbiotic Scaffolding." arXiv:2605.26940, 26 May 2026. Accepted at the LREC 2026 2nd Workshop on Language-driven Deliberation Technology (arXiv comment; the PDF itself names no venue). | Erasure(s) = Σ sal(x_i)(1 − max_c sim(c, x_i)) over salient critiques (p.5). "flagging clusters where max sim(c, C_k) < 0.7 ... this threshold should be calibrated to human judgments ... through pilot annotation studies" (p.4). "testable blueprint" (p.1). Absence of a ranking study and of validation is consistent with the blueprint framing; the absence was not exhaustively searched. | **VERIFIED** |
| 16 | Zhu, S., Yang, S., Bakker, M.A., Pentland, A., Pei, J. "Can AI Truly Represent Your Voice in Deliberations? A Comprehensive Study of Large-Scale Opinion Aggregation with LLMs." arXiv:2510.05154 (v1 2 Oct 2025; read v5, 20 Mar 2026). | 0.504 (DeliberationJudge/DeBERTa, representativeness Pearson; App. G.2, Tables 9 and 10). GPT-5 3-shot 0.398 (Table 10). "Overall, correlations never exceed 0.4" (§3.1). 18 LLMs benchmarked. Minority defined by self-report or by LOF on all-MiniLM-L6-v2 embeddings (top 10%). Four dimensions on a 5-point Likert scale. "Upon publication, we will release..." | **VERIFIED** (see A11 on wording) |
| 17 | Zhang, Y., Zhang, N., Liu, Y., Fabbri, A., Liu, J., Kamoi, R., Lu, X., Xiong, C., Zhao, J., Radev, D., McKeown, K., Zhang, R. "Fair Abstractive Summarization of Diverse Perspectives." NAACL 2024 (arXiv comment). arXiv:2311.07884. | BUR, UER, AUC and SOF (§5); τ = 0.8 (§5). "68.97% Krippendorff's alpha" (§6.3; NM writes 0.69). Randolph's kappa 0.41 across 4 annotators (§6.3). Reference summaries also unfair (§6.2). github.com/psunlpgroup/FairSumm. | **VERIFIED** |
| 18 | Shandilya, A., Dash, A., Chakraborty, A., Ghosh, K., Ghosh, S. "Fairness for Whom? Understanding the Reader's Perception of Fairness in Text Summarization." FILA 2020 workshop at IEEE BigData 2020. arXiv:2101.12406. | Perceived Opinion Bias = Gini coefficient of per-opinion representation (p.7). POB correlations are higher than ROUGE (Table II, p.8). | **VERIFIED** (see A12 on wording) |
| 19 | Khosravani, M., Huang, C., Trabelsi, A. "Enhancing Argument Summarization: Prioritizing Exhaustiveness in Key Point Generation and Introducing an Automatic Coverage Evaluation Metric." NAACL 2024. arXiv:2404.11793. | 83.18 / 77.27 / 64.84% at 100 / 75 / 50% coverage (ArgKP, Table 2, §4.1). 90.01% micro precision (§5.2.1). github.com/b14ck-sun/arg-sum. | **VERIFIED** (NM's rounding is fine; these are ArgKP numbers) |
| 20 | Huang et al., WASSA 2023 | Title as proposed is wrong (A8) | **METADATA-MISMATCH** |
| 21 | Mahajan, S. "Participatory provenance as representational auditing for AI-mediated public consultation." arXiv:2604.20711, 22 Apr 2026. | 5,253 records, Canada 2025 consultation; "statistical significance depended on the embedding model"; "higher observed mean coverage than exact-length random text" (abstract, fetch) | **VERIFIED** |
| 22 | Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E.P., Zhang, H., Gonzalez, J.E., Stoica, I. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023 Datasets and Benchmarks. arXiv:2306.05685. | "achieving over 80% agreement"; "position, verbosity, and self-enhancement biases" (abstract) | **VERIFIED** |
| 23 | Cachola, I., Khashabi, D., Dredze, M. "Evaluating the Evaluators: Are readability metrics good measures of readability?" EMNLP 2025, pp. 24011-24027. doi:10.18653/v1/2025.emnlp-main.1225 (ACL Anthology). arXiv:2508.19221. | "6 of the 8 metrics have a poor correlation (less than 0.3 Pearson correlation)" (p.2). FKGL Pearson 0.16 (Table 2a, p.5). Best LM 0.56, Llama 3.3 70B (Table 2b, p.5; abstract). | **VERIFIED** (previously snippet-only; now opened) |
| 24 | Fish, S., Gölz, P., Parkes, D.C., Procaccia, A.D., Rusak, G., Shapira, I., Wüthrich, M. "Generative Social Choice." arXiv:2309.01291 (v1 3 Sep 2023). EC 2024 per researchr (search only). | Proportionally representative slate built with LLM queries. "has traditionally only been applicable to choices among a few predetermined alternatives". "84 out of 100 participants feel 'excellently' or 'exceptionally' represented" (current abstract) | **VERIFIED** (arXiv; see A15) |
| 25 | Boehmer, N., Fish, S., Procaccia, A.D. "Generative Social Choice: The Next Generation." ICML 2025 (arXiv comment). arXiv:2505.22939. | "A common approach in previous work has been to craft a single consensus statement that every participant endorses" (§1.2, Related Work, **not** the abstract) | **VERIFIED** |
| 26 | Blair, C. "Deliberative Machines: From Reflective Dialogue to Fair Consensus with Language Models and Social Choice." University of Waterloo thesis, 2025. hdl:10012/21859. | "HM lacks fairness guarantees": not in the abstract | **CLAIM-MISMATCH** (A6) |
| 27 | Yao, B., Shang, C., Du, W., He, J., Lian, R., Zhang, Y., Su, H., Swamy, S., Qi, Y. "Peacemaker or Troublemaker: How Sycophancy Shapes Multi-Agent Debate." arXiv:2509.23055, 27 Sep 2025 (no venue found). | "sycophancy is a core failure mode that amplifies disagreement collapse" (abstract) | **VERIFIED** |
| 27b | arXiv:2604.02668, attributed to "Yao et al." | Actually Kasprova et al., SIGDIAL 2026 (A5) | **METADATA-MISMATCH** |

### B2. Bridging and Community Notes references (PB; every quote rechecked against the arXiv API abstract text)

| # | Reference | Quote check | Status |
|---|---|---|---|
| 28 | Wojcik, S., Hilgard, S., Judd, N., Mocanu, D., Ragain, S., Hunzaker, M.B.F., Coleman, K., Baxter, J. "Birdwatch: Crowd Wisdom and Bridging Algorithms can Inform Understanding and Reduce the Spread of Misinformation." arXiv:2210.15723, 2022. | "identify annotations that appeal broadly across heterogeneous user groups": exact. Those who saw bridging-selected annotations were "significantly less likely to reshare". | **VERIFIED** |
| 29 | Ovadya, A., Thorburn, L. "Bridging Systems: Open Problems for Countering Destructive Divisiveness across Ranking, Recommenders, and Governance." arXiv:2301.09976, 2023. | "systems which increase mutual understanding and trust across divides": exact. Full text not read, so no open-problems claim may be attributed. | **VERIFIED** (abstract claim only) |
| 30 | Milli, S., Thorburn, L., Bouchaud, P., Wang, Y., Garg, N., Pierson, E. "Bridging in Social Media Feeds Censors Controversial Topics." NeurIPS 2024 Pluralistic Alignment **Workshop**. | "it can also downrank URLs that relate to controversial topics": exact. "70 million URLs shared on Facebook": exact. | **METADATA-MISMATCH** (venue; A7) |
| 31 | Revel, M., Milli, S., Lu, T., Watson-Daniels, J., Nickel, M. "Representative Ranking for Deliberation in the Public Sphere." arXiv:2503.18962 (v2, 9 Jul 2025; no venue stated). | "these interventions may also inadvertently reduce the visibility of legitimate viewpoints" (abstract, exact). "solely focusing on conversational quality might inadvertently result in the censorship of certain groups" (§1, fetch, exact). | **VERIFIED** |
| 32 | Hafid, S., Berriche, M., Cointet, J.-P. "Algorithmic Approaches to Opinion Selection for Online Deliberation: A Comparative Study." arXiv:2602.15439, 17 Feb 2026. | "enforcing consensus-seeking algorithmic strategies can imply ignoring or flattening conflicting preferences" and "which may lead to erasing minority voices and reducing content diversity": both exact, from the abstract | **VERIFIED** |
| 33 | Fish et al. 2023 (= #24) | "has traditionally only been applicable to choices among a few predetermined alternatives": exact. 84/100: found. | **VERIFIED** |
| 34 | Small, C., Bjorkegren, M., Erkkilä, T., Shaw, L., Megill, C. "Polis: Scaling Deliberation by Mapping High Dimensional Opinion Spaces." *RECERCA* 26(2), 2021. doi:10.6035/recerca.5516. | "building shared understanding" and "cultivating points of consensus": both in the abstract. The "respect dissent" claim was not checked and must not be cited. | **VERIFIED** (abstract claims only) |
| 35 | Boehmer et al. 2025 (= #25) | PB said NOT OPENED; it has now been opened, and the quote is in §1.2 | **VERIFIED** |
| 36 | Turan, D., McKenzie, C. "How can AI be used to inform policymaking?" AI4Democracy series, IE Center for the Governance of Change, June 2024 (Talk to the City, developed by the AI Objectives Institute; p.10). | Metadata from the PDF's own "Suggested citation" (p.36). No claim was proposed by PB. | **VERIFIED** (metadata) |
| 37 | Goyal, M., Arora, N., Goel, A. "Quality-Sensitive Matrix Factorization for Community Notes: Towards Sample Efficiency and Manipulation Resistance." arXiv:2604.11224, 2026. | No claim proposed | **VERIFIED** (metadata) |
| 38 | "2025 study: Community Notes vulnerable to rater bias and manipulation" (wiki summary) | Source not identified | **COULD-NOT-OPEN** |

### B3. T3_scout references (mostly for Ideas 2 and 3, which were not pursued)

| # | Reference | Check | Status |
|---|---|---|---|
| 39 | google-deepmind/habermas_machine (GitHub) | 4 parquet files listed; ~450 MB on GCS; Apache 2.0 for software; "All other materials" CC-BY 4.0 (the data is not named explicitly) | **VERIFIED** |
| 40 | De, S., Bakker, M.A., Baxter, J., Saveski, M. "Supernotes: Driving Consensus in Crowd-Sourced Fact-Checking." WWW '25, pp. 3751-3761. doi:10.1145/3696410.3714934 (search: MIT DSpace). arXiv:2411.06116. | 91% (abstract); preferred 75.2% of the time | **VERIFIED** |
| 41 | Li, H., De, S., Revel, M., Haupt, A., Miller, B., Coleman, K., Baxter, J., Saveski, M., Bakker, M.A. "Scaling Human Judgment in Community Notes with LLMs." arXiv:2506.24118. | RLCF (abstract) | **VERIFIED** |
| 42 | Li, H., Bakker, M.A. "AI Fact-Checking in the Wild: A Field Evaluation of LLM-Written Community Notes on X." arXiv:2604.02592. | 1,614 notes; 108,169 ratings; 42,521 raters; more positive ratings "across raters with different political viewpoints" | **VERIFIED** |
| 43 | Reber, D., Reber, J., Holtzman, A., Veitch, V. "Can LLMs Anticipate Their Cruxes?" arXiv:2610.21006. | "a sub-question that a model's rollouts disagree on" | **VERIFIED** |
| 44 | Tan, C., Niculae, V., Danescu-Niculescu-Mizil, C., Lee, L. "Winning Arguments: Interaction Dynamics and Persuasion Strategies in Good-faith Online Discussions." WWW 2016. arXiv:1602.01103. ConvoKit page: 3051 conversations, 293,297 utterances, `download("winning-args-corpus")`. | All match | **VERIFIED** |
| 45 | Labruna, T., Modzelewski, A., Satta, G., Da San Martino, G. "Detecting Winning Arguments with Large Language Models and Persuasion Strategies." arXiv:2601.10660. | Pairwise task description not in the abstract | **CLAIM-MISMATCH** |
| 46 | Hackenburg, K., Tappin, B.M., Hewitt, L., Saunders, E., Black, S., Lin, H., Fist, C., Margetts, H., Rand, D.G., Summerfield, C. "The levers of political persuasion with conversational AI." *Science* 390(6777), Dec 2025. doi:10.1126/science.aea3884 (search: LSE repository, OII). arXiv:2507.13919. | N=76,977; 19 LLMs; 707 issues (abstract). "information density explains 44%" (full text). Accuracy 56% vs 70% (Study 2) and 72% vs 82% (Study 3), so "56-72%" spans two studies. | **VERIFIED** (Science metadata at search level) |
| 47 | Costello, T.H., Pennycook, G., Rand, D.G. "Durably reducing conspiracy beliefs through dialogues with AI." *Science* 385(6714):eadq1814, 2024. | 2190 participants; ~20%; 2 months (Europe PMC abstract) | **VERIFIED**, but **HELD** out of the bib (expression of concern; A3) |
| 48 | Salvi, F., Horta Ribeiro, M., Gallotti, R., West, R. "On the conversational persuasiveness of GPT-4." *Nat Hum Behav* 9(8):1645-1653, 2025. | 81.2% relative odds increase confirmed. The non-personalised null was not found. Erratum 2026. | **CLAIM-MISMATCH** (partial) |
| 49 | Liu, J., Salvi, F., Schoenegger, P., et al. (40 authors). "When Large Language Models are More Persuasive Than Incentivized Humans, and Why." arXiv:2505.09662. | Claude 3.5 Sonnet more persuasive than incentivised humans in truthful and deceptive settings; accuracy up when truthful and down when deceptive; "wanes over repeated interactions" | **VERIFIED** |
| 50 | Khan, A., Hughes, J., Valentine, D., Ruis, L., Sachan, K., Radhakrishnan, A., Grefenstette, E., Bowman, S.R., Rocktäschel, T., Perez, E. "Debating with More Persuasive LLMs Leads to More Truthful Answers." ICML 2024, PMLR 235:23662-23733 (search). arXiv:2402.06782. | 76%/88% vs 48%/60% (abstract). The consultancy sub-claim was not found in the abstract (A10). | **VERIFIED** (debate numbers; consultancy sub-claim unchecked) |
| 51 | Cheng, M., Yu, S., Lee, C., Khadpe, P., Ibrahim, L., Jurafsky, D. "ELEPHANT: Measuring and understanding social sycophancy in LLMs." ICLR 2026 (search). arXiv:2505.13995. | 45 percentage points; 48% | **VERIFIED** |
| 52 | Schoenegger, P., Park, P.S., Karger, E., Trott, S., Tetlock, P.E. "AI-Augmented Predictions: LLM Assistants Improve Human Forecasting Accuracy." *ACM TiiS* 15(1), 2025. doi:10.1145/3707649 (search). arXiv:2402.07862. | "by between 24 percent and 28 percent"; the second assistant is "overconfident and base-rate neglecting" | **VERIFIED** |
| 53 | Conlon, J.J., Schwardmann, P. "AI Sycophancy and Decisions." CESifo Working Paper 12681, May 2026. | 1,500 participants; 30 decision environments; advice "depolarizes"; "Increasing sycophancy weakens depolarization" (p.3) | **VERIFIED** |
| 54 | Stray, J., Yang, D.Z., Luo, S., Takagi, M.N., Chang, S. "Political Neutrality as Balanced Approval: A Large-Scale Human Evaluation of AI Responses." arXiv:2605.28911. | 208,152 evaluations; 7,434 participants; default responses lean liberal | **VERIFIED** |
| 55 | Xu, R., Qi, X., Qi, Z., Xu, W., Guo, Z. "DebateQA: Evaluating Question Answering on Debatable Knowledge." arXiv:2408.01419. | Dispute Awareness metric | **VERIFIED** |
| 56 | Zhou, X., et al. "Mind the Sim2Real Gap in User Simulation for Agentic Tasks." COLM 2026. arXiv:2603.11245. | Human USI is 92.7, not 92.9 (A9) | **CLAIM-MISMATCH** |
| 57 | Feroz, F., Kunst, J.R. "Can AI Debias the News? ..." arXiv:2605.01006. | Six models; no human effect; backfire predicted wrongly | **VERIFIED** |
| 58 | Cui, Z., Li, N., Zhou, H. "Can Large Language Models Replace Human Subjects? ..." arXiv:2409.00128. | 156 experiments, not 154 (A9) | **CLAIM-MISMATCH** |
| 59 | Chuang, Y.-S., et al. "DEBATE: A Large-Scale Benchmark for Evaluating Opinion Dynamics in Role-Playing LLM Agents." NeurIPS 2026 Evaluations and Datasets track (arXiv comment). arXiv:2510.25110. | "RPLA groups exhibit strong opinion convergence relative to human groups" | **VERIFIED** |
| 60 | Karger, E., Bastani, H., Yueh-Han, C., Jacobs, Z., Halawi, D., Zhang, F., Tetlock, P.E. "ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities." arXiv:2409.19839. | Metadata only; dataset availability not checked | **VERIFIED** (metadata) |
| 61 | Nie, S., Omoomi, K., Flek, L., Zhao, Z., Welch, C. "PERSPECTRA: A Scalable and Configurable Pluralist Benchmark of Perspectives from Arguments." ICLR 2026 (search: iclr.cc poster page). arXiv:2602.08716. | Kialo plus Reddit; 100 topics | **VERIFIED** |
| 62 | Radharapu et al. (= #5); Tessler (= #1); Wan (= #2) | See above | See above |

Not proposed for citation, so not checked: Bakker et al. 2022 and Small et al. 2023 (NC lists them as not yet searched).

## C. Counts (61 unique references; #33, #35 and #62 are duplicate rows)
| Status | Count | Rows |
|---|---|---|
| VERIFIED | 51 | Includes Farrow (abstract claims only) and Costello (held out of the bib) |
| CLAIM-MISMATCH | 5 | #26, #45, #48, #56, #58 (plus the Farrow "weak proxy" attribution, noted in #11) |
| METADATA-MISMATCH | 3 | #20, #27b, #30 |
| COULD-NOT-OPEN | 2 | #1s, #38 |

refs.bib holds only VERIFIED entries (50: the 51 VERIFIED minus Costello). A mismatched reference may enter the bib only after the author applies the fix in section A and the verifier rechecks it.
