"""Groq provider helper for TrustBench agents.

The implementation is designed to work in two modes:

1. Real mode (default) — uses the official `groq` SDK and requires
   `GROQ_API_KEY` plus an accessible model name.
2. Fake mode (set `TRUSTBENCH_FAKE_PROVIDER=1`) — returns deterministic
   stub responses so local tests can execute without external calls.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
import threading


try:
    import groq  # type: ignore

    _GROQ_AVAILABLE = True
except Exception:  # pragma: no cover - import error handled gracefully
    groq = None  # type: ignore
    _GROQ_AVAILABLE = False


class GroqProviderError(RuntimeError):

DEFAULT_MAX_CONCURRENCY = int(os.getenv("GROQ_MAX_CONCURRENCY", "4"))
DEFAULT_RETRIES = int(os.getenv("GROQ_RETRIES", "2"))
DEFAULT_RETRY_BACKOFF = float(os.getenv("GROQ_RETRY_BACKOFF", "0.5"))



@dataclass
class GroqConfig:
    api_key: str
    model: str
    temperature: float = 0.0
    max_output_tokens: int = 512
    timeout: float = 60.0


class GroqProvider:
    _semaphore = threading.BoundedSemaphore(DEFAULT_MAX_CONCURRENCY)
    """Thin wrapper around the Groq SDK with JSON helpers."""

    def __init__(self, cfg: GroqConfig, *, fake: bool = False):
        self.cfg = cfg
        self.fake = fake or bool(int(os.getenv("TRUSTBENCH_FAKE_PROVIDER", "0")))
        self._client = None

    @classmethod
    def from_env(cls, model: Optional[str] = None) -> "GroqProvider":
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key and not os.getenv("TRUSTBENCH_FAKE_PROVIDER"):
            raise GroqProviderError(
                "GROQ_API_KEY not set. Provide a key or enable fake provider via TRUSTBENCH_FAKE_PROVIDER=1."
            )
        cfg = GroqConfig(
            api_key=api_key,
            model=(model or os.getenv("GROQ_MODEL") or "llama-3.1-70b-versatile"),
            temperature=float(os.getenv("GROQ_TEMPERATURE", "0.0")),
            max_output_tokens=int(os.getenv("GROQ_MAX_TOKENS", "512")),
            timeout=float(os.getenv("GROQ_TIMEOUT", "60")),
        )
        fake = bool(int(os.getenv("TRUSTBENCH_FAKE_PROVIDER", "0")))
        return cls(cfg, fake=fake)

    # -- private helpers -------------------------------------------------
    def _ensure_client(self) -> "groq.Groq":  # type: ignore[name-defined]
        if self.fake:
            return None  # type: ignore[return-value]
        if not _GROQ_AVAILABLE:
            raise GroqProviderError(
                "groq package not installed. `pip install groq` or enable fake provider."
            )
        if self._client is None:
            self._client = groq.Groq(api_key=self.cfg.api_key)  # type: ignore[attr-defined]
        return self._client  # type: ignore[return-value]

    # -- public API ------------------------------------------------------
    def completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Return completion text and latency metadata."""
        temperature = kwargs.get("temperature", self.cfg.temperature)
        max_tokens = kwargs.get("max_output_tokens", self.cfg.max_output_tokens)

        if self.fake:
            start = time.time()
            time.sleep(0.01)  # simulate network latency
            text = self._fake_completion(prompt)
            return {"text": text, "latency": time.time() - start, "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(text.split())}}

        attempt = 0
        last_exc: Exception | None = None
        while attempt <= DEFAULT_RETRIES:
            attempt += 1
            self._semaphore.acquire()
            try:
                client = self._ensure_client()
                start = time.time()
                response = client.chat.completions.create(  # type: ignore[attr-defined]
                    model=self.cfg.model,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": "You are a precise assistant for TrustBench evaluations."},
                        {"role": "user", "content": prompt},
                    ],
                    timeout=self.cfg.timeout,
                )
                latency = time.time() - start
                message = response.choices[0].message
                completion_text = message.content if isinstance(message.content, str) else message.content[0].text  # type: ignore[index]
                usage = getattr(response, "usage", None)
                return {"text": completion_text, "latency": latency, "usage": dict(usage) if usage else {}}
            except Exception as exc:  # pragma: no cover - network failures
                last_exc = exc
                time.sleep(DEFAULT_RETRY_BACKOFF * attempt)
            finally:
                self._semaphore.release()
        raise GroqProviderError(f"Groq completion failed after retries: {last_exc}")

    def llm_json(self, prompt: str, *, max_retries: int = 2, **kwargs: Any) -> Dict[str, Any]:
        """Request a JSON response from the LLM, retrying if parsing fails."""
        last_error: Optional[Exception] = None
        for _ in range(max_retries):
            raw = self.completion(prompt, **kwargs)["text"]
            try:
                return json.loads(self._extract_json(raw))
            except Exception as exc:  # pragma: no cover - exercised in fallback loops
                last_error = exc
        raise GroqProviderError(f"Failed to decode JSON response: {last_error}")

    # -- fake helpers ----------------------------------------------------
    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found in response: {text!r}")
        return text[start : end + 1]

    @staticmethod
    def _fake_completion(prompt: str) -> str:
        """Deterministic stub for tests."""
        if "refuse" in prompt.lower():
            return '{"refusal_correct": true, "rationale": "Stub refusal"}'
        if "latency-probe" in prompt.lower():
            return "OK"
        # simple echo for QA
        return "This is a stubbed response for testing purposes."
