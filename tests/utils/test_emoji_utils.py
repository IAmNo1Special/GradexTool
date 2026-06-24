import unittest.mock
from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from utils import emoji_utils


@pytest.fixture
def dummy_image_bytes() -> Any:
    img = Image.new("RGB", (256, 256), color="red")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@pytest.fixture
def mock_session() -> None:  # type: ignore[misc]
    with patch("aiohttp.ClientSession") as mock_session_cls:
        session_mock = MagicMock()
        mock_session_cls.return_value.__aenter__.return_value = session_mock
        yield session_mock


def setup_mock_response(
    session_mock: Any,
    method: Any,
    status: Any,
    json_data: Any = None,
    text_data: Any = "",
    content: Any = b"",
) -> Any:
    response_mock = AsyncMock()
    response_mock.status = status
    response_mock.json.return_value = json_data
    response_mock.text.return_value = text_data
    response_mock.read.return_value = content

    ctx_mgr = MagicMock()
    ctx_mgr.__aenter__.return_value = response_mock
    getattr(session_mock, method).return_value = ctx_mgr
    return response_mock


# Tests for img_url_to_emoji_size
@pytest.mark.asyncio
async def test_img_url_to_emoji_size_success(
    mock_session: Any, dummy_image_bytes: Any
) -> None:
    setup_mock_response(mock_session, "get", 200, content=dummy_image_bytes)
    res = await emoji_utils.img_url_to_emoji_size("http://example.com/img.png")
    assert res is not None
    img = Image.open(BytesIO(res))
    assert img.size == (128, 128)


@pytest.mark.asyncio
async def test_img_url_to_emoji_size_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "get", 404, text_data="Not Found")
    res = await emoji_utils.img_url_to_emoji_size("http://example.com/img.png")
    assert res == b""
    captured = capsys.readouterr()
    assert "Failed to fetch image: 404 - Not Found" in captured.out


# Tests for create_application_emoji
@pytest.mark.asyncio
async def test_create_application_emoji_success(mock_session: Any) -> None:
    setup_mock_response(
        mock_session, "post", 201, json_data={"name": "test_emoji", "id": "12345"}
    )
    res = await emoji_utils.create_application_emoji(b"dummy_data", "test_emoji")
    assert res == {"name": "test_emoji", "id": "12345"}


@pytest.mark.asyncio
async def test_create_application_emoji_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "post", 400, text_data="Bad Request")
    res = await emoji_utils.create_application_emoji(b"dummy_data", "test_emoji")
    assert res == {}
    captured = capsys.readouterr()
    assert "Failed to create emoji: 400 - Bad Request" in captured.out


# Tests for list_application_emojis
@pytest.mark.asyncio
async def test_list_application_emojis_success(mock_session: Any) -> None:
    setup_mock_response(
        mock_session,
        "get",
        200,
        json_data={
            "items": [{"name": "emoji1", "id": "1"}, {"name": "emoji2", "id": "2"}]
        },
    )
    res = await emoji_utils.list_application_emojis()
    assert res == [{"name": "emoji1", "id": "1"}, {"name": "emoji2", "id": "2"}]


@pytest.mark.asyncio
async def test_list_application_emojis_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "get", 401, text_data="Unauthorized")
    res = await emoji_utils.list_application_emojis()
    assert res == []
    captured = capsys.readouterr()
    assert "Failed to fetch emojis: 401 - Unauthorized" in captured.out


# Tests for get_application_emoji
@pytest.mark.asyncio
async def test_get_application_emoji_success(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(
        mock_session, "get", 200, json_data={"name": "emoji1", "id": "1"}
    )
    await emoji_utils.get_application_emoji("1")
    captured = capsys.readouterr()
    assert "Emoji Name: emoji1, Emoji ID: 1" in captured.out


@pytest.mark.asyncio
async def test_get_application_emoji_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "get", 404, text_data="Not Found")
    await emoji_utils.get_application_emoji("1")
    captured = capsys.readouterr()
    assert "Failed to fetch emoji: 404 - Not Found" in captured.out


# Tests for modify_application_emoji
@pytest.mark.asyncio
async def test_modify_application_emoji_success(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(
        mock_session, "patch", 200, json_data={"name": "new_name", "id": "1"}
    )
    await emoji_utils.modify_application_emoji("1", "new_name")
    captured = capsys.readouterr()
    assert "Emoji modified: new_name (ID: 1)" in captured.out


@pytest.mark.asyncio
async def test_modify_application_emoji_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "patch", 400, text_data="Bad Request")
    await emoji_utils.modify_application_emoji("1", "new_name")
    captured = capsys.readouterr()
    assert "Failed to modify emoji: 400 - Bad Request" in captured.out


# Tests for delete_application_emoji
@pytest.mark.asyncio
async def test_delete_application_emoji_success(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "delete", 204)
    await emoji_utils.delete_application_emoji("1")
    captured = capsys.readouterr()
    assert "Emoji with ID 1 deleted successfully." in captured.out


@pytest.mark.asyncio
async def test_delete_application_emoji_failure(mock_session: Any, capsys: Any) -> None:
    setup_mock_response(mock_session, "delete", 400, text_data="Bad Request")
    await emoji_utils.delete_application_emoji("1")
    captured = capsys.readouterr()
    assert "Failed to delete emoji: 400 - Bad Request" in captured.out


# Tests for create_emoji_from_url
@pytest.mark.asyncio
@patch("utils.emoji_utils.img_url_to_emoji_size", new_callable=AsyncMock)
@patch("utils.emoji_utils.create_application_emoji", new_callable=AsyncMock)
async def test_create_emoji_from_url(
    mock_create_app_emoji: Any, mock_img_url_to_emoji: Any
) -> None:
    mock_img_url_to_emoji.return_value = b"image_data"
    mock_create_app_emoji.return_value = {"name": "test", "id": "123"}
    res = await emoji_utils.create_emoji_from_url("http://test.com/img.png", "test")
    assert res == {"name": "test", "id": "123"}
    mock_img_url_to_emoji.assert_called_once_with("http://test.com/img.png")
    mock_create_app_emoji.assert_called_once_with(b"image_data", emoji_name="test")


# Tests for create_revomon_emojis
@pytest.mark.asyncio
@patch("utils.emoji_utils.list_application_emojis", new_callable=AsyncMock)
@patch("utils.emoji_utils.create_emoji_from_url", new_callable=AsyncMock)
@patch("utils.emoji_utils.RevomonTable")
@patch("utils.emoji_utils.get_attributes", new_callable=AsyncMock)
async def test_create_revomon_emojis_success(
    mock_get_attrs: Any,
    mock_revo_table: Any,
    mock_create_emoji: Any,
    mock_list_emojis: Any,
) -> None:
    mock_revo_table_inst = MagicMock()
    mock_revo_table_inst.get_names = AsyncMock(
        return_value=["existing-mon", "partial_mon", "new_mon", "error_mon"]
    )
    mock_revo_table.return_value = mock_revo_table_inst

    def get_attrs_side_effect(name: Any) -> Any:
        return {
            "profile_img": f"http://test.com/{name}.png",
            "shiny_profile_img": f"http://test.com/{name}_shiny.png",
        }

    mock_get_attrs.side_effect = get_attrs_side_effect

    def create_emoji_side_effect(url: Any, emoji_name: Any) -> Any:
        if "error" in emoji_name:
            raise Exception("Test error")
        return {"name": emoji_name, "id": "123"}

    mock_create_emoji.side_effect = create_emoji_side_effect

    mock_list_emojis.side_effect = [
        [
            {"name": "existing_mon", "id": "1"},
            {"name": "partial_mon_shiny", "id": "2"},
        ],  # First call
        [{"name": "existing_mon", "id": "1"}],  # Second call, doesn't matter much
    ]

    res = await emoji_utils.create_revomon_emojis()
    assert len(res) == 1
    assert mock_create_emoji.call_count == 4


# Tests for create_land_emojis
@pytest.mark.asyncio
@patch("utils.emoji_utils.list_application_emojis", new_callable=AsyncMock)
@patch("utils.emoji_utils.create_emoji_from_url", new_callable=AsyncMock)
@patch("utils.emoji_utils.OwnedLandsTable")
async def test_create_land_emojis(
    mock_lands_table: Any, mock_create_emoji: Any, mock_list_emojis: Any
) -> None:
    mock_list_emojis.return_value = [{"name": "existing_land", "id": "1"}]

    mock_lands_table_inst = MagicMock()
    mock_lands_table_inst.get_ids = AsyncMock(return_value=[1, 2])

    def get_info_side_effect(token_id: Any) -> Any:
        if token_id == 1:
            return [[0, 1, 2, "existing", "land", 5, 6, "http://test.com/land1.png"]]
        elif token_id == 2:
            return [[0, 1, 2, "new", "land", 5, 6, "http://test.com/land2.png"]]

    mock_lands_table_inst.get_info = AsyncMock(side_effect=get_info_side_effect)
    mock_lands_table.return_value = mock_lands_table_inst

    mock_create_emoji.return_value = {"name": "new_land", "id": "2"}

    res = await emoji_utils.create_land_emojis()
    assert len(res) == 2
    assert mock_create_emoji.call_count == 1
    mock_create_emoji.assert_called_once_with(
        "http://test.com/land2.png", emoji_name="new_land"
    )


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_if_name_main() -> None:
    import runpy

    with unittest.mock.patch.dict("sys.modules"):
        import sys

        sys.modules.pop("utils.emoji_utils", None)

        runpy.run_module("utils.emoji_utils", run_name="__main__")
