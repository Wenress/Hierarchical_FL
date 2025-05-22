import yaml
from pathlib import Path

# ---------- util -----------
def load_config(path: str | Path = "config.yaml") -> dict:
    """Loads the configuration file as a dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)