"""High-level orchestration helper for repository jobs."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from .github_service import GitHubService, RepositoryCheckout
from .job_store import JobStage, JobState, JobStatus, JobStore


class JobManager:
    """Coordinates job lifecycle transitions while deferring heavy work to services."""

    def __init__(self, store: Optional[JobStore] = None, github_service: Optional[GitHubService] = None) -> None:
        self.store = store or JobStore()
        self.github = github_service or GitHubService(self.store.root)

    def enqueue(self, repo_url: str, *, profile: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> JobStatus:
        """Create a new job entry and prepare its workspace."""
        job = self.store.create_job(repo_url, profile=profile, metadata=metadata)
        checkout = self.github.allocate_workspace(job)
        self.store.update_job(
            job.id,
            metadata_update={
                "workspace": str(checkout.workdir),
                **checkout.metadata,
            },
            message="Job queued for analysis",
        )
        return self.store.get_job(job.id)  # type: ignore[return-value]

    def transition(
        self,
        job_id: str,
        *,
        state: Optional[JobState] = None,
        stage: Optional[JobStage] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        artifacts: Optional[Dict[str, object]] = None,
    ) -> JobStatus:
        """Update job metadata; returns the new snapshot."""
        return self.store.update_job(
            job_id,
            state=state,
            stage=stage,
            progress=progress,
            message=message,
            error=error,
            artifacts=artifacts,
        )

    def get(self, job_id: str) -> Optional[JobStatus]:
        return self.store.get_job(job_id)

    def list(self) -> Iterable[JobStatus]:
        return self.store.list_jobs()
