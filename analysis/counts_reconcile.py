"""Reconcile the evaluable-round counts (decisions.md D49d item 2): D32 / a2_variation_counts.py says 1,409 evaluable
rounds; gate1/A2_TIER_R4.json (a2_informativeness.counts) says 1,464 (all launches) and 1,211 (confirmatory).
Reads scorer output only (a2_scores_v2.jsonl) + the development-launch list; optionally the real A2 primary output JSON
to add the rounds that actually enter the fit.  Writes analysis/results/COUNTS_RECONCILE.json (+ .md written by hand
from it is NOT done: the .md is generated here too).
Usage: python -I counts_reconcile.py [A2_primary_output.json] [A2d_output.json]"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402
import a2_informativeness as INF  # noqa: E402

TAG = C.check_kind("real")
SC = C.A / "scores" / "a2_scores_v2.jsonl"
sc = [json.loads(x) for x in open(SC, encoding="utf-8")]
dev = C.dev_launch_ids()
rounds = defaultdict(list)
for r in sc:
    rounds[(r["launch_id"], r["round_id"])].append(r)


def tally(keys):
    R = {k: rounds[k] for k in keys}
    o = {"rounds": len(R), "launches": len({k[0] for k in R})}
    o["extraction_failed"] = sum(1 for v in R.values() if not v[0]["extract_ok"])
    o["zero_crux"] = sum(1 for v in R.values() if v[0]["extract_ok"] and v[0]["n_cruxes"] == 0)
    crux = {k: v for k, v in R.items() if v[0]["n_cruxes"]}
    o["with_ge1_crux"] = len(crux)
    o["ge1_crux_all4_E_missing"] = sum(1 for v in crux.values() if all(x["E"] is None for x in v))
    o["ge1_crux_some_but_not_all_E_missing"] = sum(1 for v in crux.values() if any(x["E"] is None for x in v) and any(x["E"] is not None for x in v))
    ev = {k: v for k, v in crux.items() if all(x["E"] is not None for x in v)}
    o["evaluable_all4_E__D32_definition"] = len(ev)
    o["rounds_with_ge1_nonmissing_E__A2_TIER_counts_definition"] = sum(1 for v in R.values() if any(x["E"] is not None for x in v))
    var = [k for k, v in ev.items() if len({x["E"] for x in v}) > 1]
    o["R_inf_all4_E"] = len(var)
    o["K_inf_all4_E"] = len({k[0] for k in var})
    varp = [k for k, v in R.items() if len({x["E"] for x in v if x["E"] is not None}) > 1]
    o["R_inf_A2_TIER_counts_definition"] = len(varp)
    o["K_inf_A2_TIER_counts_definition"] = len({k[0] for k in varp})
    return o


allk = list(rounds)
conf = [k for k in allk if k[0] not in dev]
res = {"gate_tag": TAG, "inputs": {"a2_scores_v2.jsonl": C.sha256_file(SC), "pilot_groups.jsonl": C.sha256_file(C.PILOT / "pilot_groups.jsonl")},
       "all_launches": tally(allk), "confirmatory_set": tally(conf)}
# reproduce a2_informativeness.counts() exactly on a statement table built from the same scores
st = pd.DataFrame([{"launch_id": r["launch_id"], "round_id": r["round_id"], "cand": int(r["cand"]),
                    "E": float("nan") if r["E"] is None else float(r["E"])} for r in sc])
res["a2_informativeness_counts_reproduced"] = {"all": INF.counts(st, "E"), "confirmatory": INF.counts(st[~st.launch_id.isin(dev)], "E")}
res["A2_TIER_R4_json"] = {k: json.loads((C.GATE / "A2_TIER_R4.json").read_text(encoding="utf-8"))[k]
                          for k in ("counts", "counts_including_development_launches")}
for i, f in enumerate(sys.argv[1:3]):
    j = json.loads(Path(f).read_text(encoding="utf-8"))
    res[["A2_primary_fit", "A2d_fit"][i]] = {"file": Path(f).name, "sha256": C.sha256_file(f), "n_rounds_in_fit": j["n_rounds"],
                                             "rounds_dropped_missing_E": j["rounds_dropped_missing_E"],
                                             "rounds_no_E_variation": j["rounds_no_E_variation"],
                                             "launches_with_E_variation": j["launches_with_E_variation"], "n_clusters": j["n_clusters"],
                                             "rater_rounds_dropped_all_tied": j["rater_rounds_dropped_all_tied"]}
outj = C.A / "results" / "COUNTS_RECONCILE.json"
outj.write_text(json.dumps(res, indent=1), encoding="utf-8")
C.write_sidecar(outj)
run_log.log_run(__file__, "real (scorer output only)", "n/a", [SC, C.PILOT / "pilot_groups.jsonl"] + sys.argv[1:3], str(outj),
                f"[{TAG}] evaluable-round count reconciliation")
print(json.dumps(res, indent=1))
