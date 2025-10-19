# Project 2 – Multi-Agent Repository Auditor

This directory contains the minimal, self-contained implementation that fulfils the Project&nbsp;2 rubric. Everything you need to run and evaluate the multi-agent workflow lives here.

## What’s Inside

- `main.py` – CLI entry point that wires LangGraph, executes the workflow, and writes reports.
- `multi_agent_system/` – Lightweight package with tools, agents, orchestration logic, and reporting helpers.
- `requirements.txt` – Focused dependency list (LangGraph only).

## Setup

```powershell
python -m venv .venv          # optional but recommended
.\.venv\Scripts\activate
pip install -r requirements.txt
```

If you already installed dependencies at the repository root, you can reuse that environment.

## Run the Workflow

From this directory:

# Project 2 – Multi-Agent Repository Auditor

This directory contains the minimal, self-contained implementation that fulfils the Project&nbsp;2 rubric. Everything you need to run and evaluate the multi-agent workflow lives here.

## 🚀 Quick Start - Choose Your Interface

### Option 1: Interactive Launcher (Recommended)
Double-click `launch.bat` for a menu with multiple options:
- Command Line Interface
- Web Interface 
- Quick analysis presets

### Option 2: Web Interface
```powershell
python web_interface.py
```
Then open http://localhost:5000 in your browser for a beautiful web UI.

### Option 3: Command Line
```powershell
python main.py --repo .. --output output
```

### Option 4: Batch Scripts
```powershell
# Windows Batch
run_audit.bat .                    # Analyze current directory
run_audit.bat ..                   # Analyze parent directory  
run_audit.bat "C:\path\to\repo"    # Analyze specific path

# PowerShell
.\run_audit.ps1 .                  # Analyze current directory
.\run_audit.ps1 .. my_output       # Custom output directory
```

## What's Inside

- `main.py` – CLI entry point that wires LangGraph, executes the workflow, and writes reports.
- `web_interface.py` – Beautiful web UI for easy repository analysis
- `launch.bat` – Interactive launcher with multiple interface options
- `run_audit.bat` / `run_audit.ps1` – Convenient wrapper scripts
- `multi_agent_system/` – Lightweight package with tools, agents, orchestration logic, and reporting helpers.
- `requirements.txt` – Focused dependency list (LangGraph + Flask).

## Setup

```powershell
python -m venv .venv          # optional but recommended
.\.venv\Scripts\activate
pip install -r requirements.txt
```

If you already installed dependencies at the repository root, you can reuse that environment.

## Example Results

### Trust_Bench_Clean Analysis
- **Overall Score:** 35.36/100 ("needs_attention")
- **Security:** Found 38 potential secrets
- **Quality:** 700 files, 7.1% test coverage
- **Documentation:** Basic README (43 words)

### Project2v2 Self-Analysis  
- **Overall Score:** 61.33/100 ("fair")
- **Security:** Clean (2 regex patterns detected)
- **Quality:** 11 files, no tests
- **Documentation:** Good README (271 words, 4 sections)

## Deliverables Checklist (Rubric Mapping)

- ✅ **Main orchestrator script**: `main.py`
- ✅ **At least 3 agents**: Manager, SecurityAgent, QualityAgent, DocumentationAgent
- ✅ **At least 3 tools**: secret scan, repository structure analysis, documentation review
- ✅ **Inter-agent communication**: logged conversation stored in the report
- ✅ **Tangible output**: JSON + Markdown summary in the output directory
- ✅ **README & requirements**: this document with clear setup/run steps
- ⭐ **Security emphasis**: high-signal credential scanner baked into the workflow
- 🎯 **User-friendly interfaces**: Web UI, batch scripts, interactive launcher

You now have a clean, runnable package that can be copied, zipped, or submitted independently of the legacy Trust Bench stack.

- `--repo` (optional) points to the repository you want to audit. Defaults to the parent directory (`..`).  
- `--output` (optional) sets where the generated `report.json` and `report.md` should be written. Defaults to `./output`.

Example console output:

```
=== Multi-Agent Evaluation Complete ===
Repository: C:\Projects\Trust_Bench_Clean
Overall Score: 46.86
Grade: needs_attention
Report (JSON): C:\Projects\Trust_Bench_Clean\Project2v2\output\report.json
Report (Markdown): C:\Projects\Trust_Bench_Clean\Project2v2\output\report.md
```

## Deliverables Checklist (Rubric Mapping)

- ✅ **Main orchestrator script**: `main.py`
- ✅ **At least 3 agents**: Manager, SecurityAgent, QualityAgent, DocumentationAgent
- ✅ **At least 3 tools**: secret scan, repository structure analysis, documentation review
- ✅ **Inter-agent communication**: logged conversation stored in the report
- ✅ **Tangible output**: JSON + Markdown summary in the output directory
- ✅ **README & requirements**: this document with clear setup/run steps
- ⭐ **Security emphasis**: high-signal credential scanner baked into the workflow

You now have a clean, runnable package that can be copied, zipped, or submitted independently of the legacy Trust Bench stack.
