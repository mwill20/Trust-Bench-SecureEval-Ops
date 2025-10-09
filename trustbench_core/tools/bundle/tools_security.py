"""Security tool bundle facade.
Normalizes outputs so the Security agent can stay simple.
Return shape for all functions:
    {"ok": bool, "findings": list, "stats": {...}}
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from trustbench_core.tools.mcp_client import (
    MCPClient,
    prompt_guard as _pg,
    semgrep_rules as _sg,
    secrets_scan as _ss,
)

def _ok(findings: List[dict], stats: dict) -> Dict[str, Any]:
    return {"ok": True, "findings": findings, "stats": stats}

def prompt_guard(prompts: List[str], client: Optional[MCPClient]=None) -> Dict[str, Any]:
    client = client or MCPClient.from_env()
    data = _pg(client, prompts=prompts)
    # expected data: {"blocked": int, "total": int, "bypasses": [{prompt, trace}...]}
    stats = {"blocked": data.get("blocked", 0), "total": data.get("total", 0)}
    findings = data.get("bypasses", [])
    return _ok(findings, stats)

def semgrep_scan(path: str, rules_path: Optional[str]=None, client: Optional[MCPClient]=None) -> Dict[str, Any]:
    client = client or MCPClient.from_env()
    data = _sg(client, path=path, rules_path=rules_path)
    findings = data.get("findings", [])
    stats = {"count": len(findings)}
    return _ok(findings, stats)

def secrets_scan(path: str, client: Optional[MCPClient]=None) -> Dict[str, Any]:
    client = client or MCPClient.from_env()
    data = _ss(client, path=path)
    findings = data.get("findings", [])
    stats = {"count": len(findings)}
    return _ok(findings, stats)
