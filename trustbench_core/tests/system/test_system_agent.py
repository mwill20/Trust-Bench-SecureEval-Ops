from types import SimpleNamespace

from trustbench_core.agents import system_perf


class FakeProvider:
    def __init__(self, latencies):
        self._latencies = iter(latencies)

    def completion(self, prompt, **kwargs):
        latency = next(self._latencies, 0.05)
        return {"text": "ack", "latency": latency}


def test_system_perf_metrics(monkeypatch, tmp_path):
    latencies = [0.1, 0.2, 0.25, 0.3, 0.15]
    provider = FakeProvider(latencies)
    monkeypatch.setattr(
        system_perf,
        "GroqProvider",
        SimpleNamespace(from_env=lambda model=None: provider),
    )

    profile = {
        "thresholds": {"p95_latency": 0.35},
        "sampling": {"n": len(latencies), "seed": 123},
    }
    result = system_perf.run(profile, tmp_path / "runs")
    assert result['metrics']['p95_latency'] >= 0.25
    assert not result["failures"]


def test_system_perf_failure(monkeypatch, tmp_path):
    provider = FakeProvider([0.5, 0.6, 0.55])
    monkeypatch.setattr(
        system_perf,
        "GroqProvider",
        SimpleNamespace(from_env=lambda model=None: provider),
    )
    profile = {
        "thresholds": {"p95_latency": 0.2},
        "sampling": {"n": 3, "seed": 1},
    }
    result = system_perf.run(profile, tmp_path / "runs")
    assert result["failures"], "Expect failure when latency exceeds threshold"