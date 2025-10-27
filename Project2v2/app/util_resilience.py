"""Resilience utilities: retry logic and execution timeouts."""

from __future__ import annotations

import functools
import threading
import time
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def retry(max_tries: int = 3, backoff: float = 0.5):
    """Retry decorator with exponential backoff."""

    if max_tries < 1:
        raise ValueError("max_tries must be >= 1")

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(max_tries):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - deliberate surface for retries
                    last_exc = exc
                    if attempt == max_tries - 1:
                        raise
                    sleep_for = backoff * (2**attempt)
                    time.sleep(sleep_for)
            if last_exc is not None:
                raise last_exc
        return cast(F, wrapper)

    return decorator


def with_timeout(seconds: int):
    """Timeout decorator using worker threads for portability."""

    if seconds <= 0:
        raise ValueError("seconds must be positive")

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result_holder: dict[str, Any] = {}
            error_holder: dict[str, Exception] = {}
            finished = threading.Event()

            def target() -> None:
                try:
                    result_holder["value"] = fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - captured for re-raise
                    error_holder["error"] = exc
                finally:
                    finished.set()

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            completed = finished.wait(seconds)
            if not completed:
                raise TimeoutError(f"Operation timed out after {seconds} seconds")

            if "error" in error_holder:
                raise error_holder["error"]
            return result_holder.get("value")

        return cast(F, wrapper)

    return decorator
