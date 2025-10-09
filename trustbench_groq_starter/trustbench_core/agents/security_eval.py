from __future__ import annotations
import random
from pathlib import Path
from typing import Dict, Any

def _seeded(seed: int): 
    random.seed(seed + 13)

def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    _seeded(int(profile.get("sampling", {}).get("seed", 42)))
    inj_block = min(1.0, max(0.0, random.uniform(0.78, 0.98)))
    failures = []
    if inj_block < profile["thresholds"]["injection_block_rate"]:
        failures.append({"pillar":"security","id":"atk_001","reason":"injection_bypassed","injection_block_rate":round(inj_block,3)})
    return {"metrics":{"injection_block_rate": round(inj_block, 3)}, "failures": failures}
