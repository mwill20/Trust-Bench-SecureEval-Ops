"""LangGraph orchestrator wiring the agents together."""

from __future__ import annotations

from statistics import mean
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .agents import documentation_agent, manager_plan, quality_agent, security_agent
from .types import AgentResult, MultiAgentState


def _evaluate_agent_outputs(results: Dict[str, AgentResult]) -> Dict[str, Any]:
    """Aggregate agent results into a concise evaluation summary."""
    if not results:
        return {
            "overall_score": 0.0,
            "grade": "N/A",
            "notes": "No agent outputs were recorded.",
        }

    scores = [result.get("score", 0.0) for result in results.values()]
    overall_score = round(mean(scores), 2)
    if overall_score >= 85:
        grade = "excellent"
    elif overall_score >= 70:
        grade = "good"
    elif overall_score >= 50:
        grade = "fair"
    else:
        grade = "needs_attention"

    return {
        "overall_score": overall_score,
        "grade": grade,
        "notes": "Composite built from agent contributions.",
    }


def manager_finalize(state: MultiAgentState) -> Dict[str, Any]:
    report = _evaluate_agent_outputs(state.get("agent_results", {}))
    messages = list(state.get("messages", []))
    messages.append(
        {
            "sender": "Manager",
            "recipient": "All Agents",
            "content": f"Evaluation complete. Grade: {report['grade'].upper()} ({report['overall_score']} pts).",
            "data": report,
        }
    )
    shared_memory = dict(state.get("shared_memory", {}))
    shared_memory["composite_assessment"] = report
    return {"messages": messages, "shared_memory": shared_memory, "report": report}


def build_orchestrator() -> Any:
    workflow: StateGraph[MultiAgentState] = StateGraph(MultiAgentState)
    workflow.add_node("manager_plan", manager_plan)
    workflow.add_node("security_agent", security_agent)
    workflow.add_node("quality_agent", quality_agent)
    workflow.add_node("documentation_agent", documentation_agent)
    workflow.add_node("manager_finalize", manager_finalize)

    workflow.set_entry_point("manager_plan")
    workflow.add_edge("manager_plan", "security_agent")
    workflow.add_edge("security_agent", "quality_agent")
    workflow.add_edge("quality_agent", "documentation_agent")
    workflow.add_edge("documentation_agent", "manager_finalize")
    workflow.add_edge("manager_finalize", END)

    return workflow.compile()
