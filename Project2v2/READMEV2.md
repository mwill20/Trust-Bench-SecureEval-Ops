
<p align="center">
  <img src="assests/images/TrustBench.png" alt="TrustBench Logo" width="200"/>
</p>

# Trust_Bench – Multi-Agent Security Evaluation Framework

## 1️⃣ Project Title & Overview

**Trust_Bench – Multi-Agent Security Evaluation Framework**

Trust_Bench is a collaborative, agentic AI system for automated security and quality evaluation of code repositories. It leverages multiple specialized agents, orchestrated via LangGraph, to scan, analyze, and report on repository security, code quality, and documentation health. The system is designed for AI security, evaluation, and coordination research, and features a modern web UI for interactive analysis and LLM-powered Q&A.

- **Frameworks:** LangGraph (orchestration), Flask (web UI), custom agent logic
- **Domain:** AI security, multi-agent evaluation, automated code review

---

## 2️⃣ System Architecture

Trust_Bench uses a modular, message-passing architecture:

```
[Manager/Orchestrator]
   ↓
[SecurityAgent] → [QualityAgent] → [DocumentationAgent]
   ↘──────────────↗
```
- **Orchestration:** LangGraph graph (Python)
- **Communication:** Message passing, shared context, and direct agent-to-agent messaging
- **Flow:** The Orchestrator coordinates agent execution, collects findings, and manages cross-agent communication for collaborative scoring.

---

## 3️⃣ Agent Roles and Responsibilities

### 🛡️ SecurityAgent
- **Purpose:** Scans code for secrets, credentials, and vulnerabilities
- **Inputs:** Repository files
- **Outputs:** Security findings, alerts to other agents
- **Key Tools:** Secret scanner, credential pattern matcher

### 🔍 QualityAgent
- **Purpose:** Analyzes code structure, language, and test coverage
- **Inputs:** Repository files, security context
- **Outputs:** Quality metrics, test coverage, context for docs agent
- **Key Tools:** File counter, test coverage analyzer

### 📝 DocumentationAgent
- **Purpose:** Reviews documentation for completeness and security/test guidance
- **Inputs:** README and docs, quality/security context
- **Outputs:** Documentation score, improvement suggestions
- **Key Tools:** Markdown parser, section counter

### 🤖 Orchestrator (Manager)
- **Purpose:** Coordinates agent workflow, tracks collaboration, compiles final report
- **Inputs:** All agent outputs
- **Outputs:** Final scores, collaboration metrics, report

---

## 4️⃣ Tool Integrations

- **Secret Scanner:** Used by SecurityAgent to detect keys, tokens, and credentials
- **Structure Analyzer:** Used by QualityAgent to count files, detect languages, and measure test coverage
- **Documentation Reviewer:** Used by DocumentationAgent to parse and assess README structure and content

All tools extend LLM/agent capabilities by providing structured, actionable findings for collaborative evaluation.

---

## 5️⃣ Installation & Setup

```powershell
git clone https://github.com/mwill20/Trust_Bench.git
cd Trust_Bench/Project2v2
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-phase1.txt
pip install -r requirements-optional.txt  # optional extras
cp .env_example .env  # (if present)
# Fill in API keys as needed
```
- **Python version:** 3.10+
- **Dependencies:** Install `requirements-phase1.txt` for the core runtime and `requirements-optional.txt` for extras like RAG evaluation, static analysis, and dashboards.

---

## 6️⃣ Running the System

**Web UI (Recommended):**
```powershell
python web_interface.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

**Command Line:**
```powershell
python main.py --repo <path_to_repo> --output <output_dir>
```

**Batch Scripts:**
```powershell
run_audit.bat .
run_audit.bat ..
run_audit.bat "C:\path\to\repo"
```

**Expected Outputs:**
- `output/report.json` (detailed results)
- `output/report.md` (human-readable summary)

---

## 7️⃣ Evaluation Metrics / Pillars

- **Faithfulness:** Accuracy of agent findings
- **System Latency:** Time to complete analysis
- **Refusal Accuracy:** LLM/agent refusal to answer unsafe queries
- **Injection Block Rate:** Effectiveness of prompt injection sanitization
- **Security Scan Findings:** Number and severity of secrets/vulnerabilities found

**Sample Output:**
```json
{
  "summary": {
    "overall_score": 61,
    "grade": "fair",
    "collaboration_metrics": {
      "cross_agent_messages": 5,
      "security_impact": true
    }
  },
  "agents": {
    "SecurityAgent": {"score": 80, "summary": "No secrets found."},
    "QualityAgent": {"score": 60, "summary": "Good structure, no tests."},
    "DocumentationAgent": {"score": 45, "summary": "Docs lack security/test info."}
  }
}
```


---

## 8️⃣ File Structure

```
Project2v2/
├── main.py                # Orchestrator entry point
├── web_interface.py       # Flask web UI
├── multi_agent_system/    # Agents, orchestrator, tools
│   ├── agents.py
│   ├── orchestrator.py
│   ├── tools.py
│   └── types.py
├── security_utils.py      # Input validation, sanitization
├── llm_utils.py           # LLM provider abstraction
├── requirements.txt
├── launch.bat             # Interactive launcher
├── run_audit.bat / .ps1   # Batch/PowerShell scripts
├── output/                # Analysis results
├── tests/                 # Unit tests
├── README.md
├── USER_GUIDE.md
└── ...
```

Core dependency manifests:
- `requirements-phase1.txt` – minimal runtime stack (LangGraph, Flask, requests).
- `requirements-optional.txt` – optional extras for analytics and dashboards (`ragas`, `semgrep`, `streamlit`).
- `requirements.txt` – legacy shim that references the phase 1 list for compatibility.

---

## 9️⃣ MCP Server (If Applicable)

*This project does not expose a separate MCP server, but the architecture is compatible with MCP-style tool endpoints if extended.*

---


## 🔟 Results / Reports

- Example: `output/report.md`, `output/report.json`
- **Summary:**
  - Faithfulness: 0.8 (acceptable)
  - No critical security issues
  - Collaboration: 5 cross-agent messages

---

## 📹 Demo Video (Placeholder)

*A video demonstration of Trust_Bench will be added here. [Insert link or embedded video when available.]*

---

## 🖼️ Screenshots / Artifacts (Placeholder)

*Screenshots, sample reports, or other artifacts will be added here as required. [Insert images or files as needed.]*

---

## 11️⃣ Limitations & Next Steps

- Evaluation metrics are not yet weighted or customizable
- Only OpenAI, Groq, and Gemini providers tested
- No live RAG or retrieval-augmented generation
- UI could be extended for more visualization
- Future: add more agents, integrate RAGAS, support more LLM providers, expand MCP endpoints

---

## 12️⃣ Credits & References

- Ready Tensor AI Agent Course (Module 2)
- LangGraph, CrewAI, AutoGen, Semgrep, OpenAI
- Special thanks to the Ready Tensor team and instructors

---


