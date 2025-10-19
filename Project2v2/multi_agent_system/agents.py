"""Agent node definitions used by the LangGraph orchestrator."""

from __future__ import annotations

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
    }
    return {"agent_results": results}


def manager_plan(state: MultiAgentState) -> Dict[str, Any]:
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

    messages = list(state.get("messages", []))
    for task in tasks:
        messages = _append_message(
            messages,
            sender="Manager",
            recipient=task["agent"],
            content=f"Task assigned: {task['objective']}",
            data={"tool": task["tool"]},
        )
    return {"shared_memory": shared_memory, "messages": messages}


def security_agent(state: MultiAgentState) -> Dict[str, Any]:
    repo_root = state["repo_root"]
    tool_result = run_secret_scan(repo_root)

    messages = _append_message(
        state.get("messages", []),
        sender="SecurityAgent",
        recipient="Manager",
        content="Secret scan completed.",
        data=serialize_tool_result(tool_result),
    )
    shared_memory = deepcopy(state.get("shared_memory", {}))
    shared_memory["security_findings"] = tool_result.details.get("matches", [])
    return {
        "messages": messages,
        "shared_memory": shared_memory,
        **_store_agent_result(state, "SecurityAgent", tool_result),
    }


def quality_agent(state: MultiAgentState) -> Dict[str, Any]:
    repo_root = state["repo_root"]
    tool_result = analyze_repository_structure(repo_root)

    messages = _append_message(
        state.get("messages", []),
        sender="QualityAgent",
        recipient="Manager",
        content="Repository structure summarized.",
        data=serialize_tool_result(tool_result),
    )
    shared_memory = deepcopy(state.get("shared_memory", {}))
    shared_memory["language_histogram"] = tool_result.details.get("language_histogram", {})
    return {
        "messages": messages,
        "shared_memory": shared_memory,
        **_store_agent_result(state, "QualityAgent", tool_result),
    }


def documentation_agent(state: MultiAgentState) -> Dict[str, Any]:
    repo_root = state["repo_root"]
    tool_result = evaluate_documentation(repo_root)

    messages = _append_message(
        state.get("messages", []),
        sender="DocumentationAgent",
        recipient="Manager",
        content="Documentation review finished.",
        data=serialize_tool_result(tool_result),
    )
    shared_memory = deepcopy(state.get("shared_memory", {}))
    shared_memory["documentation"] = tool_result.details
    return {
        "messages": messages,
        "shared_memory": shared_memory,
        **_store_agent_result(state, "DocumentationAgent", tool_result),
    }
