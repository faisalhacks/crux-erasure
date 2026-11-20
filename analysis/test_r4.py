"""Tests for the [R4] implementation (see analysis/eval/R4_IMPLEMENTATION.md).  DUMMY / SYNTHETIC / SHUFFLED data only:
no label file, no real ranking, nothing in P/labels is read or written.  Each run writes into its own fresh directory.
  (A) gate1 [R4]: both labeler designs, missing / late pass 2, volunteer present / absent / late / incomplete, DESIGN.json
      write-once, first-pass tamper, N2 check, LLM annotator, wording, never writes into labels/.
  (B) analysis-set default: the development launches are excluded from A2, N1, N4, A3, the informativeness tier."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import gate1 as G1  # noqa: E402
import make_dummy_labels as MD  # noqa: E402
import a2_within_round as A2  # noqa: E402
import a2_informativeness as INF  # noqa: E402
import n1_winner_vs_mean as N1  # noqa: E402
import n4_minority as N4  # noqa: E402
import a3_ai_vs_human as A3  # noqa: E402

R = C.A / "testout" / "runs" / ("r4_" + C.utc_stamp())
R.mkdir(parents=True)
ok = True


def chk(n, c, d=""):
    global ok
    ok &= bool(c)
    print(("PASS " if c else "FAIL ") + n + " :: " + str(d), flush=True)


def exits(fn, *a, **k):
    try:
        fn(*a, **k)
    except SystemExit as e:
        return True, str(e)
    return False, ""


def cp(name, **kw):
    src = MD.build(name, **kw)
    dst = R / src.name
    shutil.copytree(src, dst)          # copy2: modification times are preserved (the one-hour rule reads them)
    return dst


def A(root, step, *extra):
    return ["--step", step, "--kind", "dummy", "--labels-dir", str(root / "labels"), "--gate-dir", str(root / "gate"), *extra]


def run(root, step, *extra):
    return G1.main(A(root, step, *extra))


def snap(root):
    return {p.name: C.sha256_file(p) for p in sorted((root / "labels").iterdir())}


def gate_files(root, stem="gate1_computed__"):
    return sorted(f for f in (root / "gate").glob(stem + "*.json"))


# =============================================================== (A) gate1 [R4]
snaps = {}
# ---- A1 single-labeler, full B = 10,000: PROVISIONAL -> kappa -> PASS
sg = cp("single_good", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7)
snaps["sg"] = snap(sg)
chk("fixture: single design has no volunteer file", not (sg / "labels" / "volunteer_pass1.csv").exists(), "volunteer file absent")
v0 = run(sg, "validity")
D = json.loads((sg / "gate" / "DESIGN.json").read_text(encoding="utf-8"))
chk("DESIGN.json = single_labeler (volunteer file absent), write-once with sidecar",
    D["design"] == "single_labeler" and (sg / "gate" / "DESIGN.json.sha256").exists() and "author_pass1.csv" in D["files_in_labels_dir"]
    and all("sha256" in x and "mtime_utc" in x for x in D["files_in_labels_dir"].values()), D["design"])
chk("single: validity before kappa -> PROVISIONAL_PASS (BA lower bound > 0.5, kappa not recorded)",
    v0["status"] == "PROVISIONAL_PASS" and not v0["kappa_recorded"], f"{v0['status']} BA={v0['balanced_accuracy']['ba']:.3f} lo={v0['balanced_accuracy']['lo']:.3f}")
chk("single: BA is against the author's FIRST-PASS labels on the originals only (38 minus UNSURE)",
    v0["balanced_accuracy"]["against"].startswith("author pass-1") and v0["balanced_accuracy"]["n_used"] <= 38, str(v0["balanced_accuracy"]["n_used"]))
chk("single: headline carries the PROVISIONAL stamp and the single-annotator wording",
    v0["headline"]["state_stamp"] == "PROVISIONAL" and v0["headline"]["annotator_wording"] == "validated against a single hypothesis-aware human annotator", v0["headline"]["state_stamp"])
h = v0["headline"]
nd = h["n_definite"]
chk("headline: H = HIDES / definite with Wilson CI, UNSURE bounds, conditional rate",
    abs(h["H"] - h["n_hides"] / nd) < 1e-12 and h["H_wilson95"][0] <= h["H"] <= h["H_wilson95"][1] and len(h["bounds_unsure_as_not_hiding_and_as_hiding"]) == 2
    and "conditional_H_among_hides_or_shows" in h, f"H={h['H']:.3f} n={nd} CI={h['H_wilson95']}")
k = run(sg, "kappa")
kj = k["kappa"]
chk("single: kappa step = self-consistency on the 20 repeats, cut 0.60, CI + AC1 + CI, KAPPA.json write-once",
    k["status"] == "COMPUTED" and kj["n_repeats"] == 20 and kj["cut"] == 0.60 and len(kj["kappa_ci95"]) == 2 and not np.isnan(kj["ac1"])
    and len(kj["ac1_ci95"]) == 2 and kj["B"] == 10000 and kj["seed"] == 20261116 and (sg / "gate" / "KAPPA.json.sha256").exists(),
    f"kappa={kj['kappa']:.3f} CI={[round(x, 2) for x in kj['kappa_ci95']]} AC1={kj['ac1']:.3f} pass={kj['pass']}")
chk("single: kappa split by kind (15 originals, 5 N2) and 4x4 table reported",
    kj["by_kind_original"]["n"] == 15 and kj["by_kind_n2"]["n"] == 5 and sum(sum(r.values()) for r in kj["table_4x4"].values()) == 20, "ok")
chk("single: pass-2 one-hour rule recorded (both times) and provisional-output flag stored",
    k["pass2_rule"]["ok"] and "pass2_mtime_utc" in k["pass2_rule"] and "pass2_started_utc" in k["pass2_rule"]
    and k["provisional_real_rank_output_existed_when_pass2_arrived"] in (True, False), str(k["pass2_rule"]["pass1_mtime_source"]))
e, msg = exits(run, sg, "kappa")
chk("single: second kappa run refused (write-once)", e and "write-once" in msg, msg[:60])
v1 = run(sg, "validity")
chk("single: validity after kappa >= 0.60 -> PASS; PROVISIONAL record kept (two gate1_computed files)",
    v1["status"] == ("PASS" if kj["pass"] else "FAIL") and len(gate_files(sg)) == 2, f"{v1['status']} files={len(gate_files(sg))}")
chk("single: ADJ.csv not required and not read in single design", v1["status"] != "INCOMPLETE" and not (sg / "labels" / "ADJ.csv").exists(), "ok")
fh = G1.WORDING
chk("validation wording strings are the binding R4 text",
    fh["single_labeler"] == "validated against a single hypothesis-aware human annotator" and "hypothesis-blind volunteer" in fh["two_human"]
    and "adjudicated by the two together without sight of scores, rankings, model or condition" in fh["two_human"], "ok")
G1.B = 1000    # speed only: the logic is the same; the full B = 10,000 ran above
sv2 = sg / "gate"

# ---- A2 single: pass 2 missing / late
sm = cp("single_nop2", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7, with_pass2=False)
km = run(sm, "kappa")
chk("single: pass 2 missing -> WAITING_PASS2, KAPPA.json NOT written, reason given",
    km["status"] == "WAITING_PASS2" and not (sm / "gate" / "KAPPA.json").exists() and "missing" in km["reason"], km["reason"][:60])
vm = run(sm, "validity")
chk("single: pass 2 missing -> gate stays PROVISIONAL_PASS ('self-consistency not yet checked', not a pass)",
    vm["status"] == "PROVISIONAL_PASS" and not vm["kappa_recorded"], vm["status"])
sl = cp("single_late", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7, pass2_start_gap_min=30, pass2_mtime_gap_min=150)
kl = run(sl, "kappa")
chk("single: pass_started_utc < 60 min after pass 1 -> kappa NOT computed", kl["status"] == "WAITING_PASS2" and "pass_started_utc" in kl["reason"] and not (sl / "gate" / "KAPPA.json").exists(), kl["reason"][:80])
sl2 = cp("single_late2", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.95, seed=7, pass2_start_gap_min=120, pass2_mtime_gap_min=20)
kl2 = run(sl2, "kappa")
chk("single: file mtime < 60 min after pass 1 -> kappa NOT computed", kl2["status"] == "WAITING_PASS2" and "mtime" in kl2["reason"], kl2["reason"][:80])
shutil.copy2(sg / "labels" / "author_pass2.csv", sl / "labels" / "author_pass2.csv")   # a replacement pass-2 file that meets the rule
kl3 = run(sl, "kappa")
seen = (sl / "gate" / "pass2_seen.jsonl").read_text(encoding="utf-8").strip().splitlines()
chk("single: a replaced pass-2 file is accepted while KAPPA.json does not exist; every pass-2 hash seen is logged",
    kl3["status"] == "COMPUTED" and len(seen) == 2, f"{kl3['status']} hashes logged={len(seen)}")

vm2 = run(sm, "validity", "--scores-v1", str(sm / "gate" / "scores.csv"))
s64 = vm2["FR_6_4a"]
chk("FR 6.4a fields still reported beside the gate (BA_crux, BA_sh, zero-crux share, wording rule, scorer-v1 BA)",
    all(k_ in s64 for k_ in ("BA_crux", "BA_sh", "zero_crux_share_of_correct_AI_negatives", "wording_rule_fires", "scorer_v1_gate_BA")),
    f"BA_crux n={s64['BA_crux']['n']} BA_sh n={s64['BA_sh']['n']} wording_fires={s64['wording_rule_fires']}")

# ---- A3 single: failures
sf = cp("single_kfail", design="single_labeler", acc=0.99, r=0.45, ai_acc=0.95, seed=11)
kf = run(sf, "kappa")
vf = run(sf, "validity")
chk("single: self-consistency kappa < 0.60 -> gate FAIL even though BA lower bound > 0.5",
    (not kf["kappa"]["pass"]) and vf["status"] == "FAIL" and vf["balanced_accuracy"]["passed"], f"kappa={kf['kappa']['kappa']:.2f} {vf['status']}")
chk("single: failed agreement -> headline stamped 'not the paper's headline'", "AGREEMENT_NOT_ESTABLISHED" in vf["headline"]["state_stamp"], vf["headline"]["state_stamp"][:40])
sb = cp("single_bafail", design="single_labeler", acc=0.99, r=0.99, ai_acc=0.5, seed=8)
vb = run(sb, "validity")
chk("single: BA lower bound <= 0.5 -> FAIL at once (no kappa needed)", vb["status"] == "FAIL" and not vb["kappa_recorded"], f"lo={vb['balanced_accuracy']['lo']:.3f}")

# ---- A4 incomplete / tamper / design guard
si = cp("single_inc", design="single_labeler", seed=7)
d = pd.read_csv(si / "labels" / "author_pass1.csv", dtype=str, keep_default_na=False)
d.loc[0, "label"] = ""
d.to_csv(si / "labels" / "author_pass1.csv", index=False)
ki = run(si, "validity")
chk("blank first-pass label -> INCOMPLETE, nothing filled, DESIGN.json not written (no gate time yet)",
    ki["status"] == "INCOMPLETE" and any("blank" in p for p in ki["problems"]) and not (si / "gate" / "DESIGN.json").exists(), str(ki["problems"][:1])[:70])
d = pd.read_csv(sg / "labels" / "author_pass1.csv", dtype=str, keep_default_na=False)
d.loc[0, "label"] = "SHOWS" if d.loc[0, "label"] != "SHOWS" else "HIDES"
st = sg / "labels" / "author_pass1.csv"
orig_bytes = st.read_bytes()
d.to_csv(st, index=False)
vt = run(sg, "validity")
chk("first-pass file edited after gate time -> STOP / INCOMPLETE, hash mismatch named", vt["status"] == "INCOMPLETE" and any("STOP" in p for p in vt["problems"]), str(vt["problems"][:1])[:80])
st.write_bytes(orig_bytes)
dp = sg / "gate" / "DESIGN.json"
dtxt = dp.read_bytes()
dp.write_bytes(dtxt.replace(b"single_labeler", b"two_human", 1))
e, msg = exits(run, sg, "validity")
chk("DESIGN.json altered -> every step refuses", e and "DESIGN.json" in msg, msg[:70])
dp.write_bytes(dtxt)
dp.unlink()
e, msg = exits(run, sg, "validity")
chk("DESIGN.json deleted after outputs exist -> refuses (design cannot be re-decided)", e and "DESIGN.json" in msg, msg[:70])
dp.write_bytes(dtxt)

# ---- A5 two-human
tg = cp("two_good", design="two_human", acc=0.99, vol_acc=0.99, ai_acc=0.95, adj_acc=0.99, seed=7)
snaps["tg"] = snap(tg)
kt = run(tg, "kappa")
DT = json.loads((tg / "gate" / "DESIGN.json").read_text(encoding="utf-8"))
chk("DESIGN.json = two_human because volunteer_pass1.csv exists (existence only)", DT["design"] == "two_human" and "volunteer_pass1.csv" in DT["files_in_labels_dir"], DT["design"])
chk("two-human: kappa = inter-rater author pass 1 vs volunteer on 50 items, cut 0.40, CI + AC1",
    kt["status"] == "COMPUTED" and kt["kappa"]["n_items"] == 50 and kt["kappa"]["cut"] == 0.40 and len(kt["kappa"]["kappa_ci95"]) == 2 and not np.isnan(kt["kappa"]["ac1"])
    and kt["kappa"]["by_kind_original"]["n"] == 38 and kt["kappa"]["by_kind_n2"]["n"] == 12, f"kappa={kt['kappa']['kappa']:.3f} pass={kt['kappa']['pass']}")
vtg = run(tg, "validity")
chk("two-human: validity PASS with adjudicated labels; no PROVISIONAL state",
    vtg["status"] in ("PASS", "FAIL") and vtg["status"] != "PROVISIONAL_PASS" and vtg["balanced_accuracy"]["against"] == "adjudicated labels", f"{vtg['status']} adjudicated={vtg['n_adjudicated']}")
chk("two-human: BA vs the volunteer's own labels (hypothesis-blind) and vs author pass 1 printed beside it",
    "ba_vs_volunteer_own_labels_before_adjudication_hypothesis_blind" in vtg["also_reported"] and "ba_vs_author_pass1_labels" in vtg["also_reported"], "ok")
chk("two-human: headline prints each annotator's own H (volunteer labelled hypothesis-blind) and the two-human wording",
    "volunteer_own_hypothesis_blind_annotator" in vtg["headline"] and "author_own_pass1" in vtg["headline"] and "hypothesis-blind volunteer" in vtg["headline"]["annotator_wording"], "ok")
# ADJ missing -> INCOMPLETE; no label created
tn = cp("two_noadj", design="two_human", acc=0.9, vol_acc=0.8, seed=9)
run(tn, "kappa")
(tn / "labels" / "ADJ.csv").unlink()
vn = run(tn, "validity")
chk("two-human: missing ADJ.csv -> INCOMPLETE, items named, nothing filled", vn["status"] == "INCOMPLETE" and any("ADJ.csv" in p for p in vn["problems"]), str(vn["problems"][:1])[:80])
tf = cp("two_finallabel", design="two_human", acc=0.9, vol_acc=0.8, seed=9)
run(tf, "kappa")
pd.read_csv(tf / "labels" / "ADJ.csv").rename(columns={"adj_label": "final_label"}).to_csv(tf / "labels" / "ADJ.csv", index=False)
vff = run(tf, "validity")
chk("two-human: ADJ with final_label column rejected -> INCOMPLETE", vff["status"] == "INCOMPLETE" and any("adj_label" in p for p in vff["problems"]), str(vff["problems"][:1])[:70])
# volunteer present but incomplete at gate time
tv = cp("two_volinc", design="two_human", seed=7, vol_complete=False)
kv = run(tv, "kappa")
vv = run(tv, "validity")
DV = json.loads((tv / "gate" / "DESIGN.json").read_text(encoding="utf-8"))
chk("volunteer file present but incomplete at gate time -> design stays two_human, gate INCOMPLETE (no fall-back)",
    DV["design"] == "two_human" and kv["status"] == "INCOMPLETE" and vv["status"] == "INCOMPLETE", f"{DV['design']} {kv['status']} {vv['status']}")
# selfcons in two-human
tg_selfcons = run(tg, "selfcons")
chk("two-human: author self-consistency printed with CI, no rule", tg_selfcons["status"] == "COMPUTED" and "self_consistency" in tg_selfcons and "cut" not in tg_selfcons["self_consistency"], "ok")
e, msg = exits(run, sg, "selfcons")
chk("selfcons refused in the single-labeler design", e, msg[:60])

# ---- A6 volunteer arrives after gate time
lv_s = cp("lv_single", design="single_labeler", seed=7, acc=0.99, r=0.99, ai_acc=0.95)
lv_t = MD.build("lv_two", design="two_human", seed=7, acc=0.99, r=0.99, ai_acc=0.95)
w0 = run(lv_s, "validity")
shutil.copy2(lv_t / "labels" / "volunteer_pass1.csv", lv_s / "labels" / "volunteer_pass1.csv")
w1 = run(lv_s, "validity")
DL = json.loads((lv_s / "gate" / "DESIGN.json").read_text(encoding="utf-8"))
chk("late volunteer file: design stays single_labeler; descriptive table only; status and headline unchanged",
    DL["design"] == "single_labeler" and "late_volunteer_descriptive" in w1 and w1["status"] == w0["status"]
    and w1["headline"]["H"] == w0["headline"]["H"] and "author_vs_volunteer" in w1["late_volunteer_descriptive"], f"{w0['status']} -> {w1['status']}")

# ---- A7 N2 check
chk("Fisher: 6 HIDES / 6 not, 10 of 12 right -> p <= 0.05; 9 of 12 -> p > 0.05",
    G1.fisher_p(5, 1, 5, 1) <= 0.05 and G1.fisher_p(4, 2, 5, 1) > 0.05 and G1.fisher_p(5, 1, 4, 2) > 0.05, f"{G1.fisher_p(5, 1, 5, 1):.4f} {G1.fisher_p(5, 1, 4, 2):.4f}")
chk("Fisher: all one class -> p = 1 (does not pass)", G1.fisher_p(6, 0, 0, 0) == 1.0 and G1.fisher_p(0, 0, 6, 0) == 1.0, "ok")
n2 = run(sg, "n2check")
chk("N2 check (single design, gate 1 recorded): flag follows Fisher p <= 0.05 and the gate status; 12 items; wording fields present",
    n2["n_items"] == 12 and n2["N2_VALIDATED"] == (n2["fisher_one_sided_p"] <= 0.05 and n2["gate1_status"] == "PASS")
    and "12 N2 statements pooled over five generators" in n2["label_if_validated"], f"{n2['n2_check']} p={n2['fisher_one_sided_p']:.4f} gate={n2['gate1_status']}")
n2b = run(sb, "n2check")
chk("N2 check: gate 1 FAIL -> NOT PASSED, EXPLORATORY wording", n2b["n2_check"] == "NOT PASSED" and not n2b["N2_VALIDATED"] and "EXPLORATORY" in n2b["label_otherwise"], n2b["n2_check"])
n2p = run(sm, "n2check")
chk("N2 check: PROVISIONAL_PASS gate -> provisional flag only, never N2_VALIDATED",
    not n2p["N2_VALIDATED"] and n2p["n2_check"] in ("PROVISIONAL_PASS", "NOT PASSED"), n2p["n2_check"])

# ---- A8 LLM annotator
lm = run(sm, "llm")
chk("LLM step refused before both author files are saved (single design)", lm["status"] == "NOT_ALLOWED_YET", lm["status"])
ll = run(sg, "llm")
chk("LLM agreement: kappa + AC1 + CI on 3 categories, missing label left out and counted, labelled LLM, never human",
    ll["status"] == "COMPUTED" and len(ll["missing_or_invalid_llm_labels_left_out"]) == 1 and ll["n_llm_labels"] == 49
    and "not a human" in ll["label"] and len(ll["author_pass1_vs_llm"]["kappa_ci95"]) == 2 and ll["author_pass1_vs_llm"]["seed"] == 20261134
    and ll["author_pass1_vs_llm"]["by_kind_n2"]["n"] <= 12 and "scorer1_BA_vs_llm_labels_NOT_HUMAN" in ll, f"kappa={ll['author_pass1_vs_llm']['kappa']:.3f}")
lt = run(tg, "llm")
chk("LLM two-human: also against the volunteer and the labels of record", "volunteer_vs_llm" in lt and "labels_of_record_vs_llm" in lt, "ok")

# ---- A9 never writes into labels/; guards
chk("nothing was written into any labels/ directory during all runs (file lists and hashes unchanged)",
    snap(tg) == snaps["tg"] and {k: v for k, v in snap(sg).items()} == snaps["sg"], "ok")
e, msg = exits(G1.main, ["--step", "validity", "--kind", "dummy"])
chk("kind=dummy with the default (real) paths refused", e, msg[:70])
e, msg = exits(G1.main, ["--step", "validity", "--kind", "real", "--labels-dir", str(sg / "labels"), "--gate-dir", str(sg / "gate")])
chk("kind=real with DUMMY_ paths refused", e and "DUMMY_" in msg, msg[:70])
e, msg = exits(G1.main, ["--step", "validity", "--kind", "dummy", "--labels-dir", str(sg / "labels"), "--gate-dir", str(sg / "labels" / "DUMMY_x")])
chk("gate dir inside labels dir refused", e, msg[:70])
chk("no GATE1_RESULT.json / N2CHECK_RESULT.json written by gate1", not any((r / "gate" / n).exists() for r in (sg, tg, sm, sb) for n in ("GATE1_RESULT.json", "N2CHECK_RESULT.json")), "ok")

# =============================================================== (B) analysis set
syn = C.make_synth(n_launches=60, seed=3)
devids = {f"L{i}" for i in range(20)}
C._DEV.clear()
C._DEV.update({"ids": set(devids), "sha": "testsha"})
try:
    pj = lambda **k: C.load_params(json.dumps(k))
    r = A2.fit_models(syn, pj(B=200))
    chk("A2 default analysis set excludes the development launches", r["n_clusters"] == 40 and r["analysis_set"]["n_dev_launches_dropped"] == 20
        and r["analysis_set"]["set"].startswith("CONFIRMATORY"), f"clusters={r['n_clusters']}")
    r = A2.fit_models(syn, pj(B=200, include_dev=True))
    chk("A2 include_dev = A2d sensitivity: all launches, labelled 'including the development launches'",
        r["n_clusters"] == 60 and "including the development launches" in r["analysis_set"]["set"], r["analysis_set"]["set"])
    n1 = N1.run(syn, pj(B=200))
    chk("N1 default set excludes the development launches; include_dev restores", n1["n_clusters"] <= 40 and N1.run(syn, pj(B=200, include_dev=True))["n_clusters"] > 40, f"{n1['n_clusters']}")
    n4 = N4.run(syn, pj(B=200))
    chk("N4 default set excludes the development launches", n4["n_clusters"] == 40, str(n4["n_clusters"]))
    nz = np.random.default_rng(1).normal(0, 0.05, 240)
    st_ = pd.DataFrame([(f"L{g}", f"L{g}R0", j, "MODEL_MEDIATOR" if j < 2 else "HUMAN_MEDIATOR", 0.3 + 0.1 * j + nz[4 * g + j]) for g in range(60) for j in range(4)],
                       columns=["launch_id", "round_id", "cand", "prov", "E"])
    a3 = A3.diff_run(st_, "prov", "MODEL_MEDIATOR", "HUMAN_MEDIATOR", pj(B=200))
    chk("A3/N3 (diff_run) default set excludes the development launches", a3["n_clusters"] == 40 and a3["analysis_set"]["n_dev_launches_dropped"] == 20, str(a3["n_clusters"]))
    C._DEV.clear()
    C._DEV.update({"ids": None, "sha": None})
    e, msg = exits(C.restrict_confirmatory, syn, pj(), "real")
    chk("kind=real without the development-launch file is refused (exclusion cannot be applied)", e, msg[:70])
    # tier: informative rounds only inside the development launches
    C._DEV.clear()
    C._DEV.update({"ids": set(devids), "sha": "testsha"})
    d2 = syn.copy()
    d2["E"] = np.where(d2.launch_id.isin(devids), d2["E"], 0.5)
    for lid in [f"L{i}" for i in range(20, 25)]:
        m = d2.launch_id == lid
        d2.loc[m, "E"] = d2.loc[m, "cand"] / 3.0
    f = R / "inf_dev.csv"
    d2.to_csv(f, index=False)
    ot = INF.main(["--input", str(f), "--kind", "dummy", "--out", str(R / "A2_TIER_dummy_dev.json"), "--nfit", "10"])
    chk("tier of record counts the confirmatory set; development-launch informativeness shown only as a side figure",
        ot["K_inf"] == 5 and ot["counts_including_development_launches"]["K_inf"] == 25 and ot["tier"] == "NOT MEASURABLE"
        and ot["analysis_set"]["set"].startswith("CONFIRMATORY"), f"K_inf={ot['K_inf']} incl dev={ot['counts_including_development_launches']['K_inf']} tier={ot['tier']}")
    e, msg = exits(INF.main, ["--input", str(f), "--kind", "dummy", "--include-dev", "--out", str(C.GATE / C.TIER_FILE)])
    chk("--include-dev (all launches) may not write the tier of record", e, msg[:70])
    oa = INF.main(["--input", str(f), "--kind", "dummy", "--include-dev", "--out", str(R / "A2_TIER_dummy_alldev.json"), "--nfit", "10"])
    chk("--include-dev computes the all-launch sensitivity version and labels it", oa["K_inf"] == 25 and "SENSITIVITY" in oa["tier_of_record_set"], oa["tier_of_record_set"])
finally:
    C._DEV.clear()

# =============================================================== lock (R4 additions to common.check_kind are in test_fixes.py)
C.write_result(R / "r4_results.json", {"all_pass": bool(ok)}, __file__, "synthetic", "n/a", [], "test_r4 results")
print("R4 TESTS PASS" if ok else "R4 TESTS FAILED")
sys.exit(0 if ok else 1)
