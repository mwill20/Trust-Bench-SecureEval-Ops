<!-- LKG SHA (production): 7a6251b -->

<div align="center">
  <img src="Project2v2/assets/images/TrustBench.png" alt="Trust Bench" width="300" />
</div>

<p align="center">
  <a href="https://github.com/mwill20/Trust-Bench-SecureEval-Ops/actions/workflows/python-ci.yml">
    <img src="https://github.com/mwill20/Trust-Bench-SecureEval-Ops/actions/workflows/python-ci.yml/badge.svg" alt="CI Pipeline" />
  </a>
  <a href="docs/evidence/coverage.txt">
    <img src="https://img.shields.io/badge/coverage-79%25-brightgreen.svg" alt="Test Coverage" />
  </a>
  <a href="https://app.readytensor.ai/publications/trust-bench-secureeval-ops-v30-production-grade-multi-agent-security-evaluation-framework-Gj5sQtaeBnZH">
    <img src="https://img.shields.io/badge/📖_Publication-ReadyTensor_v3.0-blue" alt="Official Publication v3.0" />
  </a>
</p>

# Trust Bench - Multi-Agent Security Evaluation Framework

<p align="center">
  <img src="https://img.shields.io/badge/version-v3.0--final-blue" alt="Version" />
  <img src="https://img.shields.io/badge/status-Production_Ready-green" alt="Status" />
</p>

## 🏗️ Architecture Overview

<div align="center">
  <img src="Project2v2/docs/evidence/architecture_v3.png" alt="Trust Bench SecureEval + Ops v3.0 Architecture" width="600" />
  <br/>
  <em>Trust Bench v3.0 Architecture: SecureEval envelope with Ops & Observability layer</em>
</div>

### 🎥 Demo Video
Watch the full Trust Bench SecureEval + Ops demo here:  
👉 [Trust Bench v3.0 Demo (1 min 45 s)](https://1drv.ms/v/c/2c8c41c39e8a63cb/ESYtX-fABvxAiHpMaXF7EpoBE9IqpsSJRF9m9_Sisyapkg?e=u4sjhv)

*A short walkthrough showing Trust Bench SecureEval + Ops v3.0 in action — identical UI, enhanced with security guardrails, resilience, structured logs, and health probes.*

Trust Bench (Project2v2) is a LangGraph-based multi-agent workflow that inspects software repositories for security leakage, code quality gaps, and documentation health. The system features intelligent agent routing with specialized personas, cross-agent collaboration, transparent reasoning, and reproducible outputs that graders can run entirely offline.

## 🚀 Latest Features

### Phase 1: Intelligent Agent Routing ✅ Complete
### Phase 2: Ops Layer ✅ Complete
- **🧾 Structured Logging**: JSON-formatted logs with run IDs via `Project2v2/app/logging.py`
- **🩺 Health Probes**: `/healthz` and `/readyz` FastAPI routes in `Project2v2/app/health.py`
- **🔍 Observability Tests**: `pytest Project2v2/tests/test_ops_layer.py` for log formatting & health endpoints
- **📊 Documentation Updates**: OPERATIONS.md logging/health guidance, SECURITY.md redaction policy
- **📈 CI Evidence**: Coverage + validator hooks ready for pipeline integration
### Phase 0: Parity Lock-In ✅ Complete
- **🧪 Golden Fixtures**: Canonical `report.json`, `report.md`, and `bundle.zip` locked in `tests/fixtures/`
- **🛡️ Parity Tests**: `pytest Project2v2/tests/test_parity.py` verifies JSON structure, markdown digest, and bundle contents
- **📦 Artifact Freeze**: `Project2v2/output/` mirrors fixtures to guarantee identical observable behavior for future phases
- **📓 Documentation Hooks**: `OPERATIONS.md` and `SECURITY.md` populated with Phase 0 baselines to evolve alongside new features
- **🛡️ Security Agent**: Specialized vulnerability assessment and risk analysis
- **⚡ Quality Agent**: Code quality improvements and best practices guidance  
- **📚 Documentation Agent**: Documentation generation and improvement suggestions
- **🎯 Orchestrator Agent**: General queries, project overview, and multi-agent coordination
- **Smart Routing**: LLM-powered question classification with confidence scoring

### Phase 1: SecureEval Layer ✅ Complete
- **🛡️ Input Guardrails**: Pydantic validation via `Project2v2/app/security/guardrails.py`
- **🔒 Sandbox Execution**: Allowlisted subprocess wrapper (`safe_run`) preventing arbitrary shell usage
- **♻️ Resilience Decorators**: Retry with exponential backoff + cross-platform timeout wrappers
- **🧪 Safety Tests**: `pytest Project2v2/tests/test_secure_eval.py` covering validation, sandboxing, and resilience paths
- **📘 Documentation**: SECURITY.md / OPERATIONS.md updated with Phase 1 safeguards and resilience defaults
### Phase 2: Multi-Agent Consultation ✅ Complete
- **🔄 Collaborative Analysis**: Complex queries automatically trigger multiple agents
- **🎯 Multi-Agent Detection**: System identifies when specialist consultation is needed
- **📋 Executive Synthesis**: Comprehensive responses combining insights from all relevant agents
- **🤝 Cross-Domain Queries**: Handle requests spanning security, quality, and documentation
- **Intelligent Orchestration**: Seamless coordination between specialist agents

### Phase 3: Advanced Orchestration ✅ Complete
- **🤝 Consensus Building**: Agents collaborate to reach agreements on complex assessments
- **⚔️ Conflict Resolution**: Systematic resolution of conflicting agent recommendations
- **🔄 Iterative Refinement**: Multiple rounds of analysis for nuanced scenarios
- **⚖️ Priority Negotiation**: Balance competing concerns (e.g., security vs maintainability)
- **🧠 Advanced Synthesis**: Unified recommendations from complex multi-agent negotiations
- **📊 Comprehensive Analysis**: Deep, multi-perspective evaluations with consensus metrics

### Phase 4: Custom Agent Weights ✅ Complete
- **🎛️ Interactive Weight Adjustment**: Real-time sliders for Security, Quality, and Documentation agent importance
- **⚖️ Weighted Scoring System**: Final evaluation scores calculated using custom agent weightings
- **📋 Preset Configurations**: Quick-select buttons for Security Focus, Quality Focus, Documentation Focus, and Balanced approaches
- **📈 Live Score Preview**: Real-time preview of how weight changes affect final evaluation scores
- **🔧 Flexible Integration**: Works seamlessly through web interface, CLI, and API with backward compatibility

### Phase 5: Agent Confidence Scoring ✅ Complete
- **📊 Confidence Calculations**: Advanced algorithms assess agent confidence based on response completeness, specificity, and score consistency
- **🎯 Visual Confidence Meters**: Color-coded progress bars (green/yellow/red) display confidence levels for each agent analysis
- **📋 Confidence Reporting**: Confidence scores included in JSON/Markdown reports with detailed breakdowns and visual indicators
- **🔍 Smart Recommendations**: System provides insights based on confidence levels to guide users toward more reliable agent outputs
- **⚡ Real-time Display**: Live confidence updates in web interface alongside analysis results with expandable details

### Phase 6: Enhanced UI Indicators ✅ Complete
- **🎯 Consensus Journey Visualization**: Complete timeline of agent negotiations with progress markers and round-by-round analysis
- **💬 Live Negotiation Highlights**: Speech bubbles showing actual agent conversations with mood indicators (green/yellow/red)
- **⚔️ Visual Conflict Resolution**: Before/after comparison panels displaying initial disagreements vs final negotiated results
- **🔄 Interactive Process Steps**: Expandable accordion cards for each negotiation round with detailed collaboration insights
- **📊 Agent Mood Mapping**: Real-time mood badges showing agreement, negotiation, and conflict states during consensus building
- **🎭 Authentic Agent Data**: All visualizations use genuine agent conversations and collaboration data, not simulated content

### Phase 7: Enhanced Export Features ✅ Complete
- **📦 Complete Analysis Bundles**: ZIP downloads containing JSON reports, Markdown summaries, and chat transcripts in one package
- **💬 Chat Export/Import**: Save and restore conversation histories with agent routing decisions and confidence scores
- **🔄 Session Continuity**: Import previous conversations to continue analysis or share findings with team members
- **📊 Multiple Download Options**: Individual JSON/Markdown reports (legacy) plus new enhanced bundles with chat data
- **🕐 Timestamped Archives**: UTC timestamps and metadata preservation for audit trails and team collaboration
- **🛡️ Secure File Handling**: Safe path validation and proper encoding for cross-platform compatibility

## Contents
1. [Overview](#overview)
2. [Tool Integrations](#tool-integrations)
3. [Installation & Setup](#installation--setup)
4. [Running the System](#running-the-system)
5. [Evaluation Metrics Instrumentation](#evaluation-metrics-instrumentation)
6. [Reporting Outputs](#reporting-outputs)
7. [Demo Video](#demo-video)
8. [Example Results (Project2v2 self-audit)](#example-results-project2v2-self-audit)
9. [MCP Server (Scope Decision)](#mcp-server-scope-decision)
10. [File Structure (trimmed)](#file-structure-trimmed)
11. [Security & Hardening Notes](#security--hardening-notes)
12. [Documentation Roadmap & Evidence](#documentation-roadmap--evidence)
13. [Credits & References](#credits--references)

---

## Overview

- **Agents**: Manager (plan/finalize), SecurityAgent, QualityAgent, DocumentationAgent  
- **Core Tools**: regex secret scanner, repository structure analyzer, documentation reviewer  
- **Collaboration**: agents exchange messages and adjust scores based on peer findings (security alerts penalize quality/documentation; quality metrics influence documentation, etc.)  
- **Deliverables**: JSON and Markdown reports containing composite scores, agent summaries, conversation logs, and instrumentation metrics

```
[Manager Plan]
     |
[SecurityAgent] --> alerts --> [QualityAgent] --> metrics --> [DocumentationAgent]
     \____________________________ shared context _____________________________/
                           |
                   [Manager Finalize] --> report.json / report.md
```

---

## Tool Integrations

| Tool | Consumed By | Capability Extension |
|------|-------------|----------------------|
| `run_secret_scan` | SecurityAgent | Detects high-signal credentials (AWS, GitHub, RSA keys) |
| `analyze_repository_structure` | QualityAgent | Counts files, languages, estimated test coverage |
| `evaluate_documentation` | DocumentationAgent | Scores README variants by coverage and cross-agent context |
| `serialize_tool_result` | All agents | Normalizes tool dataclasses for message passing |

> MCP endpoints are intentionally **not** shipped in Project2v2. See [MCP Server (Scope Decision)](#mcp-server-scope-decision).

---

## Prerequisites

Before installing Trust Bench SecureEval + Ops, ensure you have the following:

### System Requirements

- **Python**: 3.10 or later (3.11+ recommended for best performance)
- **Operating System**: 
  - Windows 10/11 (tested on Windows 11)
  - Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
  - macOS 11+ (Big Sur or later)
- **Hardware**: 
  - **RAM**: Minimum 4 GB, 8 GB recommended for large repositories
  - **Storage**: 2 GB free disk space for dependencies and analysis artifacts
  - **CPU**: No GPU required; runs on standard CPU architectures

### Required Software

- **Git**: Version 2.30+ for repository cloning
- **Python Package Manager**: pip 21+ (included with Python 3.10+)

### Network & Access Requirements

- **Outbound Internet Access**:
  - GitHub.com (for cloning public repositories)
  - LLM Provider APIs: OpenAI, Groq, or Gemini (for interactive chat features)
- **Permissions**: Read access to target repositories you want to analyze

### API Keys (Optional but Recommended)

For the **interactive web chat** and **agent consultation** features, you need at least one LLM provider API key:

- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
  - Recommended for best performance
  - Requires active billing/credits
- **Groq API Key** (Alternative, free tier available)
- **Gemini API Key** (Google's alternative)

> **Note**: The core evaluation features (security scan, quality analysis, documentation review) work **without any API keys**. API keys are only required for the chat/consultation interface.

### Knowledge Prerequisites

- **Basic Command Line**: Familiarity with terminal/PowerShell commands
- **Git Basics**: Understanding of repository cloning and navigation
- **Python Basics**: Ability to activate virtual environments and run Python scripts

---

## Installation & Setup

### Quick Start (5 minutes)

Follow these step-by-step instructions to get Trust Bench running on your system.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/mwill20/Trust-Bench-SecureEval-Ops.git
cd Trust-Bench-SecureEval-Ops
```

**Expected output:** Repository cloned successfully, directory contains `Project2v2/` folder.

#### Step 2: Create a Virtual Environment (Recommended)

This isolates Trust Bench's dependencies from your system Python.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Expected output:** Your terminal prompt should now show `(.venv)` prefix.

#### Step 3: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install core dependencies
pip install -r Project2v2/requirements-phase1.txt

# Optional: Install advanced features (evaluation metrics, static analysis)
pip install -r Project2v2/requirements-optional.txt
```

**Expected output:**
- Core install: ~50-100 packages installed (LangGraph, Flask, Pydantic, etc.)
- Optional install: Additional packages for enhanced analysis capabilities

**Verification:**
```bash
python -c "import langgraph, flask, pydantic; print('Dependencies OK')"
```

Should print: `Dependencies OK`

#### Step 4: Configure Environment Variables (Optional)

Copy the example environment file and add your API keys:

**Windows:**
```powershell
copy Project2v2\.env.example Project2v2\.env
```

**Linux / macOS:**
```bash
cp Project2v2/.env.example Project2v2/.env
```

Edit `Project2v2/.env` with your preferred text editor:

```bash
# Minimum configuration for chat features
OPENAI_API_KEY=sk-your-actual-key-here
LLM_PROVIDER=openai
ENABLE_SECURITY_FILTERS=true
```

> **Important**: If you skip this step, the core analysis features still work! API keys are **only required for the interactive chat interface**.

#### Step 5: Verify Installation

Run a quick self-test:

```bash
cd Project2v2
python main.py --repo ../Project2v2 --output test_output
```

**Expected output:**
```
=== Multi-Agent Evaluation Complete ===
Repository: /path/to/Trust-Bench-SecureEval-Ops/Project2v2
Overall Score: 32/100
Grade: needs_attention
System Latency: 0.08 seconds
Faithfulness: 0.62
Refusal Accuracy: 1.0
Per-Agent Timings:
  - SecurityAgent: 0.07 seconds
  - QualityAgent: 0.003 seconds
  - DocumentationAgent: 0.002 seconds
Report (JSON): test_output/report.json
Report (Markdown): test_output/report.md
```

✅ **You're ready to go!** See [Running the System](#running-the-system) below for usage options.

### Troubleshooting Installation

**Issue: `python: command not found` or `python3: command not found`**
- **Solution**: Install Python 3.10+ from [python.org](https://www.python.org/downloads/) or your package manager
- Verify: `python --version` or `python3 --version`

**Issue: `pip install` fails with permission errors**
- **Solution**: Ensure you've activated the virtual environment (Step 2)
- Or use: `pip install --user -r requirements-phase1.txt`

**Issue: `ModuleNotFoundError` after installation**
- **Solution**: Ensure you're in the activated virtual environment
- Reinstall dependencies: `pip install --force-reinstall -r Project2v2/requirements-phase1.txt`

**Issue: Windows "execution policy" blocks scripts**
- **Solution**: Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Environment Variables Reference

These variables can be set in `Project2v2/.env` or as system environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No* | None | OpenAI API key for chat features |
| `GROQ_API_KEY` | No* | None | Alternative: Groq API key |
| `GEMINI_API_KEY` | No* | None | Alternative: Google Gemini API key |
| `LLM_PROVIDER` | No | `openai` | Which LLM to use: `openai`, `groq`, or `gemini` |
| `ENABLE_SECURITY_FILTERS` | No | `true` | Enable input validation and prompt sanitization |
| `TB_MAX_FILES` | No | `2000` | Maximum files to scan per repository |
| `TB_MAX_FILE_SIZE_MB` | No | `2` | Skip files larger than this (MB) |
| `TB_CLONE_TIMEOUT` | No | `120` | Repository clone timeout (seconds) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

\* At least one LLM provider key is required for chat features; core analysis works without any keys.

---

## Running the System

### Web Interface (recommended)

```powershell
cd Project2v2
python web_interface.py
# browse to http://localhost:5001
```

The web interface now features **intelligent agent routing** that automatically directs your questions to the most appropriate specialist agent. Ask security questions, request code quality improvements, or seek documentation help - the system will route to the right expert and provide contextual responses with visual agent indicators.

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

## Interactive Web Application

Trust Bench SecureEval + Ops features a production-grade **Flask web application** that provides an intuitive interface for repository security auditing and AI-powered analysis consultation.

### Framework & Architecture

**Technology Stack:**
- **Backend**: Flask 3.0+ (Python web framework)
- **Frontend**: Custom HTML5, CSS3, JavaScript (ES6+)
- **Agent Orchestration**: LangGraph for multi-agent workflows
- **Real-time Updates**: AJAX for asynchronous status polling
- **Security**: Pydantic input validation, CSRF protection, API key sanitization

### User Interface Layout

#### Left Sidebar (Control Panel)

The sidebar contains all user inputs and configuration options:

1. **How to Use Section**
   - Quick summary of the evaluation process
   - Links to documentation and help resources

2. **Repository Input**
   - GitHub URL input field with validation
   - Example: `https://github.com/owner/repository`
   - Supports public repositories (private repos require authentication)

3. **LLM Provider Selection** (Optional)
   - Dropdown menu: OpenAI, Groq, or Gemini
   - API key input with masked display (not stored or logged)
   - "Test Connection" button for immediate validation
   - Privacy notice: Keys are session-only, never persisted

4. **Evaluation Metrics Panel**
   - **Interactive sliders** for custom agent weighting:
     - 🛡️ Security Agent (vulnerability scanning)
     - 🏗️ Quality Agent (code structure & testing)
     - 📚 Documentation Agent (README & guides)
   - **Preset buttons** for quick configuration:
     - Security Focus (50% security, 25% quality, 25% docs)
     - Quality Focus (25% security, 50% quality, 25% docs)
     - Documentation Focus (25% security, 25% quality, 50% docs)
     - Balanced (equal weights)
   - **Live score preview** showing weighted vs. equal scoring

#### Main Panel (Orchestration View)

The main panel displays real-time analysis progress and results:

1. **Progress Workflow Visualization**
   - **Step 1: Input** - Repository URL validated
   - **Step 2: Orchestrator** - Manager node coordinates agents
   - **Step 3: Agent Tiles** (expandable):
     - **Security Agent** 🛡️ - Scanning for secrets & vulnerabilities
     - **Quality Agent** 🏗️ - Analyzing code & test coverage
     - **Documentation Agent** 📚 - Reviewing docs & READMEs
   - **Step 4: Results** - Scores compiled, report generated
   - **Color-coded states**:
     - Gray: Idle/waiting
     - Blue: Active/running
     - Green: Completed successfully
     - Red: Error state

2. **Agent Detail Expandos**
   - Each agent tile has a "Show details" button
   - Reveals capabilities, collaboration context, and real-time status
   - Example: Security Agent shows number of findings, risk level

3. **Phase 3: Consensus Journey Visualization**
   - **Progress timeline** with negotiation round markers
   - **Agent mood indicators**:
     - 🟢 Green: Agreement
     - 🟡 Yellow: Negotiating
     - �red Red: Conflict
   - **Live negotiation highlights**: Speech bubbles showing agent conversations
   - **Conflict resolution panels**: Before/after comparison of disagreements

4. **Results Section**
   - **Overall Score**: Numeric score (0-100) with grade (excellent/good/fair/needs_attention)
   - **Per-dimension breakdown**:
     - Security score with confidence meter
     - Quality score with confidence meter
     - Documentation score with confidence meter
   - **Confidence visualization**: Color-coded progress bars
     - High (≥80%): Green
     - Medium (60-79%): Yellow
     - Low (<60%): Red
   - **Download options**:
     - Individual JSON/Markdown reports
     - Complete analysis bundle (ZIP with chat transcripts)
   - **Export/Import chat**: Save conversation history for later review

5. **Agent Chat Interface** (when LLM key provided)
   - **Chat history** with message threading
   - **Agent-specific responses** with avatars:
     - 🛡️ Security Agent (red accent)
     - 🏗️ Quality Agent (blue accent)
     - 📚 Documentation Agent (green accent)
     - 🎯 Orchestrator (purple accent)
   - **Routing transparency**: Each response shows why that agent was selected
   - **Confidence badges**: Visual indicator of agent certainty
   - **Context awareness**: Agents reference latest report data

### UX Design Considerations

#### 1. **Visibility of System Status**
- Real-time progress indicators prevent "black box" feeling
- Color-coded states (idle/running/completed) provide at-a-glance status
- Agent tiles update dynamically as orchestrator dispatches tasks

#### 2. **Progressive Disclosure**
- Complex details hidden by default (expandable tiles)
- High-level summary visible without scrolling
- Advanced features (custom weights, chat) optional but accessible

#### 3. **Safety & Privacy**
- **API key handling**: Keys accepted through UI, used in-memory only
- **Never logged**: Security filters redact sensitive data from logs
- **Session-only storage**: Keys cleared when browser closes
- **Privacy notice**: Explicit user communication about data handling

#### 4. **Error Recovery**
- Graceful degradation: Core features work without API keys
- Inline error messages with actionable solutions
- Timeout handling: Long-running tasks show progress, can be cancelled

#### 5. **Accessibility**
- Semantic HTML with ARIA labels
- Keyboard navigation support
- High-contrast color schemes for readability
- Responsive design (works on tablets and desktops)

#### 6. **Performance Optimization**
- Lazy loading of agent details (only when expanded)
- Debounced API calls prevent server overload
- Cached report data reduces redundant analysis

### Interactive Features Showcase

**Try these workflows:**

1. **Quick Audit**: Enter a GitHub URL, click "Analyze Repository", watch agents collaborate
2. **Custom Weighting**: Adjust sliders to emphasize security, see score preview update in real-time
3. **Agent Consultation**: After analysis, ask "What are the top security risks?" - Security Agent responds with context
4. **Consensus Exploration**: Expand orchestration timeline to see how agents negotiated conflicting findings
5. **Export & Share**: Download complete bundle, share with team, import conversation on another machine

---

## Evaluation Metrics Instrumentation

Every run records deterministic metrics alongside agent results:

- **System latency** - overall wall-clock time plus per-agent/per-tool timings (`metrics.system_latency_seconds`, `metrics.per_agent_latency`)
- **Faithfulness** - heuristic alignment of summaries with tool evidence (`metrics.faithfulness`)
- **Refusal accuracy** - simulated unsafe prompt harness (returns 1.0 while LLM calls are disabled) (`metrics.refusal_accuracy`)

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

- `report.json` - timestamp, repo path, composite summary, per-agent results, metrics, full conversation log  
- `report.md` - human-readable summary with agent cards, instrumentation metrics, conversation log  
- Optional timestamped archives (`github_analysis_*`) when launched through the web interface

---

## Deployment

Trust Bench SecureEval + Ops supports multiple deployment scenarios, from local development to production cloud environments.

### Deployment Mode 1: Local Development (Recommended for First Use)

This is the default setup described in [Installation & Setup](#installation--setup).

**Use when:**
- Exploring the tool on your laptop
- Development and testing
- Quick ad-hoc repository audits

**Start the web interface:**
```bash
cd Project2v2
python web_interface.py
```

**Access:** http://localhost:5001

### Deployment Mode 2: Docker Container (Production-Ready)

**Quick start with Docker Compose:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Trust-Bench-SecureEval-Ops.git
cd Trust-Bench-SecureEval-Ops

# 2. Create .env file with your API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Start the container
docker-compose up -d

# 4. Access the web interface
# Open http://localhost:5001 in your browser

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

**Manual Docker build and run:**

```bash
# Build the image
docker build -t trustbench:latest .

# Run with environment variables
docker run -d \
  --name trustbench \
  -p 5001:5001 \
  -e OPENAI_API_KEY=sk-your-key-here \
  -e ENABLE_SECURITY_FILTERS=true \
  -e TB_RUN_MODE=strict \
  -v trustbench-data:/data \
  -v trustbench-logs:/logs \
  trustbench:latest

# View logs
docker logs -f trustbench

# Stop and remove
docker stop trustbench
docker rm trustbench
```

**Docker features:**
- **Multi-stage build**: Smaller final image (~300 MB vs ~1 GB)
- **Non-root user**: Runs as `trustbench` user (UID 1000) for security
- **Health checks**: Automatic restart on failures
- **Persistent storage**: Volumes for analysis results and logs
- **Resource limits**: Configurable CPU/memory constraints
- **Read-only filesystem**: Enhanced security with tmpfs for temp files

**Environment variables** (see `.env.example` for full list):
```bash
# Required: At least one API key
OPENAI_API_KEY=sk-...
# or GROQ_API_KEY=gsk-...
# or GEMINI_API_KEY=...

# Optional: Configuration overrides
LLM_PROVIDER=openai
TB_MAX_FILES=2000
TB_MAX_FILE_SIZE_MB=2
AGENT_TIMEOUT_SECONDS=120
LOG_LEVEL=INFO
```

**Volumes explained:**
- `/data`: Persistent storage for analysis results and reports
- `/logs`: Application logs (if file logging enabled)

**Production deployment with Docker:**
```bash
# Use docker-compose for persistent setup
docker-compose up -d

# Update to latest version
git pull
docker-compose build
docker-compose up -d

# View resource usage
docker stats trustbench-secureeval-ops
```

### Deployment Mode 3: Server / Cloud Deployment

For long-running or team deployments, run Trust Bench on a dedicated server or cloud VM.

#### Prerequisites

- VM with Python 3.10+ (Ubuntu 22.04 LTS, Amazon Linux 2023, etc.)
- 2-4 vCPU, 8 GB RAM recommended
- Inbound port 5001 open (or your chosen port)

#### Option A: Systemd Service (Linux)

Create `/etc/systemd/system/trust-bench.service`:

```ini
[Unit]
Description=Trust Bench SecureEval + Ops Web Interface
After=network.target

[Service]
Type=simple
User=trustbench
WorkingDirectory=/opt/trust-bench/Project2v2
Environment="PATH=/opt/trust-bench/.venv/bin"
Environment="OPENAI_API_KEY=sk-your-key-here"
Environment="ENABLE_SECURITY_FILTERS=true"
ExecStart=/opt/trust-bench/.venv/bin/python web_interface.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable trust-bench
sudo systemctl start trust-bench
sudo systemctl status trust-bench
```

#### Option B: Supervisor (Cross-Platform)

Install supervisor: `pip install supervisor`

Add to `supervisord.conf`:

```ini
[program:trust-bench]
command=/opt/trust-bench/.venv/bin/python web_interface.py
directory=/opt/trust-bench/Project2v2
user=trustbench
autostart=true
autorestart=true
environment=OPENAI_API_KEY="sk-your-key",ENABLE_SECURITY_FILTERS="true"
stdout_logfile=/var/log/trust-bench/stdout.log
stderr_logfile=/var/log/trust-bench/stderr.log
```

**Start:**
```bash
supervisorctl reread
supervisorctl update
supervisorctl start trust-bench
```

#### Option C: Reverse Proxy (nginx)

For HTTPS and domain mapping, place nginx in front of Trust Bench:

```nginx
server {
    listen 443 ssl http2;
    server_name trustbench.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (for future real-time features)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Cloud Platform Examples

**AWS EC2:**
1. Launch t3.medium instance (Ubuntu 22.04)
2. Configure security group: Allow inbound TCP 5001 (or 443 if using nginx)
3. Follow systemd service setup above
4. Optional: Use Elastic IP for consistent access

**Azure VM:**
1. Create B2s VM (Ubuntu 22.04)
2. Open NSG port 5001 or 443
3. Follow systemd service setup above

**Google Cloud:**
1. Create e2-medium instance (Ubuntu 22.04)
2. Configure firewall rule for port 5001/443
3. Follow systemd service setup above

**DigitalOcean Droplet:**
1. Basic Droplet ($12/month, 2 GB RAM)
2. Follow systemd service setup above
3. Optional: Enable DigitalOcean firewall

### Security Considerations for Production

- **Use HTTPS**: Always deploy behind a reverse proxy with TLS certificates
- **Firewall**: Restrict access to trusted IP ranges if possible
- **API Keys**: Use environment variables, never commit to git
- **Rate Limiting**: Consider adding nginx rate limiting for public deployments
- **Monitoring**: Set up log aggregation (see [OPERATIONS.md](Project2v2/OPERATIONS.md))
- **Updates**: Regularly `git pull` and restart the service for security patches

### Scaling Considerations

**Current architecture supports:**
- 5-10 concurrent users (single Flask worker)
- 10-20 repository analyses per hour
- Single-server deployment

**For higher loads, consider:**
- Deploy behind Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5001 web_interface:app`
- Use Redis for session management
- Add load balancer for multiple instances
- See [OPERATIONS.md](Project2v2/OPERATIONS.md) for production hardening guidance

---

## Troubleshooting

Common issues and their solutions:

### Installation Issues

#### Error: `python: command not found`

**Symptoms:** Terminal cannot find `python` or `python3` command

**Solutions:**
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. On Linux: `sudo apt install python3.10 python3.10-venv` (Ubuntu/Debian)
3. On macOS: `brew install python@3.10`
4. Verify: `python --version` or `python3 --version` should show 3.10 or higher

#### Error: `pip install` fails with permission errors

**Symptoms:** 
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**
1. Activate virtual environment first: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/macOS)
2. Or use user install: `pip install --user -r requirements-phase1.txt`
3. Never use `sudo pip` (breaks system Python)

#### Error: `ModuleNotFoundError` after successful install

**Symptoms:** 
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solutions:**
1. Ensure virtual environment is activated (check for `(.venv)` prefix in terminal)
2. Reinstall in correct environment:
   ```bash
   pip install --force-reinstall -r Project2v2/requirements-phase1.txt
   ```
3. Verify environment: `which python` (Linux/macOS) or `where python` (Windows) should point to `.venv`

### Runtime Issues

#### App doesn't start: `Address already in use`

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
1. Another process is using port 5001
2. Find and kill it:
   - Linux/macOS: `lsof -ti:5001 | xargs kill -9`
   - Windows: `netstat -ano | findstr :5001`, then `taskkill /PID <PID> /F`
3. Or change port: Set `WEB_PORT=5002` in `.env`

#### LLM Chat Not Working: `Invalid API key`

**Symptoms:** Chat returns "Sorry, I'm having trouble accessing the AI service"

**Solutions:**
1. Verify API key is set: `echo $OPENAI_API_KEY` (Linux/macOS) or `echo %OPENAI_API_KEY%` (Windows)
2. Check key has active billing/credits at [OpenAI Platform](https://platform.openai.com/account/billing)
3. Try alternative provider: Set `LLM_PROVIDER=groq` and `GROQ_API_KEY=...` in `.env`
4. **Workaround**: Core analysis features work without API keys (only chat is affected)

#### Agent Tiles Stay "Running" Indefinitely

**Symptoms:** Progress bars stuck, no error message

**Solutions:**
1. Check timeout settings in `.env`: `AGENT_TIMEOUT_SECONDS=120` (increase if analyzing large repos)
2. View detailed logs: `tail -f Project2v2/logs/app.log` (if logging configured)
3. For large repos, increase limits:
   ```bash
   TB_MAX_FILES=5000
   TB_MAX_FILE_SIZE_MB=5
   TB_CLONE_TIMEOUT=300
   ```
4. Check network connectivity to GitHub (required for repository cloning)

#### Repository Analysis Fails Immediately

**Symptoms:** "Repository not found" or "Cloning failed" error

**Solutions:**
1. **Verify URL format**: Must be `https://github.com/owner/repo` (no trailing slash)
2. **Public repositories only**: Private repos require authentication (not yet supported in UI)
3. **Large repositories**: Repos >1 GB may timeout; increase `TB_CLONE_TIMEOUT=300`
4. **Network issues**: Check firewall/proxy settings allow access to github.com

### Web Interface Issues

#### Blank page or "Cannot GET /"

**Symptoms:** Browser shows empty page or 404 error

**Solutions:**
1. Verify app is running: Check terminal for "Running on http://127.0.0.1:5001"
2. Use correct URL: `http://localhost:5001` (not `127.0.0.1:5001` on some systems)
3. Clear browser cache: Ctrl+F5 (Windows) or Cmd+Shift+R (macOS)
4. Check browser console for JavaScript errors (F12 Developer Tools)

#### Windows: "execution policy" blocks scripts

**Symptoms:**
```
.venv\Scripts\activate : File cannot be loaded because running scripts is disabled on this system.
```

**Solutions:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
.\.venv\Scripts\activate
```

### Performance Issues

#### Analysis is very slow (>5 minutes)

**Causes & Solutions:**
1. **Large repository**: Normal for repos with 10,000+ files
   - Solution: Increase timeouts or analyze smaller repos first
2. **Slow internet**: Clone operation is network-bound
   - Solution: Pre-clone repo locally, use CLI: `python main.py --repo /path/to/local/repo`
3. **Low RAM**: System swapping to disk
   - Solution: Close other applications, add swap space, or upgrade RAM

#### Out of memory errors

**Symptoms:** 
```
MemoryError or killed by OS
```

**Solutions:**
1. Reduce file scan limits:
   ```bash
   TB_MAX_FILES=1000
   TB_MAX_FILE_SIZE_MB=1
   ```
2. Analyze smaller repositories first
3. Increase system RAM or swap space
4. Use CLI for more efficient processing: `python main.py --repo <path>`

### Getting Help

If you've tried the above solutions and still have issues:

1. **Check logs**: `Project2v2/logs/app.log` (if logging is configured)
2. **GitHub Issues**: [Open an issue](https://github.com/mwill20/Trust-Bench-SecureEval-Ops/issues) with:
   - Python version: `python --version`
   - OS details: `uname -a` (Linux/macOS) or `systeminfo` (Windows)
   - Error message (full traceback)
   - Steps to reproduce
3. **Documentation**: See [OPERATIONS.md](Project2v2/OPERATIONS.md) and [SECURITY.md](Project2v2/SECURITY.md)
4. **Community**: Check existing issues for similar problems

---

## Demo Video

<div align="center">
  <video controls width="640" poster="Project2v2/assets/images/TrustBench.png">
    <source src="https://1drv.ms/v/c/2c8c41c39e8a63cb/EQil7I1iewdEuzPdQGBqVOYBHaRg9tBcyogZvmKUXKFLyw?e=8Dl8P5" type="video/mp4" />
    Your browser does not support the video tag. You can download the walkthrough
    <a href="https://1drv.ms/v/c/2c8c41c39e8a63cb/EQil7I1iewdEuzPdQGBqVOYBHaRg9tBcyogZvmKUXKFLyw?e=8Dl8P5">here</a>.
  </video>
</div>

_If playback doesn't work on GitHub, download the file locally from the same link above._

> The full-resolution video is hosted via OneDrive to keep the repository history lean. If you want an offline copy, download it from the link above and place it under `Project2v2/assets/images/`.

---

## Example Results (Project2v2 self-audit)

- Overall Score: ~32/100 (`needs_attention`)  
- Security: seeded secrets detected (score 0) drive collaboration penalties  
- Quality: medium score, automatically penalized by SecurityAgent findings  
- Documentation: strong base score but reduced for missing security/testing guidance  
- Collaboration: more than five cross-agent messages; Manager summarizes adjustments in the final log

---

## MCP Server (Scope Decision)

Project2v2 prioritizes deterministic, offline-capable tooling. To keep grading reproducible and avoid external runtime dependencies, the earlier MCP server has been **intentionally deprecated** for this version. Required tool integrations (three or more) are provided as direct Python callables. MCP can be revisited later if cross-client interoperability (Claude Desktop, Cursor, etc.) becomes necessary, but it is **not required** for Module 2 compliance.

---

## File Structure (trimmed)

```
Trust_Bench/
|-- Project2v2/
|   |-- main.py
|   |-- web_interface.py
|   |-- multi_agent_system/
|   |   |-- agents.py
|   |   |-- orchestrator.py
|   |   |-- tools.py
|   |   `-- reporting.py
|   |-- requirements-phase1.txt
|   |-- requirements-optional.txt
|   |-- run_audit.(bat|ps1)
|   |-- launch.bat
|   `-- output/
|-- trustbench_core/      (legacy CLI wrapper forwarding to Project2v2/main.py)
`-- Project2v2/checklist.yaml (optional-features register)
```

---

## Security & Hardening Notes

- All detected secrets are synthetic and included solely for demonstration purposes. No real credentials are exposed.
- `security_utils.py` and the web UI sanitize repository URLs, prompts, and API keys.
- Optional extras (`ragas`, `semgrep`, `streamlit`) enable deeper analytics and dashboarding when desired.

---

## Future Work & Enhancements

The following features are planned for future releases:

### Future Considerations (Lower Priority)
- **Batch Analysis**: Automated analysis of multiple repositories simultaneously with queue management and comparative dashboards
  - *Note: This feature requires significant infrastructure (job queuing, background workers, database) and is planned for a later major release*

### Long-term Vision
- Additional specialized agents (Performance, Accessibility, Compliance)
- Integration with CI/CD pipelines
- Real-time repository monitoring
- Advanced analytics and trending

---

## Documentation Roadmap & Evidence

To satisfy Project 3 publication requirements, the repository ships with dedicated documentation artifacts. Keep these synchronized with feature development:

| Document | Purpose | Status / Next Action |
| --- | --- | --- |
| [`README.md`](README.md) | Executive summary, architecture overview, quickstart, CI/coverage references | ✅ Actively maintained |
| [`OPERATIONS.md`](Project2v2/OPERATIONS.md) | Operational excellence rubric (start/stop/health, logging, resilience, monitoring) | 📝 Skeleton ready – fill details as services evolve |
| [`SECURITY.md`](Project2v2/SECURITY.md) | Security & safety rubric (input validation, guardrails, sandbox, SOC 2-lite map) | 📝 Skeleton ready – update per guardrail implementation |
| [`USER_GUIDE.md`](Project2v2/USER_GUIDE.md) | End-user walkthrough + context | ✅ Append “Production Enhancements” notes when Phase 0 work lands |
| `docs/evidence/` (optional) | Test/coverage screenshots, CI logs for publication attachments | 🔄 Create as artifacts are generated |

**Working agreement:**  
- Phase 0 (“Parity Lock-In”) adds test coverage notes under README → Testing & CI Summary, and populates the open TODOs in `OPERATIONS.md` / `SECURITY.md`.  
- Each subsequent phase should update the relevant section(s) before closing the task to avoid drift.

---

## Production Enhancements (Module 3)

Phase 3 and 4 harden the system for publication while preserving identical UX:

- CI gate (`python-ci` workflow) runs tests, coverage, security audit, and rubric validator on every PR.
- Structured JSON logs, health probes, and resilience settings documented in [OPERATIONS.md](Project2v2/OPERATIONS.md).
- Security controls (input validation, sandbox, redaction, SOC 2-lite mapping) captured in [SECURITY.md](Project2v2/SECURITY.md).
- Evidence bundle placeholders live under [Project2v2/docs/evidence/](Project2v2/docs/evidence/) for publishing artifacts (CI proof, screenshots, coverage report).

---

## License & Support

### License

Trust Bench SecureEval + Ops is released under the **MIT License**.

**What this means for you:**
- ✅ **Commercial use**: Use in commercial products and services
- ✅ **Modification**: Fork, modify, and adapt the code
- ✅ **Distribution**: Share modified or unmodified versions
- ✅ **Private use**: Use privately without publishing your changes
- ⚠️ **Liability**: No warranty provided; use at your own risk

**Full license text:** See [LICENSE](LICENSE) in the repository root.

**Attribution:** When using Trust Bench in publications or products, please include:
```
Trust Bench SecureEval + Ops by Michael Williams
https://github.com/mwill20/Trust-Bench-SecureEval-Ops
Licensed under MIT
```

### Support Channels

**Bug Reports & Feature Requests:**
- **GitHub Issues**: [Open an issue](https://github.com/mwill20/Trust-Bench-SecureEval-Ops/issues)
- **Labels**:
  - `bug`: Something isn't working correctly
  - `enhancement`: New feature or improvement request
  - `documentation`: Documentation improvements
  - `question`: General questions about usage

**Security Concerns:**
- **Private reporting**: For security vulnerabilities, please open a private security advisory
- **Contact**: See [SECURITY.md](Project2v2/SECURITY.md) for responsible disclosure process
- **Do NOT** open public issues for security vulnerabilities

**Community & Discussion:**
- **GitHub Discussions**: Q&A, ideas, and general discussion
- **Pull Requests**: Contributions welcome! See [Contributing](#contributing) below

### Contributing

We welcome contributions to Trust Bench SecureEval + Ops!

**How to contribute:**

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**:
   - Follow existing code style (PEP 8 for Python)
   - Add tests for new features
   - Update documentation as needed
4. **Run tests**: `pytest Project2v2/tests/`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request** with a clear description of changes

**Contribution guidelines:**
- All PRs must pass CI checks (tests, coverage, linting)
- Maintain or improve test coverage (currently 79%)
- Update `CHANGELOG.md` with notable changes
- Follow the existing code structure and patterns

**Development setup:**
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Trust-Bench-SecureEval-Ops.git
cd Trust-Bench-SecureEval-Ops

# Create development environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install development dependencies
pip install -r Project2v2/requirements-phase1.txt
pip install -r Project2v2/requirements-optional.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest Project2v2/tests/ -v

# Format code
black Project2v2/

# Lint
flake8 Project2v2/
```

### Maintenance Status

🟢 **Actively Maintained** (as of November 2025)

This project is part of an ongoing AI security engineering learning track. We aim to:
- Address critical bugs within 48 hours
- Respond to issues and PRs within 1 week
- Keep dependencies current (quarterly security updates)
- Add new features based on community feedback

**Roadmap**: See [Future Work & Enhancements](#future-work--enhancements) above for planned features.

### Contact Information

**Maintainer**: Michael Williams ([@mwill20](https://github.com/mwill20))

**Email**: For security issues only (see SECURITY.md)

**Preferred contact**: GitHub Issues for all non-security topics

---

## Credits & References

- Ready Tensor AI Agent Course - Module 2 (Multi-Agent Evaluation)  
- LangGraph, CrewAI, AutoGen (collaboration inspiration)  
- Semgrep, OpenAI/Groq/Gemini APIs (referenced integrations)  
- Project2v2 implementation by @mwill20 and collaborators

_Version Project2v2 - October 2025 - Refactored for offline deterministic evaluation._
