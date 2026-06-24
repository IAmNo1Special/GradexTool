from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).parent.parent


def _get_configs() -> Any:
    """Load configuration from configs/configs.yaml."""
    configs_path = Path(PROJECT_ROOT, "configs", "configs.yaml")
    with open(configs_path) as f:
        return yaml.safe_load(f)


_configs = _get_configs()
GRA_GUILD_ID = _configs.get("GRA_GUILD_ID")
BOT_OWNER_ID = _configs.get("BOT_OWNER_ID")
PRO_TAMER_ROLE_IDS = _configs.get("PRO_TAMER_ROLE_IDS", [])
GRADEX_DB_PATH = _configs.get("GRADEX_DB_PATH", "data/gradex.db")

# API endpoints
REVOMON_REVODEX_ENDPOINT = _configs.get(
    "REVOMON_REVODEX_ENDPOINT", "https://api.revomon.io/revomon/revodex"
)
REVOMON_RAW_IMAGE_ENDPOINT = _configs.get(
    "REVOMON_RAW_IMAGE_ENDPOINT", "https://nft.revomon.io/image/raw/revomon"
)
REVOMON_NFT_IMAGE_ENDPOINT = _configs.get(
    "REVOMON_NFT_IMAGE_ENDPOINT", "https://nft.revomon.io/image/revomon"
)
REVOMON_BASE_TYPES_IMAGE_ENDPOINT = _configs.get(
    "REVOMON_BASE_TYPES_IMAGE_ENDPOINT", "https://app-v2.revomon.io/static/images/types"
)
REVOMON_MOVES_ENDPOINT = _configs.get(
    "REVOMON_MOVES_ENDPOINT", "https://api.revomon.io/revomon/moves"
)
POKEAPI_NATURES_ENDPOINT = _configs.get(
    "POKEAPI_NATURES_ENDPOINT", "https://pokeapi.co/api/v2/nature?limit=25"
)
POKEAPI_NATURE_ENDPOINT = _configs.get(
    "POKEAPI_NATURE_ENDPOINT", "https://pokeapi.co/api/v2/nature"
)
POKEAPI_MEDICINE_CATEGORY_ENDPOINT = _configs.get(
    "POKEAPI_MEDICINE_CATEGORY_ENDPOINT", "https://pokeapi.co/api/v2/item-category/26"
)
POKEAPI_ITEM_ENDPOINT = _configs.get(
    "POKEAPI_ITEM_ENDPOINT", "https://pokeapi.co/api/v2/item"
)

# File paths
REVOMON_FILE = _configs.get("REVOMON_FILE", "data/revomon.json")
ABILITIES_FILE = _configs.get("ABILITIES_FILE", "data/abilities.json")
UNKNOWN_ABILITIES_FILE = _configs.get(
    "UNKNOWN_ABILITIES_FILE", "data/unknown_abilities.json"
)
EVOLUTIONS_FILE = _configs.get("EVOLUTIONS_FILE", "data/evolutions.json")
BASE_TYPES_FILE = _configs.get("BASE_TYPES_FILE", "data/base_types.json")
MOVEPOOLS_FILE = _configs.get("MOVEPOOLS_FILE", "data/movepools.json")
MOVES_FILE = _configs.get("MOVES_FILE", "data/moves.json")
TYPE_CHARTS_FILE = _configs.get("TYPE_CHARTS_FILE", "data/type_charts.json")
MISSING_TYPE_CHARTS_FILE = _configs.get(
    "MISSING_TYPE_CHARTS_FILE", "data/missing_type_charts.json"
)
NATURES_FILE = _configs.get("NATURES_FILE", "data/natures.json")
MEDICINES_FILE = _configs.get("MEDICINES_FILE", "data/medicines.json")
ITEMS_FILE = _configs.get("ITEMS_FILE", "data/items.json")
FRUITYS_FILE = _configs.get("FRUITYS_FILE", "data/fruitys.json")
CAUGHT_REVOMON_FILE = _configs.get("CAUGHT_REVOMON_FILE", "data/caught_revomon.json")
CAUGHT_REVOMON_SCAN_STATE_FILE = _configs.get(
    "CAUGHT_REVOMON_SCAN_STATE_FILE", "data/caught_revomon_scan_state.json"
)
CAPSULES_FILE = _configs.get("CAPSULES_FILE", "data/capsules.json")

# Directory paths
TYPE_CHART_IMAGES_DIR = _configs.get("TYPE_CHART_IMAGES_DIR", "data/assets/type_charts")
BASE_TYPES_IMAGES_DIR = _configs.get("BASE_TYPES_IMAGES_DIR", "data/assets/base_types")
REVOMON_RAW_IMAGES_DIR = _configs.get(
    "REVOMON_RAW_IMAGES_DIR", "data/assets/revomon/raw"
)
REVOMON_NFT_IMAGES_DIR = _configs.get(
    "REVOMON_NFT_IMAGES_DIR", "data/assets/revomon/nft"
)
REVOMON_IMAGES_DOWNLOAD_MANIFEST = _configs.get(
    "REVOMON_IMAGES_DOWNLOAD_MANIFEST", "data/assets/revomon/download_results.json"
)
REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE = (
    REVOMON_IMAGES_DOWNLOAD_MANIFEST  # Alias for compatibility
)

# Other configuration
USER_AGENT = _configs.get(
    "USER_AGENT", "Mozilla/5.0 (compatible; Global Revomon Association)"
)

__all__ = [
    "PROJECT_ROOT",
    "GRA_GUILD_ID",
    "BOT_OWNER_ID",
    "PRO_TAMER_ROLE_IDS",
    "GRADEX_DB_PATH",
    "REVOMON_REVODEX_ENDPOINT",
    "REVOMON_RAW_IMAGE_ENDPOINT",
    "REVOMON_NFT_IMAGE_ENDPOINT",
    "REVOMON_BASE_TYPES_IMAGE_ENDPOINT",
    "REVOMON_MOVES_ENDPOINT",
    "POKEAPI_NATURES_ENDPOINT",
    "POKEAPI_NATURE_ENDPOINT",
    "POKEAPI_MEDICINE_CATEGORY_ENDPOINT",
    "POKEAPI_ITEM_ENDPOINT",
    "REVOMON_FILE",
    "ABILITIES_FILE",
    "UNKNOWN_ABILITIES_FILE",
    "EVOLUTIONS_FILE",
    "BASE_TYPES_FILE",
    "MOVEPOOLS_FILE",
    "MOVES_FILE",
    "TYPE_CHARTS_FILE",
    "MISSING_TYPE_CHARTS_FILE",
    "NATURES_FILE",
    "MEDICINES_FILE",
    "ITEMS_FILE",
    "FRUITYS_FILE",
    "CAUGHT_REVOMON_FILE",
    "CAUGHT_REVOMON_SCAN_STATE_FILE",
    "CAPSULES_FILE",
    "TYPE_CHART_IMAGES_DIR",
    "BASE_TYPES_IMAGES_DIR",
    "REVOMON_RAW_IMAGES_DIR",
    "REVOMON_NFT_IMAGES_DIR",
    "REVOMON_IMAGES_DOWNLOAD_MANIFEST",
    "REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE",
    "USER_AGENT",
]
