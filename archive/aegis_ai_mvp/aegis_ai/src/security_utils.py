\
import re
from typing import List, Dict, Tuple

# --- Prompt injection indicators (basic starter set) ---
PROMPT_INJECTION_PATTERNS: List[Tuple[str, str]] = [
    (r"\bignore (?:the )?(?:previous|above)\b", "Role override: ignore instructions"),
    (r"\bdisregard (?:all|any) (?:rules|instructions)\b", "Role override: disregard rules"),
    (r"\bsystem\s*:\b", "System role leakage in user content"),
    (r"\breveal (?:your )?(?:memory|secrets|keys|api key)\b", "Data exfiltration request"),
    (r"\bexfiltrat(?:e|ion)\b", "Data exfiltration"),
    (r"\bbase64:?[A-Za-z0-9+/=]{16,}\b", "Obfuscation: base64‑looking string"),
    (r"\\u200b|\\u200c|\\u200d", "Obfuscation: zero‑width characters (escaped)"),
    (r"[^\x00-\x7F]", "Obfuscation: non‑ASCII (potential homoglyphs)"),
]

# --- Risky command patterns ---
DANGEROUS_COMMANDS: List[Tuple[str, str]] = [
    (r"\brm\s+-rf\s+/", "Dangerous: rm -rf /"),
    (r"\brm\s+-rf\b", "Dangerous: rm -rf"),
    (r"\bcurl\b.*\|\s*(bash|sh)\b", "Dangerous: curl | bash"),
    (r"\bwget\b.*\|\s*(bash|sh)\b", "Dangerous: wget | bash"),
    (r"\bchmod\s+777\b", "Dangerous: chmod 777"),
    (r"\bInvoke-Expression\b", "Dangerous: Invoke-Expression (PowerShell)"),
]

# --- Risky code patterns ---
RISKY_CODE_PATTERNS: List[Tuple[str, str]] = [
    (r"\beval\(", "Use of eval()"),
    (r"\bexec\(", "Use of exec()"),
    (r"\bpickle\.loads?\(", "Unsafe deserialization: pickle"),
    (r"\byaml\.load\(", "Unsafe YAML load (use safe_load)"),
    (r"\bsubprocess\.Popen\([^)]*(shell\s*=\s*True)[^)]*\)", "subprocess with shell=True"),
    (r"\bhashlib\.md5\(", "Weak crypto: MD5"),
    (r"\bhashlib\.sha1\(", "Weak crypto: SHA1"),
]

ALLOWLIST_EXTS = {".md", ".markdown", ".txt", ".py", ".sh", ".js", ".ts", ".json", ".yml", ".yaml"}

def redact(s: str) -> str:
    # Very naive key redaction
    s = re.sub(r"(api[_-]?key\s*[:=]\s*)([A-Za-z0-9_\-]{6,})", r"\1***REDACTED***", s, flags=re.I)
    return s

def find_patterns(text: str, patterns: List[Tuple[str, str]]) -> List[Dict]:
    findings = []
    for pat, desc in patterns:
        for m in re.finditer(pat, text, flags=re.I | re.M):
            span = m.span()
            snippet = text[max(0, span[0]-60): min(len(text), span[1]+60)]
            findings.append({"desc": desc, "span": span, "snippet": snippet})
    return findings
