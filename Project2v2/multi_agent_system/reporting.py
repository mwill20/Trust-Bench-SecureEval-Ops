"""Utilities for producing human-readable outputs from agent runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

from .types import Message, MultiAgentState


def build_report_payload(state: MultiAgentState) -> Dict[str, Any]:
    """Normalize the final orchestrator state into a report dictionary."""
    timestamp = datetime.now(timezone.utc).isoformat()
    agent_results = state.get("agent_results", {})
    return {
        "generated_at": timestamp,
        "repo_root": str(state.get("repo_root", "")),
        "summary": state.get("report", {}),
        "agents": agent_results,
        "metrics": state.get("metrics", {}),
        "conversation": list(state.get("messages", [])),
    }


def _format_conversation(messages: Iterable[Message]) -> str:
    lines = []
    for entry in messages:
        sender = entry.get("sender", "Unknown")
        recipient = entry.get("recipient", "Unknown")
        content = entry.get("content", "").strip()
        lines.append(f"- **{sender} -> {recipient}:** {content}")
    return "\n".join(lines)


def _format_agent_section(agent_results: Dict[str, Dict[str, Any]]) -> str:
    lines = []
    for agent, payload in agent_results.items():
        score = payload.get("score", 0)
        summary = payload.get("summary", "")
        lines.append(f"### {agent}\n- Score: {score}\n- Summary: {summary}\n")
    return "\n".join(lines)


def _format_metrics_section(metrics: Dict[str, Any]) -> str:
    if not metrics:
        return "No instrumentation metrics recorded."

    lines = ["| Metric | Value |", "| --- | --- |"]
    lines.append(
        f"| System Latency (s) | {metrics.get('system_latency_seconds', 'n/a')} |"
    )
    lines.append(f"| Faithfulness | {metrics.get('faithfulness', 'n/a')} |")
    lines.append(
        f"| Refusal Accuracy | {metrics.get('refusal_accuracy', 'n/a')} |"
    )

    per_agent = metrics.get("per_agent_latency", {})
    for agent, timing in per_agent.items():
        total = timing.get("total_seconds", "n/a")
        lines.append(f"| {agent} total (s) | {total} |")
        for tool, duration in (timing.get("tool_breakdown") or {}).items():
            lines.append(f"| &nbsp;&nbsp;{tool} (s) | {duration} |")

    return "\n".join(lines)


def write_report_outputs(report: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    """Persist JSON and Markdown versions of the report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    markdown_path = output_dir / "report.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    markdown = [
        "# Trust Bench Multi-Agent Evaluation Report",
        f"- Generated at: {report.get('generated_at')}",
        f"- Repository: {report.get('repo_root')}",
        "",
        "## Composite Summary",
        json.dumps(report.get("summary", {}), indent=2),
        "",
        "## Agent Findings",
        _format_agent_section(report.get("agents", {})),
        "",
        "## Evaluation Metrics",
        _format_metrics_section(report.get("metrics", {})),
        "",
        "## Conversation Log",
        _format_conversation(report.get("conversation", [])),
    ]
    markdown_path.write_text("\n".join(markdown), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
