import asyncio
from unittest.mock import MagicMock, AsyncMock

# We need to import the class
from mods.revocord.hunting import WildSpawnView

async def main():
    chosen = {"name": "TestMon", "type1": "neutral"}
    view = WildSpawnView(chosen, False, 123, 456)
    
    mock_message = MagicMock()
    embed = MagicMock()
    embed.description = "Original"
    mock_message.embeds = [embed]
    mock_message.edit = AsyncMock()
    
    view.message = mock_message
    
    try:
        embed = view.message.embeds[0]
        embed.description = (embed.description or "") + "\n\n*(This encounter has expired)*"
        await view.message.edit(embed=embed, view=None)
        print("Success! Edit was called.")
    except Exception as e:
        print(f"Exception: {e}")

asyncio.run(main())
