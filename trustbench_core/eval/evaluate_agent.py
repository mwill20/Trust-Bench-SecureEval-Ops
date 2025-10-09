# eval/evaluate_agent.py
import sys, pathlib
from .utils import load_config, section, green, red
from .orchestrator import run_all

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = ROOT / "eval" / "eval_config.yaml"

def main():
    cfg = load_config(CFG)
    print(section("TrustBench Core - Evaluation Suite"))
    print("Agent:", cfg["agent_endpoint"])
    print("Dataset:", cfg["dataset_path"])
    results = run_all()
    failed = [k for k,v in results.items() if not v]
    print(section("Summary"))
    if failed:
        print(red("FAILED pillars: " + ", ".join(failed)))
        sys.exit(1)
    print(green("All pillars passed"))
    sys.exit(0)

if __name__ == "__main__":
    main()
