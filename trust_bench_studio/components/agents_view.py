"""Render agent cards driven by the manifest and live run context."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import streamlit as st

from trust_bench_studio.utils import (
    PROJECT_ROOT,
    RunSummary,
    load_agents_manifest,
)
from trust_bench_studio.utils.llm import explain


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _resolve_image_path(image_ref: str) -> Optional[Path]:
    if not image_ref:
        return None
    ref_path = Path(image_ref)
    if ref_path.is_absolute():
        return ref_path if ref_path.exists() else None
    candidate = PROJECT_ROOT / "trust_bench_studio" / ref_path
    return candidate if candidate.exists() else None


def _color_bar(hex_color: str, height: int = 6) -> None:
    color = hex_color or "#6C5CE7"
    st.markdown(
        f"""<div style="height:{height}px;background:{color};border-radius:8px;margin-bottom:8px;"></div>""",
        unsafe_allow_html=True,
    )


def _agent_header(agent: Dict[str, Any]) -> None:
    col_img, col_title = st.columns([1, 5])
    with col_img:
        image_path = _resolve_image_path(agent.get("image", ""))
        if image_path:
            st.image(str(image_path), use_column_width=True)
        else:
            st.markdown("🧩")
    with col_title:
        st.markdown(f"### {agent['name']} — {agent['role']}")
        if agent.get("personality"):
            st.caption(agent["personality"])


def _status_and_score(
    trace: Optional[Dict[str, Any]], accent_color: str
) -> Tuple[str, Optional[float]]:
    default_status = "idle"
    status = (
        (trace or {}).get("status")
        or (trace or {}).get("state")
        or default_status
    )

    score = None
    for key in ("score", "confidence", "value"):
        if isinstance((trace or {}).get(key), (int, float)):
            score = float(trace[key])
            break

    cols = st.columns(2)
    with cols[0]:
        badge = (
            f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;'
            f'background:{accent_color or "#6C5CE7"};color:#fff;font-size:0.8rem;">'
            f"{status.capitalize()}</span>"
        )
        st.markdown(badge, unsafe_allow_html=True)
    with cols[1]:
        if score is not None:
            st.write(f"**Score:** {score:.3f}")
        else:
            st.write("**Score:** —")

    if score is not None and 0.0 <= score <= 1.0:
        st.progress(score)

    return status, score


def _render_skills_and_tools(agent: Dict[str, Any], trace: Optional[Dict[str, Any]]) -> None:
    items: Dict[str, Iterable[str]] = {}
    if agent.get("skills"):
        items["Skills"] = agent["skills"]
    if agent.get("tools"):
        items["Tools"] = agent["tools"]
    if trace:
        if isinstance(trace.get("skills"), Iterable):
            items.setdefault("Skills", [])
            items["Skills"] = list(dict.fromkeys(list(items["Skills"]) + list(trace["skills"])))
        if isinstance(trace.get("tools"), Iterable):
            items.setdefault("Tools", [])
            items["Tools"] = list(dict.fromkeys(list(items["Tools"]) + list(trace["tools"])))

    for label, values in items.items():
        values_list = list(values)
        if not values_list:
            continue
        st.markdown(f"**{label}**")
        for value in values_list:
            st.write(f"- {value}")


def _render_transcript(trace: Optional[Dict[str, Any]]) -> None:
    transcript = None
    if trace:
        for key in ("transcript", "summary", "message", "output"):
            if trace.get(key):
                transcript = trace[key]
                break
    if transcript:
        with st.expander("🧠 Transcript"):
            st.code(str(transcript), language="markdown")


def _agent_chat(
    agent: Dict[str, Any],
    status: str,
    score: Optional[float],
    shared_ctx: Dict[str, Any],
    trace: Optional[Dict[str, Any]],
) -> None:
    agent_id = agent["id"]
    seed_prompt = agent.get("seed_prompt", "")
    expander_label = f"💬 Ask {agent['name']}"
    with st.expander(expander_label):
        question_key = f"studio_chat_question_{agent_id}"
        submit_key = f"studio_chat_submit_{agent_id}"
        history_key = f"studio_chat_history_{agent_id}"

        st.session_state.setdefault(history_key, [])

        question = st.text_input(
            "Question",
            placeholder="Explain this score in plain language and how to improve it…",
            key=question_key,
        )
        if st.button("Ask", key=submit_key, disabled=not question.strip()):
            context_payload = {
                "agent": {
                    "id": agent_id,
                    "name": agent["name"],
                    "role": agent["role"],
                    "status": status,
                    "score": score,
                    "trace": trace or {},
                },
                **shared_ctx,
            }
            answer = explain(
                agent_name=agent["name"],
                context_json=context_payload,
                question=question,
                system_seed=seed_prompt,
            )
            st.session_state[history_key].append(
                {"question": question, "answer": answer}
            )

        history = st.session_state.get(history_key, [])
        if history:
            last = history[-1]
            st.caption(f"You asked: {last['question']}")
            st.write(last["answer"])
        else:
            st.caption("Ask the agent about metrics, risks, or mitigations.")


def _build_trace_index(summary: Optional[RunSummary]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    if not summary:
        return index

    for snapshot in summary.agents:
        if not isinstance(snapshot, dict):
            continue
        keys = set()
        for key in ("id", "agent", "agent_id", "name", "agent_name"):
            value = snapshot.get(key)
            if value:
                keys.add(str(value).lower())
        if snapshot.get("name"):
            keys.add(_slugify(str(snapshot["name"])))
        for key in keys:
            index.setdefault(key, snapshot)

    return index


def render_agents_view(
    summary: Optional[RunSummary],
    mcp_context: Optional[Dict[str, Any]] = None,
) -> None:
    """Render data-driven agent cards for the current run."""
    agents: List[Dict[str, Any]] = load_agents_manifest()
    if not agents:
        st.info("No agents defined in agents_manifest.yaml.")
        return

    trace_index = _build_trace_index(summary)
    metrics = summary.metrics if summary else {}
    profile = (summary.raw.get("config") if summary and isinstance(summary.raw, dict) else {}) or {}

    mcp_results = (mcp_context or {}).get("results", mcp_context or {})
    combined_findings: List[Any] = []
    if isinstance(mcp_results, dict):
        for payload in mcp_results.values():
            if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
                combined_findings.extend(payload["findings"])

    shared_ctx: Dict[str, Any] = {
        "metrics": metrics,
        "profile": profile,
        "mcp_results": mcp_results,
        "findings": combined_findings,
    }

    st.subheader("Agents")
    grid = st.columns(2) if len(agents) > 1 else [st]

    for index, agent in enumerate(agents):
        slug_keys = {agent["id"].lower(), _slugify(agent["name"])}
        agent_trace = None
        for key in slug_keys:
            if key in trace_index:
                agent_trace = trace_index[key]
                break

        card = grid[index % len(grid)].container(border=True)
        with card:
            accent = agent.get("accent_color", "#6C5CE7")
            _color_bar(accent)
            _agent_header(agent)
            status, score = _status_and_score(agent_trace, accent)
            _render_skills_and_tools(agent, agent_trace)
            _render_transcript(agent_trace)
            _agent_chat(agent, status, score, shared_ctx, agent_trace or {})
