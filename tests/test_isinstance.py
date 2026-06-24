from unittest.mock import MagicMock

import discord

m = MagicMock(spec=discord.CategoryChannel)
print("Is instance?", isinstance(m, discord.CategoryChannel))
