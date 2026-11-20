"""Part 2 (v5b) item selection, decisions.md D62 (same procedure as D49b-e).  Deterministic; no random draw: it walks
the EXISTING ordered reserves in labels_build/v5/selection.json (seed 20261116).  No model call; no score read.
  originals: the 19 R4 pass-1 reserve originals in reserve order.
  N2, generator slots in the D49b order: qwen3.8-27b, gemma4-12b, phi4-14b, llama3.1-8b take the first item of their
     generator in the ordered R4 N2 reserve; ministral3-14b takes the first item of the ordered ministral full_ext
     reserve.  extra: the first remaining item of the R4 N2 reserve; if that reserve is exhausted, the first remaining
     item of the ministral reserve (the only other existing ordered reserve).
  every N2 candidate must pass the strict D49e markdown filter (select_items.MD_STRICT) and the D49b filter.
  every candidate must not duplicate a v5 item (same round or same statement) and N2 launches must be distinct from
     every v5 and v5b launch; skipped candidates are counted.
  replacements (extract_b.py): the next unused candidate of the same rule; if none, the slot is left empty and logged.
Output: labels_build/v5b/selection_b.json.   Run: C:/Users/intel/miniconda3/python.exe -I select_b.py
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
P = Path(r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1")
V5 = P / "labels_build" / "v5"
V5B = P / "labels_build" / "v5b"
GENS = ["qwen3.8-27b", "gemma4-12b", "ministral3-14b", "phi4-14b", "llama3.1-8b"]
MINI = "ministral3-14b"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location("v5_" + name, V5 / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SI = load("select_items")


def main():
    sel = json.loads((V5 / "selection.json").read_text(encoding="utf-8"))
    ext = json.loads((V5 / "extraction.json").read_text(encoding="utf-8"))
    v5_rounds = {x["round_id"] for x in ext["items"]}
    v5_stmts = {x["job_id"] if x["kind"] == "n2" else f"{x['round_id']}#cand{x['cand']}" for x in ext["items"]}
    v5_launch = {x["launch_id"] for x in ext["items"]}
    texts = SI.n2_texts()

    def n2_ok(r):
        t = next(iter(texts[r["job_id"]]))
        return not SI.has_markdown(t) and not SI.has_markdown_strict(t)

    def fresh(r):
        sid = r.get("job_id") or f"{r['round_id']}#cand{r['cand']}"
        return r["round_id"] not in v5_rounds and sid not in v5_stmts

    skipped = {"used_in_v5": 0, "markdown_strict": 0, "launch_taken": 0}

    def eligible_n2(q, taken_l):
        out = []
        for r in q:
            if not fresh(r):
                skipped["used_in_v5"] += 1
            elif not n2_ok(r):
                skipped["markdown_strict"] += 1
            elif r["launch_id"] in v5_launch or r["launch_id"] in taken_l:
                skipped["launch_taken"] += 1
            else:
                out.append(r)
        return out

    origs = [dict(r, slot="original") for r in sel["reserve_original"] if fresh(r)]
    assert len(origs) == 19, len(origs)
    r4q = eligible_n2(sel["reserve_n2"], set())
    miniq = eligible_n2(sel["reserve_ministral"], set())
    chosen, taken_l = [], set()

    def take(q, pred):
        for i, r in enumerate(q):
            if pred(r) and r["launch_id"] not in taken_l:
                q.pop(i)
                taken_l.add(r["launch_id"])
                return r
        return None
    for g in GENS:
        r = take(miniq, lambda r: True) if g == MINI else take(r4q, lambda r, g=g: r["generator"] == g)
        assert r is not None, f"STOP: no candidate for gen:{g}"
        chosen.append(dict(r, slot=f"gen:{g}"))
    r = take(r4q, lambda r: True)
    extra_from = "reserve_n2"
    if r is None:
        r = take(miniq, lambda r: True)
        extra_from = "reserve_ministral (R4 N2 reserve exhausted)"
    assert r is not None
    chosen.append(dict(r, slot="extra"))
    # remaining ordered candidates, for replacements (launch-distinct check is re-applied at use time)
    out = dict(spec="decisions.md D62 (procedure D49b-e); rule in select_b.py docstring", base_selection_sha256=sha(V5 / "selection.json"),
               v5_extraction_sha256=sha(V5 / "extraction.json"), select_items_py_sha256=sha(V5 / "select_items.py"),
               select_b_py_sha256=sha(Path(__file__)), extra_slot_from=extra_from, skipped=skipped,
               selected=origs + chosen, replacement_queue_r4_n2=r4q, replacement_queue_ministral=miniq)
    V5B.mkdir(exist_ok=True)
    (V5B / "selection_b.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print("selected", len(origs), "+", len(chosen), "| extra from", extra_from, "| skipped", skipped)
    print([(c["slot"], c.get("uid"), c["job_id"]) for c in chosen])
    print("replacement queues: r4_n2", len(r4q), "ministral", len(miniq))


if __name__ == "__main__":
    main()
