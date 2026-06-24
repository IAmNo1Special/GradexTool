import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import main  # noqa: E402


@pytest.mark.asyncio
@patch("main.update_gradex_db", new_callable=AsyncMock)
@patch("main.get_items", new_callable=MagicMock)
@patch("main.get_fruitys", new_callable=MagicMock)
@patch("main.get_capsules", new_callable=MagicMock)
@patch("main.get_medicines", new_callable=AsyncMock)
@patch("main.get_type_charts", new_callable=AsyncMock)
@patch("main.get_moves", new_callable=AsyncMock)
@patch("main.get_movepools", new_callable=AsyncMock)
@patch("main.get_natures", new_callable=AsyncMock)
@patch("main.get_abilities", new_callable=AsyncMock)
@patch("main.get_base_types", new_callable=AsyncMock)
@patch("main.get_evolutions", new_callable=MagicMock)
@patch("main.get_revomon_data", new_callable=AsyncMock)
async def test_build_data_default_args(
    mock_get_revomon_data: Any,
    mock_get_evolutions: Any,
    mock_get_base_types: Any,
    mock_get_abilities: Any,
    mock_get_natures: Any,
    mock_get_movepools: Any,
    mock_get_moves: Any,
    mock_get_type_charts: Any,
    mock_get_medicines: Any,
    mock_get_capsules: Any,
    mock_get_fruitys: Any,
    mock_get_items: Any,
    mock_update_gradex_db: Any,
) -> None:
    await main.build_data()  # type: ignore[attr-defined]

    mock_get_revomon_data.assert_awaited_once_with(download_images=True)
    mock_get_evolutions.assert_called_once_with(save_to_file=True)
    mock_get_base_types.assert_awaited_once_with(
        save_to_file=True, download_images=True
    )
    mock_get_abilities.assert_awaited_once()
    mock_get_natures.assert_awaited_once_with(save_to_file=True)
    mock_get_movepools.assert_awaited_once_with(save_to_file=True)
    mock_get_moves.assert_awaited_once_with(save_to_file=True)
    mock_get_type_charts.assert_awaited_once_with(generate_images=True)
    mock_get_medicines.assert_awaited_once()
    mock_get_capsules.assert_called_once()
    mock_get_fruitys.assert_called_once()
    mock_get_items.assert_called_once()
    mock_update_gradex_db.assert_awaited_once()


@pytest.mark.asyncio
@patch("main.update_gradex_db", new_callable=AsyncMock)
@patch("main.get_items", new_callable=MagicMock)
@patch("main.get_fruitys", new_callable=MagicMock)
@patch("main.get_capsules", new_callable=MagicMock)
@patch("main.get_medicines", new_callable=AsyncMock)
@patch("main.get_type_charts", new_callable=AsyncMock)
@patch("main.get_moves", new_callable=AsyncMock)
@patch("main.get_movepools", new_callable=AsyncMock)
@patch("main.get_natures", new_callable=AsyncMock)
@patch("main.get_abilities", new_callable=AsyncMock)
@patch("main.get_base_types", new_callable=AsyncMock)
@patch("main.get_evolutions", new_callable=MagicMock)
@patch("main.get_revomon_data", new_callable=AsyncMock)
async def test_build_data_custom_args(
    mock_get_revomon_data: Any,
    mock_get_evolutions: Any,
    mock_get_base_types: Any,
    mock_get_abilities: Any,
    mock_get_natures: Any,
    mock_get_movepools: Any,
    mock_get_moves: Any,
    mock_get_type_charts: Any,
    mock_get_medicines: Any,
    mock_get_capsules: Any,
    mock_get_fruitys: Any,
    mock_get_items: Any,
    mock_update_gradex_db: Any,
) -> None:
    await main.build_data(  # type: ignore[attr-defined]
        save_to_file=False, download_images=False, process_caught_revomon=True
    )

    mock_get_revomon_data.assert_awaited_once_with(download_images=False)
    mock_get_evolutions.assert_called_once_with(save_to_file=False)
    mock_get_base_types.assert_awaited_once_with(
        save_to_file=False, download_images=False
    )
    mock_get_abilities.assert_awaited_once()
    mock_get_natures.assert_awaited_once_with(save_to_file=False)
    mock_get_movepools.assert_awaited_once_with(save_to_file=False)
    mock_get_moves.assert_awaited_once_with(save_to_file=False)
    mock_get_type_charts.assert_awaited_once_with(generate_images=True)
    mock_get_medicines.assert_awaited_once()
    mock_get_capsules.assert_called_once()
    mock_get_fruitys.assert_called_once()
    mock_get_items.assert_called_once()
    mock_update_gradex_db.assert_awaited_once()


def test_main_execution() -> None:
    with patch.object(
        main.asyncio,  # type: ignore[attr-defined]
        "run",
        side_effect=lambda coro: coro.close(),
    ) as mock_run:
        with patch.object(main.logging, "basicConfig") as mock_config:  # type: ignore[attr-defined]
            with open(main.__file__, encoding="utf-8") as f:
                code = f.read()

            namespace = main.__dict__.copy()
            namespace["__name__"] = "__main__"

            exec(code, namespace)

            mock_config.assert_called_once()
            mock_run.assert_called_once()
