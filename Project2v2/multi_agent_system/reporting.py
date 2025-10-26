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
    eval_weights = state.get("eval_weights")
    report_summary = state.get("report", {})
    confidence_scores = state.get("confidence_scores", {})
    
    return {
        "generated_at": timestamp,
        "repo_root": str(state.get("repo_root", "")),
        "summary": report_summary,
        "agents": agent_results,
        "metrics": state.get("metrics", {}),
        "conversation": list(state.get("messages", [])),
        "evaluation_weights": eval_weights,
        "calculation_method": report_summary.get("calculation_method", "equal_weight"),
        "individual_scores": report_summary.get("individual_scores", {}),
        "weights_used": report_summary.get("weights_used", {}),
        "confidence_scores": confidence_scores,
        "process_visualization": state.get("process_visualization", {}),
    }


def _format_conversation(messages: Iterable[Message]) -> str:
    lines = []
    for entry in messages:
        sender = entry.get("sender", "Unknown")
        recipient = entry.get("recipient", "Unknown")
        content = entry.get("content", "").strip()
        lines.append(f"- **{sender} -> {recipient}:** {content}")
    return "\n".join(lines)


def _format_agent_section(agent_results: Dict[str, Dict[str, Any]], confidence_scores: Dict[str, float] = None) -> str:
    if confidence_scores is None:
        confidence_scores = {}
    
    lines = []
    for agent, payload in agent_results.items():
        score = payload.get("score", 0)
        confidence = confidence_scores.get(agent, 0.0)
        summary = payload.get("summary", "")
        
        # Format confidence with visual indicator
        conf_percent = int(confidence * 100)
        if confidence >= 0.8:
            conf_indicator = "HIGH"
            conf_emoji = "🟢"
        elif confidence >= 0.5:
            conf_indicator = "MEDIUM" 
            conf_emoji = "🟡"
        else:
            conf_indicator = "LOW"
            conf_emoji = "🔴"
        
        lines.append(f"### {agent}")
        lines.append(f"- **Score:** {score}")
        lines.append(f"- **Confidence:** {conf_emoji} {conf_indicator} - {conf_percent}% ({confidence:.3f})")
        lines.append(f"- **Summary:** {summary}\n")
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


def _format_process_visualization(process: Dict[str, Any]) -> str:
    if not process:
        return "Process timeline data not recorded."

    rounds = process.get("rounds", [])
    lines: list[str] = []
    if rounds:
        lines.append("| Stage | Progress | Summary |")
        lines.append("| --- | --- | --- |")
        for entry in rounds:
            title = entry.get("title") or entry.get("label", "Round")
            percentage = entry.get("percentage", 0)
            summary = entry.get("summary", "")
            lines.append(f"| {title} | {percentage}% | {summary} |")

    conflict = process.get("conflict_resolution", {})
    if conflict:
        lines.append("")
        lines.append("**Conflict Resolution Snapshot**")
        initial = conflict.get("initial_positions", {})
        for agent_key, payload in initial.items():
            priority = payload.get("priority", "n/a")
            score = payload.get("score", "n/a")
            lines.append(f"- {agent_key.title()}: {priority} ({score})")
        consensus = conflict.get("consensus", {})
        if consensus:
            lines.append(
                f"- Final Alignment: {consensus.get('priority', 'n/a')} "
                f"(Grade {consensus.get('grade', 'n/a').upper()}, "
                f"Score {consensus.get('overall_score', 'n/a')})"
            )
            notes = consensus.get("notes")
            if notes:
                lines.append(f"- Notes: {notes}")

    collaboration = process.get("collaboration", {})
    if collaboration:
        lines.append("")
        cross = collaboration.get("cross_communications")
        if cross is not None:
            lines.append(f"- Cross-agent communications: {cross}")
        notes = collaboration.get("notes")
        if notes:
            lines.append(f"- Collaboration notes: {notes}")

    dialogue = process.get("dialogue", [])
    if dialogue:
        lines.append("")
        lines.append("**Negotiation Highlights**")
        for entry in dialogue[-5:]:
            agent = entry.get("agent", "Agent")
            content = entry.get("content", "").strip()
            mood = entry.get("mood", "neutral")
            lines.append(f"- {agent} ({mood}): {content}")

    return "\n".join(lines) if lines else "Process timeline data not recorded."


def _format_weight_section(report: Dict[str, Any]) -> str:
    """Format evaluation weights and scoring method information."""
    calculation_method = report.get("calculation_method", "equal_weight")
    individual_scores = report.get("individual_scores", {})
    weights_used = report.get("weights_used", {})
    
    lines = ["## Evaluation Weight Configuration"]
    
    if calculation_method == "weighted":
        lines.append(f"**Scoring Method:** Custom Weighted Average")
        lines.append("")
        lines.append("| Agent | Individual Score | Weight | Weighted Contribution |")
        lines.append("| --- | --- | --- | --- |")
        
        for agent_key, score in individual_scores.items():
            if agent_key == "security":
                weight = weights_used.get("security", 33)
                agent_name = "Security Agent"
            elif agent_key == "quality":
                weight = weights_used.get("quality", 33) 
                agent_name = "Quality Agent"
            elif agent_key == "documentation":
                weight = weights_used.get("docs", 34)
                agent_name = "Documentation Agent"
            else:
                continue
                
            contribution = round((score * weight) / 100, 2)
            lines.append(f"| {agent_name} | {score} | {weight:.0f}% | {contribution} |")
            
    else:
        lines.append(f"**Scoring Method:** Equal Weight Average (33.33% each agent)")
        lines.append("")
        lines.append("| Agent | Individual Score | Weight |")
        lines.append("| --- | --- | --- |")
        
        for agent_key, score in individual_scores.items():
            if agent_key == "security":
                agent_name = "Security Agent"
            elif agent_key == "quality":
                agent_name = "Quality Agent"
            elif agent_key == "documentation":
                agent_name = "Documentation Agent"
            else:
                continue
                
            lines.append(f"| {agent_name} | {score} | 33.33% |")
    
    return "\n".join(lines)


def write_report_outputs(report: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    """Persist JSON and Markdown versions of the report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    markdown_path = output_dir / "report.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Format weight configuration section
    weight_section = _format_weight_section(report)
    
    markdown = [
        "# Trust Bench Multi-Agent Evaluation Report",
        f"- Generated at: {report.get('generated_at')}",
        f"- Repository: {report.get('repo_root')}",
        "",
        "## Composite Summary",
        json.dumps(report.get("summary", {}), indent=2),
        "",
        "## Negotiation Timeline",
        _format_process_visualization(report.get("process_visualization", {})),
        "",
        weight_section,
        "",
        "## Agent Findings",
        _format_agent_section(report.get("agents", {}), report.get("confidence_scores", {})),
        "",
        "## Evaluation Metrics",
        _format_metrics_section(report.get("metrics", {})),
        "",
        "## Conversation Log",
        _format_conversation(report.get("conversation", [])),
    ]
    markdown_path.write_text("\n".join(markdown), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
