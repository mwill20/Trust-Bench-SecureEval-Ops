# Trust Bench MCP Server

Minimal, production-friendly MCP server for the Trust_Bench project.  It exposes
repo hygiene tools over MCP stdio so any MCP-aware client (Claude Desktop,
Cursor, Windsurf, your own agent) can use them immediately.

## Tools

| Tool | Description |
|------|-------------|
| `download_and_extract_repo(repo_url)` | Downloads a public GitHub repo ZIP (`main` then `master`) and extracts it into the workspace. Returns the extraction path and detected branch. |
| `env_content(dir_path=None, max_bytes=2MB)` | Returns the content of the first `.env` file found under the provided path (or the workspace). |
| `scan_repo_for_secrets(dir_path, max_file_mb=1.5)` | Regex heuristics for common secrets (AWS/GitHub tokens, private keys, JWTs, etc.). Returns file hits and snippets. |
| `cleanup_workspace()` | Clears the workspace directory. |


## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U -r requirements.txt
python trust_bench_server.py
```

By default the server uses `./trust_bench_workspace`.  Override with
`TRUST_BENCH_WORKDIR=/desired/path`.

## MCP Client Config (example)

Merge this into your MCP client configuration (Claude Desktop shown):

```json
{
  "mcpServers": {
    "Trust_Bench": {
      "command": "python",
      "args": ["trust_bench_server.py"],
      "env": {
        "TRUST_BENCH_WORKDIR": "./trust_bench_data"
      }
    }
  }
}
```

## Docker (optional)

```bash
docker build -t trust_bench_mcp .
docker run -it --rm -e TRUST_BENCH_WORKDIR=/data -v $(pwd)/data:/data trust_bench_mcp
```

## Notes & Next Steps

* The current implementation assumes public GitHub repos via ZIP download.  
  For private repositories we can add token-authenticated downloads or `git clone`.
* `scan_repo_for_secrets` uses lightweight regex heuristics—suitable for triage, not
  compliance audits. Swap in a stronger scanner as needed.
* If your MCP client supports tool discovery you'll see these four tools immediately.
