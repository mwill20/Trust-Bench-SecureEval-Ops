"""Flow-oriented visualization of orchestrator and agents."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import streamlit as st

from trust_bench_studio.utils import load_agents_manifest, synthesize_verdict
from trust_bench_studio.utils.llm import explain
from trust_bench_studio.utils.run_store import RunSummary

SVG_TEMPLATE = (
    "<style>"
    ".flow-wrap{{display:flex;flex-direction:column;gap:18px;margin-top:8px}}"
    ".row{{display:flex;align-items:center;justify-content:center;gap:18px}}"
    ".card{{background:#15171b;border:1px solid #2a2d34;border-radius:12px;padding:12px;min-width:240px;max-width:640px;box-shadow:0 2px 8px rgba(0,0,0,0.25)}}"
    ".small{{min-width:164px;max-width:210px;text-align:left}}"
    ".title{{font-weight:600;font-size:15px;margin-bottom:4px}}"
    ".node{{position:relative;text-align:left}}"
    ".link{{stroke:#4a4f60;stroke-width:2;fill:none;opacity:0.85}}"
    ".link.complete{{stroke:#58d68d;stroke-dasharray:none;animation:none}}"
    ".link.active{{stroke:#9aa7ff}}"
    ".dash{{stroke-dasharray:6 6;animation:dash 1.8s linear infinite}}"
    "@keyframes dash {{to{{stroke-dashoffset:-120;}}}}"
    ".badge{{font-size:12px;opacity:0.85;margin-top:4px}}"
    ".dropdown{{font-size:13px;opacity:0.9;text-align:left}}"
    ".dropdown summary{{cursor:pointer;color:#9aa7ff}}"
    ".dropdown div{{margin-top:6px}}"
    "</style>"
    "<div class='flow-wrap'>"
    "  <div class='row'>"
    "    <div class='card' style='text-align:left'>"
    "      <div class='title'>User Input</div>"
    "      <div id='user-box'></div>"
    "    </div>"
    "  </div>"
    "  <div class='row'>"
    "    <div class='card node' id='orchestrator'>"
    "      <div class='title'>Logos - Orchestrator</div>"
    "      <div class='badge'>State: {orch_state}</div>"
    "      <div style='font-size:13px;opacity:0.85'>{orch_tip}</div>"
    "    </div>"
    "  </div>"
    "  <div class='row' style='position:relative;height:140px;'>"
    "    <svg width='1000' height='120' viewBox='0 0 1000 120'>"
    "      {paths}"
    "    </svg>"
    "  </div>"
    "  <div class='row' id='agent-row' style='flex-wrap:wrap'>"
    "    {agent_cards}"
    "  </div>"
    "</div>"
)

CARD_TEMPLATE = (
    "<div class='card small' style='border-top:4px solid {accent}'>"
    "  <div class='title'>{name}</div>"
    "  <div class='badge'>State: {state} • Score: {score}</div>"
    "  <details class='dropdown'><summary>About</summary>"
    "    <div>{desc}</div>"
    "  </details>"
    "  <details class='dropdown'><summary>Skills &amp; Tools</summary>"
    "    <div>{skills_tools}</div>"
    "  </details>"
    "  <div style='margin-top:8px'>{chat_btn}</div>"
    "</div>"
)


def _mk_path(x1: float, y1: float, x2: float, y2: float, state: str) -> str:
    state_lower = state.lower()
    if state_lower == "complete":
        klass = "link complete"
    elif state_lower in {"active", "running", "processing"}:
        klass = "link dash active"
    else:
        klass = "link dash"
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


def _state_for_agent(traces: Dict[str, Any], agent_id: str) -> tuple[str, str, Dict[str, Any]]:
    trace = traces.get(agent_id.lower(), {}) if traces else {}
    state = str(trace.get("state") or trace.get("status") or "idle")
    score_val = trace.get("score")
    score = f"{float(score_val):.3f}" if isinstance(score_val, (int, float)) else "—"
    return state, score, trace


def render_flow_view(
    summary: Optional[RunSummary],
    mcp_context: Optional[Dict[str, Any]],
) -> None:
    agents = load_agents_manifest()
    if not agents:
        st.info("No agents defined in agents_manifest.yaml.")
        return

    traces = _extract_trace(summary)
    profile = (summary.raw.get("config") if summary and isinstance(summary.raw, dict) else {}) or {}
    metrics = summary.metrics if summary else {}

    orch_trace = traces.get("orchestrator") or traces.get("logos") or {}
    orch_state = str(orch_trace.get("state") or orch_trace.get("status") or "idle")

    x_positions = [220, 500, 780, 340, 660]
    y_base = [100, 100, 100, 190, 190]

    non_orch_agents = [agent for agent in agents if agent.get("id") != "orchestrator"]
    paths_html: List[str] = []
    cards_html: List[str] = []

    for idx, agent in enumerate(non_orch_agents):
        state, score, trace = _state_for_agent(traces, agent["id"])

        x = x_positions[idx % len(x_positions)]
        y = y_base[idx % len(y_base)]
        paths_html.append(_mk_path(500, 20, x, y, state))

        skills = " • ".join(agent.get("skills", [])) if agent.get("skills") else "—"
        tools = " • ".join(agent.get("tools", [])) if agent.get("tools") else "—"
        skills_tools = f"<div><b>Skills:</b> {skills}</div><div><b>Tools:</b> {tools}</div>"

        chat_placeholder = "<button disabled style='opacity:0.6'>Open chat below</button>"

        cards_html.append(
            CARD_TEMPLATE.format(
                name=f"{agent['name']} - {agent['role']}",
                state=state,
                score=score,
                desc=agent.get("personality", "—"),
                skills_tools=skills_tools,
                chat_btn=chat_placeholder,
                accent=agent.get("accent_color", "#6C5CE7"),
            )
        )

    html = SVG_TEMPLATE.format(
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
            ctx = {
                "profile": profile,
                "metrics": metrics,
                "traces": traces,
                "input": st.session_state.get("flow_last_input", ""),
                "mcp_results": (mcp_context or {}),
                "verdict": verdict,
            }
            answer = explain(
                agent_name=orchestrator.get("name", "Orchestrator") if orchestrator else "Orchestrator",
                context_json=ctx,
                question="Summarize current progress and recommended next actions.",
                system_seed=seed,
            )
            st.info(answer)

    decision_color = {"pass": "green", "warn": "orange", "fail": "red"}.get(
        verdict["decision"], "gray"
    )
    st.markdown("#### Orchestrator Verdict")
    verdict_container = st.container()
    with verdict_container:
        composite_display = verdict.get("composite")
        composite_text = composite_display if composite_display is not None else "—"
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
        if st.button("Promote this run to baseline", key="flow_promote_baseline"):
            st.info("Use `python scripts/make_baseline.py --note ...` to capture the current run.")

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
            state, _, _ = _state_for_agent(traces, agent["id"])
            disabled = state.lower() not in {"complete", "done", "finished"}
            if st.button("Ask", key=f"flow_ask_{agent['id']}", disabled=disabled):
                trace = traces.get(agent["id"].lower(), {})
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
