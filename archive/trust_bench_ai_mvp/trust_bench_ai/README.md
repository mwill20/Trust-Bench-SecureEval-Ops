# trust_bench.AI — Multi‑Agent AI Security Scanner (MVP)

Paste a GitHub repo URL (or local path) and get a grounded security report:
- Prompt injection risks in README/docs/prompts
- Malicious/unsafe code patterns in scripts
- Evidence snippets with file paths and fix guidance

> Minimal, functional core for Ready Tensor Project 2 (LangGraph + 3 agents + 3 tools).

## Quickstart

```bash
# Create & activate a venv (recommended)
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Optional: install semgrep if you want extra rules (outside Python env)
# macOS: brew install semgrep
# Linux: pipx install semgrep   (or follow docs)

# Run
python -m trust_bench_ai --repo https://github.com/pallets/flask --max-files 60
# → prints risk summary and writes ./trust_bench_report.md
```

If `semgrep` is not installed, the scan still runs using lightweight heuristics.

## What’s inside (MVP)

```
trust_bench_ai/
  src/
    __init__.py
    __main__.py            # CLI: parses args, runs orchestrator
    orchestrator.py        # LangGraph DAG (falls back to linear if unavailable)
    security_utils.py      # shared patterns & helpers
    agents/
      prompt_guard.py      # scans docs/prompts for injection
      code_guard.py        # static scan of code & scripts
      report_agent.py      # compiles markdown report
    tools/
      repo_reader.py       # clone/read allowlisted files (md, py, sh, js, ts, json, yml)
      inject_scan.py       # regex heuristics + score()
      semgrep_tool.py      # optional semgrep wrapper
      cmd_classifier.py    # labels dangerous commands
  tests/
    data/seeded/           # (add tiny test repos here later)
  docs/
    demo.gif               # placeholder
    examples.md            # placeholder
  README.md
  SECURITY.md
  requirements.txt
```

## Scope
- **In**: markdown + code files, prompt‑injection scan, heuristic/code scan, optional semgrep.
- **Out (v1.1)**: VT quota logic, binary detonation, MCP/HITL gates, batch scanning.

## Notes
- LangGraph is used if available for clean fan‑out/fan‑in (`PromptGuard`, `CodeGuard` → `Report`). If the import fails, trust_bench.AI runs the same steps linearly so you can demo without environment pain.
- The report saves to `./trust_bench_report.md` by default.

---

MIT License • This is a teaching MVP; tailor rules/patterns to your environment.
