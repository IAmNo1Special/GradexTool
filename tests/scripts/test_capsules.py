import json
import runpy
import sys
import unittest.mock
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest

scripts_dir = Path(__file__).parent.parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from scripts.capsules import CapsulesTable, get_capsules  # noqa: E402


@pytest.fixture
def mock_moves_data() -> Any:
    return [
        {"capsule": 1, "idMove": 10},
        {"capsule": None, "idMove": 11},
        {"idMove": 12}, # Missing capsule
        {"capsule": 2}, # Missing idMove
        {"capsule": 3, "idMove": 13}
    ]

def test_get_capsules_moves_exists(mock_moves_data: Any) -> None:
    with patch("scripts.capsules.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_moves_data))), \
         patch("os.makedirs") as mock_makedirs:
        get_capsules()
        mock_makedirs.assert_called_once()

def test_get_capsules_moves_not_exists(mock_moves_data: Any) -> None:
    mock_moves_module = MagicMock()
    with patch("scripts.capsules.Path.exists", return_value=False), \
         patch.dict("sys.modules", {"scripts.gradex.moves": mock_moves_module}), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_moves_data))), \
         patch("os.makedirs"):
        get_capsules()
        mock_moves_module.main.assert_called_once()

def test_capsules_table_init() -> None:
    table = CapsulesTable()
    assert hasattr(table, "db_path")

@pytest.mark.asyncio
async def test_capsules_table_build() -> None:
    table = CapsulesTable()
    with patch.object(table, "create") as mock_create, \
         patch.object(table, "rebuild") as mock_rebuild, \
         patch.object(table, "count_entries") as mock_count:
        await table.build()
        mock_create.assert_called_once()
        mock_rebuild.assert_called_once()
        mock_count.assert_called_once()

@pytest.mark.asyncio
async def test_capsules_table_connect() -> None:
    table = CapsulesTable()
    with patch("sqlite3.connect") as mock_connect:
        table._connect()
        mock_connect.assert_called_once_with(table.db_path)

@pytest.mark.asyncio
async def test_capsules_table_create() -> None:
    table = CapsulesTable()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    with patch.object(table, "_connect", return_value=mock_conn):
        table.create()
        mock_conn.execute.assert_called_with("DROP TABLE IF EXISTS capsules;")
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

@pytest.mark.asyncio
async def test_capsules_table_rebuild() -> None:
    table = CapsulesTable()
    mock_mon_ids = [1, 2]
    mock_revomon_table = MagicMock()
    mock_revomon_table.get_mon_ids.return_value = mock_mon_ids

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1

    mock_response_1 = MagicMock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = {
        "data": {
            "moves": [
                {"idMove": 10, "capsule": 1, "name": "Move 1"},
                {"idMove": 11, "capsule": None, "name": "Move 2"},
                {"idMove": 12, "capsule": 2, "name": "Move 3"}
            ]
        }
    }

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 404 # Skip this one

    def mock_requests_get(url: Any) -> Any:
        if url.endswith("1"):
            return mock_response_1
        return mock_response_2

    with patch("scripts.capsules.RevomonTable", return_value=mock_revomon_table), \
         patch("requests.get", side_effect=mock_requests_get), \
         patch.object(table, "_connect", return_value=mock_conn), \
         patch.object(table, "export_to_json") as mock_export:

        await table.rebuild()

        # 1 valid response with 2 capsule moves.
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()
        mock_export.assert_called_once()

@pytest.mark.asyncio
async def test_capsules_table_rebuild_rowcount_zero() -> None:
    table = CapsulesTable()
    mock_revomon_table = MagicMock()
    mock_revomon_table.get_mon_ids.return_value = [1]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"moves": [{"idMove": 10, "capsule": 1, "name": "Move 1"}]}
    }

    with patch("scripts.capsules.RevomonTable", return_value=mock_revomon_table), \
         patch("requests.get", return_value=mock_response), \
         patch.object(table, "_connect", return_value=mock_conn), \
         patch.object(table, "export_to_json"):

        await table.rebuild()
        assert mock_cursor.execute.call_count == 1

@pytest.mark.asyncio
async def test_capsules_table_export_to_json() -> None:
    table = CapsulesTable()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1, 10, "move_1"), (2, 20, "move_2")]
    mock_cursor.description = [("cap_num",), ("move_id",), ("move_name",)]

    with patch.object(table, "_connect", return_value=mock_conn), \
         patch("builtins.open", mock_open()) as m_open:
        table.export_to_json()

        mock_cursor.execute.assert_called_with("SELECT * FROM capsules;")
        # Check json.dump
        handle = m_open()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "move_1" in written
        assert "move_2" in written

@pytest.mark.asyncio
async def test_capsules_table_count_entries() -> None:
    table = CapsulesTable()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (5,)

    with patch.object(table, "_connect", return_value=mock_conn):
        result = table.count_entries()

        mock_cursor.execute.assert_called_with("SELECT COUNT(*) FROM capsules;")
        mock_conn.close.assert_called_once()
        assert result == 5

@pytest.mark.asyncio
async def test_capsules_table_add_capsule() -> None:
    table = CapsulesTable()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch.object(table, "_connect", return_value=mock_conn):
        table.add_capsule(1, 10, "Move 1")

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

def test_main() -> None:
    with patch("scripts.capsules.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='[]')), \
         patch("os.makedirs"):
        with unittest.mock.patch.dict('sys.modules'):

            import sys

            sys.modules.pop('scripts.capsules', None)

            runpy.run_module('scripts.capsules', run_name='__main__')
