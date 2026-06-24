from typing import Any

"""Comprehensive tests for scripts/abilities.py"""

import asyncio  # noqa: E402
import json  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, mock_open, patch  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402

# We can import directly if PYTHONPATH is set or we use normal imports
from scripts.abilities import (  # noqa: E402
    AbilitiesTable,
    fetch_ability,
    get_abilities,
    process_string,
    remove_key_recursive,
    traverse,
)


def test_remove_key_recursive() -> None:
    obj = {
        "a": 1,
        "language": "en",
        "nested": {"language": "fr", "b": 2},
        "lst": [{"language": "es", "c": 3}, "just string"],
    }
    remove_key_recursive(obj, "language")
    assert obj == {"a": 1, "nested": {"b": 2}, "lst": [{"c": 3}, "just string"]}


def test_process_string() -> None:
    assert process_string(123) == 123
    assert process_string("no change") == "no change"
    assert process_string("line1\nline2") == "line1 line2"
    assert process_string("’smart‘ “quotes”") == "'smart' \"quotes\""


def test_traverse() -> None:
    obj = {
        "str": "line1\nline2",
        "int": 1,
        "list": ["“quote”", 2],
        "dict": {"nested": "’smart‘"},
    }
    expected = {
        "str": "line1 line2",
        "int": 1,
        "list": ['"quote"', 2],
        "dict": {"nested": "'smart'"},
    }
    assert traverse(obj) == expected


@pytest.mark.asyncio
async def test_fetch_ability() -> None:
    # Mock httpx.AsyncClient
    client = AsyncMock(spec=httpx.AsyncClient)
    semaphore = asyncio.Semaphore(1)

    # Test 1: 200 OK, full processing
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "overgrow",
        "generation": "gen1",
        "is_main_series": True,
        "effect_entries": [
            {"language": {"name": "en"}, "effect": "en effect"},
            {"language": {"name": "fr"}, "effect": "fr effect"},
        ],
        "flavor_text_entries": [
            {"language": {"name": "fr"}, "flavor_text": "fr flavor"},
            {"language": {"name": "en"}, "flavor_text": "en flavor 1"},
            {"language": {"name": "en"}, "flavor_text": "en flavor 2"},
        ],
        "names": [
            {"language": {"name": "en"}, "name": "Overgrow"},
            {"language": {"name": "fr"}, "name": "Engrais"},
        ],
        "effect_changes": [
            {
                "effect_entries": [
                    {"language": {"name": "en"}, "effect": "en change"},
                    {"language": {"name": "fr"}, "effect": "fr change"},
                ]
            }
        ],
    }
    client.get.return_value = mock_response

    ability_to_revomon = {"overgrow": ["bulbasaur"]}
    res_type, res_val = await fetch_ability(
        client, semaphore, "overgrow", ability_to_revomon
    )

    assert res_type == "found"
    assert "generation" not in res_val
    assert "is_main_series" not in res_val
    assert len(res_val["effect_entries"]) == 1
    assert res_val["effect_entries"][0]["effect"] == "en effect"
    assert len(res_val["flavor_text_entries"]) == 1
    assert res_val["flavor_text_entries"][0]["flavor_text"] == "en flavor 2"
    assert len(res_val["names"]) == 1
    assert res_val["names"][0]["name"] == "overgrow"
    assert len(res_val["effect_changes"][0]["effect_entries"]) == 1
    assert res_val["effect_changes"][0]["effect_entries"][0]["effect"] == "en change"
    assert res_val["pokemon"] == ["bulbasaur"]

    # Test 2: flavor text entries empty for en
    mock_response.json.return_value = {
        "name": "overgrow",
        "flavor_text_entries": [
            {"language": {"name": "fr"}, "flavor_text": "fr flavor"},
        ],
    }
    res_type, res_val = await fetch_ability(client, semaphore, "overgrow", {})
    assert res_type == "found"
    assert res_val["flavor_text_entries"] == []
    assert res_val["pokemon"] == []

    # Test 3: 404 response
    mock_response_404 = MagicMock()
    mock_response_404.status_code = 404
    client.get.return_value = mock_response_404
    res_type, res_val = await fetch_ability(client, semaphore, "unknown_ability", {})
    assert res_type == "unknown"
    assert res_val == "unknown_ability"

    # Test 4: other status code
    mock_response_500 = MagicMock()
    mock_response_500.status_code = 500
    client.get.return_value = mock_response_500
    res_type, res_val = await fetch_ability(client, semaphore, "error_ability", {})
    assert res_type == "unknown"
    assert res_val == "error_ability"

    # Test 5: HTTPError
    client.get.side_effect = httpx.HTTPError("Network error")
    res_type, res_val = await fetch_ability(client, semaphore, "http_error", {})
    assert res_type == "unknown"
    assert res_val == "http_error"

    # Test 6: Exception
    client.get.side_effect = Exception("Unknown error")
    res_type, res_val = await fetch_ability(client, semaphore, "exc_error", {})
    assert res_type == "unknown"
    assert res_val == "exc_error"


@pytest.mark.asyncio
async def test_get_abilities_file_not_found() -> None:
    with patch("scripts.abilities.os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            await get_abilities()


@pytest.mark.asyncio
@patch("scripts.abilities.httpx.AsyncClient")
@patch("scripts.abilities.os.path.exists")
@patch("scripts.abilities.os.makedirs")
async def test_get_abilities_success(
    mock_makedirs: Any, mock_exists: Any, mock_client_cls: Any
) -> None:
    mock_exists.return_value = True

    revomon_data = [
        {
            "name": "Bulbasaur",
            "idRevomon": "1",
            "ability1": "Overgrow ",
            "ability2": None,
            "abilityHidden": " Chlorophyll",
        }
    ]

    m_open = mock_open(read_data=json.dumps(revomon_data))

    with patch("builtins.open", m_open):
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        async def mock_fetch(
            client: Any, semaphore: Any, ability: Any, ability_to_revomon: Any
        ) -> Any:
            if ability == "overgrow":
                return (
                    "found",
                    {
                        "name": "overgrow",
                        "language": {"name": "en"},
                        "version_group": {"name": "x-y"},
                        "names": [{"name": "Overgrow", "language": {"name": "en"}}],
                        "desc": "Pokémon power\nnewline",
                    },
                )
            else:
                return ("unknown", "chlorophyll")

        with patch("scripts.abilities.fetch_ability", side_effect=mock_fetch):
            with (
                patch("scripts.abilities.REVOMON_FILE", "revomon.json"),
                patch("scripts.abilities.ABILITIES_FILE", "abilities.json"),
                patch("scripts.abilities.UNKNOWN_ABILITIES_FILE", "unknown.json"),
            ):
                await get_abilities()

                # Verify files were written
                assert m_open.call_count == 3
                write_calls = [call for call in m_open.mock_calls if "write" in call[0]]

                # The output writes should replace "Pokémon" with "Monster"
                written_content = "".join(
                    [c.args[0] for c in write_calls if isinstance(c.args[0], str)]
                )
                assert "Monster" in written_content
                assert "Pokémon" not in written_content


@pytest.mark.asyncio
async def test_abilities_table(tmp_path: Any) -> None:
    db_path = tmp_path / "test.db"

    with patch("scripts.abilities.GRADEX_DB_PATH", db_path):
        table = AbilitiesTable()

        # create
        table.create()

        # rebuild
        mock_abilities = [
            {"name": "Overgrow", "description": "Grass moves"},
            {"name": "Blaze", "description": "Fire moves"},
        ]
        m_open = mock_open(read_data=json.dumps(mock_abilities))

        with patch("builtins.open", m_open):
            with patch.object(table, "export_to_json") as mock_export:
                table.rebuild()
                mock_export.assert_called_once()

        # count_entries
        assert table.count_entries() == 2

        # add_ability
        table.add_ability("Torrent", "Water moves")
        assert table.count_entries() == 3

        # get_info
        info = table.get_info("overgrow")
        assert len(info) == 1
        assert info[0][0] == "overgrow"
        assert info[0][1] == "grass moves"

        # get_names
        names = table.get_names()
        assert "overgrow" in names
        assert "blaze" in names
        assert "torrent" in names

        # export_to_json
        m_export_open = mock_open()
        with patch("builtins.open", m_export_open):
            table.export_to_json()
            m_export_open.assert_called_once_with("./data/abilities.json", "w")

        # build
        with (
            patch.object(table, "create") as m_create,
            patch.object(table, "rebuild") as m_rebuild,
            patch.object(table, "count_entries") as m_count,
        ):
            table.build()
            m_create.assert_called_once()
            m_rebuild.assert_called_once()
            m_count.assert_called_once()
