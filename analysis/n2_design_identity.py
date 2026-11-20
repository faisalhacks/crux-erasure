"""Design-identity check for the N2 extension (spec Amendment 2): same rounds, same messages across generators.
Compares the extension's job set with the existing full_k1 run. Reads no model output text. Writes n2_runs/design_identity.json.
Rendered-prompt capture (chat template per model) is NOT done here; it needs a vLLM /tokenize call."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import n2_grid as n  # noqa: E402

EXT = ["ministral3-14b", "phi4-14b", "llama3.1-8b"]
full = json.loads((n.OUT / "full_k1" / "plan.json").read_text(encoding="utf-8"))
rounds = n.draw_rounds(250, n.MASTER_SEED)
rid = n.hashlib.sha256(",".join(g["round_id"] for g in rounds).encode()).hexdigest()
serving = n.serving_info(EXT)
jobs = n.build_jobs(rounds, EXT, 1, n.MASTER_SEED, serving)
ref = {}
for f in ("gens_gemma4-12b.jsonl", "gens_qwen3.8-27b.jsonl"):
    for l in (n.OUT / "full_k1" / f).read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        ref.setdefault((r["round_id"], f"{r['sys_prompt']}-{r['user_prompt']}"), set()).add(r["msg_sha256"])
bad = [j["job_id"] for j in jobs if ref.get((j["round_id"], f"{j['sys_prompt']}-{j['user_prompt']}")) != {j["msg_sha256"]}]
out = dict(round_ids_sha256_ext=rid, round_ids_sha256_full_k1=full["round_ids_sha256"], rounds_equal=rid == full["round_ids_sha256"],
           ext_jobs=len(jobs), msg_sha256_mismatches=len(bad), same_seed=full["seed"] == n.MASTER_SEED,
           same_decoding=(full["temperature"], full["top_p"], full["top_k"], full["max_tokens"]) == (n.TEMPERATURE, n.TOP_P, n.TOP_K, n.MAX_TOKENS),
           same_prompts=(full["system"], full["user_task"], full["user_format"]) == (n.SYSTEM, n.USER_TASK, n.USER_FORMAT),
           rendered_prompt_check="NOT DONE (needs vLLM /tokenize per model)")
out["PASS"] = out["rounds_equal"] and out["msg_sha256_mismatches"] == 0 and out["same_seed"] and out["same_decoding"] and out["same_prompts"]
(n.OUT / "design_identity.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
