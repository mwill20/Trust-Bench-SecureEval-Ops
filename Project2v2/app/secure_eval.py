"""SecureEval wrapper utilities to keep runtime behavior resilient."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from app.security.guardrails import clamp_output, validate_repo_input
from app.security.sandbox import safe_run
from app.util_resilience import retry, with_timeout
from multi_agent_system import build_orchestrator
from multi_agent_system.types import MultiAgentState


def _initial_state(repo_root: Path, eval_weights: Dict[str, int] | None = None) -> MultiAgentState:
    state: MultiAgentState = {
        "repo_root": repo_root,
        "shared_memory": {},
        "messages": [],
        "agent_results": {},
        "confidence_scores": {},
    }
    if eval_weights:
        state["eval_weights"] = eval_weights
    return state


def _invoke_workflow(repo_root: Path, eval_weights: Dict[str, int] | None = None) -> Dict[str, Any]:
    graph = build_orchestrator()
    return graph.invoke(_initial_state(repo_root, eval_weights))


@with_timeout(120)
@retry(max_tries=3, backoff=0.5)
def run_workflow_secure(repo_root: Path, eval_weights: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Run the orchestrator with retry/timeout protections."""

    return _invoke_workflow(repo_root, eval_weights)


def run_audit_enhanced(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input payload, execute audit, and clamp textual outputs."""

    request = validate_repo_input(payload)
    repo_path = request.path()
    if repo_path is None:
        raise ValueError("Validated payload missing repo_path for local execution")
    result = run_workflow_secure(repo_path, payload.get("eval_weights"))
    report = result.get("report")
    if isinstance(report, dict) and "summary" in report:
        summary_text = report["summary"].get("notes") if isinstance(report["summary"], dict) else None
        if isinstance(summary_text, str):
            report["summary"]["notes"] = clamp_output(summary_text)
    return result


__all__ = [
    "run_workflow_secure",
    "run_audit_enhanced",
    "safe_run",
]
