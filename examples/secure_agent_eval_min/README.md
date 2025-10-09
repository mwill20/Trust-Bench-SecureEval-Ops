# TrustBench Starter Evaluation (4 Pillars)

Minimal, drop-in harness that checks:
1. **Task Performance** (RAG correctness proxies now, RAGAS later)
2. **System Performance** (p95 latency, failure rate)
3. **Security and Robustness** (injection resistance, secret leak, dangerous command block)
4. **Ethics and Alignment** (refusal accuracy, policy violations)

## Quick Start
```bash
python -m venv .venv && .venv\Scripts\activate
pip install pytest pyyaml
python eval/evaluate_agent.py
```

## Wire in your real agent
- `tests/task/test_ragas.py::ask_agent()` → call your HTTP endpoint or local function and return `{"answer": str, "context": [str, ...]}`.
- Swap cosine proxies for `ragas` metrics when ready.
- `tests/system/test_system_perf.py::ping_agent()` → real call to agent or MCP server.
- `tests/security/test_adversarial.py` → replace stubs with `PromptGuard`, command classifier, redactor.
- `tests/ethics/test_alignment.py` → route to your policy checker and refusal templates.

## Config
Tune thresholds and dataset paths in `eval/eval_config.yaml`.
