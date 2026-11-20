# Proposed serving / grid changes for the N2 extension (NOT APPLIED; files outside t3_1 were not edited)

Apply only after the experiment council approves N2_EXTENSION_COUNCIL_PACKET.md. Revisions were read from the HF API on 2026-11-16.

## 1. modal_serving/serve_vllm.py, add to MODELS

```python
    # N2 extension generator 1 (Mistral family): Ministral-3-14B-Instruct, BF16 repo (the plain repo is FP8), Apache-2.0, ungated
    "ministral3-14b": dict(
        repo="mistralai/Ministral-3-14B-Instruct-2512-BF16", revision="3cea74c1ebaf5ce5f5a2553de470e2ceab825142",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384,
        args=["--language-model-only"]),
    # N2 extension generator 2 (AI2 OLMo family): Olmo-3.1-32B-Instruct, 64.5 GB bf16, Apache-2.0, ungated.
    # H200 (141 GB), not H100: 64.5 GB of weights leave only ~7 GB for KV on an 80 GB card.
    "olmo3.1-32b": dict(
        repo="allenai/Olmo-3.1-32B-Instruct", revision="ac0587e4a7744a551c059d8cd17ba220bc940dae",
        gpu="H200", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384, args=[]),
    # N2 extension generator 3 (Microsoft Phi family): phi-4 14.7B, MIT, ungated. Hard context limit 16384.
    "phi4-14b": dict(
        repo="microsoft/phi-4", revision="2db69c1c3e91a05d2c64a3185acfbaf36f744e25",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384, args=[]),
    # A4 second scorer (IBM Granite family): granite-4.2-30b dense 29.3B, Apache-2.0, ungated.
    # Thinking is ON by default in the chat template; the harness already sends enable_thinking=False,
    # which makes the template end the prompt with <think></think>. The parser flag is a safety net.
    "granite4.2-30b": dict(
        repo="ibm-granite/granite-4.2-30b", revision="9e668ce1c538387ef24d3644e9b0606647762636",
        gpu="H100", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384,
        args=["--reasoning-parser", "nemotron_v3"]),
```

`VLLM_IMAGE` stays `vllm/vllm-openai:v0.32.0`. Architectures: Mistral3ForConditionalGeneration, Olmo3ForCausalLM, Phi3ForCausalLM, GraniteForCausalLM. Their presence in the v0.32.0 registry was NOT verified here; the CPU `download` step does not check it. The smoke is the first real test. If `nemotron_v3` is not registered in v0.32.0, drop the flag (the template needs none when thinking is off).

## 2. modal_serving/endpoints.json, add four entries (URLs empty until `modal deploy` prints them)

Each entry must match the registry above, because the harness prices from it:

| alias | gpu | n_gpu | cpu | memory_mib | scaledown_s |
|---|---|---|---|---|---|
| ministral3-14b | L40S | 1 | 4.0 | 32768 | 120 |
| olmo3.1-32b | H200 | 1 | 8.0 | 65536 | 120 |
| phi4-14b | L40S | 1 | 4.0 | 32768 | 120 |
| granite4.2-30b | H100 | 1 | 8.0 | 65536 | 120 |

with `repo` equal to the `repo` above and `app` = `pilot-vllm-<alias>`.

## 3. t3_1/analysis/n2_grid.py, MODELS dict (assumptions to be replaced by smoke measurements)

```python
    "ministral3-14b": dict(tok_per_s=440.0, cold_s=150.0, cold_measured=False),
    "olmo3.1-32b":    dict(tok_per_s=330.0, cold_s=150.0, cold_measured=False),
    "phi4-14b":       dict(tok_per_s=420.0, cold_s=150.0, cold_measured=False),
```

`--models` already accepts `choices=sorted(MODELS)`, so nothing else changes. `DEFAULT_MODELS` stays the two existing models; new runs use `--models <alias>` with a separate `--tag`, so the existing `full_k1` outputs are not touched. Note that the existing design hash covers `models`, so the extension needs its own design hash and approval file (`council/N2_EXT_APPROVAL.json`).

`serving_info()` parses the pinned revision with the regex `"<alias>":\s*dict\(\s*repo="...",\s*revision="<40 hex>"`; the entries above are written to satisfy it.

## 4. Per-model call details the smoke must confirm

* Mistral and Phi-4 templates ignore `enable_thinking`; vLLM passes unknown `chat_template_kwargs` through harmlessly. Confirm no 400.
* The harness sends `top_k=-1`. Confirm vLLM accepts it for all four (it did for Gemma and Qwen).
* Olmo-3.1 template inserts its own default system prompt only when none is given; N2 always gives one.
* Scorer (Granite): requests carry `response_format={"type":"json_object"}`; confirm 0 parse failures on the 12 N2 validation statements plus the 60 gate-1 statements before any N2 scoring.

## 5. Annotator model (D34 item 4), add to MODELS and endpoints.json

```python
    # LLM annotator (OpenAI gpt-oss family): gpt-oss-120b, MoE 117B / 5.1B active, MXFP4 weights (~65 GB), Apache-2.0, ungated.
    # Fits one 80 GB H100. Reasoning cannot be switched off (harmony format); that is acceptable for labeling.
    "gptoss-120b": dict(
        repo="openai/gpt-oss-120b", revision="b5c939de8f754692c1647ca79fbf85e8c1e70f8a",
        gpu="H100", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384,
        args=["--reasoning-parser", "openai_gptoss"]),
```

endpoints.json row: gptoss-120b, H100, 1, 4.0->8.0 cpu, 65536 MiB, scaledown 120. Fallback: `openai/gpt-oss-20b` sha `6cee5e81ee83917806bbde320786a8fb61efebee` on L40S (about 14 GB).
Calls must set `max_tokens` >= 4096 (reasoning tokens count) and read the answer from `content`, not `reasoning_content`. Do not send `enable_thinking`; use `reasoning_effort` via `chat_template_kwargs` ("low"/"medium") if needed.
