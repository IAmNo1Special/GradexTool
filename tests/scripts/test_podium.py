import json
import sqlite3
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest

from scripts.podium import CurrentPodiumTable, WeeklyPodiumTable, db_path


@pytest.fixture
def temp_db(tmp_path: Any) -> Any:
    db_file = tmp_path / "test.db"
    return db_file

@pytest.fixture
def weekly_table(temp_db: Any) -> Any:
    table = WeeklyPodiumTable()
    table.db_path = temp_db
    return table

@pytest.fixture
def current_table(temp_db: Any) -> Any:
    table = CurrentPodiumTable()
    table.db_path = temp_db
    return table

def test_weekly_init() -> None:
    table = WeeklyPodiumTable()
    assert table.db_path == db_path

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_weekly_connect(weekly_table: Any) -> None:
    import aiosqlite
    conn = weekly_table._connect()
    assert isinstance(conn, aiosqlite.Connection)
    await conn.close()

@pytest.mark.asyncio
async def test_weekly_build(weekly_table: Any) -> None:
    with patch.object(weekly_table, 'create') as mock_create, \
         patch.object(weekly_table, 'rebuild') as mock_rebuild, \
         patch.object(weekly_table, 'count_entries') as mock_count:
        await weekly_table.build()
        mock_create.assert_called_once()
        mock_rebuild.assert_called_once()
        mock_count.assert_called_once()

@pytest.mark.asyncio
async def test_weekly_create(weekly_table: Any) -> None:
    await weekly_table.create()
    conn = sqlite3.connect(weekly_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weeklyPodium';")
    assert cursor.fetchone() is not None
    conn.close()

    # Call create again to hit the "DROP TABLE IF EXISTS" code path
    await weekly_table.create()
    conn = sqlite3.connect(weekly_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weeklyPodium';")
    assert cursor.fetchone() is not None
    conn.close()

@patch('scripts.podium.requests.get')
@pytest.mark.asyncio
async def test_weekly_rebuild_success(mock_get: Any, weekly_table: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "weeklyPodium": [
                {
                    "rank": 1,
                    "username": "user1",
                    "amount": 100,
                    "profilePicture": "url1",
                    "times": 5
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    await weekly_table.create()
    with patch.object(weekly_table, 'export_to_json') as mock_export:
        await weekly_table.rebuild()
        mock_export.assert_called_once()

    conn = sqlite3.connect(weekly_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weeklyPodium;")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == (1, "user1", 100, "url1", 5)
    conn.close()

@patch('scripts.podium.requests.get')
@pytest.mark.asyncio
async def test_weekly_rebuild_failure(mock_get: Any, weekly_table: Any, capsys: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with patch.object(weekly_table, 'export_to_json') as mock_export:
        await weekly_table.rebuild()
        mock_export.assert_not_called()

    captured = capsys.readouterr()
    assert "Failed to fetch data: 404" in captured.out

@patch('builtins.open', new_callable=mock_open)
@pytest.mark.asyncio
async def test_weekly_export_to_json(mock_file: Any, weekly_table: Any) -> None:
    await weekly_table.create()
    await weekly_table.add_entry(1, "user1", 100, "url1", 5)
    await weekly_table.export_to_json()

    mock_file.assert_called_once_with("./data/weekly_podium.json", "w")
    handle = mock_file()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    data = json.loads(written)
    assert len(data) == 1
    assert data[0]["rank"] == 1
    assert data[0]["username"] == "user1"
    assert data[0]["amount"] == 100
    assert data[0]["profile_picture"] == "url1"
    assert data[0]["times"] == 5

@pytest.mark.asyncio
async def test_weekly_count_entries(weekly_table: Any) -> None:
    await weekly_table.create()
    assert await weekly_table.count_entries() == 0
    await weekly_table.add_entry(1, "user1", 100, "url1", 5)
    assert await weekly_table.count_entries() == 1

@pytest.mark.asyncio
async def test_weekly_add_entry(weekly_table: Any) -> None:
    await weekly_table.create()
    await weekly_table.add_entry(1, "user1", 100, "url1", 5)
    conn = sqlite3.connect(weekly_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weeklyPodium;")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == (1, "user1", 100, "url1", 5)
    conn.close()


def test_current_init() -> None:
    table = CurrentPodiumTable()
    assert table.db_path == db_path

@pytest.mark.asyncio
async def test_current_connect(current_table: Any) -> None:
    import aiosqlite
    conn = current_table._connect()
    assert isinstance(conn, aiosqlite.Connection)
    await conn.close()

@pytest.mark.asyncio
async def test_current_build(current_table: Any) -> None:
    with patch.object(current_table, 'create') as mock_create, \
         patch.object(current_table, 'rebuild') as mock_rebuild, \
         patch.object(current_table, 'count_entries') as mock_count:
        await current_table.build()
        mock_create.assert_called_once()
        mock_rebuild.assert_called_once()
        mock_count.assert_called_once()

@pytest.mark.asyncio
async def test_current_create(current_table: Any) -> None:
    await current_table.create()
    conn = sqlite3.connect(current_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currentPodium';")
    assert cursor.fetchone() is not None
    conn.close()

    # Call create again to hit the "DROP TABLE IF EXISTS" code path
    await current_table.create()
    conn = sqlite3.connect(current_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currentPodium';")
    assert cursor.fetchone() is not None
    conn.close()

@patch('scripts.podium.requests.get')
@pytest.mark.asyncio
async def test_current_rebuild_success(mock_get: Any, current_table: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "currentPodium": [
                {
                    "rank": 1,
                    "username": "user1",
                    "profilePicture": "url1"
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    await current_table.create()
    with patch.object(current_table, 'export_to_json') as mock_export:
        await current_table.rebuild()
        mock_export.assert_called_once()

    conn = sqlite3.connect(current_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM currentPodium;")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == (1, "user1", "url1")
    conn.close()

@patch('scripts.podium.requests.get')
@pytest.mark.asyncio
async def test_current_rebuild_failure(mock_get: Any, current_table: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    with patch.object(current_table, 'export_to_json') as mock_export:
        await current_table.rebuild()
        mock_export.assert_not_called()

@patch('builtins.open', new_callable=mock_open)
@pytest.mark.asyncio
async def test_current_export_to_json(mock_file: Any, current_table: Any) -> None:
    await current_table.create()
    await current_table.add_entry(1, "user1", "url1")
    await current_table.export_to_json()

    mock_file.assert_called_once_with("./data/current_podium.json", "w")
    handle = mock_file()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    data = json.loads(written)
    assert len(data) == 1
    assert data[0]["rank"] == 1
    assert data[0]["username"] == "user1"
    assert data[0]["profile_picture"] == "url1"

@pytest.mark.asyncio
async def test_current_count_entries(current_table: Any) -> None:
    await current_table.create()
    assert await current_table.count_entries() == 0
    await current_table.add_entry(1, "user1", "url1")
    assert await current_table.count_entries() == 1

@pytest.mark.asyncio
async def test_current_add_entry(current_table: Any) -> None:
    await current_table.create()
    await current_table.add_entry(1, "user1", "url1")
    conn = sqlite3.connect(current_table.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM currentPodium;")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == (1, "user1", "url1")
    conn.close()

