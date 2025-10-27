# Changelog

## v3.0-module3-final (October 27, 2025) - Tag: v3.0-module3 - Latest Commit: 2e2c4a3

**SecureEval + Ops integration with repository cleanup and production hardening.**

### Latest Updates (Commit 1aa4474)
- **Repository Cleanup**: Removed Python cache files, coverage artifacts (32 files cleaned)
- **Import Path Fixes**: Updated absolute imports to relative imports for better modularity
- **Production Hardening**: Added comprehensive .gitignore, validated 29/29 tests passing
- **CI Pipeline Verified**: GitHub Actions working with green checks after cleanup

**SecureEval + Ops integration (validation, sandboxing, resilience, structured logging, health probes, CI pipeline).**

### New Features
- **Phase 3: CI/CD Pipeline** - GitHub Actions workflow with pytest coverage, pip-audit security scanning, repository validator integration
- **Phase 4: Evidence Bundle** - Complete documentation with OPERATIONS.md, SECURITY.md, and publication-ready evidence artifacts
- **Ops Layer** - Structured JSON logging with run IDs, FastAPI health endpoints (/healthz, /readyz), retry/timeout resilience
- **Security Layer** - Input validation via Pydantic, sandbox execution allowlist, output clamping, secrets redaction policy
- **SOC 2-Lite Controls** - Complete mapping across Security, Availability, Processing Integrity, Confidentiality, Privacy

### Technical Achievements
- **Repository Validator**: 100% scores across docs, tests, automation categories
- **Test Coverage**: 79% ops package coverage (11/11 tests passing, focused scope on Project2v2.app)
- **CI/CD Pipeline**: GitHub Actions with green check validation - Run 18850725946
- **Documentation**: Complete OPERATIONS.md and SECURITY.md with real implementation details
- **Evidence Bundle**: Populated with actual artifacts (coverage reports, health probes, JSON logs, CI workflow)
- **Parity Maintained**: No user-facing UX changes, identical observable behavior preserved

### Implementation Details
- CI gate: `python-ci` workflow runs tests, coverage, security audit, and rubric validator on every PR
- Structured logs: `{"ts": "ISO-8601", "level": "INFO", "run_id": "uuid", "logger": "root", "msg": "text"}`
- Health probes: Liveness and readiness endpoints for operational monitoring
- Security controls: Input validation, sandbox allowlist (git/python/pip), 10k character output clamping
- Resilience: Retry with exponential backoff (max_tries=3, backoff=0.5s), 120s timeout wrappers
