"""FastAPI backend powering the Trust_Bench Studio React UI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from trust_bench_studio.utils import (
    load_agents_manifest,
    synthesize_verdict,
)
from trust_bench_studio.utils.mcp_client import MCPClient
from trust_bench_studio.utils.run_store import (
    RunRecord,
    RunSummary,
    list_runs,
    load_run_summary,
)

MAX_INPUT_LENGTH = 2048
PERMITTED_TOOLS = {
    "cleanup_workspace",
    "scan_repo_for_secrets",
    "env_content",
}


def _latest_run_record() -> RunRecord:
    runs = list_runs()
    if not runs:
        raise HTTPException(
            status_code=404,
            detail="No evaluation runs found. Execute an evaluation before using the studio.",
        )
    for record in runs:
        if record.name == "latest":
            return record
    return runs[0]


def _load_latest_summary() -> RunSummary:
    record = _latest_run_record()
    summary = load_run_summary(record.path)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run at {record.path} did not contain any usable metrics or trace data.",
        )
    return summary


def _summary_to_dict(summary: RunSummary) -> Dict[str, Any]:
    return {
        "metrics": summary.metrics,
        "agents": summary.agents,
        "raw": summary.raw,
    }


def _sanitize_user_input(value: str, field_name: str) -> str:
    trimmed = value.strip()
    if len(trimmed) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} exceeds maximum length of {MAX_INPUT_LENGTH} characters.",
        )
    return trimmed


class MCPRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


class BaselineRequest(BaseModel):
    note: Optional[str] = Field(default=None, max_length=256)


app = FastAPI(title="Trust_Bench Studio API", version="0.3-alpha")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/agents")
def get_agents_manifest() -> Dict[str, Any]:
    manifest = load_agents_manifest()
    return {"agents": manifest}


@app.get("/api/run/latest")
def get_latest_run() -> Dict[str, Any]:
    summary = _load_latest_summary()
    record = _latest_run_record()
    return {
        "run": record.name,
        "path": str(record.path),
        "summary": _summary_to_dict(summary),
    }


@app.get("/api/verdict")
def get_latest_verdict() -> Dict[str, Any]:
    summary = _load_latest_summary()
    verdict = synthesize_verdict(summary, None)
    return {"verdict": verdict}


@app.post("/api/input/sanitize")
def sanitize_user_input(payload: Dict[str, str] = Body(...)) -> Dict[str, str]:
    text = payload.get("text", "")
    cleaned = _sanitize_user_input(text, "input")
    return {"text": cleaned}


@app.post("/api/mcp/{tool_name}")
def invoke_mcp_tool(tool_name: str, request: MCPRequest) -> Dict[str, Any]:
    if tool_name not in PERMITTED_TOOLS:
        raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' is not permitted.")

    client = MCPClient()
    response = client.call_tool(tool_name, **request.arguments)
    if response is None:
        raise HTTPException(
            status_code=503,
            detail="MCP bridge did not return a response. Ensure the MCP server is running.",
        )
    return {"tool": tool_name, "response": response}


@app.post("/api/baseline/promote")
def promote_to_baseline(request: BaselineRequest) -> Dict[str, Any]:
    note = request.note or "auto baseline"
    _sanitize_user_input(note, "note")

    script_path = Path(__file__).resolve().parents[2] / "scripts" / "make_baseline.py"
    if not script_path.exists():
        raise HTTPException(status_code=500, detail="Baseline script not found.")

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path), "--note", note],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # pragma: no cover - system errors
        raise HTTPException(status_code=500, detail=f"Failed to launch baseline script: {exc}") from exc

    if completed.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Baseline script failed: {completed.stderr or completed.stdout}",
        )

    return {"status": "ok", "stdout": completed.stdout.strip()}

