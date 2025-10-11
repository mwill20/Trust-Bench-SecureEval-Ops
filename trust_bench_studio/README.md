# Trust_Bench Studio Command Center

The Streamlit dashboard has evolved into a React + FastAPI experience that preserves the original Flow, agent manifest, verdict synthesis, and MCP tooling. All evaluation plumbing continues to live in Python; the UI now consumes it via REST endpoints.

## Quick Start

### 1. Backend (FastAPI)
```bash
uvicorn trust_bench_studio.api.server:app --reload
```

### 2. Frontend (React + Vite)
```bash
cd trust_bench_studio/frontend
npm install
npm run dev
```
Navigate to http://127.0.0.1:5173 to access the Studio command center.

### 3. Optional: Production build
```bash
npm run build
```
The output lands in `trust_bench_studio/frontend/dist/`; serve it with any static host or mount it behind FastAPI.

## Architecture Overview

- **Backend** – `trust_bench_studio/api/server.py`
  - `/api/agents`: manifest-driven metadata (names, roles, prompts, colors, images).
  - `/api/run/latest`: loads `eval/runs/latest` via `load_run_summary`.
  - `/api/verdict`: wraps `synthesize_verdict` to publish composite PASS/WARN/FAIL decisions.
  - `/api/mcp/{tool}`: bridges to `trust_bench_studio.utils.mcp_client.call_tool` with guardrails.
  - `/api/baseline/promote`: shells out to `scripts/make_baseline.py` to snapshot curated baselines.

- **Frontend** – `trust_bench_studio/frontend/`
  - Replicates the Flow narrative (input → Logos → agents) with animated links, per-agent chats, and orchestrator verdict panel.
  - Dashboard, Agents, and Reports views source their data from the REST API, mirroring the legacy Streamlit tabs.
  - Guardrails enforce sanitized user input, escaped transcripts/findings, and safe MCP interactions.

- **Legacy entrypoint** – `streamlit run trust_bench_studio/app.py` now displays setup instructions and (optionally) a preview of the production build.

## Flow Walkthrough

1. **Dispatch** – Enter a task or repo URL, hit *Start Analysis*. Dashed/glowing edges show in-flight orchestration; solid lines signal completion.
2. **Orchestrator Verdict** – Logos aggregates agent outputs, applies security/ethics vetoes, computes composite scores, and surfaces top drivers + recommended actions (generate report, cleanup, promote baseline).
3. **Agent Chats** – Unlock automatically after each agent finishes. Seed prompts come from the manifest; chats never re-run evaluations—only explain existing evidence.
4. **Reports & MCP** – Trigger workspace actions (`cleanup_workspace`, `scan_repo_for_secrets`, `env_content`). Responses are cached and visible in the log panel and accessible to chats.

## Testing

```bash
python -m compileall trust_bench_studio
pytest -q tests/test_agents_manifest.py tests/test_orchestrator_synthesis.py
```

Front-end checks live in the `frontend` subdirectory (`npm run lint`, `npm run build`). Ensure the FastAPI backend is available during UI manual tests.

## Screenshots (to add)
- Flow command center – input, Logos, agents, verdict.
- Dashboard metrics vs. baseline.
- Agent tiles with chat unlocked post-completion.
- Reports & MCP action log and raw JSON viewer.

Add PNG/JPEG captures under `docs/images/studio/` to keep the repo lightweight.

## Security Notes

- User input is clipped and pattern-checked before being stored or echoed.
- All transcripts/findings render via escaped HTML to prevent injection.
- MCP actions enforce allow-listed tools and argument sizes.

## Baseline Snapshots

Promoting a run to baseline still shells out to `scripts/make_baseline.py` (now available via REST and the UI action button). The new Flow verdict driver surfaces when a baseline snapshot is recommended.

