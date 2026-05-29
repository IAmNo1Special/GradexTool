from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent


def _get_configs():
    """Load configuration from configs/configs.yaml."""
    configs_path = Path(PROJECT_ROOT, "configs", "configs.yaml")
    with open(configs_path) as f:
        return yaml.safe_load(f)


CONFIG = get_config()
GRA_GUILD_ID = CONFIG.get("gra_guild_id")
PRO_TAMER_ROLE_IDS = CONFIG.get("pro_tamer_role_ids", [])
