\
from typing import Dict
# Try LangGraph, but fall back to linear orchestrator if unavailable
try:
    from langgraph.graph import StateGraph
    _HAS_LG = True
except Exception:  # pragma: no cover
    _HAS_LG = False

from .agents.prompt_guard import prompt_guard
from .agents.code_guard import code_guard
from .agents.report_agent import compile_report
from .tools.repo_reader import load_repo

def run_pipeline(state: Dict) -> Dict:
    if not _HAS_LG:
        # Linear fallback
        state = load_repo(state)
        state = prompt_guard(state)
        state = code_guard(state)
        state = compile_report(state)
        return state

    # LangGraph DAG
    g = StateGraph(state_schema=dict)
    g.add_node("fetch_repo", load_repo)
    g.add_node("prompt_guard", prompt_guard)
    g.add_node("code_guard", code_guard)
    g.add_node("report", compile_report)

    g.set_entry_point("fetch_repo")
    g.add_edge("fetch_repo", "prompt_guard")
    g.add_edge("fetch_repo", "code_guard")
    g.add_edge(["prompt_guard", "code_guard"], "report")
    g.set_finish_point("report")

    app = g.compile()
    return app.invoke(state)
