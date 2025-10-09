"""System performance agent that measures Groq latency."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from trustbench_core.providers import GroqProvider, GroqProviderError
from trustbench_core.utils.env import resolve_model

LATENCY_PROMPT = "Latency-probe: respond with a short acknowledgement."


@dataclass
class SystemPerfConfig:
    model: str
    sample_n: int
    seed: int
    threshold: float

    @classmethod
    def from_profile(cls, profile: Dict[str, Any]) -> "SystemPerfConfig":
        sampling = profile.get("sampling", {})
        threshold = profile.get("thresholds", {}).get("p95_latency", 5.0)
        return cls(
            model=resolve_model(profile.get("model", profile.get("provider_model", ""))),
            sample_n=int(sampling.get("n", 10)),
            seed=int(sampling.get("seed", 42)),
            threshold=float(threshold),
        )


def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    cfg = SystemPerfConfig.from_profile(profile)
    provider = GroqProvider.from_env(model=cfg.model)

    latencies: List[float] = []
    responses: List[str] = []
    for _ in range(cfg.sample_n):
        start = time.time()
        try:
            result = provider.completion(LATENCY_PROMPT)
        except GroqProviderError as exc:
            raise GroqProviderError(f"Latency probe failed: {exc}") from exc
        latencies.append(result["latency"] or (time.time() - start))
        responses.append(result["text"])

    latencies.sort()
    p95_index = max(0, int(0.95 * len(latencies)) - 1)
    p95_latency = latencies[p95_index]
    mean_latency = statistics.fmean(latencies) if latencies else 0.0

    workdir.mkdir(parents=True, exist_ok=True)
    with (workdir / "latency_samples.json").open("w", encoding="utf-8") as handle:
        json.dump({"latencies": latencies, "responses": responses}, handle, indent=2)

    failures = []
    if p95_latency > cfg.threshold:
        failures.append(
            {
                "pillar": "system",
                "id": "latency",
                "reason": "p95_latency_exceeded",
                "score": p95_latency,
                "threshold": cfg.threshold,
            }
        )

    metrics = {
        "p95_latency": p95_latency,
        "mean_latency": mean_latency,
        "samples": len(latencies),
    }
    return {"metrics": metrics, "failures": failures}
