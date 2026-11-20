# Gate-1 labelling packets (built, not yet released)

Built by `build_packets.py` per FROZEN_RULES.md sections 5 and 6.1. Verified by `verify_packets.py`.
No label exists. Nothing here was written to `P\labels\`. Seeds and data hash are in `P\analysis\RUNS.md`.

## Release gate (human)
FROZEN_RULES.md section 5 says packets are released only after `P\analysis\scorer_manifest.json` exists.
At build time it did not. Do not hand the packets to a labeler before it does.

## What each labeler receives (and nothing else)
| Labeler | Files to give |
|---|---|
| L1 (consultant, blind) | `packet_L1.html`, `TEMPLATE_L1.csv`, `LABELER_INSTRUCTIONS_L1.md` |
| L2 (author) | `packet_L2.html`, `TEMPLATE_L2.csv`, `LABELER_INSTRUCTIONS_L2.md` |

**Never give a labeler:** `key.json` (NOT for labelers: it links item ids to launches and duplicates),
this README, `build_packets.py`, `verify_packets.py`, `packet_L*.csv` (same content as the HTML),
or anything from `analysis\`, `decisions.md`, `BRIEF.md`, `FROZEN_RULES.md`. L1 must not be told the
hypothesis; this README and FROZEN_RULES.md describe the project, so keep them away from L1.

## How a labeler fills the CSV
1. Open the packet HTML. It has 44 items, one section each, shown with an `item_id`.
2. Open the template CSV in a text-safe editor (not one that reformats; keep UTF-8 and the header).
   It already lists the 44 `item_id` values, in packet order. Do not add, delete, rename or reorder columns.
3. For each item, fill the row with that `item_id`:
   - `label`: exactly one of `HIDES`, `SHOWS`, `NO_DISAGREEMENT`, `UNSURE`. Case and surrounding spaces are ignored; no other word is accepted.
   - `main_disagreement`: a few words, at most 4 points, most important first, or `none`.
   - `comment`: optional.
4. Leave no `label` blank. Do not copy an earlier answer for a repeated-looking item; label each on its own.
5. Do not discuss rows with the other labeler until both files are in. Do not use any AI tool.

## Saving (done by the human, not by any agent)
Save the finished file as `C:\Users\intel\Downloads\OU\projects\_apart_intel\t3_1\labels\L1.csv`
(or `L2.csv`): UTF-8, header `item_id,label,main_disagreement,comment`, 44 rows. The first such file
freezes FROZEN_RULES.md. The pipeline never writes, fills or corrects these files.

## Design as built
- 60 distinct statements, one per launch, drawn from 721 eligible launches outside the 150 development launches.
- 20 shared (same `item_id` in both packets), 20 unique to L1, 20 unique to L2.
- Per labeler: 2 shared + 2 unique items repeated under fresh `item_id`s, at least 10 rows after the first appearance (44 rows each).
- Opinions are sorted by participant id (ids not shown), numbered from 1, untruncated.

## Implementation choices not fixed by FROZEN_RULES.md (accepted by orchestrator)
1. Item-id naming seed 20261130 (random 8 hex characters). FROZEN fixes no id rule; the seed affects no sampling.
2. Spacing of repeats: FROZEN says "at least 10 rows after". A repeat is impossible if its original is in the last 10 rows, so the 40-row shuffle was redrawn from the same seeded rng until every repeated original sat in rows 1-30 (L1: 4 draws, L2: 1 draw). Final order is still fully determined by seeds 20261117 / 20261118.
3. Frozen paths `P\gate1\sample.json` and `P\gate1\item_key.csv` were derived from `key.json` by `write_frozen_paths.py` (no redraw; 88 key rows = 44 per labeler). `gate1packets` was not written.
4. The ranking columns were read only to apply eligibility rule 2(e); no ranking, rating or score is joined to any item. Counts reproduce the frozen ones (1,960 rounds, 871 launches, 9,501 rater rows).
5. Privacy (ETHICS_REVIEW D-1, D-6): packets contain verbatim participant opinions, which can include age, town, religion or job. Keep them off shared drives and public links; do not quote them in the paper without the quoting policy. The CSV collects only the frozen label fields.
