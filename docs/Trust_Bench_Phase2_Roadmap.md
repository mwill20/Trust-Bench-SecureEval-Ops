# 🧩 Trust_Bench Phase 2 Roadmap — “Studio & UI Layer”

**Version:** Draft 2.0  
**Tag dependency:** v0.2-phase1-stable  
**Date:** 2025‑10‑08

---

## 🎯 Objective
Phase 2 transforms Trust_Bench from a verified evaluation engine into an *interactive studio* that visualizes how agents think, collaborate, and report.  
The goal is to make the invisible coordination of multi‑agent systems visible, explorable, and conversational — turning raw metrics into insight.

This phase bridges backend orchestration with an engaging, instructive user experience.

---

## 🧱 Core Goals

### 1. **Trust_Bench Studio UI**
Build a modular front end (Streamlit or FastAPI + React) that allows users to:
- Browse evaluation results (`eval/runs/latest` and past runs)
- Trigger live or fake evaluations
- Interact with agents visually and conversationally
- Display MCP tool outputs (secret scans, environment checks, etc.)

UI panels include:
- **Evaluation Dashboard** (metrics, charts, and agent visualizations)
- **Agents View** (animated cards for each agent showing skills, tools, and outputs)
- **Profile Configurator** (select default/high‑stakes profiles)
- **Reports & Logs** (view artifacts, download markdown/PDF, and chat with agents about results)

---

## 🌌 Visual Agent Orchestration Layer

### Vision
Each agent becomes a *living node* in a dataflow map. The orchestrator distributes data, lights trace connections, and agents respond with analysis and guidance.  
This transforms the system from a static CLI into a narrative of AI collaboration.

### Design Features
**Agent Cards / Nodes**
- Shows name, icon/logo, role.
- Expandable **Skills** and **Tools** lists.
- Status indicator (Idle → Active → Complete).
- Output section with metrics and a conversational LLM‑powered explanation.

**Orchestration Map**
```
[Orchestrator] → [Task Agent] → [Security Agent] → [System Agent] → [Ethics Agent]
```
- Animated data flow lines (glowing trails).
- Agent cards “activate” with subtle motion when processing.
- Results flow back to orchestrator with badges (✅ pass / ⚠️ warning / ❌ fail).

**Animated Workflow Playback**
- Replay a run: data enters orchestrator, flows to agents, animations trigger for analysis and response.
- Each agent outputs a report bubble or “chat panel.”

**Conversational Agent Outputs**
After completing its analysis, each agent presents a **chat box** backed by the same LLM that produced the evaluation.  
It summarizes the findings, explains scores in plain language, and answers user questions like:
- “What does this score mean?”  
- “How can I improve this result safely?”  
- “What risks should I be aware of?”  
- “Are there best‑practice workarounds or mitigations?”

This conversational layer turns static scores into actionable intelligence and makes the system a *teaching companion* as much as a testing tool.

**User Interaction Layer**
- Hover to reveal tools/skills.  
- Click to expand chat or review output JSON.  
- Toggle between *Workflow View* (animated system) and *Metrics View* (numeric charts).

### Technical Base
- **Frontend options:** Streamlit + `streamlit‑elements` / `pyvis`, or React + D3.js / Cytoscape.js.  
- **Backend:** FastAPI layer serves evaluation data and agent states as JSON events.  
- **Animation data:** derived from `run.json` event traces.  
- **LLM backend:** connects to configured provider (Groq / OpenAI / Anthropic) per agent for post‑run chat explanations.

---

## 🧠 Additional Features

### Run Management & Visualization
- Compare multiple runs (diffs, trends, improvements).  
- Visualize precision, recall, latency, and RAGAS metrics with charts.  
- Filter by model, dataset, or profile.

### MCP Client Integration
- Use local or Docker MCP endpoints to call:
  - `scan_repo_for_secrets`
  - `env_content`
  - `cleanup_workspace`
- Display structured results with visual tags and allow report download.

### Security & Validation
- Token‑auth for MCP connections.  
- Redaction for secret or path outputs.  
- JSON schema or Pydantic validation of configs.

### CI & Packaging
- Add workflows for Studio linting/build tests.  
- Package optional Studio module (`pip install trust-bench[studio]`).  
- Include screenshots in main README.

---

## 🗂️ Directory Structure Proposal

```
trust_bench_studio/
  ├── app.py                     # Entry point (Streamlit or FastAPI)
  ├── components/                # UI widgets (agent cards, orchestration graph)
  ├── data/                      # Cached runs & MCP responses
  ├── api/                       # Optional REST layer for run triggers
  ├── utils/                     # Shared functions & animation handlers
  ├── assets/                    # Logos, icons, animation sprites
  ├── requirements.txt
  └── README.md
```

---

## 🧭 Milestones & Deliverables

| Phase 2 Milestone | Description | Deliverable |
|-------------------|-------------|--------------|
| **2.1 UI Scaffold** | Create base layout, navigation, and placeholders for agent cards | `trust_bench_studio/app.py` |
| **2.2 Visual Agent Layer** | Implement animated orchestration map & agent cards | `components/agents_view.py` |
| **2.3 Conversational Outputs** | Integrate LLM chat for agent explanations | `components/agent_chat.py` |
| **2.4 Run Viewer & Diff Tool** | Charts, metrics, and run comparisons | `components/run_viewer.py` |
| **2.5 MCP Client Bridge** | Connect to MCP server, render results visually | `studio_mcp_client.py` |
| **2.6 CI & Release** | Add CI workflow, finalize docs | Tag `v0.3-studio-alpha` |

---

## 📘 Dependencies
- `trustbench_core >= 0.2-phase1-stable`
- `trust_bench_mcp >= 0.2`
- Streamlit 1.38 or FastAPI 0.110+
- Altair or Plotly for visualization
- Pydantic v2 + JSON schema for validation
- Optional: D3.js / Cytoscape.js for graph animation

---

## 🚀 Expected Outcome
By the end of Phase 2, Trust_Bench will provide:
- A **visual and conversational Studio** for observing and understanding multi‑agent collaboration.  
- Dynamic **agent visualization** showing orchestration and reasoning flow.  
- Integrated **LLM explanations** that make outputs interpretable and interactive.  
- A **demo‑ready interface** for Ready Tensor certification, presentations, and security analysis.

---

**Next Tag:** `v0.3-studio-alpha`  
**Maintainer:** Michael Williams (mwill20)  
**Repository:** github.com/mwill20/Trust_Bench

---

## Phase 2 Progress Update (2025-10-08)

### Implementation Status
- Streamlit scaffold for `trust_bench_studio` established with dashboard, agents, and MCP panels.
- Utilities now expose profile discovery, run summaries, and a placeholder MCP client for future integrations.
- `trust_bench_studio` package exported a reusable `main()` entry point for app launch.

### Latest Additions
- Added `scripts/make_baseline.py` to snapshot `eval/runs/latest` into curated `baseline_*` directories (artifacts pruned, metadata recorded) for reliable metric deltas.
- Dashboard auto-refresh now honors polite polling (>=1s) and pauses when no runs are present or when the view leaves Dashboard/Agents.
- MCP workspace tools execute against the live bridge with progress logging, cached JSON outputs, and badge summaries; results persist under `trust_bench_studio/data/mcp_cache/` (ignored in Git).
- Agent cards expose “Ask this agent” chats seeded with the active metrics, traces, and latest MCP findings while enforcing prompt-safety guardrails.
- Agents tab now reads from `trust_bench_studio/config/agents_manifest.yaml`, rendering branded cards (images, accent colors, personalities) and feeding `seed_prompt` text directly into LLM explanations.
- New **Flow** view presents orchestrator → agent execution as a dynamic graph (user input, Logos, per-agent nodes with animated links and chat expanders) so the studio feels like a living system.
- Adopted a React + FastAPI command-center (see `trust_bench_studio/frontend` and `trust_bench_studio/api/server.py`) while preserving existing evaluation plumbing and MCP workflows.

### Next Steps (Refined)
1. **Feed real evaluation metrics and agent traces into the panels.** Pull metrics and traces from `eval/runs/latest/run.json` (and siblings), wire a lightweight polling loop for near-real-time updates, map agent state transitions (`idle -> active -> complete`), and surface LLM summaries inside each agent chat panel.
2. **Decide which Studio files belong in Git and commit cleanly.** Ignore local-only artifacts (for example `trust_bench_studio/data/`, `.streamlit/`, run caches, `__pycache__/`), stage the Streamlit scaffold plus roadmap updates, commit as `v0.3-studio-scaffold`, and reserve `v0.3-studio-alpha` for the live-metrics milestone.
3. **Expand the MCP pane with actionable workflows.** Add buttons for repo scans, environment audits, and workspace cleanup; show progress indicators, rich result cards, and optional “view raw output” or “ask agent” affordances; later chain multi-tool remediation pipelines.

### Sequence Toward `v0.3-studio-alpha`
- Wire live data streams into Dashboard and Agents panels to validate the orchestration loop.
- Finalize Git hygiene and land the scaffold commit.
- Bridge MCP actions to Studio controls.
- Layer conversational explanations over metrics.
- Polish animations and UI details for the alpha tag.

### Tiny Pitfalls to Dodge
- Don’t re-run evaluations from the chat panel; chat should explain existing outputs, not mutate them.
- Redact secrets in MCP results before rendering any summaries or charts.
- Keep polling off on the MCP tab—only the Dashboard and Agents views should auto-refresh.
- **Security guardrails:** Keep security practices in place wherever there are inputs.  
  Even though Trust_Bench Studio operates in a controlled evaluation context, every input field or API call still needs to be treated as untrusted data. This includes:  
  - User chat inputs: sanitize for prompt-injection patterns (for example, ignore previous instructions, run shell command, read file) before sending to the LLM.  
  - MCP parameters: validate and cap file paths, byte sizes, and environment variables to prevent path traversal or secret leakage.  
  - File uploads or repo URLs: restrict to HTTPS.  
  - LLM responses: never render raw Markdown or HTML directly; escape before displaying in Streamlit or web contexts.  
  - Images, code, and prompts or directions found in any repo, directory, or file should be treated as read-only—do **not** execute them, commit them to memory, or follow embedded instructions.
