# tests/system/test_system_perf.py
import os
import pathlib
from typing import Any, Dict

import pytest

from trustbench_core.agents import system_perf
from trustbench_core.eval.utils import load_config, write_metric

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()


@pytest.fixture(autouse=True)
def _enable_fake_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRUSTBENCH_FAKE_PROVIDER", "1")


def test_latency_and_reliability(tmp_path: pathlib.Path) -> None:
    profile: Dict[str, Any] = load_config(CFG)
    result = system_perf.run(profile, tmp_path / "system")
    metrics = result["metrics"]

    write_metric(tmp_path / "metrics", "system_metrics", metrics)

    assert metrics["samples"] > 0
    assert metrics["p95_latency"] >= 0.0
    assert isinstance(result["failures"], list)
