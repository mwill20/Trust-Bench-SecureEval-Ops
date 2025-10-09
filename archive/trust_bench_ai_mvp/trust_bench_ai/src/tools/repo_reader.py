\
import os, tempfile, subprocess, shutil, pathlib
from typing import Dict, List
from ..security_utils import ALLOWLIST_EXTS

def _is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://") or s.endswith(".git")

def _shallow_clone(url: str) -> str:
    tmp = tempfile.mkdtemp(prefix="trust_bench_repo_")
    try:
        subprocess.check_call(["git", "clone", "--depth", "1", url, tmp])
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return tmp

def load_repo(state: Dict) -> Dict:
    """Fetch repo (URL or local path), walk allowlisted files, store in state['files']."""
    repo = state.get("repo")
    max_files = int(state.get("max_files", 200))
    if not repo:
        raise ValueError("Missing 'repo' in state")
    # Clone if needed
    root = _shallow_clone(repo) if _is_url(repo) else repo
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = pathlib.Path(dirpath) / fn
            if p.suffix.lower() in ALLOWLIST_EXTS:
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                rel = str(p)
                files.append({"path": rel, "text": txt})
                if len(files) >= max_files:
                    break
        if len(files) >= max_files:
            break
    state["files"] = files
    state["repo_root"] = root
    return state
