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

## Verification Checklist (Phase 3: Code Quality)

To verify the code quality guarantees introduced in Phase 3, reviewers can run the following commands:

### Automated Test Suite

Run all Phase 3 tests (settings, exceptions, integration):

```bash
cd Project2v2
pytest tests/ -k "phase3" -v
```

**Expected result:** 24 tests passed

**What this validates:**
- ✅ Pydantic Settings load correctly from defaults and environment variables
- ✅ All 3 custom exception types (ConfigurationError, ProviderError, AgentExecutionError) raise and catch correctly
- ✅ Exception context is preserved through `raise...from` chains
- ✅ Error messages are descriptive and include specific details

### Manual Exception Testing

Trigger each exception type to validate error handling:

**A. ConfigurationError** (missing/invalid configuration):
```bash
cd Project2v2
# Temporarily rename .env
Rename-Item .env .env.backup
python main.py --repo . --output test_output
# Restore .env
Rename-Item .env.backup .env
```

**Expected behavior:** System runs with defaults (no .env required), graceful degradation

**B. ProviderError** (invalid API key):
```bash
cd Project2v2
# Set invalid API key temporarily
$env:OPENAI_API_KEY="sk-invalid-test-key"
$env:LLM_PROVIDER="openai"
# Trigger LLM call (use web interface chat or CLI with consultation)
python web_interface.py
# Visit http://localhost:5001 and ask a question in chat
```

**Expected behavior:** Clean error message with HTTP status code (401), helpful guidance, no raw Python stack traces

**C. AgentExecutionError** (agent runtime error):
```bash
cd Project2v2
python main.py --repo /nonexistent/path --output test_output
```

**Expected behavior:** Clear error message identifying which operation failed, exit code ≠ 0, no stack traces to console

### Structured Logging Verification

Inspect log format during execution:

```bash
cd Project2v2
python main.py --repo . --output test_output 2>&1 | Select-String "^\d{4}-\d{2}-\d{2}"
```

**Expected format:** `timestamp | level | name | message`

**Example output:**
```
2025-11-14 13:07:28,815 | INFO | multi_agent_system.agents | SecurityAgent: Starting security scan...
2025-11-14 13:07:28,930 | INFO | multi_agent_system.agents | QualityAgent: Starting quality analysis...
```

**What to verify:**
- ✅ Consistent format across all log lines
- ✅ Multiple log levels present (INFO, DEBUG, ERROR)
- ✅ Module names preserved (helps with debugging)
- ✅ No debug `print()` statements in production code

### Production Readiness Validation

Run the Ready Tensor validator to confirm 100% score:

```bash
cd Project2v2
python ops/validate_repo.py
```

**Expected result:**
```
Repository Validation Summary
         docs: 100.0 %
        tests: 100.0 %
   automation: 100.0 %
      overall: 100.0 %
All thresholds satisfied.
```

### Evidence Documentation

For complete verification details, including test output, manual test procedures, and Docker compatibility analysis, see:

📄 **[docs/evidence/phase3_verification.md](docs/evidence/phase3_verification.md)**

This document provides:
- Full pytest output (24/24 tests passing)
- Manual test scenarios with exact commands and observed results
- Exception type validation with code samples
- Logging format confirmation
- Ready Tensor validator results
- Docker compatibility analysis
- Reproducibility commands for reviewers

---

_Remember to update this document whenever operational characteristics change (timeouts, health checks, deployment scripts, etc.)._
