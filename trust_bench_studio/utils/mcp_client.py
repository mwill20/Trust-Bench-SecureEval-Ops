"""Lightweight MCP client wrapper used by the Studio UI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, request

from .config import MCP_BASE_URL, MCP_CACHE_DIR, PROJECT_ROOT


@dataclass
class MCPReport:
    """Container for MCP task results."""

    name: str
    payload: Dict[str, Any]


class MCPClient:
    """Minimal HTTP client for interacting with the MCP bridge."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or MCP_BASE_URL).rstrip("/")

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> Optional[dict]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        data = json.dumps(body or {}).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"}
        req = request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with request.urlopen(req, timeout=15) as response:
                payload = response.read().decode("utf-8")
        except (error.URLError, TimeoutError):
            return None

        try:
            document = json.loads(payload)
        except json.JSONDecodeError:
            return None

        return document if isinstance(document, dict) else None

    def list_reports(self) -> List[MCPReport]:
        """Fetch the latest reports when an MCP server is reachable."""
        payload = self._request("GET", "reports")
        if not payload:
            return []

        reports: List[MCPReport] = []
        for name, body in payload.items():
            if isinstance(body, dict):
                reports.append(MCPReport(name=name, payload=body))
        return reports

    def call_tool(self, tool_name: str, **kwargs: Any) -> Optional[dict]:
        """Invoke an MCP tool endpoint and persist the response to cache."""
        payload = {"tool": tool_name, "arguments": kwargs}
        response = self._request("POST", f"tools/{tool_name}", payload)
        if response is not None:
            self._cache_tool_result(tool_name, response)
        return response

    def _cache_tool_result(self, tool_name: str, payload: dict) -> None:
        MCP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        cache_path = MCP_CACHE_DIR / f"{tool_name}_{timestamp}.json"
        try:
            cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            # Caching errors should not block UI updates.
            return


def default_workspace_path() -> Path:
    """Return the root directory scanned by default MCP tools."""
    return PROJECT_ROOT

