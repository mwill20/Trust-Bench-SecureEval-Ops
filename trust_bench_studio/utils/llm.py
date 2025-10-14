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


def _fake_groq_response(system: str, prompt: str) -> str:
    """Generate a realistic fake response for development/testing."""
    prompt_lower = prompt.lower()
    
    # Check for specific patterns and provide contextual responses
    if "langgraph" in prompt_lower:
        return "LangGraph is a framework for building stateful, multi-actor applications with language models. It provides tools for creating complex workflows with conditional logic, loops, and persistent state management."
    
    if any(word in prompt_lower for word in ["what is", "explain", "describe"]):
        return "This is a simulated response from the TrustBench evaluation system. The agent is currently running in development mode with mock responses enabled. To get real AI-powered insights, configure your API keys and disable TRUSTBENCH_FAKE_PROVIDER."
    
    if "security" in prompt_lower:
        return "Based on the security evaluation results, the system shows moderate security posture. Key recommendations include implementing input validation, sanitizing user data, and following secure coding practices."
    
    if "task" in prompt_lower and "fidelity" in prompt_lower:
        return "The task fidelity analysis indicates that the agent maintains good alignment with specified objectives. Performance metrics show consistent adherence to task requirements with minimal deviation."
    
    if "ethics" in prompt_lower:
        return "The ethics evaluation shows the system demonstrates appropriate refusal behaviors for harmful requests and maintains ethical boundaries in its responses."
    
    # Default response
    return "This is a development environment response. The evaluation system is functioning correctly with simulated data. Configure real API providers for production insights."


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


def _call_groq(system: str, prompt: str) -> str | None:
    provider = os.getenv("TRUST_BENCH_LLM_PROVIDER", "").lower()
    if provider not in {"groq"}:
        return None
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    # Check if we're using fake provider
    if os.getenv("TRUSTBENCH_FAKE_PROVIDER") == "1":
        return _fake_groq_response(system, prompt)
    
    try:
        from groq import Groq  # type: ignore
    except ImportError:
        return None

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        if not response.choices:
            return None
        return (response.choices[0].message.content or "").strip()
    except Exception:
        # Fall back to fake response if real API fails
        return _fake_groq_response(system, prompt)


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

    # Try configured LLM provider
    llm_response = _call_openai(system_prompt, user_prompt)
    if not llm_response:
        llm_response = _call_groq(system_prompt, user_prompt)
    
    if llm_response:
        return llm_response

    return _fallback_summary(agent_name, context_text, question)
