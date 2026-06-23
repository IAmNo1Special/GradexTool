from typing import Any
import unittest.mock
import pytest
from unittest.mock import patch, MagicMock
from utils.land_utils import (
    get_land_info_for_ids,
    get_land_owners_and_ids,
    get_land_data,
    get_lands_for_sale,
    get_zkevm_token_data,
    get_lands_for_sale_amount,
)


class MockResponse:
    def __init__(self, json_data: Any=None, status: Any=200, text_data: Any="") -> None:
        self.json_data = json_data
        self.status = status
        self.text_data = text_data

    async def json(self) -> Any:
        return self.json_data

    async def text(self) -> Any:
        return self.text_data


class MockGetContext:
    def __init__(self, response: Any) -> None:
        self.response = response

    async def __aenter__(self) -> Any:
        return self.response

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class MockSessionContext:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def __aenter__(self) -> Any:
        return self.session

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


@pytest.fixture
def mock_session() -> None:  # type: ignore[misc]
    with patch('aiohttp.ClientSession') as mock_client_session:
        session_instance = MagicMock()
        mock_client_session.return_value = MockSessionContext(session_instance)
        yield session_instance


@pytest.mark.asyncio
async def test_get_land_info_for_ids(mock_session: Any) -> None:
    mock_response = MockResponse(
        json_data={
            "result": [
                {
                    "token_id": "1",
                    "image": "http://image1.png",
                    "attributes": [
                        {"value": "Forest"},  # biome
                        {"value": "ignore"},
                        {"value": "Land"},  # entity_type
                        {"value": "ID1"},  # id
                        {"value": "Common"},  # rarity
                        {"value": "Small"}  # size
                    ]
                },
                {
                    "token_id": "2",
                    "image": "http://image2.png",
                    "attributes": [
                        {"value": "Desert"}  # biome
                    ]  # test len <= 2
                }
            ]
        }
    )
    mock_session.get.return_value = MockGetContext(mock_response)

    token_ids = [str(i) for i in range(35)]  # > 30 to test the split
    result = await get_land_info_for_ids(token_ids)

    assert len(result) == 4
    assert result[0]["id"] == "ID1"
    assert result[0]["biome"] == "forest"
    assert result[0]["land_type"] == "land"
    assert result[0]["rarity"] == "common"
    assert result[0]["size"] == "Small"
    assert result[0]["img_url"] == "http://image1.png"

    assert result[1]["id"] is None
    assert result[1]["biome"] == "desert"
    assert result[1]["land_type"] is None
    assert result[1]["rarity"] is None
    assert result[1]["size"] is None
    assert result[1]["img_url"] == "http://image2.png"


@pytest.mark.asyncio
async def test_get_land_info_for_ids_short(mock_session: Any) -> None:
    mock_response = MockResponse(
        json_data={
            "result": [
                {
                    "token_id": "1",
                    "image": "http://image1.png",
                    "attributes": [
                        {"value": "Forest"},
                        {"value": "ignore"},
                        {"value": "Land"},
                        {"value": "ID1"},
                        {"value": "Common"},
                        {"value": "Small"}
                    ]
                }
            ]
        }
    )
    mock_session.get.return_value = MockGetContext(mock_response)

    token_ids = ["1"]
    result = await get_land_info_for_ids(token_ids)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_land_owners_and_ids(mock_session: Any) -> None:
    mock_response_1 = MockResponse(
        json_data={
            "result": [
                {"account_address": "0x1", "token_id": "100"},
                {"account_address": "0xbc56eb15427dc7ec6e46cb42715c8b3f28c57c8d", "token_id": "ignore1"},
                {"account_address": "0x0000000000000000000000000000000000000000", "token_id": "ignore2"},
                {"account_address": "0x2", "token_id": "101"},
                {"account_address": "0x1", "token_id": "100"},  # duplicate token for owner
            ],
            "page": {"next_cursor": "cursor1"}
        }
    )
    mock_response_2 = MockResponse(
        json_data={
            "result": [
                {"account_address": "0x2", "token_id": "102"}
            ],
            "page": {"next_cursor": ""}
        }
    )
    mock_session.get.side_effect = [MockGetContext(mock_response_1), MockGetContext(mock_response_2)]

    result = await get_land_owners_and_ids()
    assert len(result) == 2
    assert result[0]["owners_address"] == "0x1"
    assert result[0]["owned_tokens"] == ["100"]
    assert result[1]["owners_address"] == "0x2"
    assert result[1]["owned_tokens"] == ["101", "102"]


@pytest.mark.asyncio
@patch('utils.land_utils.get_land_owners_and_ids')
@patch('utils.land_utils.get_land_info_for_ids')
async def test_get_land_data(mock_get_info: Any, mock_get_owners: Any) -> None:
    mock_get_owners.return_value = [
        {"owners_address": "0x1", "owned_tokens": ["1"]},
        {"owners_address": "0x2", "owned_tokens": ["2", "3"]}
    ]
    mock_get_info.side_effect = [
        [{"id": "L1"}],
        [{"id": "L2"}, {"id": "L3"}]
    ]
    result = await get_land_data()
    # It should sort by count descending
    assert len(result) == 2
    assert result[0]["owners_address"] == "0x2"
    assert result[0]["count"] == 2
    assert result[0]["land_info"] == [{"id": "L2"}, {"id": "L3"}]

    assert result[1]["owners_address"] == "0x1"
    assert result[1]["count"] == 1


@pytest.mark.asyncio
async def test_get_lands_for_sale(mock_session: Any) -> None:
    mock_response = MockResponse(
        json_data={"result": [{"id": "order1"}]}
    )
    mock_session.get.return_value = MockGetContext(mock_response)

    result = await get_lands_for_sale()
    assert result == [{"id": "order1"}]


@pytest.mark.asyncio
async def test_get_zkevm_token_data_success(mock_session: Any) -> None:
    mock_response = MockResponse(
        status=200,
        json_data={"symbol": "TEST"}
    )
    mock_session.get.return_value = MockGetContext(mock_response)

    result = await get_zkevm_token_data("0x123")
    assert result == {"symbol": "TEST"}


@pytest.mark.asyncio
async def test_get_zkevm_token_data_failure(mock_session: Any) -> None:
    mock_response = MockResponse(
        status=404,
        text_data="Not Found"
    )
    mock_session.get.return_value = MockGetContext(mock_response)

    result = await get_zkevm_token_data("0x123")
    assert result is None


@pytest.mark.asyncio
@patch('utils.land_utils.get_lands_for_sale')
@patch('utils.land_utils.get_zkevm_token_data')
async def test_get_lands_for_sale_amount(mock_get_token: Any, mock_get_sale: Any) -> None:
    mock_get_sale.return_value = [
        {
            "account_address": "0xO1",
            "sell": [{"token_id": "T1"}],
            "buy": [{"contract_address": "0xT1", "amount": "1000000000000000000"}],
            "fees": [{"amount": "500000000000000000"}]
        },
        {
            "account_address": "0xO2",
            "sell": [{"token_id": "T2"}],
            "buy": [{"type": "NATIVE", "amount": "2000000000000000000"}],
            "fees": []
        },
        {
            "account_address": "0xO3",
            "sell": [{"token_id": "T3"}],
            "buy": [{"contract_address": "0xT3", "amount": "1000000"}],
            "fees": []
        }
    ]

    mock_get_token.side_effect = [
        {"decimals": 18, "symbol": "WIMX", "exchange_rate": "2.0"},  # T1
        None,  # T2 - NATIVE
        {"decimals": 6, "symbol": "USDC", "exchange_rate": "1.0"},  # T3
    ]

    result = await get_lands_for_sale_amount()

    # T1: 1.5 * 2.0 = 3.0 USD
    assert "T1" in result
    assert result["T1"]["owners_address"] == "0xO1"
    assert result["T1"]["for_sale_token"] == 1.5
    assert result["T1"]["token_symbol"] == "IMX"  # WIMX replaced by IMX
    assert result["T1"]["for_sale_usd"] == 3.0

    # T2: NATIVE (default missing token data: 18 decimals, 0 exchange rate)
    assert "T2" in result
    assert result["T2"]["for_sale_token"] == 2.0
    assert result["T2"]["token_symbol"] == "UNKNOWN"
    assert result["T2"]["for_sale_usd"] == 0.0

    # T3: 1000000 -> 1.0 (6 decimals) -> * 1.0 = 1.0
    assert "T3" in result
    assert result["T3"]["for_sale_token"] == 1.0
    assert result["T3"]["token_symbol"] == "USDC"
    assert result["T3"]["for_sale_usd"] == 1.0


@pytest.mark.asyncio
@patch('utils.land_utils.get_lands_for_sale')
async def test_get_lands_for_sale_amount_key_error(mock_get_sale: Any) -> None:
    mock_get_sale.return_value = [
        {
            "account_address": "0xO1",
            "sell": [{"token_id": "T1"}],
            "buy": [{"type": "ERC20", "amount": "1"}],  # Missing contract_address
            "fees": []
        }
    ]
    with pytest.raises(KeyError):
        await get_lands_for_sale_amount()


def test_main_block() -> None:
    import runpy
    # Execute the module to cover the if __name__ == "__main__": block
    with unittest.mock.patch.dict('sys.modules'):

        import sys

        sys.modules.pop('utils.land_utils', None)

        runpy.run_module('utils.land_utils', run_name='__main__')

