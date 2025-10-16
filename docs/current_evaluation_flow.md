# Current Evaluation Flow

This note captures how the existing Trust Bench Studio experience works before we begin repository ingestion changes. It focuses on the `/api/evaluate` endpoint, how metrics are stored, and where the React UI reads results.

## Backend Request Path

1. **Entry point** – `POST /api/evaluate` in `trust_bench_studio/api/server.py:357`.
2. **Validation** – The request payload contains `repo_url` and optional `profile`.  
   - `repo_url` is sanitized and must start with `https://github.com/`.  
   - In demo mode the URL is not cloned; it is only echoed in the response.
3. **Data collection** – `_load_latest_summary()` loads the most recent run metadata through `trust_bench_studio/utils/run_store.py`.
   - `run_store.list_runs()` scans `runs/` (or `trustbench_core/eval/runs/`) for evaluation folders.
   - `RunSummary` aggregates `metrics.json`, `summary.json`, etc.
4. **Verdict synthesis** – `utils/orchestrator_synthesis.synthesize_verdict()` converts metrics to a pass/warn/fail decision and pillar breakdowns.
5. **Response payload** – Backend returns:
   ```json
   {
     "status": "complete",
     "repo_url": "...",
     "verdict": { ... },
     "summary": {
       "metrics": {...},
       "agents": [...],
       "raw": {...}
     },
     "message": "Demo mode: ..."
   }
   ```
   The summary mirrors the `RunSummary` structure.

## Data Storage

- Evaluation artifacts are stored under either `runs/` or `trustbench_core/eval/runs/`.  
  Typical files include:
  - `metrics.json`, `summary.json`, `report.json` (score data)
  - `run.json`, `trace.json`, `agents.json` (process trace)
  - `report.html` (if a report was generated)
- The `runs/latest` symlink/dir is what `_load_latest_summary()` uses to find the most recent data.

## Frontend Consumption

1. **Flow Panel**
   - `App.tsx` triggers backend operations (currently mocked) and displays live status logs.
   - Pillar verdicts and composite scores are rendered in the dashboard once the backend response arrives.
2. **Settings Tab**
   - `EvaluationSettings.tsx` hits `/api/settings/evaluation` to read/write custom thresholds.  
   - These settings don’t yet feed back into `/api/evaluate`, but the plan is to do so when agents run on arbitrary repos.
3. **Reports View**
   - `ReportListItem` and `ReportViewer` components consume `/api/reports/list` and `/api/reports/view/{id}`.  
   - Both rely on the same run-store files produced during evaluation.
4. **Agent Chat**
   - `/api/chat/agent` uses `RunSummary` + agent manifest to generate contextual explanations via `utils.llm.explain`.

## Key Takeaways

- `/api/evaluate` is currently demo-only; it reuses the most recent evaluation run on disk instead of cloning repos.
- All downstream UI panels consume data from run artifacts captured in `runs/` / `trustbench_core/eval/runs/`.
- Repository ingestion needs to extend this flow by creating new run directories per analysis job and reusing the same summary/verdict generation utilities.
