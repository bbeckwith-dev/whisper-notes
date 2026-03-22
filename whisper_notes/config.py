import json
from pathlib import Path

DEFAULT_VAULTS = [
    "fantasy-writing",
    "game-development",
    "self-observations",
    "software-engineering",
]


def load_config(path: Path) -> dict:
    """Load config from JSON file, creating defaults if missing."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    config = {"vaults": list(DEFAULT_VAULTS)}
    save_config(config, path)
    return config


def save_config(config: dict, path: Path) -> None:
    """Write config to JSON file."""
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def add_vault(config: dict, vault: str) -> None:
    """Add a vault if it doesn't already exist."""
    if vault not in config["vaults"]:
        config["vaults"].append(vault)
