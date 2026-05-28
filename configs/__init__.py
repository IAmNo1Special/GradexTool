from pathlib import Path

import yaml


def get_config():
    """Load configuration from configs/config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


CONFIG = get_config()
GRA_GUILD_ID = CONFIG.get("gra_guild_id")
PRO_TAMER_ROLE_IDS = CONFIG.get("pro_tamer_role_ids", [])
