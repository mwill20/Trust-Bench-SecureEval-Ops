\
from typing import Dict, List
from ..security_utils import redact

def _risk_summary(findings: List[Dict]) -> Dict:
    total = len(findings)
    score = min(100, sum(f.get("score", 0) for f in findings) // max(1, total))
    verdict = "High" if score >= 70 else "Moderate" if score >= 40 else "Low"
    return {"total": total, "score": score, "verdict": verdict}

def compile_report(state: Dict) -> Dict:
    findings: List[Dict] = state.get("findings", [])
    summary = _risk_summary(findings)
    lines = []
    lines.append(f"# trust_bench.AI Security Report")
    lines.append("")
    lines.append(f"**Overall Risk Score:** {summary['score']}/100  •  **Verdict:** {summary['verdict']}")
    lines.append(f"**Findings:** {summary['total']}")
    lines.append("")
    # Group by agent
    by_agent = {}
    for f in findings:
        by_agent.setdefault(f["agent"], []).append(f)
    for agent, items in by_agent.items():
        lines.append(f"## {agent} Findings")
        for i, it in enumerate(items, 1):
            lines.append(f"- **{i}. {it['path']}**  (score {it.get('score', 0)})")
            for h in it.get("hits", []):
                desc = h.get("desc", "hit")
                snip = redact(h.get("snippet", ""))
                snip = snip.replace("\n", " ")[:220]
                lines.append(f"  - {desc}: `{snip}`")
        lines.append("")
    if not findings:
        lines.append("_No issues detected by the MVP ruleset. Treat as preliminary only._")
    report_md = "\n".join(lines)
    state["report_md"] = report_md
    # Persist
    out = state.get("out_path", "trust_bench_report.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report_md)
    state["report_path"] = out
    return state
