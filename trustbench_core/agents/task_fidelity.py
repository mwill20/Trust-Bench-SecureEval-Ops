"""Task fidelity agent using RAGAS (with deterministic fallback).

The public contract is `run(profile: dict, workdir: Path) -> {"metrics": {...}, "failures": [...]}`.
Profiles may inject the following keys:
- dataset_path: path to JSONL examples (defaults to datasets/golden/example.jsonl)
- thresholds.faithfulness: numeric target used for failure tagging
- sampling.n / sampling.seed: number of samples and RNG seed
- model: model name for the Groq provider
"""

from __future__ import annotations

import json
import os
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from trustbench_core.providers import GroqProvider, GroqProviderError
from trustbench_core.utils.env import resolve_model

try:  # pragma: no cover - real path exercised in integration envs
    from ragas import evaluate as ragas_evaluate  # type: ignore
    from ragas.dataset_schema import Dataset  # type: ignore
    from ragas.metrics import faithfulness as ragas_faithfulness  # type: ignore

    _RAGAS_AVAILABLE = True
except Exception:  # pragma: no cover - fallback for local tests
    _RAGAS_AVAILABLE = False


DEFAULT_DATASET = Path("datasets/golden/example.jsonl")
DEFAULT_PROMPT = (
    "You are evaluating TrustBench task fidelity. Answer the question accurately.\n\n"
    "Question: {question}\n"
    "Return only the answer without additional commentary."
)


@dataclass
class TaskFidelityConfig:
    dataset_path: Path
    model: str
    sample_n: int = 10
    seed: int = 42
    threshold: float = 0.85

    @classmethod
    def from_profile(cls, profile: Dict[str, Any]) -> "TaskFidelityConfig":
        thresholds = profile.get("thresholds", {})
        sampling = profile.get("sampling", {})
        dataset = profile.get("dataset_path", str(DEFAULT_DATASET))
        dataset_path = Path(dataset)
        if not dataset_path.is_absolute():
            dataset_path = Path(".").resolve() / dataset_path
        return cls(
            dataset_path=dataset_path,
            model=resolve_model(profile.get("model", profile.get("provider_model", ""))),
            sample_n=int(sampling.get("n", 10)),
            seed=int(sampling.get("seed", 42)),
            threshold=float(thresholds.get("faithfulness", 0.85)),
        )


def _load_dataset(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    if not records:
        raise ValueError(f"Dataset at {path} is empty.")
    return records


def _sample_records(records: Sequence[Dict[str, Any]], cfg: TaskFidelityConfig) -> List[Dict[str, Any]]:
    rng = random.Random(cfg.seed)
    if cfg.sample_n >= len(records):
        return list(records)
    return rng.sample(list(records), cfg.sample_n)


def _build_prompt(entry: Dict[str, Any]) -> str:
    return DEFAULT_PROMPT.format(question=entry.get("input") or entry.get("question"))


def _fake_score(answer: str, truth: str) -> float:
    # Simple token overlap fallback when ragas is unavailable
    ans_tokens = set(answer.lower().split())
    truth_tokens = set(truth.lower().split())
    if not truth_tokens:
        return 0.0
    return len(ans_tokens & truth_tokens) / len(truth_tokens)


def _score_with_ragas(rows: List[Dict[str, Any]], answers: List[str]) -> Tuple[List[float], Dict[str, Any]]:
    if _RAGAS_AVAILABLE and os.getenv("OPENAI_API_KEY"):  # pragma: no branch
        dataset = Dataset.from_list(
            [
                {
                    "question": row.get("input") or row.get("question"),
                    "contexts": [row.get("truth", "")],
                    "answer": answer,
                    "ground_truth": row.get("truth", ""),
                }
                for row, answer in zip(rows, answers)
            ]
        )
        try:
            result = ragas_evaluate(dataset, [ragas_faithfulness])  # type: ignore[arg-type]
            faithfulness_scores = list(result["faithfulness"])  # type: ignore[index]
            return faithfulness_scores, {"ragas": True}
        except Exception as exc:  # pragma: no cover - network/LLM issues
            return _scores_with_fallback(rows, answers, reason=f"ragas_error:{exc!r}")

    reason = "ragas_unavailable" if not _RAGAS_AVAILABLE else "openai_api_key_missing"
    return _scores_with_fallback(rows, answers, reason=reason)


def _scores_with_fallback(
    rows: List[Dict[str, Any]], answers: List[str], reason: str
) -> Tuple[List[float], Dict[str, Any]]:
    scores = [_fake_score(answer, row.get("truth", "")) for row, answer in zip(rows, answers)]
    return scores, {"ragas": False, "reason": reason}


def _write_debug(workdir: Path, rows: List[Dict[str, Any]], answers: List[str], scores: List[float]) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    details = [
        {
            "id": row.get("id"),
            "question": row.get("input") or row.get("question"),
            "answer": answer,
            "truth": row.get("truth"),
            "score": score,
        }
        for row, answer, score in zip(rows, answers, scores)
    ]
    with (workdir / "task_fidelity_details.json").open("w", encoding="utf-8") as handle:
        json.dump(details, handle, indent=2)


def run(profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    """Execute task fidelity evaluation for the supplied profile."""
    cfg = TaskFidelityConfig.from_profile(profile)
    rows = _sample_records(_load_dataset(cfg.dataset_path), cfg)

    provider = GroqProvider.from_env(model=cfg.model)
    answers: List[str] = []
    latencies: List[float] = []

    for entry in rows:
        prompt = _build_prompt(entry)
        try:
            result = provider.completion(prompt)
        except GroqProviderError as exc:
            raise GroqProviderError(f"Task fidelity completion failed for id={entry.get('id')}: {exc}") from exc
        answers.append(result["text"])
        latencies.append(result["latency"])

    scores, meta = _score_with_ragas(rows, answers)
    mean_score = statistics.fmean(scores) if scores else 0.0

    failures = []
    for entry, answer, score in zip(rows, answers, scores):
        if score < cfg.threshold:
            failures.append(
                {
                    "pillar": "task",
                    "id": entry.get("id"),
                    "reason": "low_faithfulness",
                    "score": score,
                    "answer": answer,
                }
            )

    _write_debug(workdir, rows, answers, scores)

    metrics = {
        "faithfulness": mean_score,
        "avg_latency": statistics.fmean(latencies) if latencies else 0.0,
        "samples": len(scores),
        **meta,
    }
    return {"metrics": metrics, "failures": failures}

