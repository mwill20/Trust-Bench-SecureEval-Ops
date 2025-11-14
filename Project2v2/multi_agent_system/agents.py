"""
Agent node definitions used by the LangGraph orchestrator.

This module implements the specialized agents that perform repository evaluation:
- SecurityAgent: Scans for secrets and security vulnerabilities
- QualityAgent: Analyzes code structure and testing practices  
- DocumentationAgent: Evaluates documentation completeness and quality

Agents collaborate by sharing findings through the shared_memory context and
explicit inter-agent messages.
"""

from __future__ import annotations

import logging
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from .tools import (
    analyze_repository_structure,
    evaluate_documentation,
    run_secret_scan,
    serialize_tool_result,
)
from .types import AgentResult, Message, MultiAgentState, ToolResult
from core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


def _append_message(messages: list[Message], **payload: Any) -> list[Message]:
    updated = list(messages)
    record: Message = {
        "sender": payload.get("sender", ""),
        "recipient": payload.get("recipient", ""),
        "content": payload.get("content", ""),
        "data": payload.get("data", {}),
    }
    updated.append(record)
    return updated


def _store_agent_result(
    state: MultiAgentState, agent_key: str, tool_result: ToolResult
) -> Dict[str, Dict[str, AgentResult]]:
    results = deepcopy(state.get("agent_results", {}))
    results[agent_key] = {
        "score": tool_result.score,
        "summary": tool_result.summary,
        "details": tool_result.details,
        "confidence": 0.0,  # Will be calculated later in orchestrator
    }
    return {"agent_results": results}


def _record_timing(
    shared_memory: Dict[str, Any],
    agent_name: str,
    total_seconds: float,
    tool_timings: Dict[str, float],
) -> Dict[str, Any]:
    timings: Dict[str, Any] = dict(shared_memory.get("timings", {}))
    timings[agent_name] = {
        "total_seconds": round(total_seconds, 4),
        "tool_breakdown": {
            tool: round(duration, 4) for tool, duration in tool_timings.items()
        },
    }
    updated = dict(shared_memory)
    updated["timings"] = timings
    return updated


def manager_plan(state: MultiAgentState) -> Dict[str, Any]:
    """
    Initialize the multi-agent workflow by assigning tasks to specialized agents.
    
    This is the first node in the orchestration graph. It sets up the evaluation
    session, assigns objectives to each agent, and preserves configuration like
    custom evaluation weights.
    
    Args:
        state: Initial multi-agent workflow state containing repo_root and optional eval_weights.
    
    Returns:
        dict: Updated state with task assignments, session metadata, and initial messages.
    """
    tasks = [
        {
            "agent": "SecurityAgent",
            "objective": "Scan the repository for high-signal secrets or credentials.",
            "tool": "secret_scan",
        },
        {
            "agent": "QualityAgent",
            "objective": "Summarize repository structure and gauge test coverage.",
            "tool": "repository_structure",
        },
        {
            "agent": "DocumentationAgent",
            "objective": "Review README files and verify documentation depth.",
            "tool": "documentation_review",
        },
    ]
    shared_memory = deepcopy(state.get("shared_memory", {}))
    shared_memory["tasks"] = tasks
    shared_memory["session_started_at"] = datetime.now(timezone.utc).isoformat()
    shared_memory["perf_session_started_at"] = time.perf_counter()
    shared_memory.setdefault("timings", {})

    messages = list(state.get("messages", []))
    for task in tasks:
        messages = _append_message(
            messages,
            sender="Manager",
            recipient=task["agent"],
            content=f"Task assigned: {task['objective']}",
            data={"tool": task["tool"]},
        )
    # Preserve eval_weights from the original state
    result = {"shared_memory": shared_memory, "messages": messages}
    if "eval_weights" in state:
        result["eval_weights"] = state["eval_weights"]
    return result


def security_agent(state: MultiAgentState) -> Dict[str, Any]:
    """
    Execute security evaluation by scanning for secrets and vulnerabilities.
    
    Args:
        state: Current multi-agent workflow state.
    
    Returns:
        dict: Updated state with security findings and agent results.
    
    Raises:
        AgentExecutionError: If security scanning fails.
    """
    try:
        repo_root = state["repo_root"]
        logger.info(f"SecurityAgent: Starting security scan for {repo_root}")
        agent_start = time.perf_counter()
        tool_start = time.perf_counter()
        tool_result = run_secret_scan(repo_root)
        tool_elapsed = time.perf_counter() - tool_start
        logger.debug(f"SecurityAgent: Secret scan completed in {tool_elapsed:.2f}s")
    except Exception as e:
        logger.error(f"SecurityAgent: Failed to execute secret scan: {e}", exc_info=True)
        raise AgentExecutionError(f"SecurityAgent failed during secret scan: {e}") from e
    
    # Prepare findings for other agents to use
    security_findings = tool_result.details.get("matches", [])
    
    # Enhanced security analysis context
    risk_level = "low"
    if len(security_findings) > 5:
        risk_level = "high"
    elif len(security_findings) > 0:
        risk_level = "medium"
    
    messages = _append_message(
        state.get("messages", []),
        sender="SecurityAgent",
        recipient="Manager",
        content=f"Secret scan completed. Risk level: {risk_level.upper()} ({len(security_findings)} findings).",
        data=serialize_tool_result(tool_result),
    )
    
    # Proactively notify other agents about security context
    if security_findings:
        messages = _append_message(
            messages,
            sender="SecurityAgent",
            recipient="QualityAgent",
            content=f"FYI: Found {len(security_findings)} security issues that may impact quality assessment.",
            data={"security_context": {"findings_count": len(security_findings), "risk_level": risk_level}}
        )
        
        messages = _append_message(
            messages,
            sender="SecurityAgent",
            recipient="DocumentationAgent", 
            content=f"Alert: {len(security_findings)} security findings detected - please check if docs address security practices.",
            data={"security_alert": {"findings_count": len(security_findings), "risk_level": risk_level}}
        )
    
    shared_memory = deepcopy(state.get("shared_memory", {}))
    shared_memory["security_findings"] = security_findings
    shared_memory["security_context"] = {
        "risk_level": risk_level,
        "findings_count": len(security_findings),
        "requires_attention": len(security_findings) > 0
    }
    shared_memory = _record_timing(
        shared_memory,
        "SecurityAgent",
        time.perf_counter() - agent_start,
        {"run_secret_scan": tool_elapsed},
    )
    
    return {
        "messages": messages,
        "shared_memory": shared_memory,
        **_store_agent_result(state, "SecurityAgent", tool_result),
    }


def quality_agent(state: MultiAgentState) -> Dict[str, Any]:
    """
    Execute quality evaluation by analyzing repository structure and testing.
    
    Args:
        state: Current multi-agent workflow state.
    
    Returns:
        dict: Updated state with quality metrics and agent results.
    
    Raises:
        AgentExecutionError: If quality analysis fails.
    """
    try:
        repo_root = state["repo_root"]
        shared_memory = state.get("shared_memory", {})
        logger.info(f"QualityAgent: Starting quality analysis for {repo_root}")
        agent_start = time.perf_counter()
        
        tool_start = time.perf_counter()
        tool_result = analyze_repository_structure(repo_root)
        tool_elapsed = time.perf_counter() - tool_start
        logger.debug(f"QualityAgent: Structure analysis completed in {tool_elapsed:.2f}s")
    except Exception as e:
        logger.error(f"QualityAgent: Failed to analyze repository structure: {e}", exc_info=True)
        raise AgentExecutionError(f"QualityAgent failed during structure analysis: {e}") from e
    
    # Collaborate with Security Agent findings
    security_findings = shared_memory.get("security_findings", [])
    if security_findings:
        # Reduce quality score if security issues found
        security_penalty = min(len(security_findings) * 5, 25)  # Max 25 point penalty
        adjusted_score = max(0, tool_result.score - security_penalty)
        
        # Create new tool result with adjusted score
        from .types import ToolResult
        tool_result = ToolResult(
            name=tool_result.name,
            score=adjusted_score,
            summary=f"{tool_result.summary} (Adjusted for {len(security_findings)} security findings)",
            details=tool_result.details
        )
        
        # Add collaboration note
        collab_message = f"Adjusted quality score down by {security_penalty} points due to {len(security_findings)} security finding(s) from SecurityAgent."
        
        # Send direct message to SecurityAgent
        messages = _append_message(
            state.get("messages", []),
            sender="QualityAgent",
            recipient="SecurityAgent",
            content=f"Incorporated your {len(security_findings)} security findings into quality assessment.",
            data={"security_penalty": security_penalty}
        )
    else:
        messages = list(state.get("messages", []))
        collab_message = "No security issues found - maintaining base quality score."
    
    # Report back to Manager
    messages = _append_message(
        messages,
        sender="QualityAgent",
        recipient="Manager",
        content=f"Repository structure summarized. {collab_message}",
        data=serialize_tool_result(tool_result),
    )
    
    updated_shared_memory = deepcopy(shared_memory)
    updated_shared_memory["language_histogram"] = tool_result.details.get("language_histogram", {})
    updated_shared_memory["quality_metrics"] = {
        "total_files": tool_result.details.get("total_files", 0),
        "test_ratio": tool_result.details.get("test_ratio", 0),
        "adjusted_for_security": len(security_findings) > 0
    }
    updated_shared_memory = _record_timing(
        updated_shared_memory,
        "QualityAgent",
        time.perf_counter() - agent_start,
        {"analyze_repository_structure": tool_elapsed},
    )
    
    return {
        "messages": messages,
        "shared_memory": updated_shared_memory,
        **_store_agent_result(state, "QualityAgent", tool_result),
    }


def documentation_agent(state: MultiAgentState) -> Dict[str, Any]:
    """
    Execute documentation evaluation by reviewing README and docs quality.
    
    Args:
        state: Current multi-agent workflow state.
    
    Returns:
        dict: Updated state with documentation assessment and agent results.
    
    Raises:
        AgentExecutionError: If documentation evaluation fails.
    """
    try:
        repo_root = state["repo_root"]
        shared_memory = state.get("shared_memory", {})
        logger.info(f"DocumentationAgent: Starting documentation evaluation for {repo_root}")
        agent_start = time.perf_counter()
        
        tool_start = time.perf_counter()
        tool_result = evaluate_documentation(repo_root)
        tool_elapsed = time.perf_counter() - tool_start
        logger.debug(f"DocumentationAgent: Documentation evaluation completed in {tool_elapsed:.2f}s")
    except Exception as e:
        logger.error(f"DocumentationAgent: Failed to evaluate documentation: {e}", exc_info=True)
        raise AgentExecutionError(f"DocumentationAgent failed during documentation evaluation: {e}") from e
    
    # Collaborate with Quality Agent findings
    quality_metrics = shared_memory.get("quality_metrics", {})
    security_findings = shared_memory.get("security_findings", [])
    
    messages = list(state.get("messages", []))
    collaboration_notes = []
    
    if quality_metrics:
        total_files = quality_metrics.get("total_files", 0)
        test_ratio = quality_metrics.get("test_ratio", 0)
        
        # Adjust documentation score based on project size and quality
        adjusted_score = tool_result.score
        
        if total_files > 100:
            # Large projects need better documentation
            if tool_result.score < 80:
                size_penalty = 10
                adjusted_score = max(0, adjusted_score - size_penalty)
                collaboration_notes.append(f"Large project ({total_files} files) needs better documentation - reduced score by {size_penalty}")
        
        if test_ratio == 0 and total_files > 10:
            # No tests detected - documentation should mention testing approach
            test_penalty = 5
            adjusted_score = max(0, adjusted_score - test_penalty)
            collaboration_notes.append(f"No tests found by QualityAgent - documentation lacks testing info - reduced score by {test_penalty}")
            
        # Create adjusted tool result if needed
        if adjusted_score != tool_result.score:
            from .types import ToolResult
            tool_result = ToolResult(
                name=tool_result.name,
                score=adjusted_score,
                summary=f"{tool_result.summary} (Adjusted based on quality metrics)",
                details=tool_result.details
            )
        
        # Send collaboration message to QualityAgent
        messages = _append_message(
            messages,
            sender="DocumentationAgent",
            recipient="QualityAgent",
            content=f"Used your metrics (files: {total_files}, test ratio: {test_ratio:.1%}) to enhance documentation assessment.",
            data={"collaboration": "quality_metrics_integration"}
        )
    
    if security_findings:
        # If security issues exist, check if documentation mentions security practices
        if tool_result.score > 90:  # Only excellent docs should maintain high score with security issues
            security_doc_penalty = 5
            adjusted_score = max(0, tool_result.score - security_doc_penalty)
            collaboration_notes.append(f"Security issues found but not addressed in docs - reduced score by {security_doc_penalty}")
            
            # Create adjusted tool result
            from .types import ToolResult
            tool_result = ToolResult(
                name=tool_result.name,
                score=adjusted_score,
                summary=f"{tool_result.summary} (Adjusted for security gaps)",
                details=tool_result.details
            )
            
            # Send message to SecurityAgent
            messages = _append_message(
                messages,
                sender="DocumentationAgent", 
                recipient="SecurityAgent",
                content=f"Noted your {len(security_findings)} findings - documentation lacks security guidance.",
                data={"security_doc_gap": True}
            )
    
    # Report comprehensive analysis to Manager
    collab_summary = "; ".join(collaboration_notes) if collaboration_notes else "Baseline documentation assessment maintained."
    
    messages = _append_message(
        messages,
        sender="DocumentationAgent",
        recipient="Manager",
        content=f"Documentation review finished. {collab_summary}",
        data=serialize_tool_result(tool_result),
    )
    
    updated_shared_memory = deepcopy(shared_memory)
    updated_shared_memory["documentation"] = tool_result.details
    updated_shared_memory["documentation"]["collaboration_adjustments"] = collaboration_notes
    updated_shared_memory = _record_timing(
        updated_shared_memory,
        "DocumentationAgent",
        time.perf_counter() - agent_start,
        {"evaluate_documentation": tool_elapsed},
    )
    
    return {
        "messages": messages,
        "shared_memory": updated_shared_memory,
        **_store_agent_result(state, "DocumentationAgent", tool_result),
    }
