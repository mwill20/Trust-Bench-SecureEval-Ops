# eval/utils.py
import os, subprocess, yaml, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_pytest(path, extra_env=None):
    env = os.environ.copy()
    env.update(extra_env or {})
    target = pathlib.Path(path)
    if not target.is_absolute():
        target = ROOT / target
    return subprocess.call(
        ["pytest", "-q", str(target)],
        cwd=str(ROOT),
        env=env,
    )

def section(title: str) -> str:
    return f"\n=== {title} ==="


def green(text: str) -> str:
    return text


def red(text: str) -> str:
    return text

def write_metric(metrics_dir, name, payload):
    p = pathlib.Path(metrics_dir); p.mkdir(parents=True, exist_ok=True)
    with open(p / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
