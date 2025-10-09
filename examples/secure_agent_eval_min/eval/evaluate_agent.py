# eval/evaluate_agent.py
import sys
from pathlib import Path

from .utils import load_config, green, red, section, run_pytest

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "eval" / "eval_config.yaml"

def main() -> None:
    cfg = load_config(CFG)
    print(section("Secure Agent Evaluation - 4 Pillars"))
    print("Agent:", cfg["agent_endpoint"])
    print("Dataset:", cfg["dataset_path"])

    suites = [
        ("Task Performance", "tests/task"),
        ("System Performance", "tests/system"),
        ("Security & Robustness", "tests/security"),
        ("Ethics & Alignment", "tests/ethics"),
    ]

    failures = []
    for name, rel in suites:
        print(section(name))
        target = ROOT / rel
        code = run_pytest(str(target), extra_env={"EVAL_CFG": str(CFG)})
        if code != 0:
            failures.append(name)
            print(red(f"FAIL: {name}"))
        else:
            print(green(f"PASS: {name}"))

    print(section("Summary"))
    if failures:
        print(red("FAILED pillars: " + ", ".join(failures)))
        sys.exit(1)
    print(green("All pillars passed"))
    sys.exit(0)


if __name__ == "__main__":
    main()
