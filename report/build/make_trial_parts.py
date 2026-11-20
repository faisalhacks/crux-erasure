"""Writes PLACEHOLDER trial parts (no real drafts existed at setup time). Not report content."""
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trial_parts")
os.makedirs(D, exist_ok=True)
para = ("PLACEHOLDER text for layout trial only; it carries no claim. " * 9).strip()


def w(name, s):
    open(os.path.join(D, name), "w", encoding="utf-8").write(s)


abstract = " ".join(["placeholder"] * 190)
w("00_front.md", "# [PROJECT TITLE] (TRIAL LAYOUT, placeholder text)\n\nAuthor 1, Affiliation  \nAuthor 2, Affiliation\n\n"
  "With Apart Research\n\n*Research conducted at the AI x Epistemics Research Sprint, November 2026*\n\n"
  f"## Abstract\n\n{abstract}\n")
w("10_intro.md", f"## 1. Introduction\n\n{para}\n\n{para}\n\n## 2. Related Work\n\n{para}\n\n{para}\n")
w("20_methods.md", f"## 3. Methods\n\n{para}\n\n{para}\n\n{para}\n\n![Dummy figure 1. Takeaway caption goes here.](dummy1.png){{width=100%}}\n")
w("30_results.md", f"## 4. Results\n\n{para}\n\n![Dummy figure 2. Takeaway caption.](dummy2.png){{width=100%}}\n\n{para}\n\n"
  "| Condition | Estimate | 95% CI |\n|---|---|---|\n| A | 0.40 | [0.30, 0.50] |\n| matched control | 0.50 | [0.40, 0.60] |\n\n"
  "![Dummy figure 3, small.](dummy3.png){width=45%}\n")
w("40_discussion.md", f"## 5. Discussion and Limitations\n\n{para}\n\n## 6. Conclusion\n\n{para}\n")
w("90_back.md", f"## Code and Data\n\n{para}\n\n<div class=\"pb\"></div>\n\n## References\n\n[1] PLACEHOLDER.\n\n"
  f"## Appendix A. Limitations and Dual-Use / Ethical Considerations\n\n{para}\n\n## LLM Usage Statement\n\n{para}\n")
print("ok")
