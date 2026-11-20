#!/usr/bin/env bash
# Real-data runs under GATE1_RESULT.json rules R5 / VALIDATED_PRESENCE (stamp HIDE_NOT_HUMAN_VALIDATED).
# Run from P.  Each script writes a versioned JSON (<stem>__<utc>.json + .sha256) and a RUNS.md row.
set -u
PY="C:/Users/intel/miniconda3/python.exe -I"
IN=analysis/scores/a2_long_real.parquet
O=analysis/results/runs
PA=analysis/results/params
mkdir -p "$O"
run () { echo "=== $*"; $PY "$@" 2>&1 | grep -v -i "pynvml\|FutureWarning"; }
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2_primary.json --note "A2 primary (confirmatory set)"
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2b.json --params $PA/A2b.json --note "A2b own-opinion similarity"
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2d.json --params $PA/A2d.json --note "A2d"
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2e.json --params $PA/A2e.json --note "A2e E_pos (SIDED shown)"
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2f.json --params $PA/A2f.json --note "A2f vagueness"
run analysis/a2_within_round.py --input $IN --kind real --out $O/A2g.json --params $PA/A2g.json --note "A2g E_w member-weighted"
run analysis/a2i_informative.py --input $IN --kind real --out $O/A2i.json
run analysis/n1_winner_vs_mean.py --input $IN --kind real --out $O/N1.json --note "N1 [R3] adjusted (family test alpha)"
run analysis/n4_minority.py --input $IN --kind real --out $O/N4.json
