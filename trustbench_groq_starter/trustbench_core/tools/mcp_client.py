from typing import Dict, Any, List

def discover() -> List[str]:
    return ["scan_repo", "secrets_scan", "semgrep_rules", "vt_lookup", "ragas_eval", "prompt_guard"]

def call(tool_name: str, **kwargs) -> Dict[str, Any]:
    return {"tool": tool_name, "ok": True, "kwargs": kwargs}
