| Missing Item | How to Fix | Owner | Priority |
|--------------|------------|-------|----------|
| Separate dependency manifests (`requirements-phase1.txt`, `requirements-optional.txt`) | Split the current `Project2v2/requirements.txt` into phase-specific files reflecting minimal and optional extras, then update setup docs and CI to reference them. | @mwill20 | Medium |
| Legacy CLI entry points (`trustbench_core.eval.evaluate_agent`, fake provider flag) | Restore or stub the historical `trustbench_core` package, wiring it to the current agents, and implement `TRUSTBENCH_FAKE_PROVIDER` toggle so rubric commands execute. | @mwill20 | High |
| MCP server module (`trust_bench_mcp/trust_bench_server.py`) | Port the previous MCP server into the repository (or scaffold a new one) and document startup/configuration for Claude Desktop or Cursor. | @mwill20 | High |
| Metric instrumentation (faithfulness, latency, refusal accuracy) | Add telemetry hooks around agent execution, compute metrics, and store them alongside existing scores; surface results in `report.json`. | @mwill20 | High |
| Security dashboards / visuals | Capture report screenshots or generate HTML previews saved under `docs/images/` to replace placeholders in READMEv2.2. | @mwill20 | Low |
| Repository cleanup automation | Script removal/archival of historical `github_analysis_*` folders and add guidance in documentation. | @mwill20 | Low |
