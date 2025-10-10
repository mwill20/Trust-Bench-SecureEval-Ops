# tests/task/test_ragas.py
import os
import pathlib
from typing import Any, Dict

import pytest

from trustbench_core.agents import task_fidelity
from trustbench_core.eval.utils import load_config, write_metric

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
DATASET = pathlib.Path("trustbench_core/data/eval/qa.jsonl")


@pytest.fixture(autouse=True)
def _enable_fake_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRUSTBENCH_FAKE_PROVIDER", "1")


def test_task_performance(tmp_path: pathlib.Path) -> None:
    profile: Dict[str, Any] = load_config(CFG)
    profile["dataset_path"] = str(DATASET)

    result = task_fidelity.run(profile, tmp_path / "task")
    metrics = result["metrics"]

    metrics_dir = pathlib.Path(os.environ.get("METRICS_DIR", tmp_path / "metrics")).resolve()
    write_metric(metrics_dir, "task_metrics", metrics)

    assert metrics["samples"] > 0
    assert 0.0 <= metrics.get("faithfulness", 0.0) <= 1.0
    assert isinstance(result["failures"], list)
