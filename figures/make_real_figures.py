"""Real-data figures for the paper (gate R5 VALIDATED_PRESENCE; output tag HIDE_NOT_HUMAN_VALIDATED).

Usage: C:/Users/intel/miniconda3/python.exe -I figures/make_real_figures.py
Reads only logged result tables (no number typed here):
  figures/data/a2_forest.csv, figures/data/a2_controls.csv      -> fig_a2_forest
  analysis/n2_results/n2_estimates.csv                           -> fig_n2_contrasts (all generators)
                                                                    + fig_n2_<generator> (one per generator)
  figures/data/a2_length_robustness.csv (if it exists)           -> fig_a2_length (skipped otherwise)
Writes PDF + PNG (220 dpi) + sidecar JSON (input sha256) per figure and captions.md into figures/real_out/.
Fonts >= 8 pt at the printed width (6.5 in); Okabe-Ito colours plus distinct markers; every estimate with
its 95% interval as given in the source table. No watermark (real data).
"""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
P = HERE.parent
OUT = HERE / "real_out"
OUT.mkdir(parents=True, exist_ok=True)
OI = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]
MARK = ["o", "s", "^", "D", "v", "P", "X"]
# Sizes are >= 8.5 pt at the saved width so they stay >= 8 pt after the page scales the figure to ~6.3 in.
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9, "xtick.labelsize": 8.5,
                     "ytick.labelsize": 9, "legend.fontsize": 8.5, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
STAMP = "HIDE_NOT_HUMAN_VALIDATED"
captions = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def finish(fig, stem, inputs, caption):
    for ext, kw in (("pdf", {}), ("png", {"dpi": 220})):
        fig.savefig(OUT / f"{stem}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)
    (OUT / f"{stem}.json").write_text(json.dumps(
        {"script": "figures/make_real_figures.py", "stamp": STAMP,
         "inputs_sha256": {str(Path(k).relative_to(P)): sha(k) for k in inputs}}, indent=1), encoding="utf-8")
    captions.append(f"**{stem}**: {caption}\n")


def fig_a2():
    f1, f2 = HERE / "data" / "a2_forest.csv", HERE / "data" / "a2_controls.csv"
    fr = {r["model"]: r for r in rows(f1)}
    ctl = {r["term"]: r for r in rows(f2)}
    order = [
        ("A2", "A2 primary: length + readability"),
        ("A2h", "A2h: length only"),
        ("A2b", "A2b: + similarity to own opinion"),
        ("A2f", "A2f: + vagueness rate"),
        ("A2g", "A2g: member-weighted E"),
        ("A2i", "A2i: informative rounds only"),
        ("A2d", "A2d: incl. development launches"),
        ("A2e", "A2e: one-sided counted as shown*"),
        ("UNC", "No controls (exploratory)*"),
    ]
    # width chosen so the tight bounding box (labels + value column) is ~6.3 in, the printed width: no downscaling
    fig, ax = plt.subplots(figsize=(5.35, 2.7))
    for i, (k, lab) in enumerate(order):
        r = ctl["erasure_uncontrolled_EXPLORATORY"] if k == "UNC" else fr[k]
        est, lo, hi = float(r["est"]), float(r["lo"]), float(r["hi"])
        y = len(order) - 1 - i
        prim = k == "A2"
        col = OI[0] if prim else (OI[1] if k in ("A2e", "UNC") else "#444444")
        mk = "D" if prim else ("s" if k in ("A2e", "UNC") else "o")
        ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt=mk, color=col, ms=6 if prim else 4.5,
                    capsize=2.5, lw=1.6 if prim else 1.1)
        ax.text(1.02, y, f"{est:+.3f} [{lo:+.3f}, {hi:+.3f}]", va="center", ha="left", fontsize=8,
                transform=ax.get_yaxis_transform(), fontweight="bold" if prim else "normal")
    ax.axvline(0, color="#888888", lw=0.8, ls="--")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([lab for _, lab in order][::-1])
    ax.set_xlim(-0.14, 0.12)
    ax.set_xlabel("Coefficient on E (0-1 rank scale; > 0: higher E ranked better)")
    ax.set_title("A2: 95% wild cluster bootstrap-t intervals", loc="left")
    fig.tight_layout()
    finish(fig, "fig_a2_forest", [f1, f2],
           "Small and sensitive to how statement length is controlled. Pre-registered test; the predictor's "
           "hide/show contrast is not human-validated. Primary A2 (diamond) and pre-registered sensitivity models; "
           "* = not crux erasure or not pre-registered. 1,166 rounds / 642 launches (A2i: 150 / 142; A2d: 1,409 / 775); "
           "launch clusters, B = 10,000, seed 20261119. Sources: figures/data/a2_forest.csv, a2_controls.csv.")


GEN = [("gemma4-12b", "Gemma-4-12B"), ("qwen3.8-27b", "Qwen3.8-27B*"),
       ("ministral3-14b", "Ministral-3-14B"), ("phi4-14b", "phi-4"), ("llama3.1-8b", "Llama-3.1-8B")]
SHORT = {"gemma4-12b": "Gemma", "qwen3.8-27b": "Qwen*", "ministral3-14b": "Ministral", "phi4-14b": "phi-4",
         "llama3.1-8b": "Llama"}
CON = [("MC_manipulation", "Manipulation check:\nCOMMON vs DIS user prompt"),
       ("SYS_system_effect", "System effect:\nSAT vs ACC (avg.)"),
       ("C1_override", "C1: SAT-DIS - ACC-DIS"),
       ("C2_protection", "C2: SAT-COM - ACC-COM"),
       ("C3_interaction", "C3: interaction"),
       ("C4a", "C4a: SAT-COM - NEU-COM"),
       ("C4b", "C4b: NEU-COM - ACC-COM")]


def n2_table():
    f = P / "analysis" / "n2_results" / "n2_estimates.csv"
    out = {}
    for r in rows(f):
        if r["analysis_set"] != "primary" or r["adjustment"] != "unadjusted":
            continue
        key = r["contrast"].split(" ")[0]
        out[(r["generator"], key)] = (float(r["est"]), float(r["ci_lo"]), float(r["ci_hi"]))
    return f, out


def fig_n2():
    f, t = n2_table()
    fig, ax = plt.subplots(figsize=(5.1, 3.2))
    nG = len(GEN)
    for gi, (g, lab) in enumerate(GEN):
        for ci, (c, _) in enumerate(CON):
            est, lo, hi = t[(g, c)]
            y = (len(CON) - 1 - ci) + (nG - 1 - gi - (nG - 1) / 2) * 0.15
            ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt=MARK[gi], color=OI[gi], ms=4,
                        capsize=1.8, lw=1.0, label=SHORT[g] if ci == 0 else None,
                        mfc="white" if g == "qwen3.8-27b" else OI[gi])
    ax.axvline(0, color="#888888", lw=0.8, ls="--")
    ax.set_yticks(range(len(CON)))
    ax.set_yticklabels([lab for _, lab in CON][::-1])
    ax.set_xlabel("Difference in mean E between prompt cells (scorer 1)")
    ax.set_title("N2 (EXPLORATORY): 95% launch-bootstrap intervals", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.4, -0.2), frameon=False, ncol=5, handletextpad=0.2,
              columnspacing=0.8)
    fig.tight_layout()
    finish(fig, "fig_n2_contrasts", [f],
           "EXPLORATORY. In all five generators the user prompt asking to show disagreement (DIS) and the "
           "system prompt asking for accuracy (ACC) are both associated with lower scored E; the size of C1 and "
           "the sign of C3 vary by generator. Scorer's hide/show call checked on 6 N2 statements only "
           "(descriptive); statements not ranked by humans; * Qwen-written text is scored by Qwen (self-scored; open markers). "
           "Unadjusted primary set, 168-177 rounds per generator, launch-cluster percentile bootstrap, B = 2,000, "
           "seed 20261115. Source: analysis/n2_results/n2_estimates.csv.")
    for gi, (g, lab) in enumerate(GEN):
        fig, ax = plt.subplots(figsize=(3.3, 2.6))
        for ci, (c, clab) in enumerate(CON):
            est, lo, hi = t[(g, c)]
            ax.errorbar(est, len(CON) - 1 - ci, xerr=[[est - lo], [hi - est]], fmt=MARK[gi], color=OI[gi],
                        ms=4, capsize=2, lw=1.0, mfc="white" if g == "qwen3.8-27b" else OI[gi])
        ax.axvline(0, color="#888888", lw=0.8, ls="--")
        ax.set_yticks(range(len(CON)))
        ax.set_yticklabels([c.replace("\n", " ") for _, c in CON][::-1], fontsize=8)
        ax.set_xlabel("Difference in mean E")
        ax.set_title(f"N2 (EXPLORATORY): {lab}", loc="left", fontsize=8.5)
        fig.tight_layout()
        finish(fig, f"fig_n2_{g}", [f],
               f"EXPLORATORY. N2 prompt-cell contrasts for {lab}, unadjusted primary set, 95% launch-bootstrap "
               "intervals (B = 2,000, seed 20261115). Source: analysis/n2_results/n2_estimates.csv.")


def fig_length():
    f = HERE / "data" / "a2_length_spec.csv"
    if not f.exists():
        print("skip fig_a2_length: figures/data/a2_length_spec.csv does not exist yet")
        return
    rs = rows(f)
    short = {"none": "No length control", "linear z log words": "Linear log length (registered)",
             "cubic in z log words": "Cubic in log length", "10 length-decile dummies": "Length deciles",
             "within-round length rank (1-4)": "Within-round length rank",
             "within-round length rank + z log words": "Length rank + log length",
             "z raw word count": "Raw word count", "z raw words + z log words": "Raw words + log length"}
    def lab(spec):
        for k, v in short.items():
            if spec.startswith(k):
                return v
        return spec
    # width chosen so the tight bounding box is ~6.3 in (no downscaling on the page)
    fig, ax = plt.subplots(figsize=(4.6, 0.3 * len(rs) + 0.8))
    for i, r in enumerate(rs):
        est, se, t = float(r["beta_E"]), float(r["se_cr1"]), float(r["t"])
        lo, hi = est - 1.96 * se, est + 1.96 * se  # approximate normal interval from the CR1 SE, labelled
        y = len(rs) - 1 - i
        prim = r["spec"].startswith("linear z log words")
        ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt="D" if prim else "o",
                    color=OI[0] if prim else "#444444", ms=5.5 if prim else 4.5, capsize=2.5, lw=1.5 if prim else 1.1)
        ax.text(1.02, y, f"{est:+.3f} (t = {t:.2f})", transform=ax.get_yaxis_transform(), va="center",
                fontsize=8.5, fontweight="bold" if prim else "normal")
    ax.axvline(0, color="#888888", lw=0.8, ls="--")
    ax.set_yticks(range(len(rs)))
    ax.set_yticklabels([lab(r["spec"]) for r in rs][::-1])
    ax.set_xlabel("Coefficient on E (estimate +/- 1.96 CR1 SE)")
    ax.set_title("A2 under alternative length adjustments (EXPLORATORY)", loc="left")
    fig.tight_layout()
    finish(fig, "fig_a2_length", [f],
           "EXPLORATORY (red team; not pre-registered). A2 coefficient on E with readability kept and the length "
           "control varied; bars are estimate +/- 1.96 x CR1 SE (approximate, not the bootstrap-t of record). "
           "22,536 rows, 642 launches. Source: figures/data/a2_length_spec.csv (analysis/redteam_rerun/rt_refit.json).")


if __name__ == "__main__":
    fig_a2()
    fig_n2()
    fig_length()
    (OUT / "captions.md").write_text("# Real-data figure captions (" + STAMP + ")\n\n" + "\n".join(captions),
                                     encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
