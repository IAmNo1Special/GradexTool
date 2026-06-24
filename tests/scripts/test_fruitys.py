import runpy
import unittest.mock
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest

from scripts.fruitys import FruitysTable, get_fruitys


@patch("scripts.fruitys.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("scripts.fruitys.json.dump")
def test_get_fruitys(
    mock_json_dump: Any, mock_open_file: Any, mock_makedirs: Any
) -> None:
    with patch(
        "scripts.fruitys.FRUITYS",
        [{"name": "Test", "type": "TestType", "description": "some description."}],
    ):
        get_fruitys()
        mock_makedirs.assert_called_once()
        mock_open_file.assert_called_once()
        mock_json_dump.assert_called_once()

        args, kwargs = mock_json_dump.call_args
        data = args[0]
        assert "1" in data
        assert data["1"]["name"] == "test"
        assert data["1"]["type"] == "testtype"
        assert data["1"]["description"] == "Some description."
        assert data["1"]["idFruity"] == 1


@patch("scripts.fruitys.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("scripts.fruitys.json.dump")
def test_get_fruitys_missing_keys(
    mock_json_dump: Any, mock_open_file: Any, mock_makedirs: Any
) -> None:
    with patch("scripts.fruitys.FRUITYS", [{}]):
        get_fruitys()
        args, kwargs = mock_json_dump.call_args
        data = args[0]
        assert "1" in data
        assert "name" not in data["1"]


class TestFruitysTable:
    @pytest.fixture
    def mock_db(self) -> None:  # type: ignore[misc]
        with patch("scripts.fruitys.sqlite3.connect") as mock_connect:
            yield mock_connect

    @pytest.fixture
    def table(self) -> Any:
        return FruitysTable()

    def test_init(self, table: Any) -> None:
        assert table.db_path is not None

    def test_build(self, table: Any) -> None:
        table.create = MagicMock()
        table.rebuild = MagicMock()
        table.count_entries = MagicMock()
        table.build()
        table.create.assert_called_once()
        table.rebuild.assert_called_once()
        table.count_entries.assert_called_once()

    def test_create(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        table.create()

        mock_conn.execute.assert_called_with("DROP TABLE IF EXISTS fruitys;")
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("scripts.fruitys.json.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_rebuild(
        self, mock_open_file: Any, mock_json_load: Any, table: Any, mock_db: Any
    ) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        mock_json_load.return_value = [
            {"name": "A", "description": "desc", "type": "type"}
        ]
        table.export_to_json = MagicMock()

        table.rebuild()

        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        table.export_to_json.assert_called_once()

    @patch("scripts.fruitys.json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_export_to_json(
        self, mock_open_file: Any, mock_json_dump: Any, table: Any, mock_db: Any
    ) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("a", "b", "c")]
        mock_cursor.description = [("name",), ("description",), ("type",)]

        table.export_to_json()

        mock_json_dump.assert_called_once()

    def test_count_entries(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [5]

        assert table.count_entries() == 5
        mock_conn.close.assert_called_once()

    def test_add_fruity(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        table.add_fruity("name", "desc", "type")
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_info(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("name", "desc", "type")]

        assert table.get_info("name") == [("name", "desc", "type")]

    def test_get_type(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("type",)]

        assert table.get_type("name") == "type"

    def test_get_names(self, table: Any, mock_db: Any) -> None:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("name1",), ("name2",)]

        assert table.get_names() == ["name1", "name2"]


@patch("os.makedirs")
@patch("json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_main(mock_open_file: Any, mock_json_dump: Any, mock_makedirs: Any) -> None:
    with unittest.mock.patch.dict("sys.modules"):
        import sys

        sys.modules.pop("scripts.fruitys", None)

        runpy.run_module("scripts.fruitys", run_name="__main__")
