# A3 Evaluation Kit (drop-in for AegisEval)
Reference harness illustrating how we structure scenario-specific runners, datasets, and reports.
Use it as a design pattern when expanding TrustBench profiles or adding bespoke eval modules.
Files added:
- eval/a3_runner.py         : CLI runner that computes simulated RAGAS + jaccard + coherence metrics
- data/a3/sample.jsonl      : example dataset (1 row)
- tests/a3/test_a3_eval.py  : pytest that runs the runner (simulation mode)
- reports/                  : outputs (CSV + Markdown report) will be created here

Quick run (local):
  python -m venv .venv && source .venv/bin/activate
  pip install pytest pyyaml
  python eval/a3_runner.py --dataset data/a3/sample.jsonl --out reports/a3_report.md --csv reports/a3_scores.csv --simulate
  cat reports/a3_report.md
