import os
import pathlib
import sys

EXAMPLE_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_ROOT))

DEFAULT_CFG = EXAMPLE_ROOT / "eval" / "eval_config.yaml"
os.environ.setdefault("EVAL_CFG", str(DEFAULT_CFG))
DEFAULT_RUNS = EXAMPLE_ROOT / "eval" / "runs" / "latest"
os.environ.setdefault("METRICS_DIR", str(DEFAULT_RUNS))

os.environ.setdefault('TRUSTBENCH_FAKE_PROVIDER', '1')
