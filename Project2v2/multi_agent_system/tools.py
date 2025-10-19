"""Standalone tools that extend the capabilities of the agents."""

from __future__ import annotations

import json
import math
import re
import os
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .types import ToolResult

SECRET_PATTERNS: Dict[str, str] = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "GitHub Token": r"gh[pousr]_[0-9A-Za-z]{36}",
    "Slack Token": r"xox[baprs]-[0-9A-Za-z-]{10,60}",
    "Private RSA Key": r"-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----",
}


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
}


def _iter_repo_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


def run_secret_scan(repo_root: Path, max_file_mb: float = 1.5) -> ToolResult:
    """Scan repository files for high-signal secret patterns."""
    limit_bytes = max_file_mb * 1024 * 1024
    matches = []
    scanned = 0

    for file_path in _iter_repo_files(repo_root):
        try:
            if file_path.stat().st_size > limit_bytes:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            scanned += 1
        except OSError:
            continue

        for label, pattern in SECRET_PATTERNS.items():
            match = re.search(pattern, text)
            if not match:
                continue
            span = match.span()
            start = max(span[0] - 40, 0)
            end = min(span[1] + 40, len(text))
            snippet = text[start:end].replace("\n", "\\n")
            matches.append({"file": str(file_path), "pattern": label, "snippet": snippet})
            break

    score = max(0.0, 100.0 - len(matches) * 20.0)
    summary = (
        f"Scanned {scanned} files and detected {len(matches)} potential secret hit(s)."
        if matches
        else f"Scanned {scanned} files with no high-confidence secret matches."
    )
    return ToolResult(
        name="secret_scan",
        score=score,
        summary=summary,
        details={"matches": matches, "scanned": scanned},
    )


LANGUAGE_EXTENSIONS: Dict[str, Tuple[str, ...]] = {
    "python": (".py", ".pyw"),
    "typescript": (".ts", ".tsx"),
    "javascript": (".js", ".jsx", ".mjs"),
    "markdown": (".md", ".mdx"),
    "yaml": (".yml", ".yaml"),
    "json": (".json",),
}


def _classify_language(path: Path) -> str:
    for language, suffixes in LANGUAGE_EXTENSIONS.items():
        if path.suffix.lower() in suffixes:
            return language
    return "other"


def analyze_repository_structure(repo_root: Path) -> ToolResult:
    """Compute a language histogram and basic structure heuristics."""
    language_counts: Counter[str] = Counter()
    total_files = 0
    test_files = 0

    for file_path in _iter_repo_files(repo_root):
        total_files += 1
        language = _classify_language(file_path)
        language_counts[language] += 1
        if "test" in file_path.parts or file_path.name.startswith("test_"):
            test_files += 1

    diversity = len([lang for lang, count in language_counts.items() if count > 0])
    diversity_score = min(100.0, 20.0 + diversity * 10.0)
    test_ratio = (test_files / total_files) if total_files else 0.0
    testing_score = min(100.0, test_ratio * 200.0)
    score = round((diversity_score * 0.4) + (testing_score * 0.6), 2)

    summary = (
        f"Indexed {total_files} files across {diversity} language group(s); "
        f"{test_files} appear to be tests."
    )
    details = {
        "language_histogram": dict(language_counts),
        "total_files": total_files,
        "test_files": test_files,
        "test_ratio": round(test_ratio, 3),
    }
    return ToolResult(
        name="repository_structure",
        score=score,
        summary=summary,
        details=details,
    )


def evaluate_documentation(repo_root: Path) -> ToolResult:
    """Inspect documentation assets such as README files."""
    readme_files = sorted(repo_root.glob("README*.md"))
    total_words = 0
    sections = 0

    readme_text: Dict[Path, str] = {}
    for readme in readme_files:
        try:
            text = readme.read_text(encoding="utf-8")
        except OSError:
            continue
        readme_text[readme] = text
        total_words += len(text.split())
        sections += text.count("\n## ")

    lower_texts = [content.lower() for content in readme_text.values()]
    has_quickstart = any("quick start" in content for content in lower_texts)
    has_architecture = any("architecture" in content for content in lower_texts)

    coverage_score = min(100.0, math.log2(total_words + 1) * 12.0 + sections * 5.0)
    bonus = 10.0 if has_quickstart else 0.0
    bonus += 10.0 if has_architecture else 0.0
    score = round(min(100.0, coverage_score + bonus), 2)

    summary = (
        f"Found {len(readme_files)} README file(s) with roughly {total_words} words and {sections} section heading(s)."
        if readme_files
        else "No README markdown files discovered in the repository root."
    )
    details = {
        "readme_paths": [str(path) for path in readme_files],
        "total_words": total_words,
        "sections": sections,
        "has_quickstart": has_quickstart,
        "has_architecture": has_architecture,
    }
    return ToolResult(
        name="documentation_review",
        score=score,
        summary=summary,
        details=details,
    )


def serialize_tool_result(result: ToolResult) -> Dict[str, object]:
    """Convert dataclass results to plain dictionaries for JSON serialization."""
    return asdict(result)
