# R5 vote: editor seat (feasibility, timing, paper coherence)

Read: R5_PROPOSAL.md; decisions.md D41, D44, D46-D49c; BRIEF.md §0, §3, §13; status.md. No score, rank, rating value or label read. Nothing computed.

**VOTE: APPROVE-WITH-CONDITIONS**

## Binding conditions

1. **The packet goes out first.** The human's 25 labels are the only step that cannot be sped up with compute, and status NOT_EVALUATED (R5.6) would leave a paper with no real-data results. Releasing the packet waits only on the D49b/D49c build and the R5.2.1 hashes. It never waits on panel smokes, step-2 code, or the N2 amendment.
2. **One draft frame per status, written before the gate is recorded.** Write a title, an abstract results sentence and a claims list for each status in R5.6, starting with EXPLORATORY_UNVALIDATED and VALIDATED_PRESENCE. By R5's own statements these are the likely outcomes: step 3 is "likely INCONCLUSIVE" (R5.2.4), and step 2's specificity is "expected to be low" (R5.1.3). When the gate is recorded, pick the matching frame. Nothing gets reframed after the result.
3. **A pass/fail bar for panel format.** Use R5.3 as written: at least 20 dev calls per model, at least 95% valid after one retry (so 1 failure is the most allowed), at most one revision of the format line, and the decision is fixed before any packet call. The D41/D46/D48 failures were label-count and parse failures on the scorer task, so they tell us little about a two-key yes/no JSON. Smoke the three models in parallel and off the critical path. If fewer than 2 pass, report "no panel" and move on. No re-runs and no substitute models.
4. **Cut task P2.** It adds model-versus-model numbers on 50 items with no human comparison. That is more forking paths and nothing for the paper (see Q4).
5. **N2 Amendment 5 is hashed before any N2 scoring.** N2 scoring (about 1 h on Modal) then runs as soon as the amendment exists, with its outputs sealed (hash recorded, not opened) until the gate is recorded. This keeps the scoring off the post-gate critical path and leaves hard rule 3 intact: these are scores on generated statements, not ranks.
6. **AI disclosure.** The LLM-use statement names gpt-oss-120b as quote extractor, Qwen3.8-27B as the only scorer (also an N2 generator), the panel and its result (or "no panel"), and the agentic pipeline that wrote the code and drafts. The only human judgement is the author's, given with the hypothesis known, on 25 items. LAYOUT_DEFECTS lists this statement as missing, so it is required before handover.
7. **Wording scope from R5.1.1, everywhere.** That includes the abstract and figure captions.

## Open questions

1. **Yes, use the scoped wording.** The bare phrase would let a reader think the hiding call was validated. A reviewer who catches that would treat it as overclaiming, which is grounds for rejection.
2. **Accept step 2 as written.** It is the human's step 2 and it is pre-registered. In the paper, though, it is called "validation of the disagreement-presence component" and never "primary validation of the scorer". The paper's construct is hiding, and the headline must not suggest otherwise.
3. **Keep the 0.60 point bar.** At about 1,600 rounds, "lower bound > 0.5" is nearly vacuous (R5.8 item 2). Reviewers dislike validations that cannot fail (BRIEF §10).
4. **Exclude gpt-oss**, since judging its own extraction is self-evaluation. **Do not run P2** (condition 4).
5. **Confirm.** Usable-but-unsupportive results go to EXPLORATORY_UNVALIDATED. The stricter reading is the coherent one.
6. **No.** With 10-20 usable items, CONTRADICTED is underpowered (R5.2.4). Report it in the text as R5 specifies. It must not fail the gate.
7. **Accept.** With 6 items there is no N2 validation path. N2 stays EXPLORATORY and is presented as a descriptive extension, not as the lead.
8. **Leave both out entirely.** Neither is needed for any frame in condition 2. Both add post-gate forking paths, and the critique coding is LLM-mediated and selected on the winner. Mention them as future work in one sentence.

## Feasibility

About 11 h remain until the deadline. Everything except the human's labelling can run in parallel: packet build, step-2 code and synthetic tests, panel smokes, the N2 amendment and sealed N2 scoring, and the pre-drafted frames. After the gate is recorded, the remaining work is running the analyses already coded (status.md) and choosing a frame. That is feasible if the packet is released early. BRIEF §0 still governs. If the labels arrive late, report the paper as NOT_EVALUATED. Do not cut checks to make it fit. Nothing here is cut because of the clock. P2 and the Q8 analyses are cut because they add no claim the paper can make.
