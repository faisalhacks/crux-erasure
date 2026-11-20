# V5b verification packet part 2: runs (decisions.md D62)

## 2026-11-16T08:41Z selection + extraction script fixed (before any model call)
- select_b.py sha256 be2d1919ecfd590d6afcbffc893cdf1e13f5bd75f6aaeaf3519eaf7970ee177d (no random draw; walks the existing ordered reserves of v5/selection.json 2555c211...). selection_b.json sha256 e866c2499435818c6e48678e041b62f62ca35bc26e22f1764dd092687b37d7f1; deterministic (two runs identical).
- Selected: the 19 R4 pass-1 reserve originals in reserve order; N2 qwen3.8-27b uid 39, gemma4-12b uid 49, ministral3-14b ministral3-14b|5197d600ee317e90ccefd83a76d36107|SAT-COMMON|0, phi4-14b uid 44, llama3.1-8b uid 42; extra: the R4 N2 reserve is exhausted, so it comes from the ministral reserve: ministral3-14b|ca5d87cf11b1f32b170320f4afc2fa67|NEU-COMMON|0.
- Skipped while walking: used in v5 2, strict markdown 32, launch taken 0. Replacement queues left: R4 N2 0, ministral 139 (originals: none left).
- extract_b.py sha256 8dd783607fe15bbf9eee6fde8ddc5facc76916b83bb6d4dcf22c39aea5524e30 (imports v5/extract.py, same X1 cb25581a..., seeds 0/1, same validator). labels\ listing: empty.

## 2026-11-16T08:56Z extraction: STOPPED (app did not serve)
- ESTIMATE ledger row 08:41Z ($1.391 worst case, cap $1.5). The gptoss-120b session never became ready: 0 model calls in 892 s; the 900 s wall limit (inside the 15-min serve limit) fired and the run stopped. No cold-start time recorded.
- ACTUAL ledger row 08:56Z: $1.3768 = harness list-price figure (rate x elapsed + scaledown), an UPPER BOUND, not a billing figure; a no-cost NOTE row says so. Post-run poll: 0 containers (ours or others); nothing stopped; container list at 08:57Z: empty.
- Not retried: the serve limit was hit, a retry would exceed the $1.5 cap and the 09:15Z deadline. No extraction_b.json, no packet, no key, no packet_v5b_scores.jsonl. labels\ listing: empty; nothing opened.
