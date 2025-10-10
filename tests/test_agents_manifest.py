import re
from pathlib import Path

from trust_bench_studio.utils import PROJECT_ROOT, load_agents_manifest


def test_agents_manifest_structure():
    agents = load_agents_manifest()
    assert agents, "agents_manifest.yaml must define at least one agent"

    required_keys = {"id", "name", "role", "seed_prompt", "image", "accent_color"}
    hex_pattern = re.compile(r"#([0-9a-fA-F]{6})$")

    for agent in agents:
        missing = required_keys - agent.keys()
        assert not missing, f"Agent {agent} missing keys: {missing}"

        assert str(agent["seed_prompt"]).strip(), f"Agent {agent['id']} seed_prompt must not be empty"

        image_path = Path(agent["image"])
        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / "trust_bench_studio" / image_path
        assert image_path.exists(), f"Image for agent {agent['id']} not found: {image_path}"

        color = str(agent["accent_color"])
        assert hex_pattern.match(color), f"Accent color for agent {agent['id']} must be #RRGGBB"
