# server.py
import io
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Union

import requests

try:
    from mcp.server import Server as MCPServer
    _MCP_IMPORT_ERROR = None
except ImportError as _exc:  # pragma: no cover - triggered only when MCP is absent
    _MCP_IMPORT_ERROR = _exc

    class MCPServer:  # type: ignore[override]
        """Minimal stub so the module remains importable without MCP installed."""

        def __init__(self, *args, **kwargs) -> None:
            self._error = _MCP_IMPORT_ERROR

        def resource(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

        def tool(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

        def run(self) -> None:
            raise RuntimeError(
                "Model Context Protocol (modelcontextprotocol) is not installed."
            ) from self._error


Server = MCPServer

# ---------- config ----------
BASE_DIR = Path(__file__).parent
DATA_DIR = (BASE_DIR / "data").resolve()
REPO_DIR = DATA_DIR / "repo"  # extraction target
REPO_DIR.mkdir(parents=True, exist_ok=True)

GAZETTEER_PATH = BASE_DIR / "gazetteer.txt"
DEFAULT_BRANCHES = ("main", "master")

# simple secret patterns (expand as needed)
SECRET_REGEXES = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*([A-Za-z0-9/+=]{40})",
    "Generic API Key": r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
    ".env style": r"^[A-Z0-9_]{2,}=\S+",
}

server = Server("trustbench-mcp")


# --------- helpers ----------
def _http_get(url: str) -> requests.Response:
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    return response


def _download_zip_to_memory(url: str) -> bytes:
    return _http_get(url).content


def _ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _extract_zip_bytes(zip_bytes: bytes, destination: Path) -> None:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        archive.extractall(destination)


def _repo_zip_url(repo_url: str) -> str:
    # normalize https://github.com/org/repo(.git)?
    base = repo_url[:-4] if repo_url.endswith(".git") else repo_url
    return f"{base}/archive/refs/heads/{{branch}}.zip"


def _iter_files(root: Path, exts: Union[List[str], None] = None):
    for path in root.rglob("*"):
        if path.is_file():
            if not exts or path.suffix.lower() in exts:
                yield path


def _load_gazetteer() -> List[str]:
    if not GAZETTEER_PATH.exists():
        return []
    return [
        line.strip()
        for line in GAZETTEER_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# --------- resources ----------
@server.resource("trustbench/repo_root")
def repo_root() -> str:
    """Absolute path of the extracted repository root (for debugging/visibility)."""
    return str(REPO_DIR)


@server.resource("trustbench/gazetteer")
def gazetteer_terms() -> Dict[str, List[str]]:
    """Current gazetteer terms loaded by the server."""
    return {"terms": _load_gazetteer()}


# --------- tools ----------
@server.tool("download_and_extract_repo")
def download_and_extract_repo(repo_url: str) -> Dict[str, str]:
    """
    Download a GitHub repository zip (main/master) and extract to ./data/repo.
    Args:
      repo_url: Full GitHub repo URL (https://github.com/org/repo[.git])
    Returns:
      {"status": "ok", "repo_dir": "..."} OR {"status": "error", "message": "..."}
    """
    try:
        _ensure_clean_dir(REPO_DIR)
        template = _repo_zip_url(repo_url)
        last_error: Exception | None = None
        for branch in DEFAULT_BRANCHES:
            try:
                blob = _download_zip_to_memory(template.format(branch=branch))
                _extract_zip_bytes(blob, REPO_DIR)
                # many GitHub zips nest everything under one top-level folder; flatten once
                children = list(REPO_DIR.iterdir())
                if len(children) == 1 and children[0].is_dir():
                    tmp_dir = REPO_DIR / "__tmp__"
                    children[0].rename(tmp_dir)
                    for item in tmp_dir.iterdir():
                        shutil.move(str(item), REPO_DIR / item.name)
                    tmp_dir.rmdir()
                return {"status": "ok", "repo_dir": str(REPO_DIR)}
            except Exception as error:  # noqa: BLE001 - surface after both branches
                last_error = error
        return {"status": "error", "message": f"Failed both main/master: {last_error}"}
    except Exception as error:  # noqa: BLE001
        return {"status": "error", "message": str(error)}


@server.tool("env_content")
def env_content(dir_path: str | None = None) -> Dict[str, Union[str, List[str]]]:
    """
    Locate and return content of any .env files under dir_path (defaults to repo).
    Returns:
      {"found": [...], "samples": [{"path": "...", "head": "first lines"}]}
    """
    root = Path(dir_path) if dir_path else REPO_DIR
    found: List[str] = []
    samples: List[Dict[str, str]] = []
    for path in _iter_files(root):
        if path.name == ".env":
            found.append(str(path))
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                samples.append(
                    {"path": str(path), "head": "\n".join(text.splitlines()[:20])}
                )
            except Exception:  # noqa: BLE001
                continue
    return {"found": found, "samples": samples}


@server.tool("secrets_scan")
def secrets_scan(dir_path: str | None = None,
                 max_bytes: int = 500_000) -> Dict[str, List[Dict[str, str]]]:
    """
    Regex-based scan for likely secrets in the repo (lightweight baseline).
    Args:
      dir_path: optional root (defaults to extracted repo)
      max_bytes: per-file cap to avoid huge reads
    Returns:
      {"findings": [{"file": "...", "kind": "AWS Access Key", "line": "..."}]}
    """
    root = Path(dir_path) if dir_path else REPO_DIR
    findings: List[Dict[str, str]] = []
    compiled = {name: re.compile(pattern, re.M) for name, pattern in SECRET_REGEXES.items()}
    gazetteer_terms = _load_gazetteer()

    for file_path in _iter_files(root, exts=None):
        try:
            if file_path.stat().st_size > max_bytes:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")

            for term in gazetteer_terms:
                if term and term.lower() in text.lower():
                    findings.append(
                        {"file": str(file_path), "kind": f"Gazetteer: {term}", "line": ""}
                    )

            for kind, pattern in compiled.items():
                for match in pattern.finditer(text):
                    line_end = text.find("\n", match.start())
                    if line_end == -1:
                        line_end = len(text)
                    line_text = text[match.start(): line_end]
                    findings.append(
                        {
                            "file": str(file_path),
                            "kind": kind,
                            "line": line_text.strip()[:300],
                        }
                    )
        except Exception:  # noqa: BLE001
            continue
    return {"findings": findings}


@server.tool("grep")
def grep(pattern: str,
         dir_path: str | None = None,
         ignore_case: bool = True) -> List[Dict[str, str]]:
    """
    Grep-like search across repo.
    Returns: [{"file": "...", "line_no": "...", "line": "..."}]
    """
    root = Path(dir_path) if dir_path else REPO_DIR
    flags = re.I if ignore_case else 0
    regex = re.compile(pattern, flags)
    results: List[Dict[str, str]] = []

    for file_path in _iter_files(root, exts=[".py", ".md", ".txt", ".json", ".yml", ".yaml", ".env"]):
        try:
            for idx, line in enumerate(file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if regex.search(line):
                    results.append(
                        {"file": str(file_path), "line_no": str(idx), "line": line[:300]}
                    )
        except Exception:  # noqa: BLE001
            continue
    return results


if __name__ == "__main__":
    server.run()
