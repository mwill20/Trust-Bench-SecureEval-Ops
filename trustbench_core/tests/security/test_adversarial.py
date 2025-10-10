# tests/security/test_adversarial.py
import os
import pathlib
from typing import Any, Dict

import pytest

from trustbench_core.agents import security_eval
from trustbench_core.eval.utils import load_config, write_metric
from trustbench_core.tools.bundle import tools_security

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
ADVERSARIAL = pathlib.Path("trustbench_core/data/security/adversarial.txt")
REPO_FIXTURE = pathlib.Path("datasets/golden/fixtures/repos/vuln-mini-1")


@pytest.fixture(autouse=True)
def _stub_security_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    def _prompt_guard(prompts, client=None):
        total = len(prompts)
        return {"ok": True, "findings": [], "stats": {"total": total, "blocked": total}}

    def _semgrep_scan(path, rules_path=None, client=None):
        return {"ok": True, "findings": [], "stats": {"count": 0}}

    def _secrets_scan(path, client=None):
        return {"ok": True, "findings": [], "stats": {"count": 0}}

    monkeypatch.setattr(tools_security, "prompt_guard", _prompt_guard)
    monkeypatch.setattr(tools_security, "semgrep_scan", _semgrep_scan)
    monkeypatch.setattr(tools_security, "secrets_scan", _secrets_scan)


def test_security_metrics(tmp_path: pathlib.Path) -> None:
    profile: Dict[str, Any] = load_config(CFG)
    profile["adversarial_path"] = str(ADVERSARIAL)
    profile["repo_path"] = str(REPO_FIXTURE)

    result = security_eval.run(profile, tmp_path / "security")
    metrics = result["metrics"]

    metrics_dir = pathlib.Path(os.environ.get("METRICS_DIR", tmp_path / "metrics")).resolve()
    write_metric(metrics_dir, "security_metrics", metrics)

    assert metrics["injection_block_rate"] == 1.0
    assert metrics["semgrep_findings"] == 0
    assert metrics["secret_findings"] == 0
    assert isinstance(result["failures"], list)
