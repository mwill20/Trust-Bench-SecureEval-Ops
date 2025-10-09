\
from typing import Dict, List
from ..security_utils import RISKY_CODE_PATTERNS, find_patterns
from ..tools import semgrep_tool, cmd_classifier

CODE_EXTS = {".py", ".sh", ".js", ".ts", ".json", ".yml", ".yaml"}

def code_guard(state: Dict) -> Dict:
    files: List[Dict] = state.get("files", [])
    findings = []
    code_paths = []
    for f in files:
        path = f["path"]
        if any(path.lower().endswith(ext) for ext in CODE_EXTS):
            code_paths.append(path)
            # Heuristic risky code matches
            hits = find_patterns(f["text"], RISKY_CODE_PATTERNS)
            if hits:
                findings.append({
                    "agent": "CodeGuard",
                    "path": path,
                    "score": min(100, len(hits) * 15),
                    "hits": hits,
                })
            # Command classifier tagging (embedded shell snippets)
            label = cmd_classifier.dangerous_command_label(f["text"]);
            if label:
                findings.append({
                    "agent": "CodeGuard",
                    "path": path,
                    "score": 50,
                    "hits": [{"desc": "Dangerous command suggestion", "snippet": label}],
                })
    # Optional semgrep
    sfind = semgrep_tool.run_semgrep(code_paths) if code_paths else []
    for sf in sfind:
        findings.append({
            "agent": "CodeGuard",
            "path": sf["path"],
            "score": 40,
            "hits": [{"desc": f"Semgrep: {sf['message']}", "snippet": f"{sf['severity']}"}],
        })
    state.setdefault("findings", []).extend(findings)
    return state
