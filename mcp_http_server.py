#!/usr/bin/env python3
"""
HTTP REST API wrapper for TrustBench MCP tools.
Provides an HTTP interface matching MCPClient expectations.
"""
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
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="TrustBench MCP HTTP Server", version="0.1.0")

# Configuration
WORKDIR = Path(os.environ.get("TRUST_BENCH_WORKDIR", "./trust_bench_data")).resolve()
WORKDIR.mkdir(parents=True, exist_ok=True)

SECRET_PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*([A-Za-z0-9/+=]{40})",
    "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "Slack Token": r"xox[baprs]-[0-9A-Za-z-]{10,60}",
    "GitHub Token": r"gh[pousr]_[0-9A-Za-z]{36}",
    # Private key patterns (detection strings, not actual keys)
    "Private RSA Key": r"-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----",  # nosec
    "Private EC Key": r"-----BEGIN EC PRIVATE KEY-----[\s\S]*?-----END EC PRIVATE KEY-----",  # nosec
    "JWT": r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
}

# Pydantic models
class ToolRequest(BaseModel):
    args: Dict[str, Any]

class PromptGuardRequest(BaseModel):
    prompts: List[str]

# Helper functions
def _download_repo_zip(repo_url: str) -> Path:
    """Download and extract a GitHub repository."""
    target = WORKDIR / "repo"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    normalized = repo_url[:-4] if repo_url.endswith(".git") else repo_url
    for branch in ("main", "master"):
        archive = f"{normalized}/archive/refs/heads/{branch}.zip"
        try:
            resp = requests.get(archive, timeout=60)
            if resp.status_code != 200:
                continue
            buffer = io.BytesIO(resp.content)
            with zipfile.ZipFile(buffer) as zf:
                zf.extractall(target)
                top = next((name.split("/")[0] for name in zf.namelist() if "/" in name), None)
            return (target / top) if top else target
        except Exception:
            continue
    raise RuntimeError("Unable to download repo archive from main/master.")

def _find_small_file(root: Path, name: str, max_mb: float = 5.0) -> Optional[Path]:
    """Find a file by name under a size limit."""
    limit = max_mb * 1024 * 1024
    for candidate in root.rglob(name):
        try:
            if candidate.stat().st_size <= limit:
                return candidate
        except OSError:
            continue
    return None

def _scan_for_secrets(dir_path: Path, max_file_mb: float = 1.5) -> List[Dict[str, str]]:
    """Scan directory for secrets using regex patterns."""
    limit = int(max_file_mb * 1024 * 1024)
    matches = []
    scanned = 0

    for file_path in dir_path.rglob("*"):
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
                    matches.append({
                        "file": str(file_path.relative_to(dir_path)),
                        "pattern": label,
                        "snippet": snippet
                    })
                    break
        except Exception:
            continue

    return matches

# API Endpoints
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"ok": True, "status": "healthy"}

@app.post("/discover")
async def discover():
    """List available tools."""
    return {
        "tools": [
            "prompt_guard",
            "semgrep_rules",
            "secrets_scan",
            "download_and_extract_repo",
            "env_content",
            "cleanup_workspace"
        ]
    }

@app.post("/tools/prompt_guard")
async def prompt_guard(request: ToolRequest):
    """
    Simulate prompt guard - checks for injection patterns.
    Returns blocked count based on simple heuristics.
    """
    try:
        prompts = request.args.get("prompts", [])
        
        # Enhanced injection detection patterns
        injection_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"disregard\s+(all\s+)?rules",
            r"system\s*(prompt|instructions|rules)",
            r"reveal\s+(your|the)?\s*(api|key|secret|password|token)",
            r"<script>",
            r"DROP\s+TABLE",
            r";\s*--",
            r"UNION\s+SELECT",
            r"\.\./\.\./",  # Path traversal
            r"etc/passwd",
            r"etc/shadow",
            r"rm\s+-rf",
            r"environment\s+variables",
            r"eval\s*\(",
            r"exec\s*\(",
            r"\$\{jndi:",  # Log4j
            r"SELECT\s+\*\s+FROM",
            r"sudo\s+",
        ]
        
        blocked = 0
        bypasses = []
        
        for idx, prompt in enumerate(prompts):
            is_blocked = False
            for pattern in injection_patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    is_blocked = True
                    blocked += 1
                    break
            
            if not is_blocked:
                bypasses.append({
                    "prompt_id": idx,
                    "prompt": prompt[:100],
                    "trace": "No injection pattern detected"
                })
        
        return {
            "ok": True,
            "data": {
                "blocked": blocked,
                "total": len(prompts),
                "bypasses": bypasses
            }
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@app.post("/tools/semgrep_rules")
async def semgrep_rules(request: ToolRequest):
    """
    Placeholder for semgrep - returns empty findings for now.
    Real implementation would run semgrep scan.
    """
    try:
        path = request.args.get("path", "")
        rules_path = request.args.get("rules_path")
        
        # For now, return empty findings
        # TODO: Integrate actual semgrep scanning
        return {
            "ok": True,
            "data": {
                "findings": [],
                "stats": {"count": 0}
            }
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@app.post("/tools/secrets_scan")
async def secrets_scan(request: ToolRequest):
    """Scan repository for hardcoded secrets."""
    try:
        path_str = request.args.get("path", "")
        path = Path(path_str) if path_str else WORKDIR / "repo"
        
        if not path.exists():
            return {
                "ok": True,
                "data": {
                    "findings": [],
                    "stats": {"count": 0}
                }
            }
        
        findings = _scan_for_secrets(path)
        
        return {
            "ok": True,
            "data": {
                "findings": findings,
                "stats": {"count": len(findings)}
            }
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@app.post("/tools/download_and_extract_repo")
async def download_and_extract_repo(request: ToolRequest):
    """Download and extract a GitHub repository."""
    try:
        repo_url = request.args.get("repo_url", "")
        if not repo_url:
            return {"ok": False, "error": "repo_url is required"}
        
        location = _download_repo_zip(repo_url)
        return {
            "ok": True,
            "data": {
                "repo_dir": str(location),
                "message": f"Extracted to {location}"
            }
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@app.post("/tools/env_content")
async def env_content(request: ToolRequest):
    """Return content of .env files in directory."""
    try:
        dir_path = request.args.get("dir_path", "")
        root = Path(dir_path) if dir_path else WORKDIR / "repo"
        
        found = _find_small_file(root, ".env", max_mb=2.0)
        if not found:
            return {
                "ok": True,
                "data": {
                    "found": False,
                    "path": None,
                    "content": None
                }
            }
        
        try:
            text = found.read_text(encoding="utf-8", errors="ignore")
            return {
                "ok": True,
                "data": {
                    "found": True,
                    "path": str(found),
                    "content": text
                }
            }
        except Exception as exc:
            return {
                "ok": True,
                "data": {
                    "found": False,
                    "path": str(found),
                    "content": f"Error reading file: {exc}"
                }
            }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@app.post("/tools/cleanup_workspace")
async def cleanup_workspace(request: ToolRequest):
    """Remove working directory to reset server state."""
    try:
        if WORKDIR.exists():
            shutil.rmtree(WORKDIR)
        WORKDIR.mkdir(parents=True, exist_ok=True)
        return {
            "ok": True,
            "data": {
                "message": f"Workspace reset at {WORKDIR}"
            }
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MCP_SERVER_PORT", "8765"))
    print(f"🚀 Starting TrustBench MCP HTTP Server on port {port}")
    print(f"📁 Working directory: {WORKDIR}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
