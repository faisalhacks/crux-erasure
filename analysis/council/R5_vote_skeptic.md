# R5 vote — skeptic (hostile reviewer) seat

Read: R5_PROPOSAL.md; decisions.md D49, D49a, D49b, D49c; BRIEF.md §3–§4. No score, rank or rating value read; nothing computed.

**Vote: APPROVE-WITH-CONDITIONS.**

The design is mostly honest about its own limits (R5.1.3 "what it cannot show", R5.2.4 power, R5.8). Its main fault: it lets a check that covers presence only unlock confirmatory claims about hiding. A hostile reviewer would see this at once. Step 2 validates component (a) only. The hypothesis tested in A2 is about `E`'s show-versus-hide contrast within a round, and R5.1.3 says step 2 shows "anything about `E`'s within-round variation" cannot be shown. Calling A2 "confirmatory" under VALIDATED_PRESENCE (R5.6) therefore overclaims.

## Binding conditions

1. **VALIDATED_PRESENCE must not make A2 confirmatory.** Under that status, `beta_E`, N1 and every `E`-based rate are reported as "pre-registered test; the predictor's hide/show contrast is not human-validated". The words "confirm", "confirmatory" and "detected" are not used for them. Holm-adjusted p-values may be printed.
2. **Step 2 PASS + step 3 CONTRADICTED → EXPLORATORY_UNVALIDATED** for every `E`-based result. CONTRADICTED still does not FAIL the gate (Q6). But when the only human look at the hide call agrees with it no better than chance, no confirmatory `E` analysis is defensible.
3. **Wording of step 2.** "Validated against participants' own pre-deliberation position ratings" only with the scope phrase "for whether a group disagrees, not for whether a statement hides it" in the same sentence. Allowed only on PASS. On WEAK, write "agreed only weakly with". The bare D49 phrase is never used. Methods state plainly that D49 step 2's goal, a participant reference for *hidden* disagreement, could not be met because no such signal exists (D49a).
4. **H5 is not a headline.** Title and abstract never give H5 without, in the same sentence, n, the Wilson interval, "one hypothesis-aware author" and "LLM-extracted quotes". It is never phrased as a prevalence of hiding in the population.
5. **Author exposure disclosure.** Before `author_verification.csv` is hashed, a decisions.md entry records whether the author had previously seen any of the 25 statements, or their scores, during development (R4 sample work, debugging). The paper prints it.
6. **VALIDATED_HIDE_EVIDENCE directional claims** must also state "n = k items with Q1 = YES, Fisher p = …, single non-blind author". The claim never appears in the title.
7. **Panel stays out of the argument.** Panel numbers never appear in the abstract, and never in the same paragraph as a validation claim used as corroboration. Text says P1 shares its inputs (the same quotes) with the author, so agreement is partly built in.
8. **Novelty sentence** ("first attempt…") only after a logged literature search under hard rule 4. Otherwise it is dropped.
9. Hsplit class counts are printed beside BA2, and BA2 is printed with sens and spec in the main text, not only in an appendix.

## Open questions

1. Yes, scoped wording, and only on PASS (condition 3).
2. Acceptable as "step 2", but only as a presence check. For the hiding construct, report "no usable participant reference" (condition 3).
3. Keep 0.60 plus a lower bound above 0.5. At n ≈ 1,600 a lower bound alone is vacuous. The bar is stricter than the BRIEF §4 bar, which is permissible.
4. Exclude gpt-oss from the panel (self-evaluation). Drop P2. It is model-against-model on items no human labelled, and it only adds forking paths. If P2 is kept, it goes in the appendix only.
5. Confirmed.
6. No FAIL, but downgrade (condition 2).
7. Accept. `N2_VALIDATED` is unavailable, and the Amendment 5 path needs its own vote and hash before any N2 scoring.
8. Leave both out of the paper body. The critique analysis is winner-selected and LLM-coded, so it should not run at all. The survey gap may appear in the appendix only, labelled exploratory, with its rule written down before it runs.
