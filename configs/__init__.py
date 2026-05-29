from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent


def _get_configs():
    """Load configuration from configs/configs.yaml."""
    configs_path = Path(PROJECT_ROOT, "configs", "configs.yaml")
    with open(configs_path) as f:
        return yaml.safe_load(f)


_configs = _get_configs()
GRA_GUILD_ID = _configs.get("GRA_GUILD_ID")
PRO_TAMER_ROLE_IDS = _configs.get("PRO_TAMER_ROLE_IDS", [])

__all__ = ["PROJECT_ROOT", "GRA_GUILD_ID", "PRO_TAMER_ROLE_IDS"]
