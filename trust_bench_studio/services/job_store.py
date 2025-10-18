"""Disk-backed job metadata tracking for repository analyses."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from trust_bench_studio.utils import STUDIO_DATA_DIR


class JobState(str, Enum):
    """High-level job lifecycle states."""

    QUEUED = "queued"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    EVALUATING = "evaluating"
    REPORTING = "reporting"
    COMPLETE = "complete"
    FAILED = "failed"


class JobStage(str, Enum):
    """Granular stages used for progress displays."""

    INIT = "init"
    CLONING = "cloning"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    REPORTING = "reporting"
    COMPLETE = "complete"


def _now() -> str:
    return datetime.utcnow().isoformat()


def _clamp_progress(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class JobStatus:
    """Normalized snapshot of repository analysis work."""

    id: str
    repo_url: str
    state: JobState = JobState.QUEUED
    stage: JobStage = JobStage.INIT
    progress: float = 0.0
    message: str = ""
    profile: Optional[str] = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    error: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        data["stage"] = self.stage.value
        data["progress"] = float(self.progress)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobStatus":
        return cls(
            id=str(data["id"]),
            repo_url=str(data["repo_url"]),
            state=JobState(data.get("state", JobState.QUEUED.value)),
            stage=JobStage(data.get("stage", JobStage.INIT.value)),
            progress=float(data.get("progress", 0.0)),
            message=str(data.get("message", "")),
            profile=data.get("profile"),
            created_at=str(data.get("created_at", _now())),
            updated_at=str(data.get("updated_at", _now())),
            error=data.get("error"),
            artifacts=data.get("artifacts") or {},
            metadata=data.get("metadata") or {},
        )


class JobStore:
    """Read/write interface for job metadata stored on disk."""

    STATUS_FILENAME = "status.json"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else STUDIO_DATA_DIR / "repositories"
        self.root.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, JobStatus] = {}
        self._lock = threading.Lock()
        self._hydrate_existing()

    # -- public API -----------------------------------------------------
    def create_job(
        self,
        repo_url: str,
        *,
        profile: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobStatus:
        """Create a new job and persist metadata immediately."""
        job_id = uuid.uuid4().hex
        job = JobStatus(
            id=job_id,
            repo_url=repo_url,
            profile=profile,
            metadata=metadata or {},
        )
        with self._lock:
            self._jobs[job_id] = job
            self._persist(job)
        return job

    def get_job(self, job_id: str) -> Optional[JobStatus]:
        with self._lock:
            # First try to refresh from disk in case another process updated it
            self._refresh_job_from_disk(job_id)
            job = self._jobs.get(job_id)
            return JobStatus.from_dict(job.to_dict()) if job else None

    def list_jobs(self) -> Iterable[JobStatus]:
        with self._lock:
            return [JobStatus.from_dict(job.to_dict()) for job in self._jobs.values()]

    def update_job(
        self,
        job_id: str,
        *,
        state: Optional[JobState] = None,
        stage: Optional[JobStage] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        artifacts: Optional[Dict[str, Any]] = None,
        metadata_update: Optional[Dict[str, Any]] = None,
    ) -> JobStatus:
        """Update job fields atomically and persist the change."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise KeyError(f"Unknown job id '{job_id}'")

            if state is not None:
                job.state = state
            if stage is not None:
                job.stage = stage
            if progress is not None:
                job.progress = _clamp_progress(progress)
            if message is not None:
                job.message = message
            if error is not None:
                job.error = error
            if artifacts:
                job.artifacts.update(artifacts)
            if metadata_update:
                job.metadata.update(metadata_update)

            if job.state in {JobState.COMPLETE, JobState.FAILED}:
                job.stage = JobStage.COMPLETE
                job.progress = 1.0 if job.state == JobState.COMPLETE else job.progress

            job.updated_at = _now()
            self._persist(job)
            return JobStatus.from_dict(job.to_dict())

    # -- internal helpers -----------------------------------------------
    def _refresh_job_from_disk(self, job_id: str) -> None:
        """Refresh a specific job from disk if it exists."""
        job_dir = self.root / job_id
        status_path = job_dir / self.STATUS_FILENAME
        if status_path.exists():
            try:
                data = json.loads(status_path.read_text(encoding="utf-8"))
                job = JobStatus.from_dict(data)
                self._jobs[job.id] = job
            except (json.JSONDecodeError, OSError, KeyError, ValueError):
                # If there's an error reading, keep the existing version
                pass

    def _hydrate_existing(self) -> None:
        for child in self.root.iterdir():
            if not child.is_dir():
                continue
            status_path = child / self.STATUS_FILENAME
            if status_path.exists():
                try:
                    data = json.loads(status_path.read_text(encoding="utf-8"))
                    job = JobStatus.from_dict(data)
                    self._jobs[job.id] = job
                except (json.JSONDecodeError, OSError, KeyError, ValueError):
                    continue

    def _persist(self, job: JobStatus) -> None:
        job_dir = self.root / job.id
        job_dir.mkdir(parents=True, exist_ok=True)
        status_path = job_dir / self.STATUS_FILENAME
        status_path.write_text(json.dumps(job.to_dict(), indent=2), encoding="utf-8")

