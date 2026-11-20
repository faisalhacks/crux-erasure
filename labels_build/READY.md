# READY: verification packet (D49, D49b–e, D51). Published 2026-11-16T01:23Z

The R4 packets in `labels_build\r4\` are VOID. Do not use them.

## What to open (folder `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\v5\`)
1. `INSTRUCTIONS_verification.md`: read first (short)
2. `packet_verification.html`: open in a browser; 25 items
3. `TEMPLATE_author_verification.csv`: fill in this file

For each item answer two questions with `yes` or `no`:
- Q1. Do these quotes disagree?
- Q2. Does the statement acknowledge this disagreement? (answer it even when Q1 is no)

Columns: `item_id,q1_quotes_disagree,q2_statement_acknowledges,comment,pass_started_utc`
(`comment` optional; `pass_started_utc` = when you started, `YYYY-MM-DDTHH:MMZ`, the same on every row.)
Work from the packet only, with no AI tools. Don't open `key_verification.csv` or anything else in v5 or the project.

## Save as (exactly)
`C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels\author_verification.csv`

Saving it freezes FROZEN_RULES. Save once, complete (25 rows).

## Time-out (D51)
T_ready = 2026-11-16T01:23Z. If the file is not in `labels\` by **2026-11-16T01:53Z**, step 3 is recorded as
NOT DONE. Three LLMs then answer the same questions (supplementary, never called human), and gate 1 is decided by
the participant presence check alone. A file arriving later is reported as a separate post-gate check.

## Hashes
packet_verification.html 5371023f3314136853d6f2097bffd3e8cc22c2ed7e06500466552741524bbe34
TEMPLATE_author_verification.csv c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331
(verify.py: ALL CHECKS PASS, 34 checks; build log in v5\RUNS.md)
