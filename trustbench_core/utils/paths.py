"""Path resolution helpers for TrustBench core modules."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_data_path(path: str | Path) -> Path:
    """Resolve project-relative data paths regardless of the current working directory."""
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    cwd_path = Path.cwd() / candidate
    if cwd_path.exists():
        return cwd_path

    repo_path = REPO_ROOT / candidate
    if repo_path.exists():
        return repo_path

    # Fall back to repo-relative path even if the file does not yet exist so callers
    # receive a stable, explanatory location in error messages.
    return repo_path

