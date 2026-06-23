import discord
from unittest.mock import MagicMock

m = MagicMock(spec=discord.CategoryChannel)
print("Is instance?", isinstance(m, discord.CategoryChannel))
