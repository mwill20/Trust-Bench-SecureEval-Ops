# TrustBench (Groq-first Starter)

Minimal, runnable scaffold for agent evaluation with **Groq**. 
It gives you: a CLI orchestrator, four skill-based pillar agents, profiles, artifacts, a Streamlit Studio, and CI wiring.

> Works without keys (simulated scores). If `GROQ_API_KEY` is set, Task/Ethics agents can use the real model.

## Quick Start
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
cp .env.example .env   # add GROQ_API_KEY if you have one

# Run a local eval
python -m trustbench_core.orchestrator --profile profiles/default.yaml

# Open the last HTML report
python -m trustbench_core.reports.writer --open-last

# Studio (optional)
streamlit run studio_app/app.py
```

## CI (GitHub)
Add `.github/workflows/eval.yml` and a repository secret `GROQ_API_KEY` (optional).

## Layout
```
trustbench_core/         # library + CLI
  orchestrator.py
  agents/ (task_fidelity, security_eval, system_perf, ethics_refusal)
  providers/groq_provider.py
  tools/mcp_client.py
  reports/writer.py
profiles/
datasets/golden/
studio_app/app.py
```

## Notes
- Artifacts land in `runs/<timestamp>/` (metrics.json, failures.csv, report.html).
- Gate passes when all metrics meet thresholds in the profile YAML.
