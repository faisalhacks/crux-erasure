# V5 verification packet: runs

## 2026-11-16T00:55Z select.py: STOPPED before selection (no model call, nothing launched)
- Spec: decisions.md D49/D49b. Seed 20261116 (not consumed: the script stops before the first draw).
- Inputs (sha256): key_author.csv 4c6fc75109b9ec96560cc68fd7c58f0982ba7b61b43a742370be5fa73ed84a0b;
  n2_packet_selection.json 7709a6e59604d3733b03305c2e0d309b09bfd8e238b1e0e7d85ccaef5ffbfe87;
  full_k1/gens_gemma4-12b.jsonl 942746ca306abce84c31b06b1604a8b1c8d32c813fb7db5b453dfce82397c36a;
  full_k1/gens_qwen3.8-27b.jsonl 99ed998c7011b4a4ca66eb60b9ca7864aeecc206aa4559bdb7156539d7a933fe;
  full_ext/gens_llama3.1-8b.jsonl 7089573fd7fae49803abd9f376cfd6f11419da9e43ded7aff40d84ac6e2a5431;
  full_ext/gens_ministral3-14b.jsonl 1b40228c3915114b9691aa694c20eb0012430348a2018153da0c67508258aaee;
  full_ext/gens_phi4-14b.jsonl fab609a13fa631e787210121393cd9ce83c2f84fd47cb9ae969dc3bf05ef067a.
  select.py 985bab8c5ae8110d8645a9e42e0a1d68cf71acad240e492bc2e45ba42635c122.
- Markdown rule (applied to the 12 R4 pass-1 N2 statements before any draw): `**`, any `#`, or a list-bullet line.
- Result: markdown in 2 of 12 N2 items, and they are BOTH ministral3-14b items (R4 uids 46 and 47, both literal `**`
  bold; uid 46 has 16 hits, uid 47 has 2). The other 10 have no hits. So the R4 pass-1 sample has no markdown-free
  ministral3-14b item, and D49b "1 per generator" cannot be met from the R4 pass-1 sample as specified.
- Script stops at its assert. No selection.json, no prompt, no Modal launch, no ledger row. labels\ was empty
  (directory listing only). Needs an orchestrator decision before anything else runs.

## 2026-11-16T00:56Z select.py rerun under D49c: SELECTION RECORDED (before any model call)
- Seed 20261116 (one random.Random stream: originals, then N2 generators in D49b order with the ministral slot drawn
  from the D49c pool at its position, then the extra N2 item). Rule: select.py docstring. Deterministic: two runs gave
  the same selection.json.
- select.py sha256 b22d0787d10ac22d16d5a937821c413d7b8c4cae627ec1d342273adc513ae0c1;
  selection.json sha256 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3.
- Extra inputs vs the STOP entry: gate1/sample.json b26bd3e753f0eac50948ec52cb6a0a67f6dd3d3fc5503b209029e18686b00709;
  pilots/T3_1/pilot_groups.jsonl 085d78472d9df42894a065f279656260a35931c3176d9dc5d23c7a38a6868daa (others unchanged, listed above).
- R4 N2 items excluded for markdown: 2 (uids 46, 47, both ministral3-14b).
- Ministral3-14b full_ext outputs containing markdown (D49c, count only): 992.
- Selected: originals (R4 uid) 13, 37, 25, 21, 32, 20, 0, 16, 6, 22, 31, 24, 30, 35, 33, 18, 11, 26, 7;
  N2: qwen3.8-27b uid 40, gemma4-12b uid 48, ministral3-14b job ministral3-14b|b581bf2ccc05c503b906cce875ff9351|ACC-COMMON|0
  (full_ext, D49c), phi4-14b uid 45, llama3.1-8b uid 43, extra uid 41.
- Ordered reserves (full lists in selection.json): originals 19; R4 N2 5 (49, 38, 39, 42, 44); ministral 174.

## 2026-11-16T00:58Z extraction prompt and script fixed (before launch)
- X1_prompt.md sha256 cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 (neutral: two most strongly conflicting quotes; if none conflict, the two most different and conflict_found=false; JSON).
- extract.py sha256 21fd15f5a2936bca227a97357603b14df4df60fef299fbab9da3cb291b804f1b. gpt-oss-120b (alias gptoss-120b), temperature 0, seed 0, retry seed 1, max_tokens 6000, session cap 1200 s, task cap $3.
- Dry run: 25 items loadable (all human-only rounds, >=2 opinions). Validator unit-tested offline on synthetic strings.

## 2026-11-16T01:01Z launch attempt 1 aborted before launch (no Modal session, no ledger row, $0)
- The pre-launch baseline `modal container list` hung (inherited stdin in a background shell) and timed out at 120 s; script exited before the ESTIMATE row and before any model call.
- Fix: container list/stop now run with stdin closed and `--json` (untruncated app name match pilot-vllm-gptoss-120b). Prompt, selection and validation unchanged. extract.py sha256 now 4d56bed7dc26894d358a7ec873ddf7d71d46dbdf3ea34e23d02662d39f3b0c83.

## 2026-11-16T01:04Z launch attempt 2 aborted before launch (no Modal session, no ledger row, $0)
- Same hang. Cause found: the child `python -m modal` started with cwd=labels_build/v5 imported v5/select.py in place of the stdlib `select` module. Fix: children run `python -I -m modal ...` and extract.py chdirs to P (no .py files there). Prompt, selection and validation unchanged. extract.py sha256 now f6a5a49e05591bb08a97473372eb487b9e572e8605ddc943df9d47c3b88e031f.

## 2026-11-16T01:13Z verify.py: ALL CHECKS PASS

| file | sha256 |
|---|---|
| packet_verification.html | 0ef08cadb692ba147f0b8e91db79c4a3072c9c60a6ed7ad44e107b7ba208319c |
| TEMPLATE_author_verification.csv | c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331 |
| INSTRUCTIONS_verification.md | d3048dd63c69f71022a217b516f1c9dc5885b06dffd1e14ff9552010ee928b45 |
| key_verification.csv | d3c97cdc835ce4602a21d53ef4fde644a70d0d1c6378d74c2769c48fe69bac25 |
| selection.json | 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3 |
| extraction.json | ebb7f7ee4b9fc759e285ee7198c22eda15a06019ce6a3c244662c6cfae4154f2 |
| extraction_attempts.jsonl | 5fa85b0f38b2c825b1643e4523c7c96bc7c815d6464f5f2da36849565ff243f5 |
| container_check.json | 3b80027eebd2c1e90c80c553c352402659bac0658641302fd6754afbf4df56e5 |
| X1_prompt.md | cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 |
| select.py | b22d0787d10ac22d16d5a937821c413d7b8c4cae627ec1d342273adc513ae0c1 |
| extract.py | f6a5a49e05591bb08a97473372eb487b9e572e8605ddc943df9d47c3b88e031f |
| build_packet.py | b99388a2a0dc8728e85ef94bd76131b3914560c73ef0b0b35e385f37870320e5 |
| verify.py | 88e6402efb9ae059d839f308b3a24027ddbfaee91cd5d0396610859307af75ff |

## 2026-11-16T01:13Z extraction attempt 3: done
- 27 calls (25 first attempts, 1 retry with seed 1, 1 replacement first attempt); 0 truncated; 25/25 valid; quotes located by the model's opinion numbers in all 25 (search fallback 0).
- Replacements: 1. Slot gen:qwen3.8-27b: qwen3.8-27b|e3f4f02fceaab4c68b1bdb15ff7feac7|NEU-COMMON|0 (R4 uid 40) failed seed 0 and seed 1 (quote A not an exact substring), replaced by the first qwen item in the ordered N2 reserve, qwen3.8-27b|0d038cbd781dae39fbfb327e537b3e8b|ACC-DIS|0, valid on seed 0.
- conflict_found=false: 8 (kept; valid no-disagreement probes).
- Cost: $0.6543 list price (ESTIMATE $1.794 worst case; cap $3); ledger ESTIMATE 01:04Z and ACTUAL 01:12Z.
- Containers: own container ta-01M7GY56MRTAREJ094B942RTDR seen in 8 polls, then gone at 141 s (scaled down itself); nothing stopped; baseline 0, other rows 0.
- Packet order seed "20261116:v5-order" (build_packet.py).

## 2026-11-16T01:13Z verify.py: ALL CHECKS PASS

| file | sha256 |
|---|---|
| packet_verification.html | 0ef08cadb692ba147f0b8e91db79c4a3072c9c60a6ed7ad44e107b7ba208319c |
| TEMPLATE_author_verification.csv | c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331 |
| INSTRUCTIONS_verification.md | d3048dd63c69f71022a217b516f1c9dc5885b06dffd1e14ff9552010ee928b45 |
| key_verification.csv | d3c97cdc835ce4602a21d53ef4fde644a70d0d1c6378d74c2769c48fe69bac25 |
| selection.json | 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3 |
| extraction.json | ebb7f7ee4b9fc759e285ee7198c22eda15a06019ce6a3c244662c6cfae4154f2 |
| extraction_attempts.jsonl | 5fa85b0f38b2c825b1643e4523c7c96bc7c815d6464f5f2da36849565ff243f5 |
| container_check.json | 3b80027eebd2c1e90c80c553c352402659bac0658641302fd6754afbf4df56e5 |
| X1_prompt.md | cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 |
| select.py | b22d0787d10ac22d16d5a937821c413d7b8c4cae627ec1d342273adc513ae0c1 |
| extract.py | f6a5a49e05591bb08a97473372eb487b9e572e8605ddc943df9d47c3b88e031f |
| build_packet.py | b99388a2a0dc8728e85ef94bd76131b3914560c73ef0b0b35e385f37870320e5 |
| verify.py | 88e6402efb9ae059d839f308b3a24027ddbfaee91cd5d0396610859307af75ff |

## 2026-11-16T01:16Z D49e fix: before launch
- Renamed select.py -> select_items.py (it shadowed the stdlib `select` module). Logic unchanged; added MD_STRICT/has_markdown_strict (D49e), which selection does not use. Re-running select_items.py into a temp dir reproduces selection.json exactly except the recorded script hash. selection.json NOT regenerated (still 2555c211...). References updated in verify.py (load select_items) and an extract.py comment.
- select_items.py sha256 b3fb8fb21a4e75247504b27685df9c1d28abf03083a82fb3375a9fcf51cc92b2; redraw_d49e.py sha256 7b6f02bd13754c56c9e49a2d0189686a4ffda523ff68daa1bef39241a2ee09bc; extract.py sha256 65fcefe2bb27a2cde4916d5c95248cce9199a92bcd370ea4abfa719d5c52d70d; verify.py sha256 b367e744e6cf96cb042e1f97f4b8795f4a033fde651eced8168c9d00fa0290a3.
- Strict filter (D49e): *x*, any **, _x_ (not inside words), any backtick, any #, bullet or numbered-list line. On the 6 N2 slots: only gen:ministral3-14b fails (single-asterisk italics); the other 5 pass.
- Ministral3-14b full_ext outputs containing markdown, corrected (strict): 1052 (was 992 under the D49b filter).
- Ordered ministral reserve walk: positions 1-2 fail the strict filter; first passing = position 3, ministral3-14b|2bd3303580e4b73789206c080e5aa52a|ACC-COMMON|0. 32 of the 174 reserve items fail the strict filter.
- labels\ empty (listing only).

## 2026-11-16T01:21Z verify.py: ALL CHECKS PASS

| file | sha256 |
|---|---|
| packet_verification.html | 5371023f3314136853d6f2097bffd3e8cc22c2ed7e06500466552741524bbe34 |
| TEMPLATE_author_verification.csv | c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331 |
| INSTRUCTIONS_verification.md | d3048dd63c69f71022a217b516f1c9dc5885b06dffd1e14ff9552010ee928b45 |
| key_verification.csv | edcf5eb34038ab8d55b720ecfe574b3a549f5d36d0b4b4ef235909a16250545e |
| selection.json | 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3 |
| extraction.json | 71adf8bd07c8f9967849c45b6486a13b0fadd34f922a96aa97a2fdde4d44bcab |
| extraction_attempts.jsonl | 3c45c17d45f0bb87c873bbe7894ef4db3fe55067f0b3097766154d08b8f78ada |
| container_check.json | 3b80027eebd2c1e90c80c553c352402659bac0658641302fd6754afbf4df56e5 |
| X1_prompt.md | cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 |
| select_items.py | b3fb8fb21a4e75247504b27685df9c1d28abf03083a82fb3375a9fcf51cc92b2 |
| extract.py | 65fcefe2bb27a2cde4916d5c95248cce9199a92bcd370ea4abfa719d5c52d70d |
| redraw_d49e.py | 7b6f02bd13754c56c9e49a2d0189686a4ffda523ff68daa1bef39241a2ee09bc |
| build_packet.py | b99388a2a0dc8728e85ef94bd76131b3914560c73ef0b0b35e385f37870320e5 |
| verify.py | b367e744e6cf96cb042e1f97f4b8795f4a033fde651eced8168c9d00fa0290a3 |

## 2026-11-16T01:21Z verify.py: ALL CHECKS PASS

| file | sha256 |
|---|---|
| packet_verification.html | 5371023f3314136853d6f2097bffd3e8cc22c2ed7e06500466552741524bbe34 |
| TEMPLATE_author_verification.csv | c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331 |
| INSTRUCTIONS_verification.md | d3048dd63c69f71022a217b516f1c9dc5885b06dffd1e14ff9552010ee928b45 |
| key_verification.csv | edcf5eb34038ab8d55b720ecfe574b3a549f5d36d0b4b4ef235909a16250545e |
| selection.json | 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3 |
| extraction.json | 71adf8bd07c8f9967849c45b6486a13b0fadd34f922a96aa97a2fdde4d44bcab |
| extraction_attempts.jsonl | 3c45c17d45f0bb87c873bbe7894ef4db3fe55067f0b3097766154d08b8f78ada |
| container_check.json | 3b80027eebd2c1e90c80c553c352402659bac0658641302fd6754afbf4df56e5 |
| X1_prompt.md | cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 |
| select_items.py | b3fb8fb21a4e75247504b27685df9c1d28abf03083a82fb3375a9fcf51cc92b2 |
| extract.py | 65fcefe2bb27a2cde4916d5c95248cce9199a92bcd370ea4abfa719d5c52d70d |
| redraw_d49e.py | 7b6f02bd13754c56c9e49a2d0189686a4ffda523ff68daa1bef39241a2ee09bc |
| build_packet.py | b99388a2a0dc8728e85ef94bd76131b3914560c73ef0b0b35e385f37870320e5 |
| verify.py | b367e744e6cf96cb042e1f97f4b8795f4a033fde651eced8168c9d00fa0290a3 |

## 2026-11-16T01:21Z D49e fix: done
- Re-extraction for ministral3-14b|2bd3303580e4b73789206c080e5aa52a|ACC-COMMON|0 only: 1 call, valid on seed 0, no further reserve walk. Replaced ministral3-14b|b581bf2ccc05c503b906cce875ff9351|ACC-COMMON|0 (now 2 logged replacements in total). Pre-fix extraction kept as extraction_pre_d49e.json.
- Cost $0.4116 list price (ESTIMATE $1.391 worst case, cap $1.5; ledger 01:16Z / 01:21Z). Container ta-01M7GYTNEEJEFVZ31TX1RAX50R seen in 8 polls, gone at 140 s (scaled down itself); nothing stopped.
- Packet rebuilt with the unchanged order seed (the item stays at v5-02); conflict_found=false still 8. verify.py (with the strict D49e check on every shown N2 statement, as stored and as rendered) ran twice: ALL CHECKS PASS (hash tables above).

## 2026-11-16T01:22Z verify.py: ALL CHECKS PASS

| file | sha256 |
|---|---|
| packet_verification.html | 5371023f3314136853d6f2097bffd3e8cc22c2ed7e06500466552741524bbe34 |
| TEMPLATE_author_verification.csv | c86780ecc5636b8e88d5f2fd763ba9892f75a54032427d0204ff53c66baf7331 |
| INSTRUCTIONS_verification.md | d3048dd63c69f71022a217b516f1c9dc5885b06dffd1e14ff9552010ee928b45 |
| key_verification.csv | edcf5eb34038ab8d55b720ecfe574b3a549f5d36d0b4b4ef235909a16250545e |
| selection.json | 2555c21116fe0875c027f1157df0a503922c464ce29215cf30aade178fe9dba3 |
| extraction.json | 71adf8bd07c8f9967849c45b6486a13b0fadd34f922a96aa97a2fdde4d44bcab |
| extraction_attempts.jsonl | 3c45c17d45f0bb87c873bbe7894ef4db3fe55067f0b3097766154d08b8f78ada |
| container_check.json | 3b80027eebd2c1e90c80c553c352402659bac0658641302fd6754afbf4df56e5 |
| X1_prompt.md | cb25581a311fd663321124f9a722cc8325093417e5300f35b0662413af4e1ab2 |
| select_items.py | b3fb8fb21a4e75247504b27685df9c1d28abf03083a82fb3375a9fcf51cc92b2 |
| extract.py | 65fcefe2bb27a2cde4916d5c95248cce9199a92bcd370ea4abfa719d5c52d70d |
| redraw_d49e.py | 7b6f02bd13754c56c9e49a2d0189686a4ffda523ff68daa1bef39241a2ee09bc |
| build_packet.py | b99388a2a0dc8728e85ef94bd76131b3914560c73ef0b0b35e385f37870320e5 |
| verify.py | b367e744e6cf96cb042e1f97f4b8795f4a033fde651eced8168c9d00fa0290a3 |
