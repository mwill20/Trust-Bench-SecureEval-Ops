from __future__ import annotations
import webbrowser, json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template

_HTML = """<!doctype html><html><head>
<meta charset="utf-8"><title>TrustBench Report</title>
<style>
body{font-family:system-ui,Segoe UI,Arial;margin:24px;background:#0b0b0b;color:#e6e6e6}
.card{background:#151515;padding:16px;border-radius:12px;margin-bottom:12px}
.ok{color:#9FE870}.bad{color:#FF6B6B}
table{width:100%;border-collapse:collapse}
td,th{border-bottom:1px solid #333;padding:8px;text-align:left}
small{color:#9aa}
</style></head><body>
<h1>TrustBench Report</h1>
<div class="card">
  <h3>Metrics</h3>
  <table><tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
  {% for k,v in thresholds.items() %}
   <tr>
     <td>{{k}}</td>
     <td>{{metrics.get(k)}}</td>
     <td>{{v}}</td>
     <td class="{{'ok' if gate[k]['pass'] else 'bad'}}">{{'PASS' if gate[k]['pass'] else 'FAIL'}}</td>
   </tr>
  {% endfor %}
  </table>
  <p><b>Overall:</b> <span class="{{'ok' if gate['overall_pass'] else 'bad'}}">{{'PASS' if gate['overall_pass'] else 'FAIL'}}</span></p>
</div>
<div class="card">
  <h3>Failures (top)</h3>
  {% if failures %}
    <table><tr><th>pillar</th><th>id</th><th>reason</th><th>details</th></tr>
    {% for f in failures[:10] %}
      <tr><td>{{f.get('pillar')}}</td><td>{{f.get('id')}}</td><td>{{f.get('reason')}}</td><td><small>{{f}}</small></td></tr>
    {% endfor %}
    </table>
  {% else %}
    <p>No failures recorded.</p>
  {% endif %}
</div>
<small>Run dir: {{run_dir}}</small>
</body></html>"""

def write_report(run_dir: Path, metrics: Dict[str, float], gate_res: Dict[str, Any], failures: List[Dict[str, Any]]):
    thresholds = {k: gate_res[k]["threshold"] for k in metrics.keys() if k in gate_res}
    html = Template(_HTML).render(metrics=metrics, thresholds=thresholds, gate=gate_res, failures=failures, run_dir=str(run_dir))
    (run_dir / "report.html").write_text(html, encoding="utf-8")

def _find_last_run(base: Path = Path("runs")) -> Path | None:
    if not base.exists():
        return None
    runs = sorted(base.iterdir(), key=lambda p: p.name, reverse=True)
    return runs[0] if runs else None

def main_open_last():
    rd = _find_last_run()
    if not rd:
        print("No runs/ found yet.")
        return
    fp = rd / "report.html"
    if not fp.exists():
        print("No report.html found in last run.")
        return
    webbrowser.open(fp.resolve().as_uri())
    print(f"Opened: {fp}")

if __name__ == "__main__":
    main_open_last()
