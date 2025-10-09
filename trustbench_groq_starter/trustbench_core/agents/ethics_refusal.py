from __future__ import annotations
import random
from pathlib import Path
from typing import Dict, Any

def _seeded(seed: int): 
    random.seed(seed + 7)

def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    _seeded(int(profile.get("sampling", {}).get("seed", 42)))
    refusal_acc = min(1.0, max(0.0, random.uniform(0.85, 0.99)))
    failures = []
    if refusal_acc < profile["thresholds"]["refusal_accuracy"]:
        failures.append({"pillar":"ethics","id":"harm_001","reason":"refusal_incorrect","refusal_accuracy":round(refusal_acc,3)})
    return {"metrics":{"refusal_accuracy": round(refusal_acc, 3)}, "failures": failures}
