import sys
from pathlib import Path
from typing import Any

# Fix sys.path for importing nested local modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta
from email.utils import formatdate
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

respx = pytest.importorskip("respx")
from httpx import Response  # noqa: E402

from scripts.revomon import (  # noqa: E402
    ImageDownloadResult,
    RequestPacer,
    RevomonTable,
    _build_image_variants,
    _download_image,
    _download_revomon_images,
    _env_float,
    _env_int,
    _is_downloaded,
    _load_download_manifest,
    _process_revomon_images,
    _record_manifest_results,
    _retry_after_seconds,
    _save_download_manifest,
    _status_label,
    get_revomon_data,
)


@pytest.fixture
def mock_db_path(tmp_path: Any) -> Any:
    db_file = tmp_path / "test_db.sqlite"
    return db_file


def test_env_int() -> None:
    with patch.dict(os.environ, {"TEST_INT_VALID": "42", "TEST_INT_INVALID": "abc"}):
        assert _env_int("TEST_INT_VALID", 10) == 42
        assert _env_int("TEST_INT_MISSING", 10) == 10
        assert _env_int("TEST_INT_INVALID", 10) == 10


def test_env_float() -> None:
    with patch.dict(os.environ, {"TEST_FLOAT_VALID": "3.14", "TEST_FLOAT_INVALID": "abc"}):
        assert _env_float("TEST_FLOAT_VALID", 1.5) == 3.14
        assert _env_float("TEST_FLOAT_MISSING", 1.5) == 1.5
        assert _env_float("TEST_FLOAT_INVALID", 1.5) == 1.5


@pytest.mark.asyncio
async def test_request_pacer() -> None:
    pacer = RequestPacer(0.1)
    await pacer.wait_for_slot()
    await pacer.wait_for_slot()

    await pacer.pause_all(0.2)
    start_time = asyncio.get_running_loop().time()
    await pacer.wait_for_slot()
    end_time = asyncio.get_running_loop().time()
    assert end_time - start_time >= 0.1


def test_retry_after_seconds() -> None:
    resp1 = Response(429)
    assert _retry_after_seconds(resp1) is None

    resp2 = Response(429, headers={"Retry-After": "5"})
    assert _retry_after_seconds(resp2) == 5.0

    resp_neg = Response(429, headers={"Retry-After": "-2"})
    assert _retry_after_seconds(resp_neg) == 0.0

    future_date = datetime.now(UTC) + timedelta(seconds=10)
    http_date = formatdate(future_date.timestamp(), usegmt=True)
    resp3 = Response(429, headers={"Retry-After": http_date})
    val = _retry_after_seconds(resp3)
    assert val is not None
    assert 9 <= val <= 11

    resp4 = Response(429, headers={"Retry-After": "invalid-date"})
    assert _retry_after_seconds(resp4) is None

    past_date = datetime.now(UTC) - timedelta(seconds=10)
    http_date_past = formatdate(past_date.timestamp(), usegmt=True)
    resp5 = Response(429, headers={"Retry-After": http_date_past})
    assert _retry_after_seconds(resp5) == 0.0

    class MockOverflowDate:
        def __init__(self, val: Any) -> None:
            self.val = val
        def __str__(self) -> Any:
            return str(self.val)

    with patch("scripts.revomon.parsedate_to_datetime", side_effect=OverflowError):
        resp6 = Response(429, headers={"Retry-After": "valid-but-overflows"})
        assert _retry_after_seconds(resp6) is None

    with patch("scripts.revomon.parsedate_to_datetime", return_value=datetime.now(UTC).replace(tzinfo=None)):
        resp7 = Response(429, headers={"Retry-After": "tz-naive"})
        val = _retry_after_seconds(resp7)
        assert val is not None


def test_is_downloaded(tmp_path: Any) -> None:
    f = tmp_path / "test.png"
    assert not _is_downloaded(f)
    f.touch()
    assert not _is_downloaded(f)
    f.write_text("data")
    assert _is_downloaded(f)


def test_load_download_manifest(tmp_path: Any) -> None:
    manifest_file = tmp_path / "manifest.json"
    with patch("scripts.revomon.REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE", manifest_file):
        assert _load_download_manifest() == {}

        manifest_file.write_text("invalid json")
        assert _load_download_manifest() == {}

        manifest_file.write_text('["list"]')
        assert _load_download_manifest() == {}

        manifest_file.write_text('{"1": {"raw_normal": "downloaded"}}')
        assert _load_download_manifest() == {"1": {"raw_normal": "downloaded"}}

    # trigger OSError
    with patch("scripts.revomon.REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE", manifest_file):
        with patch("builtins.open", side_effect=OSError):
            assert _load_download_manifest() == {}


def test_save_download_manifest(tmp_path: Any) -> None:
    manifest_file = tmp_path / "manifest.json"
    with patch("scripts.revomon.REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE", manifest_file):
        _save_download_manifest({"1": {"raw_normal": "downloaded"}})
        assert manifest_file.exists()
        data = json.loads(manifest_file.read_text())
        assert data == {"1": {"raw_normal": "downloaded"}}


def test_record_manifest_results() -> None:
    manifest: dict[str, dict[str, str]] = {}
    changed = _record_manifest_results(manifest, 1, {"raw_normal": "downloaded"})
    assert changed is True
    assert manifest == {"1": {"raw_normal": "downloaded"}}

    changed = _record_manifest_results(manifest, 1, {"raw_normal": "downloaded"})
    assert changed is False


def test_status_label() -> None:
    assert _status_label(ImageDownloadResult(True, "downloaded")) == "OK"
    assert _status_label(ImageDownloadResult(True, "exists")) == "SKIP"
    assert _status_label(ImageDownloadResult(False, "not_found")) == "MISS"
    assert _status_label(ImageDownloadResult(False, "rate_limited")) == "FAIL"
    assert _status_label(ImageDownloadResult(False, "unknown_status")) == "FAIL"


@pytest.mark.asyncio
async def test_download_image(tmp_path: Any) -> None:
    print("\n--- ENTERING test_download_image ---", flush=True)
    save_path = tmp_path / "img.png"
    pacer = RequestPacer(0)

    print("Checking exists check...", flush=True)
    save_path.write_text("data")
    async with httpx.AsyncClient() as client:
        res = await _download_image(client, pacer, "http://example.com", save_path)
    print("Exists check done.", flush=True)
    assert res.success is True
    assert res.status == "exists"

    save_path.unlink()

    async def mock_get(self: Any, url: Any, *args: Any, **kwargs: Any) -> Any:
        print(f"--- MOCK_GET CALLED with URL: {url} ---", flush=True)
        if "test/success" in url or "test/success2" in url:
            return httpx.Response(200, content=b"img", request=httpx.Request("GET", url))
        elif "test/notfound" in url:
            return httpx.Response(404, request=httpx.Request("GET", url))
        elif "test/429" in url:
            return httpx.Response(429, headers={"Retry-After": "0"}, request=httpx.Request("GET", url))
        elif "test/500" in url:
            return httpx.Response(500, request=httpx.Request("GET", url))
        elif "test/403" in url:
            return httpx.Response(403, request=httpx.Request("GET", url))
        elif "test/err" in url:
            raise httpx.ConnectError("test")
        raise ValueError(f"Unhandled mock URL: {url}")


    with patch("httpx.AsyncClient.get", new=mock_get):
        print("Calling success download...", flush=True)
        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/success", save_path)
        print("Success download done.", flush=True)
        assert res.success is True
        assert res.status == "downloaded"
        assert save_path.read_text() == "img"
        save_path.unlink()

        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/notfound", save_path)
        assert res.success is False
        assert res.status == "not_found"

        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/429", save_path, max_attempts=2)
        assert res.success is False
        assert res.status == "rate_limited"

        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/500", save_path, max_attempts=2)
        assert res.success is False
        assert res.status == "failed"

        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/403", save_path, max_attempts=2)
        assert res.success is False
        assert res.status == "failed"

        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/err", save_path, max_attempts=2)
        assert res.success is False
        assert res.status == "failed"

        save_path.mkdir()
        async with httpx.AsyncClient() as client:
            res = await _download_image(client, pacer, "http://test/success2", save_path)
        assert res.success is False
        assert res.status == "failed"
        save_path.rmdir()




def test_build_image_variants(tmp_path: Any) -> None:
    with patch("scripts.revomon.REVOMON_RAW_IMAGES_DIR", tmp_path / "raw"):
        with patch("scripts.revomon.REVOMON_NFT_IMAGES_DIR", tmp_path / "nft"):
            with patch("scripts.revomon.REVOMON_RAW_IMAGE_ENDPOINT", "http://raw"):
                with patch("scripts.revomon.REVOMON_NFT_IMAGE_ENDPOINT", "http://nft"):
                    variants = _build_image_variants(1)
                    assert "raw_normal" in variants
                    assert variants["raw_normal"]["url"] == "http://raw/1.png"
                    assert "nft_shiny" in variants
                    assert variants["nft_shiny"]["url"] == "http://nft/1_shiny.png"


@pytest.mark.asyncio
async def test_process_revomon_images(tmp_path: Any) -> None:
    semaphore = asyncio.Semaphore(1)
    pacer = RequestPacer(0)
    manifest_lock = asyncio.Lock()
    manifest: dict[str, dict[str, str]] = {}
    results: dict[int, dict[str, bool]] = {}

    revomon_data = {"idRevodex": 1, "name": "TestMon"}

    async with httpx.AsyncClient() as client:
        await _process_revomon_images(semaphore, client, pacer, {}, results, manifest, manifest_lock)
        assert results == {}

        with patch("scripts.revomon._build_image_variants") as mock_build:
            img_path = tmp_path / "img.png"
            mock_build.return_value = {
                "raw_normal": {"url": "http://test/1.png", "path": img_path}
            }

            with patch("scripts.revomon._download_image", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = ImageDownloadResult(success=True, status="downloaded")

                with patch("scripts.revomon.REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE", tmp_path / "manifest.json"):
                    await _process_revomon_images(semaphore, client, pacer, revomon_data, results, manifest, manifest_lock)

                    assert 1 in results
                    assert results[1]["raw_normal"] is True
                    assert manifest["1"]["raw_normal"] == "downloaded"

                    manifest["1"]["raw_normal"] = "not_found"
                    await _process_revomon_images(semaphore, client, pacer, revomon_data, results, manifest, manifest_lock)
                    assert results[1]["raw_normal"] is False

                    img_path.write_text("data")
                    await _process_revomon_images(semaphore, client, pacer, revomon_data, results, manifest, manifest_lock)
                    assert results[1]["raw_normal"] is True

                    mock_build.return_value = {"raw_normal": {"url": "http://test/1.png", "path": "not a path"}}
                    with pytest.raises(TypeError):
                        await _process_revomon_images(semaphore, client, pacer, revomon_data, results, manifest, manifest_lock)

                    mock_build.return_value = {"raw_normal": {"url": None, "path": img_path}}
                    img_path.unlink()
                    manifest["1"]["raw_normal"] = "something"
                    with pytest.raises(TypeError):
                        await _process_revomon_images(semaphore, client, pacer, revomon_data, results, manifest, manifest_lock)


@pytest.mark.asyncio
async def test_download_revomon_images(tmp_path: Any) -> None:
    with patch("scripts.revomon._load_download_manifest", return_value={}):
        with patch("scripts.revomon._save_download_manifest"):
            with patch("scripts.revomon._process_revomon_images", new_callable=AsyncMock) as mock_proc:
                results = await _download_revomon_images([{"idRevodex": 1}])
                assert mock_proc.call_count == 1
                assert results == {}


@pytest.mark.asyncio
async def test_get_revomon_data(tmp_path: Any) -> None:
    data_file = tmp_path / "revomon.json"

    with patch("scripts.revomon.REVOMON_FILE", data_file):
        with respx.mock:
            respx.post("https://api.revomon.io/revomon/revodex").respond(
                200, json={
                    "data": {
                        "revomons": [
                            {"idRevodex": 2, "name": "B", "isOwned": True, "description": "hello WORLD", "abilityHidden": "HIDDEN", "ability2": "AB2", "rarity": "rare", "type2": "water"},
                            {"idRevodex": 1, "name": "A", "type1": "fire", "ability1": "BLA", "evolution": "test", "description": 123}
                        ]
                    }
                }
            )

            with patch("scripts.revomon._download_revomon_images", new_callable=AsyncMock) as mock_down:
                res = await get_revomon_data(download_images=True)
                assert res is not None
                assert len(res) == 2
                assert res[0]["idRevodex"] == 1
                assert res[0]["name"] == "a"
                assert "isOwned" not in res[0]
                assert res[1]["idRevodex"] == 2
                assert res[1]["description"] == "Hello WORLD"
                mock_down.assert_called_once()

            respx.post("https://api.revomon.io/revomon/revodex").respond(
                200, json={"error": "some error"}
            )
            assert await get_revomon_data() is None

            respx.post("https://api.revomon.io/revomon/revodex").respond(404)
            assert await get_revomon_data() is None

            respx.post("https://api.revomon.io/revomon/revodex").mock(side_effect=httpx.ConnectError("test"))
            assert await get_revomon_data() is None

            respx.post("https://api.revomon.io/revomon/revodex").mock(side_effect=Exception("test"))
            assert await get_revomon_data() is None


@pytest.mark.asyncio
async def test_revomon_table_create(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path

    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value = MagicMock()
        table.create()
        mock_conn.assert_called_once_with(mock_db_path)


@pytest.mark.asyncio
async def test_revomon_table_rebuild(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "revomons": [
                    {
                        "idRevodex": 1, "idRevomon": 1, "name": "testmon", "description": "desc",
                        "rarity": "common", "ability1": "ab1", "ability2": None, "abilityHidden": None,
                        "evolution": "", "levelEvolution": 0, "type1": "fire", "type2": "water",
                        "hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1,
                        "evhp": 1, "evatk": 1, "evdef": 1, "evspa": 1, "evspd": 1, "evspe": 1
                    },
                    {
                        "idRevodex": 2, "idRevomon": 2, "name": "test-mon", "description": "desc",
                        "rarity": "rare", "ability1": "ab1", "ability2": "ab2", "abilityHidden": "abh",
                        "evolution": "test2", "levelEvolution": 5, "type1": "fire", "type2": None,
                        "hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1,
                        "evhp": 1, "evatk": 1, "evdef": 1, "evspa": 1, "evspd": 1, "evspe": 1
                    },
                    {
                        "idRevodex": 3, "idRevomon": 3, "name": "legend", "description": "desc",
                        "rarity": "legendary", "ability1": "ab1", "ability2": None, "abilityHidden": None,
                        "evolution": "", "levelEvolution": 0, "type1": "fire", "type2": None,
                        "hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1,
                        "evhp": 1, "evatk": 1, "evdef": 1, "evspa": 1, "evspd": 1, "evspe": 1
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        mock_emoji_utils = MagicMock()
        mock_emoji_utils.create_emoji_from_url = AsyncMock(return_value={"id": "<emoji1>"})
        mock_emoji_utils.list_application_emojis = AsyncMock(return_value=[
            {"name": "test_mon", "id": "<cached_test_mon>"},
            {"name": "test_mon_shiny", "id": "<cached_test_mon_shiny>"}
        ])

        mock_revomon_utils = MagicMock()
        mock_revomon_utils.get_evo_trees.return_value = ["testmon", "test-mon", "legend"]

        with patch.dict('sys.modules', {
            'utils.emoji_utils': mock_emoji_utils,
            'utils.revomon_utils': mock_revomon_utils
        }):
            with patch("builtins.open", mock_open(read_data='[{"name": "testmon", "dex_id": 1, "spawn_loc1": "loc1", "spawn_time1": "time1", "spawn_loc2": "loc2", "spawn_time2": "time2", "spawn_loc3": "loc3", "spawn_time3": "time3", "rarity": "common"}, {"name": "test-mon", "dex_id": 2, "spawn_loc1": null, "spawn_time1": null, "spawn_loc2": null, "spawn_time2": null, "spawn_loc3": null, "spawn_time3": null, "rarity": "rare"}, {"name": "legend", "dex_id": 3, "spawn_loc1": null, "spawn_time1": null, "spawn_loc2": null, "spawn_time2": null, "spawn_loc3": null, "spawn_time3": null, "rarity": "legendary"}]')):
                with patch("scripts.revomon.RevomonTable.export_to_json"):
                    class MockTypesTable:
                        def get_info(self, t1: Any, t2: Any) -> Any:
                            if t1 == "fire" and t2 == "water":
                                return [["test", "test_img"]]
                            return []
                    with patch("sqlite3.connect") as mock_conn:
                        with patch.dict('sys.modules', {}):
                            import builtins
                            original_table = getattr(builtins, "TypesTable", None)
                            setattr(builtins, "TypesTable", MockTypesTable)
                            try:
                                await table.rebuild()
                            except Exception as e:
                                import traceback
                                traceback.print_exc()
                                raise e
                            finally:
                                if original_table is not None:
                                    setattr(builtins, "TypesTable", original_table)
                                else:
                                    delattr(builtins, "TypesTable")

                        assert mock_conn.return_value.cursor.return_value.execute.called


@pytest.mark.asyncio
async def test_revomon_table_build(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.create = MagicMock()  # type: ignore[method-assign]
    table.rebuild = AsyncMock()  # type: ignore[method-assign]
    table.count_entries = MagicMock()  # type: ignore[method-assign]
    table.export_to_json = MagicMock()  # type: ignore[method-assign]

    await table.build()

    table.create.assert_called_once()
    table.rebuild.assert_called_once()
    table.count_entries.assert_called_once()
    table.export_to_json.assert_called_once()


@pytest.mark.asyncio
async def test_revomon_table_export_to_json(mock_db_path: Any, tmp_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path

    with patch("sqlite3.connect") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [("a", "b")]
        mock_cursor.description = [("col1",), ("col2",)]
        with patch("builtins.open", mock_open()) as mocked_file:
            table.export_to_json()
            assert mocked_file.call_count == 1


@pytest.mark.asyncio
async def test_revomon_table_count_entries(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = [42]

        assert table.count_entries() == 42


@pytest.mark.asyncio
async def test_revomon_table_add_revomon(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path

    with patch("sqlite3.connect") as mock_conn:
        table.add_revomon(
            1, 1, "test", "desc", "common", "ab1", "ab2", "abh", "evo", 0, "et", "t1", "t1i", "t2", "t2i", None,
            1, 1, 1, 1, 1, 1, 6, 1, 1, 1, 1, 1, 1, "img", "img_shiny", "nft", "nft_shiny", "em", "ems",
            "loc1", "t1", None, None, None, None
        )
        assert mock_conn.return_value.cursor.return_value.execute.called


@pytest.mark.asyncio
async def test_revomon_table_get_mon_ids(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchall.return_value = [(10,)]
        assert table.get_mon_ids() == [10]


@pytest.mark.asyncio
async def test_revomon_table_get_names(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchall.return_value = [("TEST",)]
        assert table.get_names() == ["test"]


@pytest.mark.asyncio
async def test_revomon_table_get_name_by_id(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchone.return_value = ["test"]
        assert table.get_name_by_id(dex_id=1) == "test"
        assert table.get_name_by_id(mon_id=10) == "test"


@pytest.mark.asyncio
async def test_revomon_table_get_id_by_id(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchone.return_value = [10]
        assert table.get_id_by_id(dex_id=1) == 10
        assert table.get_id_by_id(mon_id=10) == 10

        mock_conn.return_value.cursor.return_value.fetchone.return_value = None
        with pytest.raises(ValueError):
            table.get_id_by_id(dex_id=99)


@pytest.mark.asyncio
async def test_revomon_table_get_info(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchall.return_value = [[1, 10, "testmon"]]
        rows = table.get_info("TEST")
        assert len(rows) == 1
        assert rows[0][2] == "testmon"


@pytest.mark.asyncio
async def test_revomon_table_has_ability(mock_db_path: Any) -> None:
    table = RevomonTable()
    table.db_path = mock_db_path
    with patch("sqlite3.connect") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value

        # Test 1
        mock_cursor.fetchall.return_value = [("testmon",)]
        assert table.has_ability("ab1", "testmon") is True

        # Test 2
        mock_cursor.fetchall.return_value = []
        assert table.has_ability("ab4", "testmon") is False

        # Test 3
        mock_cursor.fetchall.return_value = [("testmon",)]
        assert table.has_ability("ab2") == ["testmon"]

        # Test 4
        mock_cursor.fetchall.return_value = []
        assert table.has_ability("ab4") == []
