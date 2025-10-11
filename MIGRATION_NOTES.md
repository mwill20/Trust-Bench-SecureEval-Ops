# Trust_Bench Studio New UI Migration

## Overview

The Streamlit-based presentation layer has been replaced by a React command-center experience backed by a FastAPI service. Core evaluation utilities (`run_store`, `orchestrator_synthesis`, `mcp_client`, etc.) remain unchanged; the new UI consumes them via REST endpoints. This document captures the migration steps, new tooling, and local development instructions.

## What Changed

- Added `trust_bench_studio/api/server.py` exposing FastAPI endpoints for agents, runs, orchestrator verdicts, MCP actions, and baseline snapshots.
- Ported the React/Vite UI from `New_UI/` into `trust_bench_studio/frontend/` (TypeScript source plus Vite config). The layout matches the Flow / Dashboard / Agents / Reports experience while leveraging manifest-driven visuals.
- Reworked `trust_bench_studio/components/flow_view.py` to operate as a backend-friendly data provider for the React UI (sanitized inputs, animated link state, verdict actions).
- Added `tests/test_orchestrator_synthesis.py` to lock in verdict logic (composite score + veto behavior).
- Updated `.gitignore` to account for `frontend/node_modules` and build artifacts.
- Added this migration note to document new dev workflow and dependencies.

## New Dependencies

- `fastapi>=0.115`
- `uvicorn>=0.30`
- Node.js (18+) for running the Vite dev server / build pipeline inside `trust_bench_studio/frontend`.

All Python deps are captured in `requirements.txt`; Node deps live in `trust_bench_studio/frontend/package.json`.

## Running Locally

### 1. Start the API backend

```bash
uvicorn trust_bench_studio.api.server:app --reload
```

This exposes the REST API on `http://127.0.0.1:8000`. CORS is enabled for local development.

### 2. Start the React command center

```bash
cd trust_bench_studio/frontend
npm install
npm run dev
```

Vite serves the UI on `http://127.0.0.1:5173` by default. The app will call the FastAPI endpoints described above.

### 3. (Optional) Build for production

```bash
npm run build   # output in trust_bench_studio/frontend/dist
```

You can statically serve the generated files with any HTTP server (e.g., `npx serve dist`) or integrate into an ASGI mount.

## Streamlit Compatibility

`streamlit run trust_bench_studio/app.py` now displays instructions to start the FastAPI/React stack. Streamlit rendering of the old UI is deprecated.

## MCP & Baseline Actions

The new UI invokes the existing MCP helpers (`call_tool`) through `/api/mcp/{tool}`, and promotes baselines via `scripts/make_baseline.py` behind `/api/baseline/promote`. Input sanitisation, path caps, and error messaging remain enforced.

## Testing

```bash
python -m compileall trust_bench_studio
pytest -q tests/test_agents_manifest.py tests/test_orchestrator_synthesis.py
```

Front-end lint/build can be executed with `npm run lint` / `npm run build` inside `trust_bench_studio/frontend`.

## Deployment Notes

- Deploy the FastAPI app with `uvicorn` or any ASGI host.
- Serve the built React assets either via CDN or by mounting `dist/` behind a static files handler in FastAPI.
- Ensure environment variables (`MCP` configuration, provider API keys) follow the same patterns as the previous Streamlit deployment.

