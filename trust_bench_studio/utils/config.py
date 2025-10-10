"""Configuration helpers for locating Trust_Bench assets."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List


PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
PROFILES_DIR: Path = PROJECT_ROOT / "profiles"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
STUDIO_DATA_DIR: Path = PROJECT_ROOT / "trust_bench_studio" / "data"
MCP_CACHE_DIR: Path = STUDIO_DATA_DIR / "mcp_cache"

_DEFAULT_RUN_DIR_CANDIDATES: List[Path] = [
    PROJECT_ROOT / "eval" / "runs",
    PROJECT_ROOT / "runs",
]


def iter_existing_run_dirs(
    candidates: Iterable[Path] | None = None,
) -> Iterable[Path]:
    """Yield run directories that actually exist on disk."""
    for candidate in candidates or _DEFAULT_RUN_DIR_CANDIDATES:
        if candidate.exists():
            yield candidate


def get_runs_dir() -> Path:
    """Return the primary runs directory, creating a placeholder if needed."""
    for run_dir in iter_existing_run_dirs():
        return run_dir

    fallback = _DEFAULT_RUN_DIR_CANDIDATES[-1]
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


MCP_BASE_URL: str = os.getenv("TRUST_BENCH_MCP_URL", "http://localhost:3000")
