# P/serving: vendored copy of modal_serving (decisions.md D36, rule 8)

Deploy new aliases ONLY from this directory. ../modal_serving is not edited any more.
Originals copied 2026-11-16:
- serve_vllm.py sha256 32adf17d81dba790af3e6c96d633dae50e6e6e400ff9c3053596cfda8ad75667
- endpoints.json sha256 667d86b03be686704854200377396181c61cfcf8b07cd2aa552e1d9a92cb5798

Additive diff (no existing entry changed): MODELS gains ministral3-14b, phi4-14b, granite4.2-30b (no reasoning parser),
gptoss-120b (annotator; definition only, not deployed by the N2 runner). endpoints.json gains the same four aliases (url empty until deployed,
resource fields equal to MODELS). llama3.1-8b was already defined in the original. Olmo-3.1-32B was NOT added (rejected, D36).
All apps: min_containers=0, max_containers=1, scaledown 120 s, proxy auth, vLLM image vllm/vllm-openai:v0.32.0, pinned revisions.
Runners read this endpoints.json through MODAL_ENDPOINTS (n2_grid.py sets it). Deployed gemma4-12b and qwen3.8-27b URLs are unchanged.

Deploy (one alias at a time, from bash; weights first on CPU):
  cd P/serving; SERVE_MODEL=<alias> python -m modal run serve_vllm.py::download
  SERVE_MODEL=<alias> python -m modal deploy serve_vllm.py     # paste the printed URL into endpoints.json

Additive 2026-11-16 (A4 fallback, FR 6.9): MODELS and endpoints gain granite4.2-8b (ibm-granite/granite-4.2-8b, revision a7042144125ce5ae64f89610e8289647fc000b9a, L40S, no reasoning parser). granite4.2-30b url filled after deploy (V1 smoke: missed the bar, see decisions.md).

Additive 2026-11-16 (A4 fallback 1, D45): falcon-h1-34b (tiiuae/Falcon-H1-34B-Instruct, rev 6e6890e26cba1f58b1e6ee70d654ddf054f9fce8, 1x H200, no extra vLLM args).
