"""OpenAI provider helper for TrustBench agents."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    _OPENAI_AVAILABLE = False


class OpenAIProviderError(RuntimeError):
    """Generic provider failure."""
    pass


@dataclass
class OpenAIConfig:
    api_key: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 512
    timeout: float = 60.0


class OpenAIProvider:
    """Thin wrapper around the OpenAI SDK with JSON helpers."""

    def __init__(self, config: OpenAIConfig):
        if not _OPENAI_AVAILABLE:
            raise OpenAIProviderError("openai package not installed. Run: pip install openai")
        
        self.config = config
        self.client = OpenAI(api_key=config.api_key, timeout=config.timeout)

    @classmethod
    def from_env(cls, model: str = "") -> "OpenAIProvider":
        """Construct from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise OpenAIProviderError("OPENAI_API_KEY not set.")
        
        model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        config = OpenAIConfig(
            api_key=api_key,
            model=model_name,
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "512")),
            timeout=float(os.getenv("OPENAI_TIMEOUT", "60.0")),
        )
        return cls(config)

    def completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate a completion for the given prompt."""
        start = time.perf_counter()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )
            
            elapsed = time.perf_counter() - start
            text = response.choices[0].message.content or ""
            
            return {
                "text": text.strip(),
                "latency": elapsed,
                "model": self.config.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as exc:
            raise OpenAIProviderError(f"OpenAI completion failed: {exc}") from exc

    def json_completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate a JSON-formatted completion."""
        result = self.completion(prompt, **kwargs)
        
        try:
            import json
            parsed = json.loads(result["text"])
            return {**result, "parsed": parsed}
        except Exception as exc:
            raise OpenAIProviderError(f"Failed to parse JSON response: {exc}") from exc
