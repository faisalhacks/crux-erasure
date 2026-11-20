"""SYNTHETIC test fixtures (NOT human labels) for the [R4] gate (gate1.py), written only under analysis/testdata/DUMMY_<name>/
(never under P/labels or P/gate1).  build(name, ...) writes, for one scenario:
  DUMMY_<name>/labels/author_pass1.csv (50 rows: 38 original + 12 n2), author_pass2.csv (20 repeats = 15 + 5, optional),
                      volunteer_pass1.csv (50 rows, own opaque ids, different order; optional), ADJ.csv (two-human only)
  DUMMY_<name>/gate/  item_key.csv, scores.csv (38 originals), n2check_scores.jsonl (12 N2), FREEZE.json, llm_annotator/llm_labels.csv
Knobs: acc = author accuracy vs the latent truth, r = per-item self-consistency, vol_acc, ai_acc, adj_acc, timing of pass 2.
The latent truth is random; nothing here relates to any real item, score or ranking."""
import datetime
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "testdata"
TOKS = ["HIDES", "SHOWS", "NO_DISAGREEMENT"]
T1 = datetime.datetime(2026, 11, 20, 10, 0, tzinfo=datetime.timezone.utc)   # fictitious pass-1 modification time


def noisy(truth, acc, p_unsure, rng):
    out = []
    for t in truth:
        if rng.random() < p_unsure:
            out.append("UNSURE")
            continue
        h = t if rng.random() < acc else 1 - t
        out.append("HIDES" if h else TOKS[1 + int(rng.random() < 0.3)])
    return out


def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%MZ")


def write_labels(path, ids, labels, started):
    pd.DataFrame({"item_id": ids, "label": labels, "main_disagreement": "x", "comment": "",
                  "pass_started_utc": ts(started)}).to_csv(path, index=False)


def build(name, design="single_labeler", acc=0.97, r=0.97, vol_acc=0.95, ai_acc=0.88, adj_acc=0.95, seed=7, p_unsure=0.03,
          with_pass2=True, pass2_start_gap_min=120, pass2_mtime_gap_min=150, vol_complete=True, llm_acc=0.9):
    rng = np.random.default_rng(seed)
    root = OUT / f"DUMMY_{name}"
    if root.exists():
        shutil.rmtree(root)
    lab, gate = root / "labels", root / "gate"
    (gate / "llm_annotator").mkdir(parents=True)
    lab.mkdir(parents=True)
    ids = [f"P1_{i:03d}" for i in range(50)]
    kind = ["original"] * 38 + ["n2"] * 12
    truth = (rng.random(50) < 0.5).astype(int)
    T = dict(zip(ids, truth))
    a1 = noisy(truth, acc, p_unsure, rng)
    A1 = dict(zip(ids, a1))
    order = list(rng.permutation(50))
    write_labels(lab / "author_pass1.csv", [ids[i] for i in order], [A1[ids[i]] for i in order], T1 - datetime.timedelta(minutes=60))
    os.utime(lab / "author_pass1.csv", (T1.timestamp(), T1.timestamp()))
    key = [(i, "1", k, "dl", "dr", 0, "gen" if k == "n2" else "", "cell" if k == "n2" else "", "") for i, k in zip(ids, kind)]
    # pass 2: 15 originals + 5 n2 repeated under fresh ids
    rep = list(rng.choice(ids[:38], 15, replace=False)) + list(rng.choice(ids[38:], 5, replace=False))
    p2ids = [f"P2_{j:03d}" for j in range(20)]
    flip = {"HIDES": "SHOWS", "SHOWS": "HIDES", "NO_DISAGREEMENT": "HIDES", "UNSURE": "SHOWS"}
    l2 = [A1[s] if rng.random() < r else flip[A1[s]] for s in rep]
    for j, s in zip(p2ids, rep):
        key.append((j, "2", kind[ids.index(s)], "dl", "dr", 0, "", "", s))
    if with_pass2:
        o = rng.permutation(20)
        write_labels(lab / "author_pass2.csv", [p2ids[i] for i in o], [l2[i] for i in o], T1 + datetime.timedelta(minutes=pass2_start_gap_min))
        t2 = (T1 + datetime.timedelta(minutes=pass2_mtime_gap_min)).timestamp()
        os.utime(lab / "author_pass2.csv", (t2, t2))
    # volunteer: own ids, own order
    vids = [f"V_{i:03d}" for i in range(50)]
    perm = list(rng.permutation(50))
    vl = noisy(truth, vol_acc, p_unsure, rng)
    for j, i in zip(vids, perm):
        key.append((j, "vol", kind[i], "dl", "dr", 0, "", "", ids[i]))
    if design == "two_human":
        vl_rows = [(vids[j], vl[perm[j]]) for j in range(50)]
        if not vol_complete:
            vl_rows[3] = (vl_rows[3][0], "")
        write_labels(lab / "volunteer_pass1.csv", [x for x, _ in vl_rows], [y for _, y in vl_rows], T1 - datetime.timedelta(minutes=30))
        V = {ids[perm[j]]: vl[perm[j]] for j in range(50)}
        diff = [i for i in ids if V[i] != A1[i]]
        adj = noisy([T[i] for i in diff], adj_acc, 0.0, rng)
        pd.DataFrame({"item_id": diff, "adj_label": adj, "reason": "dummy"}).to_csv(lab / "ADJ.csv", index=False)
    pd.DataFrame(key, columns=["item_id", "pass", "kind", "launch_id", "round_id", "cand", "generator", "cell", "dup_of"]).to_csv(
        gate / "item_key.csv", index=False)
    E = [float(np.clip((0.75 if (t if rng.random() < ai_acc else 1 - t) else 0.25) + rng.normal(0, 0.08), 0, 1)) for t in truth]
    sc = pd.DataFrame({"item_id": ids[:38], "E": [f"{e:.3f}" for e in E[:38]], "n_cruxes": 2})
    sc.loc[3, "E"] = ""   # one parse failure
    sc.to_csv(gate / "scores.csv", index=False)
    with open(gate / "n2check_scores.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for i, e in zip(ids[38:], E[38:]):
            f.write(json.dumps({"item_id": i, "E": round(e, 3), "n_cruxes": 2}) + "\n")
    ll = noisy(truth, llm_acc, 0.02, rng)
    pd.DataFrame({"item_id": ids, "label": ll, "main_disagreement": "x"}).assign(label=lambda d: d.label.where(d.item_id != ids[5], "")).to_csv(
        gate / "llm_annotator" / "llm_labels.csv", index=False)
    (gate / "FREEZE.json").write_text(json.dumps({"author_pass1_mtime_utc": T1.isoformat().replace("+00:00", "Z"),
                                                   "author_pass1_sha256": __import__("hashlib").sha256((lab / "author_pass1.csv").read_bytes()).hexdigest()}),
                                      encoding="utf-8")
    return root


if __name__ == "__main__":
    build("single_good", "single_labeler")
    build("two_good", "two_human")
    print(sorted(p.name for p in OUT.glob("DUMMY_*")))
