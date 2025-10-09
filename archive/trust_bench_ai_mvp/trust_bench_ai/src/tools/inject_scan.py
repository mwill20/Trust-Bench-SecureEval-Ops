\
from typing import Dict, List
from ..security_utils import PROMPT_INJECTION_PATTERNS, DANGEROUS_COMMANDS, find_patterns

def score_injection(text: str) -> Dict:
    hits = find_patterns(text, PROMPT_INJECTION_PATTERNS)
    score = min(100, len(hits) * 20)  # crude: 5 hits → 100
    return {"score": score, "hits": hits}

def find_dangerous_commands(text: str) -> List[Dict]:
    return find_patterns(text, DANGEROUS_COMMANDS)
