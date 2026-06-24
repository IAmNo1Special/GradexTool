from typing import Any

"""Gradex Tool Mods Loader.

This module is responsible for discovering and loading all Gradex Tool Mods
from the './mods' directory and its subdirectories.
"""

import logging  # noqa: E402
from pathlib import Path  # noqa: E402

from discord.ext import commands  # noqa: E402

logger = logging.getLogger(__name__)


async def load_mods(gradex_tool: commands.Bot) -> None:
    """Discover and load all Gradex Tool Mods from the './mods' directory."""
    logger.info(f"Loading Gradex Tool Mods...\n{'-' * 50}")
    mods_dir = Path(__file__).parent
    _skip_cogs = {"base_cog", "shared", "broadcaster", "tv"}
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
                logger.info(f"Loaded Mod: {ext}\n{'-' * 50}")
            except Exception as e:
                logger.error(f"Failed to load Mod {ext}: {e}\n{'-' * 50}")

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
                        logger.info(f"Loaded mod: {ext}\n{'-' * 50}")
                    except Exception as e:
                        logger.error(f"Failed to load mod {ext}: {e}\n{'-' * 50}")
    logger.info(f"All Gradex Tool Mods loaded successfully!\n{'-' * 50}")
