import os
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_CFG = PROJECT_ROOT / "trustbench_core" / "eval" / "eval_config.yaml"
os.environ.setdefault("EVAL_CFG", str(DEFAULT_CFG))

DEFAULT_RUNS = PROJECT_ROOT / "trustbench_core" / "eval" / "runs" / "latest"
os.environ.setdefault("METRICS_DIR", str(DEFAULT_RUNS))
os.environ.setdefault("TRUSTBENCH_FAKE_PROVIDER", "1")
