from __future__ import annotations
import os, random, json
from pathlib import Path
from typing import Dict, Any, List

def _seeded(seed: int): 
    random.seed(seed)

def _judge_faithfulness(inputs: List[str], truths: List[str]) -> float:
    matches = 0
    for i, t in zip(inputs, truths):
        i_words = set(i.lower().split())
        t_words = set(t.lower().split())
        if len(i_words & t_words) > 1:
            matches += 1
    return matches / max(1, len(truths))

def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    seed = int(profile.get("sampling", {}).get("seed", 42))
    _seeded(seed)

    golden_path = Path("datasets/golden/example.jsonl")
    inputs, truths = [], []
    if golden_path.exists():
        for line in golden_path.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
                inputs.append(obj.get("input",""))
                truths.append(obj.get("truth",""))
            except Exception:
                pass

    faith = _judge_faithfulness(inputs or ["what is langgraph?"], truths or ["langgraph is a framework"])

    failures = []
    if faith < profile["thresholds"]["faithfulness"]:
        failures.append({"pillar":"task","id":"ex_001","reason":"low_faithfulness","faithfulness":round(faith,3)})

    return {"metrics":{"faithfulness": round(faith, 3)}, "failures": failures}
