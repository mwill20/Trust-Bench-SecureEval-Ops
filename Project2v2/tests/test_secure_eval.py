"""Tests for SecureEval layer primitives."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from app.security.guardrails import SAFE_OUTPUT_MAXLEN, clamp_output, validate_repo_input
from app.security.sandbox import safe_run
from app.util_resilience import retry, with_timeout


def test_validate_repo_input_accepts_url_and_path():
    payload = {
        "repo_url": "https://github.com/example/repo",
        "scan": ["secrets"],
    }
    validated = validate_repo_input(payload)
    assert str(validated.repo_url) == payload["repo_url"]

    payload_path = {
        "repo_path": str(Path.cwd()),
    }
    validated_path = validate_repo_input(payload_path)
    assert validated_path.path().exists()


def test_validate_repo_input_requires_location():
    with pytest.raises(ValueError):
        validate_repo_input({})


def test_clamp_output_truncates():
    text = "x" * (SAFE_OUTPUT_MAXLEN + 100)
    truncated = clamp_output(text)
    assert len(truncated) == SAFE_OUTPUT_MAXLEN
    assert truncated == text[:SAFE_OUTPUT_MAXLEN]

    assert clamp_output("hello") == "hello"
    assert clamp_output(None) == ""


def test_safe_run_allows_and_blocks_commands():
    code = "print(\"ok\")"
    rc, stdout, stderr = safe_run(["python", "-c", code])
    assert rc == 0
    assert stdout.strip() == "ok"
    assert not stderr

    rc, stdout, stderr = safe_run("echo denied")
    assert rc == 126
    assert stdout == ""
    assert "not allowed" in stderr


def test_retry_and_timeout_behaviour():
    calls = {"count": 0}

    @retry(max_tries=3, backoff=0)
    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("boom")
        return "success"

    assert flaky() == "success"
    assert calls["count"] == 3

    @with_timeout(1)
    def slow() -> None:
        time.sleep(2)

    with pytest.raises(TimeoutError):
        slow()
