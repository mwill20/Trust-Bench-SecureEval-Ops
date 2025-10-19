"""Entry point for the simplified Project 2 multi-agent system."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

from multi_agent_system import (
    build_orchestrator,
    build_report_payload,
    write_report_outputs,
)
from multi_agent_system.types import MultiAgentState


def _initial_state(repo_root: Path) -> MultiAgentState:
    return {
        "repo_root": repo_root,
        "shared_memory": {},
        "messages": [],
        "agent_results": {},
    }


def run_workflow(repo_root: Path) -> Dict[str, Any]:
    graph = build_orchestrator()
    state = _initial_state(repo_root)
    return graph.invoke(state)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the simplified Trust Bench multi-agent evaluation."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Path to the repository to evaluate (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("multi_agent_output"),
        help="Directory where reports should be written (default: ./multi_agent_output).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo.resolve()
    if not repo_root.exists():
        print(f"[error] Repository directory does not exist: {repo_root}")
        return 1

    final_state = run_workflow(repo_root)
    report = build_report_payload(final_state)
    outputs = write_report_outputs(report, args.output.resolve())

    summary = report.get("summary", {})
    print("=== Multi-Agent Evaluation Complete ===")
    print(f"Repository: {report.get('repo_root')}")
    print(f"Overall Score: {summary.get('overall_score', 'n/a')}")
    print(f"Grade: {summary.get('grade', 'n/a')}")
    print(f"Report (JSON): {outputs['json']}")
    print(f"Report (Markdown): {outputs['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
