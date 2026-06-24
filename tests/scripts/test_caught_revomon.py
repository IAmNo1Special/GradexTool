import asyncio
import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest
from httpx import Request, Response

from scripts.caught_revomon import (
    CAUGHT_REVOMON_SCAN_STATE_FILE,
    REVODEX_CAUGHT_REVOMON_FILE,
    CaughtRevomonResult,
    RequestPacer,
    _advance_frontier,
    _build_state_dict,
    _env_float,
    _env_int,
    _found_name,
    _load_results,
    _load_scan_state,
    _process_batch,
    _recompute_frontier,
    _retry_after_seconds,
    _save_json,
    get_caught_revomon,
    get_caught_revomon_data,
    save_progress,
)


def test_env_int() -> None:
    assert _env_int("NON_EXISTENT_VAR", 42) == 42
    with patch.dict(os.environ, {"NON_EXISTENT_VAR": "10"}):
        assert _env_int("NON_EXISTENT_VAR", 42) == 10
    with patch.dict(os.environ, {"NON_EXISTENT_VAR": "abc"}):
        assert _env_int("NON_EXISTENT_VAR", 42) == 42

def test_env_float() -> None:
    assert _env_float("NON_EXISTENT_VAR_FLOAT", 42.0) == 42.0
    with patch.dict(os.environ, {"NON_EXISTENT_VAR_FLOAT": "10.5"}):
        assert _env_float("NON_EXISTENT_VAR_FLOAT", 42.0) == 10.5
    with patch.dict(os.environ, {"NON_EXISTENT_VAR_FLOAT": "abc"}):
        assert _env_float("NON_EXISTENT_VAR_FLOAT", 42.0) == 42.0

@pytest.mark.asyncio
async def test_request_pacer() -> None:
    pacer = RequestPacer(0.1)
    # wait_for_slot
    start = asyncio.get_running_loop().time()
    await pacer.wait_for_slot()
    await pacer.wait_for_slot()
    end = asyncio.get_running_loop().time()
    assert end - start >= 0.1

    # pause_all
    await pacer.pause_all(0.2)
    start = asyncio.get_running_loop().time()
    await pacer.wait_for_slot()
    end = asyncio.get_running_loop().time()
    assert end - start >= 0.15 # should wait around 0.2

def test_retry_after_seconds() -> None:
    # Headers missing
    req = Request("GET", "http://test")
    resp = Response(429, request=req)
    assert _retry_after_seconds(resp) is None

    # float parse
    resp = Response(429, headers={"Retry-After": "1.5"}, request=req)
    assert _retry_after_seconds(resp) == 1.5

    # negative float
    resp = Response(429, headers={"Retry-After": "-1.5"}, request=req)
    assert _retry_after_seconds(resp) == 0.0

    # date parse naive
    naive_date = "Wed, 21 Oct 2035 07:28:00"
    resp = Response(429, headers={"Retry-After": naive_date}, request=req)
    val = _retry_after_seconds(resp)
    assert val is not None

    # date parse
    future_date = "Wed, 21 Oct 2035 07:28:00 GMT"
    resp = Response(429, headers={"Retry-After": future_date}, request=req)
    val = _retry_after_seconds(resp)
    assert val is not None
    assert val > 0

    # invalid date
    resp = Response(429, headers={"Retry-After": "invalid_date"}, request=req)
    assert _retry_after_seconds(resp) is None

@pytest.mark.asyncio
async def test_get_caught_revomon_200_valid() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    resp = Response(200, json={"data": {"catchedRevomon": {"name": "TestMon"}}}, request=req)
    client.get = AsyncMock(return_value=resp)
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "found"
    assert result.data == {"name": "TestMon"}

@pytest.mark.asyncio
async def test_get_caught_revomon_200_invalid_payload() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    # error is present
    resp = Response(200, json={"error": "some_error", "data": {}}, request=req)
    client.get = AsyncMock(return_value=resp)
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "not_found"

    # data is not dict
    resp2 = Response(200, json={"data": []}, request=req)
    client.get = AsyncMock(return_value=resp2)
    result2 = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result2.status == "not_found"

@pytest.mark.asyncio
async def test_get_caught_revomon_404() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    client.get = AsyncMock(return_value=Response(404, request=req))
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "not_found"

@pytest.mark.asyncio
async def test_get_caught_revomon_429() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")

    resp_429 = Response(429, headers={"Retry-After": "0.1"}, request=req)
    resp_200 = Response(200, json={"data": {"catchedRevomon": {"name": "TestMon"}}}, request=req)

    client.get = AsyncMock(side_effect=[resp_429, resp_200])
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=2)
    assert result.status == "found"

@pytest.mark.asyncio
async def test_get_caught_revomon_500() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")

    resp_500 = Response(500, request=req)
    resp_200 = Response(200, json={"data": {"catchedRevomon": {"name": "TestMon"}}}, request=req)

    client.get = AsyncMock(side_effect=[resp_500, resp_200])
    pacer = RequestPacer(0.0)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await get_caught_revomon(client, pacer, 1, max_attempts=2)
        assert result.status == "found"
        mock_sleep.assert_called()

@pytest.mark.asyncio
async def test_get_caught_revomon_400() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    client.get = AsyncMock(return_value=Response(400, request=req))
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "not_found"

@pytest.mark.asyncio
async def test_get_caught_revomon_other_error() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    client.get = AsyncMock(return_value=Response(403, request=req))
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "error"

@pytest.mark.asyncio
async def test_get_caught_revomon_httperror() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=httpx.ReadTimeout("Timeout"))
    pacer = RequestPacer(0.0)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await get_caught_revomon(client, pacer, 1, max_attempts=2)
        assert result.status == "error"

@pytest.mark.asyncio
async def test_get_caught_revomon_json_error() -> None:
    client = MagicMock(spec=httpx.AsyncClient)
    req = Request("GET", "http://test")
    resp = Response(200, content=b"invalid json", request=req)
    client.get = AsyncMock(return_value=resp)
    pacer = RequestPacer(0.0)

    result = await get_caught_revomon(client, pacer, 1, max_attempts=1)
    assert result.status == "error"

def test_load_results_not_exists() -> None:
    with patch("pathlib.Path.exists", return_value=False):
        assert _load_results() == {}

def test_load_results_invalid_json() -> None:
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="invalid")):
        assert _load_results() == {}

def test_load_results_not_dict() -> None:
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="[]")):
        assert _load_results() == {}

def test_load_results_valid() -> None:
    data = '{"1": {"name": "A"}, "invalid": {}, "2": {"name": "B"}}'
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=data)):
        res = _load_results()
        assert res == {1: {"name": "A"}, 2: {"name": "B"}}

def test_load_scan_state_not_exists() -> None:
    with patch("pathlib.Path.exists", return_value=False):
        assert _load_scan_state(5)["next_id"] == 5

def test_load_scan_state_invalid_json() -> None:
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="invalid")):
        assert _load_scan_state(5)["next_id"] == 5

def test_load_scan_state_not_dict() -> None:
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="[]")):
        assert _load_scan_state(5)["next_id"] == 5

def test_load_scan_state_valid() -> None:
    data = '{"next_id": 10, "statuses": {"1": "found", "invalid": "found", "2": "unknown_status"}}'
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=data)):
        res = _load_scan_state(5)
        assert res["next_id"] == 10
        assert res["statuses"] == {"1": "found"}

def test_load_scan_state_invalid_next_id() -> None:
    data = '{"next_id": "abc", "statuses": {}}'
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=data)):
        res = _load_scan_state(5)
        assert res["next_id"] == 5

def test_load_scan_state_not_dict_statuses() -> None:
    data = '{"next_id": 10, "statuses": []}'
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=data)):
        res = _load_scan_state(5)
        assert res["statuses"] == {}

def test_save_json() -> None:
    with patch("pathlib.Path.mkdir"), \
         patch("builtins.open", mock_open()), \
         patch("pathlib.Path.replace") as mock_replace:
        p = Path("dummy.json")
        _save_json(p, {"a": 1})
        mock_replace.assert_called_once_with(p)

def test_save_progress() -> None:
    results = {2: {"name": "B"}, 1: {"name": "A"}}
    state = {
        "next_id": 2,
        "statuses": {"1": "found", "2": "not_found", "3": "error"}
    }
    with patch("scripts.caught_revomon._save_json") as mock_save:
        save_progress(results, state)
        assert mock_save.call_count == 2
        args1, _ = mock_save.call_args_list[0]
        args2, _ = mock_save.call_args_list[1]

        assert args1[0] == REVODEX_CAUGHT_REVOMON_FILE
        assert list(args1[1].keys()) == ["1", "2"] # sorted

        assert args2[0] == CAUGHT_REVOMON_SCAN_STATE_FILE
        saved_state = args2[1]
        assert "1" in saved_state["statuses"]
        assert "2" in saved_state["statuses"] # since >= next_id
        assert "3" in saved_state["statuses"]

def test_advance_frontier() -> None:
    assert _advance_frontier(10, "found", 5, 2) == (10, 0)
    assert _advance_frontier(10, "not_found", 5, 2) == (5, 3)
    assert _advance_frontier(10, "error", 5, 2) == (5, 2)

def test_recompute_frontier() -> None:
    statuses = {"1": "found", "2": "not_found", "3": "error", "4": "found", "5": "not_found"}
    # start=1, next=6
    last_found, missing = _recompute_frontier(statuses, 1, 6)
    assert last_found == 4
    assert missing == 1

def test_build_state_dict() -> None:
    d = _build_state_dict(1, 10, 5, 6, 4, 1, {"1": "found"}, stop_reason="max_id")
    assert d["start_id"] == 1
    assert d["stop_reason"] == "max_id"

def test_found_name() -> None:
    assert _found_name(None) == "Unknown"
    assert _found_name([]) == "Unknown"  # type: ignore[arg-type]
    assert _found_name({"name": "Pika"}) == "Pika"
    assert _found_name({}) == "Unknown"

@pytest.mark.asyncio
async def test_process_batch() -> None:
    client = MagicMock()
    pacer = RequestPacer(0.0)

    async def mock_get(client: Any, pacer: Any, id_catched: Any, max_attempts: Any=8) -> Any:
        return CaughtRevomonResult(status="found" if id_catched == 1 else "not_found")

    with patch("scripts.caught_revomon.get_caught_revomon", side_effect=mock_get):
        res = await _process_batch(client, pacer, [1, 2])
        assert len(res) == 2
        assert res[0].status == "found"
        assert res[1].status == "not_found"

@pytest.mark.asyncio
async def test_get_caught_revomon_data_max_id() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 1, "statuses": {}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress") as mock_save:

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        results = await get_caught_revomon_data(max_id=1, empty_tail_limit=10)
        assert results == {}
        assert mock_save.call_count >= 1

@pytest.mark.asyncio
async def test_get_caught_revomon_data_empty_tail() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={1: {"name": "A"}}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 2, "statuses": {"1": "found"}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        results = await get_caught_revomon_data(max_id=10, empty_tail_limit=1)
        assert results == {1: {"name": "A"}}

@pytest.mark.asyncio
async def test_get_caught_revomon_data_error_pause() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 1, "statuses": {}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("error")] * len(ids)
        results = await get_caught_revomon_data(max_id=1, empty_tail_limit=10)
        assert results == {}

@pytest.mark.asyncio
async def test_get_caught_revomon_data_found() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 1, "statuses": {}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        def mock_side_effect(c: Any, p: Any, ids: Any) -> Any:
            return [CaughtRevomonResult("found", {"name": "Test"}) if i == 1 else CaughtRevomonResult("not_found") for i in ids]

        mock_batch.side_effect = mock_side_effect
        results = await get_caught_revomon_data(max_id=2, empty_tail_limit=10)
        assert len(results) == 1
        assert results[1] == {"name": "Test"}

@pytest.mark.asyncio
async def test_get_caught_revomon_data_existing_status() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={1: {"name": "A"}}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 1, "statuses": {"1": "found", "2": "not_found"}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("found", {"name": "B"}) if i == 3 else CaughtRevomonResult("not_found") for i in ids]
        results = await get_caught_revomon_data(max_id=3, empty_tail_limit=10)
        assert results == {1: {"name": "A"}, 3: {"name": "B"}}

@pytest.mark.asyncio
async def test_get_caught_revomon_data_checkpoint() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 1, "statuses": {}}), \
         patch("scripts.caught_revomon.CHECKPOINT_INTERVAL", 1), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress") as mock_save:

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        await get_caught_revomon_data(max_id=1, empty_tail_limit=10)
        assert mock_save.call_count >= 1

@pytest.mark.asyncio
async def test_get_caught_revomon_data_recompute_frontier() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={1: {"name": "A"}}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 3, "statuses": {"1": "found", "2": "not_found"}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        await get_caught_revomon_data(max_id=3, empty_tail_limit=10)

@pytest.mark.asyncio
async def test_get_caught_revomon_data_recompute_frontier_mismatch() -> None:
    state = {
        "version": 1,
        "next_id": 3,
        "statuses": {"1": "found", "2": "not_found"},
        "last_found_id": 1,
        "consecutive_missing_after_last_found": 1
    }
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value=state), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        await get_caught_revomon_data(max_id=3, empty_tail_limit=10)

@pytest.mark.asyncio
async def test_get_caught_revomon_data_batch_break() -> None:
    state = {
        "version": 1,
        "next_id": 1,
        "statuses": {"2": "found"},
    }
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value=state), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        await get_caught_revomon_data(max_id=2, empty_tail_limit=10)

@pytest.mark.asyncio
async def test_get_caught_revomon_data_100() -> None:
    with patch("scripts.caught_revomon._load_results", return_value={}), \
         patch("scripts.caught_revomon._load_scan_state", return_value={"version": 1, "next_id": 100, "statuses": {}}), \
         patch("scripts.caught_revomon._process_batch", new_callable=AsyncMock) as mock_batch, \
         patch("scripts.caught_revomon.save_progress"):

        mock_batch.side_effect = lambda c, p, ids: [CaughtRevomonResult("not_found")] * len(ids)
        await get_caught_revomon_data(start_id=100, max_id=100, empty_tail_limit=10)

def test_main_execution() -> None:
    with patch("asyncio.run", side_effect=lambda coro: coro.close()) as mock_run:
        import runpy
        import sys
        with patch.dict('sys.modules'):
            sys.modules.pop('scripts.caught_revomon', None)
            try:
                runpy.run_module("scripts.caught_revomon", run_name="__main__", alter_sys=True)
            except Exception:
                pass
        mock_run.assert_called_once()
