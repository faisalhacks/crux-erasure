"""Clean stop of an N3 scoring attempt that never got a container (D57 follow-up): release the harness reservation
(no GPU time was used) and write the $0 ACTUAL ledger row.  Never touches containers.
Usage: python -I n3_stop_clean.py <reservation_id> <attempt label> <note>"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "pilot_harness"))
sys.path.insert(0, str(HERE))
from budget import Budget  # noqa: E402
import scorer as S  # noqa: E402

rid, label, note = sys.argv[1], sys.argv[2], sys.argv[3]
b = Budget()
b.release(rid, "N3 attempt stopped: Modal never started a qwen3.8-27b container (/health 503, container list empty); no GPU time used")
b.close()
S.ledger_row(f"scorer N3 iteration-1 labels qwen3.8-27b v2 ACTUAL ({label})", "N3", "H100x1", "", 0.0, 2000,
             "orchestrator D57 + follow-up (own pilot T3-1-N3, cap $3)", note + "; HIDE_NOT_HUMAN_VALIDATED")
print("released", rid)
