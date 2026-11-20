## 1. Introduction

<!-- Editor edits 5, 6 and hostile B8 (report/review_editor.md, review_hostile.md; D60). SOURCES: 82.8% = RESULTS_MAIN.md prevalence (SIDED 0.8285); N2 = N2_RESULTS.md section 6. -->

Language models are being used as mediators in deliberation: group members write opinions on a question, a model drafts candidate statements meant to speak for the whole group, and the members rank the candidates. The Habermas Machine picks the winner by aggregating these rankings, and its statements helped groups find common ground [CITE:tessler2024habermas]. Such rankings are also the obvious training signal for future mediators.

That creates a risk. A statement can win broad approval by leaving out, blurring or one-sidedly settling the points on which the group actually disagrees, so that each member reads it as compatible with their own view. We call this **crux erasure**: a statement hides a crux when a reader of the statement alone would not learn that members disagreed on that point. If rankings reward crux erasure, a system trained on approval will learn to hide disagreement. We frame this, as our own hypothesis, as a group analogue of sycophancy, in which preference data favour responses that match the user's views over accurate ones [CITE:sharma2024sycophancy]. The original study points the other way: its revised statements "demonstrably incorporated minority critiques" [CITE:tessler2024habermas], on a stance measure that cannot tell a statement that names a disagreement from a vague one (Section 2). To our knowledge, prior work did not link what participants reward to disagreement-hiding content.

**Contributions.**

- To our knowledge, the first test of whether participants' rankings of candidate statements favour hiding disagreement: within-round and per-rater, with length and readability controls, pre-registered, on 721 launches held out from all prompt development.
- A crux erasure score that takes the disagreement from the opinions alone. Its detection of disagreement was validated against participants' own pre-deliberation position ratings, for whether a group disagrees, not for whether a statement hides it; its hide/show judgement is not human-validated.
- An exploratory prompt grid (N2): across five open-weight models writing for the same 250 rounds, a "keep everyone satisfied" system prompt raised scored E relative to "be accurate about differences" in all five (statements not ranked by people).
- A record of what did not work: no candidate second scorer, a human check not done in time, and an estimate that depends on the length control.

The pre-registered test gave a small association whose sign depends on whether length is controlled and whose precision depends on how (Section 4), so this paper does not settle whether participants reward hidden disagreement; it shows what such a test needs. By the scorer's reading, most hiding is one-sided (82.8% of crux labels are SIDED), so the test cannot separate rewarding hidden disagreement from rewarding a statement that states the rater's side.
