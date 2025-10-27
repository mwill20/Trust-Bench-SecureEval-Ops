# OPERATIONS

> This document describes runtime operations for Trust Bench SecureEval + Ops.
> Phase 0 locks in the current behavior; later phases will extend resilience and monitoring notes.

## Overview
- Baseline operations for both CLI (`Project2v2/main.py`) and the Flask web interface (`Project2v2/web_interface.py`).
- Applies to the parity snapshot tagged at `v3.0-phase0-parity`.

## Start / Stop / Health
- **Start**
  - CLI: `python Project2v2/main.py --repo <path-to-repo> --output Project2v2/output`
  - Web UI: `python Project2v2/web_interface.py`
- **Stop**
  - Use `Ctrl+C` (SIGINT) in the hosting terminal. Both CLI and web interface exit gracefully.
- **Health Probes**
  - Not exposed during Phase 0. CLI parity is validated via exit code `0`; HTTP `/healthz` will arrive in later phases.

## Logging
- `app/logging.py` configures JSON-formatted logs (fields: `ts`, `level`, `run_id`, `logger`, `msg`). Example: `{"ts":"2025-10-27T06:43:00Z","level":"INFO","run_id":"abc123","logger":"root","msg":"analysis complete"}`.
- Logs stream to STDOUT by default; redirect to a file or aggregator as needed.
- Exceptions include `exc_info` fields, enabling structured monitoring pipelines.

## Resilience Settings
- SecureEval layer wraps orchestrator execution with `retry(max_tries=3, backoff=0.5)` and `with_timeout(120)` from `app/util_resilience.py`.
- Defaults ensure a failing invocation is attempted up to three times with exponential backoff (0.5s, 1s, 2s).
- Timeouts raise `TimeoutError`; future phases will expose `.env` overrides for these thresholds.

## Error Handling & Recovery
- CLI errors bubble to STDERR and exit with non-zero status. Rerun the command after addressing the reported issue.
- Web interface surfaces errors in toast-style alerts while logging stack traces to the terminal.

## Monitoring Tips
- Tail structured logs with `Get-Content -Path <logfile> -Wait` (Windows) or `tail -f` (Unix).
- Attach `run_id` values to support request correlation across services.
- Health endpoints: `GET /healthz` (liveness) and `GET /readyz` (readiness) exposed via FastAPI router.

## CI Reference
- Parity gate: `pytest Project2v2/tests/test_parity.py` (locks JSON, Markdown, and bundle artifacts).
- SecureEval gate: `pytest Project2v2/tests/test_secure_eval.py` validating guardrails, sandbox, and resilience decorators.
- Future phases will expand CI to include secure-eval validators, coverage thresholds, and linting.

---

_Remember to update this document whenever operational characteristics change (timeouts, health checks, deployment scripts, etc.)._
