import asyncio
import json
import os
import runpy
import sys
import unittest.mock
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

sys.path.insert(0, os.path.abspath("scripts"))

from scripts.movepools import (
    _save_movepools_to_file,
    get_movepool,
    get_movepools,
    get_raw_movepool,
)


@pytest.fixture
def mock_client() -> Any:
    client = MagicMock(spec=httpx.AsyncClient)
    return client

@pytest.mark.asyncio
async def test_get_raw_movepool_success(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": None, "data": {"moves": []}}
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await get_raw_movepool(mock_client, 1)
    assert result == {"moves": []}

@pytest.mark.asyncio
async def test_get_raw_movepool_not_200(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await get_raw_movepool(mock_client, 1)
    assert result is None

@pytest.mark.asyncio
async def test_get_raw_movepool_missing_data(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": None}
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await get_raw_movepool(mock_client, 1)
    assert result is None

@pytest.mark.asyncio
async def test_get_raw_movepool_has_error(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": "Some error"}
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await get_raw_movepool(mock_client, 1)
    assert result is None

@pytest.mark.asyncio
async def test_get_raw_movepool_httperror(mock_client: Any) -> None:
    mock_client.get = AsyncMock(side_effect=httpx.HTTPError("error"))
    result = await get_raw_movepool(mock_client, 1)
    assert result is None

@pytest.mark.asyncio
async def test_get_raw_movepool_exception(mock_client: Any) -> None:
    mock_client.get = AsyncMock(side_effect=Exception("error"))
    result = await get_raw_movepool(mock_client, 1)
    assert result is None

@pytest.mark.asyncio
async def test_get_movepool_no_id() -> None:
    revomon: dict[str, Any] = {}
    movepool_data: dict[str, Any] = {}
    await get_movepool(asyncio.Semaphore(1), None, revomon, movepool_data)  # type: ignore[arg-type]
    assert movepool_data == {}

@pytest.mark.asyncio
@patch("scripts.movepools.get_raw_movepool")
@patch("scripts.movepools.to_sentence_case")
async def test_get_movepool_success(mock_to_sentence_case: Any, mock_get_raw: Any) -> None:
    mock_to_sentence_case.side_effect = lambda x: x.capitalize()
    mock_get_raw.return_value = {
        "moves": [
            {
                "idMove": 1,
                "category": "Physical",
                "name": "Tackle",
                "type": "Normal",
                "description": "a basic attack."
            },
            {
                "idMove": 2
            }
        ]
    }
    revomon = {"idRevomon": 1, "name": "Bulbasaur"}
    movepool_data: dict[str, Any] = {}

    await get_movepool(asyncio.Semaphore(1), None, revomon, movepool_data)  # type: ignore[arg-type]

    assert revomon["movepool"] == [1, 2]
    assert movepool_data[1][0]["category"] == "physical"  # type: ignore[index]
    assert movepool_data[1][0]["name"] == "tackle"  # type: ignore[index]
    assert movepool_data[1][0]["type"] == "normal"  # type: ignore[index]
    assert movepool_data[1][0]["description"] == "A basic attack."  # type: ignore[index]

@pytest.mark.asyncio
@patch("scripts.movepools.get_raw_movepool")
async def test_get_movepool_none(mock_get_raw: Any) -> None:
    mock_get_raw.return_value = None
    revomon = {"idRevomon": 1, "name": "Bulbasaur"}
    movepool_data: dict[str, Any] = {}

    await get_movepool(asyncio.Semaphore(1), None, revomon, movepool_data)  # type: ignore[arg-type]

    assert revomon["movepool"] == []
    assert movepool_data[1] is None  # type: ignore[index]

@pytest.mark.asyncio
@patch("scripts.movepools.get_raw_movepool")
async def test_get_movepool_empty_moves(mock_get_raw: Any) -> None:
    mock_get_raw.return_value = {}
    revomon = {"idRevomon": 1, "name": "Bulbasaur"}
    movepool_data: dict[str, Any] = {}

    await get_movepool(asyncio.Semaphore(1), None, revomon, movepool_data)  # type: ignore[arg-type]

    assert revomon["movepool"] == []

@pytest.mark.asyncio
async def test_get_movepools_file_not_found(tmp_path: Any) -> None:
    with patch("scripts.movepools.REVODEX_REVOMON_FILE", tmp_path / "not_found.json"):
        with pytest.raises(FileNotFoundError):
            await get_movepools()

@pytest.mark.asyncio
async def test_get_movepools_success(tmp_path: Any) -> None:
    # Set up files
    revomon_file = tmp_path / "revomon.json"
    revomon_data = [{"idRevomon": 1}, {"idRevomon": 2}]
    # Create enough tasks to trigger chunking logic (chunk_size=50)
    revomon_data.extend([{"idRevomon": i} for i in range(3, 55)])
    revomon_file.write_text(json.dumps(revomon_data))

    with patch("scripts.movepools.REVODEX_REVOMON_FILE", revomon_file), \
         patch("scripts.movepools.REVODEX_MOVEPOOLS_FILE", tmp_path / "movepools.json"), \
         patch("scripts.movepools.get_movepool") as mock_get_movepool:

        async def mock_get_pool(semaphore: Any, client: Any, revomon: Any, movepool_data: Any) -> None:
            movepool_data[revomon["idRevomon"]] = []
        mock_get_movepool.side_effect = mock_get_pool

        res = await get_movepools(save_to_file=True)
        assert len(res) == 54
        assert (tmp_path / "movepools.json").exists()

@pytest.mark.asyncio
async def test_get_movepools_success_no_save(tmp_path: Any) -> None:
    # Set up files
    revomon_file = tmp_path / "revomon.json"
    revomon_data = [{"idRevomon": 1}, {"idRevomon": 2}]
    revomon_file.write_text(json.dumps(revomon_data))

    with patch("scripts.movepools.REVODEX_REVOMON_FILE", revomon_file), \
         patch("scripts.movepools.REVODEX_MOVEPOOLS_FILE", tmp_path / "movepools.json"), \
         patch("scripts.movepools.get_movepool") as mock_get_movepool:

        async def mock_get_pool(semaphore: Any, client: Any, revomon: Any, movepool_data: Any) -> None:
            movepool_data[revomon["idRevomon"]] = []
        mock_get_movepool.side_effect = mock_get_pool

        res = await get_movepools(save_to_file=False)
        assert len(res) == 2
        assert not (tmp_path / "movepools.json").exists()

def test_save_movepools_to_file(tmp_path: Any) -> None:
    movepool_data: dict[str, Any] = {2: [], 1: []}  # type: ignore[dict-item]
    target_file = tmp_path / "movepools.json"
    with patch("scripts.movepools.REVODEX_MOVEPOOLS_FILE", target_file):
        _save_movepools_to_file(movepool_data, sort=True)
        assert target_file.exists()
        saved = json.loads(target_file.read_text())
        assert list(saved.keys()) == ["1", "2"] # json stringifies keys

def test_save_movepools_to_file_no_sort(tmp_path: Any) -> None:
    movepool_data: dict[str, Any] = {2: [], 1: []}  # type: ignore[dict-item]
    target_file = tmp_path / "movepools.json"
    with patch("scripts.movepools.REVODEX_MOVEPOOLS_FILE", target_file):
        _save_movepools_to_file(movepool_data, sort=False)
        assert target_file.exists()

def test_main() -> None:
    with patch("scripts.movepools.get_movepools"), \
         patch("asyncio.run", side_effect=lambda coro: coro.close()) as mock_run:
        with unittest.mock.patch.dict('sys.modules'):

            import sys

            sys.modules.pop('scripts.movepools', None)

            runpy.run_module('scripts.movepools', run_name='__main__')
        mock_run.assert_called_once()
