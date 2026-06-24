import asyncio
import runpy
import unittest.mock
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

from scripts.medicines import (
    fetch_url,
    get_medicine_categories,
    get_medicines,
    process_item,
    process_string,
)


@pytest.mark.asyncio
async def test_fetch_url() -> None:
    client = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"a": 1}
    client.get = AsyncMock(return_value=response)

    assert await fetch_url(client, "url") == {"a": 1}

    response.status_code = 404
    assert await fetch_url(client, "url") is None

    client.get.side_effect = httpx.HTTPError("error")
    assert await fetch_url(client, "url") is None

    client.get.side_effect = Exception("error")
    assert await fetch_url(client, "url") is None

def test_process_string() -> None:
    assert process_string(None) is None  # type: ignore[arg-type]
    assert process_string("") == ""
    assert process_string("a\nb\rc") == "a b c"
    assert process_string("\u2018a\u2019 \u201ca\u201d") == "'a' \"a\""
    assert process_string("Pokémon and Pokemon") == "Revomon and Revomon"
    assert process_string("a    b") == "a b"

@pytest.mark.asyncio
async def test_get_medicine_categories() -> None:
    client = MagicMock()
    with patch("scripts.medicines.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = [
            {"name": "cat1", "items": [{"name": "item1", "url": "url1"}]},
            None, None, None, None, None, None
        ]
        items = await get_medicine_categories(client)
        assert len(items) == 1
        assert items[0] == {"name": "item1", "url": "url1", "category": "cat1"}

@pytest.mark.asyncio
async def test_process_item() -> None:
    client = MagicMock()
    semaphore = asyncio.Semaphore(1)
    potions_list: list[dict[str, Any]] = []

    with patch("scripts.medicines.fetch_url", new_callable=AsyncMock) as mock_fetch:
        # Success case with en entries
        mock_fetch.return_value = {
            "cost": 100,
            "effect_entries": [
                {"language": {"name": "fr"}},
                {"language": {"name": "en"}, "effect": "effect1\n", "short_effect": "short1"}
            ],
            "flavor_text_entries": [
                {"language": {"name": "fr"}},
                {"language": {"name": "en"}, "text": "flavor1  "}
            ]
        }
        await process_item(semaphore, client, {"name": "Item1", "category": "Cat1", "url": "url1"}, potions_list)
        assert len(potions_list) == 1
        assert potions_list[0] == {
            "name": "item1",
            "category": "cat1",
            "cost": 100,
            "effect": "Effect1",
            "short_effect": "Short1",
            "flavor_text": "Flavor1",
        }

        # Failed fetch
        mock_fetch.return_value = None
        await process_item(semaphore, client, {"name": "Item2", "category": "Cat1", "url": "url2"}, potions_list)
        assert len(potions_list) == 1  # unchanged

        # Success case without en entries
        mock_fetch.return_value = {
            "cost": None,
            "effect_entries": [],
            "flavor_text_entries": []
        }
        await process_item(semaphore, client, {"name": "Item3", "category": "Cat1", "url": "url3"}, potions_list)
        assert len(potions_list) == 2
        assert potions_list[1] == {
            "name": "item3",
            "category": "cat1",
            "cost": None,
            "effect": "",
            "short_effect": "",
            "flavor_text": "",
        }

@pytest.mark.asyncio
@patch("scripts.medicines.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("scripts.medicines.json.dump")
async def test_get_medicines(mock_json_dump: Any, mock_open_file: Any, mock_makedirs: Any) -> None:
    with patch("scripts.medicines.get_medicine_categories", new_callable=AsyncMock) as mock_get_cat:
        with patch("scripts.medicines.process_item", new_callable=AsyncMock) as mock_process:
            mock_get_cat.return_value = [{"name": "item1", "category": "cat1", "url": "url1"}]

            async def side_effect(sem: Any, client: Any, ref: Any, plist: Any) -> None:
                plist.append({"name": "z", "category": "cat1", "cost": 100, "effect": "", "short_effect": "", "flavor_text": ""})
                plist.append({"name": "a", "category": "cat1", "cost": 100, "effect": "", "short_effect": "", "flavor_text": ""})

            mock_process.side_effect = side_effect

            await get_medicines()

            mock_makedirs.assert_called_once()
            mock_open_file.assert_called_once()
            mock_json_dump.assert_called_once()

            data = mock_json_dump.call_args[0][0]
            assert "1" in data
            assert data["1"]["name"] == "a"
            assert data["1"]["idPotion"] == 1
            assert "2" in data
            assert data["2"]["name"] == "z"
            assert data["2"]["idPotion"] == 2

@patch("asyncio.run", side_effect=lambda coro: coro.close())
def test_main(mock_run: Any) -> None:
    with unittest.mock.patch.dict('sys.modules'):

        import sys

        sys.modules.pop('scripts.medicines', None)

        runpy.run_module('scripts.medicines', run_name='__main__')
    mock_run.assert_called_once()
