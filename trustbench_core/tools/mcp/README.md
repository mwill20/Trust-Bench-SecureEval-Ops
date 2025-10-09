# TrustBench MCP Server
Exposes lightweight repo and secrets checks as **Model Context Protocol (MCP)** tools. Any MCP-aware client (Claude Desktop, Cursor, Windsurf, LangGraph agent) can discover and call these tools.

## 1) Install and scaffold
```bash
pip install modelcontextprotocol python-dotenv requests spacy
python -m spacy download en_core_web_sm
```

Layout:
```
trustbench_core/tools/mcp/
  server.py
  .env.example          # optional (API keys, etc.)
  data/                 # working area (repo extracts land here)
  gazetteer.txt         # optional list of keywords to flag
```

## 2) `server.py` (MCP server)
Implements:
- Tools: `download_and_extract_repo`, `env_content`, `secrets_scan`, `grep`
- Resources: `trustbench/repo_root`, `trustbench/gazetteer`

> Extend with extras such as `vt_lookup(hash)`, `yara_scan(dir)`, `sbom_generate()` when needed.

## 3) Register the server with your MCP client
Add to your MCP client config (example: Claude Desktop):
```json
{
  "mcpServers": {
    "trustbench": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/trustbench_core/tools/mcp"
    }
  }
}
```

Restart the client; the tools and resources will be auto-discovered.

## 4) Sample operator prompts
**Bootstrap and scan**
> Use the TrustBench server. Call `download_and_extract_repo` on `https://github.com/acme/sec-repo.git` then run `secrets_scan`. Summarize findings and surface the top 10 lines grouped by kind.

**Targeted `.env` check**
> Invoke `env_content`. If any `.env` files exist, redact values and list the keys. Suggest remediation steps for a follow-up PR.

**Pattern hunt**
> Use `grep` with pattern `(?i)(password|secret|token)` and summarize by file.

Because these are MCP tools, your agent can chain them in a Think -> Act -> Think loop without custom glue code.

## 5) Security and ops tips
- Run in a sandboxed workspace (non-prod credentials; read-only tokens).
- Redact on return: if you later add tools that read secrets, mask values.
- Rate-limit and log tool calls to avoid accidental abuse.
- Gazetteer: keep `gazetteer.txt` under version control to tune noisy hits.
- Timeouts: `requests` applies a timeout for downloads; extend where needed.
