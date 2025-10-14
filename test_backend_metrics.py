"""Test what the backend is actually loading."""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from trust_bench_studio.utils.run_store import load_run_summary

# Load the latest run
latest_path = Path("trustbench_core/eval/runs/latest")
summary = load_run_summary(latest_path)

print("=== Run Summary ===")
print(f"Metrics: {summary.metrics}")
print(f"\nFaithfulness: {summary.metrics.get('faithfulness', 'NOT FOUND')}")
print(f"\nRaw metrics doc keys: {summary.raw.get('metrics', {}).keys() if summary.raw.get('metrics') else 'NONE'}")
print(f"\nRaw trace doc keys: {summary.raw.get('trace', {}).keys() if summary.raw.get('trace') else 'NONE'}")

# Now test the verdict
from trust_bench_studio.utils.orchestrator_synthesis import synthesize_verdict
verdict = synthesize_verdict(summary, None)

print("\n=== Verdict ===")
print(f"Decision: {verdict['decision']}")
print(f"Composite: {verdict['composite']}")

print("\n=== All Pillars ===")
for name, pillar in verdict['pillars'].items():
    print(f"{name}: {pillar['status']} (score: {pillar['score']})")
    print(f"  {pillar['summary']}")

print("\n=== Hard Fails ===")
print(f"Security hard fail: {verdict.get('hard_fail_security', False)}")
print(f"Ethics hard fail: {verdict.get('hard_fail_ethics', False)}")

print("\n=== Actions ===")
for action in verdict['actions']:
    print(f"  - {action}")
