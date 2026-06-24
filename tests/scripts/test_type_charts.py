import runpy
import unittest.mock
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

import scripts.type_charts
from scripts.type_charts import (
    REVOMON_TO_POKEMON_TYPE,
    calculate_section_height,
    draw_icon_section,
    fetch_base_type_multipliers,
    fetch_single_type,
    get_font,
    get_type_charts,
    save_type_chart_images,
)


@pytest.mark.asyncio
async def test_fetch_single_type() -> None:
    client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "damage_relations": {
            "double_damage_from": [{"name": "fighting"}],
            "half_damage_from": [{"name": "flying"}],
            "no_damage_from": [{"name": "ghost"}],
        }
    }
    client.get.return_value = mock_resp

    rtype = "neutral"
    ptype = "normal"

    scripts.type_charts.BASE_TYPE_MULTIPLIERS.clear()
    scripts.type_charts.BASE_TYPE_MULTIPLIERS[rtype] = {}

    await fetch_single_type(client, rtype, ptype)

    assert scripts.type_charts.BASE_TYPE_MULTIPLIERS[rtype]["battle"] == 2.0
    assert scripts.type_charts.BASE_TYPE_MULTIPLIERS[rtype]["sky"] == 0.5
    assert scripts.type_charts.BASE_TYPE_MULTIPLIERS[rtype]["phantom"] == 0.0


@pytest.mark.asyncio
@patch("scripts.type_charts.fetch_single_type")
async def test_fetch_base_type_multipliers(mock_fetch: Any) -> None:
    await fetch_base_type_multipliers()

    assert "neutral" in scripts.type_charts.BASE_TYPE_MULTIPLIERS
    assert scripts.type_charts.BASE_TYPE_MULTIPLIERS["neutral"]["neutral"] == 1.0
    assert mock_fetch.call_count == len(REVOMON_TO_POKEMON_TYPE)


def test_get_font() -> None:
    with patch("PIL.ImageFont.truetype") as mock_truetype:
        mock_truetype.return_value = "mock_font"
        font = get_font(30)
        assert font == "mock_font"

    with (
        patch("PIL.ImageFont.truetype", side_effect=OSError),
        patch("PIL.ImageFont.load_default") as mock_default,
    ):
        mock_default.return_value = "default_font"
        font = get_font(30)
        assert font == "default_font"


def test_calculate_section_height() -> None:
    assert calculate_section_height(100, [], {}) == 0

    targets = ["fire", "water", "grass"]
    type_images = {}
    for t in targets:
        img = MagicMock()
        img.width = 100
        img.height = 100
        type_images[t] = img

    height = calculate_section_height(100, targets, type_images)
    assert height > 0

    # Check wrapping
    targets = ["fire", "water", "grass"]
    height_wrap = calculate_section_height(50, targets, type_images)
    assert height_wrap > height


def test_draw_icon_section() -> None:
    img = MagicMock()
    draw = MagicMock()
    draw.textbbox.return_value = (0, 0, 50, 20)
    targets = ["fire", "water", "grass"]
    type_images = {
        "fire": MagicMock(width=100, height=100),
        "water": MagicMock(width=100, height=100),
        "grass": MagicMock(width=100, height=100),
    }
    y_end = draw_icon_section(
        img, draw, 0, 0, 100, "LABEL", targets, type_images, "font"
    )
    assert y_end > 0

    # Wrapping test
    y_wrap = draw_icon_section(
        img, draw, 0, 0, 50, "LABEL", targets, type_images, "font"
    )
    assert y_wrap > 0

    assert (
        draw_icon_section(img, draw, 0, 0, 100, "LABEL", [], type_images, "font") == 0
    )


@patch("scripts.type_charts.TYPE_CHART_IMAGES_DIR")
@patch("scripts.type_charts.Image.new")
@patch("scripts.type_charts.ImageDraw")
def test_save_type_chart_images(
    mock_draw: Any, mock_image_new: Any, mock_dir: Any
) -> None:
    types_dict = {
        "fire": {"type1": "fire", "type2": None},
        "fire_water": {"type1": "fire", "type2": "water"},
    }
    base_type_names = ["fire", "water", "grass"]

    fire_img = MagicMock()
    fire_img.width = 100
    fire_img.height = 100
    fire_img.rotate.return_value.size = (100, 100)
    fire_img.rotate.return_value.resize.return_value.size = (70, 70)

    water_img = MagicMock()
    water_img.width = 100
    water_img.height = 100
    water_img.rotate.return_value.size = (100, 100)
    water_img.rotate.return_value.resize.return_value.size = (70, 70)

    type_images = {"fire": fire_img, "water": water_img}

    save_type_chart_images(types_dict, base_type_names, type_images)  # type: ignore[arg-type]
    assert mock_dir.mkdir.called
    assert mock_image_new.called


@pytest.mark.asyncio
@patch("scripts.type_charts.fetch_base_type_multipliers")
@patch("scripts.type_charts.save_type_chart_images")
@patch("builtins.open", new_callable=mock_open)
@patch("scripts.type_charts.TYPE_CHARTS_FILE")
@patch("scripts.type_charts.MISSING_TYPE_CHARTS_FILE")
@patch("scripts.type_charts.TYPE_CHART_IMAGES_DIR")
@patch("scripts.type_charts.BASE_TYPES_IMAGES_DIR")
async def test_get_type_charts(
    mock_base_dir: Any,
    mock_chart_dir: Any,
    mock_missing_file: Any,
    mock_charts_file: Any,
    mock_file: Any,
    mock_save: Any,
    mock_fetch: Any,
) -> None:
    import json

    # Add dummy files
    mock_file.side_effect = [
        mock_open(read_data=json.dumps(["fire", "water", "grass"])).return_value,
        mock_open(
            read_data=json.dumps(
                [{"type1": "fire", "type2": "water"}, {"type1": "grass"}]
            )
        ).return_value,
        mock_open().return_value,
        mock_open().return_value,
    ]

    scripts.type_charts.BASE_TYPE_MULTIPLIERS.clear()
    scripts.type_charts.BASE_TYPE_MULTIPLIERS["fire"] = {"water": 0.5, "grass": 2.0}
    scripts.type_charts.BASE_TYPE_MULTIPLIERS["water"] = {"fire": 2.0, "grass": 0.5}
    scripts.type_charts.BASE_TYPE_MULTIPLIERS["grass"] = {"fire": 0.5, "water": 2.0}

    await get_type_charts(generate_images=False)

    # Image load error handling
    mock_file.side_effect = [
        mock_open(read_data=json.dumps(["fire", "water", "grass"])).return_value,
        mock_open(
            read_data=json.dumps(
                [{"type1": "fire", "type2": "water"}, {"type1": "grass"}]
            )
        ).return_value,
        mock_open().return_value,
        mock_open().return_value,
    ]

    mock_path = MagicMock()
    mock_path.stem = "fire"
    mock_base_dir.glob.return_value = [mock_path]

    mock_chart_path = MagicMock()
    mock_chart_path.exists.return_value = False
    mock_chart_dir.__truediv__.return_value = mock_chart_path

    with patch("scripts.type_charts.Image.open") as mock_image_open:
        # Cause OSError on Image.open
        mock_image_open.side_effect = OSError("Error")
        await get_type_charts(generate_images=True)

    # Test missing files scenario properly (mock exist returns False)
    mock_file.side_effect = [
        mock_open(read_data=json.dumps(["fire"])).return_value,
        mock_open(read_data=json.dumps([{"type1": "fire"}])).return_value,
        mock_open().return_value,
        mock_open().return_value,
    ]
    mock_chart_path.exists.return_value = False

    with patch("scripts.type_charts.Image.open"):
        await get_type_charts(generate_images=False)

    # Test WITHOUT missing files (mock exist returns True)
    mock_file.side_effect = [
        mock_open(read_data=json.dumps(["fire"])).return_value,
        mock_open(read_data=json.dumps([{"type1": "fire"}])).return_value,
        mock_open().return_value,
        mock_open().return_value,
    ]
    mock_chart_path.exists.return_value = True
    mock_missing_file.exists.return_value = True

    with patch("scripts.type_charts.Image.open"):
        await get_type_charts(generate_images=False)
        assert mock_missing_file.unlink.called


@patch("scripts.type_charts.get_type_charts", new_callable=AsyncMock)
@patch("scripts.type_charts.asyncio.run")
def test_main(mock_run: Any, mock_get_type_charts: Any) -> None:
    mock_run.side_effect = lambda coro: coro.close()
    # simulate __name__ == '__main__'
    with patch.dict("sys.modules", {"scripts.type_charts": scripts.type_charts}):
        with unittest.mock.patch.dict("sys.modules"):
            import sys

            sys.modules.pop("scripts.type_charts", None)

            runpy.run_module("scripts.type_charts", run_name="__main__")
        mock_run.assert_called_once()
