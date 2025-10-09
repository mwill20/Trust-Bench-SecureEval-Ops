# TrustBench Core - Secure Evaluation Suite

TrustBench Core is the canonical evaluation engine for the four TrustBench pillars:
task fidelity, system robustness, security, and ethics. It bundles the run
orchestrator, simulated experiments, human-in-the-loop templates, and Markdown reporting
for quick CI or local validation.

## Quick Start
Run from the repository root after activating a virtual environment:
```bash
python -m venv .venv && .venv\Scripts\activate     # PowerShell
pip install -e ..[dev]
pytest trustbench_core/tests -q
python -c "from trustbench_core.eval.orchestrator import run_all; run_all()"
python -c "from trustbench_core.eval.report import main; main()"
```


## Phase 1 Agents
- Task fidelity uses Groq completions + RAGAS, dataset in `datasets/golden/*.jsonl`.
- Security agent hits MCP (`prompt_guard`, `semgrep_scan`, `secrets_scan`) and records bypasses.
- System performance samples Groq completions to produce latency metrics and raw traces.
- Ethics/refusal judge calls Groq `llm_json` with a rubric and lists misclassifications.
Set `GROQ_API_KEY` (or enable fake provider via `TRUSTBENCH_FAKE_PROVIDER=1`) and, if remote, `MCP_SERVER_URL`/`MCP_API_KEY`.

## Repository Map
- `eval/` - orchestration, methods, reporting, and HITL assets.
- `tests/` - pytest suites for task, system, security, and ethics signals.
- `data/` - sample datasets wired into the default config.
- `tools/` - TrustBench MCP server and hardened tool bundle prototypes.

## Configure
Tune paths and thresholds in `eval/eval_config.yaml`. During integration replace the
stubs in `tests/**` with real agent calls, swap in production datasets, and push reports
to your preferred artifact store.
