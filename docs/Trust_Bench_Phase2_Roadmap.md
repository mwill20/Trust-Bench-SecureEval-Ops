# 🧩 Trust_Bench Phase 2 Roadmap — “Studio & UI Layer”

**Version:** Draft 1.0  
**Tag dependency:** v0.2-phase1-stable  
**Date:** 2025‑10‑08

---

## 🎯 Objective
Phase 2 focuses on transforming Trust_Bench from a verified evaluation engine into an *interactive studio*.  
The goal: create a user‑friendly interface that visualizes evaluations, runs tests, and interacts with MCP tools seamlessly.

This phase bridges backend and user experience — turning Trust_Bench into a usable, demo‑ready system.

---

## 🧱 Core Goals

### 1. **Trust_Bench Studio UI**
- Build a lightweight, modular interface (Streamlit or FastAPI + React) to:
  - Browse evaluation results (`eval/runs/latest` and past runs)
  - Trigger evaluations (fake/live provider modes)
  - Display MCP tool outputs (secret scans, environment reports)
- Implement tabs or panels for:
  - **Evaluation Dashboard** (metrics, charts, thresholds)
  - **Workspace Tools** (MCP tool execution and results)
  - **Profile Configurator** (switch profiles: default, highstakes)
  - **Logs & Reports** (view artifacts, download markdown/PDF)

### 2. **Run Management & Visualization**
- Store and compare runs in a local JSONL or SQLite DB.
- Visualize with charts (e.g., RAGAS, precision, latency).
- Implement “diff view” between runs to track model or config drift.

### 3. **MCP Client Integration**
- Create simple client connector for Trust_Bench MCP server:
  - `scan_repo_for_secrets`, `env_content`, `cleanup_workspace`
  - Display structured results in the UI (e.g., collapsible panels)
- Allow optional Docker connection (e.g., via `localhost:8000`)

### 4. **Security & Validation Layer**
- Add token‑auth for MCP connections.
- Apply redaction filters on any secret/path outputs.
- Validate evaluation configs before running (JSON schema or pydantic).

### 5. **CI & Packaging**
- Extend CI to include `trust_bench_studio/` build and lint steps.
- Package as optional extra (`pip install trust-bench[studio]`).
- Add screenshots and run instructions to README.

---

## 🗂️ Directory Structure Proposal

```
trust_bench_studio/
  ├── app.py                # Streamlit/FastAPI entry point
  ├── components/           # UI elements (charts, tables, panels)
  ├── data/                 # Cached runs and MCP responses
  ├── api/                  # Optional REST layer for evaluation trigger
  ├── utils/                # UI + API shared helpers
  ├── requirements.txt
  └── README.md
```

---

## 🧭 Milestones & Deliverables

| Phase 2 Milestone | Description | Deliverable |
|-------------------|-------------|--------------|
| **2.1 UI Scaffold** | Create base UI skeleton (layout, tabs) | `trust_bench_studio/app.py` |
| **2.2 MCP Client Bridge** | Add connectors to MCP server | `studio_mcp_client.py` |
| **2.3 Run Viewer & Diff Tool** | Implement run metrics visualization | Charts + table views |
| **2.4 Profile Configurator** | Toggle evaluation profiles via UI | Dropdown config editor |
| **2.5 CI & Release** | Add workflow, finalize docs | Tag `v0.3-studio-alpha` |

---

## 📘 Dependencies
- `trustbench_core >= 0.2-phase1-stable`
- `trust_bench_mcp >= 0.2`
- Streamlit 1.38 or FastAPI 0.110+
- Altair or Plotly for visualization
- Pydantic v2 for validation

---

## 🚀 Expected Outcome
By the end of Phase 2, Trust_Bench will provide:
- An interactive Studio for evaluating and comparing agent performance.
- Integrated security tools accessible via MCP.
- A demo‑ready interface for presentations, publications, and Ready Tensor certification.

---

**Next Tag:** `v0.3-studio-alpha`  
**Maintainer:** Michael Williams (mwill20)  
**Repository:** github.com/mwill20/Trust_Bench
