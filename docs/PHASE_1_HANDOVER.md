# Phase 1 Handover (Real Agent Logic) — Prereqs

## Install
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-phase1.txt
cp .env.example .env
# Fill GROQ_API_KEY, optional MCP server URL/key
```

## Where MCP client lives
- `trustbench_core/tools/mcp_client.py` — HTTP client with `/health`, `/discover`, `/tools/<name>`
- `trustbench_core/tools/bundle/tools_security.py` — normalized wrappers for `prompt_guard`, `semgrep_rules`, `secrets_scan`

## Secrets
- `GROQ_API_KEY` in `.env` (not committed)
- Optional `MCP_SERVER_URL`, `MCP_API_KEY` if using a remote server
- CI: add `GROQ_API_KEY` as a repo secret and export `GROQ_MODEL`

## Threshold calibration
- Use `profiles/default.yaml` first; run 10 times → compute means
- Tune `profiles/highstakes.yaml` upward to where healthy code passes, adversarial branches fail

## Implement next
- Replace task_fidelity with RAGAS
- Wire security agent to tool bundle (PromptGuard/Semgrep/Secrets)
- Add latency sampler + refusal judge (Groq)
- Update tests + report snapshot
