from types import SimpleNamespace
from pathlib import Path

from trustbench_core.agents import ethics_refusal


class FakeProvider:
    def __init__(self, answers):
        self._answers = iter(answers)

    def llm_json(self, prompt, **kwargs):
        return next(self._answers, {"refusal_correct": True, "rationale": "stub"})


def test_ethics_metrics(monkeypatch, tmp_path):
    prompts_path = tmp_path / "unsafe.txt"
    prompts_path.write_text("bad prompt\nanother bad prompt\n", encoding="utf-8")

    provider = FakeProvider(
        [
            {"refusal_correct": True, "rationale": "good refusal"},
            {"refusal_correct": False, "rationale": "missed refusal"},
        ]
    )
    monkeypatch.setattr(
        ethics_refusal,
        "GroqProvider",
        SimpleNamespace(from_env=lambda model=None: provider),
    )

    profile = {
        "thresholds": {"refusal_accuracy": 0.4},
        "unsafe_path": str(prompts_path),
        "model": "stub",
    }
    result = ethics_refusal.run(profile, tmp_path / "runs")
    assert result["metrics"]["refusal_accuracy"] == 0.5
    assert result["failures"], "Expected misclassification to surface as failure"
