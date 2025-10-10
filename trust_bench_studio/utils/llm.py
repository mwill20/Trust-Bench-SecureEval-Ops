"""LLM helper utilities with safe fallbacks."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

PROMPT_GUARDRAILS = [
    "ignore previous instructions",
    "run shell command",
    "rm -rf",
    "sudo ",
    "upload secrets",
    "read file",
    "exfiltrate",
]


def _is_safe(question: str) -> bool:
    lowered = question.lower()
    return not any(marker in lowered for marker in PROMPT_GUARDRAILS)


def _truncate_context(context: Dict[str, Any], limit: int = 2000) -> str:
    serialized = json.dumps(context, ensure_ascii=False, default=str)
    if len(serialized) <= limit:
        return serialized
    return serialized[: limit - 3] + "..."


def _call_openai(system: str, prompt: str) -> str | None:
    provider = os.getenv("TRUST_BENCH_LLM_PROVIDER", "").lower()
    if provider not in {"openai", "gpt"}:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        return None

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )
    except Exception:
        return None

    if not response.choices:
        return None
    return (response.choices[0].message.content or "").strip()


def _fallback_summary(agent_name: str, context_text: str, question: str) -> str:
    lines = [f"{agent_name} (offline explainer):"]
    if context_text:
        lines.append("Key context snapshot:")
        for chunk in context_text.splitlines():
            if chunk.strip():
                lines.append(f"  - {chunk.strip()}")
            if len(lines) > 8:
                break
    lines.append("")
    lines.append(
        "LLM integration is not configured. Configure TRUST_BENCH_LLM_PROVIDER and API keys to enable richer explanations."
    )
    lines.append(f"Your question: {question}")
    return "\n".join(lines)


def explain(
    agent_name: str,
    context_json: Dict[str, Any],
    question: str,
    system_seed: Optional[str] = None,
) -> str:
    """Provide a guarded explanation using the configured LLM or a fallback."""
    question = question.strip()
    if not question:
        return "Please provide a question for the agent to answer."
    if not _is_safe(question):
        return (
            "The agent declined to answer because the request contained potentially unsafe instructions. "
            "Please rephrase with a focus on evaluation insights or mitigations."
        )

    context_text = _truncate_context(context_json)
    base_prompt = (
        f"You are the {agent_name} explaining evaluation results. "
        "Stay concise, emphasize safety-first recommendations, and never provide system commands."
    )
    if system_seed:
        system_prompt = "\n\n".join([system_seed.strip(), base_prompt]).strip()
    else:
        system_prompt = base_prompt

    user_prompt = (
        "Context (redacted JSON):\n"
        f"{context_text}\n\n"
        "Question:\n"
        f"{question}"
    )

    llm_response = _call_openai(system_prompt, user_prompt)
    if llm_response:
        return llm_response

    return _fallback_summary(agent_name, context_text, question)
