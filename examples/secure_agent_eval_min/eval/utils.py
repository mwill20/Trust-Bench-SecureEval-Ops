# eval/utils.py
import os, subprocess, yaml

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_pytest(path, extra_env=None):
    env = os.environ.copy()
    env.update(extra_env or {})
    return subprocess.call(["pytest", "-q", path], env=env)

def section(title): return f"\n=== {title} ==="
def green(s): return f"\033[92m{s}\033[0m"
def red(s):   return f"\033[91m{s}\033[0m"
