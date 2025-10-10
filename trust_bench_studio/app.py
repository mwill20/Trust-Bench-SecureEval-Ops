"""Streamlit application entry point for Trust_Bench Studio."""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import streamlit as st

# Ensure the project root is on sys.path when the app is launched directly (for example via Streamlit).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from trust_bench_studio.components import (
    render_agents_view,
    render_flow_view,
    render_layout,
    render_mcp_panel,
    render_profile_sidebar,
    render_run_panels,
)
from trust_bench_studio.utils import (
    MCPClient,
    RunRecord,
    RunSummary,
    list_profiles,
    list_runs,
    load_run_summary,
    trigger_evaluation,
)

REFRESHABLE_VIEWS = {"Dashboard", "Agents", "Flow"}


def _initialize_session_defaults() -> None:
    st.session_state.setdefault("studio_profile", "")
    st.session_state.setdefault("studio_run_index", 0)
    st.session_state.setdefault("studio_live_refresh", False)
    st.session_state.setdefault("studio_refresh_interval", 3)
    st.session_state.setdefault("studio_active_view", "Dashboard")
    st.session_state.setdefault("studio_last_refresh_ts", time.time())


def _get_selected_profile() -> Optional[Path]:
    value = st.session_state.get("studio_profile")
    return Path(value) if value else None


def _set_selected_profile(profile: Optional[Path]) -> None:
    st.session_state["studio_profile"] = str(profile) if profile else ""


def _handle_run(profile_path: Path) -> None:
    process = trigger_evaluation(profile_path)
    if process:
        st.sidebar.success(
            f"Started evaluation with PID {process.pid} for `{profile_path.name}`."
        )
    else:
        st.sidebar.info(
            "Evaluation script not available; integrate CLI runner to enable live runs."
        )


def _summaries_for_runs(runs: Iterable[RunRecord]) -> List[Optional[RunSummary]]:
    return [load_run_summary(record.path) for record in runs]


def _pick_active_index(run_labels: Sequence[str]) -> int:
    active_index = st.session_state.get("studio_run_index", 0)
    if not run_labels:
        return 0
    if active_index >= len(run_labels):
        active_index = 0
    return active_index


def _select_view() -> str:
    options = ["Dashboard", "Agents", "Flow", "Reports & MCP"]
    current = st.session_state.get("studio_active_view", options[0])
    try:
        index = options.index(current)
    except ValueError:
        index = 0
    selection = st.radio(
        "Studio view",
        options=options,
        index=index,
        horizontal=True,
        key="studio_view_switch",
    )
    st.session_state["studio_active_view"] = selection
    return selection


def _render_live_controls(refresh_enabled: bool) -> None:
    with st.sidebar.expander("Live Updates", expanded=False):
        interval = st.slider(
            "Refresh interval (seconds)",
            min_value=1,
            max_value=30,
            step=1,
            value=int(st.session_state.get("studio_refresh_interval", 3)),
            key="studio_refresh_interval_slider",
        )
        st.session_state["studio_refresh_interval"] = interval

        auto_refresh = st.toggle(
            "Enable auto-refresh",
            value=bool(st.session_state.get("studio_live_refresh", False)),
            key="studio_live_refresh_toggle",
            disabled=not refresh_enabled,
        )
        if not refresh_enabled:
            auto_refresh = False
        st.session_state["studio_live_refresh"] = auto_refresh

        if st.button("Refresh now", use_container_width=True):
            st.session_state["studio_manual_refresh_ts"] = time.time()
            st.experimental_rerun()

        last_refresh_ts = st.session_state.get("studio_last_refresh_ts")
        if last_refresh_ts:
            timestamp = datetime.fromtimestamp(last_refresh_ts).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            st.caption(f"Last refresh: {timestamp}")


def _schedule_refresh_loop(should_refresh: bool) -> None:
    if not should_refresh:
        return

    interval = float(st.session_state.get("studio_refresh_interval", 3))
    interval = max(0.75, interval)
    time.sleep(interval)
    st.experimental_rerun()


def main() -> None:
    """Launch the Trust_Bench Studio UI."""
    _initialize_session_defaults()
    render_layout()

    profiles = list_profiles()
    selected_profile = _get_selected_profile()
    selected_profile = render_profile_sidebar(
        profiles=profiles,
        selected_profile=selected_profile,
        on_run=_handle_run,
    )
    _set_selected_profile(selected_profile)

    runs = list_runs()
    summaries = _summaries_for_runs(runs)

    run_labels = [record.name for record in runs]
    active_index = _pick_active_index(run_labels)

    view = _select_view()
    refresh_enabled = bool(run_labels) and view in REFRESHABLE_VIEWS
    _render_live_controls(refresh_enabled=refresh_enabled)

    if view == "Dashboard":
        if not run_labels:
            st.info("No evaluation runs found. Create one to populate the dashboard.")
        else:
            selected_label = st.selectbox(
                "Active run",
                options=run_labels,
                index=active_index,
                key="studio_run_selectbox",
            )
            active_index = run_labels.index(selected_label)
            st.session_state["studio_run_index"] = active_index

            render_run_panels(
                run_names=run_labels,
                active_index=active_index,
                summaries=summaries,
            )

            st.caption(f"Run directory: `{runs[active_index].path}`")

    if view == "Agents":
        active_summary = summaries[active_index] if run_labels and summaries else None
        mcp_state = st.session_state.get("mcp_ui_state", {})
        mcp_results = {}
        if isinstance(mcp_state, dict):
            mcp_results = mcp_state.get("results", {}) or {}
        render_agents_view(
            summary=active_summary,
            mcp_context={"results": mcp_results} if mcp_results else {},
        )

    if view == "Flow":
        active_summary = summaries[active_index] if run_labels and summaries else None
        mcp_state = st.session_state.get("mcp_ui_state", {})
        mcp_results = {}
        if isinstance(mcp_state, dict):
            mcp_results = mcp_state.get("results", {}) or {}
        render_flow_view(
            summary=active_summary,
            mcp_context={"results": mcp_results} if mcp_results else {},
        )

    if view == "Reports & MCP":
        client = MCPClient()
        render_mcp_panel(client)

    st.session_state["studio_last_refresh_ts"] = time.time()
    _schedule_refresh_loop(
        should_refresh=bool(
            run_labels
            and st.session_state.get("studio_live_refresh")
            and view in REFRESHABLE_VIEWS
        )
    )


if __name__ == "__main__":
    main()
