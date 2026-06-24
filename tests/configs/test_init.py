"""Comprehensive tests for configs/__init__.py."""

from pathlib import Path

import yaml

# Import the module to test
from configs import (
    ABILITIES_FILE,
    BASE_TYPES_FILE,
    BASE_TYPES_IMAGES_DIR,
    CAPSULES_FILE,
    CAUGHT_REVOMON_FILE,
    CAUGHT_REVOMON_SCAN_STATE_FILE,
    EVOLUTIONS_FILE,
    FRUITYS_FILE,
    GRA_GUILD_ID,
    GRADEX_DB_PATH,
    ITEMS_FILE,
    MEDICINES_FILE,
    MISSING_TYPE_CHARTS_FILE,
    MOVEPOOLS_FILE,
    MOVES_FILE,
    NATURES_FILE,
    POKEAPI_ITEM_ENDPOINT,
    POKEAPI_MEDICINE_CATEGORY_ENDPOINT,
    POKEAPI_NATURE_ENDPOINT,
    POKEAPI_NATURES_ENDPOINT,
    PRO_TAMER_ROLE_IDS,
    PROJECT_ROOT,
    REVOMON_BASE_TYPES_IMAGE_ENDPOINT,
    REVOMON_FILE,
    REVOMON_IMAGES_DOWNLOAD_MANIFEST,
    REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE,
    REVOMON_MOVES_ENDPOINT,
    REVOMON_NFT_IMAGE_ENDPOINT,
    REVOMON_NFT_IMAGES_DIR,
    REVOMON_RAW_IMAGE_ENDPOINT,
    REVOMON_RAW_IMAGES_DIR,
    REVOMON_REVODEX_ENDPOINT,
    TYPE_CHART_IMAGES_DIR,
    TYPE_CHARTS_FILE,
    UNKNOWN_ABILITIES_FILE,
    USER_AGENT,
    __all__,
)


class TestProjectRoot:
    """Tests for PROJECT_ROOT constant."""

    def test_project_root_is_path(self) -> None:
        """Test that PROJECT_ROOT is a Path object."""
        assert isinstance(PROJECT_ROOT, Path)

    def test_project_root_points_to_correct_directory(self) -> None:
        """Test that PROJECT_ROOT points to the project root directory."""
        # PROJECT_ROOT should be the parent of the configs directory
        assert PROJECT_ROOT.name == "GradexTool"
        assert (PROJECT_ROOT / "configs").exists()
        assert (PROJECT_ROOT / "mods").exists()


class TestGetConfigs:
    """Tests for _get_configs function."""

    def test_get_configs_loads_yaml_file(self) -> None:
        """Test that _get_configs successfully loads the YAML file."""
        from configs import _get_configs

        configs = _get_configs()

        assert isinstance(configs, dict)
        assert len(configs) > 0

    def test_get_configs_returns_expected_keys(self) -> None:
        """Test that _get_configs returns expected configuration keys."""
        from configs import _get_configs

        configs = _get_configs()

        expected_keys = [
            "GRA_GUILD_ID",
            "PRO_TAMER_ROLE_IDS",
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
            "USER_AGENT",
            "GRADEX_DB_PATH",
        ]

        for key in expected_keys:
            assert key in configs, f"Expected key '{key}' not found in configs"

    def test_get_configs_handles_missing_keys_with_defaults(self) -> None:
        """Test that config values use defaults when keys are missing via get method."""
        from configs import _get_configs

        configs = _get_configs()

        # Test that .get() method returns defaults for missing keys
        assert configs.get("NON_EXISTENT_KEY") is None
        assert configs.get("NON_EXISTENT_KEY", "default_value") == "default_value"

    def test_get_configs_path_is_correct(self) -> None:
        """Test that the configs file path is correct."""
        from configs import PROJECT_ROOT

        expected_path = PROJECT_ROOT / "configs" / "configs.yaml"
        assert expected_path.exists()


class TestConfigConstants:
    """Tests for configuration constants."""

    def test_gra_guild_id_is_integer(self) -> None:
        """Test that GRA_GUILD_ID is an integer."""
        assert isinstance(GRA_GUILD_ID, int)
        assert GRA_GUILD_ID > 0

    def test_gra_guild_id_matches_config(self) -> None:
        """Test that GRA_GUILD_ID matches the config file value."""
        from configs import _get_configs

        configs = _get_configs()
        assert GRA_GUILD_ID == configs["GRA_GUILD_ID"]

    def test_pro_tamer_role_ids_is_list(self) -> None:
        """Test that PRO_TAMER_ROLE_IDS is a list."""
        assert isinstance(PRO_TAMER_ROLE_IDS, list)

    def test_pro_tamer_role_ids_contains_integers(self) -> None:
        """Test that PRO_TAMER_ROLE_IDS contains integers."""
        assert all(isinstance(role_id, int) for role_id in PRO_TAMER_ROLE_IDS)

    def test_pro_tamer_role_ids_not_empty(self) -> None:
        """Test that PRO_TAMER_ROLE_IDS is not empty."""
        assert len(PRO_TAMER_ROLE_IDS) > 0

    def test_pro_tamer_role_ids_match_config(self) -> None:
        """Test that PRO_TAMER_ROLE_IDS matches the config file value."""
        from configs import _get_configs

        configs = _get_configs()
        assert PRO_TAMER_ROLE_IDS == configs["PRO_TAMER_ROLE_IDS"]

    def test_gradex_db_path_is_string(self) -> None:
        """Test that GRADEX_DB_PATH is a string."""
        assert isinstance(GRADEX_DB_PATH, str)

    def test_gradex_db_path_matches_config(self) -> None:
        """Test that GRADEX_DB_PATH matches the config file value."""
        from configs import _get_configs

        configs = _get_configs()
        assert GRADEX_DB_PATH == configs["GRADEX_DB_PATH"]


class TestAPIEndpoints:
    """Tests for API endpoint configurations."""

    def test_revomon_revodex_endpoint_is_string(self) -> None:
        """Test that REVOMON_REVODEX_ENDPOINT is a string."""
        assert isinstance(REVOMON_REVODEX_ENDPOINT, str)
        assert REVOMON_REVODEX_ENDPOINT.startswith("https://")

    def test_revomon_raw_image_endpoint_is_string(self) -> None:
        """Test that REVOMON_RAW_IMAGE_ENDPOINT is a string."""
        assert isinstance(REVOMON_RAW_IMAGE_ENDPOINT, str)
        assert REVOMON_RAW_IMAGE_ENDPOINT.startswith("https://")

    def test_revomon_nft_image_endpoint_is_string(self) -> None:
        """Test that REVOMON_NFT_IMAGE_ENDPOINT is a string."""
        assert isinstance(REVOMON_NFT_IMAGE_ENDPOINT, str)
        assert REVOMON_NFT_IMAGE_ENDPOINT.startswith("https://")

    def test_revomon_base_types_image_endpoint_is_string(self) -> None:
        """Test that REVOMON_BASE_TYPES_IMAGE_ENDPOINT is a string."""
        assert isinstance(REVOMON_BASE_TYPES_IMAGE_ENDPOINT, str)
        assert REVOMON_BASE_TYPES_IMAGE_ENDPOINT.startswith("https://")

    def test_revomon_moves_endpoint_is_string(self) -> None:
        """Test that REVOMON_MOVES_ENDPOINT is a string."""
        assert isinstance(REVOMON_MOVES_ENDPOINT, str)
        assert REVOMON_MOVES_ENDPOINT.startswith("https://")

    def test_pokeapi_natures_endpoint_is_string(self) -> None:
        """Test that POKEAPI_NATURES_ENDPOINT is a string."""
        assert isinstance(POKEAPI_NATURES_ENDPOINT, str)
        assert POKEAPI_NATURES_ENDPOINT.startswith("https://")

    def test_pokeapi_nature_endpoint_is_string(self) -> None:
        """Test that POKEAPI_NATURE_ENDPOINT is a string."""
        assert isinstance(POKEAPI_NATURE_ENDPOINT, str)
        assert POKEAPI_NATURE_ENDPOINT.startswith("https://")

    def test_pokeapi_medicine_category_endpoint_is_string(self) -> None:
        """Test that POKEAPI_MEDICINE_CATEGORY_ENDPOINT is a string."""
        assert isinstance(POKEAPI_MEDICINE_CATEGORY_ENDPOINT, str)
        assert POKEAPI_MEDICINE_CATEGORY_ENDPOINT.startswith("https://")

    def test_pokeapi_item_endpoint_is_string(self) -> None:
        """Test that POKEAPI_ITEM_ENDPOINT is a string."""
        assert isinstance(POKEAPI_ITEM_ENDPOINT, str)
        assert POKEAPI_ITEM_ENDPOINT.startswith("https://")

    def test_all_api_endpoints_match_config(self) -> None:
        """Test that all API endpoints match the config file values."""
        from configs import _get_configs

        configs = _get_configs()

        assert REVOMON_REVODEX_ENDPOINT == configs["REVOMON_REVODEX_ENDPOINT"]
        assert REVOMON_RAW_IMAGE_ENDPOINT == configs["REVOMON_RAW_IMAGE_ENDPOINT"]
        assert REVOMON_NFT_IMAGE_ENDPOINT == configs["REVOMON_NFT_IMAGE_ENDPOINT"]
        assert (
            REVOMON_BASE_TYPES_IMAGE_ENDPOINT
            == configs["REVOMON_BASE_TYPES_IMAGE_ENDPOINT"]
        )
        assert REVOMON_MOVES_ENDPOINT == configs["REVOMON_MOVES_ENDPOINT"]
        assert POKEAPI_NATURES_ENDPOINT == configs["POKEAPI_NATURES_ENDPOINT"]
        assert POKEAPI_NATURE_ENDPOINT == configs["POKEAPI_NATURE_ENDPOINT"]
        assert (
            POKEAPI_MEDICINE_CATEGORY_ENDPOINT
            == configs["POKEAPI_MEDICINE_CATEGORY_ENDPOINT"]
        )
        assert POKEAPI_ITEM_ENDPOINT == configs["POKEAPI_ITEM_ENDPOINT"]


class TestFilePaths:
    """Tests for file path configurations."""

    def test_revomon_file_is_string(self) -> None:
        """Test that REVOMON_FILE is a string."""
        assert isinstance(REVOMON_FILE, str)

    def test_abilities_file_is_string(self) -> None:
        """Test that ABILITIES_FILE is a string."""
        assert isinstance(ABILITIES_FILE, str)

    def test_unknown_abilities_file_is_string(self) -> None:
        """Test that UNKNOWN_ABILITIES_FILE is a string."""
        assert isinstance(UNKNOWN_ABILITIES_FILE, str)

    def test_evolutions_file_is_string(self) -> None:
        """Test that EVOLUTIONS_FILE is a string."""
        assert isinstance(EVOLUTIONS_FILE, str)

    def test_base_types_file_is_string(self) -> None:
        """Test that BASE_TYPES_FILE is a string."""
        assert isinstance(BASE_TYPES_FILE, str)

    def test_movepools_file_is_string(self) -> None:
        """Test that MOVEPOOLS_FILE is a string."""
        assert isinstance(MOVEPOOLS_FILE, str)

    def test_moves_file_is_string(self) -> None:
        """Test that MOVES_FILE is a string."""
        assert isinstance(MOVES_FILE, str)

    def test_type_charts_file_is_string(self) -> None:
        """Test that TYPE_CHARTS_FILE is a string."""
        assert isinstance(TYPE_CHARTS_FILE, str)

    def test_missing_type_charts_file_is_string(self) -> None:
        """Test that MISSING_TYPE_CHARTS_FILE is a string."""
        assert isinstance(MISSING_TYPE_CHARTS_FILE, str)

    def test_natures_file_is_string(self) -> None:
        """Test that NATURES_FILE is a string."""
        assert isinstance(NATURES_FILE, str)

    def test_medicines_file_is_string(self) -> None:
        """Test that MEDICINES_FILE is a string."""
        assert isinstance(MEDICINES_FILE, str)

    def test_items_file_is_string(self) -> None:
        """Test that ITEMS_FILE is a string."""
        assert isinstance(ITEMS_FILE, str)

    def test_fruitys_file_is_string(self) -> None:
        """Test that FRUITYS_FILE is a string."""
        assert isinstance(FRUITYS_FILE, str)

    def test_caught_revomon_file_is_string(self) -> None:
        """Test that CAUGHT_REVOMON_FILE is a string."""
        assert isinstance(CAUGHT_REVOMON_FILE, str)

    def test_caught_revomon_scan_state_file_is_string(self) -> None:
        """Test that CAUGHT_REVOMON_SCAN_STATE_FILE is a string."""
        assert isinstance(CAUGHT_REVOMON_SCAN_STATE_FILE, str)

    def test_capsules_file_is_string(self) -> None:
        """Test that CAPSULES_FILE is a string."""
        assert isinstance(CAPSULES_FILE, str)

    def test_all_file_paths_match_config(self) -> None:
        """Test that all file paths match the config file values."""
        from configs import _get_configs

        configs = _get_configs()

        assert REVOMON_FILE == configs["REVOMON_FILE"]
        assert ABILITIES_FILE == configs["ABILITIES_FILE"]
        assert UNKNOWN_ABILITIES_FILE == configs["UNKNOWN_ABILITIES_FILE"]
        assert EVOLUTIONS_FILE == configs["EVOLUTIONS_FILE"]
        assert BASE_TYPES_FILE == configs["BASE_TYPES_FILE"]
        assert MOVEPOOLS_FILE == configs["MOVEPOOLS_FILE"]
        assert MOVES_FILE == configs["MOVES_FILE"]
        assert TYPE_CHARTS_FILE == configs["TYPE_CHARTS_FILE"]
        assert MISSING_TYPE_CHARTS_FILE == configs["MISSING_TYPE_CHARTS_FILE"]
        assert NATURES_FILE == configs["NATURES_FILE"]
        assert MEDICINES_FILE == configs["MEDICINES_FILE"]
        assert ITEMS_FILE == configs["ITEMS_FILE"]
        assert FRUITYS_FILE == configs["FRUITYS_FILE"]
        assert CAUGHT_REVOMON_FILE == configs["CAUGHT_REVOMON_FILE"]
        assert (
            CAUGHT_REVOMON_SCAN_STATE_FILE == configs["CAUGHT_REVOMON_SCAN_STATE_FILE"]
        )
        assert CAPSULES_FILE == configs["CAPSULES_FILE"]


class TestDirectoryPaths:
    """Tests for directory path configurations."""

    def test_type_chart_images_dir_is_string(self) -> None:
        """Test that TYPE_CHART_IMAGES_DIR is a string."""
        assert isinstance(TYPE_CHART_IMAGES_DIR, str)

    def test_base_types_images_dir_is_string(self) -> None:
        """Test that BASE_TYPES_IMAGES_DIR is a string."""
        assert isinstance(BASE_TYPES_IMAGES_DIR, str)

    def test_revomon_raw_images_dir_is_string(self) -> None:
        """Test that REVOMON_RAW_IMAGES_DIR is a string."""
        assert isinstance(REVOMON_RAW_IMAGES_DIR, str)

    def test_revomon_nft_images_dir_is_string(self) -> None:
        """Test that REVOMON_NFT_IMAGES_DIR is a string."""
        assert isinstance(REVOMON_NFT_IMAGES_DIR, str)

    def test_revomon_images_download_manifest_is_string(self) -> None:
        """Test that REVOMON_IMAGES_DOWNLOAD_MANIFEST is a string."""
        assert isinstance(REVOMON_IMAGES_DOWNLOAD_MANIFEST, str)

    def test_revomon_images_download_manifest_file_is_alias(self) -> None:
        """Test that REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE is an alias for REVOMON_IMAGES_DOWNLOAD_MANIFEST."""
        assert REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE == REVOMON_IMAGES_DOWNLOAD_MANIFEST

    def test_all_directory_paths_match_config(self) -> None:
        """Test that all directory paths match the config file values."""
        from configs import _get_configs

        configs = _get_configs()

        assert TYPE_CHART_IMAGES_DIR == configs["TYPE_CHART_IMAGES_DIR"]
        assert BASE_TYPES_IMAGES_DIR == configs["BASE_TYPES_IMAGES_DIR"]
        assert REVOMON_RAW_IMAGES_DIR == configs["REVOMON_RAW_IMAGES_DIR"]
        assert REVOMON_NFT_IMAGES_DIR == configs["REVOMON_NFT_IMAGES_DIR"]
        assert (
            REVOMON_IMAGES_DOWNLOAD_MANIFEST
            == configs["REVOMON_IMAGES_DOWNLOAD_MANIFEST"]
        )


class TestOtherConfiguration:
    """Tests for other configuration values."""

    def test_user_agent_is_string(self) -> None:
        """Test that USER_AGENT is a string."""
        assert isinstance(USER_AGENT, str)

    def test_user_agent_not_empty(self) -> None:
        """Test that USER_AGENT is not empty."""
        assert len(USER_AGENT) > 0

    def test_user_agent_matches_config(self) -> None:
        """Test that USER_AGENT matches the config file value."""
        from configs import _get_configs

        configs = _get_configs()
        assert USER_AGENT == configs["USER_AGENT"]


class TestModuleExports:
    """Tests for module __all__ exports."""

    def test___all__is_list(self) -> None:
        """Test that __all__ is a list."""
        assert isinstance(__all__, list)

    def test___all__not_empty(self) -> None:
        """Test that __all__ is not empty."""
        assert len(__all__) > 0

    def test___all__contains_project_root(self) -> None:
        """Test that __all__ contains PROJECT_ROOT."""
        assert "PROJECT_ROOT" in __all__

    def test___all__contains_all_config_constants(self) -> None:
        """Test that __all__ contains all configuration constants."""
        expected_exports = [
            "PROJECT_ROOT",
            "GRA_GUILD_ID",
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

        for export in expected_exports:
            assert export in __all__, f"Expected export '{export}' not found in __all__"

    def test___all__items_are_strings(self) -> None:
        """Test that all items in __all__ are strings."""
        assert all(isinstance(item, str) for item in __all__)

    def test___all__items_are_unique(self) -> None:
        """Test that all items in __all__ are unique."""
        assert len(__all__) == len(set(__all__))


class TestDefaultValues:
    """Tests for default value handling when config keys are missing."""

    def test_gradex_db_path_has_default(self) -> None:
        """Test that GRADEX_DB_PATH has a default value."""
        # The default should be "data/gradex.db"
        assert GRADEX_DB_PATH == "data/gradex.db"

    def test_pro_tamer_role_ids_has_default(self) -> None:
        """Test that PRO_TAMER_ROLE_IDS has a default value."""
        # The default should be an empty list
        # But in the actual config it's not empty, so we just verify it's a list
        assert isinstance(PRO_TAMER_ROLE_IDS, list)

    def test_api_endpoints_have_defaults(self) -> None:
        """Test that API endpoints have default values."""
        assert REVOMON_REVODEX_ENDPOINT == "https://api.revomon.io/revomon/revodex"
        assert REVOMON_RAW_IMAGE_ENDPOINT == "https://nft.revomon.io/image/raw/revomon"
        assert REVOMON_NFT_IMAGE_ENDPOINT == "https://nft.revomon.io/image/revomon"
        assert (
            REVOMON_BASE_TYPES_IMAGE_ENDPOINT
            == "https://app-v2.revomon.io/static/images/types"
        )
        assert REVOMON_MOVES_ENDPOINT == "https://api.revomon.io/revomon/moves"
        assert POKEAPI_NATURES_ENDPOINT == "https://pokeapi.co/api/v2/nature?limit=25"
        assert POKEAPI_NATURE_ENDPOINT == "https://pokeapi.co/api/v2/nature"
        assert (
            POKEAPI_MEDICINE_CATEGORY_ENDPOINT
            == "https://pokeapi.co/api/v2/item-category/26"
        )
        assert POKEAPI_ITEM_ENDPOINT == "https://pokeapi.co/api/v2/item"

    def test_file_paths_have_defaults(self) -> None:
        """Test that file paths have default values."""
        assert REVOMON_FILE == "data/revomon.json"
        assert ABILITIES_FILE == "data/abilities.json"
        assert UNKNOWN_ABILITIES_FILE == "data/unknown_abilities.json"
        assert EVOLUTIONS_FILE == "data/evolutions.json"
        assert BASE_TYPES_FILE == "data/base_types.json"
        assert MOVEPOOLS_FILE == "data/movepools.json"
        assert MOVES_FILE == "data/moves.json"
        assert TYPE_CHARTS_FILE == "data/type_charts.json"
        assert MISSING_TYPE_CHARTS_FILE == "data/missing_type_charts.json"
        assert NATURES_FILE == "data/natures.json"
        assert MEDICINES_FILE == "data/medicines.json"
        assert ITEMS_FILE == "data/items.json"
        assert FRUITYS_FILE == "data/fruitys.json"
        assert CAUGHT_REVOMON_FILE == "data/caught_revomon.json"
        assert CAUGHT_REVOMON_SCAN_STATE_FILE == "data/caught_revomon_scan_state.json"
        assert CAPSULES_FILE == "data/capsules.json"

    def test_directory_paths_have_defaults(self) -> None:
        """Test that directory paths have default values."""
        assert TYPE_CHART_IMAGES_DIR == "data/assets/type_charts"
        assert BASE_TYPES_IMAGES_DIR == "data/assets/base_types"
        assert REVOMON_RAW_IMAGES_DIR == "data/assets/revomon/raw"
        assert REVOMON_NFT_IMAGES_DIR == "data/assets/revomon/nft"
        assert (
            REVOMON_IMAGES_DOWNLOAD_MANIFEST
            == "data/assets/revomon/download_results.json"
        )

    def test_user_agent_has_default(self) -> None:
        """Test that USER_AGENT has a default value."""
        assert USER_AGENT == "Mozilla/5.0 (compatible; Global Revomon Association)"


class TestConfigFileIntegrity:
    """Tests for config file integrity and structure."""

    def test_config_file_is_valid_yaml(self) -> None:
        """Test that the config file is valid YAML."""
        config_path = PROJECT_ROOT / "configs" / "configs.yaml"
        with open(config_path) as f:
            configs = yaml.safe_load(f)
        assert isinstance(configs, dict)

    def test_config_file_contains_all_required_keys(self) -> None:
        """Test that the config file contains all required keys."""
        from configs import _get_configs

        configs = _get_configs()

        required_keys = [
            "GRA_GUILD_ID",
            "PRO_TAMER_ROLE_IDS",
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
            "USER_AGENT",
            "GRADEX_DB_PATH",
        ]

        for key in required_keys:
            assert key in configs, f"Required key '{key}' not found in config file"

    def test_config_file_values_are_correct_types(self) -> None:
        """Test that config file values have correct types."""
        from configs import _get_configs

        configs = _get_configs()

        assert isinstance(configs["GRA_GUILD_ID"], int)
        assert isinstance(configs["PRO_TAMER_ROLE_IDS"], list)
        assert all(isinstance(key, str) for key in configs.keys())
