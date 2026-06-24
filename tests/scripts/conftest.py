from typing import Any

"""Pytest configuration and common fixtures for testing scripts."""

import json  # noqa: E402
import sqlite3  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture
def temp_data_dir() -> None:  # type: ignore[misc]
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        yield data_dir


@pytest.fixture
def temp_db_path(temp_data_dir: Any) -> None:  # type: ignore[misc]
    """Create a temporary database path for testing."""
    db_path = temp_data_dir / "test_gradex.db"
    yield db_path


@pytest.fixture
def mock_db_connection(temp_db_path: Any) -> None:  # type: ignore[misc]
    """Create a mock database connection for testing."""
    conn = sqlite3.connect(temp_db_path)
    yield conn
    conn.close()


@pytest.fixture
def scripts_sample_revomon_data() -> Any:
    """Sample revomon data for testing."""
    return [
        {
            "dex_id": 1,
            "mon_id": 1,
            "name": "dekute",
            "description": "A timid but playful creature.",
            "type1": "toxic",
            "type2": "forest",
            "ability1": "overgrow",
            "ability2": None,
            "ability_hidden": "chlorophyll",
            "hp": 45,
            "atk": 49,
            "def": 49,
            "spa": 65,
            "spd": 65,
            "spe": 45,
            "evolution": "desuke",
            "level_evolution": 16,
            "rarity": "rare"
        },
        {
            "dex_id": 2,
            "mon_id": 2,
            "name": "desuke",
            "description": "A more powerful form of dekute.",
            "type1": "toxic",
            "type2": "forest",
            "ability1": "overgrow",
            "ability2": None,
            "ability_hidden": "chlorophyll",
            "hp": 60,
            "atk": 62,
            "def": 63,
            "spa": 80,
            "spd": 80,
            "spe": 60,
            "evolution": "deksciple",
            "level_evolution": 36,
            "rarity": "epic"
        }
    ]


@pytest.fixture
def sample_nature_data() -> Any:
    """Sample nature data for testing."""
    return {
        "1": {
            "name": "adamant",
            "increased_stat": "atk",
            "decreased_stat": "spa",
            "idNature": 1
        },
        "2": {
            "name": "modest",
            "increased_stat": "spa",
            "decreased_stat": "atk",
            "idNature": 2
        }
    }


@pytest.fixture
def sample_ability_data() -> Any:
    """Sample ability data for testing."""
    return {
        "1": {
            "id": 1,
            "name": "overgrow",
            "effect_entries": [
                {
                    "effect": "Powers up grass-type moves when HP is low.",
                    "short_effect": "Powers up grass-type moves in a pinch."
                }
            ],
            "flavor_text_entries": []
        },
        "2": {
            "id": 2,
            "name": "blaze",
            "effect_entries": [
                {
                    "effect": "Powers up fire-type moves when HP is low.",
                    "short_effect": "Powers up fire-type moves in a pinch."
                }
            ],
            "flavor_text_entries": []
        }
    }


@pytest.fixture
def sample_item_data() -> Any:
    """Sample item data for testing."""
    return {
        "1": {
            "name": "potion",
            "description": "Restores 20 HP.",
            "obtained_from": "shop",
            "cost": 100,
            "idItem": 1
        },
        "2": {
            "name": "super potion",
            "description": "Restores 50 HP.",
            "obtained_from": "shop",
            "cost": 300,
            "idItem": 2
        }
    }


@pytest.fixture
def sample_move_data() -> Any:
    """Sample move data for testing."""
    return {
        "1": {
            "id": 1,
            "name": "tackle",
            "type": "normal",
            "category": "physical",
            "power": 40,
            "accuracy": 100,
            "pp": 35
        },
        "2": {
            "id": 2,
            "name": "ember",
            "type": "fire",
            "category": "special",
            "power": 40,
            "accuracy": 100,
            "pp": 25
        }
    }


@pytest.fixture
def sample_type_data() -> Any:
    """Sample type data for testing."""
    return {
        "fire": {
            "types_str": "fire",
            "type1": "fire",
            "type2": None,
            "fire": 1.0,
            "water": 0.5,
            "grass": 2.0,
            "ice": 2.0,
            "neutral": 1.0
        },
        "water": {
            "types_str": "water",
            "type1": "water",
            "type2": None,
            "fire": 2.0,
            "water": 1.0,
            "grass": 0.5,
            "ice": 0.5,
            "neutral": 1.0
        }
    }


@pytest.fixture
def sample_fruity_data() -> Any:
    """Sample fruity data for testing."""
    return {
        "1": {
            "name": "barka",
            "description": "Reduces toxic damage.",
            "type": "held",
            "idFruity": 1
        },
        "2": {
            "name": "cassius",
            "description": "Recovers HP at low health.",
            "type": "held",
            "idFruity": 2
        }
    }


@pytest.fixture
def sample_capsule_data() -> Any:
    """Sample capsule data for testing."""
    return []


@pytest.fixture
def sample_evolution_data() -> Any:
    """Sample evolution data for testing."""
    return [
        {
            "base": "dekute",
            "evolves_to": "desuke",
            "method": "level",
            "condition": 16
        }
    ]


@pytest.fixture
def sample_medicine_data() -> Any:
    """Sample medicine data for testing."""
    return [
        {
            "name": "potion",
            "description": "Restores 20 HP.",
            "category": "healing",
            "cost": 100
        }
    ]


@pytest.fixture
def sample_base_types() -> Any:
    """Sample base types list for testing."""
    return ["fire", "water", "grass", "electric", "ice", "toxic", "forest"]


@pytest.fixture
def mock_api_response() -> Any:
    """Mock API response for testing."""
    return {
        "status_code": 200,
        "json": lambda: {
            "data": {
                "revomons": [
                    {
                        "idRevodex": 1,
                        "idRevomon": 1,
                        "name": "Testmon",
                        "type1": "fire",
                        "type2": None
                    }
                ]
            }
        }
    }


@pytest.fixture
def scripts_mock_requests_get() -> None:  # type: ignore[misc]
    """Mock requests.get for API calls."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def scripts_mock_requests_post() -> None:  # type: ignore[misc]
    """Mock requests.post for API calls."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_aiohttp_client() -> None:  # type: ignore[misc]
    """Mock aiohttp client for async HTTP requests."""
    with patch('aiohttp.ClientSession') as mock_session:
        session = AsyncMock()
        mock_session.return_value = session
        yield session


@pytest.fixture
def sample_json_file(temp_data_dir: Any, scripts_sample_revomon_data: Any) -> None:  # type: ignore[misc]
    """Create a sample JSON file for testing."""
    json_file = temp_data_dir / "revomon.json"
    with open(json_file, 'w') as f:
        json.dump(scripts_sample_revomon_data, f, indent=2)  # type: ignore[name-defined]
    yield json_file


# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an event loop for async tests."""
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     yield loop
#     loop.close()



@pytest.fixture
def mock_logger() -> Any:
    """Create a mock logger for testing."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_progress_bar() -> Any:
    """Create a mock progress bar for testing."""
    progress = MagicMock()
    progress.update = MagicMock()
    progress.close = MagicMock()
    return progress
