from typing import List, Dict, Any
import os, json

try:
    from groq import Groq
except Exception:
    Groq = None

_client = None
def _get_client():
    global _client
    if _client is None and Groq is not None and os.getenv("GROQ_API_KEY"):
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def llm_complete(messages: List[Dict[str, str]], model: str | None = None, **kwargs) -> str:
    client = _get_client()
    if client is None:
        return "SIMULATED_OUTPUT"
    model = model or os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=kwargs.get("temperature", 0.2),
        max_tokens=kwargs.get("max_tokens", 800),
        stream=False,
    )
    return resp.choices[0].message.content or ""

def llm_json(messages: List[Dict[str, str]], schema_hint: str, **kwargs) -> Dict[str, Any]:
    sys = {
        "role": "system",
        "content": (
            "Return ONLY a compact JSON object. No prose. "
            f"Schema (informal): {schema_hint}"
        ),
    }
    out = llm_complete([sys] + messages, **kwargs).strip()
    out = out.split("```")[-1] if "```" in out else out
    try:
        return json.loads(out)
    except Exception:
        s, e = out.find("{"), out.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(out[s : e + 1])
            except Exception:
                pass
        return {"_raw": out, "_error": "non_json"}
