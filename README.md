# Trust Bench – Multi-Agent Security Evaluation Framework

![Version](https://img.shields.io/badge/version-Project2v2-blue)

Trust Bench (Project2v2) is a deterministic, LangGraph-based multi-agent workflow that inspects software repositories for security leakage, code quality gaps, and documentation health. The system emphasizes cross-agent collaboration, transparent reasoning, and reproducible outputs that graders can run entirely offline.

## Contents
1. [Overview](#overview)
2. [Tool Integrations](#tool-integrations)
3. [Installation & Setup](#installation--setup)
4. [Running the System](#running-the-system)
5. [Evaluation Metrics Instrumentation](#evaluation-metrics-instrumentation)
6. [Reporting Outputs](#reporting-outputs)
7. [Example Results (Project2v2 self-audit)](#example-results-project2v2-self-audit)
8. [MCP Server (Scope Decision)](#mcp-server-scope-decision)
9. [File Structure (trimmed)](#file-structure-trimmed)
10. [Security & Hardening Notes](#security--hardening-notes)
11. [Credits & References](#credits--references)

---

## Overview

- **Agents**: Manager (plan/finalize), SecurityAgent, QualityAgent, DocumentationAgent  
- **Core Tools**: regex secret scanner, repository structure analyzer, documentation reviewer  
- **Collaboration**: agents exchange messages and adjust scores based on peer findings (security alerts penalise quality and documentation; quality metrics influence documentation, etc.)  
- **Deliverables**: JSON + Markdown reports with composite scores, agent summaries, conversation logs, and instrumentation metrics

```
[Manager Plan]
     |
[SecurityAgent] → alerts → [QualityAgent] → metrics → [DocumentationAgent]
     |                                                   |
     └──────────── shared context & collaboration ───────┘
             |
       [Manager Finalize] → report.json / report.md
```

---

## Tool Integrations

| Tool | Consumed By | Capability Extension |
|------|-------------|----------------------|
| `run_secret_scan` | SecurityAgent | Detects high-signal credentials (AWS, GitHub, RSA keys) |
| `analyze_repository_structure` | QualityAgent | Counts files, languages, estimated test coverage |
| `evaluate_documentation` | DocumentationAgent | Scores README variants by coverage and cross-agent context |
| `serialize_tool_result` | All agents | Normalises tool dataclasses for message passing |

> MCP endpoints are intentionally **not** shipped in Project2v2. See “MCP Server (Scope Decision)” below.

---

## Installation & Setup

```powershell
git clone https://github.com/mwill20/Trust_Bench.git
cd Trust_Bench
python -m venv .venv          # optional but recommended
.\.venv\Scripts\activate
pip install -r Project2v2/requirements-phase1.txt
pip install -r Project2v2/requirements-optional.txt  # extras: ragas, semgrep, streamlit
copy Project2v2\.env_example .env                    # populate provider keys if desired
```

If you prefer to run entirely offline, leave API keys empty; all analyses will still complete deterministically.

Environment variables (for web UI / LLM chat):

- `LLM_PROVIDER` (default `openai`; options: `openai`, `groq`, `gemini`)
- `OPENAI_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY` (as required by provider)
- `ENABLE_SECURITY_FILTERS` (defaults to `true` for prompt/repo sanitisation)

---

## Running the System

### Web Interface (recommended)
```powershell
cd Project2v2
python web_interface.py
# browse to http://localhost:5000
```

### Direct CLI
```powershell
cd Project2v2
python main.py --repo .. --output output
```

### Legacy CLI (kept for rubric compatibility)
```powershell
python -m trustbench_core.eval.evaluate_agent --repo <path> --output Project2v2/output
```
This forwards to `Project2v2/main.py`; the new entrypoint remains the single source of truth.

### Convenience Scripts
```powershell
cd Project2v2
.\run_audit.ps1 .. my_output   # PowerShell
run_audit.bat ..               # Windows CMD
launch.bat                     # Interactive menu (web UI, CLI, presets)
```

---

## Evaluation Metrics Instrumentation

Every run records deterministic metrics alongside agent results:

- **System latency** – overall wall-clock time plus per-agent/per-tool timings (`metrics.system_latency_seconds`, `metrics.per_agent_latency`)
- **Faithfulness** – heuristic alignment of summaries with tool evidence (`metrics.faithfulness`)
- **Refusal accuracy** – simulated unsafe prompt harness (returns 1.0 while LLM calls are disabled) (`metrics.refusal_accuracy`)

Metrics appear in both `report.json` (under `metrics`) and `report.md` (rendered table). Example CLI output:

```
System Latency: 0.08 seconds
Faithfulness: 0.62
Refusal Accuracy: 1.0
Per-Agent Timings:
  - SecurityAgent: 0.07 seconds
  - QualityAgent: 0.003 seconds
  - DocumentationAgent: 0.002 seconds
```

---

## Reporting Outputs

Each audit (web or CLI) produces:

- `report.json` – timestamp, repo path, composite summary, per-agent results, metrics, full conversation log  
- `report.md` – human-readable summary with agent cards, instrumentation metrics, conversation log  
- Optional timestamped archives (`github_analysis_*`) when launched through the web interface

---

## Example Results (Project2v2 self-audit)

- Overall Score: ~32/100 (“needs_attention”)  
- Security: seeded secrets detected (score 0) → drives collaboration penalties  
- Quality: medium score, automatically penalised by SecurityAgent findings  
- Documentation: strong base score but reduced for missing security/testing guidance  
- Collaboration: >5 cross-agent messages; Manager summarises adjustments in the final log

---

## MCP Server (Scope Decision)

Project2v2 prioritises deterministic, offline-capable tooling. To keep grading reproducible and avoid external runtime dependencies, the earlier MCP server has been **intentionally deprecated** for this version. Required tool integrations (three or more) are provided as direct Python callables. MCP can be revisited later if cross-client interoperability (Claude Desktop, Cursor, etc.) becomes necessary, but it is **not required** for Module 2 compliance.

---

## File Structure (trimmed)

```
Trust_Bench/
├── Project2v2/
│   ├── main.py
│   ├── web_interface.py
│   ├── multi_agent_system/
│   │   ├── agents.py
│   │   ├── orchestrator.py
│   │   ├── tools.py
│   │   ├── reporting.py
│   │   └── types.py
│   ├── requirements-phase1.txt
│   ├── requirements-optional.txt
│   ├── run_audit.(bat|ps1), launch.bat
│   └── output/ (latest reports)
├── trustbench_core/…  (legacy CLI wrapper → Project2v2/main.py)
└── Project2v2/checklist.yaml (optional-features register)
```

---

## Security & Hardening Notes

- All detected secrets are synthetic and included solely for demonstration purposes — no real credentials are exposed.
- `security_utils.py` and the web UI sanitise repository URLs, prompts, and API keys.
- Optional extras (`ragas`, `semgrep`, `streamlit`) enable deeper analytics and dashboarding when desired.

---

## Credits & References

- Ready Tensor AI Agent Course – Module 2 (Multi-Agent Evaluation)  
- LangGraph, CrewAI, AutoGen (collaboration inspiration)  
- Semgrep, OpenAI/Groq/Gemini APIs (referenced integrations)  
- Project2v2 implementation by @mwill20 and collaborators
