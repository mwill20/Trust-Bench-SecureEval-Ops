# eval/orchestrator.py
import json
import os
import pathlib
import subprocess

from .utils import load_config, run_pytest, section, write_metric

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = ROOT / "eval" / "eval_config.yaml"

def select_eval_method(goal:str)->str:
    goal = goal.lower()
    if goal in ("accuracy","faithfulness","usefulness"):
        return "llm_judge"
    if goal in ("latency","reliability","throughput"):
        return "rule_based"
    if goal in ("security","robustness","injection","secrets"):
        return "simulated_experiments"
    if goal in ("ethics","alignment","bias"):
        return "hitl_review"
    return "rule_based"

def run_all():
    cfg = load_config(CFG)
    metrics_dir_config = pathlib.Path(cfg.get("runs_dir", "eval/runs/latest"))
    if not metrics_dir_config.is_absolute():
        metrics_dir_config = ROOT.parent / metrics_dir_config
    metrics_dir = str(metrics_dir_config)
    extra_env = {"EVAL_CFG": str(CFG), "METRICS_DIR": metrics_dir}
    results = {}

    print(section("Task Performance"))
    code = run_pytest("tests/task", extra_env=extra_env); results["task"] = (code==0)
    print(section("System Performance"))
    code = run_pytest("tests/system", extra_env=extra_env); results["system"] = (code==0)
    print(section("Security & Robustness"))
    code = run_pytest("tests/security", extra_env=extra_env); results["security"] = (code==0)
    print(section("Ethics & Alignment"))
    code = run_pytest("tests/ethics", extra_env=extra_env); results["ethics"] = (code==0)

    write_metric(metrics_dir, "_summary", {"pillars": results})
    manifest = {
        "schema_version": 1,
        "profile": cfg.get("profile_name", cfg.get("profile", "default")),
        "metrics_dir": str(metrics_dir_config),
        "git_sha": _git_sha(),
        "fake_provider": os.getenv("TRUSTBENCH_FAKE_PROVIDER") == "1",
    }
    (metrics_dir_config / "run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    combined_metrics = {}
    for metric_file in metrics_dir_config.glob("*_metrics.json"):
        try:
            data = json.loads(metric_file.read_text(encoding="utf-8"))
            combined_metrics.update(data)
        except Exception:
            pass
    if combined_metrics:
        combined_metrics["fake_provider"] = manifest["fake_provider"]
        (metrics_dir_config / "metrics.json").write_text(
            json.dumps(combined_metrics, indent=2), encoding="utf-8"
        )
    failed = [name for name, ok in results.items() if not ok]
    gate_path = metrics_dir_config / "gate.json"
    gate_path.write_text(
        json.dumps({"blocked": bool(failed), "failed": failed}, indent=2),
        encoding="utf-8",
    )
    failures_path = metrics_dir_config / "failures.csv"
    if failed:
        failures_path.parent.mkdir(parents=True, exist_ok=True)
        failures_path.write_text(
            "pillar\n" + "\n".join(failed),
            encoding="utf-8",
        )
    elif failures_path.exists():
        failures_path.unlink()

    print(section("Done."))
    return results


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"
