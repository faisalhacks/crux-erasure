"""Draft-layout builder for the Apart AI x Epistemics paper. NEVER a final layout.

Pipeline: report/parts/*.md + report/*_draft.md (explicit template order, see ORDER)
 -> branch filter -> [CITE:key] -> (Author et al., Year) from report/refs.bib
 -> pandoc HTML -> Edge headless print-to-PDF -> PyMuPDF page PNGs + checks
 -> build/out/DRAFT_layout.pdf, pg-NN.png, checks.json, DRAFT_combined.md (paste source)
Template: the official Apart template is a Google Doc (no LaTeX). This reproduces its section
order and single-column look only; fonts and margins are ASSUMED (Letter, 1 in, Arial 11 pt).

Branches: Discussion text for alternative outcomes sits between
  <!-- IF key=value --> ... <!-- ENDIF -->
Default keeps every branch. --branch key=value[,key=value] drops the other values of each key.
A one-branch-per-group length check (val=pass, a2=positive, n2=validated) is always built too,
into out/lengthcheck/, so the body page count is measured on text that could actually ship.

Usage: python -I build.py [--dummy-figs] [--branch key=value,...]
Every page carries a "DUMMY / NOT RESULTS" stamp; every dummy figure carries the same watermark.
"""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.dirname(HERE)
P = os.path.dirname(REPORT)
OUT = os.path.join(HERE, "out")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# --real: results are real (gate R5 VALIDATED_PRESENCE). No DUMMY stamp, no browser header/footer (keeps the
# internal file path out of the PDF), page numbers from a CSS @page margin box, no separate length-check build.
REAL = "--real" in sys.argv
STAMP = "" if REAL else "DUMMY / NOT RESULTS"
LENGTH_CHECK_BRANCHES = {"val": "pass", "a2": "positive", "n2": "validated"}

# Template order: Title, Abstract, 1 Intro, 2 Related Work, 3 Methods, 4 Results,
# 5 Discussion and Limitations, 6 Conclusion, Code and Data (+ Author Contributions),
# References, Appendix A (limitations + dual use), Appendix B, LLM Usage Statement.
ORDER = [
    "parts/00_front.md", "parts/05_abstract.md", "parts/10_introduction.md",
    "related_work.md", "methods_draft.md", "parts/40_results.md",
    "parts/50_discussion.md", "parts/60_conclusion.md", "parts/70_code_data.md",
    "@PAGEBREAK", "parts/90_references.md", "@PAGEBREAK",
    "limitations_dualuse_draft.md", "parts/95_appendix_b.md", "parts/80_llm_usage.md",
]
# Cited works that are deliberately NOT in refs.bib (pending verifier recheck); shown, and flagged in checks.
UNVERIFIED_CITES = {"milli2024bridging": "Milli et al., 2024"}


def free_ram_mb():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-c",
                            "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                           capture_output=True, text=True)
        return int(r.stdout.strip()) // 1024
    except Exception:
        return -1


def dummy_figs():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figdir = os.path.join(OUT, "dummy_figs")
    os.makedirs(figdir, exist_ok=True)
    for i, (w, h) in enumerate([(6.5, 2.4), (6.5, 2.6), (3.4, 2.4)], 1):
        fig, ax = plt.subplots(figsize=(w, h))
        ax.errorbar([1, 2, 3], [0.4, 0.5, 0.6], yerr=0.1, fmt="o")
        ax.set_title(f"{STAMP} - placeholder figure {i}", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
        fig.text(0.5, 0.5, STAMP, fontsize=26 if w > 4 else 15, color="red",
                 alpha=0.35, ha="center", va="center", rotation=20)
        fig.tight_layout()
        fig.savefig(os.path.join(figdir, f"dummy{i}.png"), dpi=200)
        plt.close(fig)
    return figdir


def bib_cites():
    txt = open(os.path.join(REPORT, "refs.bib"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", txt, re.S):
        key, body = m.group(1).strip(), m.group(2)
        a = re.search(r"author\s*=\s*\{(.*)\},?\s*\n", body)
        y = re.search(r"year\s*=\s*\{(\d{4})\}", body)
        if not a:
            continue
        authors = [s.strip() for s in a.group(1).split(" and ")]
        last = lambda s: re.sub(r"[{}\\'\"]", "", s.split(",")[0].strip())
        if len(authors) == 1:
            name = last(authors[0])
        elif len(authors) == 2:
            name = f"{last(authors[0])} and {last(authors[1])}"
        else:
            name = f"{last(authors[0])} et al."
        out[key] = f"{name}, {y.group(1) if y else 'n.d.'}"
    return out


def cite(md, bib, used, missing):
    # Narrative citation: "Tessler et al. [CITE:tessler2024habermas]" -> "Tessler et al. (2024)"
    def narr(m):
        name, k = m.group(1), m.group(2).strip()
        ref = bib.get(k) or UNVERIFIED_CITES.get(k)
        if ref and ref.rsplit(", ", 1)[0] == name:
            used.add(k)
            if k not in bib:
                missing.add(k)
            return f"{name} ({ref.rsplit(', ', 1)[1]})"
        return m.group(0)
    md = re.sub(r"([A-Z][A-Za-zÀ-ſ-]+(?: et al\.| and [A-Z][A-Za-z-]+)?) \[CITE:([^\];]+)\]", narr, md)

    def rep(m):
        keys = [k.strip().replace("CITE:", "") for k in m.group(1).split(";")]
        parts = []
        for k in keys:
            used.add(k)
            if k in bib:
                parts.append(bib[k])
            elif k in UNVERIFIED_CITES:
                parts.append(UNVERIFIED_CITES[k]); missing.add(k)
            else:
                parts.append(f"MISSING-REF:{k}"); missing.add(k)
        return "(" + "; ".join(parts) + ")"
    return re.sub(r"\[CITE:([^\]]+)\]", rep, md)


def filter_branches(md, keep):
    def rep(m):
        k, v, body = m.group(1), m.group(2), m.group(3)
        return body if (k not in keep or keep[k] == v) else ""
    return re.sub(r"<!-- IF (\w+)=(\w+) -->(.*?)<!-- ENDIF -->", rep, md, flags=re.S)


def assemble(keep):
    chunks, srcs = [], []
    for item in ORDER:
        if item == "@PAGEBREAK":
            chunks.append('<div class="pb"></div>')
            continue
        path = os.path.join(REPORT, item)
        srcs.append(item)
        chunks.append(open(path, encoding="utf-8").read())
    md = "\n\n".join(chunks)
    return filter_branches(md, keep), srcs


CSS = """
@page { size: Letter; margin: 1in; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.25; }
h1 { font-size: 16pt; margin: 0 0 6pt 0; } h2 { font-size: 13pt; margin: 12pt 0 4pt 0; }
h3 { font-size: 11.5pt; margin: 8pt 0 3pt 0; }
h1,h2,h3 { break-after: avoid; } p { margin: 0 0 6pt 0; } li { margin-bottom: 2pt; }
img { max-width: 100%; } figure { margin: 6pt 0; break-inside: avoid; text-align: center; }
figcaption { font-size: 9.5pt; text-align: left; } table { border-collapse: collapse; font-size: 9.5pt; margin-bottom: 8pt; }
td, th { border: 1px solid #888; padding: 2px 5px; }
.stamp { text-align: center; font-size: 9pt; font-weight: bold; color: #c00; margin-bottom: 4pt; }
.pb { break-before: page; }
"""
CSS_REAL = """
@page { @bottom-center { content: counter(page); font-family: Arial, Helvetica, sans-serif; font-size: 9pt; } }
"""


def render(md, outdir, label):
    os.makedirs(outdir, exist_ok=True)
    # Per-page stamp: Edge's default print header shows the page title on every page, so the
    # title carries the stamp (position:fixed elements were mis-placed in print). Plus one visible line on p.1.
    if not REAL:
        md = f'<div class="stamp">{STAMP} - DRAFT LAYOUT, NOT FINAL</div>\n\n' + md
    md_path = os.path.join(outdir, "DRAFT_combined_render.md")
    open(md_path, "w", encoding="utf-8").write(md)
    css = os.path.join(outdir, "style.css")
    open(css, "w", encoding="utf-8").write(CSS + (CSS_REAL if REAL else ""))
    html = os.path.join(outdir, "draft.html")
    subprocess.run(["pandoc", md_path, "-f", "markdown+smart", "-s", "-t", "html5",
                    "--embed-resources", "--resource-path",
                    P + os.pathsep + os.path.join(OUT, "dummy_figs"),
                    "-c", css, "--metadata", "title=", "-o", html,
                    "-V", f"pagetitle={label}"], check=True)
    pdf = os.path.join(outdir, "DRAFT_layout.pdf")
    hf = ["--no-pdf-header-footer", "--print-to-pdf-no-header"] if REAL else []
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", *hf,
                    f"--print-to-pdf={pdf}", "file:///" + html.replace("\\", "/")],
                   check=True, timeout=120)
    import pymupdf
    doc = pymupdf.open(pdf)
    texts = [pg.get_text() for pg in doc]
    heads = {}
    for i, t in enumerate(texts, 1):
        for key in ("Abstract", "1. Introduction", "2. Related Work", "3. Methods", "4. Results",
                    "5. Discussion and Limitations", "6. Conclusion", "Code and Data", "References",
                    "Appendix A. Limitations", "Appendix B. Supplementary", "LLM Usage Statement"):
            if re.search(r"^\s*" + re.escape(key), t, re.M):
                heads.setdefault(key, i)
    refs = heads.get("References", len(doc) + 1)
    body_pages = refs - 1
    stamp_missing = [] if REAL else [i for i, t in enumerate(texts, 1) if STAMP not in t]
    path_leak = [i for i, t in enumerate(texts, 1) if "file:///" in t or "draft.html" in t]
    for f in glob.glob(os.path.join(outdir, "pg-*.png")):
        os.remove(f)
    for i, pg in enumerate(doc, 1):
        pg.get_pixmap(dpi=80).save(os.path.join(outdir, f"pg-{i:02d}.png"))
    imgs = []
    for i, pg in enumerate(doc, 1):
        for im in pg.get_image_info():
            b = im["bbox"]
            imgs.append({"page": i, "w_in": round((b[2] - b[0]) / 72, 2), "h_in": round((b[3] - b[1]) / 72, 2)})
    return {"pdf": pdf, "pages_total": len(doc), "body_pages_before_references": body_pages,
            "body_cap": 8, "body_within_cap": body_pages <= 8, "heading_first_page": heads,
            "pages_missing_stamp": stamp_missing, "pages_with_file_path": path_leak, "images": imgs,
            "fonts": sorted({f[3] for pg in doc for f in pg.get_fonts()})}


def abstract_words():
    t = open(os.path.join(REPORT, "parts", "05_abstract.md"), encoding="utf-8").read()
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S).replace("## Abstract", "")
    all_words = len(t.split())
    no_slots = len(re.sub(r"\[[A-Z-]+ SLOT:[^\]]*\]", "", t).split())
    return {"incl_slot_text": all_words, "excl_slot_text": no_slots, "target": "150-250"}


def slot_counts(md):
    vis = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    pats = {"RESULT SLOT": r"\[RESULT SLOT", "LABEL-DESIGN SLOT": r"\[LABEL-DESIGN SLOT",
            "HUMAN SLOT": r"\[HUMAN SLOT", "VERIFY": r"\[VERIFY", "[IF": r"\[IF ",
            "FROZEN": r"\[FROZEN", "TODO": r"TODO", "SLOT (any)": r"SLOT"}
    return {k: len(re.findall(rx, vis)) for k, rx in pats.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    ram = free_ram_mb()
    print("free RAM MB:", ram)
    if 0 <= ram < 1500:
        sys.exit("free RAM < 1.5 GB; not building")
    if "--dummy-figs" in sys.argv:
        dummy_figs()
    keep = {}
    if "--branch" in sys.argv:
        for kv in sys.argv[sys.argv.index("--branch") + 1].split(","):
            k, v = kv.split("="); keep[k] = v
    bib = bib_cites()
    md, srcs = assemble(keep)
    used, missing = set(), set()
    md_c = cite(md, bib, used, missing)
    open(os.path.join(OUT, "DRAFT_combined.md"), "w", encoding="utf-8").write(md_c)
    refs_txt = open(os.path.join(REPORT, "parts", "90_references.md"), encoding="utf-8").read()
    full = render(md_c, OUT, "Draft layout" if REAL else f"{STAMP} - DRAFT LAYOUT")
    if REAL:
        lc = {"skipped": "--real: the parts keep one branch only, so the main build is the length check"}
    else:
        md1, _ = assemble(LENGTH_CHECK_BRANCHES)
        lc = render(cite(md1, bib, set(), set()), os.path.join(OUT, "lengthcheck"), f"{STAMP} - LENGTH CHECK")
    res = {"label": ("DRAFT LAYOUT - real results (gate R5 VALIDATED_PRESENCE) - not final" if REAL
                     else "DRAFT LAYOUT - DUMMY / NOT RESULTS - not final"), "sources_in_order": srcs,
           "branches_kept": keep or "all", "all_branches": full,
           "length_check_one_branch_per_group": dict(lc, branches=LENGTH_CHECK_BRANCHES),
           "abstract_words": abstract_words(), "slot_counts_visible_text": slot_counts(md_c),
           "cited_keys": sorted(used), "cited_not_in_refs_bib": sorted(missing),
           "refs_bib_keys_cited_but_absent_from_reference_list": sorted(
               k for k in used if k in bib and bib[k].split(",")[0].split(" ")[0] not in refs_txt),
           "free_ram_mb": ram}
    json.dump(res, open(os.path.join(OUT, "checks.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
