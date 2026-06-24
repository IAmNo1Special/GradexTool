import asyncio
from unittest.mock import AsyncMock, patch


async def main():
    mock = AsyncMock()
    mock.return_value = {"inventory": {"159": 1}}

    with patch("mods.revocord.hunting.get_or_create_account", mock):
        from mods.revocord.hunting import get_or_create_account
        account = await get_or_create_account("123")
        print("Account is:", account)

asyncio.run(main())
