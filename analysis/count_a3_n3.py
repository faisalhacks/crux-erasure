"""FR s8 data-availability counts for A3 and N3 (no scores, no ranks used as outcomes).
A3: rounds that pass every FR s2 filter EXCEPT 'all candidates MODEL_MEDIATOR', and contain >= 1 HUMAN_MEDIATOR and
    >= 1 MODEL_MEDIATOR candidate.  N3: FR s2-eligible rounds that also have iteration_index == 1 candidates.
Both counted in launches of the confirmatory set (development launches excluded, FR s8 [R4]) and, as a side figure,
including them.  Filter logic copied from pilots/T3_1/s03_prep.py (the FR s2 filter of record).
Usage: python -I count_a3_n3.py OUT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pyarrow.parquet as pq  # noqa: E402
import common as C  # noqa: E402
import run_log  # noqa: E402

out = Path(sys.argv[1])
if C.sha256_file(C.SRC_PARQUET) != C.FROZEN_SRC_SHA:
    sys.exit("source parquet hash mismatch")
COLS = ["launch_id", "round_id", "iteration_index", "own_opinion.metadata.provenance",
        "other_opinions.metadata.provenance", "critique.metadata.provenance", "candidates.text",
        "candidates.metadata.id", "candidates.metadata.provenance", "rankings.candidate_ids",
        "rankings.numerical_ranks", "rankings.metadata.provenance", "ratings.metadata.provenance"]
df = pq.read_table(C.SRC_PARQUET, columns=COLS).to_pandas()
bot_crit = set(map(tuple, df.loc[df["critique.metadata.provenance"] == "BOT_CITIZEN", ["launch_id", "round_id"]].values))
it1 = df[(df.iteration_index == 1)]
it1_with_cands = set()
for (lid, rid), g in it1.groupby(["launch_id", "round_id"], sort=False):
    if any(len(list(c if c is not None else [])) > 0 for c in g["candidates.text"]):
        it1_with_cands.add((lid, rid))
it0 = df[df.iteration_index == 0]
a3_rounds, n3_rounds, elig = [], [], 0
for (lid, rid), g in it0.groupby(["launch_id", "round_id"], sort=True):
    if (lid, rid) in bot_crit:
        continue
    bot = False
    for _, r in g.iterrows():
        if r["own_opinion.metadata.provenance"] != "HUMAN_CITIZEN" or any(p != "HUMAN_CITIZEN" for p in r["other_opinions.metadata.provenance"]):
            bot = True
    if bot:
        continue
    r0 = g.iloc[0]
    cands, cids, cprov = list(r0["candidates.text"]), list(r0["candidates.metadata.id"]), list(r0["candidates.metadata.provenance"])
    if len(cands) != 4:
        continue
    if any((c or "").strip() == "Citizen's Jury" or len((c or "").split()) < 15 for c in cands):
        continue
    nr = 0
    for _, r in g.iterrows():
        if r["rankings.metadata.provenance"] != "HUMAN_CITIZEN" or r["ratings.metadata.provenance"] != "HUMAN_CITIZEN":
            continue
        if list(r["rankings.candidate_ids"]) != cids:
            continue
        ranks = list(map(int, r["rankings.numerical_ranks"]))
        if len(ranks) != 4 or -1 in ranks:
            continue
        nr += 1
    if nr < 3:
        continue
    allmodel = all(p == "MODEL_MEDIATOR" for p in cprov)
    if allmodel:
        elig += 1
        if (lid, rid) in it1_with_cands:
            n3_rounds.append(lid)
    elif "HUMAN_MEDIATOR" in cprov and "MODEL_MEDIATOR" in cprov:
        a3_rounds.append(lid)
dev = C.dev_launch_ids()
res = {"eligible_rounds_check": elig, "expected_eligible_rounds": C.FROZEN_COUNTS["n_rounds"],
       "A3": {"rounds_confirmatory": sum(1 for l in a3_rounds if l not in dev), "launches_confirmatory": len({l for l in a3_rounds if l not in dev}),
              "rounds_incl_dev": len(a3_rounds), "launches_incl_dev": len(set(a3_rounds)), "floor_launches": 30},
       "N3": {"rounds_confirmatory": sum(1 for l in n3_rounds if l not in dev), "launches_confirmatory": len({l for l in n3_rounds if l not in dev}),
              "rounds_incl_dev": len(n3_rounds), "launches_incl_dev": len(set(n3_rounds)), "floor_launches": 30},
       "source_parquet_sha256": C.FROZEN_SRC_SHA}
for k in ("A3", "N3"):
    res[k]["qualifies"] = res[k]["launches_confirmatory"] >= 30
out.write_text(json.dumps(res, indent=1), encoding="utf-8")
C.write_sidecar(out)
run_log.log_run(__file__, "real-counts (no scores, no ranks)", "n/a", [C.SRC_PARQUET, C.PILOT / "pilot_groups.jsonl"], str(out),
                f"FR s8 A3/N3 availability: A3 {res['A3']['launches_confirmatory']} launches, N3 {res['N3']['launches_confirmatory']} launches (confirmatory)")
print(json.dumps(res, indent=1))
