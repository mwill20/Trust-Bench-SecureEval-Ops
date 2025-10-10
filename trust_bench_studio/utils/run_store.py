"""Helpers for listing and inspecting evaluation runs."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from numbers import Number
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .config import PROJECT_ROOT, get_runs_dir

METRIC_FILES: Tuple[str, ...] = ("metrics.json", "summary.json", "report.json")
TRACE_FILES: Tuple[str, ...] = ("run.json", "trace.json", "agents.json")


@dataclass(frozen=True)
class RunRecord:
    """Metadata for a stored evaluation run."""

    name: str
    path: Path

    def __str__(self) -> str:  # pragma: no cover - convenience for UI selections
        return self.name


@dataclass(frozen=True)
class RunSummary:
    """Normalized representation of evaluation artifacts for UI consumption."""

    metrics: Dict[str, float] = field(default_factory=dict)
    agents: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_metrics(self) -> bool:
        return bool(self.metrics)

    @property
    def has_agents(self) -> bool:
        return bool(self.agents)


def list_runs(search_roots: Iterable[Path] | None = None) -> List[RunRecord]:
    """Collect run records from disk."""
    roots: List[Path] = list(search_roots or [get_runs_dir()])
    records: List[RunRecord] = []

    for root in roots:
        if not root.exists():
            continue

        for candidate in sorted(root.iterdir(), reverse=True):
            if candidate.is_dir():
                records.append(RunRecord(name=candidate.name, path=candidate.resolve()))

        latest_entry = root / "latest"
        if latest_entry.exists():
            resolved = latest_entry.resolve() if latest_entry.is_symlink() else latest_entry
            if resolved.is_dir():
                record = RunRecord(name="latest", path=resolved.resolve())
                if record not in records:
                    records.insert(0, record)

    return records


def _load_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _first_existing(run_path: Path, candidates: Sequence[str]) -> Optional[Path]:
    for name in candidates:
        candidate = run_path / name
        if candidate.exists():
            return candidate
    return None


def _collect_numeric(node: Any, *, prefix: str = "", depth: int = 0, limit: int = 32) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    def walk(value: Any, key_prefix: str, current_depth: int) -> None:
        if len(metrics) >= limit:
            return
        if isinstance(value, Number):
            label = key_prefix or "value"
            metrics.setdefault(label, float(value))
            return
        if isinstance(value, dict) and current_depth < 3:
            for sub_key, sub_value in value.items():
                new_prefix = f"{key_prefix}.{sub_key}" if key_prefix else str(sub_key)
                walk(sub_value, new_prefix, current_depth + 1)
        elif isinstance(value, list) and current_depth < 2:
            for index, item in enumerate(value[:8]):
                new_prefix = f"{key_prefix}[{index}]" if key_prefix else str(index)
                walk(item, new_prefix, current_depth + 1)

    walk(node, prefix, depth)
    return metrics


def _extract_metrics(doc: Optional[dict]) -> Dict[str, float]:
    if not isinstance(doc, dict):
        return {}

    for key in ("metrics", "scores", "overall", "summary", "aggregates"):
        if key in doc and isinstance(doc[key], dict):
            metrics = _collect_numeric(doc[key], prefix=key)
            if metrics:
                return metrics

    metrics = {
        name: float(value)
        for name, value in doc.items()
        if isinstance(value, Number)
    }
    if metrics:
        return metrics

    return _collect_numeric(doc)


def _normalize_tools(raw: Any) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, (list, tuple, set)):
        items = list(raw)
    else:
        items = [raw]
    return sorted({str(item) for item in items if item})


def _merge_transcript(existing: str, new_entry: Any) -> str:
    text = str(new_entry).strip()
    if not text:
        return existing
    if not existing:
        return text
    if text in existing:
        return existing
    return "\n".join([existing, text])


def _status_from_event(value: Any, default: str) -> str:
    if not value:
        return default
    status_text = str(value).lower()
    if any(keyword in status_text for keyword in ("fail", "error", "exception")):
        return "error"
    if any(keyword in status_text for keyword in ("complete", "finished", "success", "done")):
        return "complete"
    if any(keyword in status_text for keyword in ("start", "run", "active", "processing")):
        return "active"
    return status_text or default


def _extract_agents(doc: Optional[dict]) -> List[Dict[str, Any]]:
    if not isinstance(doc, dict):
        return []

    agent_sources = []
    for key in ("agents", "agent_reports"):
        if key in doc and isinstance(doc[key], list):
            agent_sources.extend(doc[key])

    if agent_sources:
        normalized = []
        for raw_agent in agent_sources:
            if not isinstance(raw_agent, dict):
                continue
            name = str(
                raw_agent.get("name")
                or raw_agent.get("id")
                or raw_agent.get("agent_id")
                or "Agent"
            )
            status = _status_from_event(raw_agent.get("status") or raw_agent.get("state"), "idle")
            transcript = str(
                raw_agent.get("summary")
                or raw_agent.get("message")
                or raw_agent.get("output")
                or ""
            )
            tools = _normalize_tools(raw_agent.get("tools") or raw_agent.get("tool_calls"))
            normalized.append(
                {
                    "name": name,
                    "status": status,
                    "tools": tools,
                    "transcript": transcript,
                }
            )
        if normalized:
            return normalized

    events = doc.get("events")
    if not isinstance(events, list):
        return []

    aggregated: Dict[str, Dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        agent_name = str(
            event.get("agent")
            or event.get("agent_name")
            or event.get("name")
            or event.get("actor")
            or "Agent"
        )
        record = aggregated.setdefault(
            agent_name,
            {"name": agent_name, "status": "idle", "tools": [], "transcript": ""},
        )

        record["status"] = _status_from_event(
            event.get("status") or event.get("event") or event.get("type"),
            record["status"],
        )

        tool = event.get("tool") or event.get("tool_name")
        tool_calls = event.get("tools") or event.get("tool_calls")
        merged_tools = set(record["tools"])
        for item in _normalize_tools(tool_calls or (tool and [tool])):
            merged_tools.add(item)
        record["tools"] = sorted(merged_tools)

        for key in ("content", "message", "output", "text", "summary"):
            if key in event:
                record["transcript"] = _merge_transcript(record["transcript"], event[key])

    return list(aggregated.values())


def load_run_summary(run_path: Path) -> Optional[RunSummary]:
    """Load summary data for the given run directory."""
    metrics_path = _first_existing(run_path, METRIC_FILES)
    trace_path = _first_existing(run_path, TRACE_FILES)

    metrics_doc = _load_json(metrics_path) if metrics_path else None
    trace_doc = _load_json(trace_path) if trace_path else None

    metrics = _extract_metrics(metrics_doc) or _extract_metrics(trace_doc)
    agents = _extract_agents(trace_doc or metrics_doc)

    if not metrics and not agents and not (metrics_doc or trace_doc):
        fallback_path = _first_existing(run_path, tuple(str(p.name) for p in run_path.glob("*.json")))
        if fallback_path:
            fallback_doc = _load_json(fallback_path)
            metrics = _extract_metrics(fallback_doc)
            agents = _extract_agents(fallback_doc)
            trace_doc = trace_doc or fallback_doc
            metrics_doc = metrics_doc or fallback_doc

    raw_payload = {
        "metrics": metrics_doc,
        "trace": trace_doc,
    }

    if not any(raw_payload.values()):
        return None

    return RunSummary(metrics=metrics, agents=agents, raw=raw_payload)


def diff_metrics(
    baseline: Mapping[str, float] | None,
    candidate: Mapping[str, float] | None,
) -> Dict[str, Tuple[Optional[float], Optional[float], Optional[float]]]:
    """Compute metric deltas between two runs."""
    keys = set()
    if baseline:
        keys.update(baseline.keys())
    if candidate:
        keys.update(candidate.keys())

    deltas: Dict[str, Tuple[Optional[float], Optional[float], Optional[float]]] = {}
    for key in sorted(keys):
        base = float(baseline[key]) if baseline and key in baseline else None
        cand = float(candidate[key]) if candidate and key in candidate else None
        delta = (cand - base) if (base is not None and cand is not None) else None
        deltas[key] = (base, cand, delta)

    return deltas


def trigger_evaluation(profile_path: Path) -> subprocess.Popen[str] | None:
    """Launch a background evaluation for the selected profile."""
    eval_script = PROJECT_ROOT / "scripts" / "run_profile_eval.py"
    if not eval_script.exists():
        return None

    command: Sequence[str] = [
        "python",
        str(eval_script),
        "--profile",
        str(profile_path),
    ]

    try:
        return subprocess.Popen(command, cwd=PROJECT_ROOT, text=True)
    except OSError:
        return None
