"""Utility helpers for profile/env resolution."""

from __future__ import annotations

import os


def resolve_model(value: str | None, default: str = "llama-3.1-70b-versatile") -> str:
    """Resolve `${VAR:-fallback}` style strings used in profile YAML."""
    if not value:
        return os.getenv("GROQ_MODEL", default)
    if value.startswith("${") and value.endswith("}"):
        body = value[2:-1]
        if ":-" in body:
            key, fallback = body.split(":-", 1)
            return os.getenv(key, fallback)
        return os.getenv(body, default)
    return value
