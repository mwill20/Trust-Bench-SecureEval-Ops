"""Run task fidelity evaluation with real provider (not fake)."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path('.env'))

# Force real provider
os.environ['TRUSTBENCH_FAKE_PROVIDER'] = '0'

print("Configuration:")
print(f"  OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"  TRUSTBENCH_FAKE_PROVIDER: {os.getenv('TRUSTBENCH_FAKE_PROVIDER')}")
print(f"  TRUST_BENCH_LLM_PROVIDER: {os.getenv('TRUST_BENCH_LLM_PROVIDER')}")
print()

from trustbench_core.eval.utils import load_config, write_metric
from trustbench_core.agents import task_fidelity

profile = load_config('trustbench_core/eval/eval_config.yaml')
workdir = Path('trustbench_core/eval/runs/latest_real')
workdir.mkdir(parents=True, exist_ok=True)

print("Running task fidelity evaluation with real provider...")
print(f"Dataset: {profile.get('dataset_path', 'default')}")
print(f"Sampling: {profile.get('sampling', {})}")
print()

try:
    result = task_fidelity.run(profile, workdir)
    
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print("\nMetrics:")
    for key, value in result['metrics'].items():
        print(f"  {key}: {value}")
    
    print(f"\nFailures: {len(result['failures'])}")
    if result['failures']:
        print("\nFailure details:")
        for f in result['failures']:
            print(f"  - ID: {f.get('id', 'N/A')}")
            print(f"    Reason: {f['reason']}")
            print(f"    Score: {f['score']}")
            print(f"    Answer: {f.get('answer', 'N/A')[:200]}...")
            print()
    
    # Check details file
    details_file = workdir / 'task_fidelity_details.json'
    if details_file.exists():
        import json
        details = json.loads(details_file.read_text())
        print("\nDetailed answers:")
        for d in details:
            print(f"\n  Question: {d['question']}")
            print(f"  Truth: {d.get('truth', 'N/A')}")
            print(f"  Answer: {d.get('answer', 'N/A')}")
            print(f"  Score: {d['score']}")
    
    # Write metrics to the standard location for the web UI
    write_metric('trustbench_core/eval/runs/latest', 'task_metrics', result['metrics'])
    print("\nMetrics written to: trustbench_core/eval/runs/latest/task_metrics.json")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
