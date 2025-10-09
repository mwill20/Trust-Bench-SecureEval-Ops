from types import SimpleNamespace
from pathlib import Path

from trustbench_core.agents import security_eval
from trustbench_core.tools.bundle import tools_security


def test_security_agent(monkeypatch, tmp_path):
    prompts_file = tmp_path / "adv.txt"
    prompts_file.write_text("attack one\nattack two\n", encoding="utf-8")
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    def fake_prompt_guard(prompts, client=None):
        return {"ok": True, "stats": {"blocked": 1, "total": 2}, "findings": [{"prompt_id": "attack-two"}]}

    def fake_semgrep(path, rules_path=None, client=None):
        return {"ok": True, "findings": [{"file": "x.py"}], "stats": {"count": 1}}

    def fake_secrets(path, client=None):
        return {"ok": True, "findings": [], "stats": {"count": 0}}

    monkeypatch.setattr(tools_security, "prompt_guard", fake_prompt_guard)
    monkeypatch.setattr(tools_security, "semgrep_scan", fake_semgrep)
    monkeypatch.setattr(tools_security, "secrets_scan", fake_secrets)

    profile = {
        "thresholds": {"injection_block_rate": 0.4},
        "adversarial_path": str(prompts_file),
        "repo_path": str(repo_path),
    }
    result = security_eval.run(profile, tmp_path / "runs")
    assert result["metrics"]["injection_block_rate"] == 0.5
    assert result["metrics"]["semgrep_findings"] == 1
    # Semgrep finding should create a failure entry
    reasons = {failure["reason"] for failure in result["failures"]}
    assert "semgrep_findings" in reasons
