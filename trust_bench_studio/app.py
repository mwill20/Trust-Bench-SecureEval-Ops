"""Streamlit helper to guide developers through the new React-based Studio UI."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "trust_bench_studio" / "frontend"
BUILD_DIR = FRONTEND_DIR / "dist"


def _render_build_preview() -> None:
    index_file = BUILD_DIR / "index.html"
    if not index_file.exists():
        st.warning(
            "A production build has not been generated yet. Run `npm run build` inside "
            "`trust_bench_studio/frontend/` and refresh this page to preview the bundled UI."
        )
        return

    html = index_file.read_text(encoding="utf-8")
    st.components.v1.html(html, height=900, scrolling=True)


def main() -> None:
    st.set_page_config(page_title="Trust_Bench Studio", layout="wide")
    st.title("Trust_Bench Studio – React Command Center")

    st.markdown(
        """
        The Streamlit interface has been replaced by a React + FastAPI command center.
        Use the instructions below to run the new stack locally.
        """
    )

    st.subheader("Run locally")
    st.markdown(
        """
        1. Start the backend:
           ```bash
           uvicorn trust_bench_studio.api.server:app --reload
           ```
        2. Launch the frontend:
           ```bash
           cd trust_bench_studio/frontend
           npm install
           npm run dev
           ```
        3. Open your browser at http://127.0.0.1:5173 to access the Studio command center.
        """
    )

    st.info(
        "This Streamlit page remains for backwards compatibility. "
        "You can also preview a production build (if generated) below."
    )

    with st.expander("Preview production build (requires `npm run build`)", expanded=False):
        _render_build_preview()


if __name__ == "__main__":
    main()

