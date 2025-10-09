import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from trustbench_core.agents import task_fidelity


def _write_dataset(path: Path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_task_fidelity_success(monkeypatch, tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    _write_dataset(
        dataset,
        [
            {"id": "ex_1", "input": "What is LangGraph?", "truth": "LangGraph is a framework."},
            {"id": "ex_2", "input": "Define RAG.", "truth": "RAG is retrieval augmented generation."},
        ],
    )

    class FakeProvider:
        def completion(self, prompt, **kwargs):
            if "LangGraph" in prompt:
                return {"text": "LangGraph is a framework.", "latency": 0.01}
            return {"text": "RAG is retrieval augmented generation.", "latency": 0.02}

    monkeypatch.setattr(
        task_fidelity,
        "GroqProvider",
        SimpleNamespace(from_env=lambda model=None: FakeProvider()),
    )
    monkeypatch.setattr(task_fidelity, "_RAGAS_AVAILABLE", False)

    profile = {
        "thresholds": {"faithfulness": 0.5},
        "sampling": {"n": 2, "seed": 123},
        "dataset_path": str(dataset),
        "model": "stub",
    }
    result = task_fidelity.run(profile, tmp_path / "runs")
    assert result["metrics"]["faithfulness"] >= 0.5
    assert not result["failures"]


def test_task_fidelity_failure(monkeypatch, tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    _write_dataset(
        dataset,
        [
            {"id": "ex_1", "input": "Question?", "truth": "Correct answer."},
        ],
    )

    class FakeProvider:
        def completion(self, prompt, **kwargs):
            return {"text": "incorrect output", "latency": 0.03}

    monkeypatch.setattr(
        task_fidelity,
        "GroqProvider",
        SimpleNamespace(from_env=lambda model=None: FakeProvider()),
    )
    monkeypatch.setattr(task_fidelity, "_RAGAS_AVAILABLE", False)

    profile = {
        "thresholds": {"faithfulness": 0.99},
        "sampling": {"n": 1, "seed": 7},
        "dataset_path": str(dataset),
        "model": "stub",
    }
    result = task_fidelity.run(profile, tmp_path / "runs")
    assert result["metrics"]["faithfulness"] < 0.99
    assert result["failures"], "Expect failure when score is below threshold"
