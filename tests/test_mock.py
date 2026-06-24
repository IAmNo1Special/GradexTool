import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch


async def main() -> None:
    mock = AsyncMock()
    mock.return_value = {"inventory": {"159": 1}}

    with patch("mods.revocord.shared.get_or_create_account", mock):
        from mods.revocord.shared import get_or_create_account
        account = await get_or_create_account(123)
        print("Account is:", account)

if __name__ == "__main__":
    asyncio.run(main())
