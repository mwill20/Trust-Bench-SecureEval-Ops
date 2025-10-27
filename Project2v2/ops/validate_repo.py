"""Repository validator enforcing Project 3 rubric thresholds."""

from __future__ import annotations

from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def check_exists(path: Path) -> bool:
    return path.exists()


def main() -> int:
    categories: dict[str, list[bool]] = {
        "docs": [],
        "tests": [],
        "automation": [],
    }

    readme = read_text(ROOT / "README.md")
    categories["docs"].append("Phase 2: Ops Layer" in readme)
    categories["docs"].append("Production Enhancements" in readme)

    operations = read_text(PROJECT / "OPERATIONS.md")
    categories["docs"].append("Structured Logging" in operations or "JSON" in operations)
    categories["docs"].append("/healthz" in operations and "/readyz" in operations)

    security = read_text(PROJECT / "SECURITY.md")
    categories["docs"].append("Guardrails" in security or "Input Validation" in security)
    categories["docs"].append("Sensitive Data Redaction" in security)

    categories["tests"].append(check_exists(PROJECT / "tests" / "test_parity.py"))
    categories["tests"].append(check_exists(PROJECT / "tests" / "test_secure_eval.py"))
    categories["tests"].append(check_exists(PROJECT / "tests" / "test_ops_layer.py"))
    categories["tests"].append(check_exists(PROJECT / "tests" / "fixtures" / "report.json"))

    workflow = ROOT / ".github" / "workflows" / "python-ci.yml"
    categories["automation"].append(workflow.exists())

    validator_path = PROJECT / "ops" / "validate_repo.py"
    categories["automation"].append(validator_path.exists())

    scores: dict[str, float] = {}
    for name, results in categories.items():
        if results:
            scores[name] = sum(results) / len(results) * 100
        else:
            scores[name] = 0

    overall = sum(scores.values()) / len(scores)

    print("Repository Validation Summary")
    for name, value in scores.items():
        print(f"  {name:>11}: {value:5.1f} %")
    print(f"  {'overall':>11}: {overall:5.1f} %")

    if overall < 80 or any(value < 50 for value in scores.values()):
        print("Validator thresholds not met (>=80 overall, >=50 per category).")
        return 1

    print("All thresholds satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
