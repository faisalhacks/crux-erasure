# SHARE: what may be sent to the volunteer (R4, D37)

## Send exactly these two files, and nothing else

1. `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\r4\volunteer_packet.csv`
2. `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels_build\r4\VOLUNTEER_INSTRUCTIONS.md`

Both contain verbatim participant opinions: send privately, not to a public or shared location.
The volunteer is told nothing else (no hypothesis, no project name, no results).

## Never share (any of these)

- `P\FROZEN_RULES.md`, `P\BRIEF.md`, `P\decisions.md`, `P\status.md`, `P\PLAN.md`, `P\EXPERIMENTS.md` and any other project note
- Everything in `P\analysis\` (scores, scorer runs, N2 runs, specs, drafts) and `P\report\`
- Everything in `P\gate1\` (sample.json, item_key.csv, A2_TIER.json) and any results or drafts
- Keys: `labels_build\r4\key_volunteer.json`, `labels_build\r4\key_author.csv`, `labels_build\n2_packet_selection.json`
- Author packets: `labels_build\r4\packet_author_pass1.html`, `packet_author_pass2.html`, `TEMPLATE_author_pass1.csv`,
  `TEMPLATE_author_pass2.csv`, `LABELER_INSTRUCTIONS_author.md`
- `labels_build\r4\RUNS.md`, `labels_build\r4_build.py`, `r4_verify.py`, `READY.md`, `README.md`, the archive folder
  `labels_build\archive_void_preR4\`, and anything in `P\labels\`

(`P` = `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1`.)

## What the volunteer returns

- Exact file name: `volunteer_pass1.csv` (CSV, UTF-8)
- Exact columns, in this order, header row first, exactly 50 rows below it:
  `item_id,label,main_disagreement,comment,pass_started_utc`
- `item_id` unchanged from the packet (ids start with `v`). `label` is one of `HIDES`, `SHOWS`, `NO_DISAGREEMENT`,
  `UNSURE`. `pass_started_utc` = `YYYY-MM-DDTHH:MMZ`, same value on every row.
- The packet CSV has three extra text columns (`question`, `opinions`, `statement`). The volunteer instructions tell
  the volunteer to delete them before saving, so the returned file has the five columns above. Check the file
  before saving it; do not edit labels. A returned file with other columns is incomplete under FROZEN section 5
  and must be sent back to the volunteer to fix, not repaired by you or the pipeline.

## Where you save it (unchanged, exactly as received)

`C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels\volunteer_pass1.csv`

Saving any file into `labels\` freezes FROZEN_RULES (the first label file of any kind). If you want the two-human
design, `volunteer_pass1.csv` must be in `labels\` before, or together with, the completed `author_pass1.csv`
(FROZEN 6.0). The volunteer has no second pass.
