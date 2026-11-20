# COSTS.md: T3-1 Modal spend and GPU choice

Source for all prices: https://modal.com/pricing (fetched 2026-11-15). Per-second
values match `pilot_harness/prices.py` (MODAL_GPU_PER_S). $/hr = per-second x 3600.

## Caps (BRIEF.md rule 5, section 11)

- Modal global cap: **$150** (`pilot_harness/budget.py`, GLOBAL_CAP_USD = 150.0).
  Note: this ledger's global cap also covers all other providers. It was $50.
- Per-experiment caps (config dict `EXPERIMENT_CAPS_USD` in budget.py): T3-1 core + Tier 2 10,
  N2 10, N6 5, B 10, F-min 25, F-exp 40, new experiment 30, buffer 20. These sum to 150.
  Enforcement happens through the `pilot_cap` argument callers pass.

## Spend to date (2026-11-15)

- Harness ledger, T3-1 Modal jobs: $0.650 list price (3 smoke runs + setup overhead). Detail in ledger.csv.
- Modal billing for the project's `pilot-vllm-*` apps: $0.597 (gemma4-12b $0.176, qwen3.8-27b $0.422).
- The same Modal workspace also bills other projects (llm-consciousness-*, quant-*, oss-pr-runner,
  card-reach, qb-read, lgw-read; about $15.7 this month). These are NOT T3-1 spend and are excluded from the ledger.
- Workspace billing summary, this month: metered $17.61, credits -$16.16, billed $0.00.

## Per-model GPU list prices (modal.com/pricing)

| GPU | $/sec | $/hr | Notes |
|---|---|---|---|
| T4 | 0.000164 | 0.59 | |
| L4 | 0.000222 | 0.80 | 24 GB VRAM |
| A10 | 0.000306 | 1.10 | 24 GB VRAM. Page lists "A10"; billing shows A10G for another project |
| L40S | 0.000542 | 1.95 | 48 GB VRAM |
| A100 40 GB | 0.000583 | 2.10 | |
| A100 80 GB | 0.000694 | 2.50 | |
| H100 SXM | 0.001097 | 3.95 | |
| H200 SXM | 0.001261 | 4.54 | |
| B200 | 0.001736 | 6.25 | |

CPU $0.0000131 per physical core per second. Memory $0.00000222 per GiB per second.
Free credit: Starter $30/month, Team $100/month. The harness ignores credit, so it overstates real spend.

## Cheapest GPU per planned job

VRAM fit is a working assumption, not measured. Each job must confirm it in a smoke run before the full run.

| Job | Model class (assumed) | Cheapest adequate GPU | $/hr | Why |
|---|---|---|---|---|
| N2 generation (current models write statements) | ~12B bf16 (Gemma-4-12B class) | L40S (48 GB) | 1.95 | Smoke test already ran on L40S. Use L4 only if the model fits 24 GB in fp16/quantised. |
| N2 generation, ~27B class | ~27B bf16 | H100 | 3.95 | Smoke test ran on H100. Quantised 27B could fit L40S (verify). |
| A4 second scorer | ~8B classifier, scoring only | L4 (24 GB) | 0.80 | Scoring is short and cheap. Fall back to A10 at 1.10 if L4 is out of memory. |
| F fine-tune (LoRA on ~8B) | ~8B bf16 LoRA | A10 (24 GB) for the cheapest $/hr, or L40S (48 GB) if the batch needs more memory | 1.10 / 1.95 | Cheapest $/hr that plausibly fits. Choose by $/run: faster GPUs can cost less per completed run. Measure before committing. |

## Rule: estimate and timeout before every job

Before any Modal job launches, the job must write one ledger row with:
1. `estimate_usd` = $/hr x (max wall-clock hours) + cold-start allowance, using the table above.
2. `timeout_s` set on the Modal function. The harness hold assumes it.
3. `approved_by`. Jobs over $5 need the experiment council (BRIEF section 8).

A job with no estimate row or no timeout does not launch. At $150 cumulative, stop all Modal jobs (BRIEF section 14).

## Open items

- Two deployed `pilot-vllm-*` apps (ap-1zICEI6idq1NNUtkV5L5at, ap-SjaTupPcJSiqo6zAtVdPbL) show 0 tasks and 0 containers.
  A stop command was denied by the permission classifier, so they are still deployed. A human should stop them.
  Idle deployed apps with 0 containers bill nothing for compute.
- The $150 cap is for T3-1. The workspace total includes other projects. Confirm with the human whether the $150 applies to T3-1 only.
