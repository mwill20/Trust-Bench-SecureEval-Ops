"""Simple test to verify OpenAI+RAGAS works with actual API calls."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Verify
print("Environment check:")
print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗ MISSING'}")
print(f"  GROQ_API_KEY: {'✓' if os.getenv('GROQ_API_KEY') else '✗ MISSING'}")
print(f"  TRUST_BENCH_LLM_PROVIDER: {os.getenv('TRUST_BENCH_LLM_PROVIDER', 'not set')}")
print()

# Force real provider
os.environ['TRUSTBENCH_FAKE_PROVIDER'] = '0'

# Quick RAGAS test with minimal dataset
from trustbench_core.agents.task_fidelity import _score_with_ragas

rows = [
    {"question": "What is vector search?", "truth": "Vector search retrieves items by similarity in embedding space."},
]
answers = ["Vector search finds similar items using embeddings and distance metrics."]

print("Testing RAGAS scoring with 1 sample...")
try:
    scores, meta = _score_with_ragas(rows, answers)
    print(f"\n✓ RAGAS Success!")
    print(f"  Score: {scores[0]}")
    print(f"  Meta: {meta}")
except Exception as e:
    print(f"\n✗ RAGAS Failed: {e}")
    import traceback
    traceback.print_exc()
