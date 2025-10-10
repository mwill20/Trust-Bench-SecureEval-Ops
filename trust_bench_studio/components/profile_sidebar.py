"""Sidebar controls for selecting and inspecting evaluation profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

import streamlit as st


def render_profile_sidebar(
    profiles: List[Path],
    selected_profile: Optional[Path],
    on_run: Callable[[Path], None],
) -> Optional[Path]:
    """Render the sidebar with profile selection and actions.

    Args:
        profiles: Available profile files.
        selected_profile: Current selection.
        on_run: Callback invoked when the user requests an evaluation run.

    Returns:
        The profile chosen by the user (maybe updated).
    """
    st.sidebar.header("Profiles")

    if not profiles:
        st.sidebar.warning("No profiles found in `profiles/`.")
        return None

    profile_labels = [profile.name for profile in profiles]
    default_index = profile_labels.index(selected_profile.name) if selected_profile else 0
    index = st.sidebar.selectbox(
        "Active profile",
        options=list(range(len(profiles))),
        format_func=lambda i: profile_labels[i],
        index=default_index,
    )
    active_profile = profiles[index]

    with active_profile.open("r", encoding="utf-8") as handle:
        profile_content = handle.read()

    with st.sidebar.expander("Thresholds", expanded=False):
        try:
            doc = json.loads(profile_content) if active_profile.suffix == ".json" else None
        except json.JSONDecodeError:
            doc = None

        if doc:
            thresholds: Dict[str, float] = doc.get("thresholds", {})
            for key, value in thresholds.items():
                st.write(f"**{key}**: {value}")
        else:
            st.code(profile_content, language=active_profile.suffix.lstrip("."))

    if st.sidebar.button("Run Evaluation", use_container_width=True):
        on_run(active_profile)

    return active_profile
