![Trust_Bench Logo](docs/images/logo.png)

# Trust_Bench – Multi-Agent Security Evaluation Framework

> Coordinated LangGraph agents audit source repositories for secrets, quality gaps, and documentation risks.

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg) ![Status](https://img.shields.io/badge/status-active-green.svg) ![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## Project Overview

Trust_Bench (Project2v2) is a refactored multi-agent evaluation harness that inspects software repositories for security leakage, code hygiene, and documentation readiness. It leverages LangGraph to orchestrate domain-specific agents, each backed by deterministic Python tools so the framework can operate with or without external LLM providers. The system focuses on AI security evaluation, emphasizing inter-agent collaboration and explainable scoring.

## System Architecture

Agents cooperate through a LangGraph state machine where the Manager plans work, specialized agents execute tooling, and finalization aggregates scores into human-readable reports.

```
[Manager Plan]
      │
      ▼
[Security Agent] ──alerts──► [Quality Agent] ──metrics──► [Documentation Agent]
      │                                                            │
      └──────────────collaboration messages────────────────────────┘
      ▼
[Manager Finalize] → report.json / report.md
```

- **Orchestration layer:** LangGraph `StateGraph` (`multi_agent_system/orchestrator.py`)
- **Communication:** explicit message passing captured in shared memory and appended conversation logs
- **Shared context:** security findings and quality metrics feed downstream scoring adjustments

## Agent Roles and Responsibilities

| Agent | Purpose | Inputs | Outputs | Key Tools |
|-------|---------|--------|---------|-----------|
| **Manager (plan/finalize)** | Defines task list, aggregates results, records collaboration metrics | Repository root path | `report.json`, conversation log, summary score | LangGraph state management |
| **SecurityAgent** | Scan repository for secrets and credential leaks | Repo filesystem | Risk level, list of matches, notifications to other agents | `run_secret_scan` (regex-driven secret scanner) |
| **QualityAgent** | Assess code structure, language diversity, and test coverage | Repo structure + SecurityAgent alerts | Quality score, language histogram, test ratio | `analyze_repository_structure` |
| **DocumentationAgent** | Evaluate README coverage and cross-reference quality/security context | README files, shared metrics | Documentation score, collaboration adjustments | `evaluate_documentation` |

## Tool Integrations

| Tool | Description | Consuming Agent | Capability Extension |
|------|-------------|-----------------|----------------------|
| `run_secret_scan` | Regex-based detector for high-signal secrets (AWS, GitHub, Slack, RSA keys) | SecurityAgent | Security posture signal without third-party services |
| `analyze_repository_structure` | Counts files, detects languages, estimates test coverage | QualityAgent | Structural quality metrics feeding documentation evaluation |
| `evaluate_documentation` | Parses README variants, tracks sections and word count | DocumentationAgent | Measures documentation completeness and supports collaboration penalties |
| `serialize_tool_result` | Utility to convert tool dataclasses into message payloads | All agents | Ensures structured data exchange within LangGraph state |

_(No MCP tools are bundled in the current Project2v2 snapshot.)_

## Installation & Setup

```powershell
git clone https://github.com/mwill20/Trust_Bench.git
cd Trust_Bench\Project2v2
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-phase1.txt
pip install -r requirements-optional.txt  # optional extras
copy .env_example .env
# Populate OPENAI_API_KEY / GROQ_API_KEY / GEMINI_API_KEY as desired
```

- Requires **Python 3.10+**
- Core dependencies live in `Project2v2/requirements-phase1.txt`; optional extras live in `Project2v2/requirements-optional.txt`
- A compatibility shim (`requirements.txt`) still installs the phase 1 set
- Environment variables are documented in `Project2v2/.env_example`
- Optional extras currently include `ragas`, `semgrep`, and `streamlit` to support RAG evaluation, static analysis, and dashboard demos.

## Running the System

### Web Interface (recommended)
```powershell
.\.venv\Scripts\activate
python web_interface.py
# Navigate to http://localhost:5000 and submit a GitHub repo URL
```

### CLI Batch Audit
```powershell
python main.py --repo .. --output output
```

### Windows Helpers
```powershell
.\run_audit.ps1 ..  # PowerShell wrapper
run_audit.bat ..    # CMD wrapper
```

The CLI and web flows generate timestamped folders `github_analysis_*` containing:

- `report.json` – structured scores, conversation log, collaboration metrics
- `report.md` – human-readable summary

_Legacy Trust_Bench commands such as `python -m trustbench_core.eval.evaluate_agent` (fake vs. real provider) are not yet ported; see README_GAP_PLAN.md._

## Evaluation Metrics / Pillars

| Metric | Description | Current Status |
|--------|-------------|----------------|
| **Faithfulness** | Deterministic heuristic comparing each agent’s summary to the evidence returned by its tooling (persisted at `metrics.faithfulness`) | Implemented |
| **System Latency** | Wall-clock run time plus per-agent/per-tool timings stored under `metrics.system_latency_seconds` and `metrics.per_agent_latency` | Implemented |
| **Refusal Accuracy** | Offline policy harness that simulates unsafe prompts and records refusal ratio at `metrics.refusal_accuracy` | Implemented (LLM integrations fallback to simulated refusals) |
| **Injection Block Rate** | Prompt-injection detection effectiveness | `sanitize_prompt` + frontend guards (qualitative) |
| **Security Scan Findings** | Count of leaked secrets | Available via `report.json > agents.SecurityAgent.details.matches` |

Each run now writes a `metrics` block to `output/report.json` (or the chosen output folder) and a Markdown metrics table to `output/report.md`, capturing overall system latency, averaged faithfulness, refusal accuracy, and per-agent/per-tool timing breakdowns.

Example excerpt (from `output/report.json`):

```json
{
  "summary": {"overall_score": 35.36, "grade": "needs_attention"},
  "agents": {
    "SecurityAgent": {"score": 0.0, "summary": "Scanned 694 files and detected 38 potential secret hit(s)."},
    "QualityAgent": {"score": 40.57, "summary": "Indexed 700 files across 6 language group(s); 50 appear to be tests."},
    "DocumentationAgent": {"score": 65.51, "summary": "Found 1 README file(s) with roughly 43 words."}
  }
}
```

## File Structure

```
Trust_Bench/
├── Project2v2/
│   ├── assets/images/TrustBench.png
│   ├── multi_agent_system/
│   │   ├── agents.py
│   │   ├── orchestrator.py
│   │   ├── tools.py
│   │   └── types.py
│   ├── tests/test_security_utils.py
│   ├── llm_utils.py
│   ├── security_utils.py
│   ├── main.py
│   ├── web_interface.py
│   ├── requirements-phase1.txt
│   ├── requirements-optional.txt
│   └── output/ (latest report artifacts)
├── README.md (legacy)
└── READMEv2.2.md
```

_Legacy trustbench_core / trust_bench_mcp modules are not included in this refactored workspace._

## MCP Server (Status)

No MCP server entry point ships with Project2v2. The historical MCP server (`trust_bench_mcp/trust_bench_server.py`) referenced in Module 2 is absent; integration guidance will be added once the server is restored (see README_GAP_PLAN.md).

## Results / Reports

- Latest run artifacts: `Project2v2/output/report.json` and `Project2v2/output/report.md`
- Timestamped archives: `Project2v2/github_analysis_*`
- Sample highlight: security scan flagged 38 secret-like strings (mostly seeded test keys), resulting in an overall `needs_attention` grade.
- Placeholder for visuals: ![Report Screenshot Placeholder](docs/images/report_preview.png)

## Limitations & Next Steps

- LLM provider integration is optional but not fully wired; metrics such as faithfulness or refusal accuracy require future enhancements.
- MCP server, fake-provider sim, and advanced dashboards are missing from this snapshot.
- Report generation currently leans on deterministic tooling; incorporating auto-remediation suggestions is a planned improvement.
- Cleanup of historical `github_analysis_*` folders is recommended before packaging releases.

## Credits & References

- Ready Tensor AI Agent Course – Module 2 (Multi-Agent Evaluation)
- LangGraph – stateful agent orchestration
- CrewAI / AutoGen (inspiration for collaborative patterns)
- Semgrep & OpenAI (referenced for future integrations)
- Contributors: Project2v2 refactor by @mwill20 and collaborators

## Security Enhancements & Evaluations

Recent hardening work includes:

- `security_utils.py` – prompt-injection heuristics, API-key masking, HTML escaping
- Frontend sanitization mirroring backend filters for repo URLs and chat prompts
- Tooling-driven secret scans highlighting high-signal credential leaks

Planned dashboards / graphs: ![Security Metrics Placeholder](docs/images/security_dashboard.png)

---

_For outstanding rubric gaps and remediation steps, see `README_GAP_PLAN.md`._
