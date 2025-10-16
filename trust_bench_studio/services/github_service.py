"""Utilities for preparing repository workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from trust_bench_studio.utils import STUDIO_DATA_DIR
from trust_bench_studio.services.job_store import JobStatus


@dataclass
class RepositoryCheckout:
    """Represents a local workspace allocated for repository analysis."""

    job_id: str
    repo_url: str
    workdir: Path
    metadata: Dict[str, str]


class GitHubService:
    """Placeholder GitHub integration used while the ingestion pipeline is bootstrapped."""

    def __init__(self, workspaces_root: Optional[Path] = None) -> None:
        self.workspaces_root = Path(workspaces_root) if workspaces_root else STUDIO_DATA_DIR / "repositories"
        self.workspaces_root.mkdir(parents=True, exist_ok=True)

    def allocate_workspace(self, job: JobStatus) -> RepositoryCheckout:
        """
        Reserve a workspace directory for the given job.

        The actual cloning/fetching work will be implemented later; for now we just
        ensure a deterministic directory structure exists so downstream services can
        deposit artifacts.
        """
        job_dir = self.workspaces_root / job.id
        workdir = job_dir / "workspace"
        workdir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "status": "pending_clone",
        }
        return RepositoryCheckout(
            job_id=job.id,
            repo_url=job.repo_url,
            workdir=workdir,
            metadata=metadata,
        )
