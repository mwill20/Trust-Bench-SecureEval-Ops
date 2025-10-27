# SECURITY & SAFETY OVERVIEW

> This living document captures Trust Bench SecureEval + Ops safety controls.
> Phase 0 establishes baseline policies; future phases will replace TODO markers with concrete enforcement details.

## Input Validation
- `app/security/guardrails.py` uses Pydantic models (`RepoInput`) to validate audit payloads.
- Both `repo_url` (HttpUrl) and `repo_path` inputs are type-checked; malformed payloads raise informative validation errors.

## Output Clamping & Guardrails
- `clamp_output` enforces a 10k character ceiling for outbound text (reports, summaries).
- Future phases will extend clamping to streamed chat responses and refusal policies.

## Command Allowlist & Sandbox Strategy
- `app/security/sandbox.py` introduces `safe_run`, limiting subprocess calls to allowlisted binaries (`git`, `python`, `pip`).
- Commands outside the allowlist return exit code 126 with an explanatory message; timeouts return 124.
- Containerization and OS-level sandboxing will be evaluated in future phases.

## Sensitive Data Redaction
- Structured logs intentionally omit secrets; run IDs are random UUIDs for tracing, not user identifiers.
- UI/API layers must continue to mask API keys before logging (see `web_interface.py`).

## Secret Handling Policy
- API keys for LLM providers enter via `.env` or UI form fields and are stored only in memory.
- Keys are never logged; the web interface masks credentials before echoing status messages.
- Future phases will add integration tests to assert redaction behavior.

## Dependency & Vulnerability Management
- `requirements.txt` remains pinned; SecureEval introduces retry/timeouts without adding third-party deps.
- `pip-audit` integration is planned for Phase 2 alongside Ops instrumentation.

## SOC 2-Lite Control Mapping

| SOC 2 Criterion      | Implementation in Trust Bench SecureEval + Ops | Status |
| -------------------- | ----------------------------------------------- | ------ |
| Security             | Guardrails validate payloads, clamp reports, and block untrusted subprocess calls. | In place |
| Availability         | Liveness (/healthz) and readiness (/readyz) endpoints exposed for probe integration. | In place |
| Processing Integrity | Deterministic workflow captured via golden fixtures and parity tests. | In place |
| Confidentiality      | Secrets injected through environment variables and never persisted to disk. | In place |
| Privacy              | No end-user data retained beyond session memory. | In place |

---

_Update this file alongside any security-related pull request to keep publication evidence accurate._
