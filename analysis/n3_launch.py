"""Launcher for analysis/n3_score.py: sets PILOT_ENV_FILE (proxy token file written by modal_serving/setup_secrets.py)
and dumps all thread tracebacks every 120 s to stderr so a stall is visible. argv passed through."""
import faulthandler
import os
import runpy
import sys
from pathlib import Path

os.environ.setdefault("PILOT_ENV_FILE", str(Path.home() / ".modal_vllm.env"))
faulthandler.dump_traceback_later(120, repeat=True)
script = r"C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\analysis\n3_score.py"
sys.argv = [script] + sys.argv[1:]
sys.path.insert(0, str(Path(script).parent))
runpy.run_path(script, run_name="__main__")
