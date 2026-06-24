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

from scripts.base_types import (
    download_base_type_images,
    get_base_types,
    save_base_types_file,
)


def test_save_base_types_file(tmp_path: Any) -> None:
    test_file = tmp_path / "types.json"
    with patch("scripts.base_types.BASE_TYPES_FILE", test_file):
        save_base_types_file(["fire", "water"])
        assert test_file.exists()
        with open(test_file) as f:
            assert json.load(f) == ["fire", "water"]

@pytest.mark.asyncio
async def test_download_base_type_images_success(tmp_path: Any) -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"image data"
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("scripts.base_types.BASE_TYPES_IMAGES_DIR", tmp_path):
        res = await download_base_type_images(mock_client, "fire")
        assert res is True
        assert (tmp_path / "fire.png").exists()
        assert (tmp_path / "fire.png").read_bytes() == b"image data"

@pytest.mark.asyncio
async def test_download_base_type_images_not_200(tmp_path: Any) -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("scripts.base_types.BASE_TYPES_IMAGES_DIR", tmp_path):
        res = await download_base_type_images(mock_client, "fire")
        assert res is False

@pytest.mark.asyncio
async def test_download_base_type_images_http_error(tmp_path: Any) -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(side_effect=httpx.HTTPError("error"))

    with patch("scripts.base_types.BASE_TYPES_IMAGES_DIR", tmp_path):
        res = await download_base_type_images(mock_client, "fire")
        assert res is False

@pytest.mark.asyncio
async def test_download_base_type_images_exception(tmp_path: Any) -> None:
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(side_effect=Exception("error"))

    with patch("scripts.base_types.BASE_TYPES_IMAGES_DIR", tmp_path):
        res = await download_base_type_images(mock_client, "fire")
        assert res is False

@pytest.mark.asyncio
async def test_get_base_types(tmp_path: Any) -> None:
    revomon_file = tmp_path / "revomon.json"
    revomon_file.write_text('[{"type1": "Fire", "type2": null}, {"type1": "Water", "type2": "Flying"}]')

    with patch("scripts.base_types.REVOMON_FILE", revomon_file), \
         patch("scripts.base_types.save_base_types_file") as mock_save, \
         patch("scripts.base_types.download_base_type_images") as mock_download:
        mock_download.return_value = True

        res = await get_base_types(save_to_file=True, download_images=True)
        assert res == ["fire", "flying", "water"]
        mock_save.assert_called_with(res)
        assert mock_download.call_count == 3

@pytest.mark.asyncio
async def test_get_base_types_no_save_no_download(tmp_path: Any) -> None:
    revomon_file = tmp_path / "revomon.json"
    revomon_file.write_text('[{"type1": "Fire", "type2": null}]')

    with patch("scripts.base_types.REVOMON_FILE", revomon_file), \
         patch("scripts.base_types.save_base_types_file") as mock_save, \
         patch("scripts.base_types.download_base_type_images") as mock_download:
        res = await get_base_types(save_to_file=False, download_images=False)
        assert res == ["fire"]
        mock_save.assert_not_called()
        mock_download.assert_not_called()

def test_main() -> None:
    with patch("scripts.base_types.get_base_types"), \
         patch("asyncio.run", side_effect=lambda coro: coro.close()) as mock_run:
        with unittest.mock.patch.dict('sys.modules'):

            import sys

            sys.modules.pop('scripts.base_types', None)

            runpy.run_module('scripts.base_types', run_name='__main__')
        mock_run.assert_called_once()
