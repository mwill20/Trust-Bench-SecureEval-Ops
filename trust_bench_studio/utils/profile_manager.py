"""Profile discovery and loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from .config import PROFILES_DIR

PROFILE_EXTENSIONS = (".json", ".yaml", ".yml")


def list_profiles(extra_dirs: Iterable[Path] | None = None) -> List[Path]:
    """Return available profile files, sorted alphabetically."""
    search_roots: List[Path] = [PROFILES_DIR]
    if extra_dirs:
        search_roots.extend(extra_dirs)

    seen: set[Path] = set()
    results: List[Path] = []

    for root in search_roots:
        if not root.exists():
            continue
        for candidate in sorted(root.iterdir()):
            if candidate.suffix.lower() in PROFILE_EXTENSIONS and candidate.is_file():
                normalized = candidate.resolve()
                if normalized not in seen:
                    seen.add(normalized)
                    results.append(normalized)

    return results


def load_profile(profile_path: Path) -> Optional[dict]:
    """Load a profile document as JSON when possible."""
    try:
        text = profile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    if profile_path.suffix.lower() == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    return None

