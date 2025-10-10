"""Create a timestamped baseline run from the latest evaluation output."""

from __future__ import annotations

import argparse
import shutil
from datetime import UTC, datetime
from pathlib import Path


def _copy_latest_run(destination: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    candidate_dirs = [
        project_root / "eval" / "runs",
        project_root / "trustbench_core" / "eval" / "runs",
    ]
    runs_dir = next((path for path in candidate_dirs if path.exists()), None)
    if runs_dir is None:
        searched = ", ".join(str(path) for path in candidate_dirs)
        raise FileNotFoundError(f"No evaluation runs directory found. Searched: {searched}")

    latest = runs_dir / "latest"
    source: Path | None = None
    if latest.exists():
        source = latest
    else:
        candidates = [
            d for d in runs_dir.iterdir()
            if d.is_dir() and not d.name.startswith("baseline_") and d.name != "latest"
        ]
        if candidates:
            candidates.sort(key=lambda d: d.stat().st_mtime, reverse=True)
            source = candidates[0]
            print(f"Warning: 'latest' not found, using most recent run: {source}")
        else:
            print(f"Error: No evaluation runs found in {runs_dir}. Please run an evaluation first.")
            raise FileNotFoundError(f"No evaluation runs found in {runs_dir}.")
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("artifacts", "artifacts/*", "__pycache__"),
    )


def _write_metadata(baseline_dir: Path, note: str | None) -> None:
    readme = baseline_dir / "README.md"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    readme.write_text(
        "\n".join(
            [
                f"# Baseline Run — {timestamp}",
                "",
                "This baseline mirrors the contents of `eval/runs/latest` at the time of capture.",
                "Trimmed artifacts are intentionally omitted to keep dashboards fast.",
                f"Notes: {note or 'not provided'}",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a baseline run snapshot.")
    parser.add_argument("--note", help="Optional notes about model/profile/seeds.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
    baseline_dir = project_root / "eval" / "runs" / f"baseline_{timestamp}"
    baseline_dir.mkdir(parents=True, exist_ok=False)

    _copy_latest_run(baseline_dir)
    _write_metadata(baseline_dir, args.note)

    for required in ("run.json", "metrics.json"):
        if not (baseline_dir / required).exists():
            raise FileNotFoundError(f"{required} missing in {baseline_dir}")

    print(f"Baseline ready: {baseline_dir}")


if __name__ == "__main__":
    main()
