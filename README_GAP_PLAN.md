| Missing Item | How to Fix | Owner | Priority |
|--------------|------------|-------|----------|
| Legacy CLI entry points (`trustbench_core.eval.evaluate_agent`, fake provider flag) | Restore or stub the historical `trustbench_core` package, wiring it to the current agents, and implement `TRUSTBENCH_FAKE_PROVIDER` toggle so rubric commands execute. | @mwill20 | High |
| ~~MCP server module (`trust_bench_mcp/trust_bench_server.py`)~~ | **Deprecated for Project2v2:** LangGraph tooling provides required integrations; MCP will be reconsidered if cross-client interoperability is needed. | @mwill20 | ✅ |
| ~~Metric instrumentation (faithfulness, latency, refusal accuracy)~~ | **Completed (2025-10-20):** Metrics recorded in `metrics.*` within `report.json`/`report.md`, including latency, faithfulness, refusal accuracy, and per-agent timings. | @mwill20 | ✅ |
| Security dashboards / visuals | Capture report screenshots or generate HTML previews saved under `docs/images/` to replace placeholders in READMEv2.2. | @mwill20 | Low |
| Repository cleanup automation | Script removal/archival of historical `github_analysis_*` folders and add guidance in documentation. | @mwill20 | Low |
