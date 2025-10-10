"""Shared layout helpers for the Trust_Bench Studio UI."""

from __future__ import annotations

import streamlit as st


def render_layout() -> None:
    """Configure page layout and global styles."""
    st.set_page_config(page_title="Trust_Bench Studio", layout="wide")

    st.title("Trust_Bench Studio")
    st.caption(
        "Interactive workspace for exploring evaluation runs, MCP tool outputs, "
        "and profile thresholds."
    )
