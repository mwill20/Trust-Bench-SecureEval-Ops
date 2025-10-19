"""
Utility helpers for basic input validation, sanitization, and escaping.

These functions centralise security-related logic so backend routes (and any
future callers) can opt-in via the `ENABLE_SECURITY_FILTERS` environment
variable.  The helpers are intentionally lightweight so they can be expanded
incrementally as new hardening requirements emerge.
"""

from __future__ import annotations

import html
import os
import re
from typing import Optional
from urllib.parse import urlparse


def security_filters_enabled() -> bool:
    """Return True when security helpers should actively enforce checks."""
    flag = os.getenv("ENABLE_SECURITY_FILTERS", "true").strip().lower()
    return flag not in {"0", "false", "no", "off"}


def normalize_text(value: Optional[str]) -> str:
    """Return a trimmed string representation of user-provided text."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    return str(value).strip()


class ValidationError(ValueError):
    """Raised when input validation fails."""


_REPO_REGEX = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(/.*)?$")


def validate_repo_url(raw_url: str) -> str:
    """
    Ensure the provided repository URL targets GitHub and contains owner/repo.

    Returns a normalized HTTPS URL when valid, otherwise raises ValidationError.
    """
    value = normalize_text(raw_url)
    if not value:
        raise ValidationError("Repository URL is required.")

    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"}:
        raise ValidationError("Repository URL must include http(s) scheme.")
    if parsed.hostname not in {"github.com", "www.github.com"}:
        raise ValidationError("Only github.com repositories are supported.")
    if not _REPO_REGEX.match(parsed.path or ""):
        raise ValidationError("Repository URL must include owner and repository name.")

    # Normalize to https://github.com/owner/repo(...optional path)
    normalized_path = "/".join(part for part in parsed.path.split("/") if part)
    normalized_url = f"https://github.com/{normalized_path}"
    return normalized_url


def sanitize_prompt(text: str, max_length: int = 4000) -> str:
    """
    Basic prompt sanitization to reduce prompt injection patterns.

    Currently removes control characters and truncates to max_length.
    """
    value = normalize_text(text)
    # Remove ASCII control chars except newlines/tabs.
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    if len(value) > max_length:
        value = value[:max_length]
    return value


def escape_html(text: str) -> str:
    """Escape HTML entities for safe rendering in templates."""
    return html.escape(normalize_text(text))


def safe_log_message(message: str, max_length: int = 500) -> str:
    """
    Prepare a string for logging by stripping control characters and truncating.
    """
    cleaned = sanitize_prompt(message, max_length=max_length)
    return cleaned


__all__ = [
    "security_filters_enabled",
    "normalize_text",
    "ValidationError",
    "validate_repo_url",
    "sanitize_prompt",
    "escape_html",
    "safe_log_message",
]

