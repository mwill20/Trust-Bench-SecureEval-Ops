#!/usr/bin/env python
"""Trust Bench MCP Server

Exposes lightweight repo hygiene tools over MCP stdio so any MCP client
can orchestrate Trust_Bench evaluations.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("trust_bench_mcp")

WORKDIR = Path(os.getenv("TRUST_BENCH_WORKDIR", "./trust_bench_workspace")).resolve()
WORKDIR.mkdir(parents=True, exist_ok=True)

HTTP_TIMEOUT = float(os.getenv("TRUST_BENCH_HTTP_TIMEOUT", "30"))

SECRET_PATTERNS: Dict[str, str] = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*([A-Za-z0-9/+=]{40})",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9]{36}",
    "Slack Token": r"xox[baprs]-[A-Za-z0-9-]{10,48}",
    "JWT": r"eyJ[A-Za-z0-9-_]{10,}\.[A-Za-z0-9-_]{10,}\.[A-Za-z0-9-_]{10,}",
    "Private Key Header": r"-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----",
    "Generic API Key": r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}['\"]?",
}

app = FastMCP("trust_bench")


def _http_get(url: str) -> requests.Response:
    logger.info("Downloading %s", url)
    resp = requests.get(url, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return resp


def _download_repo_zip(repo_url: str) -> Tuple[BytesIO, str]:
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    for branch in ("main", "master"):
        zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        try:
            resp = _http_get(zip_url)
            return BytesIO(resp.content), branch
        except requests.HTTPError as exc:
            logger.warning("Branch %s unavailable (%s)", branch, exc)
            continue
    raise ValueError("Unable to fetch repo zip (tried main and master)")


def _safe_extract(zip_bytes: BytesIO, dest: Path) -> Path:
    """Extract zip file into dest safely and return repo root."""
    with zipfile.ZipFile(zip_bytes) as archive:
        archive.extractall(dest)
    entries = list(dest.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dest


@app.tool()
def download_and_extract_repo(repo_url: str) -> Dict[str, str]:
    """Download a GitHub repo zip (main/master) and extract into workspace."""
    tmp_dir = tempfile.mkdtemp(prefix="trust_bench_", dir=WORKDIR)
    target = Path(tmp_dir)
    zip_bytes, branch = _download_repo_zip(repo_url)
    repo_root = _safe_extract(zip_bytes, target)
    logger.info("Extracted repo into %s (branch=%s)", repo_root, branch)
    return {
        "workdir": str(target),
        "repo_root": str(repo_root),
        "branch": branch,
    }


@app.tool()
def env_content(dir_path: Optional[str] = None, max_bytes: int = 2 * 1024 * 1024) -> Dict[str, Optional[str]]:
    """Return the contents of the first .env file found under dir_path."""
    root = Path(dir_path or WORKDIR).resolve()
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    for env_file in root.rglob(".env"):
        size = env_file.stat().st_size
        if size > max_bytes:
            continue
        logger.info("Reading .env file at %s", env_file)
        text = env_file.read_text(encoding="utf-8", errors="ignore")
        return {"path": str(env_file), "content": text, "bytes": size}
    return {"path": None, "content": None, "bytes": 0}


def _iter_files(path: Path) -> Iterable[Path]:
    for entry in path.rglob("*"):
        if entry.is_file():
            yield entry


@app.tool()
def scan_repo_for_secrets(dir_path: str, max_file_mb: float = 1.5) -> Dict[str, List[Dict[str, str]]]:
    """Scan a directory for potential secrets using regex heuristics."""
    root = Path(dir_path).resolve()
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    limit_bytes = max_file_mb * 1024 * 1024
    compiled = {name: re.compile(pattern) for name, pattern in SECRET_PATTERNS.items()}
    findings: List[Dict[str, str]] = []

    for file_path in _iter_files(root):
        try:
            if file_path.stat().st_size > limit_bytes:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:  # pragma: no cover - IO issues
            logger.warning("Skipping %s (%s)", file_path, exc)
            continue
        for name, pattern in compiled.items():
            for match in pattern.finditer(text):
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                snippet = text[line_start:line_end].strip()
                findings.append(
                    {
                        "file": str(file_path),
                        "pattern": name,
                        "snippet": snippet[:200],
                    }
                )
    return {"results": findings, "count": len(findings)}


@app.tool()
def cleanup_workspace() -> Dict[str, str]:
    """Remove all files under the TRUST_BENCH_WORKDIR."""
    for child in WORKDIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)
    return {"status": "ok", "workdir": str(WORKDIR)}


if __name__ == "__main__":
    logger.info("Starting Trust_Bench MCP server (workdir=%s)", WORKDIR)
    app.run()
