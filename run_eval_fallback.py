"""Run evaluation with fallback scoring (no RAGAS) to avoid async issues."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path('.env'))

# Use fake provider to avoid RAGAS hanging
os.environ['TRUSTBENCH_FAKE_PROVIDER'] = '1'

print("=" * 60)
print("TrustBench Evaluation - Fallback Scoring Mode")
print("=" * 60)
print("Using deterministic fallback scorer (avoids RAGAS async issues)")
print()

from trustbench_core.eval.orchestrator import run_all

print("Starting evaluation...")
results = run_all()

print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)

for pillar, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {pillar.upper()}: {status}")

print("\nMetrics saved to: trustbench_core/eval/runs/latest/")
print("Refresh the web UI to see updated scores.")
