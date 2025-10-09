"""TrustBench MCP Client
A small, typed wrapper to call MCP tools consistently.

Usage:
    from trustbench_core.tools.mcp_client import MCPClient, ToolError
    client = MCPClient.from_env()
    tools = client.discover()
    out = client.call("prompt_guard", prompts=[...])
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json, os, time
import urllib.request

class ToolError(RuntimeError):
    def __init__(self, tool: str, message: str, data: Optional[dict]=None):
        super().__init__(f"{tool}: {message}")
        self.tool = tool
        self.data = data or {}

@dataclass
class MCPConfig:
    base_url: str = "http://localhost:8765"
    api_key: Optional[str] = None
    timeout_s: float = 30.0

class MCPClient:
    def __init__(self, cfg: MCPConfig):
        self.cfg = cfg

    @classmethod
    def from_env(cls) -> "MCPClient":
        return cls(MCPConfig(
            base_url=os.getenv("MCP_SERVER_URL", "http://localhost:8765"),
            api_key=os.getenv("MCP_API_KEY") or None,
            timeout_s=float(os.getenv("MCP_TIMEOUT_S", "30")),
        ))

    def _req(self, path: str, payload: dict) -> dict:
        url = self.cfg.base_url.rstrip("/") + path
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        if self.cfg.api_key:
            req.add_header("Authorization", f"Bearer {self.cfg.api_key}")
        with urllib.request.urlopen(req, timeout=self.cfg.timeout_s) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    # --- Public API ---
    def health(self) -> bool:
        try:
            out = self._req("/health", {})
            return bool(out.get("ok"))
        except Exception:
            return False

    def discover(self) -> List[str]:
        out = self._req("/discover", {})
        return list(out.get("tools", []))

    def call(self, tool: str, **kwargs) -> dict:
        out = self._req("/tools/" + tool, {"args": kwargs})
        if not out.get("ok", False):
            raise ToolError(tool, out.get("error", "unknown"), out)
        return out.get("data", {})

# Convenience wrappers (kept thin, so agents stay clean)
def prompt_guard(client: MCPClient, prompts: List[str]) -> Dict[str, Any]:
    return client.call("prompt_guard", prompts=prompts)

def semgrep_rules(client: MCPClient, path: str, rules_path: Optional[str]=None) -> Dict[str, Any]:
    return client.call("semgrep_rules", path=path, rules_path=rules_path or os.getenv("SEMGREP_RULES_PATH"))

def secrets_scan(client: MCPClient, path: str) -> Dict[str, Any]:
    return client.call("secrets_scan", path=path)
