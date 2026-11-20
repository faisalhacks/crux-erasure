"""Seeded, outcome-blind selection of the 12 N2 packet items (spec Amendment 2, section 10).
Uses ONLY ids (generator, cell, round, launch). Reads no generated text, no score, no flag.
Writes P/labels_build/n2_packet_selection.json. Run once, BEFORE the extension outputs exist.
  python -I n2_packet_selection.py
"""
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import n2_grid as n  # noqa: E402  (importing runs no generation)

P = n.P
OUT = P / "labels_build" / "n2_packet_selection.json"
SEED = 20261116
GENERATORS = ["gemma4-12b", "qwen3.8-27b", "ministral3-14b", "phi4-14b", "llama3.1-8b"]
CELL_IDS = [f"{s}-{u}" for s, u in n.CELLS]


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; the selection is written once and never redrawn.")
    rng = random.Random(f"N2-packet|{SEED}")
    gens = GENERATORS[:]
    rng.shuffle(gens)                       # position 0,1 get 3 items, positions 2,3,4 get 2
    cells = CELL_IDS[:]
    rng.shuffle(cells)
    n_items = [3, 3, 2, 2, 2]
    pairs = []                              # cyclic Latin-style: generator i takes cells i, i+1, ... (no repeat)
    for i, g in enumerate(gens):
        for j in range(n_items[i]):
            pairs.append((g, cells[(i + j) % 5]))
    assert len(pairs) == 12 and len(set(pairs)) == 12
    # eligible rounds: in the N2 sample, outside gate-1 sample, the 150 development launches
    main_rounds = n.draw_rounds(250, n.MASTER_SEED)
    dev_l = {json.loads(l)["launch_id"] for l in open(n.DEV_GROUPS, encoding="utf-8")}
    g1 = json.loads((P / "gate1" / "sample.json").read_text(encoding="utf-8"))["sample"]
    g1_l = {x["launch_id"] for v in g1.values() for x in v}
    g1_r = {x["round_id"] for v in g1.values() for x in v}
    elig = [g for g in main_rounds if g["launch_id"] not in dev_l and g["launch_id"] not in g1_l and g["round_id"] not in g1_r]
    elig.sort(key=lambda g: g["round_id"])
    rng.shuffle(elig)
    used_l, items = set(), []
    for slot, (g, c) in enumerate(pairs):
        pick = next(r for r in elig if r["launch_id"] not in used_l and r["round_id"] not in {i["round_id"] for i in items})
        used_l.add(pick["launch_id"])
        s_, u_ = c.split("-")
        items.append(dict(slot=slot, generator=g, cell=c, round_id=pick["round_id"], launch_id=pick["launch_id"],
                          question_id=pick["question_id"], job_id=f"{g}|{pick['round_id']}|{c}|0"))
    doc = dict(seed=SEED, rule="generators shuffled: first two get 3 items, others 2; cells shuffled; generator i takes cells i.. cyclic (no generator-cell repeat); "
                              "each item from a distinct round and launch of the 250-round N2 sample, outside the 150 development launches and the gate-1 sample; "
                              "rounds drawn by seed from the sorted eligible list, never by text, score or flag",
               generator_order=gens, cell_order=cells, n_eligible_rounds=len(elig),
               n2_round_ids_sha256=hashlib.sha256(",".join(g["round_id"] for g in main_rounds).encode()).hexdigest(),
               selection_script_sha256=n.sha256_file(Path(__file__)), items=items,
               note="Selection fixed before any extension text exists. gemma4-12b and qwen3.8-27b texts already exist (full_k1); the rule used ids only.")
    OUT.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(json.dumps(items, indent=0)[:2500])
    print("eligible", len(elig), "sha256", n.sha256_file(OUT))


if __name__ == "__main__":
    main()
