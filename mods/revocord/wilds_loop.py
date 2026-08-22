import json
import logging
import random
import time
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands, tasks

from mods.revocord.hunting import BIOME_TYPES
from scripts.gradexDB import (
    active_spawns_table,
    get_guild_biome,
    get_guild_spawn_state,
)

logger = logging.getLogger("discord_bot")


class WildsLoopCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.revomons: list[dict[str, Any]] = []
        self.evolved_names: set[str] = set()
        self.natures: list[dict[str, Any]] = []
        self._load_data()
        self.wilds_spawn_loop.start()

    async def cog_unload(self) -> None:
        self.wilds_spawn_loop.cancel()

    def _load_data(self) -> None:
        evolutions_path = Path("data", "evolutions.json")
        if evolutions_path.exists():
            try:
                with open(evolutions_path, encoding="utf-8") as f:
                    ev_data = json.load(f)
                    for _, ev_info in ev_data.items():
                        to_name = ev_info.get("to")
                        if to_name:
                            self.evolved_names.add(to_name.strip().lower())
            except Exception as e:
                logger.error("Failed to load evolution data: %s", e)

        revomon_path = Path("data", "revomon.json")
        if revomon_path.exists():
            try:
                with open(revomon_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self.revomons = (
                        data.get("revomons", data) if isinstance(data, dict) else data
                    )
            except Exception as e:
                logger.error("Failed to load revomon data: %s", e)

        self.natures = []
        natures_path = Path("data", "natures.json")
        if natures_path.exists():
            try:
                with open(natures_path, encoding="utf-8") as f:
                    self.natures = json.load(f)
            except Exception:
                pass

    def _get_revomon_image_path(
        self, revomon_data: dict[str, Any], is_shiny: bool
    ) -> Path:
        id_revodex = revomon_data.get("dex_id", revomon_data.get("idRevodex"))
        suffix = "_shiny" if is_shiny else ""
        img_path = Path("data", "assets", "revomon", "raw", f"{id_revodex}{suffix}.png")
        if is_shiny and not img_path.exists():
            img_path = Path("data", "assets", "revomon", "raw", f"{id_revodex}.png")
        return img_path

    async def _do_spawn(self, guild: discord.Guild) -> None:
        current_biome = await get_guild_biome(guild.id)
        allowed_types = BIOME_TYPES.get(current_biome, {"neutral"})

        eligible = []
        for r in self.revomons:
            r_type1 = (r.get("type1") or "").lower()
            r_type2 = (r.get("type2") or "").lower()
            if (r_type1 in allowed_types or r_type2 in allowed_types) and r.get(
                "name", ""
            ).lower() not in self.evolved_names:
                eligible.append(r)

        if not eligible:
            return

        chosen = random.choice(eligible)
        is_shiny = random.random() < 0.01

        name = chosen.get("name", "Unknown").title()

        nature = (
            random.choice(self.natures)["name"].title() if self.natures else "Hardy"
        )
        raw_abilities = [
            chosen.get(k)
            for k in ["ability1", "ability2", "ability_hidden"]
            if chosen.get(k)
        ]
        abilities = [a for a in raw_abilities if isinstance(a, str)]
        ability = random.choice(abilities).title() if abilities else "Unknown"
        ivs = {
            k: random.randint(0, 31) for k in ["hp", "atk", "def", "spa", "spd", "spe"]
        }

        timestamp = int(time.time())
        id_revomon = chosen.get("mon_id", chosen.get("idRevomon", 0))

        encounter_data = {
            "nature": nature.lower(),
            "ability": ability.lower(),
            "ivs": ivs,
            "mon_id": id_revomon,
            "name": name,
            "is_shiny": is_shiny,
            "timestamp": timestamp,
        }

        # Generate a unique spawn ID (random 63-bit positive integer)
        spawn_id = random.randint(1, 2**62)

        await active_spawns_table.add_spawn(
            spawn_id, guild.id, json.dumps(encounter_data)
        )

    @tasks.loop(seconds=15)
    async def wilds_spawn_loop(self) -> None:
        if not self.revomons:
            return

        current_time = int(time.time())
        for guild in self.bot.guilds:
            try:
                state = await get_guild_spawn_state(guild.id)
                eff_limit = state["max_spawn_limit"]
                if state["temp_limit_expires"] > current_time:
                    eff_limit += state["temp_spawn_limit"]

                if state["current_spawns"] >= eff_limit:
                    continue

                if current_time < state["next_spawn_time"]:
                    continue

                await self._do_spawn(guild)

                mult = (
                    state["spawn_multiplier"]
                    if state["spawn_multiplier_expires"] > current_time
                    else 1.0
                )
                delay = random.randint(60, 300)
                delay = max(10, int(delay / mult))

                from scripts.gradexDB import update_guild_spawn_config

                await update_guild_spawn_config(
                    guild.id, next_spawn_time=current_time + delay
                )
            except Exception as e:
                logger.error(f"Error in wilds_spawn_loop for guild {guild.id}: {e}")

    @wilds_spawn_loop.before_loop
    async def before_wilds_spawn_loop(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WildsLoopCog(bot))
