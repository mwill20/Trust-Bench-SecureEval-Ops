"""
Compatibility shim for legacy command:
    python -m trustbench_core.eval.evaluate_agent --repo <path> --output <dir>

This forwards to Project2v2/main.py so Project2v2 stays the single source of truth.
"""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

# Resolve repo root from this file: <root>/trustbench_core/eval/evaluate_agent.py
REPO_ROOT = Path(__file__).resolve().parents[2]
NEW_MAIN = REPO_ROOT / "Project2v2" / "main.py"


def _proxy_main() -> None:
    if not NEW_MAIN.exists():
        sys.stderr.write(f"[ERROR] Cannot locate Project2v2 entrypoint: {NEW_MAIN}\n")
        sys.exit(2)

    parser = argparse.ArgumentParser(prog="trustbench_core.eval.evaluate_agent")
    parser.add_argument("--repo", required=True, help="Path to repository to audit")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "Project2v2" / "output"),
        help="Output directory for reports (default: Project2v2/output)",
    )
    # allow passthrough of any extra args without failing
    args, unknown = parser.parse_known_args()

    # Forward to new main in-process using current interpreter.
    # Equivalent to: python Project2v2/main.py --repo ... --output ... [unknown...]
    project_root = str(NEW_MAIN.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    sys.argv = [str(NEW_MAIN), "--repo", args.repo, "--output", args.output, *unknown]
    runpy.run_path(str(NEW_MAIN), run_name="__main__")


if __name__ == "__main__":
    _proxy_main()
