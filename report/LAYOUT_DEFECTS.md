# Layout defects (TRIAL LAYOUT, not final) - 2026-11-15

Built by `report/build/build.py` from the current drafts (abstract_skeleton, related_work, methods_draft, limitations_dualuse_draft) + a dummy results scaffold (3 watermarked dummy figures, 1 dummy table). Output: `report/build/out/TRIAL_layout.pdf`, page PNGs `out/pg-NN.png` (80 dpi), `out/checks.json`. Every number below is from checks.json or from reading the PNGs. The HUMAN builds and submits the real PDF.

## Template status
- Official template = Google Doc (copy link in `skills/layout_apart_template.md`). Fetched its text via export (works without login). No LaTeX/Overleaf/docx source. Section order captured: Title/authors/"With Apart Research"/event footnote, Abstract, 1 Introduction, 2 Related Work, 3 Methods, 4 Results, 5 Discussion and Limitations (incl. Future Work), 6 Conclusion, Code and Data, Author Contributions (optional), References, Appendix (optional), LLM Usage Statement. Template says ~4 pages recommended excluding refs/appendix; the sprint rule is an 8-page cap.
- Not reproducible locally: exact fonts, margins, info box, styles (Google Doc not rendered). Trial uses ASSUMED Letter, 1 in margins, Arial 11 pt. Final must be pasted into a copy of the Google Doc by a human.
- Toolchain: pandoc 3.11 + Edge headless (HTML to PDF) + PyMuPDF. No LaTeX, Typst or LibreOffice installed; nothing installed system-wide.

## Checks
| Check | Result | Verdict |
|---|---|---|
| Main body vs 8-page cap | body ends on p.5 of 6 total (appendix heading starts bottom of p.5); drafts are mostly skeleton, so this is a floor, not a forecast | OK for now; recheck with real Results/Discussion |
| Abstract words (150-250) | 197 counted, but that is the skeleton's slot instructions (incl. "[RESULT SLOT]"), not an abstract | UNKNOWN; recount on real abstract by script |
| Figures | dummy 6.3x3.1 in and 6.3x4.4 in legible; 2.9x2.1 in figure legible only barely (axis text ~6 pt) | Real figures: minimum 8 pt text at final size; avoid <3.2 in wide |
| Fonts embedded | Arial, Arial Bold, Consolas (PyMuPDF font list) | OK in trial; Google Doc export must be rechecked |
| Required sections present | MISSING: Introduction, Discussion, Conclusion, Results (only dummy), LLM Usage Statement, References, Code and Data | HIGH |
| Limitations + dual-use appendix | present as skeleton (`limitations_dualuse_draft.md`) | OK, content unfilled |

## Defects
| # | Flaw | Where | Sev | Fix |
|---|---|---|---|---|
| 1 | No Introduction, Discussion, Conclusion, References, Code and Data, LLM Usage Statement parts exist | whole report | HIGH | write parts; LLM statement must be factual (BRIEF requires it though sprint page does not) |
| 2 | Drafts are titled "(draft)/(skeleton)" with their own H1s and notes; template wants numbered sections 1-6 | all parts | MED | strip H1s/notes; renumber to template (Methods is "3", not "1/2/3/4" inside) |
| 3 | Methods internal numbering ("1. Data" ... "4. Analysis plan") collides with template numbering | methods_draft.md | MED | use unnumbered subheads (3.1, 3.2) |
| 4 | Gate-1 paragraph renders as one run-on block: list items written as " - Step 1: ..." on one line, not markdown list | methods_draft.md p.3 | MED | put each step on its own line starting with "- " after a blank line |
| 5 | Table touches next heading (no spacing after table) in trial CSS | p.5 | LOW | add margin below tables; in Google Doc add spacer |
| 6 | Abstract skeleton includes instruction text; word count meaningless until replaced | abstract_skeleton.md | MED | count by script on final text; keep 150-250 |
| 7 | Dummy figure 3 watermark clipped when sized at 45% (dummy artifact only) | p.5 | INFO | n/a to real figures; real figures: no in-figure watermark |
| 8 | No figure/table yet from scripts; template requires at least one figure with takeaway caption, CIs | Results | HIGH | `figures/make_figures.py` outputs are not yet in `figures/*.pdf`; use PNG/PDF at final width |
| 9 | Pandoc cannot embed PDF figures into HTML; build uses PNG | build | LOW | export each figure as PNG (>=200 dpi) as well as PDF |
| 10 | Placeholder tokens like [FROZEN:...], [RESULT SLOT] still in text | methods, abstract | HIGH if shipped | grep for `\[[A-Z_:a-z]*SLOT\]` and `\[FROZEN` before any submit |

## Status update 2026-11-16 (draft-layout round; see DRAFT_STATUS.md)
Build is now `report/build/build.py` (explicit template order from report/parts + drafts), output `out/DRAFT_layout.pdf`, `out/pg-NN.png`, `out/checks.json`, `out/DRAFT_combined.md`; a one-branch-per-group length check in `out/lengthcheck/`.
- **#1 FIXED (text):** Introduction, Results (slots), Discussion, Conclusion, Code and Data, References, Appendix B and LLM Usage Statement now exist in report/parts/.
- **#2 FIXED:** template numbering 1-6 (1. Introduction ... 6. Conclusion), unnumbered Code and Data / References / Appendix A / Appendix B / LLM Usage Statement; draft titles and notes moved into HTML comments.
- **#3 FIXED:** methods subsections are unnumbered (### Data, Crux erasure score, Validation, Analysis).
- **#4 FIXED:** the run-on gate-1 block is gone (gate-1 text replaced by a D49 slot); every list is a real markdown list (checked on p.4-5 of the PNGs).
- **#5 OPEN (LOW):** table spacing improved by CSS margin; recheck in the Google Doc.
- **#6 FIXED:** abstract is prose with slots, parts/05_abstract.md; 225 words including slot text, 169 excluding (target 150-250).
- **#7 n/a**, **#8 OPEN (HIGH)** until real figures exist, **#9 OPEN (LOW)**, **#10 OPEN** (placeholders remain by design; counts in checks.json).
- **New #11 (LOW):** Edge's print header/footer is used to stamp every page "DUMMY / NOT RESULTS"; the footer also prints the local file path. The draft PDF is for internal page checks only.
- **New #12 (MED):** body = 8 pages with one branch per group (at the cap, no margin); 9 pages with all branches. The D49 validation text is not in yet, so expect to cut about half a page.

No layout here is final. Re-run: `python -I report/build/build.py --dummy-figs` (drop the flag and delete `build/trial_parts/dummy_results.md` once real figures exist).
