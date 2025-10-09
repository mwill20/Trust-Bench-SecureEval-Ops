TrustBench tool bundle prototypes (hardening and glue helpers).

Contents:
- `tools_security.py`: hardened tools (`download_and_extract_repo`, `env_content`, `secrets_scan`, registry wiring).
- `agent_tools_glue.py`: reference glue layer for routing tool calls within a LangGraph or similar agent loop.

Usage:
- Copy or import these helpers into your agent project.
- Replace the LLM stub with your production model client for tool-selection decisions.
- Run tests against the fixtures in `datasets/golden` to validate detection and masking behaviour.
