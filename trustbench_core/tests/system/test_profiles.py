import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROFILES = ["profiles/default.yaml", "profiles/highstakes.yaml"]
REQUIRED_KEYS = {"profile", "provider", "model", "thresholds", "sampling"}


def test_profiles_have_required_keys():
    for rel_path in PROFILES:
        cfg = yaml.safe_load((ROOT / rel_path).read_text(encoding="utf-8"))
        missing = REQUIRED_KEYS - set(cfg.keys())
        assert not missing, f"{rel_path} missing keys: {missing}"
        assert "faithfulness" in cfg["thresholds"]
        assert "n" in cfg["sampling"]
