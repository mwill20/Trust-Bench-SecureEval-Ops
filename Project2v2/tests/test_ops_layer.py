"""Tests for Phase 2 Ops Layer utilities."""

from __future__ import annotations

import json
from io import StringIO
from typing import Iterable

import pytest
from fastapi.testclient import TestClient

from Project2v2.app.health import router
from Project2v2.app.logging import configure_logging


@pytest.fixture
def configured_logger():
    buffer = StringIO()
    adapter = configure_logging(level="DEBUG", run_id="test-run", stream=buffer)
    buffer.truncate(0)
    buffer.seek(0)
    return adapter, buffer


def _parse_logs(raw: str):
    return [json.loads(line) for line in raw.splitlines() if line]


def test_json_log_format(configured_logger):
    logger, buffer = configured_logger
    logger.info("system ready")
    entries = _parse_logs(buffer.getvalue())
    assert entries, "expected log entries"
    record = entries[-1]
    assert record["msg"] == "system ready"
    assert record["level"] == "INFO"
    assert record["run_id"] == "test-run"
    assert record["ts"].endswith("Z")


def test_run_id_generated_when_missing():
    buffer = StringIO()
    adapter = configure_logging(level="INFO", stream=buffer)
    buffer.truncate(0)
    buffer.seek(0)
    adapter.warning("missing run id checks")
    entries = _parse_logs(buffer.getvalue())
    assert entries[-1]["run_id"] != "N/A"


def test_health_endpoints():
    client = TestClient(router)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json() == {"ready": True}
