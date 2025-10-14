# tests/system/test_system_perf.py
import concurrent.futures as cf
import os
import pathlib
import random
import time

from eval.utils import load_config

THIS_FILE = pathlib.Path(__file__).resolve()
EXAMPLE_CFG = THIS_FILE.parents[2] / "eval" / "eval_config.yaml"
CFG = pathlib.Path(os.environ.get("EVAL_CFG", EXAMPLE_CFG)).resolve()


def ping_agent(endpoint: str) -> tuple[bool, float]:
    start = time.time()
    try:
        time.sleep(0.05 + random.random() * 0.05)  # replace with real call latency
        return True, time.time() - start
    except Exception:  # noqa: BLE001 - placeholder until real call wired
        return False, time.time() - start


def test_latency_and_reliability() -> None:
    cfg = load_config(CFG)
    thresholds = cfg["thresholds"]
    samples = cfg.get("sampling", {}).get("n", 50)
    latencies = []
    failures = 0
    with cf.ThreadPoolExecutor(max_workers=cfg.get("concurrency", 5)) as executor:
        futures = [executor.submit(ping_agent, cfg["agent_endpoint"]) for _ in range(samples)]
        for future in futures:
            ok, latency = future.result()
            latencies.append(latency)
            failures += 0 if ok else 1

    latencies.sort()
    p95_index = max(0, int(0.95 * len(latencies)) - 1)
    p95_latency = latencies[p95_index]
    failure_rate = failures / len(latencies)
    print({"p95_latency_seconds": p95_latency, "failure_rate": failure_rate})
    assert p95_latency <= thresholds["p95_latency_seconds"]
    assert failure_rate <= thresholds["failure_rate"]
