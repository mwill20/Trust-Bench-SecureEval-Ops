\
import json, shutil, subprocess, tempfile, os
from typing import List, Dict

def run_semgrep(paths: List[str]) -> List[Dict]:
    """Run semgrep if installed; return normalized findings list. Safe no‑op if missing."""
    if shutil.which("semgrep") is None:
        return []  # semgrep not available; skip
    with tempfile.TemporaryDirectory() as td:
        cmd = ["semgrep", "--error", "--quiet", "--json"] + paths
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            data = json.loads(out)
        except subprocess.CalledProcessError as e:
            # Treat failures as no findings for MVP
            return []
    findings = []
    for r in data.get("results", []):
        path = r.get("path")
        start = r.get("start", {})
        end = r.get("end", {})
        message = r.get("extra", {}).get("message", "semgrep finding")
        sev = r.get("extra", {}).get("severity", "INFO").upper()
        findings.append({
            "path": path,
            "start": start.get("line"),
            "end": end.get("line"),
            "message": message,
            "severity": sev,
            "tool": "semgrep",
        })
    return findings
