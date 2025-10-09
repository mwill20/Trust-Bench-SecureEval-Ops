from __future__ import annotations
import random
from pathlib import Path
from typing import Dict, Any

def _seeded(seed: int): 
    random.seed(seed + 29)

def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    _seeded(int(profile.get("sampling", {}).get("seed", 42)))
    samples = [random.uniform(0.8, 3.2) for _ in range(30)]
    samples.sort()
    idx = int(0.95 * (len(samples)-1))
    p95 = samples[idx]
    failures = []
    if p95 > profile["thresholds"]["p95_latency"]:
        failures.append({"pillar":"system","id":"latency","reason":"p95_above_threshold","p95_latency":round(p95,3)})
    return {"metrics":{"p95_latency": round(p95, 3)}, "failures": failures}
