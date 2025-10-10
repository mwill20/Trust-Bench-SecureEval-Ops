"""Loader utilities for agent manifest metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .config import PROJECT_ROOT

DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "trust_bench_studio" / "config" / "agents_manifest.yaml"


def load_agents_manifest(manifest_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load agent definitions from the manifest YAML file."""
    path = manifest_path or DEFAULT_MANIFEST_PATH
    if not path.exists():
        return []

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "PyYAML is required to parse agents_manifest.yaml. Install it via `pip install pyyaml`."
        ) from exc

    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)

    agents = document.get("agents") if isinstance(document, dict) else None
    if not isinstance(agents, list):
        return []

    return [agent for agent in agents if isinstance(agent, dict)]


def iter_agents(manifest_path: Optional[Path] = None) -> Iterable[Dict[str, Any]]:
    """Yield agent definitions one by one."""
    for agent in load_agents_manifest(manifest_path):
        yield agent

