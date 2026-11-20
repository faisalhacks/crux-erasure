"""Make figures 1-6 from result JSONs (no hard-coded numbers; pipeline schematic has no numbers).
Usage: python -I make_figures.py [--in DIR] [--out DIR]   (default: dummy/ -> dummy_out/)
Any input with kind in {dummy, synthetic, shuffled} is watermarked and file names get the DUMMY_ prefix.
Missing optional inputs (a3, n3, n4, a4) are shown as 'not available' rather than invented.
Caption text goes to captions.md (takeaway first sentence); sidecar JSON per figure holds inputs+sha256."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OI = dict(black="#000000", orange="#E69F00", sky="#56B4E9", green="#009E73", blue="#0072B2",
          verm="#D55E00", pink="#CC79A7")
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8, "xtick.labelsize": 8,
                     "ytick.labelsize": 8, "legend.fontsize": 8, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})
W = 3.3  # single column inches

ap = argparse.ArgumentParser()
HERE = Path(__file__).resolve().parent
ap.add_argument("--in", dest="indir", default=str(HERE / "dummy"))
ap.add_argument("--out", default=str(HERE / "dummy_out"))
a = ap.parse_args()
IN, OUT = Path(a.indir), Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
used = {}
captions = []


def load(name, required=True):
    p = IN / name
    if not p.exists():
        if required:
            raise SystemExit(f"missing {p}")
        return None
    used[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text(encoding="utf-8"))


def is_dummy(*ds):
    return any(d and d.get("kind") in ("dummy", "synthetic", "shuffled") for d in ds)


def finish(fig, stem, dummy, caption):
    if dummy:
        fig.text(0.5, 0.5, "DUMMY DATA", fontsize=26, color="red", alpha=0.22, ha="center", va="center",
                 rotation=30, weight="bold", zorder=100)
        stem = "DUMMY_" + stem
        caption = "[DUMMY DATA - placeholder numbers, not results] " + caption
    for ext, kw in (("pdf", {}), ("png", {"dpi": 220})):
        fig.savefig(OUT / f"{stem}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)
    captions.append(f"**{stem}**: {caption}\n")
    (OUT / f"{stem}.json").write_text(json.dumps({"script": "figures/make_figures.py", "inputs_sha256": dict(used),
                                                  "dummy": dummy}, indent=1), encoding="utf-8")


def forest(ax, rows, xlabel, ref=0.0, reflabel=None):
    """rows: (label, est, lo, hi, color, marker) or None for gap. Draws top to bottom."""
    n = len(rows)
    ys = []
    for i, r in enumerate(rows):
        y = n - 1 - i
        if r is None:
            continue
        lab, e, lo, hi, c, m = r
        ax.errorbar(e, y, xerr=[[e - lo], [hi - e]], fmt=m, color=c, capsize=2.5, ms=5, lw=1.4)
        ys.append((y, lab))
    ax.axvline(ref, color="grey", ls="--", lw=1)
    ax.set_yticks([y for y, _ in ys])
    ax.set_yticklabels([l for _, l in ys])
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel(xlabel)


# ---------- Fig 1: gate 1
g = load("gate1.json")
k, b = g["kappa"], g["balanced_accuracy"]
fig, axs = plt.subplots(1, 2, figsize=(W, 2.4), gridspec_kw={"width_ratios": [1, 1]})
ax = axs[0]
ax.bar([0], [k["primary"]], color=OI["sky"], edgecolor="k", width=0.5)
lo, hi = k["primary_ci_info_only"]
ax.errorbar([0], [k["primary"]], yerr=[[k["primary"] - lo], [hi - k["primary"]]], color="k", capsize=3)
ax.axhline(k["cutoff"], color=OI["verm"], ls="--"); ax.text(0.58, k["cutoff"] + 0.02, "0.60 cut-off", color=OI["verm"], ha="right", fontsize=7, bbox=dict(fc="white", ec="none", pad=1))
ax.set_xticks([0]); ax.set_xticklabels([f"kappa\n(n={k['n_shared']} shared)"]); ax.set_ylim(0, 1); ax.set_ylabel("Cohen's kappa")
ax.set_xlim(-0.6, 0.6)
ax = axs[1]
ax.bar([0], [b["ba"]], color=OI["green"], edgecolor="k", width=0.5)
ax.errorbar([0], [b["ba"]], yerr=[[b["ba"] - b["lo"]], [b["hi"] - b["ba"]]], color="k", capsize=3)
ax.axhline(0.5, color=OI["verm"], ls="--"); ax.text(0.58, 0.52, "chance 0.5", color=OI["verm"], ha="right", fontsize=7, bbox=dict(fc="white", ec="none", pad=1))
ax.set_xticks([0]); ax.set_xticklabels([f"balanced acc.\n(n={b['n_used']})"]); ax.set_ylim(0, 1); ax.set_ylabel("Balanced accuracy")
ax.set_xlim(-0.6, 0.6)
fig.suptitle(f"Gate 1: {g['verdict']}   unsure excluded: {b['n_unsure_excluded']} "
             f"(L1 {k['unsure_L1']}, L2 {k['unsure_L2']} on shared)", fontsize=7.5, y=1.0)
fig.tight_layout()
finish(fig, "fig1_gate1", is_dummy(g),
       f"Gate 1 verdict: {g['verdict']} - kappa {k['primary']:.2f} on the {k['n_shared']} shared items "
       f"(cut-off {k['cutoff']}; CI informational) and balanced accuracy {b['ba']:.2f} (bootstrap 95% CI "
       f"{b['lo']:.2f}-{b['hi']:.2f}; pass needs lower bound > 0.5) for AI scorer vs adjudicated labels, "
       f"n={b['n_used']} after excluding {b['n_unsure_excluded']} unsure items. Seed per analysis/gate1.py run log.")

# ---------- Fig 2: A2 forest
a2 = load("a2.json")
c = a2["controlled"]
rows = [("Erasure (controlled)", c["erasure"]["est"], c["erasure"]["lo"], c["erasure"]["hi"], OI["blue"], "o"),
        ("Length (control)", c["length"]["est"], c["length"]["lo"], c["length"]["hi"], OI["orange"], "s"),
        ("Clarity (control)", c["clarity"]["est"], c["clarity"]["lo"], c["clarity"]["hi"], OI["green"], "^"),
        None,
        ("Erasure (no controls)", a2["uncontrolled"]["erasure"]["est"], a2["uncontrolled"]["erasure"]["lo"],
         a2["uncontrolled"]["erasure"]["hi"], OI["pink"], "D")]
fig, ax = plt.subplots(figsize=(W, 2.2))
forest(ax, rows, "Effect on within-round rank\n(conditional-logit coef. per SD, 95% CI)")
fig.tight_layout()
finish(fig, "fig2_a2_forest", is_dummy(a2),
       f"A2: erasure coefficient {c['erasure']['est']:.2f} (95% CI {c['erasure']['lo']:.2f} to {c['erasure']['hi']:.2f}) "
       f"after controlling for length and clarity; a CI crossing 0 means no detectable effect. Pairs within round, "
       f"predictors z-scored, {a2['n_clusters']} clusters, bootstrap B={a2['B']} resampling by group, seed {a2['seed']}.")

# ---------- Fig 3: N1
n1 = load("n1.json")
e = n1["erasure"]
rows = [("Erasure", e["est"], e["lo"], e["hi"], OI["blue"], "o"), ("Length", n1["length"]["est"], n1["length"]["lo"], n1["length"]["hi"], OI["orange"], "s"),
        ("Clarity", n1["clarity"]["est"], n1["clarity"]["lo"], n1["clarity"]["hi"], OI["green"], "^")]
fig, ax = plt.subplots(figsize=(W, 1.8))
forest(ax, rows, "Winner minus round average\n(paired difference, 95% CI)")
fig.tight_layout()
finish(fig, "fig3_n1_winner", is_dummy(n1),
       f"N1: the winning statement's erasure score exceeds its round's average by {e['est']:.2f} "
       f"(95% CI {e['lo']:.2f} to {e['hi']:.2f}); length and clarity differences shown for comparison. Paired within round, "
       f"{n1['n_clusters']} clusters, group bootstrap B={n1['B']}, seed {n1['seed']}.")

# ---------- Fig 4: tier-2 panel
a4, a3, n3, n4 = load("a4.json", False), load("a3.json", False), load("n3.json", False), load("n4.json", False)
rows = [("A2 primary scorer", c["erasure"]["est"], c["erasure"]["lo"], c["erasure"]["hi"], OI["blue"], "o")]
na = []
if a4:
    r = a4["controlled"]["erasure"]; rows.append(("A4 second scorer", r["est"], r["lo"], r["hi"], OI["orange"], "s"))
else: na.append("A4")
if a3:
    r = a3["erasure"]; rows.append(("A3 AI vs human-written", r["est"], r["lo"], r["hi"], OI["green"], "^"))
else: na.append("A3")
if n3:
    r = n3["erasure"]; rows.append(("N3 draft vs revised", r["est"], r["lo"], r["hi"], OI["pink"], "D"))
else: na.append("N3")
if n4:
    for key, lab, col, m in (("minority", "N4 minority raters", OI["verm"], "v"), ("majority", "N4 majority raters", OI["sky"], "P")):
        r = n4[key]; rows.append((lab, r["est"], r["lo"], r["hi"], col, m))
else: na.append("N4")
fig, ax = plt.subplots(figsize=(W, 0.45 * len(rows) + 1.0))
forest(ax, rows, "Erasure coef. (95% CI)")
if na:
    ax.text(0.02, 0.02, "not available: " + ", ".join(na), transform=ax.transAxes, fontsize=7)
fig.tight_layout()
finish(fig, "fig4_tier2_forest", is_dummy(a2, a4, a3, n3, n4),
       "Tier 2: every Tier-2 check is shown on the same scale as A2, so agreement or disagreement with the primary estimate "
       "is visible at a glance; intervals crossing 0 are not detectable effects. Rows: second scorer (A4), AI- vs human-written (A3), "
       "first draft vs revised (N3), minority- vs majority-side raters (N4). Clusters per row are in each result JSON; "
       f"group-clustered bootstrap 95% CI. Missing rows: {', '.join(na) or 'none'}. All Tier-2 analyses are labelled exploratory unless frozen.")

# ---------- Fig 5: N2 grid
n2 = load("n2.json")
sysk, usrk = ["keep_all_satisfied", "accurate_differences"], ["common_ground", "show_disagreement"]
sysl, usrl = ["System: keep\neveryone satisfied", "System: be accurate\nabout differences"], ["User: common\nground", "User: show\ndisagreement"]
fig, axs = plt.subplots(1, 2, figsize=(W, 2.7), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.7})
ax = axs[0]
M = [[n2["cells"][f"{s}|{u}"]["mean"] for u in usrk] for s in sysk]
im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1)
for i, s in enumerate(sysk):
    for j, u in enumerate(usrk):
        cl = n2["cells"][f"{s}|{u}"]
        ax.text(j, i, f"{cl['mean']:.2f}\n[{cl['lo']:.2f},\n{cl['hi']:.2f}]", ha="center", va="center", fontsize=7,
                color="white" if cl["mean"] < 0.6 else "black")
ax.set_xticks([0, 1]); ax.set_xticklabels(["common\nground", "show\ndisagr."]); ax.set_yticks([0, 1]); ax.set_yticklabels(["keep all\nsatisfied", "accurate\nabout diffs"])
ax.set_xlabel("User prompt"); ax.set_ylabel("System prompt")
ax = axs[1]
for i, (s, lab, col, m) in enumerate(zip(sysk, ["System: keep satisfied", "System: accurate"], [OI["verm"], OI["blue"]], ["o", "s"])):
    ms = [n2["cells"][f"{s}|{u}"] for u in usrk]
    ax.errorbar([0.05 * (i - 0.5) + j for j in (0, 1)], [x["mean"] for x in ms],
                yerr=[[x["mean"] - x["lo"] for x in ms], [x["hi"] - x["mean"] for x in ms]], color=col, marker=m, capsize=2.5, label=lab)
ax.set_xticks([0, 1]); ax.set_xticklabels(["common\nground", "show\ndisagr."]); ax.set_xlim(-0.3, 1.3)
ax.set_ylim(0, 1.0); ax.set_ylabel("Mean erasure score"); ax.set_xlabel("User prompt"); ax.legend(frameon=False, loc="lower left", fontsize=6.5)
fig.tight_layout()
finish(fig, "fig5_n2_grid", is_dummy(n2),
       "N2: the 2x2 grid shows how much each prompt factor changes the erasure of generated statements; non-parallel lines in the right "
       f"panel would indicate an interaction. Cell = {n2['measure']} with 95% CI (group bootstrap); clusters per cell "
       f"{', '.join(str(v['n_clusters']) for v in n2['cells'].values())}. Exploratory (Tier 3).")

# ---------- Fig 6: schematic (no data)
steps = [("1  Opinions", "participants' views per round"), ("2  Candidates", "AI + human statements per round"),
         ("3  Rankings", "each rater ranks candidates"), ("4  Erasure score", "AI scorer: does it hide disagreement?\n(gate 1: blind human labels)"),
         ("5  Within-round test", "rank vs erasure, controls: length, clarity"),
         ("6  Group bootstrap", "resample groups, 95% CI"), ("7  Tier 2/3 checks", "N1, A3, A4, N3, N4, N2")]
fig, ax = plt.subplots(figsize=(W, 5.0))
ax.set_xlim(0, 1); ax.set_ylim(0, len(steps)); ax.axis("off")
cols = [OI["sky"], OI["sky"], OI["sky"], OI["orange"], OI["green"], OI["green"], OI["pink"]]
for i, (t, d) in enumerate(steps):
    y = len(steps) - 1 - i
    ax.add_patch(FancyBboxPatch((0.03, y + 0.1), 0.94, 0.72, boxstyle="round,pad=0.01", fc=cols[i], ec="k", alpha=0.55))
    ax.text(0.06, y + 0.66, t, fontsize=8, weight="bold", va="center")
    ax.text(0.06, y + 0.34, d, fontsize=6.5, va="center")
    if i < len(steps) - 1:
        ax.annotate("", xy=(0.5, y - 0.02), xytext=(0.5, y + 0.1), arrowprops=dict(arrowstyle="->", lw=1.2))
fig.tight_layout()
finish(fig, "fig6_pipeline", False,
       "Pipeline: statements are scored for hiding disagreement by an AI scorer validated against blind human labels (gate 1), "
       "then tested against what raters actually ranked, within each round, with length and clarity controlled. Colour groups: data (blue), "
       "scorer (orange), primary test (green), follow-ups (pink). Schematic only, no data.")

(OUT / "captions.md").write_text("# Figure captions (generated by make_figures.py)\n\n" + "\n".join(captions), encoding="utf-8")
print("wrote", len(captions), "figures to", OUT)
