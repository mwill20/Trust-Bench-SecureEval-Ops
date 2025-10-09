#!/usr/bin/env python
"""Environment doctor for TrustBench Phase 1."""
from __future__ import annotations

import json
import os
import shutil
import sys
from importlib import import_module
from pathlib import Path
from typing import Dict, List

ENV_VARS = [
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "MCP_SERVER_URL",
    "MCP_API_KEY",
    "TRUSTBENCH_FAKE_PROVIDER",
]

SEMANTIC_TOOLS = {
    "semgrep": ["semgrep", "--version"],
}


def check_env() -> Dict[str, str]:
    findings = {}
    for var in ENV_VARS:
        value = os.getenv(var)
        if value:
            findings[var] = "<set>" if "KEY" in var else value
        else:
            findings[var] = "<missing>"
    return findings


def ensure_packages() -> Dict[str, bool]:
    packages = ["groq", "ragas"]
    results = {}
    for pkg in packages:
        try:
            import_module(pkg)
            results[pkg] = True
        except Exception:
            results[pkg] = False
    return results


def ensure_binaries() -> Dict[str, bool]:
    results = {}
    for name, command in SEMANTIC_TOOLS.items():
        exe = shutil.which(command[0])
        results[name] = bool(exe)
    return results


def ensure_files() -> Dict[str, bool]:
    required = [
        Path("profiles/default.yaml"),
        Path("profiles/highstakes.yaml"),
        Path("datasets/golden/example.jsonl"),
    ]
    return {str(path): path.exists() for path in required}


def main() -> None:
    env = check_env()
    pkgs = ensure_packages()
    bins = ensure_binaries()
    files = ensure_files()

    issues: List[str] = []

    if env["GROQ_API_KEY"] == "<missing>" and os.getenv("TRUSTBENCH_FAKE_PROVIDER") != "1":
        issues.append("GROQ_API_KEY not set and fake provider disabled. Export GROQ_API_KEY or set TRUSTBENCH_FAKE_PROVIDER=1.")
    if env["GROQ_MODEL"] == "<missing>":
        issues.append("GROQ_MODEL not set (defaults to llama-3.1-70b-versatile).")
    if not pkgs.get("groq"):
        issues.append("groq package missing. Install via `pip install groq`.")
    if not pkgs.get("ragas"):
        issues.append("ragas package missing. Install via `pip install ragas`.")
    if not bins.get("semgrep"):
        issues.append("Semgrep binary not found in PATH. Install via `pip install semgrep` or system package.")
    missing_files = [path for path, ok in files.items() if not ok]
    if missing_files:
        issues.append(f"Missing dataset/profile files: {', '.join(missing_files)}")

    report = {
        "environment": env,
        "packages": pkgs,
        "binaries": bins,
        "files": files,
        "fake_provider": os.getenv("TRUSTBENCH_FAKE_PROVIDER") == "1",
    }
    print(json.dumps(report, indent=2))

    if issues:
        print("\nEnvironment doctor found issues:\n- " + "\n- ".join(issues), file=sys.stderr)
        sys.exit(1)
    print("\nEnvironment looks good!")


if __name__ == "__main__":
    main()

