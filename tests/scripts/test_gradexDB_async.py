import json  # noqa: N999
import sqlite3
from collections.abc import Generator
from contextlib import closing
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from scripts.gradexDB import (
    AbilitiesTable,
    CapsulesTable,
    CounterdexTable,
    CurrentPodiumTable,
    FruitysTable,
    ItemsTable,
    MovesTable,
    NaturesTable,
    OwnedLandsTable,
    RevomonMovesTable,
    RevomonTable,
    TypesTable,
    UsersTable,
    WeeklyPodiumTable,
    update_gradex_db,
)


@pytest.fixture
def mock_db(tmp_path: Any) -> Generator[str]:
    db_file = tmp_path / "test.db"
    with patch("scripts.gradexDB.db_path", str(db_file)):
        yield str(db_file)


@pytest.fixture
def mock_requests() -> Generator[tuple[MagicMock, MagicMock]]:
    with (
        patch("scripts.gradexDB.requests.get") as mock_get,
        patch("scripts.gradexDB.requests.post") as mock_post,
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"revomons": [{"idRevodex": 1, "idRevomon": 1, "name": "TestMon"}]}
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "moves": [
                    {
                        "idMove": 1,
                        "capsule": 1,
                        "name": "testmove",
                        "category": "cat",
                        "type": "type",
                        "description": "desc",
                        "accuracy": 100,
                        "power": 40,
                        "pp": 35,
                        "priority": 1,
                        "method": "level",
                        "level": 5,
                    }
                ]
            }
        }
        yield mock_get, mock_post


@pytest.fixture
def mock_json_files() -> Any:
    mock_data = {
        "./data/counterdex.json": json.dumps(
            [
                {
                    "name": "testmon",
                    "description": "desc",
                    "tier": "A",
                    "metamoves": "none",
                    "metabuilds": "none",
                    "tips": "none",
                    "counters": "none",
                    "weakness": "none",
                }
            ]
        ),
        "./data/abilities.json": json.dumps(
            {
                "1": {
                    "id": 1,
                    "name": "overgrow",
                    "effect_entries": [{"short_effect": "Boosts grass."}],
                },
                "2": {
                    "id": 2,
                    "name": "blaze",
                    "flavor_text_entries": [{"flavor_text": "Boosts fire."}],
                },
            }
        ),
        "./data/capsules.json": json.dumps(
            [{"name": "capsule1", "description": "captures"}]
        ),
        "./data/fruitys.json": json.dumps(
            {
                "1": {
                    "idFruity": 1,
                    "name": "apple",
                    "description": "tasty",
                    "type": "food",
                }
            }
        ),
        "./data/items.json": json.dumps(
            {
                "item1": {
                    "name": "potion",
                    "description": "heals",
                    "obtained_from": "shop",
                    "cost": 100,
                }
            }
        ),
        "./data/natures.json": json.dumps(
            {
                "nature1": {
                    "name": "adamant",
                    "increased_stat": "atk",
                    "decreased_stat": "spa",
                }
            }
        ),
        "./data/revomon.json": json.dumps(
            [
                {
                    "dex_id": 1,
                    "mon_id": 1,
                    "name": "testmon",
                    "description": "desc",
                    "type1": "fire",
                    "type2": None,
                    "ability1": "blaze",
                    "ability2": None,
                    "ability_hidden": None,
                    "hp": 50,
                    "atk": 50,
                    "def": 50,
                    "spa": 50,
                    "spd": 50,
                    "spe": 50,
                    "evolution": None,
                    "level_evolution": None,
                    "rarity": "common",
                }
            ]
        ),
        "./data/base_types.json": json.dumps(["fire"]),
        "./data/type_charts.json": json.dumps({"fire": {"neutral": 1.0}}),
    }

    def custom_open(filename: Any, mode: Any = "r", *args: Any, **kwargs: Any) -> Any:
        if mode == "w":
            return mock_open()()
        content = mock_data.get(filename, "[]")
        return mock_open(read_data=content)()

    with patch("builtins.open", side_effect=custom_open) as m_open:
        yield m_open


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_counterdex_table(
    mock_db: Any, mock_requests: Any, mock_json_files: Any
) -> None:
    table = CounterdexTable()
    await table.build()

    # Test adding and getting info
    await table.add_revomon(
        2, 2, "anothermon", "desc", "tier", "m", "b", "tips", "counters"
    )
    assert await table.count_entries() == 2
    info = await table.get_info("anothermon")
    assert len(info) == 1
    assert info[0][2] == "anothermon"
    assert info[0][9] is None  # weakness


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_abilities_table(mock_db: Any, mock_json_files: Any) -> None:
    table = AbilitiesTable()
    await table.build()
    assert await table.count_entries() == 2
    names = await table.get_names()
    assert "overgrow" in names
    assert "blaze" in names
    info = await table.get_info("overgrow")
    assert len(info) == 1
    assert info[0][1] == "overgrow"


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_capsules_table(mock_db: Any, mock_json_files: Any) -> None:
    table = CapsulesTable()
    await table.build()
    assert await table.count_entries() == 1


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_fruitys_table(mock_db: Any, mock_json_files: Any) -> None:
    table = FruitysTable()
    await table.build()
    assert await table.count_entries() == 1
    names = await table.get_names()
    assert "apple" in names
    info = await table.get_info("apple")
    assert len(info) == 1
    assert info[0][1] == "apple"


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_items_table(mock_db: Any, mock_json_files: Any) -> None:
    table = ItemsTable()
    await table.build()
    await table.add_item("item2", "desc2", "shop", 50)
    assert await table.count_entries() == 2
    info = await table.get_info("item")
    assert len(info) == 1
    names = await table.get_names()
    assert "potion" in names
    assert "item2" in names


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_moves_table(
    mock_db: Any, mock_requests: Any, mock_json_files: Any
) -> None:
    # MovesTable.rebuild depends on RevomonTable
    rev_table = RevomonTable()
    await rev_table.create()
    rev_table.rebuild = MagicMock()  # type: ignore[method-assign]
    # Add a dummy revomon so get_mon_ids returns something
    with closing(sqlite3.connect(mock_db)) as conn, conn:
        conn.execute(
            "INSERT INTO revomon (dex_id, mon_id, name) VALUES (1, 1, 'testmon')"
        )
        conn.commit()

    table = MovesTable()
    await table.build()
    await table.rebuild()  # Trigger rowcount == 0 (duplicate skip)

    await table.add_move(2, None, "move2", "cat", "type", "desc2", 100, 50, 10, 0)
    assert await table.count_entries() == 2

    info = await table.get_info("move2")
    assert len(info) == 1
    names = await table.get_names()
    assert "move2" in names


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_natures_table(mock_db: Any, mock_json_files: Any) -> None:
    table = NaturesTable()
    await table.build()
    await table.add_nature("timid", None, "atk", "likes", "dislikes")
    assert await table.count_entries() == 2

    info = await table.get_info("timid")
    assert len(info) == 1
    names = await table.get_names()
    assert "adamant" in names


@pytest.mark.asyncio
@pytest.mark.gradexDB
async def test_ownedlands_table(mock_db: Any, mock_json_files: Any) -> None:
    # OwnedLandsTable has async build and uses utils
    with (
        patch("utils.land_utils.get_land_data", new_callable=AsyncMock) as m_land,
        patch(
            "utils.emoji_utils.list_application_emojis", new_callable=AsyncMock
        ) as m_emojis,
        patch(
            "utils.emoji_utils.create_emoji_from_url", new_callable=AsyncMock
        ) as m_create,
    ):
        m_land.return_value = [
            {
                "owners_address": "0x1",
                "land_info": [
                    {
                        "token_id": 1,
                        "id": 1,
                        "biome": "forest",
                        "land_type": "base",
                        "rarity": "common",
                        "size": "small",
                        "img_url": "url",
                    }
                ],
            },
            {
                "owners_address": "0x2",
                "land_info": [
                    {
                        "token_id": 2,
                        "id": 2,
                        "biome": "desert",
                        "land_type": "advanced",
                        "rarity": "rare",
                        "size": "medium",
                        "img_url": "url2",
                    }
                ],
            },
        ]
        m_emojis.return_value = [{"name": "forest_base", "id": "123"}]
        m_create.return_value = {"id": "456", "name": "desert_advanced"}

        table = OwnedLandsTable()
        # Mock update_lands_sale_data
        table.update_lands_sale_data = AsyncMock()  # type: ignore[method-assign]
        await table.build()

        assert await table.count_entries() == 2
        ids = await table.get_ids()
        assert 1 in ids
        biomes = await table.get_biomes()
        assert "forest" in biomes
        land_types = await table.get_land_types()
        assert "base" in land_types

        info = await table.get_info(token_id=1, sort_by="biome", asc=False)
        assert len(info) == 1
        info2 = await table.get_info(
            id=1,
            owners_address="0x1",
            biome="forest",
            land_type="base",
            rarity="common",
            size="small",
            img_url="url",
            sale_status=0,
            sort_by="id",
        )
        assert len(info2) == 1

        # Test remaining sorting logic branches
        await table.get_info(sort_by="owners_address")
        await table.get_info(sort_by="land_type")
        await table.get_info(sort_by="rarity")
        await table.get_info(sort_by="size")
        await table.get_info(sort_by="img_url")
        await table.get_info(sort_by="sale_status")
        await table.get_info(sort_by="invalid_sort")

        # Hit sale_status filter and empty result
        await table.get_info(sale_status=1)
        await table.get_info(token_id=999)


@pytest.mark.asyncio
@pytest.mark.gradexDB
async def test_ownedlands_update_sale_data(mock_db: Any) -> None:
    table = OwnedLandsTable()
    await table.create()
    with closing(sqlite3.connect(mock_db)) as conn, conn:
        conn.execute(
            "INSERT INTO ownedLands (token_id, id, owners_address, biome, land_type, rarity, size, img_url, emoji, for_sale) VALUES (1, 1, '0x', 'f', 'b', 'r', 's', 'u', 'e', 0)"
        )
        conn.execute(
            "INSERT INTO ownedLands (token_id, id, owners_address, biome, land_type, rarity, size, img_url, emoji, for_sale) VALUES (2, 2, '0x', 'f', 'b', 'r', 's', 'u', 'e', 0)"
        )
        conn.commit()

    with (
        patch("scripts.gradexDB.OwnedLandsTable.get_ids") as m_ids,
        patch(
            "scripts.gradexDB.get_lands_for_sale_amount", new_callable=AsyncMock
        ) as m_sale_data,
    ):
        m_ids.return_value = [1, 2]
        m_sale_data.return_value = {
            "1": {
                "owners_address": "0x2",
                "for_sale_token": 10,
                "token_symbol": "ETH",
                "for_sale_usd": 20,
            }
        }
        await table.update_lands_sale_data()
        info = await table.get_info(token_id=1)
        assert info[0][9] == 1  # for_sale


@pytest.mark.asyncio
@pytest.mark.gradexDB
async def test_revomon_table(mock_db: Any, mock_json_files: Any) -> None:
    table = RevomonTable()
    await table.build()
    assert await table.count_entries() == 1
    mon_ids = await table.get_mon_ids()
    assert 1 in mon_ids
    assert await table.get_id_by_id(1) == 1
    assert await table.get_name_by_id(1) == "testmon"
    names = await table.get_names()
    assert "testmon" in names
    assert await table.has_ability("blaze", "testmon") is True
    assert await table.has_ability("overgrow", "testmon") is False
    assert await table.has_ability("blaze") == ["testmon"]
    assert await table.has_ability("overgrow") == []


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_revomon_moves_table(
    mock_db: Any, mock_requests: Any, mock_json_files: Any
) -> None:
    rev_table = RevomonTable()
    await rev_table.create()
    moves_table = MovesTable()
    await moves_table.create()
    with closing(sqlite3.connect(mock_db)) as conn, conn:
        conn.execute(
            "INSERT INTO revomon (dex_id, mon_id, name) VALUES (1, 1, 'testmon')"
        )
        conn.execute(
            "INSERT INTO moves (id, name, category, type, description, accuracy, power, pp, priority) VALUES (1, 'testmove', 'cat', 'type', 'desc', 100, 40, 35, 1)"
        )
        conn.commit()

    table = RevomonMovesTable()
    await table.build()
    await table.rebuild()  # Trigger continue branch for existing entry

    assert await table.count_entries() == 1
    await table.add_link(1, "testmon", 2, "move2", "tm", 0)
    assert await table.count_entries() == 2

    moves = await table.get_moves_for_revomon(1)
    assert len(moves) == 1  # Note: only matches existing moves table entries

    mons = await table.get_mons_for_move(move_id=1)
    assert "testmon" in mons
    mons = await table.get_mons_for_move(move_name="testmove")
    assert "testmon" in mons
    assert await table.get_mons_for_move() is None


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_current_podium_table(mock_db: Any) -> None:
    table = CurrentPodiumTable()
    await table.build()
    assert await table.count_entries() == 0


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_weekly_podium_table(mock_db: Any) -> None:
    table = WeeklyPodiumTable()
    await table.build()
    assert await table.count_entries() == 0


@pytest.mark.gradexDB
@pytest.mark.asyncio
async def test_types_table(mock_db: Any, mock_json_files: Any) -> None:
    table = TypesTable()
    await table.build()
    assert await table.count_entries() == 1

    await table.add_type("water", {"type 1": "water", "neutral": 1.0})
    assert await table.count_entries() == 2

    info = await table.get_info("water")
    assert len(info) == 1
    info2 = await table.get_info("water", "something")
    assert len(info2) == 0
    mono = await table.get_mono_types()
    assert "fire" in mono


@pytest.mark.asyncio
@pytest.mark.gradexDB
async def test_users_table(mock_db: Any) -> None:
    table = UsersTable()
    await table.build()

    await table.add_user(1, "user1", 1, "0x", 0, 0, 100, 50, 10, 5, 2, 1)
    assert await table.count_entries() == 1

    await table.update_user(1, username="updated")
    user = await table.get_user(1)
    assert user["username"] == "updated"

    with pytest.raises(ValueError):
        await table.update_user(None)

    # Manually export to JSON
    await table.export_to_json()

    users = await table.get_users()
    assert len(users) == 1

    await table.delete_user(1)
    assert await table.count_entries() == 0
    assert await table.get_user(1) is False


@pytest.mark.asyncio
@pytest.mark.gradexDB
async def test_update_gradex_db(
    mock_db: Any, mock_requests: Any, mock_json_files: Any
) -> None:
    with (
        patch("utils.land_utils.get_land_data", new_callable=AsyncMock) as m_land,
        patch(
            "utils.emoji_utils.list_application_emojis", new_callable=AsyncMock
        ) as m_emojis,
        patch("utils.emoji_utils.create_emoji_from_url", new_callable=AsyncMock),
    ):
        m_land.return_value = []
        m_emojis.return_value = []

        # Avoid running OwnedLandsTable in the test because it is commented out in gradexDB.py
        await update_gradex_db()
