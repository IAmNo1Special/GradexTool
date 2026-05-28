"""Gradex Tool Main Entry Point."""

import sys
from os import getenv
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from configs.logging_config import setup_logging
from data.gradexDB import update_gradex_db
from mods import load_mods

load_dotenv()

logger = setup_logging("gradex_tool")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

gradex_tool: commands.Bot = commands.Bot(command_prefix="/", intents=intents)

gradex_tool.remove_command("help")

async def entrypoint(rebase: bool = False):
    logger.info(f"Starting Gradex Tool...\n{'-' * 50}")
    if rebase:
        logger.info(f"Rebasing Gradex DB...\n{'-' * 50}")
        await update_gradex_db()
    

    await load_mods()

    discord_bot_token = getenv("DISCORD_BOT_TOKEN", "")
    if not discord_bot_token:
        logger.error(f"DISCORD_BOT_TOKEN not found. Exiting.\n{'-' * 50}")
        sys.exit(1)

    try:
        async with gradex_tool:
            await gradex_tool.start(discord_bot_token, reconnect=True)
    except Exception as e:
        logger.error(f"Gradex Tool failed to start: {e}\n{'-' * 50}")
        sys.exit(1)
    finally:
        logger.info(f"Gradex Tool has been shut down.\n{'-' * 50}")


@gradex_tool.event
async def on_ready():
    logger.info(f"Gradex Tool is online.\n{'-' * 50}")
    synced_commands = await gradex_tool.tree.sync()
    logger.info(f"Synced {len(synced_commands)} commands\n{'-' * 50}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(entrypoint(rebase=True))
