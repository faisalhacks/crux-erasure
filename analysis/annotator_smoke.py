"""FR 6.8 'Format try-out': gpt-oss-120b LLM annotator, at most 20 calls on DEVELOPMENT-launch rounds, to check the output parses.
NOT run on packet items. Reads only: question, opinions, candidate text of development rounds (raters dropped at load).
Input = the volunteer version of the labeler instructions verbatim (labels_build/r4/VOLUNTEER_INSTRUCTIONS.md, from 'You will see'
to 'Do not leave `label` blank.'), then the item (question, numbered opinions, statement), then the one added format line.
Decoding: temperature 0, seed 0, one retry with seed 1; reasoning left at the served default; max_tokens 6000 (>= 4096 per
serve_vllm.py note). Usage (python -I): annotator_smoke.py [--n 10] --confirm-launch
Output: analysis/annotator_smoke/{items.json, results.jsonl, summary.json}. Never writes to labels/ or gate1/llm_annotator/."""
import argparse
import asyncio
import json
import os
import random
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["MODAL_ENDPOINTS"] = str(HERE.parent / "serving" / "endpoints.json")
import scorer as S  # noqa: E402

ALIAS = "gptoss-120b"
TOK = {"HIDES", "SHOWS", "NO_DISAGREEMENT", "UNSURE"}
FORMAT_LINE = 'Return JSON only: {"main_disagreement": "<your points, or none>", "label": "HIDES" or "SHOWS" or "NO_DISAGREEMENT" or "UNSURE"}'
MAX_TOK = 6000
OUT = HERE / "annotator_smoke"
SEED_PICK = 20261140


def instructions():
    t = (HERE.parent / "labels_build" / "r4" / "VOLUNTEER_INSTRUCTIONS.md").read_text(encoding="utf-8")
    a = t.index("You will see a question")
    end = "Do not leave `label` blank."
    b = t.index(end) + len(end)
    return t[a:b]


def item_text(g, cand):
    ops = "\n".join(f"{i + 1}. {t}" for i, (_, t) in enumerate(sorted(g["opinions"].items())))
    return f"Question: {g['question']}\n\nOpinions:\n{ops}\n\nStatement:\n{g['candidates'][cand]}"


def build_prompt(g, cand):
    return instructions() + "\n\n---\n\n" + item_text(g, cand) + "\n\n" + FORMAT_LINE


def parse(text):
    js = S.parse_json_obj(text)
    if not js or str(js.get("label", "")).strip().upper() not in TOK or not isinstance(js.get("main_disagreement"), str):
        return None
    return dict(label=str(js["label"]).strip().upper(), main_disagreement=js["main_disagreement"])


async def run(a):
    rounds = S.load_rounds(S.DEV_GROUPS)                         # development launches only; `raters` dropped
    ks = sorted(rounds)
    random.Random(SEED_PICK).shuffle(ks)
    items = [dict(launch_id=k[0], round_id=k[1], cand=0) for k in ks[:a.n]]
    prompts = [build_prompt(rounds[(i["launch_id"], i["round_id"])], i["cand"]) for i in items]
    OUT.mkdir(exist_ok=True)
    (OUT / "items.json").write_text(json.dumps(dict(seed=SEED_PICK, items=items, prompt_sha256=S.sha256_text(prompts[0]),
                                                    instructions_sha256=S.sha256_text(instructions()), format_line=FORMAT_LINE), indent=1), encoding="utf-8")
    if not a.confirm_launch:
        raise SystemExit("REFUSED: needs --confirm-launch")
    ep = S.modal_endpoints()[ALIAS]
    rate = S.modal_container_rate(ep["gpu"], int(ep.get("n_gpu", 1)), float(ep.get("cpu", 0)), float(ep.get("memory_mib", 0)) / 1024)
    max_s = 1800
    worst = round(rate * (max_s + ep["scaledown_s"] + 15), 3)
    assert worst < 5.0, worst
    S.ledger_row(f"LLM annotator smoke {ALIAS} ({a.n} dev items, <=2 attempts) ", "annotator-format-tryout", "H100x1", worst, "", max_s,
                 "annotator runner (smoke under $5, orchestrator D36/D38/D40)",
                 f"ESTIMATE row before launch; worst-case reservation ${worst} ({max_s} s + scaledown), expected ~$0.8 with first cold start; dev items only")
    llm = S.LLM(pilot="T3-1-LLMann-smoke", pilot_cap=5.0, timeout_s=600.0, concurrency={"modal": 10})
    recs, sess = [], None
    S.BASELINE_IDS.update(re.findall(r"ta-[0-9A-Za-z]+", S.container_check().get("stdout_tail", "") or ""))
    t0 = time.time()
    try:
        async with llm.modal_session(ALIAS, max_seconds=max_s) as s:
            pend = list(range(len(items)))
            res = {i: dict(attempts=[], parsed=None) for i in pend}
            for seed in (0, 1):
                if not pend:
                    break
                jobs = [dict(provider="modal", model=ALIAS, messages=[{"role": "user", "content": prompts[i]}], max_tokens=MAX_TOK,
                             temperature=0.0, seed=seed, extra={}) for i in pend]
                out = await llm.run_many(jobs, stop_on_budget=True)
                nxt = []
                for i, r in zip(pend, out):
                    if isinstance(r, Exception):
                        res[i]["attempts"].append(dict(seed=seed, error=str(r)[:200]))
                        nxt.append(i)
                        continue
                    p = parse(r["text"])
                    res[i]["attempts"].append(dict(seed=seed, text=r["text"], finish_reason=r.get("finish_reason"), usage=r.get("usage"), parse_ok=p is not None))
                    if p:
                        res[i]["parsed"] = p
                    else:
                        nxt.append(i)
                pend = nxt
        sess = dict(billed_s=s.billed_s, session_cost_usd=round(s.cost_usd, 4), cold_start_s=s.cold_start_s)
    finally:
        await llm.aclose()
        cc = S.container_wait_empty(ALIAS)
        (OUT / "container_check.json").write_text(json.dumps(cc, indent=1), encoding="utf-8")
    with open(OUT / "results.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for i, it in enumerate(items):
            f.write(json.dumps(dict(**it, **res[i]), ensure_ascii=False) + "\n")
    labs = [res[i]["parsed"]["label"] for i in res if res[i]["parsed"]]
    summ = dict(items=len(items), valid=len(labs), failed=len(items) - len(labs), labels={k: labs.count(k) for k in sorted(set(labs))},
                first_attempt_failures=sum(1 for i in res if res[i]["attempts"] and not res[i]["attempts"][0].get("parse_ok")),
                truncated=sum(1 for i in res for x in res[i]["attempts"] if x.get("finish_reason") == "length"),
                thinking_text_in_content=sum(1 for i in res for x in res[i]["attempts"] if "<think" in (x.get("text") or "") or "analysis" in (x.get("text") or "")[:20].lower()),
                completion_tokens=[x.get("usage") for i in res for x in res[i]["attempts"][:1]][:3], session=sess, wall_s=round(time.time() - t0, 1),
                container_check={k: v for k, v in cc.items() if k != "stdout_tail"}, prompt_sha256=S.sha256_text(prompts[0]))
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if sess:
        S.ledger_row(f"LLM annotator smoke {ALIAS} ACTUAL", "annotator-format-tryout", "H100x1", "", sess["session_cost_usd"], max_s,
                     "annotator runner (smoke under $5, orchestrator D36/D38/D40)",
                     f"ACTUAL list-price session cost; wall {summ['wall_s']} s; cold start {sess['cold_start_s']} s; containers after: own rows {cc.get('own_rows_final')}, stopped by id {cc.get('stopped_by_id')}")
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--confirm-launch", action="store_true")
    asyncio.run(run(ap.parse_args()))
