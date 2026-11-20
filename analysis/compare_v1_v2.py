"""Outcome-free comparison of scorer v1 vs v2 (E1 silence fix). Reads only extractions/scores + opinions/candidates
(via scorer.load_rounds, which drops `raters`). Usage (python -I): compare_v1_v2.py dev|gate|show <set> <n>...
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scorer as S  # noqa: E402

SETS = {
    "dev": dict(v1_ext=HERE / "scorer_runs/probe_v1/extractions.jsonl", v1_sc=HERE / "scorer_runs/probe_v1/scores.jsonl",
                v2_ext=HERE / "scorer_runs/probe/extractions.jsonl", v2_sc=HERE / "scorer_runs/probe/scores.jsonl", groups=S.DEV_GROUPS),
    "gate": dict(v1_ext=HERE / "scores/gate1_extractions_v1.jsonl", v1_sc=HERE / "scores/gate1_scores_v1.jsonl",
                 v2_ext=HERE / "scores/gate1_extractions.jsonl", v2_sc=HERE / "scores/gate1_scores.jsonl", groups=S.ALL_GROUPS),
}


def rd(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")]


def side_stats(ext):
    n_cx = n_empty = n_single_vs_many = n_all = n_over = 0
    sizes = []
    for r in ext:
        for c in (r["cruxes"] or []):
            n_cx += 1
            a, b = len(c["members_a"]), len(c["members_b"])
            if a == 0 or b == 0:
                n_empty += 1
            if min(a, b) == 1 and max(a, b) >= 3:
                n_single_vs_many += 1
            if a + b >= 5:
                n_all += 1
            sizes.append(a + b)
    return dict(cruxes=n_cx, empty_side=n_empty, one_vs_3plus=n_single_vs_many, covers_ge5=n_all,
               mean_members_assigned=round(sum(sizes) / len(sizes), 2) if sizes else None)


def within_round_var(sc, key="E"):
    by = defaultdict(list)
    for r in sc:
        if r[key] is not None:
            by[(r["launch_id"], r["round_id"])].append(r[key])
    return sum(1 for v in by.values() if len(set(v)) > 1), len(by)


def summarize(name, ext, sc):
    from collections import Counter
    labs = Counter(l for r in sc for l in (r["labels"] or []))
    stm = len(sc)
    e = [r["E"] for r in sc if r["E"] is not None]
    out = dict(version=name, rounds=len(ext), extract_ok=sum(1 for r in ext if r["ok"]), zero_crux_rounds=sum(1 for r in ext if r["ok"] and r["n_cruxes"] == 0),
               crux_count_dist=dict(sorted(Counter(r["n_cruxes"] for r in ext if r["ok"]).items())), side=side_stats(ext), statements=stm,
               label_ok_fail=sum(1 for r in sc if r["label_ok"] is False), label_counts=dict(labs),
               E_values=dict(sorted(Counter(e).items())), ai_pos=sum(1 for r in sc if r["ai_binary"] is True),
               ai_neg=sum(1 for r in sc if r["ai_binary"] is False), ai_missing=sum(1 for r in sc if r["ai_binary"] is None))
    out["within_round_E_varies(rounds_varying,rounds_with_E)"] = within_round_var(sc, "E")
    return out


def main():
    mode = sys.argv[1]
    if mode in SETS:
        s = SETS[mode]
        r = {v: (rd(s[v + "_ext"]), rd(s[v + "_sc"])) for v in ("v1", "v2")}
        res = {v: summarize(v, *r[v]) for v in r}
        # crux-count change per round
        c1 = {(x["launch_id"], x["round_id"]): x["n_cruxes"] for x in r["v1"][0] if x["ok"]}
        c2 = {(x["launch_id"], x["round_id"]): x["n_cruxes"] for x in r["v2"][0] if x["ok"]}
        both = set(c1) & set(c2)
        res["paired_rounds"] = len(both)
        res["rounds_fewer_cruxes"] = sum(1 for k in both if c2[k] < c1[k])
        res["rounds_more_cruxes"] = sum(1 for k in both if c2[k] > c1[k])
        res["rounds_same"] = sum(1 for k in both if c2[k] == c1[k])
        res["rounds_became_zero"] = sum(1 for k in both if c1[k] > 0 and c2[k] == 0)
        res["rounds_ceased_zero"] = sum(1 for k in both if c1[k] == 0 and c2[k] > 0)
        # E_pos (SIDED counted as shown) variation, informational
        for v in ("v1", "v2"):
            by = defaultdict(list)
            for x in r[v][1]:
                if x["labels"]:
                    by[(x["launch_id"], x["round_id"])].append(sum(1 for l in x["labels"] if l not in ("VISIBLE", "SIDED")) / len(x["labels"]))
            res[v + "_within_round_Epos_varies"] = (sum(1 for q in by.values() if len(set(q)) > 1), len(by))
        # gate: AI binary changes on the same statement
        if mode == "gate":
            b1 = {(x["launch_id"], x["round_id"], x["cand"]): x for x in r["v1"][1]}
            b2 = {(x["launch_id"], x["round_id"], x["cand"]): x for x in r["v2"][1]}
            res["gate_binary_changes"] = sum(1 for k in b1 if b1[k]["ai_binary"] != b2[k]["ai_binary"])
            res["gate_binary_pos_to_neg"] = sum(1 for k in b1 if b1[k]["ai_binary"] is True and b2[k]["ai_binary"] is False)
            res["gate_binary_neg_to_pos"] = sum(1 for k in b1 if b1[k]["ai_binary"] is False and b2[k]["ai_binary"] is True)
        print(json.dumps(res, indent=1, default=str))
    elif mode == "show":
        s = SETS[sys.argv[2]]
        rounds = S.load_rounds(s["groups"])
        e1, e2 = {(x["launch_id"], x["round_id"]): x for x in rd(s["v1_ext"])}, {(x["launch_id"], x["round_id"]): x for x in rd(s["v2_ext"])}
        keys = sorted(e1)
        for i in [int(a) for a in sys.argv[3:]]:
            k = keys[i]
            g = rounds[k]
            print("=" * 100)
            print(f"[{i}] round {k[1][:8]}\nQ: {g['question']}")
            for j, (_, t) in enumerate(sorted(g["opinions"].items())):
                print(f"  OP{j + 1}: {t}")
            for v, e in (("v1", e1), ("v2", e2)):
                x = e.get(k)
                print(f"  -- {v}: {x['n_cruxes'] if x and x['ok'] else 'FAIL'} cruxes")
                for c in (x["cruxes"] or []) if x else []:
                    print(f"     * {c['issue']}\n        A{c['members_a']}: {c['side_a']}\n        B{c['members_b']}: {c['side_b']}")


main()
