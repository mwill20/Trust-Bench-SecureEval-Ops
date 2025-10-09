"""
agent_tools_glue.py

Glue code showing how to integrate tools_security into a LangGraph "Think→Act→Think" loop.
This module is conservative and includes a linear fallback for offline runs.
It expects src/tools_security.py to exist and exposes two small helpers:
- llm_tool_invoke_stub(state): a tiny LLM stub that returns tool_calls
- tools_executor_node(state): executes tool calls and appends results to state['meta']
"""

from typing import Dict, Any, List
import json, time, os
from pathlib import Path

try:
    from .tools_security import create_tool_registry, get_all_tools
except Exception:
    from tools_security import create_tool_registry, get_all_tools

# Simple heuristic LLM stub - in production replace with a real LLM -> tool binding
def llm_tool_invoke_stub(state: Dict[str, Any]) -> Dict[str, Any]:
    pending_idx = state.get(\"pending_index\")
    if pending_idx is None:
        return {}
    findings = state.get(\"findings\", [])
    if pending_idx >= len(findings):
        return {}
    f = findings[pending_idx]
    snippet = getattr(f, \"snippet\", \"\") if f else \"\"
    calls = []
    repo_root = state.get(\"repo_root\", state.get(\"repo_url\", \".\"))
    # heuristics
    if \"curl\" in snippet or \"| bash\" in snippet or \"base64\" in snippet:
        calls.append({\"name\": \"secrets_scan\", \"args\": {\"dir_path\": repo_root}})
    if \".env\" in snippet:
        calls.append({\"name\": \"env_content\", \"args\": {\"dir_path\": repo_root}})
    return {\"tool_calls\": calls, \"note\": \"heuristic-tool-suggestions\"}

def tools_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    reg = create_tool_registry()
    instr = state.get(\"llm_instruction\", {})  # expects {"tool_calls":[{...}]}
    tool_calls = instr.get(\"tool_calls\") or []
    executed = []
    for call in tool_calls:
        name = call.get(\"name\")
        args = call.get(\"args\", {}) or {}
        fn = reg.get(name)
        if not fn:
            executed.append({\"tool\": name, \"error\": \"unknown_tool\"})
            continue
        try:
            res = fn(**args)
        except Exception as e:
            res = {\"error\": str(e)}
        rec = {\"tool\": name, \"args\": args, \"result\": res, \"ts\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\", time.gmtime())}
        executed.append(rec)
        meta = state.setdefault(\"meta\", {})
        meta.setdefault(\"tool_calls\", []).append(rec)
        # Attach secrets_scan results to the pending finding if present
        if name == \"secrets_scan\" and isinstance(res, list) and res:
            idx = state.get(\"pending_index\")
            if idx is not None and idx < len(state.get(\"findings\", [])):
                f = state[\"findings\"][idx]
                try:
                    f.meta = getattr(f, \"meta\", {}) or {}
                    f.meta[\"secrets_scan\"] = res
                except Exception:
                    if isinstance(f, dict):
                        f.setdefault(\"meta\", {})[\"secrets_scan\"] = res
    return {\"executed\": executed}
