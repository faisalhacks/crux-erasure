"""N2 text-FORM counters per cell for a finished generation run: n, words, over-cap rate (> 150 words).
No scoring, no content reading. Usage: python -I n2_overcap.py [run_dir]"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
run = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "n2_runs" / "full_k1"
CAP = 150
out = {}
for f in sorted(run.glob("gens_*.jsonl")):
    rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    for cell in sorted({(r["sys_prompt"], r["user_prompt"]) for r in rows}):
        rs = [r for r in rows if (r["sys_prompt"], r["user_prompt"]) == cell]
        w = sorted(r["n_words"] for r in rs)
        out[f"{rs[0]['model']}|{cell[0]}-{cell[1]}"] = dict(
            n=len(rs), mean_words=round(sum(w) / len(w), 1), median_words=w[len(w) // 2], max_words=w[-1],
            over_cap=sum(x > CAP for x in w), over_cap_rate=round(sum(x > CAP for x in w) / len(w), 3))
(run / "overcap_report.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    print(k, v)
