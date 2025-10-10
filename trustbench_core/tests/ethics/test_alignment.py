# tests/ethics/test_alignment.py
import os
import pathlib
from typing import Any, Dict

import pytest

from trustbench_core.agents import ethics_refusal
from trustbench_core.eval.utils import load_config, write_metric

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
UNSAFE = pathlib.Path("trustbench_core/data/ethics/unsafe.txt")


@pytest.fixture(autouse=True)
def _enable_fake_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the refusal agent uses the deterministic stub."""
    monkeypatch.setenv("TRUSTBENCH_FAKE_PROVIDER", "1")


def test_ethics_metrics(tmp_path: pathlib.Path) -> None:
    profile: Dict[str, Any] = load_config(CFG)
    profile["unsafe_path"] = str(UNSAFE)

    result = ethics_refusal.run(profile, tmp_path / "ethics")
    metrics = result["metrics"]

    metrics_dir = pathlib.Path(os.environ.get("METRICS_DIR", tmp_path / "metrics")).resolve()
    write_metric(metrics_dir, "ethics_metrics", metrics)

    assert 0.0 <= metrics.get("refusal_accuracy", 0.0) <= 1.0
    assert metrics.get("samples", 0) >= 0
    assert isinstance(result["failures"], list)
