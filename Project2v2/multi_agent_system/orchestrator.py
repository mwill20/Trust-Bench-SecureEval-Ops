"""LangGraph orchestrator wiring the agents together."""

from __future__ import annotations

import time
from statistics import mean
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .agents import documentation_agent, manager_plan, quality_agent, security_agent
from .policy_tests import run_refusal_tests
from .types import AgentResult, MultiAgentState


def _evaluate_agent_outputs(results: Dict[str, AgentResult], eval_weights: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Aggregate agent results into a concise evaluation summary."""
    if not results:
        return {
            "overall_score": 0.0,
            "grade": "N/A",
            "notes": "No agent outputs were recorded.",
            "calculation_method": "none",
        }

    # Extract individual agent scores
    security_score = results.get("SecurityAgent", {}).get("score", 0.0)
    quality_score = results.get("QualityAgent", {}).get("score", 0.0) 
    docs_score = results.get("DocumentationAgent", {}).get("score", 0.0)
    
    # Calculate scores with or without weights
    if eval_weights:
        # Weighted calculation
        weights = {
            "security": eval_weights.get("security", 33),
            "quality": eval_weights.get("quality", 33), 
            "docs": eval_weights.get("docs", 34)
        }
        
        # Ensure weights sum to 100 (normalize if needed)
        total_weight = sum(weights.values())
        if total_weight != 100:
            for key in weights:
                weights[key] = (weights[key] / total_weight) * 100
        
        overall_score = round(
            (security_score * weights["security"] + 
             quality_score * weights["quality"] + 
             docs_score * weights["docs"]) / 100, 2
        )
        
        notes = f"Weighted composite: Security({weights['security']:.0f}%), Quality({weights['quality']:.0f}%), Docs({weights['docs']:.0f}%)"
        calculation_method = "weighted"
        
    else:
        # Standard equal-weight calculation
        scores = [result.get("score", 0.0) for result in results.values()]
        overall_score = round(mean(scores), 2)
        notes = "Equal-weight composite from agent contributions."
        calculation_method = "equal_weight"
    
    # Determine grade based on overall score
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
        "notes": notes,
        "calculation_method": calculation_method,
        "individual_scores": {
            "security": security_score,
            "quality": quality_score, 
            "documentation": docs_score
        },
        "weights_used": eval_weights if eval_weights else {"security": 33.33, "quality": 33.33, "docs": 33.34}
    }


def _collect_detail_tokens(payload: Any, *, tokens: set[str]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            tokens.add(str(key).lower())
            _collect_detail_tokens(value, tokens=tokens)
    elif isinstance(payload, list):
        tokens.add(str(len(payload)))
        for item in payload[:5]:
            _collect_detail_tokens(item, tokens=tokens)
    elif isinstance(payload, (int, float)):
        tokens.add(str(payload))


def _calculate_agent_confidence(agent_result: AgentResult) -> float:
    """Calculate confidence score for an agent result based on multiple factors."""
    summary = agent_result.get("summary", "")
    details = agent_result.get("details", {})
    score = agent_result.get("score", 0.0)
    
    # Factor 1: Response completeness (0.0-0.5)
    summary_length = len(summary.strip())
    detail_count = len(str(details))
    
    completeness_score = 0.0
    if summary_length > 100:  # Substantial summary
        completeness_score += 0.3
    elif summary_length > 50:  # Moderate summary
        completeness_score += 0.2
    elif summary_length > 20:  # Basic summary
        completeness_score += 0.1
    
    if detail_count > 200:  # Rich details
        completeness_score += 0.2
    elif detail_count > 50:  # Some details
        completeness_score += 0.1
        
    # Factor 2: Score consistency (0.0-0.3)
    # Higher scores generally indicate more confident analysis
    score_confidence = min(0.3, score / 100.0 * 0.3)
    
    # Factor 3: Specificity indicators (0.0-0.3)
    specificity_score = 0.0
    summary_lower = summary.lower()
    
    # Look for specific technical terms and concrete findings
    specific_terms = ['vulnerability', 'error', 'warning', 'issue', 'recommendation', 
                     'function', 'class', 'method', 'variable', 'file', 'line', 'test', 'code']
    specific_count = sum(1 for term in specific_terms if term in summary_lower)
    specificity_score = min(0.3, specific_count * 0.06)
    
    # Base confidence (ensures reasonable minimum)
    base_confidence = 0.2
    
    # Combine all factors
    confidence = base_confidence + completeness_score + score_confidence + specificity_score
    
    # Normalize to 0.0-1.0 range
    confidence = min(1.0, max(0.15, confidence))  # Ensure minimum 15% confidence
    
    return round(confidence, 3)


def _faithfulness_score(agent_result: AgentResult) -> float:
    summary = (agent_result.get("summary") or "").lower()
    details = agent_result.get("details") or {}
    if not summary:
        return 0.0

    tokens: set[str] = set()
    _collect_detail_tokens(details, tokens=tokens)
    tokens.discard("")
    if not tokens:
        # Nothing tangible to compare but summary exists.
        return 0.5

    matches = sum(1 for token in tokens if token in summary)
    coverage = matches / max(1, len(tokens))
    base = 0.2 if matches == 0 else 0.4
    score = min(1.0, base + coverage * 0.6)
    return round(score, 2)


def manager_finalize(state: MultiAgentState) -> Dict[str, Any]:
    # Get eval_weights from state if available
    eval_weights = state.get("eval_weights")
    agent_results = state.get("agent_results", {})
    
    # Calculate confidence scores for each agent
    confidence_scores = {}
    for agent_name, result in agent_results.items():
        confidence_scores[agent_name] = _calculate_agent_confidence(result)
    
    report = _evaluate_agent_outputs(agent_results, eval_weights)
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

    # Metrics instrumentation
    run_started = shared_memory.get("perf_session_started_at")
    system_latency = (
        round(time.perf_counter() - run_started, 4) if isinstance(run_started, (int, float)) else 0.0
    )
    per_agent_latency = shared_memory.get("timings", {})

    faithfulness_scores = [
        _faithfulness_score(agent_payload)
        for agent_payload in agent_results.values()
    ]
    faithfulness = round(
        sum(faithfulness_scores) / len(faithfulness_scores), 2
    ) if faithfulness_scores else 0.0

    refusals, total_prompts = run_refusal_tests()
    refusal_accuracy = round(refusals / total_prompts, 2) if total_prompts else 1.0

    metrics = {
        "system_latency_seconds": system_latency,
        "faithfulness": faithfulness,
        "refusal_accuracy": refusal_accuracy,
        "per_agent_latency": per_agent_latency,
    }
    
    messages.append(
        {
            "sender": "Manager",
            "recipient": "All Agents", 
            "content": f"Evaluation complete. Grade: {report['grade'].upper()} ({report['overall_score']} pts).{collab_note}",
            "data": {
                **report,
                "collaboration_metrics": {
                    "interactions": collaboration_count,
                    "adjustments": collaboration_summary,
                },
                "metrics": metrics,
            },
        }
    )
    
    updated_shared_memory = dict(shared_memory)
    updated_shared_memory["composite_assessment"] = report
    updated_shared_memory["collaboration_summary"] = {
        "total_interactions": collaboration_count,
        "collaborative_adjustments": collaboration_summary
    }
    updated_shared_memory["metrics"] = metrics
    
    return {
        "messages": messages,
        "shared_memory": updated_shared_memory,
        "report": report,
        "metrics": metrics,
        "confidence_scores": confidence_scores,
    }


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
