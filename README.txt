# Phase-1 Live Helper Pack

This pack includes:
- `calibrate_thresholds.py` -- now supports `--runs-dir` so you can calibrate from a directory of prior runs.
- `mcp_server_stub.py` -- tiny local HTTP server that mimics the MCP endpoints your security agent expects.

## MCP stub
```bash
python mcp_server_stub.py
export MCP_SERVER_URL=http://127.0.0.1:8765
```

## Calibrate thresholds
```bash
# Using existing runs
python calibrate_thresholds.py --runs-dir trustbench_core/eval/runs/default_calibration

# Or invoke N runs
python calibrate_thresholds.py --profile profiles/default.yaml --runs 10
```
