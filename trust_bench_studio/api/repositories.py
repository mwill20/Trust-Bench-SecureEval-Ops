"""API endpoints for repository ingestion job management."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl, field_validator

from trust_bench_studio.services import JobManager, JobStatus

router = APIRouter()


class AnalyzeRepositoryRequest(BaseModel):
    repo_url: HttpUrl = Field(..., description="GitHub repository URL to analyze")
    profile: Optional[str] = Field(default=None, description="Optional evaluation profile id", max_length=64)

    @field_validator("repo_url")
    @classmethod
    def _ensure_github(cls, value: HttpUrl) -> HttpUrl:
        if not str(value).startswith("https://github.com/"):
            raise ValueError("Repository URL must start with https://github.com/")
        return value


def _serialize_job(job: JobStatus) -> Dict[str, Any]:
    payload = job.to_dict()
    # Maintain a predictable order for client rendering
    ordered = {
        "id": payload["id"],
        "repo_url": payload["repo_url"],
        "state": payload["state"],
        "stage": payload["stage"],
        "progress": payload["progress"],
        "message": payload["message"],
        "profile": payload.get("profile"),
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
        "error": payload.get("error"),
        "artifacts": payload.get("artifacts", {}),
        "metadata": payload.get("metadata", {}),
    }
    return ordered


job_manager = JobManager()


@router.post("/analyze")
def analyze_repository(request: AnalyzeRepositoryRequest) -> Dict[str, Any]:
    repo_url = str(request.repo_url).rstrip("/")
    job = job_manager.enqueue(
        repo_url,
        profile=request.profile,
        metadata={"requested_profile": request.profile} if request.profile else None,
    )
    return {"job": _serialize_job(job)}


@router.get("/{job_id}/status")
def get_repository_status(job_id: str) -> Dict[str, Any]:
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {"job": _serialize_job(job)}
