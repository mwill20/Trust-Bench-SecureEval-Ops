"""JSON logging utilities for SecureEval operational visibility."""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Format log records as JSON lines suitable for aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "run_id": getattr(record, "run_id", "N/A"),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", *, run_id: Optional[str] = None, stream=None) -> logging.LoggerAdapter:
    """Configure root logger with JSON formatter and return an adapter."""

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    adapter = logging.LoggerAdapter(root, {"run_id": run_id or str(uuid.uuid4())})
    adapter.debug("Logging configured", extra={"run_id": adapter.extra["run_id"]})
    return adapter


__all__ = ["configure_logging", "JsonFormatter"]
