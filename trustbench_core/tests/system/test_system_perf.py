# tests/system/test_system_perf.py
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor

from trustbench_core.eval.utils import load_config, write_metric
from trustbench_core.agents import system_perf

CFG = pathlib.Path(os.environ.get("EVAL_CFG", "eval/eval_config.yaml")).resolve()
BASE_DIR = CFG.parent.parent
DEFAULT_METRICS_DIR = BASE_DIR / "eval" / "runs" / "latest"
METRICS_DIR = pathlib.Path(os.environ.get("METRICS_DIR", DEFAULT_METRICS_DIR))


def test_latency_and_reliability() -> None:
    cfg = load_config(CFG)
    thresholds = cfg["thresholds"]

    latencies = []
    failures = 0
    samples = cfg.get("sampling", {}).get("n", 10)

    with ThreadPoolExecutor(max_workers=cfg["concurrency"]) as executor:
        futures = [
            executor.submit(system_perf.run, cfg["agent_endpoint"], idx / samples)
            for idx in range(samples)
        ]
        for future in futures:
            result = future.result()
            latencies.append(result["latency"])
            failures += 0 if result["ok"] else 1

    latencies.sort()
    p95_index = max(0, int(0.95 * len(latencies)) - 1)
    p95_latency = latencies[p95_index]
    failure_rate = failures / len(latencies)

    write_metric(
        METRICS_DIR,
        "system_metrics",
        {"p95_latency_seconds": p95_latency, "failure_rate": failure_rate},
    )
    assert p95_latency <= thresholds["p95_latency_seconds"]
    assert failure_rate <= thresholds["failure_rate"]
