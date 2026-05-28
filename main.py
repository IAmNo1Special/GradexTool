"""Gradex Tool Main Entry Point."""

import sys
from os import getenv
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from configs.logging_config import setup_logging
from data.gradexDB import update_gradex_db

load_dotenv()

logger = setup_logging("gradex_tool")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

gradex_tool: commands.Bot = commands.Bot(command_prefix="/", intents=intents)

gradex_tool.remove_command("help")


async def load_mods():
    """Discover and load all Gradex Tool Mods from the './mods' directory."""
    logger.info("Loading Gradex Tool Mods...")
    mods_dir = Path(__file__).parent / "mods"
    _skip_cogs = {"base_cog"}
    _skip_mods = {"example_mod", "elevens_arena"}
    # Load cogs saved directly in ./mods/ directory

    for filepath in mods_dir.iterdir():
        if (
            filepath.is_file()
            and filepath.suffix == ".py"
            and not filepath.name.startswith("_")
            and filepath.stem not in _skip_cogs
        ):
            ext = f"mods.{filepath.stem}"
            try:
                await gradex_tool.load_extension(ext)
                logger.info(f"Loaded Mod: {ext}")
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Failed to load Mod {ext}: {e}")
                logger.info("-" * 50)

    # Load nested mods from subdirectories
    for mod_dir in mods_dir.iterdir():
        if (
            mod_dir.is_dir()
            and not mod_dir.name.startswith("_")
            and mod_dir.name not in _skip_mods
        ):
            for filename in mod_dir.iterdir():
                if (
                    filename.suffix == ".py"
                    and not filename.name.startswith("_")
                    and filename.stem not in _skip_cogs
                ):
                    ext = f"mods.{mod_dir.name}.{filename.stem}"
                    try:
                        await gradex_tool.load_extension(ext)
                        logger.info(f"Loaded mod: {ext}")
                        logger.info("-" * 50)
                    except Exception as e:
                        logger.error(f"Failed to load mod {ext}: {e}")
                        logger.error("-" * 50)


async def entrypoint(rebase: bool = False):
    logger.info("Starting Gradex Tool...")
    if rebase:
        logger.info("Rebasing Gradex DB...")
        await update_gradex_db()
    

    await load_mods()

    discord_bot_token = getenv("DISCORD_BOT_TOKEN", "")
    if not discord_bot_token:
        logger.error("DISCORD_BOT_TOKEN not found. Exiting.")
        sys.exit(1)

    try:
        async with gradex_tool:
            await gradex_tool.start(discord_bot_token, reconnect=True)
    except Exception as e:
        logger.error(f"Gradex Tool failed to start: {e}")
        sys.exit(1)
    finally:
        logger.info("Gradex Tool has been shut down.")


@gradex_tool.event
async def on_ready():
    logger.info("Gradex Tool is online.")
    logger.info("-" * 50)
    synced_commands = await gradex_tool.tree.sync()
    logger.info(f"Synced {len(synced_commands)} commands")
    logger.info("-" * 50)


if __name__ == "__main__":
    import asyncio
    asyncio.run(entrypoint(rebase=True))
