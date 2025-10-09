
import json, pathlib
from typing import Dict, List

def load_fixtures(state: Dict, fixtures_root: str = 'fixtures') -> Dict:
    """Load local fixtures into the pipeline state.
    Supported layout: fixtures/repos/*, fixtures/logs/*.jsonl, fixtures/intel/vt_stub.json"""
    root = pathlib.Path(fixtures_root)
    files = []
    # repos
    repos_dir = root / 'repos'
    if repos_dir.exists():
        for repo in repos_dir.iterdir():
            if repo.is_dir():
                repo_files = []
                for p in repo.rglob('*'):
                    if p.is_file():
                        try:
                            txt = p.read_text(encoding='utf-8', errors='ignore')
                        except Exception:
                            continue
                        repo_files.append({'path': str(p.relative_to(repo)), 'full_path': str(p), 'text': txt})
                files.append({'repo_name': repo.name, 'files': repo_files})
    state.setdefault('fixture_repos', files)
    # logs
    logs_dir = root / 'logs'
    logs = []
    if logs_dir.exists():
        for lf in logs_dir.glob('*.jsonl'):
            with lf.open('r', encoding='utf-8') as fh:
                for line in fh:
                    try:
                        logs.append(json.loads(line.strip()))
                    except Exception:
                        logs.append({'raw': line.strip()})
    state['fixture_logs'] = logs
    # intel
    intel_file = root / 'intel' / 'vt_stub.json'
    if intel_file.exists():
        try:
            with intel_file.open('r', encoding='utf-8') as fh:
                state['fixture_vt'] = json.load(fh)
        except Exception:
            state['fixture_vt'] = {}
    return state
