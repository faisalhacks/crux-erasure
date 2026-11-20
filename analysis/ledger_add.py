"""Append one ledger row (ESTIMATE or ACTUAL) for a Modal job that scorer.py does not book itself (deploy/download jobs).
Usage (python -I): ledger_add.py <job> <exp> <gpu> <estimate_usd|-> <actual_usd|-> <timeout_s> <notes>
Actuals must come from a measured source (harness ledger or Modal billing), never a guess."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scorer as S  # noqa: E402

job, exp, gpu, est, act, timeout, notes = sys.argv[1:8]
S.ledger_row(job, exp, gpu, "" if est == "-" else float(est), "" if act == "-" else float(act), int(timeout),
             "scorer runner (A4/annotator smoke, each under $5, no approval needed per orchestrator D36/D38/D40)", notes)
print("ok; cumulative", S.ledger_last_cum())
