import asyncio
from typing import Any
from unittest.mock import AsyncMock


async def test_async_mock() -> None:
    def my_side_effect(**kwargs: Any) -> str:
        return "hello"

    m = AsyncMock(side_effect=my_side_effect)
    res = await m()
    print("Type of res:", type(res), "Value:", res)


asyncio.run(test_async_mock())
