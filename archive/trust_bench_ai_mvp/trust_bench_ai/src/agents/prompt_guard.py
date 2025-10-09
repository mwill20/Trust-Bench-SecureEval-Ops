\
from typing import Dict, List
from ..tools import inject_scan

DOC_EXTS = {".md", ".markdown", ".txt"}

def prompt_guard(state: Dict) -> Dict:
    files: List[Dict] = state.get("files", [])
    findings = []
    for f in files:
        path = f["path"]
        if any(path.lower().endswith(ext) for ext in DOC_EXTS):
            res = inject_scan.score_injection(f["text"])
            if res["score"] > 0:
                findings.append({
                    "agent": "PromptGuard",
                    "path": path,
                    "score": res["score"],
                    "hits": res["hits"],
                })
    state.setdefault("findings", []).extend(findings)
    return state
