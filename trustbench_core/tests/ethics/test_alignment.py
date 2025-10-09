# tests/ethics/test_alignment.py
import os
import pathlib

from trustbench_core.eval.utils import load_config, write_metric
from trustbench_core.agents import ethics_refusal

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
BASE_DIR = CFG.parent.parent
DEFAULT_METRICS_DIR = BASE_DIR / "eval" / "runs" / "latest"
METRICS_DIR = pathlib.Path(os.environ.get("METRICS_DIR", DEFAULT_METRICS_DIR))


def test_ethics_metrics() -> None:
    cfg = load_config(CFG)
    thresholds = cfg["thresholds"]
    unsafe_path = (BASE_DIR / cfg["unsafe_path"]).resolve()
    with open(unsafe_path, "r", encoding="utf-8") as handle:
        prompts = [line.strip() for line in handle if line.strip()]

    refusals = 0
    violations = 0
    for prompt in prompts:
        result = ethics_refusal.run(prompt)
        if result["refused"]:
            refusals += 1
        else:
            violations += 1

    total = max(1, len(prompts))
    refusal_accuracy = refusals / total
    violation_rate = violations / total

    write_metric(
        METRICS_DIR,
        "ethics_metrics",
        {"refusal_accuracy": refusal_accuracy, "policy_violation_rate": violation_rate},
    )
    assert refusal_accuracy >= thresholds["refusal_accuracy"]
    assert violation_rate <= thresholds["policy_violation_rate"]
