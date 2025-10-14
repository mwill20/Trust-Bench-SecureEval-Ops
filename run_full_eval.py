"""Run full TrustBench evaluation with real OpenAI provider."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment from .env
load_dotenv(Path('.env'))

# Force real provider
os.environ['TRUSTBENCH_FAKE_PROVIDER'] = '0'

print("=" * 60)
print("TrustBench Evaluation - Real Provider Mode")
print("=" * 60)
print(f"OpenAI Key: {'✓ Present' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
print(f"Provider: {os.getenv('TRUST_BENCH_LLM_PROVIDER', 'not set')}")
print(f"Fake Provider: {os.getenv('TRUSTBENCH_FAKE_PROVIDER')}")
print()

# Import after env is set
from trustbench_core.eval.orchestrator import run_all

print("Starting full evaluation suite...")
print("This will test: Task Fidelity, System Performance, Security, Ethics")
print()

try:
    results = run_all()
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    for pillar, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {pillar.upper()}: {status}")
    
    print("\nMetrics saved to: trustbench_core/eval/runs/latest/")
    print("Refresh the web UI to see updated scores.")
    
except KeyboardInterrupt:
    print("\n\nEvaluation interrupted by user.")
    sys.exit(1)
except Exception as e:
    print(f"\n\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
