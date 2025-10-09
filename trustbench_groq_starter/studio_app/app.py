import streamlit as st
import subprocess, sys
from pathlib import Path

st.set_page_config(page_title="TrustBench Studio", page_icon="🛡️", layout="wide")
st.title("TrustBench Studio (Groq)")

profile = st.text_input("Profile path", "profiles/default.yaml")
repo = st.text_input("Repository URL or local path (optional)", "")

col1, col2 = st.columns(2)
with col1:
    if st.button("Run Evaluation"):
        cmd = [sys.executable, "-m", "trustbench_core.orchestrator", "--profile", profile]
        if repo.strip():
            cmd += ["--repo", repo.strip()]
        with st.status("Running...", expanded=True) as status:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            lines = []
            for line in proc.stdout:
                lines.append(line.rstrip())
                st.write(line.rstrip())
            proc.wait()
            status.update(label="Finished", state="complete")
        st.session_state["last_log"] = "\n".join(lines)

with col2:
    st.subheader("Last Report")
    runs = sorted(Path("runs").glob("*"))
    if runs:
        last = runs[-1]
        st.caption(f"Run: {last.name}")
        rep = last / "report.html"
        if rep.exists():
            st.markdown(f"[Open report]({rep.resolve().as_uri()})")
        else:
            st.write("No report yet.")
    else:
        st.write("No runs found.")

st.divider()
st.code(st.session_state.get("last_log", ""), language="bash")
