#!/usr/bin/env python3
"""
Trust_Bench MCP server exposed over stdio for Model Context Protocol clients.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "Missing dependency: install the MCP python SDK via `pip install -U mcp`.\n"
        f"Import error: {exc}"
    )

SERVER_NAME = "Trust_Bench"
WORKDIR = Path(os.environ.get("TRUST_BENCH_WORKDIR", "./trust_bench_data")).resolve()
WORKDIR.mkdir(parents=True, exist_ok=True)

app = FastMCP(SERVER_NAME, version="0.1.0")

SECRET_PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*([A-Za-z0-9/+=]{40})",
    "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "Slack Token": r"xox[baprs]-[0-9A-Za-z-]{10,60}",
    "GitHub Token": r"gh[pousr]_[0-9A-Za-z]{36}",
    "Private RSA Key": r"-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----",
    "Private EC Key": r"-----BEGIN EC PRIVATE KEY-----[\s\S]*?-----END EC PRIVATE KEY-----",
    "JWT": r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
}


def _download_repo_zip(repo_url: str) -> Path:
    target = WORKDIR / "repo"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    normalized = repo_url[:-4] if repo_url.endswith(".git") else repo_url
    for branch in ("main", "master"):
        archive = f"{normalized}/archive/refs/heads/{branch}.zip"
        resp = requests.get(archive, timeout=60)
        if resp.status_code != 200:
            continue
        buffer = io.BytesIO(resp.content)
        with zipfile.ZipFile(buffer) as zf:
            zf.extractall(target)
            top = next((name.split("/")[0] for name in zf.namelist() if "/" in name), None)
        return (target / top) if top else target
    raise RuntimeError("Unable to download repo archive from main/master.")


def _find_small_file(root: Path, name: str, max_mb: float = 5.0) -> Optional[Path]:
    limit = max_mb * 1024 * 1024
    for candidate in root.rglob(name):
        try:
            if candidate.stat().st_size <= limit:
                return candidate
        except OSError:
            continue
    return None


@app.tool()
def download_and_extract_repo(repo_url: str) -> Dict[str, Any]:
    """Download and extract a public GitHub repository."""
    try:
        location = _download_repo_zip(repo_url)
        return {"ok": True, "repo_dir": str(location), "message": f"Extracted to {location}"}
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "repo_dir": "", "message": f"Download failed: {exc}"}


@app.tool()
def env_content(dir_path: str) -> Dict[str, Any]:
    """Return the first `.env` file encountered under `dir_path`."""
    root = Path(dir_path).resolve()
    found = _find_small_file(root, ".env", max_mb=2.0)
    if not found:
        return {"found": False, "path": None, "content": None}
    try:
        text = found.read_text(encoding="utf-8", errors="ignore")
        return {"found": True, "path": str(found), "content": text}
    except Exception as exc:  # pragma: no cover
        return {"found": False, "path": str(found), "content": f"Error reading file: {exc}"}


@app.tool()
def scan_repo_for_secrets(dir_path: str, max_file_mb: float = 1.5) -> Dict[str, Any]:
    """Scan repository files for high-signal secret patterns."""
    root = Path(dir_path).resolve()
    limit = int(max_file_mb * 1024 * 1024)
    matches: List[Dict[str, str]] = []
    scanned = 0

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            if file_path.stat().st_size > limit:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            scanned += 1
            for label, pattern in SECRET_PATTERNS.items():
                match = re.search(pattern, text)
                if match:
                    span = match.span()
                    start = max(span[0] - 40, 0)
                    end = min(span[1] + 40, len(text))
                    snippet = text[start:end].replace("\n", "\\n")
                    matches.append({"file": str(file_path), "pattern": label, "snippet": snippet})
                    break
        except Exception:
            continue

    summary = f"Scanned {scanned} files. Found {len(matches)} potential secret hits."
    return {"files_scanned": scanned, "matches": matches, "summary": summary}


@app.tool()
def cleanup_workspace() -> Dict[str, Any]:
    """Remove the working directory to reset server state."""
    try:
        if WORKDIR.exists():
            shutil.rmtree(WORKDIR)
        WORKDIR.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "message": f"Workspace reset at {WORKDIR}"}
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "message": str(exc)}


if __name__ == "__main__":
    print(f"Starting MCP server '{SERVER_NAME}' (workdir={WORKDIR})...")
    app.run()
