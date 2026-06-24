import asyncio
import json
import unittest.mock
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from scripts import moves


def test_env_bool(monkeypatch: Any) -> None:
    monkeypatch.delenv("TEST_BOOL", raising=False)
    assert moves._env_bool("TEST_BOOL") is False
    assert moves._env_bool("TEST_BOOL", default=True) is True

    monkeypatch.setenv("TEST_BOOL", "1")
    assert moves._env_bool("TEST_BOOL") is True

    monkeypatch.setenv("TEST_BOOL", "FALSE")
    assert moves._env_bool("TEST_BOOL") is False


def test_env_int(monkeypatch: Any) -> None:
    monkeypatch.delenv("TEST_INT", raising=False)
    assert moves._env_int("TEST_INT", 5) == 5

    monkeypatch.setenv("TEST_INT", "10")
    assert moves._env_int("TEST_INT", 5) == 10

    monkeypatch.setenv("TEST_INT", "not_an_int")
    assert moves._env_int("TEST_INT", 5) == 5


def test_env_float(monkeypatch: Any) -> None:
    monkeypatch.delenv("TEST_FLOAT", raising=False)
    assert moves._env_float("TEST_FLOAT", 1.5) == 1.5

    monkeypatch.setenv("TEST_FLOAT", "2.5")
    assert moves._env_float("TEST_FLOAT", 1.5) == 2.5

    monkeypatch.setenv("TEST_FLOAT", "not_a_float")
    assert moves._env_float("TEST_FLOAT", 1.5) == 1.5


@pytest.mark.asyncio
async def test_request_pacer() -> None:
    pacer = moves.RequestPacer(0.1)
    start_time = asyncio.get_running_loop().time()
    await pacer.wait_for_slot()
    await pacer.wait_for_slot()
    end_time = asyncio.get_running_loop().time()
    assert end_time - start_time >= 0.1

    await pacer.pause_all(0.2)
    start_time = asyncio.get_running_loop().time()
    await pacer.wait_for_slot()
    end_time = asyncio.get_running_loop().time()
    assert end_time - start_time >= 0.2


def test_retry_after_seconds() -> None:
    # Header missing
    response = httpx.Response(429, request=httpx.Request("GET", "http://test"))
    assert moves._retry_after_seconds(response) is None

    # Header is float
    response = httpx.Response(
        429, headers={"Retry-After": "5.5"}, request=httpx.Request("GET", "http://test")
    )
    assert moves._retry_after_seconds(response) == 5.5

    # Header is date
    future = datetime.now(UTC) + timedelta(seconds=10)
    date_str = future.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response = httpx.Response(
        429,
        headers={"Retry-After": date_str},
        request=httpx.Request("GET", "http://test"),
    )
    assert 9 <= moves._retry_after_seconds(response) <= 11  # type: ignore[operator]

    # Header is valid date but missing tz
    date_str_naive = future.strftime("%a, %d %b %Y %H:%M:%S")
    response = httpx.Response(
        429,
        headers={"Retry-After": date_str_naive},
        request=httpx.Request("GET", "http://test"),
    )
    assert 9 <= moves._retry_after_seconds(response) <= 11  # type: ignore[operator]

    # Header is invalid date
    response = httpx.Response(
        429,
        headers={"Retry-After": "invalid_date"},
        request=httpx.Request("GET", "http://test"),
    )
    assert moves._retry_after_seconds(response) is None


def test_main_block(monkeypatch: Any) -> None:
    import runpy

    mock_run = MagicMock(side_effect=lambda coro: coro.close())
    monkeypatch.setattr("asyncio.run", mock_run)

    mock_basic_config = MagicMock()
    monkeypatch.setattr("logging.basicConfig", mock_basic_config)

    with unittest.mock.patch.dict("sys.modules"):
        import sys

        sys.modules.pop("scripts.moves", None)

        runpy.run_module("scripts.moves", run_name="__main__")

    mock_basic_config.assert_called_once()
    mock_run.assert_called_once()


def test_load_json_file(tmp_path: Any) -> None:
    # Non-existent file
    file_path = tmp_path / "test.json"
    assert moves._load_json_file(file_path) is None

    # Valid file
    file_path.write_text('{"key": "value"}', encoding="utf-8")
    assert moves._load_json_file(file_path) == {"key": "value"}

    # Invalid file
    file_path.write_text("not_json", encoding="utf-8")
    assert moves._load_json_file(file_path) is None


def test_save_json_file(tmp_path: Any) -> None:
    file_path = tmp_path / "test.json"
    data = {"key": "value"}
    moves._save_json_file(file_path, data)
    assert json.loads(file_path.read_text(encoding="utf-8")) == data


def test_id_revomon_list() -> None:
    revomon_data = [{"idRevomon": "1"}, {"idRevomon": "2"}, {"name": "test"}]
    assert moves._id_revomon_list(revomon_data) == [1, 2]


def test_normalize_move() -> None:
    move = {
        "level": 10,
        "method": "levelup",
        "category": "PHYSICAL",
        "name": "TACKLE",
        "type": "NORMAL",
        "description": "A physical attack in which the user charges and slams into the target with its whole body.",
    }
    normalized = moves._normalize_move(move)
    assert "level" not in normalized
    assert "method" not in normalized
    assert normalized["category"] == "physical"
    assert normalized["name"] == "tackle"
    assert normalized["type"] == "normal"
    assert "physical attack" in normalized["description"].lower()


def test_moves_from_movepools() -> None:
    movepools = {
        "1": [
            {"idMove": 1, "name": "tackle"},
            {"idMove": 2, "name": "growl"},
        ],
        "2": [
            {"idMove": 1, "name": "tackle"},
            {"idMove": 3, "name": "scratch"},
        ],
        "3": None,
        "4": [],
    }
    moves_list = moves._moves_from_movepools(movepools)
    assert len(moves_list) == 3
    assert moves_list[0]["idMove"] == 1
    assert moves_list[1]["idMove"] == 2
    assert moves_list[2]["idMove"] == 3


def test_load_movepools_cache(tmp_path: Any, monkeypatch: Any) -> None:
    file_path = tmp_path / "movepools.json"
    monkeypatch.setattr(moves, "GRADEX_MOVEPOOLS_FILE", file_path)

    # Empty
    assert moves._load_movepools_cache() == {}

    # Valid
    file_path.write_text(
        '{"1": [], "invalid": [], "2": null, "3": "not_list"}', encoding="utf-8"
    )
    assert moves._load_movepools_cache() == {"1": [], "2": None}


def test_save_movepools_cache(tmp_path: Any, monkeypatch: Any) -> None:
    file_path = tmp_path / "movepools.json"
    monkeypatch.setattr(moves, "GRADEX_MOVEPOOLS_FILE", file_path)

    movepools: list[Any] = {"2": [], "1": None}  # type: ignore[assignment]
    moves._save_movepools_cache(movepools)  # type: ignore[arg-type]
    saved = json.loads(file_path.read_text(encoding="utf-8"))
    assert list(saved.keys()) == ["1", "2"]


@pytest.mark.asyncio
async def test_fetch_moves_for_revomon() -> None:
    pacer = moves.RequestPacer(0.0)

    # Success
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get.return_value = httpx.Response(
        200,
        json={"data": {"moves": [{"idMove": 1}]}},
        request=httpx.Request("GET", "http://test"),
    )
    result = await moves.fetch_moves_for_revomon(client, pacer, 1)
    assert result.status == "found"
    assert result.moves == [{"idMove": 1}]

    # 200 Not Found (error in payload)
    client.get.return_value = httpx.Response(
        200, json={"error": "not found"}, request=httpx.Request("GET", "http://test")
    )
    result = await moves.fetch_moves_for_revomon(client, pacer, 1)
    assert result.status == "not_found"

    # 404
    client.get.return_value = httpx.Response(
        404, request=httpx.Request("GET", "http://test")
    )
    result = await moves.fetch_moves_for_revomon(client, pacer, 1)
    assert result.status == "not_found"

    # 429 then 200
    client.get.side_effect = [
        httpx.Response(
            429,
            request=httpx.Request("GET", "http://test"),
            headers={"Retry-After": "0.01"},
        ),
        httpx.Response(
            200,
            json={"data": {"moves": [{"idMove": 1}]}},
            request=httpx.Request("GET", "http://test"),
        ),
    ]
    result = await moves.fetch_moves_for_revomon(client, pacer, 1, max_attempts=2)
    assert result.status == "found"
    assert result.moves == [{"idMove": 1}]

    # 500 then 200
    client.get.side_effect = [
        httpx.Response(500, request=httpx.Request("GET", "http://test")),
        httpx.Response(
            200,
            json={"data": {"moves": [{"idMove": 1}]}},
            request=httpx.Request("GET", "http://test"),
        ),
    ]
    result = await moves.fetch_moves_for_revomon(client, pacer, 1, max_attempts=2)
    assert result.status == "found"

    # HTTPError
    client.get.side_effect = httpx.HTTPError("test")
    result = await moves.fetch_moves_for_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "error"

    # Invalid JSON
    client.get.side_effect = [
        httpx.Response(
            200, text="not_json", request=httpx.Request("GET", "http://test")
        ),
    ]
    result = await moves.fetch_moves_for_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "error"

    # 403 (unhandled)
    client.get.side_effect = [
        httpx.Response(403, request=httpx.Request("GET", "http://test")),
    ]
    result = await moves.fetch_moves_for_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_fetch_missing_movepools(monkeypatch: Any) -> None:
    monkeypatch.setattr(moves, "CLIENT_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(moves, "CONCURRENCY_LIMIT", 2)
    monkeypatch.setattr(moves, "REQUEST_INTERVAL_SECONDS", 0.0)

    movepools: dict[str, Any] = {}
    missing_ids = [1, 2, 3]

    async def mock_fetch(
        client: Any, pacer: Any, id_revomon: Any, max_attempts: Any = 1
    ) -> Any:
        if id_revomon == 1:
            return moves.MovesFetchResult(status="found", moves=[{"idMove": 1}])
        elif id_revomon == 2:
            return moves.MovesFetchResult(status="not_found")
        else:
            return moves.MovesFetchResult(status="error")

    monkeypatch.setattr(moves, "fetch_moves_for_revomon", mock_fetch)
    monkeypatch.setattr(moves, "_save_movepools_cache", lambda x: None)

    failed_ids = await moves._fetch_missing_movepools(movepools, missing_ids)
    assert failed_ids == [3]
    assert movepools["1"] == [{"idMove": 1}]
    assert movepools["2"] is None
    assert "3" not in movepools


@pytest.mark.asyncio
async def test_get_moves(monkeypatch: Any, tmp_path: Any) -> None:
    revomon_file = tmp_path / "revomon.json"
    movepools_file = tmp_path / "movepools.json"
    moves_file = tmp_path / "moves.json"

    monkeypatch.setattr(moves, "GRADEX_REVOMON_FILE", revomon_file)
    monkeypatch.setattr(moves, "GRADEX_MOVEPOOLS_FILE", movepools_file)
    monkeypatch.setattr(moves, "GRADEX_MOVES_FILE", moves_file)

    # 1. Neither revomon.json nor movepools.json exists
    assert await moves.get_moves() == []

    # 2. revomon.json doesn't exist, but movepools.json does
    movepools_file.write_text(
        '{"1": [{"idMove": 1, "name": "tackle"}]}', encoding="utf-8"
    )
    result = await moves.get_moves()
    assert len(result) == 1
    assert result[0]["idMove"] == 1

    # 3. revomon.json exists, missing_ids to fetch
    revomon_file.write_text(
        '[{"idRevomon": "1"}, {"idRevomon": "2"}]', encoding="utf-8"
    )
    movepools_file.write_text(
        '{"1": [{"idMove": 1, "name": "tackle"}]}', encoding="utf-8"
    )

    async def mock_fetch_missing(movepools: Any, missing_ids: Any) -> Any:
        assert missing_ids == [2]
        movepools["2"] = [{"idMove": 2, "name": "growl"}]
        return []

    monkeypatch.setattr(moves, "_fetch_missing_movepools", mock_fetch_missing)
    monkeypatch.setattr(moves, "REFRESH_MOVEPOOL_CACHE", False)

    result = await moves.get_moves(save_to_file=True)
    assert len(result) == 2
    assert result[0]["idMove"] == 1
    assert result[1]["idMove"] == 2
    assert moves_file.exists()

    # 4. failed_ids returned by fetch_missing
    async def mock_fetch_missing_failed(movepools: Any, missing_ids: Any) -> Any:
        return [2]

    monkeypatch.setattr(moves, "_fetch_missing_movepools", mock_fetch_missing_failed)
    assert await moves.get_moves() == []

    # 5. REFRESH_MOVEPOOL_CACHE = True
    async def mock_fetch_missing_refresh(movepools: Any, missing_ids: Any) -> Any:
        assert missing_ids == [1, 2]
        return []

    monkeypatch.setattr(moves, "REFRESH_MOVEPOOL_CACHE", True)
    monkeypatch.setattr(moves, "_fetch_missing_movepools", mock_fetch_missing_refresh)
    await moves.get_moves()

    # 6. No missing IDs
    movepools_file.write_text('{"1": [], "2": []}', encoding="utf-8")
    monkeypatch.setattr(moves, "REFRESH_MOVEPOOL_CACHE", False)
    assert await moves.get_moves() == []
