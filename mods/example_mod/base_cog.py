import logging

from discord.ext import commands


class CogName(commands.Cog):
    """Example cog for Gradex Tool Mods."""

    def __init__(self, gradex_tool: commands.Bot):
        self.gradex_tool = gradex_tool
        self.cog_name = "CogName"

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        logging.info(f"{self.cog_name} is ready!")
        logging.info("-" * 50)


async def setup(gradex_tool: commands.Bot):
    """Setup function for the cog."""
    cog = CogName(gradex_tool)
    logging.info(f"Loading {cog.cog_name}...")
    try:
        await gradex_tool.add_cog(cog)
        logging.info(f"Successfully loaded {cog.cog_name}")
    except Exception as e:
        logging.error(f"ERROR loading {cog.cog_name}: {e}")
