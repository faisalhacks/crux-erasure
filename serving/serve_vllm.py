# Pilot vLLM server on Modal: OpenAI-compatible, logprobs on, one app per model.
#
# Adapted from Modal's official example
#   github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/llm-serving/vllm_inference.py
#   (commit dfcf4a21a3b87ca6f1cd25e3db227f4d319ff50e, 2026-11-10).
# Changes from the example, and why:
#   * model chosen by the SERVE_MODEL env var at deploy time (registry below), one Modal app per model;
#   * proxy auth ON (the example sets unauthenticated=True). Requests need
#     `Authorization: Bearer wk-...ws-...` (a workspace proxy token, see setup_secrets.py); requests
#     without it are rejected at Modal's edge and never wake a GPU;
#   * scaledown_window 2 min (example: 15 min), max_containers=1, min_containers=0 (scale to zero).
#     max_containers=1 also makes the client-side GPU-second ledger an upper bound on real usage;
#   * explicit cpu/memory requests, so the harness can price a container-second exactly;
#   * weights pre-downloaded by a CPU-only function (no GPU billed while downloading);
#   * logprobs: --max-logprobs 20, --logprobs-mode raw_logprobs (logprobs of the model's own
#     distribution, before temperature / top-k / top-p), --generation-config vllm (do NOT silently
#     apply the repo's default top_k/top_p/temperature: requests get exactly what they send);
#   * official vllm/vllm-openai image instead of cuda + pip (vLLM 0.32.0 is the first release line
#     whose registry has Gemma4UnifiedForConditionalGeneration, needed for gemma-4-12B-it).
#
# Usage (PowerShell; bash: SERVE_MODEL=gemma4-12b modal deploy serve_vllm.py):
#   $env:SERVE_MODEL="gemma4-12b"; modal run serve_vllm.py::download   # CPU-only, caches weights
#   $env:SERVE_MODEL="gemma4-12b"; modal deploy serve_vllm.py          # URL is printed
#   modal app stop pilot-vllm-gemma4-12b                               # tear down
import json
import os

import modal

MINUTES = 60
VLLM_PORT = 8000
SCALEDOWN_S = 2 * MINUTES      # idle time before the container (and its GPU bill) stops
VLLM_IMAGE = "vllm/vllm-openai:v0.32.0"

# ---------------------------------------------------------------------------------------------
# Model ladder. Revisions pinned (HF commit sha read 2026-11-15). gpu = Modal GPU string.
# cpu (physical cores) and memory (MiB) are billed too; the harness prices all three.
# ---------------------------------------------------------------------------------------------
MODELS = {
    # small rung: newest Gemma (2026-05), 12B dense, bf16 23.9 GB, Apache-2.0, ungated
    "gemma4-12b": dict(
        repo="google/gemma-4-12B-it", revision="43c9d014b231474fa7212dbb48a762566c2b255d",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384,
        args=["--language-model-only", "--reasoning-parser", "gemma4"]),
    # cheap legacy baseline: Llama-3.1-8B-Instruct, bf16 16.1 GB, gated (local HF token HAS access)
    "llama3.1-8b": dict(
        repo="meta-llama/Llama-3.1-8B-Instruct", revision="0e9e39f249a16976918f6564b8830bc894c89659",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384, args=[]),
    # ~30B rung: newest Qwen dense (2026-08), 27.8B, bf16 55.6 GB, Apache-2.0, ungated
    "qwen3.8-27b": dict(
        repo="Qwen/Qwen3.8-27B", revision="37561816e66b5b9153b1b64c10968c18c1e6f4a0",
        gpu="H100", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384,
        args=["--language-model-only", "--reasoning-parser", "qwen3"]),
    # ~70B rung (preferred): Llama-3.3-70B-Instruct, bf16 141 GB. GATED: the local HF token gets
    # 403 on this repo today -> request access on HF first (NEEDS-HUMAN). 2x H200 = 282 GB.
    "llama3.3-70b": dict(
        repo="meta-llama/Llama-3.3-70B-Instruct", revision="6f6073b423013f6a7d4d9f39144961bfbfbc386b",
        gpu="H200", n_gpu=2, cpu=16.0, memory=196608, max_model_len=16384, args=[]),
    # ~70B rung (ungated alternative, reasoning model): same Llama-70B architecture, MIT
    "r1-distill-llama-70b": dict(
        repo="deepseek-ai/DeepSeek-R1-Distill-Llama-70B", revision="b1c0b44b4369b597ad119a196caf79a9c40e141e",
        gpu="H200", n_gpu=2, cpu=16.0, memory=196608, max_model_len=16384,
        args=["--reasoning-parser", "deepseek_r1"]),
    # ---- N2 extension (decisions.md D36), added in the vendored copy P/serving only; revisions read from the HF API 2026-11-16 ----
    # generator (Mistral family): Ministral-3-14B-Instruct, BF16 repo (the plain repo is FP8), Apache-2.0, ungated
    "ministral3-14b": dict(
        repo="mistralai/Ministral-3-14B-Instruct-2512-BF16", revision="3cea74c1ebaf5ce5f5a2553de470e2ceab825142",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384,
        args=["--language-model-only"]),
    # generator (Microsoft Phi family): phi-4 14.7B, MIT, ungated, 16384 context
    "phi4-14b": dict(
        repo="microsoft/phi-4", revision="2db69c1c3e91a05d2c64a3185acfbaf36f744e25",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384, args=[]),
    # A4 second scorer (IBM Granite family): granite-4.2-30b dense 29.3B, Apache-2.0, ungated.
    # NO reasoning parser (D36 / skeptic condition 2); thinking is switched off per request by the harness
    # (enable_thinking=false). The smoke must show content non-empty and no think text.
    "granite4.2-30b": dict(
        repo="ibm-granite/granite-4.2-30b", revision="9e668ce1c538387ef24d3644e9b0606647762636",
        gpu="H100", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384, args=[]),
    # A4 fallback scorer (FR 6.9): granite-4.2-8b dense 8.8B BF16, same family and same no-reasoning-parser setting. Revision = HF API sha read 2026-11-16.
    "granite4.2-8b": dict(
        repo="ibm-granite/granite-4.2-8b", revision="a7042144125ce5ae64f89610e8289647fc000b9a",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384, args=[]),
    # A4 fallback 1 (FR 6.9 R4a, D45): Falcon-H1-34B-Instruct (TII), hybrid Transformer+Mamba, BF16 67 GB -> 1x H200. Revision = HF API sha 2026-11-16.
    "falcon-h1-34b": dict(
        repo="tiiuae/Falcon-H1-34B-Instruct", revision="6e6890e26cba1f58b1e6ee70d654ddf054f9fce8",
        gpu="H200", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384, args=[]),
    # A4 fallback 2 (FR 6.9 R4a, D45): Command R7B (Cohere), gated=auto (terms must be accepted by the account holder; NOT requested by the runner). Revision = HF API sha 2026-11-16.
    "command-r7b": dict(
        repo="CohereLabs/c4ai-command-r7b-12-2024", revision="4f3d0aa6856e322f2f4480fe65420d5d53d297b8",
        gpu="L40S", n_gpu=1, cpu=4.0, memory=32768, max_model_len=16384, args=[]),
    # LLM annotator (OpenAI gpt-oss family): gpt-oss-120b, MoE, MXFP4 weights (~65 GB), Apache-2.0, ungated, fits one H100.
    # Reasoning cannot be switched off (harmony format). Calls need max_tokens >= 4096; answer is read from content.
    "gptoss-120b": dict(
        repo="openai/gpt-oss-120b", revision="b5c939de8f754692c1647ca79fbf85e8c1e70f8a",
        gpu="H100", n_gpu=1, cpu=8.0, memory=65536, max_model_len=16384,
        args=["--reasoning-parser", "openai_gptoss"]),
}

ALIAS = os.environ.get("SERVE_MODEL", "gemma4-12b")
if ALIAS not in MODELS:
    raise SystemExit(f"SERVE_MODEL={ALIAS!r} not in {sorted(MODELS)}")
CFG = MODELS[ALIAS]

vllm_image = (
    modal.Image.from_registry(VLLM_IMAGE)
    .entrypoint([])  # silence the image's own entrypoint
    # the image ships python3 (with vLLM) but no `python`; Modal needs `python` to detect the version
    .run_commands("command -v python || ln -s \"$(command -v python3)\" /usr/local/bin/python",
                  "python --version && python -c 'import vllm, huggingface_hub; print(vllm.__version__)'")
    .env({
        "SERVE_MODEL": ALIAS,           # bake the choice in, so the container imports the same CFG
        "HF_XET_HIGH_PERFORMANCE": "1",
        "VLLM_LOG_STATS_INTERVAL": "10",
    })
)

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface-pilot")

app = modal.App(f"pilot-vllm-{ALIAS}")


@app.function(image=vllm_image, volumes={"/root/.cache/huggingface": hf_cache_vol},
              secrets=[hf_secret], cpu=4.0, memory=8192, timeout=60 * MINUTES)
def download():
    """CPU-only: put the pinned weights into the shared volume so the GPU container never downloads."""
    from huggingface_hub import snapshot_download

    path = snapshot_download(CFG["repo"], revision=CFG["revision"],
                             allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja",
                                             "tokenizer*"],
                             ignore_patterns=["consolidated*", "original/*"])
    hf_cache_vol.commit()
    print("cached", CFG["repo"], CFG["revision"], "->", path)


@app.server(
    image=vllm_image,
    gpu=f"{CFG['gpu']}:{CFG['n_gpu']}",
    cpu=CFG["cpu"],
    memory=CFG["memory"],
    scaledown_window=SCALEDOWN_S,
    startup_timeout=20 * MINUTES,     # cold start: image pull + weight load + CUDA graphs
    min_containers=0,                 # scale to zero
    max_containers=1,                 # one replica: bounded spend, and the ledger is an upper bound
    target_concurrency=64,
    volumes={"/root/.cache/huggingface": hf_cache_vol, "/root/.cache/vllm": vllm_cache_vol},
    secrets=[hf_secret],
    port=VLLM_PORT,
    unauthenticated=False,            # Modal proxy auth required (Authorization: Bearer wk-...ws-...)
)
class Server:
    @modal.enter()
    def start(self):
        import subprocess

        cmd = [
            "vllm", "serve", CFG["repo"],
            "--revision", CFG["revision"],
            "--served-model-name", ALIAS, CFG["repo"],
            "--host", "0.0.0.0", "--port", str(VLLM_PORT),
            "--uvicorn-log-level=info",
            "--tensor-parallel-size", str(CFG["n_gpu"]),
            "--max-model-len", str(CFG["max_model_len"]),
            "--max-logprobs", "20",
            "--logprobs-mode", "raw_logprobs",
            "--generation-config", "vllm",
            "--enforce-eager",         # FAST_BOOT from the example: skip compile + CUDA graphs
            *CFG["args"],
        ]
        env = dict(os.environ, HF_HUB_OFFLINE="1")  # weights must already be in the volume
        print(*cmd)                                 # contains no secrets
        self.process = subprocess.Popen(cmd, env=env)

    @modal.exit()
    def stop(self):
        self.process.terminate()


@app.local_entrypoint()
def show():
    """Print the registry entry this deploy would use (no secrets)."""
    print(json.dumps({"alias": ALIAS, "app": app.name, **{k: v for k, v in CFG.items()}}, indent=1))
