from trust_bench_studio.utils.orchestrator_synthesis import synthesize_verdict


def test_veto_and_composite() -> None:
    summary_stub = type(
        "Summary",
        (),
        {
            "metrics": {"faithfulness": 0.9, "avg_latency": 2.0},
            "raw": {"config": {"thresholds": {"warn_threshold": 0.7}}},
            "agents": [],
        },
    )()

    traces = {
        "task": {"score": 0.9, "state": "complete"},
        "system": {"score": 0.8, "state": "complete"},
        "security": {"state": "complete"},
        "ethics": {"state": "complete"},
    }

    verdict = synthesize_verdict(summary_stub, None)
    assert verdict["decision"] in {"pass", "warn", "fail"}
    assert 0.0 <= verdict["composite"] <= 1.0

    summary_stub.metrics["injection_block_rate"] = 0.1
    verdict_fail = synthesize_verdict(summary_stub, None)
    assert verdict_fail["decision"] == "fail"
    assert any("security" in driver.lower() for driver in verdict_fail["drivers"])
