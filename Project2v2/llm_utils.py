"""Lightweight helpers for calling different LLM chat providers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

try:
    from .core.settings import settings
except ImportError:
    from core.settings import settings


class LLMError(RuntimeError):
    """Raised when an upstream LLM provider request fails."""


@dataclass
class ProviderConfig:
    name: str
    api_key_var: str
    default_model: str


_PROVIDERS: Dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        name="openai",
        api_key_var="OPENAI_API_KEY",
        default_model="gpt-4o-mini",
    ),
    "groq": ProviderConfig(
        name="groq",
        api_key_var="GROQ_API_KEY",
        default_model="llama-3.1-8b-instant",
    ),
    "gemini": ProviderConfig(
        name="gemini",
        api_key_var="GEMINI_API_KEY",
        default_model="gemini-1.5-flash",
    ),
}


def _ensure_api_key(provider: ProviderConfig, api_key_override: Optional[str] = None) -> str:
    if api_key_override:
        return api_key_override
    api_key = settings.get_api_key_for_provider(provider.name)
    if not api_key:
        raise LLMError(
            f"{provider.name.title()} API key missing. "
            f"Set the '{provider.api_key_var}' environment variable or provide it in the UI."
        )
    return api_key


def _build_prompt(question: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Combine question and optional context into a single prompt string."""
    prompt_sections = []

    if context:
        report = context.get("report")
        if report:
            prompt_sections.append(
                "Latest audit report:\n"
                f"{json.dumps(report, indent=2)}"
            )

        messages = context.get("messages")
        if messages:
            formatted_messages = []
            for message in messages:
                sender = message.get("sender", "Unknown")
                recipient = message.get("recipient", "Unknown")
                content = message.get("content", "")
                formatted_messages.append(f"{sender} -> {recipient}: {content}")

            prompt_sections.append(
                "Recent agent messages:\n" + "\n".join(formatted_messages)
            )

    prompt_sections.append(f"User question:\n{question.strip()}")
    prompt_sections.append(
        "Provide a concise, factual answer based on the available context."
    )

    return "\n\n".join(prompt_sections).strip()


def _call_openai(prompt: str, api_key_override: Optional[str] = None) -> str:
    provider = _PROVIDERS["openai"]
    api_key = _ensure_api_key(provider, api_key_override)
    model = provider.default_model  # Using default model from provider config

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that answers questions about "
                        "Trust Bench audit outputs."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )

    if response.status_code >= 400:
        raise LLMError(
            f"OpenAI request failed ({response.status_code}): {response.text}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(
            f"OpenAI response missing message content: {json.dumps(data)}"
        ) from exc


def _call_groq(prompt: str, api_key_override: Optional[str] = None) -> str:
    provider = _PROVIDERS["groq"]
    api_key = _ensure_api_key(provider, api_key_override)
    model = provider.default_model  # Using default model from provider config

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You help users understand Trust Bench audit findings. "
                        "Use the provided context."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )

    if response.status_code >= 400:
        raise LLMError(
            f"Groq request failed ({response.status_code}): {response.text}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(
            f"Groq response missing message content: {json.dumps(data)}"
        ) from exc


def _call_gemini(prompt: str, api_key_override: Optional[str] = None) -> str:
    provider = _PROVIDERS["gemini"]
    api_key = _ensure_api_key(provider, api_key_override)
    model = provider.default_model  # Using default model from provider config

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [
                {"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            ],
        },
        timeout=30,
    )

    if response.status_code >= 400:
        raise LLMError(
            f"Gemini request failed ({response.status_code}): {response.text}"
        )

    data = response.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text_parts = [part.get("text", "") for part in parts]
        return "\n".join(filter(None, text_parts)).strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(
            f"Gemini response missing text content: {json.dumps(data)}"
        ) from exc


_CALLERS = {
    "openai": _call_openai,
    "groq": _call_groq,
    "gemini": _call_gemini,
}


def chat_with_llm(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    provider_override: Optional[str] = None,
    api_key_override: Optional[str] = None,
) -> Dict[str, str]:
    """Send a chat completion request to the selected provider."""
    if not question.strip():
        raise LLMError("Question is empty.")

    provider_key = (provider_override or settings.llm_provider).lower()
    if provider_key not in _CALLERS:
        raise LLMError(
            f"Unsupported provider '{provider_key}'. "
            f"Supported providers: {', '.join(_CALLERS.keys())}."
        )

    prompt = _build_prompt(question, context)
    answer = _CALLERS[provider_key](prompt, api_key_override=api_key_override)

    return {
        "provider": provider_key,
        "answer": answer,
    }


def test_provider_credentials(provider: str, api_key: str) -> Dict[str, str]:
    """Send a lightweight prompt to verify that a provider API key works."""
    provider_key = (provider or "").lower()
    if provider_key not in _CALLERS:
        raise LLMError(
            f"Unsupported provider '{provider}'. "
            f"Supported providers: {', '.join(_CALLERS.keys())}."
        )
    if not api_key:
        raise LLMError("API key is required to test the connection.")

    answer = _CALLERS[provider_key](
        "Connection test: respond with OK.",
        api_key_override=api_key,
    )
    return {
        "provider": provider_key,
        "answer": answer,
    }


__all__ = ["chat_with_llm", "LLMError", "test_provider_credentials"]
