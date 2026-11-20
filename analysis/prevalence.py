"""FR s7.3 prevalence quantities (pre-specified descriptive; no ranks read), [R4](a): confirmatory set only.
From scorer 1 over eligible rounds with >= 1 crux:
  share_E_eq_1        share of statements with E = 1 (statements with E present)
  share_any_VISIBLE   share of statements with >= 1 VISIBLE crux (statements with E present)
  label_share_<L>     share of crux labels equal to L, over all (statement x crux) labels
  R_inf_over_rounds   informative rounds / rounds of the A2 analysis set (>= 1 crux, no missing E; FR 7.1)
Interval: FR s7 [R2] method of record applied to a mean = intercept-only OLS, wild cluster bootstrap-t, Rademacher,
launch clusters, B = 10,000, seed 20261128 (FR 7.3), via common.mean_ci.  Each unit (statement, label, round) has
equal weight.  Usage: python -I prevalence.py OUT.json [--include-dev]"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402

TAG = C.check_kind("real")
SEED, B = 20261128, 10000
out = Path(sys.argv[1])
incl = "--include-dev" in sys.argv
SC = C.A / "scores" / "a2_scores_v2.jsonl"
sc = [json.loads(x) for x in open(SC, encoding="utf-8")]
dev = C.dev_launch_ids()
if not incl:
    sc = [r for r in sc if r["launch_id"] not in dev]
rounds = defaultdict(list)
for r in sc:
    rounds[(r["launch_id"], r["round_id"])].append(r)
crux = {k: v for k, v in rounds.items() if v[0]["n_cruxes"]}


def ci(vals, launches):
    codes, nc = C.cluster_codes(np.asarray(launches))
    r = C.mean_ci(np.asarray(vals, float), codes, nc, B, SEED, 0.05, "wild")
    r.update(n_units=len(vals), n_launches=int(nc))
    return r


stm = [x for v in crux.values() for x in v if x["E"] is not None]
res = {"gate_tag": TAG, "set": "SENSITIVITY: including the development launches" if incl else "CONFIRMATORY (development launches excluded)",
       "B": B, "seed": SEED, "interval": "wild cluster bootstrap-t (intercept-only), launch clusters",
       "rounds_with_ge1_crux": len(crux), "statements_with_E": len(stm),
       "statements_missing_E_in_crux_rounds": sum(1 for v in crux.values() for x in v if x["E"] is None)}
res["share_E_eq_1"] = ci([float(x["E"] == 1.0) for x in stm], [x["launch_id"] for x in stm])
res["share_any_VISIBLE"] = ci([float("VISIBLE" in (x["labels"] or [])) for x in stm], [x["launch_id"] for x in stm])
labs = [(x["launch_id"], lb) for x in stm for lb in x["labels"]]
for L in ("VISIBLE", "SIDED", "BLENDED", "OMITTED"):
    res["label_share_" + L] = ci([float(lb == L) for _, lb in labs], [l for l, _ in labs])
ev = {k: v for k, v in crux.items() if all(x["E"] is not None for x in v)}
res["R_inf_over_rounds"] = ci([float(len({x["E"] for x in v}) > 1) for v in ev.values()], [k[0] for k in ev])
out.parent.mkdir(parents=True, exist_ok=True)
res["inputs"] = {"a2_scores_v2.jsonl": C.sha256_file(SC), "pilot_groups.jsonl": C.sha256_file(C.PILOT / "pilot_groups.jsonl")}
vp = C.write_result(out, res, __file__, "real", SEED, [SC, C.PILOT / "pilot_groups.jsonl"],
                    f"FR 7.3 prevalence ({res['set']}) B={B} wild intercept-only")
print(vp)
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ("est", "lo", "hi", "n_units")} if "est" in v else v) for k, v in res.items()}, indent=1))
