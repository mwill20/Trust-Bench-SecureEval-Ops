#!/usr/bin/env python3
# Minimal MCP-like stub for local testing.
# Endpoints: /health, /discover, /tools/prompt_guard, /tools/semgrep_rules, /tools/secrets_scan
from __future__ import annotations
import json, os, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = int(os.getenv("MCP_STUB_PORT", "8765"))
ROOT = Path(os.getenv("MCP_STUB_ROOT", "."))

SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9-_]{12,}"),
    re.compile(r"(?i)password\s*[:=]\s*['\"]?.{6,}"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{20,}")
]

def json_response(handler: BaseHTTPRequestHandler, status: int, obj: dict) -> None:
    body = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            return json_response(self, 200, {"ok": True})
        if self.path == "/discover":
            return json_response(self, 200, {"tools": ["prompt_guard", "semgrep_rules", "secrets_scan"]})
        return json_response(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        args = payload.get("args", {})

        if self.path == "/tools/prompt_guard":
            prompts = args.get("prompts", [])
            blocked, bypasses = 0, []
            for prompt in prompts:
                if re.search(r"(?i)(ignore|bypass|jailbreak|system prompt)", prompt):
                    blocked += 1
                else:
                    bypasses.append({"prompt": prompt, "trace": "heuristic_allow"})
            return json_response(
                self,
                200,
                {"ok": True, "data": {"blocked": blocked, "total": len(prompts), "bypasses": bypasses}},
            )

        if self.path == "/tools/semgrep_rules":
            path = Path(args.get("path", ".")).resolve()
            findings = []
            for fp in path.rglob("*.py"):
                try:
                    text = fp.read_text(errors="ignore")
                except Exception:
                    continue
                if "eval(" in text:
                    findings.append({"file": str(fp), "rule": "no-eval"})
            return json_response(self, 200, {"ok": True, "data": {"findings": findings}})

        if self.path == "/tools/secrets_scan":
            path = Path(args.get("path", ".")).resolve()
            findings = []
            for fp in path.rglob("*"):
                if fp.is_file() and fp.stat().st_size < 2_000_000:
                    try:
                        text = fp.read_text(errors="ignore")
                    except Exception:
                        continue
                    for pattern in SECRET_PATTERNS:
                        if pattern.search(text):
                            findings.append({"file": str(fp), "pattern": pattern.pattern})
                            break
            return json_response(self, 200, {"ok": True, "data": {"findings": findings}})

        return json_response(self, 404, {"ok": False, "error": "unknown tool"})

def main() -> None:
    server = HTTPServer(("0.0.0.0", PORT), MCPHandler)
    print(f"MCP stub listening on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
