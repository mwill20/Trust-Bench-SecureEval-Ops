"""Simple health and readiness endpoints for operational probes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Basic liveness indicator."""

    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> dict[str, bool]:
    """Readiness indicator (no dependencies to check yet)."""

    return {"ready": True}


__all__ = ["router", "healthz", "readyz"]
