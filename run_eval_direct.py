"""Direct evaluation without pytest to avoid RAGAS hang."""
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment
load_dotenv(Path('.env'))
# DISABLED: Use real LLM provider instead of fake
# os.environ['TRUSTBENCH_FAKE_PROVIDER'] = '1'

print("=" * 60)
print("TrustBench Direct Evaluation")
print("=" * 60)
print("Running agents directly (bypassing pytest)")
print()

from trustbench_core.agents import task_fidelity, system_perf, security_eval, ethics_refusal
from trustbench_core.eval.utils import load_config, write_metric

# Load config
config = load_config('trustbench_core/eval/eval_config.yaml')
metrics_dir = Path('trustbench_core/eval/runs/latest')

# Task Performance
print("=== Task Performance ===")
task_result = task_fidelity.run(config, metrics_dir / 'task_direct')
write_metric(str(metrics_dir), 'task_metrics', task_result['metrics'])
print(f"  Faithfulness: {task_result['metrics']['faithfulness']:.2f}")
print(f"  Samples: {task_result['metrics']['samples']}")
print(f"  Failures: {len(task_result['failures'])}")

# System Performance
print("\n=== System Performance ===")
system_result = system_perf.run(config, metrics_dir / 'system_direct')
write_metric(str(metrics_dir), 'system_metrics', system_result['metrics'])
print(f"  Mean Latency: {system_result['metrics']['mean_latency']:.4f}s")
print(f"  P95 Latency: {system_result['metrics']['p95_latency']:.4f}s")

# Security
print("\n=== Security & Robustness ===")
security_result = security_eval.run(config, metrics_dir / 'security_direct')
write_metric(str(metrics_dir), 'security_metrics', security_result['metrics'])
print(f"  Injection Block Rate: {security_result['metrics']['injection_block_rate']:.2f}")
print(f"  Secret Findings: {security_result['metrics']['secret_findings']}")

# Ethics
print("\n=== Ethics & Alignment ===")
ethics_result = ethics_refusal.run(config, metrics_dir / 'ethics_direct')
write_metric(str(metrics_dir), 'ethics_metrics', ethics_result['metrics'])
print(f"  Refusal Accuracy: {ethics_result['metrics']['refusal_accuracy']:.2f}")

# Combine metrics
all_metrics = {}
all_metrics.update(task_result['metrics'])
all_metrics.update(system_result['metrics'])
all_metrics.update(security_result['metrics'])
all_metrics.update(ethics_result['metrics'])
# Note: fake_provider flag comes from individual agent metrics

# Write combined metrics
with open(metrics_dir / 'metrics.json', 'w') as f:
    json.dump(all_metrics, f, indent=2)

# Write gate status
failures = {
    'task': len(task_result['failures']) > 0,
    'system': len(system_result['failures']) > 0,
    'security': len(security_result['failures']) > 0,
    'ethics': len(ethics_result['failures']) > 0,
}

with open(metrics_dir / 'gate.json', 'w') as f:
    json.dump({
        'blocked': any(failures.values()),
        'failed': [k for k, v in failures.items() if v]
    }, f, indent=2)

print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)
print("\nResults:")
for pillar, failed in failures.items():
    status = "✗ FAIL" if failed else "✓ PASS"
    print(f"  {pillar.upper()}: {status}")

print(f"\nMetrics written to: {metrics_dir}")
print("Refresh the web UI to see updated scores!")
