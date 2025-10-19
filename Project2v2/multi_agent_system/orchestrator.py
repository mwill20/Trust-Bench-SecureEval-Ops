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
    shared_memory = state.get("shared_memory", {})
    
    # Count collaboration interactions
    collaboration_count = sum(1 for msg in messages if msg.get("sender") != "Manager" and msg.get("recipient") != "Manager")
    
    # Check for collaborative adjustments
    security_context = shared_memory.get("security_context", {})
    quality_metrics = shared_memory.get("quality_metrics", {})
    doc_adjustments = shared_memory.get("documentation", {}).get("collaboration_adjustments", [])
    
    collaboration_summary = []
    if security_context.get("requires_attention"):
        collaboration_summary.append(f"Security findings influenced quality and documentation scores")
    if quality_metrics.get("adjusted_for_security"):
        collaboration_summary.append(f"Quality assessment incorporated security analysis")
    if doc_adjustments:
        collaboration_summary.append(f"Documentation score adjusted based on quality metrics")
    
    collab_note = f" Agents collaborated on {collaboration_count} cross-communications." if collaboration_count > 0 else ""
    if collaboration_summary:
        collab_note += f" Collaborative adjustments: {'; '.join(collaboration_summary)}."
    
    messages.append(
        {
            "sender": "Manager",
            "recipient": "All Agents", 
            "content": f"Evaluation complete. Grade: {report['grade'].upper()} ({report['overall_score']} pts).{collab_note}",
            "data": {**report, "collaboration_metrics": {"interactions": collaboration_count, "adjustments": collaboration_summary}},
        }
    )
    
    updated_shared_memory = dict(shared_memory)
    updated_shared_memory["composite_assessment"] = report
    updated_shared_memory["collaboration_summary"] = {
        "total_interactions": collaboration_count,
        "collaborative_adjustments": collaboration_summary
    }
    
    return {"messages": messages, "shared_memory": updated_shared_memory, "report": report}


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
