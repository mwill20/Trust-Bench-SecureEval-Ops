#!/usr/bin/env python3
"""
Cleanup old TrustBench evaluation runs and temporary files.
Archives old runs and frees disk space while preserving recent runs and baseline.
"""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
KEEP_RECENT_RUNS = 10  # Number of recent runs to keep
RUNS_DIR = PROJECT_ROOT / "trustbench_core" / "eval" / "runs"
ARCHIVE_DIR = RUNS_DIR / "archive"


def get_run_directories() -> List[Path]:
    """Get all run directories except 'latest', 'baseline', and 'archive'."""
    if not RUNS_DIR.exists():
        return []
    
    excluded = {"latest", "baseline", "archive"}
    runs = []
    
    for item in RUNS_DIR.iterdir():
        if item.is_dir() and item.name not in excluded:
            runs.append(item)
    
    # Sort by modification time (most recent first)
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return runs


def get_directory_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    except (OSError, PermissionError):
        pass
    return total


def format_size(bytes_size: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def archive_run(run_path: Path, archive_dir: Path) -> int:
    """Archive a run directory and return bytes freed."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped archive name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{run_path.name}_{timestamp}"
    archive_path = archive_dir / archive_name
    
    size_before = get_directory_size(run_path)
    
    try:
        shutil.move(str(run_path), str(archive_path))
        print(f"  📦 Archived: {run_path.name} → archive/{archive_name}")
        return size_before
    except Exception as exc:
        print(f"  ⚠️  Failed to archive {run_path.name}: {exc}", file=sys.stderr)
        return 0


def cleanup_temp_files() -> int:
    """Clean up temporary files and caches."""
    bytes_freed = 0
    temp_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/.pytest_cache",
        "**/*.log",
    ]
    
    for pattern in temp_patterns:
        for item in PROJECT_ROOT.glob(pattern):
            try:
                size = get_directory_size(item) if item.is_dir() else item.stat().st_size
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                bytes_freed += size
            except Exception:
                continue
    
    return bytes_freed


def main():
    """Main cleanup routine."""
    print("🧹 Starting TrustBench Workspace Cleanup...")
    print()
    
    total_freed = 0
    
    # Step 1: Archive old runs
    print(f"📂 Scanning evaluation runs (keeping {KEEP_RECENT_RUNS} most recent)...")
    runs = get_run_directories()
    
    if not runs:
        print("  ℹ️  No old runs found to archive")
    else:
        print(f"  Found {len(runs)} run(s)")
        
        # Archive runs beyond the keep limit
        if len(runs) > KEEP_RECENT_RUNS:
            runs_to_archive = runs[KEEP_RECENT_RUNS:]
            print(f"  Archiving {len(runs_to_archive)} old run(s)...")
            
            for run_path in runs_to_archive:
                freed = archive_run(run_path, ARCHIVE_DIR)
                total_freed += freed
        else:
            print(f"  All {len(runs)} runs are recent - nothing to archive")
    
    print()
    
    # Step 2: Clean up temporary files
    print("🗑️  Cleaning up temporary files...")
    temp_freed = cleanup_temp_files()
    total_freed += temp_freed
    
    if temp_freed > 0:
        print(f"  ✅ Cleaned: {format_size(temp_freed)}")
    else:
        print("  ℹ️  No temporary files found")
    
    print()
    
    # Step 3: Summary
    print("=" * 60)
    print("✅ Cleanup Complete!")
    print()
    print(f"📊 Summary:")
    print(f"  • Kept recent runs: {min(len(runs), KEEP_RECENT_RUNS)}")
    print(f"  • Archived old runs: {max(0, len(runs) - KEEP_RECENT_RUNS)}")
    print(f"  • Total space freed: {format_size(total_freed)}")
    print()
    print(f"📁 Archive location: {ARCHIVE_DIR.relative_to(PROJECT_ROOT)}")
    print()
    print("ℹ️  Protected items (never deleted):")
    print("  • runs/latest/ - Current evaluation")
    print("  • runs/baseline/ - Golden baseline")
    print(f"  • {KEEP_RECENT_RUNS} most recent runs")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cleanup interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌ Cleanup failed: {exc}", file=sys.stderr)
        sys.exit(1)
