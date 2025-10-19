# Project 2 – Multi-Agent Repository Auditor

This directory contains the minimal, self-contained implementation that fulfils the Project&nbsp;2 rubric. Everything you need to run and evaluate the multi-agent workflow lives here.

## 🤝 Enhanced Agent Collaboration

Our multi-agent system features **intelligent collaboration** where agents actively communicate and influence each other's assessments:

### Cross-Agent Intelligence
- **SecurityAgent → QualityAgent**: Quality scores are automatically reduced when security issues are detected (up to 25-point penalty)
- **QualityAgent → DocumentationAgent**: Documentation assessment incorporates code quality metrics (file counts, test coverage)
- **SecurityAgent → DocumentationAgent**: Documentation scores are penalized when security issues aren't addressed in docs
- **Direct Agent Communication**: Agents send contextual messages to each other with structured data

### Collaborative Decision Making
- Quality Agent adjusts scoring based on security findings: `"Adjusted quality score down by 25 points due to 5 security finding(s) from SecurityAgent"`
- Documentation Agent considers both quality metrics and security context: `"No tests found by QualityAgent - documentation lacks testing info"`
- All cross-agent communications are logged in detailed conversation histories
- Final scores reflect collaborative intelligence, not just individual tool outputs

### Example Collaboration Flow
```
SecurityAgent → QualityAgent: "FYI: Found 5 security issues that may impact quality assessment"
QualityAgent → SecurityAgent: "Incorporated your 5 security findings into quality assessment"
DocumentationAgent → SecurityAgent: "Noted your 5 findings - documentation lacks security guidance"
```

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
Then open http://localhost:5000 in your browser for a beautiful web UI with real-time collaboration visualization.

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
- `web_interface.py` – Beautiful web UI with real-time agent progress and collaboration visualization
- `launch.bat` – Interactive launcher with multiple interface options
- `run_audit.bat` / `run_audit.ps1` – Convenient wrapper scripts
- `multi_agent_system/` – Lightweight package with collaborative agents, orchestration logic, and reporting helpers.
  - `agents.py` – SecurityAgent, QualityAgent, DocumentationAgent with cross-communication
  - `orchestrator.py` – LangGraph workflow with collaboration tracking
  - `tools.py` – Secret scanning, structure analysis, documentation review tools
  - `types.py` – Shared data structures and messaging protocols
- `requirements.txt` – Focused dependency list (LangGraph + Flask).

## Setup

```powershell
python -m venv .venv          # optional but recommended
.\.venv\Scripts\activate
pip install -r requirements.txt
```

If you already installed dependencies at the repository root, you can reuse that environment.

## Agent Collaboration in Action

### 🛡️ SecurityAgent (Proactive Communication)
- Scans for AWS keys, GitHub tokens, private keys, etc.
- **Collaborates by**: Immediately notifying other agents of security findings
- **Impact**: Influences quality and documentation scoring based on security context

### 🔍 QualityAgent (Security-Aware Assessment)  
- Analyzes code structure, languages, and test coverage
- **Collaborates by**: Adjusting scores based on SecurityAgent findings
- **Impact**: Reduces quality score when security issues detected (more realistic assessment)

### 📝 DocumentationAgent (Context-Aware Scoring)
- Reviews README files, counts sections, checks completeness
- **Collaborates by**: Using QualityAgent metrics and SecurityAgent alerts
- **Impact**: Penalizes documentation that doesn't address testing or security gaps

### 🤖 Manager (Collaboration Orchestrator)
- Coordinates all agents and tracks cross-communications
- **Reports**: Number of collaborative interactions and their impact on final scores
- **Transparency**: Full conversation log showing agent-to-agent decision making

## Example Collaborative Results

### Collaboration Metrics from Recent Run:
```
Grade: NEEDS_ATTENTION (30.0 pts)
Agents collaborated on 5 cross-communications:
- Security findings influenced quality and documentation scores
- Quality assessment incorporated security analysis  
- Documentation score adjusted based on quality metrics
```

### Individual Agent Adjustments:
- **QualityAgent**: `"Adjusted for 5 security findings"` (25-point reduction)
- **DocumentationAgent**: `"Adjusted based on quality metrics"` + `"Adjusted for security gaps"` (10-point total reduction)

## Example Results

### Trust_Bench_Clean Analysis (Collaborative Assessment)
- **Overall Score:** ~30/100 ("needs_attention")
- **Security:** 5 potential secrets detected → Influences other agents
- **Quality:** 53 files, 0% test coverage → Penalizes documentation
- **Documentation:** Good content but lacks security/testing guidance → Score reduced

### Project2v2 Self-Analysis (Collaborative Assessment)
- **Overall Score:** ~61/100 ("fair") 
- **Security:** Clean (minimal findings) → No cross-agent penalties
- **Quality:** 53 files, no dedicated tests → Affects documentation assessment
- **Documentation:** Good README but collaboration reveals testing gaps

## Deliverables Checklist (Rubric Mapping)

- ✅ **Main orchestrator script**: `main.py`
- ✅ **At least 3 agents**: Manager, SecurityAgent, QualityAgent, DocumentationAgent
- ✅ **At least 3 tools**: secret scan, repository structure analysis, documentation review
- ✅ **Inter-agent communication**: Enhanced with direct agent-to-agent messaging and collaborative scoring
- ✅ **Tangible output**: JSON + Markdown summary in the output directory with collaboration metrics
- ✅ **README & requirements**: this document with clear setup/run steps
- ⭐ **Security emphasis**: high-signal credential scanner with cross-agent impact
- 🎯 **User-friendly interfaces**: Web UI, batch scripts, interactive launcher
- 🤝 **Advanced Collaboration**: Agents influence each other's assessments for more intelligent results

## Command Line Usage

- `--repo` (optional) points to the repository you want to audit. Defaults to the parent directory (`..`).  
- `--output` (optional) sets where the generated `report.json` and `report.md` should be written. Defaults to `./output`.

Example console output showing collaboration:

```
=== Multi-Agent Evaluation Complete ===
Repository: C:\Projects\Trust_Bench_Clean\Project2v2
Overall Score: 30.0
Grade: needs_attention
Report (JSON): C:\Projects\Trust_Bench_Clean\Project2v2\collaboration_test\report.json
Report (Markdown): C:\Projects\Trust_Bench_Clean\Project2v2\collaboration_test\report.md
```

## What Makes This Special

🧠 **Intelligent Collaboration**: Unlike simple multi-agent systems, our agents actually influence each other's decisions in real-time

📊 **Contextual Scoring**: Final scores reflect cross-domain insights (security impacts quality, quality impacts documentation)

🔍 **Full Transparency**: Complete conversation logs show exactly how agents collaborated to reach their assessments

🚀 **Multiple Interfaces**: From simple double-click launcher to sophisticated web UI with real-time progress

You now have a clean, runnable package that demonstrates advanced multi-agent collaboration and can be copied, zipped, or submitted independently of the legacy Trust Bench stack.