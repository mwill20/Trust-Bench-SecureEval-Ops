"""Typed helpers shared across the simplified multi-agent workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, TypedDict


@dataclass(frozen=True)
class ToolResult:
    """Normalized response from a tool invocation."""

    name: str
    score: float
    summary: str
    details: Dict[str, Any]


class AgentResult(TypedDict, total=False):
    """Structured output captured for each agent."""

    score: float
    summary: str
    details: Dict[str, Any]
    confidence: float


class Message(TypedDict, total=False):
    """Conversation events exchanged between agents."""

    sender: str
    recipient: str
    content: str
    data: Dict[str, Any]


class MultiAgentState(TypedDict, total=False):
    """Shared state that LangGraph nodes read/write."""

    repo_root: Path
    shared_memory: Dict[str, Any]
    messages: List[Message]
    agent_results: Dict[str, AgentResult]
    report: Dict[str, Any]
    metrics: Dict[str, Any]
    eval_weights: Dict[str, int]
    confidence_scores: Dict[str, float]
    process_visualization: Dict[str, Any]
