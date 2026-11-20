"""Tests for the R5 gate code (FROZEN_RULES 6.R5; decisions.md D50, D51).  Synthetic / dummy data in temp dirs only.
The real project (labels/, gate1/, FROZEN_RULES.md) is never touched.   python -I test_r5.py"""
import inspect
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common as C  # noqa: E402
import freeze  # noqa: E402
import gate1_r5 as G  # noqa: E402
import step2_reference as S2  # noqa: E402
import verification_eval as V  # noqa: E402

FAILS = []
N = [0]


def chk(name, cond, info=""):
    N[0] += 1
    if not cond:
        FAILS.append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if (info and not cond) else ""))


REAL_GATE_BEFORE = sorted(os.listdir(HERE.parent / "gate1"))
REAL_LABELS_BEFORE = sorted(os.listdir(HERE.parent / "labels"))
B = 400

# =============================================================== step 2
for nm, cols in (("A2", S2.COLS_A2), ("CC", S2.COLS_CC), ("PS", S2.COLS_PS), ("EXT", S2.EXTRACT_KEYS)):
    bad = [c for c in cols for f in S2.FORBIDDEN_SUBSTR if f.lower() in c.lower()] + [c for c in cols if c in S2.FORBIDDEN_EXACT]
    chk(f"s2 whitelist {nm} has no rank/rating/E/label/critique/survey column", not bad, bad)
chk("s2 PS reads ratings.agreement only from the position-ratings file", "ratings.agreement" not in S2.COLS_CC)
chk("s2 E not in extraction keys", "E" not in S2.EXTRACT_KEYS)

chk("member_value maps tokens", S2.member_value(["AGREE"]) == 2 and S2.member_value(["strongly_disagree"]) == -3)
chk("member_value MOCK / empty / two tokens -> unrated",
    S2.member_value(["MOCK"]) is None and S2.member_value([]) is None and S2.member_value(["AGREE", "AGREE"]) is None)
chk("hsplit both sides", S2.hsplit([1, -1, 0]) == 1)
chk("hsplit neutral counts to neither side", S2.hsplit([0, 0, 2]) == 0 and S2.hsplit([0, -1, -3]) == 0)
chk("hsplit strong", S2.hsplit([1, -2], strong=True) == 0 and S2.hsplit([2, -2], strong=True) == 1)

good = S2.evaluate(S2.synth_table(sens=0.85, spec=0.6), B=B)
chk("s2 good scorer -> PASS", good["outcome"] == "PASS", (good["BA2"], good["lb_used"]))
chance = S2.evaluate(S2.synth_table(sens=0.85, spec=0.15, seed=2), B=B)
chk("s2 chance scorer (finds a crux almost always) -> FAIL", chance["outcome"] == "FAIL", (chance["BA2"], chance["lb_used"]))
weak = S2.evaluate(S2.synth_table(n_launch=800, sens=0.7, spec=0.45, seed=3), B=B)
chk("s2 weak scorer -> WEAK", weak["outcome"] == "WEAK", (weak["BA2"], weak["lb_used"]))
small = S2.evaluate(S2.synth_table(n_launch=50, seed=4), B=B)
chk("s2 < 200 rounds / < 100 launches -> UNUSABLE", small["outcome"] == "UNUSABLE", small["unusable_reasons"])
rare = S2.evaluate(S2.synth_table(n_launch=150, rounds_per=2, p_split=0.9, seed=5), B=B)
chk("s2 Hsplit class < 50 rounds -> UNUSABLE", rare["outcome"] == "UNUSABLE", rare["hsplit_class_counts"])
chk("s2 decide: > 1% single-class resamples -> UNUSABLE",
    S2.decide(0.7, [(0.6, 0.8, 101, 10000)], (True, []))[0] == "UNUSABLE")
chk("s2 decide: exactly 1% single-class resamples is allowed",
    S2.decide(0.7, [(0.6, 0.8, 100, 10000)], (True, []))[0] == "PASS")
chk("s2 decide uses the SMALLER lower bound", S2.decide(0.7, [(0.6, 0.8, 0, 10), (0.49, 0.8, 0, 10)], (True, []))[0] == "FAIL")
chk("s2 decide: point 0.5999 with LB > 0.5 is WEAK, 0.60 is PASS",
    S2.decide(0.5999, [(0.55, 0.65, 0, 10)], (True, []))[0] == "WEAK" and S2.decide(0.60, [(0.55, 0.65, 0, 10)], (True, []))[0] == "PASS")

# statistician condition 5: ONLY the primary BA2 decides
chk("s2 decide() takes only the primary BA2, its bootstraps and usability",
    list(inspect.signature(S2.decide).parameters) == ["ba2", "boots", "usable_counts"])
t = S2.synth_table(seed=6)
base = S2.evaluate(t, B=B)
t2 = t.copy()
t2["hsplit_strong"] = 1 - t2["hsplit_strong"]
t2["sd_values"] = -t2["sd_values"]
alt = S2.evaluate(t2, B=B)
chk("s2 changing reported-only variants (strong split, SD) does not change outcome or LB",
    alt["outcome"] == base["outcome"] and alt["lb_used"] == base["lb_used"] and
    alt["reported_no_rule"]["BA2_strong_split"] != base["reported_no_rule"]["BA2_strong_split"])
orig_rep = S2.reported
S2.reported = lambda *a, **k: {"BA2_strong_split": 0.0, "BA2_all_rated": 1.0, "spearman_ncruxes_sd": -1.0}
alt2 = S2.evaluate(t, B=B)
S2.reported = orig_rep
chk("s2 replacing every reported variant does not change outcome", alt2["outcome"] == base["outcome"] and alt2["BA2"] == base["BA2"])

tq = S2.synth_table(seed=7, q_pool=60)
rq = S2.evaluate(tq, B=B)
chk("s2 question ids in > 1 launch -> question bootstrap run", rq.get("question_in_more_than_one_launch") and "question_boot" in rq)
chk("s2 lb_used = min(launch LB, question LB)",
    rq["lb_used"] is None or abs(rq["lb_used"] - min(rq["launch_boot"]["lb"], rq["question_boot"]["lb"])) < 1e-12, rq.get("lb_used"))
chk("s2 one question per launch -> no question bootstrap", "question_boot" not in base)

tm = S2.synth_table(seed=8)
b8 = S2.evaluate(tm, B=B)
tm.loc[:9, "ext_ok"] = False
rm = S2.evaluate(tm, B=B)
chk("s2 missing extraction counted as the wrong call", rm["n_extraction_missing_counted_wrong"] == 10 and
    rm["confusion"]["tp"] + rm["confusion"]["tn"] < b8["confusion"]["tp"] + b8["confusion"]["tn"] and
    sum(rm["confusion"].values()) == sum(b8["confusion"].values()))
td = S2.synth_table(seed=9)
td.loc[:79, "dropped_too_long"] = True       # 80 of 1,200 = 6.7% > 5%
rd = S2.evaluate(td, B=B)
chk("s2 context drops excluded and counted; > 5% -> BA2 with drops as wrong reported",
    rd["n_dropped_context_length"] == 80 and rd["n_usable_rounds"] == 1120 and "BA2_context_drops_as_wrong" in rd["reported_no_rule"])
td2 = S2.synth_table(seed=9)
td2.loc[:39, "dropped_too_long"] = True      # 3.3%: no extra figure
chk("s2 context drops <= 5% -> no drops-as-wrong figure", "BA2_context_drops_as_wrong" not in S2.evaluate(td2, B=B)["reported_no_rule"])
tc = S2.synth_table(seed=10)
tc.loc[:4, "n_rated"] = tc.loc[:4, "n_members"] - 2
rc = S2.evaluate(tc, B=B)
chk("s2 > 1 unrated member -> round unusable", rc["n_unusable_rating_coverage"] == 5)
chk("s2 reports prevalences, n_rated==5 BA, class counts, sens/spec",
    all(k in base["reported_no_rule"] for k in ("prevalence_hsplit", "prevalence_sdis", "BA2_n_rated_5"))
    and "hsplit_class_counts" in base and base["sens"] is not None and base["spec"] is not None)

# real-data path on a FAKE project in a temp dir (freeze before reading, refuse repeat)
tmp = Path(tempfile.mkdtemp(prefix="r5_s2_"))
try:
    root = tmp / "proj"
    (root / "analysis" / "scores").mkdir(parents=True)
    (root / "labels").mkdir()
    (root / "gate1").mkdir()
    data = tmp / "data"
    data.mkdir()
    (root / "FROZEN_RULES.md").write_text("dummy rules\n", encoding="utf-8")
    shutil.copy(HERE / "step2_reference.py", root / "analysis" / "step2_reference.py")
    rng = np.random.default_rng(11)
    toks = list(S2.TOKENS)
    a2rows, ccrows, psrows, ext = [], [], [], []
    for L in range(130):
        for r in range(2):
            rid, q = f"L{L}r{r}", f"q{L}_{r}"
            split = rng.random() < 0.6
            for m in range(5):
                pid = f"p{L}_{m}"
                a2rows.append({"launch_id": f"L{L}", "round_id": rid, "rank": 0, "E": 0.5})
                ccrows.append({"launch_id": f"L{L}", "round_id": rid, "iteration_index": 0, "question.id": q,
                               "own_opinion.metadata.participant_id": pid, "metadata.provenance": "HUMAN_CITIZEN",
                               "rankings.numerical_ranks": [0, 1, 2, 3]})
                v = (["AGREE", "DISAGREE"][m % 2] if split else "AGREE")
                psrows.append({"launch_id": f"L{L}", "question.id": q, "metadata.participant_id": pid,
                               "metadata.provenance": "HUMAN_CITIZEN", "metadata.status": "COMPLETED", "rating_index": 0,
                               "ratings.agreement": [v], "monotonic_timestamp": L * 10 + m})
            sd = split if rng.random() < 0.85 else (not split)
            ext.append({"launch_id": f"L{L}", "round_id": rid, "ok": True, "n_cruxes": int(sd) * 2,
                        "dropped_too_long": False, "cruxes": []})
    pd.DataFrame(a2rows).to_parquet(root / "analysis" / "scores" / "a2_long_shuffled.parquet")
    pd.DataFrame(ccrows).to_parquet(data / "hm_all_candidate_comparisons.parquet")
    pd.DataFrame(psrows).to_parquet(data / "hm_all_position_statement_ratings.parquet")
    with open(root / "analysis" / "scores" / "a2_extractions_v2.jsonl", "w", encoding="utf-8") as f:
        for e in ext:
            f.write(json.dumps(e) + "\n")
    dev = tmp / "pilot_groups.jsonl"
    dev.write_text(json.dumps({"launch_id": "L0"}) + "\n", encoding="utf-8")
    chk("s2 real: FREEZE.json absent before", not (root / "gate1" / "FREEZE.json").exists())
    out, res = S2.run_real(root, data, dev, expected_rounds=258, B=B)
    fz = json.loads((root / "gate1" / "FREEZE.json").read_text(encoding="utf-8"))
    chk("s2 real: FREEZE.json written by the step-2 trigger with labels empty",
        "step2" in fz["trigger"] and fz["first_label_file"] is None)
    chk("s2 real: FREEZE.json written before the result (frozen_utc <= result file mtime)",
        (root / "gate1" / "FREEZE.json").stat().st_mtime <= out.stat().st_mtime)
    chk("s2 real: FROZEN_RULES read-only after freeze", freeze.is_readonly(root / "FROZEN_RULES.md"))
    chk("s2 real: script hash recorded in FREEZE", fz["files"]["step2_reference.py"]["sha256"] == S2.sha(root / "analysis" / "step2_reference.py"))
    chk("s2 real: dev launch excluded, result written, outcome is a code",
        res["outcome"] in S2_CODES if (S2_CODES := ("PASS", "WEAK", "FAIL", "UNUSABLE")) else False, res["outcome"])
    chk("s2 real: per-round file kept private", any((root / "gate1" / "step2_private").iterdir()))
    try:
        S2.run_real(root, data, dev, expected_rounds=258, B=B)
        chk("s2 real: second run refused", False)
    except SystemExit:
        chk("s2 real: second run refused", True)
    for p in (root / "gate1").glob("STEP2_computed__*.json"):
        p.unlink()
    try:
        S2.run_real(root, data, dev, expected_rounds=999, B=B)
        chk("s2 real: wrong round count refused", False)
    except SystemExit:
        chk("s2 real: wrong round count refused", True)
    # a changed script is refused
    os.chmod(root / "FROZEN_RULES.md", 0o666)
    (root / "analysis" / "step2_reference.py").write_text("# changed\n", encoding="utf-8")
    try:
        S2.ensure_freeze(root)
        chk("s2 real: changed step-2 script refused", False)
    except SystemExit:
        chk("s2 real: changed step-2 script refused", True)
finally:
    for p in tmp.rglob("*"):
        try:
            os.chmod(p, 0o666)
        except OSError:
            pass
    shutil.rmtree(tmp, ignore_errors=True)

# freeze.py R5 trigger
tmp = Path(tempfile.mkdtemp(prefix="r5_fz_"))
try:
    (tmp / "labels").mkdir()
    (tmp / "gate1").mkdir()
    (tmp / "FROZEN_RULES.md").write_text("x\n", encoding="utf-8")
    c, m = freeze.run(tmp, tmp / "gate1" / "FREEZE.json")
    chk("freeze: default trigger with labels empty -> nothing frozen", c == 1)
    (tmp / "pk.csv").write_text("a\n", encoding="utf-8")
    (tmp / "gate1" / "R5_FREEZE_MANIFEST.json").write_text(json.dumps({"paths": ["pk.csv", "missing.csv"]}), encoding="utf-8")
    c, m = freeze.run(tmp, tmp / "gate1" / "FREEZE.json", trigger="step2")
    rec = json.loads((tmp / "gate1" / "FREEZE.json").read_text(encoding="utf-8"))
    chk("freeze: step2 trigger freezes with labels empty", c == 0 and rec["first_label_file"] is None, m)
    chk("freeze: R5 manifest files hashed, missing ones listed",
        rec["r5_manifest_files"]["pk.csv"] and "missing.csv" in rec["missing_tracked"])
    c, m = freeze.run(tmp, tmp / "gate1" / "FREEZE.json", trigger="bogus")
    chk("freeze: unknown trigger refused", c == 2)
finally:
    for p in tmp.rglob("*"):
        try:
            os.chmod(p, 0o666)
        except OSError:
            pass
    shutil.rmtree(tmp, ignore_errors=True)

# =============================================================== step 3
ids = [f"it{i:02d}" for i in range(25)]


def make_scores(path, E, ncr=None, kinds=None):
    with open(path, "w", encoding="utf-8") as f:
        for j, i in enumerate(ids):
            f.write(json.dumps({"item_id": i, "kind": (kinds or ["original"] * 19 + ["n2"] * 6)[j], "E": E[j],
                                "n_cruxes": (ncr[j] if ncr else (2 if E[j] is not None else 2)), "ok": E[j] is not None}) + "\n")


def make_labels(path, q1, q2, cols=None, ts="2026-11-16T02:00Z", drop=0, bad=None):
    rows = [",".join(cols or V.COLUMNS)]
    for j, i in enumerate(ids[: 25 - drop]):
        rows.append(f"{i},{bad if (bad and j == 0) else q1[j]},{q2[j]},,{ts}")
    Path(path).write_text("\n".join(rows) + "\n", encoding="utf-8")


tmp = Path(tempfile.mkdtemp(prefix="r5_s3_"))
try:
    sc = tmp / "scores.jsonl"
    # 16 Q1-yes items; author 'not acknowledged' on 8; scorer right on all 16
    q1 = ["YES"] * 16 + ["NO"] * 9
    q2 = ["NO"] * 8 + ["YES"] * 8 + ["YES"] * 9
    E = [0.9] * 8 + [0.1] * 8 + [0.5] * 9
    make_scores(sc, E)
    lab = tmp / "author_verification.csv"
    make_labels(lab, q1, q2)
    ans, probs = V.read_author_file(lab, set(ids))
    chk("s3 valid file parses", not probs, probs)
    r = V.evaluate(ans, V.read_scores(sc), B=B)
    chk("s3 perfect scorer -> SUPPORTED", r["outcome"] == "SUPPORTED", r["fisher_p_one_sided_conditional"])
    chk("s3 V_ev = 16/25 with Wilson", r["V_ev"]["k"] == 16 and r["V_ev"]["wilson"][0] < 0.64 < r["V_ev"]["wilson"][1])
    chk("s3 Fisher orientation: [[8,0],[0,8]] p = 1/12870", abs(r["fisher_p_one_sided_conditional"] - 1 / 12870) < 1e-12,
        r["fisher_p_one_sided_conditional"])
    chk("s3 H5 from originals with Q1=YES (16 >= 10)", r["H5"] is not None and r["H5"]["n"] == 16 and r["H5"]["k"] == 8)
    # anti-scorer -> CONTRADICTED with the D50 wording
    make_scores(sc, [0.1] * 8 + [0.9] * 8 + [0.5] * 9)
    r = V.evaluate(ans, V.read_scores(sc), B=B)
    chk("s3 anti scorer -> CONTRADICTED", r["outcome"] == "CONTRADICTED")
    chk("s3 CONTRADICTED wording is the point-estimate form", r["contradicted_wording"].startswith("point balanced accuracy <= 0.5"))
    # moderate: 6/8 and 6/8 right -> p ~ 0.066 -> INCONCLUSIVE
    make_scores(sc, [0.9] * 6 + [0.1] * 2 + [0.1] * 6 + [0.9] * 2 + [0.5] * 9)
    r = V.evaluate(ans, V.read_scores(sc), B=B)
    chk("s3 6/8 + 6/8 -> INCONCLUSIVE (Fisher p > 0.05, BA 0.75)", r["outcome"] == "INCONCLUSIVE",
        (r["fisher_p_one_sided_conditional"], r["BA3"]))
    # 9 Q1-yes -> UNUSABLE
    make_labels(lab, ["YES"] * 9 + ["NO"] * 16, ["NO"] * 5 + ["YES"] * 20)
    ans, _ = V.read_author_file(lab, set(ids))
    chk("s3 9 Q1-yes items -> UNUSABLE", V.evaluate(ans, V.read_scores(sc), B=B)["outcome"] == "UNUSABLE")
    # class of 2 -> UNUSABLE
    make_labels(lab, ["YES"] * 16 + ["NO"] * 9, ["NO"] * 2 + ["YES"] * 23)
    ans, _ = V.read_author_file(lab, set(ids))
    chk("s3 only 2 'not acknowledged' -> UNUSABLE", V.evaluate(ans, V.read_scores(sc), B=B)["outcome"] == "UNUSABLE")
    # missing E counted wrong
    make_labels(lab, q1, q2)
    ans, _ = V.read_author_file(lab, set(ids))
    make_scores(sc, [None] * 8 + [0.1] * 8 + [0.5] * 9)
    r = V.evaluate(ans, V.read_scores(sc), B=B)
    chk("s3 missing E counted as the wrong call", r["n_missing_E_on_q1_yes_counted_wrong"] == 8 and r["table_A_by_S"][0] == [0, 8])
    # zero cruxes = not hiding
    make_scores(sc, [None] * 25, ncr=[0] * 25)
    r = V.evaluate(ans, V.read_scores(sc), B=B)
    chk("s3 zero cruxes -> S = 0, presence C = 0", r["table_A_by_S"][0] == [0, 8] and r["presence_table"]["C1_Q1yes"] == 0)
    # schema problems
    make_labels(lab, q1, q2, bad="MAYBE")
    chk("s3 invalid token -> problem", V.read_author_file(lab, set(ids))[1])
    make_labels(lab, q1, q2, drop=1)
    chk("s3 24 rows -> problem", V.read_author_file(lab, set(ids))[1])
    make_labels(lab, q1, q2, cols=["item_id", "q1", "q2", "comment", "pass_started_utc"])
    chk("s3 wrong columns -> problem", V.read_author_file(lab, set(ids))[1])
    make_labels(lab, q1, q2, ts="yesterday")
    chk("s3 unparseable pass_started_utc -> problem", V.read_author_file(lab, set(ids))[1])
    make_labels(lab, [x.lower() for x in q1], [" " + x.lower() + " " for x in q2])
    chk("s3 case and spaces ignored", not V.read_author_file(lab, set(ids))[1])
    # run(): incomplete -> INCOMPLETE (never filled); hash written once; changed file refused
    gd = tmp / "gate"
    make_scores(sc, E)
    make_labels(lab, q1, q2, drop=3)
    st, rr = V.run(lab, sc, gd, B=B)
    chk("s3 run: incomplete file -> INCOMPLETE, no hash written", st == "INCOMPLETE" and not (gd / "AUTHOR_VERIFICATION_HASH.json").exists())
    make_labels(lab, q1, q2)
    st, rr = V.run(lab, sc, gd, B=B)
    chk("s3 run: complete -> COMPUTED, hash recorded", st == "COMPUTED" and (gd / "AUTHOR_VERIFICATION_HASH.json").exists())
    make_labels(lab, q1, ["YES"] * 25)
    try:
        V.run(lab, sc, gd, B=B)
        chk("s3 run: replaced author file refused", False)
    except SystemExit:
        chk("s3 run: replaced author file refused", True)
    tpl = HERE.parent / "labels_build" / "v5" / "TEMPLATE_author_verification.csv"
    if tpl.exists():
        chk("s3 COLUMNS == the packet builder's template header",
            tpl.read_text(encoding="utf-8-sig").splitlines()[0].split(",") == V.COLUMNS)
    key = tmp / "key.csv"
    key.write_text("item_id,kind,launch_id\n" + "".join(f"{i},{'original' if j < 19 else 'n2'},L\n" for j, i in enumerate(ids)),
                   encoding="utf-8")
    chk("s3 read_key: 25 items, 19 original / 6 n2",
        len(V.read_key(key)) == 25 and list(V.read_key(key).values()).count("n2") == 6)
    gd2 = tmp / "gate2"
    make_labels(lab, q1, q2)
    st, rr = V.run(lab, sc, gd2, B=B, key_file=key)
    chk("s3 run with key: COMPUTED, key hash recorded", st == "COMPUTED" and rr["key_sha256"])
    key.write_text("item_id,kind\n" + "".join(f"{i},n2\n" for i in ids), encoding="utf-8")
    try:
        V.run(lab, sc, tmp / "gate3", B=B, key_file=key)
        chk("s3 run: key kind mismatch refused", False)
    except SystemExit:
        chk("s3 run: key kind mismatch refused", True)
    chk("s3 decide() rule order", V.decide(True, 0.01, 0.4) == "SUPPORTED" and V.decide(True, 0.2, 0.5) == "CONTRADICTED"
        and V.decide(True, 0.2, 0.6) == "INCONCLUSIVE" and V.decide(False, 0.0, 1.0) == "UNUSABLE")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# =============================================================== gate combination (D50) and D51 time-out
cb = G.combine
chk("g ON_TIME PASS+SUPPORTED -> VALIDATED_BOTH", cb("PASS", "SUPPORTED", "ON_TIME")[0] == "VALIDATED_BOTH")
chk("g ON_TIME PASS+INCONCLUSIVE -> VALIDATED_PRESENCE", cb("PASS", "INCONCLUSIVE", "ON_TIME")[0] == "VALIDATED_PRESENCE")
chk("g ON_TIME PASS+UNUSABLE -> VALIDATED_PRESENCE", cb("PASS", "UNUSABLE", "ON_TIME")[0] == "VALIDATED_PRESENCE")
chk("g ON_TIME PASS+CONTRADICTED -> EXPLORATORY_UNVALIDATED", cb("PASS", "CONTRADICTED", "ON_TIME")[0] == "EXPLORATORY_UNVALIDATED")
chk("g ON_TIME WEAK+SUPPORTED -> VALIDATED_HIDE_EVIDENCE", cb("WEAK", "SUPPORTED", "ON_TIME")[0] == "VALIDATED_HIDE_EVIDENCE")
chk("g ON_TIME UNUSABLE+SUPPORTED -> VALIDATED_HIDE_EVIDENCE", cb("UNUSABLE", "SUPPORTED", "ON_TIME")[0] == "VALIDATED_HIDE_EVIDENCE")
chk("g ON_TIME FAIL+SUPPORTED -> FAIL", cb("FAIL", "SUPPORTED", "ON_TIME")[0] == "FAIL")
chk("g ON_TIME WEAK+INCONCLUSIVE -> EXPLORATORY_UNVALIDATED", cb("WEAK", "INCONCLUSIVE", "ON_TIME")[0] == "EXPLORATORY_UNVALIDATED")
chk("g ON_TIME UNUSABLE+UNUSABLE -> EXPLORATORY_UNVALIDATED", cb("UNUSABLE", "UNUSABLE", "ON_TIME")[0] == "EXPLORATORY_UNVALIDATED")
chk("g ON_TIME incomplete author file -> PENDING", cb("PASS", "INCOMPLETE", "ON_TIME")[0] == "PENDING")
chk("g step 2 missing -> PENDING", cb(None, "SUPPORTED", "ON_TIME")[0] == "PENDING")
for s2, want in (("PASS", "VALIDATED_PRESENCE"), ("WEAK", "EXPLORATORY_UNVALIDATED"), ("UNUSABLE", "EXPLORATORY_UNVALIDATED"),
                 ("FAIL", "FAIL")):
    chk(f"g NOT_DONE (D51) step2 {s2} -> {want}", cb(s2, None, "NOT_DONE")[0] == want)
    chk(f"g LATE (D51) step2 {s2} -> {want}, even with a SUPPORTED step 3", cb(s2, "SUPPORTED", "LATE")[0] == want)
chk("g NOT_DONE never exceeds VALIDATED_PRESENCE",
    all(cb(s, x, "NOT_DONE")[0] in ("VALIDATED_PRESENCE", "EXPLORATORY_UNVALIDATED", "FAIL") for s in G.STEP2_CODES for x in (None,) + G.STEP3_CODES))

T0 = datetime(2026, 11, 16, 2, 0, tzinfo=timezone.utc)
tmp = Path(tempfile.mkdtemp(prefix="r5_g_"))
try:
    root = tmp / "proj"
    (root / "labels").mkdir(parents=True)
    (root / "gate1").mkdir()
    (root / "gate1" / "STEP2_computed__20261116T020000Z.json").write_text(json.dumps({"outcome": "PASS"}), encoding="utf-8")
    (root / "gate1" / "STEP3_computed__20261116T023000Z.json").write_text(json.dumps({"outcome": "SUPPORTED"}), encoding="utf-8")
    lab = root / "labels" / "author_verification.csv"
    st, rec = G.run(root, now=T0 + timedelta(minutes=40))
    chk("D51: T_READY.txt missing -> PENDING", st == "PENDING" and rec["author_timing"] == "PENDING")
    chk("D51 T_READY format YYYY-MM-DDTHH:MMZ parses as UTC",
        G.parse_iso("2026-11-16T01:23Z") == datetime(2026, 11, 16, 1, 23, tzinfo=timezone.utc))
    (root / "gate1" / "T_READY.txt").write_text("2026-11-16T02:00Z\n", encoding="utf-8")
    # (1) author file present before T_cut
    lab.write_text("x\n", encoding="utf-8")
    ts = (T0 + timedelta(minutes=20)).timestamp()
    os.utime(lab, (ts, ts))
    st, rec = G.run(root, now=T0 + timedelta(minutes=40))
    chk("D51 (1) author file before T_cut -> ON_TIME, step 3 used -> VALIDATED_BOTH",
        rec["author_timing"] == "ON_TIME" and st == "VALIDATED_BOTH", (st, rec["author_timing"]))
    ts = (T0 + timedelta(minutes=30)).timestamp()
    os.utime(lab, (ts, ts))
    chk("D51 (1b) mtime exactly T_cut counts as on time", G.run(root, now=T0 + timedelta(minutes=40))[1]["author_timing"] == "ON_TIME")
    # (1c) present before T_cut but still incomplete at T_cut -> not submitted
    s3f = root / "gate1" / "STEP3_computed__20261116T023000Z.json"
    s3f.write_text(json.dumps({"outcome": "INCOMPLETE"}), encoding="utf-8")
    st, rec = G.run(root, now=T0 + timedelta(minutes=25))
    chk("D51 (1c) incomplete file before T_cut -> PENDING (wait)", st == "PENDING")
    st, rec = G.run(root, now=T0 + timedelta(minutes=35))
    chk("D51 (1d) incomplete file at T_cut -> NOT_DONE, step 2 alone -> VALIDATED_PRESENCE",
        st == "VALIDATED_PRESENCE" and rec["author_timing"] == "NOT_DONE", (st, rec["author_timing"]))
    s3f.write_text(json.dumps({"outcome": "SUPPORTED"}), encoding="utf-8")
    # (2) absent at T_cut
    lab.unlink()
    st, rec = G.run(root, now=T0 + timedelta(minutes=29))
    chk("D51 (2a) absent before T_cut -> PENDING (nothing recorded)", st == "PENDING")
    st, rec = G.run(root, now=T0 + timedelta(minutes=31))
    chk("D51 (2b) absent at T_cut -> step 3 NOT_DONE, gate from step 2 alone -> VALIDATED_PRESENCE",
        rec["author_timing"] == "NOT_DONE" and st == "VALIDATED_PRESENCE" and rec["step3_outcome"] == "NOT_DONE", (st, rec))
    chk("D51 (2c) panel never part of the status", "never part" in rec["panel"])
    # (3) arriving after T_cut
    lab.write_text("x\n", encoding="utf-8")
    ts = (T0 + timedelta(minutes=45)).timestamp()
    os.utime(lab, (ts, ts))
    st, rec = G.run(root, now=T0 + timedelta(minutes=50))
    chk("D51 (3) author file after T_cut -> LATE, not used: VALIDATED_PRESENCE (not BOTH) + post-gate note",
        rec["author_timing"] == "LATE" and st == "VALIDATED_PRESENCE" and any("post-gate" in n for n in rec["notes"]), (st, rec))
    chk("D51 (3b) late file: step-3 file not read into the record", rec["step3_file"] is None)
    rc = G.main(["--root", str(root)])
    chk("gate1_r5 main writes a computed record (never GATE1_RESULT.json)",
        rc == 0 and any((root / "gate1").glob("gate1_r5_computed__*.json")) and not (root / "gate1" / "GATE1_RESULT.json").exists())
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# =============================================================== common.check_kind R5 path
tmp = Path(tempfile.mkdtemp(prefix="r5_ck_"))
try:
    (tmp / C.TIER_FILE).write_text("{}", encoding="utf-8")
    for st, want in (("VALIDATED_BOTH", "VALIDATED_R5_BOTH"), ("VALIDATED_PRESENCE", "HIDE_NOT_HUMAN_VALIDATED"),
                     ("VALIDATED_HIDE_EVIDENCE", "VALIDATED_R5_HIDE_EVIDENCE_ONLY"),
                     ("EXPLORATORY_UNVALIDATED", "EXPLORATORY_UNVALIDATED"), ("FAIL", "EXPLORATORY_UNVALIDATED")):
        (tmp / "GATE1_RESULT.json").write_text(json.dumps({"rules": "R5", "status": st}), encoding="utf-8")
        chk(f"check_kind R5 {st} -> {want} (no DESIGN.json needed)", C.check_kind("real", tmp) == want)
    (tmp / "GATE1_RESULT.json").write_text(json.dumps({"rules": "R5", "status": "NOT_EVALUATED"}), encoding="utf-8")
    try:
        C.check_kind("real", tmp)
        chk("check_kind R5 NOT_EVALUATED refused", False)
    except SystemExit:
        chk("check_kind R5 NOT_EVALUATED refused", True)
finally:
    C.GATE_TAG["tag"] = ""
    shutil.rmtree(tmp, ignore_errors=True)

chk("real gate1/ untouched by the tests", sorted(os.listdir(HERE.parent / "gate1")) == REAL_GATE_BEFORE)
chk("real labels/ untouched by the tests", sorted(os.listdir(HERE.parent / "labels")) == REAL_LABELS_BEFORE)
print(f"\n{N[0] - len(FAILS)}/{N[0]} passed")
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
