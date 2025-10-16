# Trust Bench Repository Analysis Plan

This checklist tracks implementation of the repository ingestion and evaluation system.  
Always follow the build → test → troubleshoot → fix → push-to-main cadence before marking a task complete.  
Add new tasks as the scope evolves.

---

## Execution Protocol

- [ ] Validate environment prerequisites (Python venv, npm install, required env vars, repo auth).
- [ ] Implement the scoped changes for the current checklist item.
- [ ] Run automated checks (e.g. `pytest`, targeted integration tests, `npm test`/`npm run lint`).
- [ ] Resolve failures, rerun tests until green.
- [ ] Verify formatting/linting (`ruff`, `black`, `prettier` as applicable).
- [ ] Confirm a clean `git status`.
- [ ] Stage only relevant files, commit with a descriptive message, and push to `main`.

---

## Phase 0 – Foundations

- [x] Confirm the FastAPI backend (`uvicorn`) and React frontend (Vite dev server) launch successfully.
- [x] Document the current `/api/evaluate` → Settings tab data flow, including usage of `runs/` and `trust_bench_studio/data/`.
- [x] Finalize team policy to push to `main` after each checklist completion (baseline workflow confirmation).

## Phase 1 – Repository Ingestion MVP

- [ ] Design the job schema (`job_store.py`) and scaffold service stubs (`GitHubService`, `JobManager`).
- [ ] Implement `POST /api/repositories/analyze` and `GET /api/repositories/{id}/status` with mocked analysis data.
- [ ] Build `RepositoryInput.tsx` and `AnalysisProgress.tsx`, wiring them to the mocked endpoints.
- [ ] Smoke-test the new endpoints and UI flow; commit and push the working state.

## Phase 2 – Analysis & Agent Orchestration

- [ ] Flesh out `GitHubService` cloning logic (size safeguards, disk layout) and integrate with `JobManager`.
- [ ] Implement `CodeAnalyzer` and `SecurityScanner`, ensuring no untrusted code execution.
- [ ] Create `AgentOrchestrator`, hook in existing agents, and expose `/api/agents/batch-evaluate`.
- [ ] Extend the UI with `CodebaseOverview.tsx`, `AgentResults.tsx`, and agent rerun controls.
- [ ] Run backend agent smoke tests and frontend checks; commit and push.

## Phase 3 – Reporting & Caching

- [ ] Build `ReportGenerator` plus `/api/reports/{id}` returning HTML/JSON artifacts.
- [ ] Introduce repository cache indexing (repo + commit) and surface cache status in job status responses.
- [ ] Deliver `ComprehensiveReport.tsx` with export/download options.
- [ ] Execute regression runs covering cached and fresh repositories; commit and push.

## Phase 4 – Hardening & Monitoring

- [ ] Add concurrency limits, rate-limit handling, and retry logic across services.
- [ ] Integrate telemetry/metrics (job duration, failure cases) and redact sensitive logs.
- [ ] Conduct security review ensuring ingestion sandboxing and secret hygiene.
- [ ] Finalize documentation and retrospective notes; commit and push.

---

## Quality Rubric

- **Correctness** – Features meet acceptance criteria, API contracts honored, tests updated.
- **Reliability** – Handles failure modes (timeouts, rate limits, malformed repos) without crashes.
- **Security** – No untrusted code execution; secrets redacted; network usage controlled.
- **Performance** – Repos ≤ 100 MB analyzed within 5 minutes; concurrency capped to avoid overload.
- **User Experience** – Progress states accurate, error messaging actionable, reports clear.
- **Maintainability** – Cohesive modules, helpful docstrings/comments, configuration centralized.
- **Test Coverage** – Critical paths covered by unit/integration tests; manual test notes captured when needed.
