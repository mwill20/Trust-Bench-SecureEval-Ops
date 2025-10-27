"""Input validation and output guardrails for SecureEval."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator

SAFE_OUTPUT_MAXLEN = 10_000


class RepoInput(BaseModel):
    """Validated payload for repository audits."""

    repo_url: Optional[HttpUrl] = None
    repo_path: Optional[str] = None
    scan: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _ensure_location(cls, values: "RepoInput") -> "RepoInput":  # type: ignore[override]
        if not values.repo_url and not values.repo_path:
            raise ValueError("either repo_url or repo_path must be provided")
        return values

    def path(self) -> Optional[Path]:
        if self.repo_path:
            return Path(self.repo_path)
        return None


def validate_repo_input(payload: dict) -> RepoInput:
    """Strictly validate inbound payloads for audit requests."""

    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    return RepoInput(**payload)


def clamp_output(text: str | None) -> str:
    """Clamp outbound text to a safe maximum length."""

    if not text:
        return ""
    if len(text) <= SAFE_OUTPUT_MAXLEN:
        return text
    return text[:SAFE_OUTPUT_MAXLEN]
