import datetime
import json
import pathlib
from typing import Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path: pathlib.Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _default_html_path(runs_path: pathlib.Path) -> pathlib.Path:
    return runs_path / "report.html"


def main(
    runs_dir: str = "eval/runs/latest",
    out_md: str = "reports/last_report.md",
    out_html: str | None = None,
) -> None:
    runs_path = pathlib.Path(runs_dir)
    if not runs_path.is_absolute():
        runs_path = ROOT / runs_path
    summary = load(runs_path / "_summary.json")
    task = load(runs_path / "task_metrics.json")
    system = load(runs_path / "system_metrics.json")
    security = load(runs_path / "security_metrics.json")
    ethics = load(runs_path / "ethics_metrics.json")

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    lines = [
        "# TrustBench Core Report\n",
        f"Generated: {timestamp}\n",
        "## Pillar Status\n",
    ]

    for name, passed in summary.get("pillars", {}).items():
        status = "pass" if passed else "fail"
        lines.append(f"- **{name.capitalize()}**: {status}")

    lines.append("\n## Metrics\n")

    def append_section(metrics: Dict[str, object], title: str) -> None:
        if not metrics:
            return
        lines.append(f"### {title}")
        for key, value in metrics.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")

    append_section(task, "Task Performance")
    append_section(system, "System Performance")
    append_section(security, "Security and Robustness")
    append_section(ethics, "Ethics and Alignment")

    markdown_path = pathlib.Path(out_md)
    if not markdown_path.is_absolute():
        markdown_path = ROOT / markdown_path
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    html_path = pathlib.Path(out_html) if out_html else _default_html_path(runs_path)
    if not html_path.is_absolute():
        html_path = ROOT / html_path
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_lines = [
        "<html>",
        "<head><title>TrustBench Core Report</title></head>",
        '<body class="trustbench-report">',
        f'<section id="report-generated" data-timestamp="{timestamp}">',
        "<h1>TrustBench Core Report</h1>",
        f"<p>Generated: {timestamp}</p>",
        "</section>",
        '<section id="pillar-status" class="pillar-status">',
        "<h2>Pillar Status</h2>",
        "<ul>",
    ]

    for name, passed in summary.get("pillars", {}).items():
        status_class = "pass" if passed else "fail"
        html_lines.append(
            f'<li class="pillar {status_class}" id="pillar-{name}">{name}: {status_class}</li>'
        )
    html_lines.extend(["</ul>", "</section>", '<section id="metrics" class="metrics">'])

    def append_metrics_section(metrics: Dict[str, object], title: str, slug: str) -> None:
        if not metrics:
            return
        html_lines.append(
            f'<div class="metric-group" id="metrics-{slug}"><h3>{title}</h3><ul>'
        )
        for key, value in metrics.items():
            html_lines.append(
                f'<li class="metric" data-key="{key}"><span class="metric-key">{key}</span>: '
                f'<span class="metric-value">{value}</span></li>'
            )
        html_lines.append("</ul></div>")

    append_metrics_section(task, "Task Performance", "task")
    append_metrics_section(system, "System Performance", "system")
    append_metrics_section(security, "Security and Robustness", "security")
    append_metrics_section(ethics, "Ethics and Alignment", "ethics")

    html_lines.extend(["</section>", "</body>", "</html>"])
    html_path.write_text("\n".join(html_lines), encoding="utf-8")
    print(f"Wrote {markdown_path} and {html_path}")


if __name__ == "__main__":
    main()
