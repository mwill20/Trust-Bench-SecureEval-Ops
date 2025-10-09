#!/usr/bin/env python3
"""
calibrate_thresholds.py  (Phase-1)

Sample multiple TrustBench runs and propose thresholds.
Supports either invoking the orchestrator, or reading an existing runs dir.

Usage A (invoke orchestrator N times):
  python calibrate_thresholds.py --profile profiles/default.yaml --runs 10

Usage B (read from a directory of previous runs):
  python calibrate_thresholds.py --runs-dir runs/default_calibration
"""
from __future__ import annotations

import argparse, json, os, re, subprocess, sys, time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:
    print("Missing dependency: pyyaml. Try `pip install pyyaml`.", file=sys.stderr)
    raise

LOWER_BETTER = {"p95_latency", "latency", "latency_p95"}
ARTIFACTS_RX = re.compile(r"Artifacts:\s*(?P<path>.+)$")

def percentile(vals: List[float], q: float) -> float:
    if not vals: return float("nan")
    xs = sorted(vals)
    if q <= 0: return xs[0]
    if q >= 100: return xs[-1]
    k = (len(xs) - 1) * q / 100.0
    f = int(k); c = min(f+1, len(xs)-1)
    if f == c: return xs[f]
    return xs[f]*(c-k) + xs[c]*(k-f)

def collect_metrics_from_run(run_dir: Path) -> Dict[str, float]:
    mp = run_dir / "metrics.json"
    if mp.exists():
        return json.loads(mp.read_text())
    combined: Dict[str, float] = {}
    for metric_file in run_dir.glob("*_metrics.json"):
        try:
            data = json.loads(metric_file.read_text())
            for k, v in data.items():
                combined.setdefault(k, float(v))
        except Exception:
            continue
    if not combined:
        raise FileNotFoundError(f"metrics.json or *_metrics.json not found in {run_dir}")
    return combined

def invoke_once(profile: str) -> Path:
    cmd = [sys.executable, "-m", "trustbench_core.eval.evaluate_agent", "--profile", profile]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    run_path = None
    assert proc.stdout is not None
    for line in proc.stdout:
        m = ARTIFACTS_RX.search(line)
        if m: run_path = Path(m.group("path").strip())
        print(line.rstrip())
    proc.wait()
    if run_path is None:
        runs_root = Path("trustbench_core") / "eval" / "runs"
        cands = sorted(runs_root.glob("*"), key=lambda p: p.stat().st_mtime)
        run_path = cands[-1] if cands else None
    if not run_path or not run_path.exists():
        raise RuntimeError("Could not determine runs directory")
    return run_path

def suggest_thresholds(samples: Dict[str, List[float]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for k, vals in samples.items():
        if not vals: continue
        if k in LOWER_BETTER or k.endswith("latency"):
            out[k] = round(percentile(vals, 90), 4)
        else:
            out[k] = round(percentile(vals, 10), 4)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", help="Profile YAML to run repeatedly")
    ap.add_argument("--runs", type=int, default=10, help="Number of runs to collect when invoking")
    ap.add_argument("--runs-dir", help="Use existing directory containing multiple run folders")
    ap.add_argument("--sleep", type=float, default=0.15, help="Pause between invocations (seconds)")
    args = ap.parse_args()

    if not args.profile and not args.runs_dir:
        ap.error("Provide either --profile (to invoke runs) or --runs-dir (to read existing runs).")

    run_dirs: List[Path] = []

    if args.runs_dir:
        root = Path(args.runs_dir)
        if not root.exists():
            raise FileNotFoundError(f"--runs-dir not found: {root}")
        for d in sorted(root.iterdir()):
            if (d / "metrics.json").exists():
                run_dirs.append(d)
        if not run_dirs:
            raise RuntimeError(f"No metrics.json found under {root}")
    else:
        for i in range(1, args.runs + 1):
            print(f"\n=== Run {i}/{args.runs} ===")
            rd = invoke_once(args.profile)
            run_dirs.append(rd)
            time.sleep(args.sleep)

    per_metric: Dict[str, List[float]] = {}
    for rd in run_dirs:
        m = collect_metrics_from_run(rd)
        for k, v in m.items():
            try:
                per_metric.setdefault(k, []).append(float(v))
            except Exception:
                pass

    summaries: Dict[str, Dict[str, float]] = {}
    for k, vals in per_metric.items():
        summaries[k] = {
            "n": len(vals),
            "min": min(vals),
            "p10": percentile(vals, 10),
            "median": percentile(vals, 50),
            "p90": percentile(vals, 90),
            "max": max(vals),
            "mean": sum(vals)/len(vals),
        }

    suggestions = suggest_thresholds(per_metric)

    out_dir = Path("calibration")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summaries.json").write_text(json.dumps(summaries, indent=2))
    (out_dir / "suggested_thresholds.json").write_text(json.dumps(suggestions, indent=2))

    import yaml as _yaml
    yaml_block = {"thresholds": suggestions}
    (out_dir / "suggested_profile.yaml").write_text(_yaml.safe_dump(yaml_block, sort_keys=True))

    print("\nSuggested thresholds:\n")
    print(_yaml.safe_dump(yaml_block, sort_keys=True))
    print(f"Wrote: {out_dir/'summaries.json'}, {out_dir/'suggested_thresholds.json'}, {out_dir/'suggested_profile.yaml'}")

if __name__ == "__main__":
    main()
