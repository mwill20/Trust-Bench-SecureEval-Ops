# tests/system/test_report_snapshot.py
import json
import pathlib
import re

from trustbench_core.eval import report


def test_report_snapshot(tmp_path: pathlib.Path) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    (runs_dir / "_summary.json").write_text(json.dumps({"pillars": {"task": True, "system": True, "security": True, "ethics": True}}), encoding="utf-8")
    (runs_dir / "task_metrics.json").write_text(json.dumps({"faithfulness": 0.9}), encoding="utf-8")
    (runs_dir / "system_metrics.json").write_text(json.dumps({"p95_latency_seconds": 1.2}), encoding="utf-8")
    (runs_dir / "security_metrics.json").write_text(json.dumps({"injection_block_rate": 0.95}), encoding="utf-8")
    (runs_dir / "ethics_metrics.json").write_text(json.dumps({"refusal_accuracy": 0.96}), encoding="utf-8")

    html_path = tmp_path / "report.html"
    md_path = tmp_path / "report.md"
    report.main(
        runs_dir=str(runs_dir),
        out_md=str(md_path),
        out_html=str(html_path),
    )
    html = html_path.read_text(encoding="utf-8")
    assert re.search(r'class="pillar-status"', html)
    assert re.search(r'id="metrics-task"', html)
    assert re.search(r'data-key="refusal_accuracy"', html)
