import argparse, json, os, time, uuid
from pathlib import Path
from typing import Dict, Any

import yaml
from rich import print as rprint

RUNS_DIR = Path("runs")

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def run_agent(module_name: str, profile: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    mod = __import__(f"trustbench_core.agents.{module_name}", fromlist=["run"])
    return mod.run(profile=profile, workdir=workdir)

def gate(metrics: Dict[str, float], thresholds: Dict[str, float]) -> Dict[str, Any]:
    results = {}
    overall = True
    for k, thr in thresholds.items():
        val = metrics.get(k, 0.0)
        ok = (val <= thr) if k.endswith("latency") else (val >= thr)
        results[k] = {"value": val, "threshold": thr, "pass": ok}
        overall = overall and ok
    results["overall_pass"] = overall
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--repo", default=None)  # reserved for future use
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args()

    profile = load_yaml(args.profile)
    run_id = f"{ts()}-{uuid.uuid4().hex[:6]}"
    outdir = RUNS_DIR / run_id
    ensure_dir(outdir)

    rprint(f"[bold cyan]TrustBench[/] run: [yellow]{run_id}[/] | profile: [magenta]{profile.get('profile')}[/]")

    metrics = {}
    failures = []

    for name in ["task_fidelity", "security_eval", "system_perf", "ethics_refusal"]:
        rprint(f"• running agent: [green]{name}[/]")
        res = run_agent(name, profile, outdir)
        metrics.update(res.get("metrics", {}))
        failures.extend(res.get("failures", []))

    thresholds = profile.get("thresholds", {})
    gate_res = gate(metrics, thresholds)

    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (outdir / "gate.json").write_text(json.dumps(gate_res, indent=2))

    if failures:
        import pandas as pd
        df = pd.DataFrame(failures)
        df.to_csv(outdir / "failures.csv", index=False)

    from trustbench_core.reports.writer import write_report
    write_report(outdir, metrics, gate_res, failures)

    rprint("\n[bold]Summary[/]")
    for k, v in thresholds.items():
        val = metrics.get(k, 0.0)
        ok = "✅" if gate_res[k]["pass"] else "❌"
        rprint(f"  {k}: {val:.3f} (thr {v}) {ok}")
    rprint(f\"\nArtifacts: {outdir}\")

    if args.ci and not gate_res["overall_pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
