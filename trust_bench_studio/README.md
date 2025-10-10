# Trust_Bench Studio

Trust_Bench Studio provides a Streamlit front end for exploring evaluation runs, visualizing agent orchestration, and reviewing MCP reports.

## Getting Started

```bash
pip install -r requirements.txt  # ensure Streamlit and project deps are available
streamlit run trust_bench_studio/app.py
```

The scaffold renders three primary areas:

- **Dashboard** – metrics diff view for evaluation runs.
- **Agents** – expandable cards with state, transcripts, and chat explainers.
- **Reports & MCP** – workspace tooling, logs, and cached MCP outputs.

## Agent Manifest

Agent metadata (names, roles, prompts, and image hooks) is defined in `trust_bench_studio/config/agents_manifest.yaml`. Load it in code with:

```python
from trust_bench_studio.utils import load_agents_manifest

for agent in load_agents_manifest():
    print(agent["name"], agent["role"])
```

Images referenced in the manifest should live under `trust_bench_studio/assets/agents/` (or update the `image` paths accordingly).

## Next Steps

1. Persist structured run summaries (metrics + agent traces) for richer dashboards.
2. Animate agent cards based on orchestrator events.
3. Surface MCP actions (scan, env audit, cleanup) with live feedback in the UI.
