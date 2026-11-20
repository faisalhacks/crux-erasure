"""Append one ACTUAL ledger row for a scorer session whose process was interrupted before it could write it.
Usage (python -I): ledger_add_actual.py <job label> <exp> <actual_usd> <timeout_s> <notes>
The actual comes from pilot_harness/ledger.jsonl (modal_session settle row), not from a guess."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scorer as S  # noqa: E402

job, exp, actual, timeout, notes = sys.argv[1:6]
S.ledger_row(job, exp, "H100x1", "", float(actual), int(timeout), "scorer runner (fix round, cap $2)", notes)
print("ok; cumulative", S.ledger_last_cum())
