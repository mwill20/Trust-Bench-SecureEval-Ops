#!/usr/bin/env python3
"""Lightweight secret scanner for use in pre-commit hooks.

This intentionally avoids third-party dependencies so it can run in
constrained environments. The script scans text files that are about to be
committed for patterns that commonly indicate leaked credentials.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Iterable, Sequence


# Files that are safe to ignore (templates, documentation examples, etc.).
SKIP_SUFFIXES = (
    ".example",
    ".sample",
    ".tmpl",
    ".template",
    ".md",
    ".rst",
    ".txt",
)

# Regular expressions targeting high-signal secrets. These are curated to be
# precise enough to avoid false positives while still catching common mistakes.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    ),
    (
        "AWS access key",
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ),
    (
        "AWS secret key assignment",
        re.compile(r"aws[_-]*secret[_-]*access[_-]*key\s*=\s*[\"']?[A-Za-z0-9/+=]{40}[\"']?", re.IGNORECASE),
    ),
    (
        "Generic API key or token",
        re.compile(
            r"(api[_-]*key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{32,}[\"']?",
            re.IGNORECASE,
        ),
    ),
    (
        "Slack token",
        re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
    ),
    (
        "Google API key",
        re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    ),
    (
        "GitHub token",
        re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
    ),
)


def run_git_command(args: Sequence[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def staged_files() -> list[pathlib.Path]:
    output = run_git_command(["diff", "--name-only", "--cached"])
    if not output:
        return []
    return [pathlib.Path(line) for line in output.splitlines() if line]


def is_binary(path: pathlib.Path) -> bool:
    try:
        with path.open("rb") as handle:
            chunk = handle.read(1024)
    except OSError:
        return False
    return b"\0" in chunk


def should_skip(path: pathlib.Path) -> bool:
    return path.suffix in SKIP_SUFFIXES


def find_secret_matches(path: pathlib.Path) -> list[str]:
    if is_binary(path) or should_skip(path):
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Assume binary if it cannot be decoded cleanly.
        return []
    except OSError:
        return []

    matches: list[str] = []
    for reason, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(content):
            # Show a short preview of the offending string.
            snippet = content[match.start() : match.end()]
            matches.append(f"{reason}: {snippet[:80]}")
    return matches


def scan_paths(paths: Iterable[pathlib.Path]) -> dict[pathlib.Path, list[str]]:
    findings: dict[pathlib.Path, list[str]] = {}
    for path in paths:
        if not path.exists():
            # Deleted files will not leak new secrets.
            continue
        matches = find_secret_matches(path)
        if matches:
            findings[path] = matches
    return findings


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Abort commits when potential secrets are detected."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional list of files to scan (defaults to staged files).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    namespace = parse_args(argv or sys.argv[1:])
    if namespace.paths:
        paths = [pathlib.Path(path) for path in namespace.paths]
    else:
        paths = staged_files()

    findings = scan_paths(paths)
    if not findings:
        return 0

    print("Potential secrets detected; commit aborted.\n", file=sys.stderr)
    for path, matches in findings.items():
        for match in matches:
            print(f"- {path}: {match}", file=sys.stderr)
    print(
        "\nIf these are false positives, adjust the scanner in scripts/scan_for_secrets.py "
        "or mask the values before committing.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
