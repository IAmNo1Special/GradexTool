from typing import Any

"""Gradex Tool Mods Loader.

This module is responsible for discovering and loading all Gradex Tool Mods
from the './mods' directory and its subdirectories.

Which mods load is controlled by an optional manifest file,
``mods/mods.yaml``:

    enabled:
      - revomon
      - elevens_arena

When the manifest is missing, the loader keeps its previous behavior:
every discovered mod loads except ``example_mod`` and ``elevens_arena``.
When the manifest is present, only the mods it lists load, so removing a
name disables that mod and adding a previously skipped name enables it.

Helper modules are kept separate from the on/off list. The cog names in
``_SKIP_COGS`` are never loaded as extensions, even if the manifest
lists them, because they are shared helpers, not mods.
"""

import logging  # noqa: E402
from pathlib import Path  # noqa: E402

import yaml  # noqa: E402
from discord.ext.commands import Bot  # noqa: E402

logger = logging.getLogger(__name__)

# Helper cog modules, shared by mods. Never loaded as extensions, and
# never governed by the mod manifest.
_SKIP_COGS = {"base_cog", "shared", "broadcaster", "tv"}

# Mods that stay off when no manifest file is present.
_DEFAULT_SKIP_MODS = {"example_mod", "elevens_arena"}

MANIFEST_FILENAME = "mods.yaml"


def _read_enabled_mods(
    mods_dir: Any, manifest_path: Any = None
) -> set[str] | None:
    """Return the manifest's enabled mod names, or None when absent.

    Returns None when the manifest file is missing, unreadable, or
    malformed, so the caller falls back to the previous behavior
    instead of failing startup.
    """
    path = manifest_path if manifest_path is not None else mods_dir / MANIFEST_FILENAME
    try:
        if not path.exists():
            return None
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Ignoring unreadable mod manifest {path}: {e}")
        return None
    if isinstance(data, dict):
        data = data.get("enabled")
    if not isinstance(data, list) or not all(isinstance(name, str) for name in data):
        logger.warning(f"Ignoring malformed mod manifest {path}: expected an 'enabled' list of names")
        return None
    return set(data)


def _is_mod_enabled(name: str, enabled_mods: set[str] | None) -> bool:
    """Check whether a mod directory or top-level mod file should load."""
    if enabled_mods is not None:
        return name in enabled_mods
    return name not in _DEFAULT_SKIP_MODS


async def load_mods(
    gradex_tool: Bot, mods_dir: Any = None, manifest_path: Any = None
) -> None:
    """Discover and load all Gradex Tool Mods from the './mods' directory.

    Args:
        gradex_tool: The bot to load extensions into.
        mods_dir: Directory to scan, defaulting to this package's directory.
            Exposed for testing so the real mods directory is not needed.
        manifest_path: Manifest file to read, defaulting to
            ``mods_dir/mods.yaml``. When it is missing, the loader keeps
            its previous behavior.
    """
    logger.info(f"Loading Gradex Tool Mods...\n{'-' * 50}")
    if mods_dir is None:
        mods_dir = Path(__file__).parent
    enabled_mods = _read_enabled_mods(mods_dir, manifest_path)
    # Load cogs saved directly in ./mods/ directory

    for filepath in mods_dir.iterdir():
        if (
            filepath.is_file()
            and filepath.suffix == ".py"
            and not filepath.name.startswith("_")
            and filepath.stem not in _SKIP_COGS
            and _is_mod_enabled(filepath.stem, enabled_mods)
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
            and _is_mod_enabled(mod_dir.name, enabled_mods)
        ):
            for filename in mod_dir.iterdir():
                if (
                    filename.suffix == ".py"
                    and not filename.name.startswith("_")
                    and filename.stem not in _SKIP_COGS
                ):
                    ext = f"mods.{mod_dir.name}.{filename.stem}"
                    try:
                        await gradex_tool.load_extension(ext)
                        logger.info(f"Loaded mod: {ext}\n{'-' * 50}")
                    except Exception as e:
                        logger.error(f"Failed to load mod {ext}: {e}\n{'-' * 50}")
    logger.info(f"All Gradex Tool Mods loaded successfully!\n{'-' * 50}")
