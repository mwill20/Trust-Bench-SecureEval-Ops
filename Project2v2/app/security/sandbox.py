"""Sandbox helpers for controlled subprocess execution."""

from __future__ import annotations

import shlex
import subprocess
from typing import Iterable, Tuple

ALLOWED_CMDS = {"git", "python", "pip"}


def safe_run(command: str | Iterable[str], timeout: int = 20) -> Tuple[int, str, str]:
    """Run a command if and only if it is allowlisted.

    Args:
        command: Shell-style string or iterable of arguments.
        timeout: Maximum number of seconds to wait before aborting.

    Returns:
        (returncode, stdout, stderr)
    """

    if isinstance(command, str):
        parts = shlex.split(command)
    else:
        parts = list(command)

    if not parts:
        return 2, "", "empty command"

    verb = parts[0]
    if verb not in ALLOWED_CMDS:
        return 126, "", f"{verb} not allowed"

    try:
        proc = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
