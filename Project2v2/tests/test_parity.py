"""Golden parity tests locking current behavior."""

from __future__ import annotations

import json
import zipfile
from hashlib import sha256
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
OUTPUT = Path(__file__).resolve().parent.parent / "output"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_report_json_parity() -> None:
    """Ensure the current JSON report structure matches the frozen baseline."""
    current = _read_json(OUTPUT / "report.json")
    golden = _read_json(FIXTURES / "report.json")

    assert set(current.keys()) == set(golden.keys())
    assert current.get("summary") == golden.get("summary")


def test_report_markdown_signature() -> None:
    """Markdown report diffusion should remain stable at the byte level."""
    current_sha = _file_sha(OUTPUT / "report.md")
    golden_sha = _file_sha(FIXTURES / "report.md")
    assert current_sha == golden_sha


def test_bundle_integrity() -> None:
    """ZIP bundle must expose the exact same top-level artifacts."""
    fixture_bundle = FIXTURES / "bundle.zip"
    current_bundle = OUTPUT / "bundle.zip"

    with zipfile.ZipFile(fixture_bundle, "r") as golden_zip, zipfile.ZipFile(current_bundle, "r") as current_zip:
        golden_names = {Path(info.filename).name for info in golden_zip.infolist()}
        current_names = {Path(info.filename).name for info in current_zip.infolist()}
        assert current_names == golden_names

        for filename in {"report.json", "report.md"} & golden_names:
            assert current_zip.read(filename) == golden_zip.read(filename)
