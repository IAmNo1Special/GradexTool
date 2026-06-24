import asyncio
from unittest.mock import AsyncMock, MagicMock

# We need to import the class
from mods.revocord.hunting import WildSpawnView


async def main() -> None:
    chosen = {"name": "TestMon", "type1": "neutral"}
    view = WildSpawnView(chosen, False, 123, 456)

    mock_message = MagicMock()
    embed = MagicMock()
    embed.description = "Original"
    mock_message.embeds = [embed]
    mock_message.edit = AsyncMock()

    view.message = mock_message

    try:
        msg = getattr(view, "message", None)
        if msg:
            embed = msg.embeds[0]
            embed.description = (embed.description or "") + "\n\n*(This encounter has expired)*"
            await msg.edit(embed=embed, view=None)
            print("Success! Edit was called.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
