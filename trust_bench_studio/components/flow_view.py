"""Flow-oriented visualization of orchestrator and agents."""

from __future__ import annotations

import subprocess
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

import streamlit as st

from trust_bench_studio.utils import (
    load_agents_manifest,
    synthesize_verdict,
)
from trust_bench_studio.utils.llm import explain
from trust_bench_studio.utils.mcp_client import MCPClient
from trust_bench_studio.utils.run_store import RunSummary


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .flow-card {background:#15171b;border:1px solid #2c3240;border-radius:12px;
          padding:12px;min-width:240px;max-width:640px;box-shadow:0 4px 12px rgba(0,0,0,0.18);}
        .flow-card.small {min-width:170px;max-width:210px;border-radius:12px;
          border:1px solid #2c3240;background:#14161a;box-shadow:none;transition:box-shadow .2s;}
        .flow-card.small:hover {box-shadow:0 6px 18px rgba(0,0,0,0.25);border-color:#3a4154;}
        .flow-title {font-weight:600;font-size:15px;margin-bottom:4px;}
        .flow-badge {font-size:12px;opacity:0.85;margin-top:4px;}
        .flow-dropdown {font-size:13px;opacity:0.9;text-align:left;}
        .flow-dropdown summary {cursor:pointer;color:#9aa7ff;}
        .flow-row {display:flex;align-items:center;justify-content:center;gap:18px;}
        .flow-wrap {display:flex;flex-direction:column;gap:18px;margin-top:8px;}
        .flow-link {stroke:#4b5062;stroke-width:2;fill:none;opacity:.9;}
        .flow-link.inflight {stroke-dasharray:6 6;animation:dash 1.1s linear infinite;
          filter:drop-shadow(0 0 3px #8aa2ff);}
        .flow-link.done {stroke:#8aa2ff;stroke-width:2.5;}
        @keyframes dash {to{stroke-dashoffset:-120;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _flow_template(orch_state: str, orch_tip: str, paths: str, agent_cards: str) -> str:
    return f"""
    <div class="flow-wrap">
      <div class="flow-row">
        <div class="flow-card" style="text-align:left">
          <div class="flow-title">User Input</div>
          <div id="user-box"></div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-card flow-node" id="orchestrator">
          <div class="flow-title">Logos - Orchestrator</div>
          <div class="flow-badge">State: {orch_state}</div>
          <div style="font-size:13px;opacity:0.85">{orch_tip}</div>
        </div>
      </div>
      <div class="flow-row" style="position:relative;height:140px;">
        <svg width="1000" height="120" viewBox="0 0 1000 120">
          {paths}
        </svg>
      </div>
      <div class="flow-row" id="agent-row" style="flex-wrap:wrap">
        {agent_cards}
      </div>
    </div>
    """


def _agent_card(
    accent: str,
    name: str,
    state: str,
    score: Optional[str],
    desc: str,
    skills_tools: str,
    chat_btn: str,
) -> str:
    badge_score = f" • Score: {score}" if score and score != "—" else ""
    return (
        "<div class='flow-card small' style='border-top:4px solid {accent}'>"
        "<div class='flow-title'>{name}</div>"
        "<div class='flow-badge'>State: {state}{badge_score}</div>"
        "<details class='flow-dropdown'><summary>About</summary>"
        "<div>{desc}</div>"
        "</details>"
        "<details class='flow-dropdown'><summary>Skills &amp; Tools</summary>"
        "<div>{skills_tools}</div>"
        "</details>"
        "<div style='margin-top:8px'>{chat_btn}</div>"
        "</div>"
    ).format(
        accent=accent,
        name=name,
        state=state,
        badge_score=badge_score,
        desc=desc,
        skills_tools=skills_tools,
        chat_btn=chat_btn,
    )


def _mk_path(x1: float, y1: float, x2: float, y2: float, state: str) -> str:
    state_lower = state.lower()
    if state_lower in {"active", "running", "processing"}:
        klass = "flow-link inflight"
    elif state_lower in {"complete", "done", "finished"}:
        klass = "flow-link done"
    else:
        klass = "flow-link"
    return (
        f"<path class='{klass}' d='M{x1},{y1} C{(x1+x2)/2},{y1} {(x1+x2)/2},{y2} {x2},{y2}' />"
    )


def _extract_trace(summary: Optional[RunSummary]) -> Dict[str, Any]:
    if not summary:
        return {}
    raw = summary.raw or {}
    trace = raw.get("trace")
    if isinstance(trace, dict):
        return trace
    agents_map: Dict[str, Dict[str, Any]] = {}
    for snapshot in summary.agents:
        if not isinstance(snapshot, dict):
            continue
        key_candidates = {
            str(snapshot.get("id", "")).lower(),
            str(snapshot.get("agent_id", "")).lower(),
            str(snapshot.get("name", "")).lower(),
        }
        for key in key_candidates:
            if key:
                agents_map[key] = snapshot
    return agents_map


def _state_for_agent(traces: Dict[str, Any], agent_id: str) -> Tuple[str, Optional[str], Dict[str, Any]]:
    trace = traces.get(agent_id.lower(), {}) if traces else {}
    state = str(trace.get("state") or trace.get("status") or "idle")
    score_val = trace.get("score")
    score = f"{float(score_val):.3f}" if isinstance(score_val, (int, float)) else None
    return state, score, trace


def _skills_tools_markup(agent: Dict[str, Any], trace: Dict[str, Any]) -> str:
    skills = agent.get("skills") or []
    tools = agent.get("tools") or []
    if isinstance(trace, dict):
        skills = skills or trace.get("skills") or []
        tools = tools or trace.get("tools") or []

    skill_text = " • ".join(str(item) for item in skills) if skills else "—"
    tool_text = " • ".join(str(item) for item in tools) if tools else "—"
    return f"<div><b>Skills:</b> {skill_text}</div><div><b>Tools:</b> {tool_text}</div>"


def render_flow_view(
    summary: Optional[RunSummary],
    mcp_context: Optional[Dict[str, Any]],
) -> None:
    agents = load_agents_manifest()
    if not agents:
        st.info("No agents defined in agents_manifest.yaml.")
        return

    _inject_css()

    traces = _extract_trace(summary)
    profile = (summary.raw.get("config") if summary and isinstance(summary.raw, dict) else {}) or {}
    metrics = summary.metrics if summary else {}

    orch_trace = traces.get("orchestrator") or traces.get("logos") or {}
    orch_state = str(orch_trace.get("state") or orch_trace.get("status") or "idle")

    x_positions = [220, 500, 780, 340, 660]
    y_positions = [100, 100, 100, 190, 190]

    non_orch_agents = [agent for agent in agents if agent.get("id") != "orchestrator"]
    paths_html: List[str] = []
    cards_html: List[str] = []

    for idx, agent in enumerate(non_orch_agents):
        state, score, trace = _state_for_agent(traces, agent["id"])
        x = x_positions[idx % len(x_positions)]
        y = y_positions[idx % len(y_positions)]
        paths_html.append(_mk_path(500, 20, x, y, state))

        skills_tools = _skills_tools_markup(agent, trace)
        chat_placeholder = "<button disabled style='opacity:0.6'>Open chat below</button>"
        cards_html.append(
            _agent_card(
                accent=agent.get("accent_color", "#6C5CE7"),
                name=f"{agent['name']} - {agent['role']}",
                state=state,
                score=score,
                desc=agent.get("personality", "—"),
                skills_tools=skills_tools,
                chat_btn=chat_placeholder,
            )
        )

    html = _flow_template(
        orch_state=orch_state,
        orch_tip="Routes inputs, enforces thresholds, aggregates results.",
        paths="\n".join(paths_html),
        agent_cards="\n".join(cards_html),
    )
    st.components.v1.html(html, height=560, scrolling=False)

    st.markdown("#### Input")
    if "flow_last_input" not in st.session_state:
        st.session_state["flow_last_input"] = ""
    st.session_state["flow_last_input"] = st.text_input(
        "Describe the task or paste a repo URL",
        placeholder="Scan this repo and summarize risks…",
        value=st.session_state.get("flow_last_input") or "",
    )

    profile_name = profile.get("name") or profile.get("profile") or "default"
    model_name = profile.get("model") or profile.get("provider_model") or "n/a"
    st.caption(f"Active profile: `{profile_name}` • Model: `{model_name}`")

    st.markdown("#### Orchestrator")
    verdict = synthesize_verdict(summary, mcp_context)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Dispatch to Agents"):
            st.success("Dispatched. Watch the flow animate as traces update.")
    with col2:
        if st.button("Ask Orchestrator about current state"):
            orchestrator = next((a for a in agents if a.get("id") == "orchestrator"), None)
            seed = orchestrator.get("seed_prompt", "") if orchestrator else ""
            tldr = verdict.get("decision", "unknown").upper()
            ctx = {
                "profile": profile,
                "metrics": metrics,
                "traces": traces,
                "input": st.session_state.get("flow_last_input", ""),
                "mcp_results": (mcp_context or {}),
                "verdict": verdict,
            }
            narration = explain(
                agent_name=orchestrator.get("name", "Orchestrator") if orchestrator else "Orchestrator",
                context_json=ctx,
                question="Summarize current progress and recommended next actions.",
                system_seed=seed,
            )
            st.info(f"**TL;DR:** {tldr} — see details below.\n\n{narration}")

    decision_color = {"pass": "green", "warn": "orange", "fail": "red"}.get(
        verdict["decision"], "gray"
    )
    st.markdown("#### Orchestrator Verdict")
    composite_value = verdict.get("composite")
    composite_text = composite_value if composite_value is not None else "—"
    st.markdown(
        f"**Decision:** <span style='color:{decision_color}'>{verdict['decision'].upper()}</span> "
        f"(composite score: {composite_text})",
        unsafe_allow_html=True,
    )
    st.caption(f"Confidence: {verdict.get('confidence', 'unknown')}")
    with st.expander("Top drivers", expanded=True):
        for driver in verdict.get("drivers", []):
            st.markdown(f"- {driver}")
    with st.expander("Recommended actions", expanded=True):
        for action in verdict.get("actions", []):
            st.markdown(f"- {action}")

    action_cols = st.columns(3)
    with action_cols[0]:
        if st.button("Generate Report"):
            st.session_state["last_report"] = {
                "verdict": verdict,
                "metrics": metrics,
                "profile": profile,
                "input": st.session_state.get("flow_last_input", ""),
            }
            st.success("Report snapshot stored in session (see Reports tab).")

    with action_cols[1]:
        if st.button("Cleanup Workspace"):
            try:
                client = MCPClient()
                response = client.call_tool("cleanup_workspace") or {}
                st.session_state["last_cleanup"] = response
                st.success("Workspace cleanup request sent.")
            except Exception as exc:  # pragma: no cover - network errors
                st.error(f"Cleanup failed: {exc}")

    with action_cols[2]:
        if st.button("Promote to Baseline"):
            note = f"{profile_name} | composite={composite_text}"
            try:
                subprocess.run(
                    [sys.executable, "scripts/make_baseline.py", "--note", note],
                    check=False,
                )
                st.success("Baseline snapshot command executed.")
            except Exception as exc:  # pragma: no cover - subprocess issues
                st.error(f"Baseline snapshot failed: {exc}")

    st.markdown("---")
    st.markdown("#### Agent Chats")
    findings: List[Any] = []
    mcp_results = (mcp_context or {}).get("results") or {}
    if isinstance(mcp_results, dict):
        for payload in mcp_results.values():
            if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
                findings.extend(payload["findings"])

    for agent in non_orch_agents:
        with st.expander(f"💬 Ask {agent['name']}"):
            question_key = f"flow_question_{agent['id']}"
            question = st.text_input(
                "Question",
                key=question_key,
                placeholder="What does your score mean and how do I improve it?",
            )
            state, _, trace = _state_for_agent(traces, agent["id"])
            disabled = state.lower() not in {"complete", "done", "finished"}
            if st.button("Ask", key=f"flow_ask_{agent['id']}", disabled=disabled):
                ctx = {
                    "profile": profile,
                    "metrics": metrics,
                    "trace": trace,
                    "input": st.session_state.get("flow_last_input", ""),
                    "findings": findings,
                }
                answer = explain(
                    agent_name=agent["name"],
                    context_json=ctx,
                    question=question,
                    system_seed=agent.get("seed_prompt", ""),
                )
                st.write(answer)
            elif disabled:
                st.caption("Chat activates once this agent completes.")
