import unittest.mock
from typing import Any

"""Tests for scripts/natures.py"""

import asyncio  # noqa: E402
import runpy  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402

from scripts.natures import (  # noqa: E402
    NATURES_FILE,
    fetch_nature,
    get_natures,
    process_nature,
)


@pytest.fixture
def mock_client() -> Any:
    client = MagicMock(spec=httpx.AsyncClient)
    return client


@pytest.mark.asyncio
async def test_fetch_nature_success(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "adamant"}
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await fetch_nature(mock_client, "adamant")
    assert result == {"name": "adamant"}
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_nature_not_found(mock_client: Any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await fetch_nature(mock_client, "adamant")
    assert result is None
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_nature_http_error(mock_client: Any) -> None:
    mock_client.get = AsyncMock(side_effect=httpx.HTTPError("error"))

    result = await fetch_nature(mock_client, "adamant")
    assert result is None
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_nature_unexpected_error(mock_client: Any) -> None:
    mock_client.get = AsyncMock(side_effect=ValueError("unexpected"))

    result = await fetch_nature(mock_client, "adamant")
    assert result is None
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_process_nature_success(mock_client: Any) -> None:
    semaphore = asyncio.Semaphore(1)
    natures_list: list[dict[str, Any]] = []

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "increased_stat": {"name": "attack"},
        "decreased_stat": {"name": "special-attack"},
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    await process_nature(semaphore, mock_client, "adamant", natures_list)

    assert len(natures_list) == 1
    assert natures_list[0] == {
        "name": "adamant",
        "increased_stat": "atk",
        "decreased_stat": "spa",
    }


@pytest.mark.asyncio
async def test_process_nature_no_stats(mock_client: Any) -> None:
    semaphore = asyncio.Semaphore(1)
    natures_list: list[dict[str, Any]] = []

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"increased_stat": None, "decreased_stat": None}
    mock_client.get = AsyncMock(return_value=mock_response)

    await process_nature(semaphore, mock_client, "hardy", natures_list)

    assert len(natures_list) == 1
    assert natures_list[0] == {
        "name": "hardy",
        "increased_stat": None,
        "decreased_stat": None,
    }


@pytest.mark.asyncio
async def test_process_nature_fetch_failed(mock_client: Any) -> None:
    semaphore = asyncio.Semaphore(1)
    natures_list: list[dict[str, Any]] = []

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    await process_nature(semaphore, mock_client, "adamant", natures_list)

    assert len(natures_list) == 0


@pytest.mark.asyncio
@patch("scripts.natures.httpx.AsyncClient")
@patch("scripts.natures.json.dump")
@patch("scripts.natures.os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
async def test_get_natures_success(
    mock_open: Any,
    mock_makedirs: Any,
    mock_json_dump: Any,
    mock_async_client_class: Any,
) -> None:
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_async_client_class.return_value = mock_client_instance

    def mock_get(url: Any, **kwargs: Any) -> Any:
        mock_resp = MagicMock()
        if url == "https://pokeapi.co/api/v2/nature?limit=25":
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "results": [{"name": "adamant"}, {"name": "jolly"}]
            }
            mock_resp.raise_for_status = MagicMock()
            return mock_resp
        elif "nature/adamant" in url:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "increased_stat": {"name": "attack"},
                "decreased_stat": {"name": "special-attack"},
            }
            return mock_resp
        elif "nature/jolly" in url:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "increased_stat": {"name": "speed"},
                "decreased_stat": {"name": "special-attack"},
            }
            return mock_resp

    mock_client_instance.get = AsyncMock(side_effect=mock_get)

    await get_natures(save_to_file=True)

    mock_makedirs.assert_called_once_with(NATURES_FILE.parent, exist_ok=True)
    mock_open.assert_called_once_with(NATURES_FILE, "w", encoding="utf-8")

    assert mock_json_dump.call_count == 1
    args, kwargs = mock_json_dump.call_args
    data = args[0]

    assert data["1"]["name"] == "adamant"
    assert data["1"]["idNature"] == 1
    assert data["2"]["name"] == "jolly"
    assert data["2"]["idNature"] == 2


@pytest.mark.asyncio
@patch("scripts.natures.httpx.AsyncClient")
async def test_get_natures_success_no_save(mock_async_client_class: Any) -> None:
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_async_client_class.return_value = mock_client_instance

    def mock_get(url: Any, **kwargs: Any) -> Any:
        mock_resp = MagicMock()
        if url == "https://pokeapi.co/api/v2/nature?limit=25":
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"results": [{"name": "adamant"}]}
            mock_resp.raise_for_status = MagicMock()
            return mock_resp
        elif "nature/adamant" in url:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "increased_stat": {"name": "attack"},
                "decreased_stat": {"name": "special-attack"},
            }
            return mock_resp

    mock_client_instance.get = AsyncMock(side_effect=mock_get)

    await get_natures(save_to_file=False)


@pytest.mark.asyncio
@patch("scripts.natures.httpx.AsyncClient")
async def test_get_natures_list_error(mock_async_client_class: Any) -> None:
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_async_client_class.return_value = mock_client_instance

    mock_client_instance.get = AsyncMock(side_effect=httpx.HTTPError("list error"))

    await get_natures(save_to_file=False)


@patch("scripts.natures.logging.basicConfig")
def test_main_execution(mock_basic_config: Any) -> None:
    with (
        patch(
            "scripts.natures.asyncio.run", side_effect=lambda coro: coro.close()
        ) as mock_asyncio_run,
        patch("scripts.natures.get_natures"),
    ):
        with unittest.mock.patch.dict("sys.modules"):
            import sys

            sys.modules.pop("scripts.natures", None)

            runpy.run_module("scripts.natures", run_name="__main__")
        mock_basic_config.assert_called_once()
        mock_asyncio_run.assert_called_once()
