"""Render MCP client actions and cached results inside Streamlit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from trust_bench_studio.utils import MCPClient, default_workspace_path


@dataclass(frozen=True)
class MCPAction:
    name: str
    label: str
    kwargs: Dict[str, Any]


TOOLBAR: List[MCPAction] = [
    MCPAction(
        name="scan_repo_for_secrets",
        label="Scan Repo for Secrets",
        kwargs={"path": str(default_workspace_path())},
    ),
    MCPAction(
        name="env_content",
        label="Environment Audit",
        kwargs={"max_bytes": 2_000_000},
    ),
    MCPAction(
        name="cleanup_workspace",
        label="Cleanup Workspace",
        kwargs={},
    ),
]


def _get_state() -> Dict[str, Any]:
    return st.session_state.setdefault(
        "mcp_ui_state",
        {"log": [], "results": {}, "running": set()},
    )


def _append_log(state: Dict[str, Any], message: str) -> None:
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    state["log"].append(f"[{timestamp}] {message}")
    state["log"] = state["log"][-12:]


def _status_pill(status: str) -> str:
    normalized = status.lower()
    if normalized in {"success", "ok", "complete"}:
        return "✅ Success"
    if normalized in {"warning", "warn"}:
        return "⚠️ Warning"
    if normalized in {"error", "failed", "failure"}:
        return "❌ Failure"
    return f"ℹ️ {status.title()}"


def _count_findings(payload: Dict[str, Any]) -> int:
    findings = payload.get("findings")
    if isinstance(findings, list):
        return len(findings)
    return 0


def _render_log_panel(state: Dict[str, Any]) -> None:
    st.write("#### Activity Log")
    if not state["log"]:
        st.caption("No MCP actions executed yet.")
        return
    st.markdown("\n".join(f"- {entry}" for entry in state["log"]))


def _render_results_panel(state: Dict[str, Any]) -> None:
    st.write("#### Recent Results")
    if not state["results"]:
        st.caption("Run a tool to see structured output here.")
        return

    for label, payload in state["results"].items():
        findings = _count_findings(payload)
        status = payload.get("status") or ("success" if findings == 0 else "warning")
        st.markdown(f"**{label}** — {_status_pill(status)} · Findings: {findings}")
        with st.expander("View raw output", expanded=False):
            st.json(payload)


def render_mcp_panel(client: MCPClient) -> None:
    """Display MCP actions alongside cached reports."""
    state = _get_state()
    st.subheader("MCP Workspace Tools")

    cols = st.columns(len(TOOLBAR))
    for column, action in zip(cols, TOOLBAR):
        running_key = f"{action.name}_running"
        is_running = running_key in state["running"]
        if column.button(action.label, key=f"btn_{action.name}", disabled=is_running):
            state["running"].add(running_key)
            _append_log(state, f"▶ {action.label} started")
            try:
                response = client.call_tool(action.name, **action.kwargs)
                if response is None:
                    _append_log(state, f"❌ {action.label} failed (no response).")
                else:
                    state["results"][action.label] = response
                    _append_log(
                        state,
                        f"✅ {action.label} complete — findings: {_count_findings(response)}",
                    )
            finally:
                state["running"].discard(running_key)

    _render_log_panel(state)
    _render_results_panel(state)

    st.write("#### Cached Reports")
    reports = client.list_reports()
    if not reports:
        st.caption("No cached MCP reports available from the server.")
        return

    for report in reports:
        with st.expander(report.name, expanded=False):
            st.json(report.payload)
