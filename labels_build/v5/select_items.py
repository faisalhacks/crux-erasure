"""V5 step-3 verification packet: ITEM SELECTION ONLY (decisions.md D49 / D49b).  Deterministic, no model call.

Population: the R4 author pass-1 sample (labels_build/r4/key_author.csv, rows pass == pass1: 38 originals + 12 N2,
dev launches already excluded by FR 6.1).  key_author.csv is read only to map items; its score/rank-free columns are
the only ones used (kind, launch_id, round_id, cand, generator, cell, uid).

Rule (seed 20261116, one random.Random stream, used in this exact order):
  1. N2 items whose statement contains markdown are excluded BEFOREHAND (see MD below), before any draw.
  2. originals: canonical order = sorted by R4 uid; perm = rng.sample(all 38); selected = perm[:19],
     ordered reserve = perm[19:].
  3. N2, one per generator, generators in the fixed D49b order GENS: perm = rng.sample(eligible items of that
     generator, all); selected = perm[0].
     EXCEPTION ministral3-14b (decisions.md D49c): both R4 pass-1 ministral items contain markdown, so this slot is
     drawn instead from ALL N2 full_ext ministral3-14b generations (sample 0, finish_reason stop), same eligibility
     as n2_packet_selection.json: launch not a development launch, launch and round not in the gate-1 sample
     (gate1/sample.json), plus markdown-free and launch not used by any R4 pass-1 N2 item (distinct launches).
     Pool sorted by job_id; perm = rng.sample(pool, all) (drawn at the ministral position of GENS);
     selected = perm[0]; ordered ministral reserve = perm[1:].
  4. N2 extra item: remaining eligible R4 N2 (sorted by uid); perm = rng.sample(remaining, all); selected = perm[0];
     ordered N2 reserve = perm[1:].
  Replacement (applied by extract.py, never here): an original slot takes the next unused original reserve item;
  a generator slot takes the first unused N2 reserve item OF THE SAME GENERATOR (the ministral slot: the next
  ministral reserve item); the extra slot takes the first unused N2 reserve item of any generator.
Output: labels_build/v5/selection.json (ids/metadata only; no text, no score, no rank).
Run:  C:/Users/intel/miniconda3/python.exe -I select_items.py   (renamed from select.py under D49e: it shadowed the
stdlib `select` module; logic unchanged except the added MD_STRICT, which this script does not use)
"""
import csv
import hashlib
import json
import random
import re
from pathlib import Path

P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
LB = P / "labels_build"
OUT = LB / "v5"
KEY = LB / "r4" / "key_author.csv"
SEL = LB / "n2_packet_selection.json"
DEV = P.parent / "pilots" / "T3_1" / "pilot_groups.jsonl"
GEN_FILES = sorted((P / "analysis" / "n2_runs" / "full_k1").glob("gens_*.jsonl")) + \
            sorted((P / "analysis" / "n2_runs" / "full_ext").glob("gens_*.jsonl"))
SEED = 20261116
GENS = ["qwen3.8-27b", "gemma4-12b", "ministral3-14b", "phi4-14b", "llama3.1-8b"]   # D49b order
N_ORIG, N_N2 = 19, 6
MINI = "ministral3-14b"
MINI_FILE = P / "analysis" / "n2_runs" / "full_ext" / "gens_ministral3-14b.jsonl"
G1 = P / "gate1" / "sample.json"
# markdown: '**', any '#', or a list bullet line ('-', '*', '+', '\u2022' or 'N.' / 'N)' followed by a space)
MD_RE = re.compile(r"\*\*|#|^[ \t]*(?:[-*+\u2022]|\d+[.)])[ \t]", re.M)
# D49e stricter filter (used by redraw_d49e.py and verify.py; MD_RE above is kept unchanged so that selection.json,
# drawn under D49b/D49c, stays reproducible): *x*, **x**, _x_, any backtick, any '#', bullet or numbered-list line.
MD_STRICT = re.compile(r"\*[^*\s][^*\n]*?\*|\*\*|(?<![0-9A-Za-z])_[^_\s][^_\n]*?_(?![0-9A-Za-z])|`|#"
                       r"|^[ \t]*(?:[-*+\u2022]|\d+[.)])[ \t]", re.M)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def has_markdown(t):
    return bool(MD_RE.search(t or ""))


def has_markdown_strict(t):
    return bool(MD_STRICT.search(t or ""))


def n2_texts():
    """job_id -> statement text (same rule as r4_build.py: duplicates must agree)."""
    texts = {}
    for f in GEN_FILES:
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                texts.setdefault(d["job_id"], set()).add(d["text"])
    return texts


def job_ids():
    sel = json.loads(SEL.read_text(encoding="utf-8"))
    return {(it["generator"], it["round_id"], it["cell"]): it["job_id"] for it in sel["items"]}


def main():
    rows = [r for r in csv.DictReader(open(KEY, encoding="utf-8")) if r["pass"] == "pass1"]
    assert len(rows) == 50, len(rows)
    dev = {json.loads(l)["launch_id"] for l in open(DEV, encoding="utf-8") if l.strip()}
    items = []
    jid = job_ids()
    texts = n2_texts()
    for r in rows:
        it = dict(uid=int(r["uid"]), kind=r["kind"], launch_id=r["launch_id"], round_id=r["round_id"],
                  cand=int(r["cand"]), generator=r["generator"], cell=r["cell"], r4_item_id=r["item_id"])
        assert it["launch_id"] not in dev, it
        if it["kind"] == "n2":
            it["job_id"] = jid[(it["generator"], it["round_id"], it["cell"])]
            ts = texts[it["job_id"]]
            assert len(ts) == 1, it["job_id"]
            it["markdown"] = has_markdown(next(iter(ts)))
        items.append(it)
    items.sort(key=lambda x: x["uid"])
    orig = [x for x in items if x["kind"] == "original"]
    n2 = [x for x in items if x["kind"] == "n2"]
    assert len(orig) == 38 and len(n2) == 12
    excluded = [x for x in n2 if x["markdown"]]
    elig = [x for x in n2 if not x["markdown"]]
    for g in GENS:
        if g != MINI:
            assert any(x["generator"] == g for x in elig), f"STOP: no markdown-free N2 item for generator {g}"
    assert not any(x["generator"] == MINI for x in elig)       # D49c premise

    # ministral pool (D49c)
    g1 = json.loads(G1.read_text(encoding="utf-8"))["sample"]
    g1_l = {x["launch_id"] for v in g1.values() for x in v}
    g1_r = {x["round_id"] for v in g1.values() for x in v}
    r4_n2_l = {x["launch_id"] for x in n2}
    mrows = [json.loads(l) for l in open(MINI_FILE, encoding="utf-8") if l.strip()]
    n_mini_md = sum(has_markdown(r["text"]) for r in mrows)
    mpool = sorted((r for r in mrows if r["sample"] == 0 and str(r["finish_reason"]) == "stop" and r["text"].strip()
                    and r["launch_id"] not in dev and r["launch_id"] not in g1_l and r["round_id"] not in g1_r
                    and r["launch_id"] not in r4_n2_l and not has_markdown(r["text"])), key=lambda r: r["job_id"])
    assert len({r["job_id"] for r in mpool}) == len(mpool)
    mitems = [dict(uid=None, kind="n2", launch_id=r["launch_id"], round_id=r["round_id"], cand=-1, generator=MINI,
                   cell=f"{r['sys_prompt']}-{r['user_prompt']}", r4_item_id="", job_id=r["job_id"],
                   source="full_ext_ministral_D49c") for r in mpool]

    rng = random.Random(SEED)
    perm_o = rng.sample(orig, len(orig))
    sel_o, res_o = perm_o[:N_ORIG], perm_o[N_ORIG:]
    sel_n2 = []
    res_mini = []
    for g in GENS:
        if g == MINI:
            perm_m = rng.sample(mitems, len(mitems))
            sel_n2.append(dict(perm_m[0], slot=f"gen:{g}"))
            res_mini = perm_m[1:]
            continue
        cand = [x for x in elig if x["generator"] == g]
        pick = rng.sample(cand, len(cand))[0]
        sel_n2.append(dict(pick, slot=f"gen:{g}", source="r4_pass1"))
    taken = {x["uid"] for x in sel_n2}
    rem = [x for x in elig if x["uid"] not in taken]
    perm_r = rng.sample(rem, len(rem))
    sel_n2.append(dict(perm_r[0], slot="extra", source="r4_pass1"))
    res_n2 = [dict(x, source="r4_pass1") for x in perm_r[1:]]
    for x in sel_o + res_o:
        x["slot"] = "original"
        x["source"] = "r4_pass1"
    assert len(sel_o) == N_ORIG and len(sel_n2) == N_N2

    def strip(x):
        return {k: v for k, v in x.items() if k != "markdown"}
    out = dict(
        spec="decisions.md D49/D49b; rule in select.py docstring",
        seed=SEED, generator_order=GENS, markdown_regex=MD_RE.pattern,
        inputs={str(p.relative_to(P.parent) if P.parent in p.parents else p): sha256_file(p)
                for p in [KEY, SEL, DEV, G1] + GEN_FILES},
        select_py_sha256=sha256_file(Path(__file__)),
        n2_excluded_markdown=[dict(uid=x["uid"], generator=x["generator"]) for x in excluded],
        ministral_full_ext_outputs=len(mrows), ministral_full_ext_with_markdown=n_mini_md,
        ministral_pool_eligible=len(mpool),
        selected=[strip(x) for x in sel_o + sel_n2],
        reserve_original=[strip(x) for x in res_o],
        reserve_n2=[strip(x) for x in res_n2],
        reserve_ministral=[strip(x) for x in res_mini],
    )
    OUT.mkdir(exist_ok=True)
    (OUT / "selection.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print("selected", len(sel_o), "+", len(sel_n2), "| N2 excluded for markdown:", len(excluded),
          "| reserve orig", len(res_o), "reserve n2", len(res_n2))
    print("selected uids:", [x["uid"] for x in sel_o + sel_n2])
    print("n2 slots:", [(x["slot"], x["uid"]) for x in sel_n2])
    print("reserve n2:", [(x["uid"], x["generator"]) for x in res_n2])
    print("ministral full_ext outputs with markdown:", n_mini_md, "of", len(mrows), "| eligible pool", len(mpool),
          "| reserve", len(res_mini))


if __name__ == "__main__":
    main()
