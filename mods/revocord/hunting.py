from typing import Any

"""Cog for wild Revomon encounter hunting loop."""

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import discord  # noqa: E402
from discord import ui  # noqa: E402
from discord.ext import commands, tasks  # noqa: E402

from mods.revocord.broadcaster import (  # noqa: E402
    broadcast_encounter,
    update_encounter_broadcast,
)
from mods.revocord.shared import get_or_create_account, update_account  # noqa: E402
from scripts.gradexDB import (  # noqa: E402
    delete_active_encounter,
    get_active_encounter,
    get_guild_biome,
    get_next_rc_id,
    save_active_encounter,
)

logger = logging.getLogger("discord_bot")

# Dynamic spawn mapping connecting physical Biomes to elemental Types
BIOME_TYPES = {
    "Forest": {"forest", "bug", "neutral"},
    "Jungle": {"forest", "bug", "toxic"},
    "Plains": {"neutral", "battle", "sky"},
    "Tundra": {"ice", "spirit"},
    "Caves": {"stone", "earth", "metal"},
    "Beach": {"water", "sky"},
    "Crater": {"fire", "stone", "draconic"},
    "Swamp": {"toxic", "phantom", "water"},
    "Desert": {"earth", "fire", "time"},
    "Urban": {"electric", "metal", "twilight"},
    "Underwater": {"water", "ice"},
}

GLOBAL_SPAWNS: set[int] = set()

ORB_CONFIG: dict[str, dict[str, Any]] = {
    "RED": {"id": "159", "mult": 1.0, "emoji": "🔴", "label": "Red Orb"},
    "BLUE": {"id": "4", "mult": 1.5, "emoji": "🔵", "label": "Blue Orb"},
    "GREEN": {"id": "31", "mult": 2.0, "emoji": "🟢", "label": "Green Orb"},
}


# Thematic hex colors based on creature types for premium visual embed backgrounds
TYPE_COLORS = {
    "battle": 0xC0392B,  # Dark Red
    "bug": 0x27AE60,  # Forest Green
    "draconic": 0x8E44AD,  # Purple
    "earth": 0xD35400,  # Orange/Brown
    "electric": 0xF1C40F,  # Yellow
    "fire": 0xE67E22,  # Orange-Red
    "forest": 0x2ECC71,  # Emerald Green
    "ice": 0x3498DB,  # Sky Blue
    "metal": 0x7F8C8D,  # Grey
    "neutral": 0xBDC3C7,  # Light Grey
    "phantom": 0x2C3E50,  # Dark Navy
    "sky": 0x5DADE2,  # Celestial Blue
    "spirit": 0x9B59B6,  # Amethyst Purple
    "stone": 0x7E5109,  # Dark Brown
    "time": 0x1ABC9C,  # Turquoise
    "toxic": 0x16A085,  # Deep Teal
    "twilight": 0x34495E,  # Slate Grey
    "water": 0x2980B9,  # Strong Blue
}


class WildSpawnView(ui.View):
    """View shown when a wild Revomon is spawned. Has Fight and Run buttons."""

    def __init__(self, revomon: dict[str, Any], is_shiny: bool, spawner_id: int, event_msg_id: int = 0) -> None:
        super().__init__(timeout=None)
        self.revomon = revomon
        self.is_shiny = is_shiny
        self.spawner_id = spawner_id
        self.event_msg_id = event_msg_id

        timestamp = int(time.time())
        id_revomon = revomon.get("mon_id", revomon.get("idRevomon", 0))
        shiny_int = 1 if is_shiny else 0

        fight_btn: ui.Button[Any] = ui.Button(
            label="Fight", style=discord.ButtonStyle.danger, emoji="⚔️",
            custom_id=f"spawn_fight:{spawner_id}:{id_revomon}:{shiny_int}:{timestamp}:{event_msg_id}",
        )
        catch_btn: ui.Button[Any] = ui.Button(
            label="Throw Orb", style=discord.ButtonStyle.success, emoji="🔮",
            custom_id=f"spawn_catch_menu:{spawner_id}:{id_revomon}:{shiny_int}:{timestamp}:{event_msg_id}",
        )
        run_btn: ui.Button[Any] = ui.Button(
            label="Run", style=discord.ButtonStyle.secondary, emoji="🏃",
            custom_id=f"spawn_run:{spawner_id}:{id_revomon}:{shiny_int}:{timestamp}:{event_msg_id}",
        )
        self.add_item(fight_btn)
        self.add_item(catch_btn)
        self.add_item(run_btn)

        if event_msg_id == 0:
            share_btn: ui.Button[Any] = ui.Button(
                label="Share", style=discord.ButtonStyle.primary, emoji="📤",
                custom_id=f"spawn_share:{spawner_id}:{id_revomon}:{shiny_int}:{timestamp}"
            )
            self.add_item(share_btn)


class HuntingCog(commands.Cog):
    """Cog for managing Revomon hunting spawner algorithms."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the HuntingCog and load game databases.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self.revomons = []
        self.evolved_names = set()



        # Load evolution chains to determine first-stage stages
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

        # Load all revomon database
        revomon_path = Path("data", "revomon.json")
        if revomon_path.exists():
            try:
                with open(revomon_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.revomons = data.get("revomons", [])
                    else:
                        self.revomons = data
            except Exception as e:
                logger.error("Failed to load revomon data: %s", e)

        # Load natures database
        self.natures = []
        natures_path = Path("data", "natures.json")
        if natures_path.exists():
            try:
                with open(natures_path, encoding="utf-8") as f:
                    self.natures = json.load(f)
            except Exception as e:
                logger.error("Failed to load natures data: %s", e)

    def _get_revomon_image_path(self, revomon_data: dict[str, Any], is_shiny: bool) -> Path:
        """Helper method to construct and fallback the correct image asset path.

        Args:
            revomon_data: Dictionary of the Revomon's database entry.
            is_shiny: Boolean indicating if the shiny variant is requested.

        Returns:
            Path object pointing to the Revomon's image sprite.
        """
        id_revodex = revomon_data.get("dex_id", revomon_data.get("idRevodex"))
        suffix = "_shiny" if is_shiny else ""
        img_path = Path("data", "assets", "revomon", "raw", f"{id_revodex}{suffix}.png")

        # Fallback to normal if shiny sprite is missing
        if is_shiny and not img_path.exists():
            img_path = Path("data", "assets", "revomon", "raw", f"{id_revodex}.png")

        return img_path



    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        """Listen to button interactions globally to handle wild encounters.

        This handles clicks both before and after bot restarts.

        Args:
            interaction: The incoming Discord interaction.
        """
        if interaction.type != discord.InteractionType.component:
            return

        if not interaction.data or not isinstance(interaction.data, dict):
            return

        custom_id = interaction.data.get("custom_id")
        if not isinstance(custom_id, str):
            return

        if custom_id == "console_hunt":
            await self.spawn_wild_revomon(interaction)
            return

        if custom_id.startswith("return_console:"):
            await interaction.response.defer()
            spawner_id = int(custom_id.split(":")[1])
            account = await get_or_create_account(spawner_id)
            from mods.revocord.portal import GameConsoleView, build_console_embed
            new_embed = await build_console_embed(account, interaction.user)
            await interaction.edit_original_response(embed=new_embed, view=GameConsoleView(spawner_id), attachments=[])
            return

        if custom_id.startswith("wilds_claim:"):
            await self.handle_wilds_claim(interaction)
            return

        prefixes = (
            "spawn_fight:",
            "spawn_run:",
            "spawn_catch_menu:",
            "spawn_throw_orb:",
            "spawn_share:",
        )
        if not any(custom_id.startswith(p) for p in prefixes):
            return

        # Parse custom_id: action:spawner_id:id_revomon:is_shiny:timestamp
        try:
            parts = custom_id.split(":")
            action = parts[0]
            spawner_id = int(parts[1])
            id_revomon = int(parts[2])
            is_shiny = bool(int(parts[3]))
            timestamp = int(parts[4])
            msg_id = int(parts[5]) if len(parts) > 5 else None
        except Exception as e:
            logger.error(f"EXCEPTION IN ON_INTERACTION: {e}", exc_info=True)
            return

        # Check trainer permission
        if interaction.user.id != spawner_id:
            await interaction.response.send_message(
                "❌ Only the trainer who encountered this wild "
                "Revomon can interact with it!",
                ephemeral=True,
            )
            return

        # Check expiration (5 minutes / 300 seconds)
        if time.time() - timestamp > 300:
            await interaction.response.defer()
            await delete_active_encounter(spawner_id)
            account = await get_or_create_account(spawner_id)
            from mods.revocord.portal import GameConsoleView, build_console_embed
            new_embed = await build_console_embed(account, interaction.user)
            await interaction.edit_original_response(
                content="❌ **This encounter has expired and the Revomon fled into the wilds!**",
                embed=new_embed,
                view=GameConsoleView(spawner_id),
                attachments=[]
            )

            msg_id = int(parts[5]) if len(parts) > 5 else 0
            if msg_id:
                try:
                    await update_encounter_broadcast(interaction.guild, msg_id, "Fled (Expired)", 0x7F8C8D)
                except Exception:
                    pass
                await self._cleanup_wilds_spawn(interaction.guild, msg_id)
            return

        # Handle the actions
        if action == "spawn_run":
            await interaction.response.defer()
            await delete_active_encounter(spawner_id)
            account = await get_or_create_account(spawner_id)
            from mods.revocord.portal import GameConsoleView, build_console_embed
            new_embed = await build_console_embed(account, interaction.user)
            await interaction.edit_original_response(embed=new_embed, view=GameConsoleView(spawner_id), attachments=[])
            if msg_id:
                try:
                    await update_encounter_broadcast(interaction.guild, msg_id, "Ran", 0x7F8C8D)
                except Exception:
                    pass
                await self._cleanup_wilds_spawn(interaction.guild, msg_id)
        elif action == "spawn_fight":
            await interaction.response.send_message(
                "Battle system is not yet implemented! 🚧", ephemeral=True
            )
        elif action == "spawn_share":
            await interaction.response.defer()
            # The original message has the embed
            if not interaction.message or not interaction.message.embeds:
                return

            embed = interaction.message.embeds[0]
            # Strip the "Expires at" footer
            embed.set_footer(text=None)

            # Find the monster data to get rarity and details
            revomon_data = None
            for r in self.revomons:
                if r.get("mon_id", r.get("idRevomon")) == id_revomon:
                    revomon_data = r
                    break

            name = revomon_data.get("name", "Unknown").title() if revomon_data else "Unknown"
            rarity = revomon_data.get("rarity", "common").title() if revomon_data else "Common"

            await broadcast_encounter(
                self.bot, interaction.user, name, str(id_revomon), rarity, is_shiny, embed
            )
            await interaction.followup.send("📤 Encounter shared to the Event Board!", ephemeral=True)
        elif action == "spawn_catch_menu":
            account = await get_or_create_account(spawner_id)
            inventory = account.get("inventory", {})
            logger.error(f"DEBUG: account={account}, inventory={inventory}")

            red_count = inventory.get(ORB_CONFIG["RED"]["id"], 0)
            blue_count = inventory.get(ORB_CONFIG["BLUE"]["id"], 0)
            green_count = inventory.get(ORB_CONFIG["GREEN"]["id"], 0)

            total_orbs = red_count + blue_count + green_count
            if total_orbs <= 0:
                await interaction.response.send_message(
                    "❌ You do not have any Orbs in your inventory!\n"
                    "Visit the **RevoCenter** thread to buy some orbs.",
                    ephemeral=True,
                )
                return

            options = []
            if red_count > 0:
                options.append(
                    discord.SelectOption(
                        label=f"Red Orb (x{red_count})",
                        value=str(ORB_CONFIG["RED"]["id"]),
                        description="Catch multiplier: 1.0x",
                        emoji="🔴",
                    )
                )
            if blue_count > 0:
                options.append(
                    discord.SelectOption(
                        label=f"Blue Orb (x{blue_count})",
                        value=str(ORB_CONFIG["BLUE"]["id"]),
                        description="Catch multiplier: 1.5x",
                        emoji="🔵",
                    )
                )
            if green_count > 0:
                options.append(
                    discord.SelectOption(
                        label=f"Green Orb (x{green_count})",
                        value=str(ORB_CONFIG["GREEN"]["id"]),
                        description="Catch multiplier: 2.0x",
                        emoji="🟢",
                    )
                )

            # Dynamic view and select menu to pick which orb to throw
            class ThrowOrbSelect(ui.Select[Any]):
                def __init__(self, select_options: Any) -> None:
                    super().__init__(
                        placeholder="Choose an Orb to throw...",
                        min_values=1,
                        max_values=1,
                        options=select_options,
                        custom_id=(
                            f"spawn_throw_orb:{spawner_id}:{id_revomon}:{parts[3]}:{timestamp}:{msg_id}"
                        ),
                    )

            class ThrowOrbView(ui.View):
                def __init__(self, select_options: Any) -> None:
                    super().__init__(timeout=60)
                    self.add_item(ThrowOrbSelect(select_options))

            view = ThrowOrbView(options)
            await interaction.response.edit_message(view=view)

        elif action == "spawn_throw_orb":
            if not interaction.data or not isinstance(interaction.data, dict):
                return
            values = interaction.data.get("values", [None])
            if isinstance(values, list) and values:
                orb_id = str(values[0]) if values[0] else None
            else:
                orb_id = None
            if not orb_id:
                return

            if not interaction.message or not interaction.message.embeds:
                await interaction.response.send_message(
                    "❌ The original encounter card is invalid.",
                    ephemeral=True,
                )
                return

            account = await get_or_create_account(spawner_id)
            inventory = account.get("inventory", {})
            count = inventory.get(orb_id, 0)

            if count <= 0:
                await interaction.response.send_message(
                    "❌ You don't have any more of that Orb left!",
                    ephemeral=True,
                )
                return

            # Find the spawned Revomon in our database
            revomon_data = None
            for r in self.revomons:
                if r.get("mon_id", r.get("idRevomon")) == id_revomon:
                    revomon_data = r
                    break

            if not revomon_data:
                await interaction.response.send_message(
                    "❌ Error: Creature data not found.", ephemeral=True
                )
                return

            name = revomon_data.get("name", "Unknown").title()
            rarity = revomon_data.get("rarity", "common").lower()

            # Reconstruct image path for embeds using DRY helper
            img_path = self._get_revomon_image_path(revomon_data, is_shiny)

            # Deduct the orb
            inventory[orb_id] -= 1
            if inventory[orb_id] <= 0:
                del inventory[orb_id]

            # Calculate capture success
            base_rates = {
                "common": 0.60,
                "uncommon": 0.45,
                "rare": 0.30,
                "epic": 0.15,
                "legendary": 0.05,
            }
            base_rate = base_rates.get(rarity, 0.30)

            orb_multipliers = {str(cfg["id"]): float(cfg["mult"]) for cfg in ORB_CONFIG.values()}
            multiplier = orb_multipliers.get(orb_id, 1.0)
            final_rate = base_rate * multiplier

            roll = random.random()
            is_success = roll < final_rate

            if is_success:
                # Universal Biome scaling
                min_lvl, max_lvl = (5, 25)
                spawn_level = random.randint(min_lvl, max_lvl)

                # Fetch generated stats from Active Encounters DB
                active_encounter_raw = await get_active_encounter(spawner_id)
                caught_nature = "hardy"
                caught_ability = "unknown"
                ivs_dict = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}

                if active_encounter_raw:
                    try:
                        encounter_data = json.loads(active_encounter_raw)
                        caught_nature = encounter_data.get("nature", "hardy")
                        caught_ability = encounter_data.get("ability", "unknown")
                        ivs_dict = encounter_data.get("ivs", ivs_dict)
                    except json.JSONDecodeError:
                        pass

                total_iv = sum(ivs_dict.values())
                iv_pct = round((total_iv / 186.0) * 100, 2)

                rc_id = await get_next_rc_id()

                new_caught = {
                    "rc_id": rc_id,
                    "idRevomon": id_revomon,
                    "name": revomon_data.get("name", "unknown").lower(),
                    "level": spawn_level,
                    "xp": 0,
                    "is_shiny": is_shiny,
                    "captured_at": int(time.time()),
                    "nature": caught_nature.lower(),
                    "ability": caught_ability.lower(),
                    "ivs": ivs_dict,
                    "iv_percent": iv_pct
                }
                caught_list = account.get("caught_revomon", [])
                caught_list.append(new_caught)

                await update_account(
                    spawner_id,
                    inventory=inventory,
                    caught_revomon=caught_list,
                )

                # Edit original message embed to premium CAUGHT state
                shiny_str = "✨ SHINY " if is_shiny else ""
                embed = interaction.message.embeds[0]
                file = None
                if img_path.exists():
                    file = discord.File(img_path, filename="revomon.png")
                    embed.set_image(url="attachment://revomon.png")
                embed.title = f"🎉 {shiny_str}{name} was CAUGHT! 🎉"
                embed.description = "It has been added to your TV."
                embed.color = 0xF1C40F  # Gold/Success

                embed.set_footer(text=f"RC-ID: #{rc_id}")

                class ReturnToConsoleView(ui.View):
                    def __init__(self, spawner_id: int):
                        super().__init__(timeout=None)
                    @ui.button(label="Back to Console", style=discord.ButtonStyle.primary, emoji="🎮", custom_id=f"return_console:{spawner_id}")
                    async def return_console(self, inter: discord.Interaction, btn: ui.Button): pass

                if file:
                    await interaction.response.edit_message(embed=embed, view=ReturnToConsoleView(spawner_id), attachments=[file])
                else:
                    await interaction.response.edit_message(embed=embed, view=ReturnToConsoleView(spawner_id), attachments=[])

                if msg_id:
                    await update_encounter_broadcast(interaction.guild, msg_id, "Caught", 0xF1C40F)
                    await self._cleanup_wilds_spawn(interaction.guild, msg_id)

                await delete_active_encounter(spawner_id)
            else:
                # Deduct orb
                await update_account(spawner_id, inventory=inventory)

                # 30% chance to flee on fail
                will_flee = random.random() < 0.30
                if will_flee:
                    await delete_active_encounter(spawner_id)
                    if msg_id:
                        try:
                            await update_encounter_broadcast(interaction.guild, msg_id, "Fled", 0x7F8C8D)
                        except Exception:
                            pass
                        await self._cleanup_wilds_spawn(interaction.guild, msg_id)
                    # Edit original message embed to FLED state
                    embed = interaction.message.embeds[0]
                    file = None
                    if img_path.exists():
                        file = discord.File(img_path, filename="revomon.png")
                        embed.set_image(url="attachment://revomon.png")
                    embed.title = f"💨 The wild {name} fled! 💨"
                    embed.description = (
                        f"Oh no! The wild **{name}** broke free and "
                        f"fled into the tall grass!"
                    )
                    embed.color = 0x7F8C8D  # Grey

                    class ReturnToConsoleView(ui.View):
                        def __init__(self, spawner_id: int):
                            super().__init__(timeout=None)
                        @ui.button(label="Back to Console", style=discord.ButtonStyle.primary, emoji="🎮", custom_id=f"return_console:{spawner_id}")
                        async def return_console(self, inter: discord.Interaction, btn: ui.Button): pass

                    if file:
                        await interaction.response.edit_message(embed=embed, view=ReturnToConsoleView(spawner_id), attachments=[file])
                    else:
                        await interaction.response.edit_message(embed=embed, view=ReturnToConsoleView(spawner_id), attachments=[])

                    if msg_id:
                        await update_encounter_broadcast(interaction.guild, msg_id, "Fled", 0x7F8C8D)

                    await interaction.followup.send(
                        f"💨 **Oh no!** The wild **{name}** broke free and "
                        f"fled into the wilds!",
                        ephemeral=True,
                    )
                else:
                    orb_name = next(
                        cfg["label"]
                        for cfg in ORB_CONFIG.values()
                        if cfg["id"] == orb_id
                    )
                    await interaction.response.send_message(
                        f"☠️ **Darn!** The wild **{name}** broke free from your "
                        f"**{orb_name}**!\n"
                        f"But it didn't run away yet! You can try throwing "
                        f"another Orb.",
                        ephemeral=True,
                    )

    async def _cleanup_wilds_spawn(self, guild: discord.Guild, msg_id: int) -> None:
        try:
            from scripts.gradexDB import active_spawns_table
            await active_spawns_table.remove_spawn(msg_id)
            if guild:
                wilds_channel = discord.utils.get(guild.text_channels, name="wilds")
                if wilds_channel:
                    msg = await wilds_channel.fetch_message(msg_id)
                    await msg.delete()
        except Exception:
            pass

    async def handle_wilds_claim(self, interaction: discord.Interaction) -> None:
        custom_id = interaction.data.get("custom_id")
        parts = custom_id.split(":")
        if len(parts) < 6:
            return

        int(parts[1])
        id_revomon = int(parts[2])
        is_shiny = bool(int(parts[3]))
        int(parts[4])
        msg_id = int(parts[5])

        await interaction.response.defer()

        from scripts.gradexDB import active_spawns_table
        spawn_data = await active_spawns_table.get_spawn(msg_id)
        if not spawn_data:
            await interaction.followup.send("❌ This Revomon has already been claimed or fled!", ephemeral=True)
            return

        chosen = next((r for r in self.revomons if r.get("mon_id", r.get("idRevomon")) == id_revomon), None)
        if not chosen:
            await interaction.followup.send("❌ Error finding creature data.", ephemeral=True)
            return

        img_path = self._get_revomon_image_path(chosen, is_shiny)

        member = interaction.user
        await save_active_encounter(member.id, json.dumps(spawn_data))

        file = discord.File(img_path, filename="revomon.png") if img_path.exists() else None

        name = chosen.get("name", "Unknown").title()
        embed_color = TYPE_COLORS.get((chosen.get("type1") or "").lower(), 0x2ECC71)

        title = f"✨ A wild SHINY {name} appeared! ✨" if is_shiny else f"🌿 A wild {name} appeared! 🌿"
        embed = discord.Embed(title=title, color=embed_color)
        if file:
            embed.set_image(url="attachment://revomon.png")

        expiry_time = time.strftime("%H:%M:%S", time.gmtime(time.time() + 300))
        embed.set_footer(text=f"In battle with {member.display_name} | Expires at {expiry_time} UTC")

        view = WildSpawnView(chosen, is_shiny, member.id, msg_id)

        try:
            edit_kwargs = {"embed": embed, "view": view}
            if file:
                edit_kwargs["attachments"] = [file]
            else:
                edit_kwargs["attachments"] = []

            if interaction.message:
                await interaction.message.edit(**edit_kwargs)
            else:
                await interaction.edit_original_response(**edit_kwargs)
        except Exception as e:
            logger.error(f"Failed to update claimed spawn msg: {e}")

    async def spawn_wild_revomon(self, interaction: discord.Interaction) -> None:
        """Perform hunting rolls and dispatch wild encounter card to user.

        Args:
            interaction: The user's Discord button interaction.
        """
        await interaction.response.defer()

        if not self.revomons:
            await interaction.followup.send(
                "❌ Creature database is currently unavailable. Try again later.",
                ephemeral=True,
            )
            return

        member = interaction.user
        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.followup.send("❌ This command must be used in a server.", ephemeral=True)
            return

        current_biome = await get_guild_biome(guild_id)
        allowed_types = BIOME_TYPES.get(current_biome, {"neutral"})

        eligible = []
        for r in self.revomons:
            r_type1 = (r.get("type1") or "").lower()
            r_type2 = (r.get("type2") or "").lower()

            # Double safety: Must share a type with the Biome AND must be a first evolution stage
            if (
                (r_type1 in allowed_types or r_type2 in allowed_types)
                and r.get("name", "").lower() not in self.evolved_names
            ):
                eligible.append(r)

        if not eligible:
            await interaction.followup.send(
                "❌ No wild Revomon are available to spawn in this area.",
                ephemeral=True,
            )
            return

        chosen = random.choice(eligible)
        is_shiny = random.random() < 0.01

        img_path = self._get_revomon_image_path(chosen, is_shiny)

        name = chosen.get("name", "Unknown").title()
        embed_color = TYPE_COLORS.get((chosen.get("type1") or "").lower(), 0x2ECC71)

        title = (
            f"✨ A wild SHINY {name} appeared! ✨"
            if is_shiny
            else f"🌿 A wild {name} appeared! 🌿"
        )
        embed = discord.Embed(
            title=title,
            color=embed_color,
        )
        # Add expiration to footer
        expiry_time = time.strftime("%H:%M:%S", time.gmtime(time.time() + 300))
        embed.set_footer(text=f"This encounter expires at {expiry_time} UTC")

        # We still need rarity to pass to the broadcaster
        rarity = chosen.get("rarity", "common").title()

        # Generate Background Battle Stats
        nature = random.choice(self.natures)["name"].title() if hasattr(self, 'natures') and self.natures else "Hardy"
        abilities = []
        for k in ["ability1", "ability2", "ability_hidden"]:
            ab = chosen.get(k)
            if ab:
                abilities.append(ab.title())
        ability = random.choice(abilities) if abilities else "Unknown"
        ivs = {
            "hp": random.randint(0, 31),
            "atk": random.randint(0, 31),
            "def": random.randint(0, 31),
            "spa": random.randint(0, 31),
            "spd": random.randint(0, 31),
            "spe": random.randint(0, 31)
        }

        encounter_data = {
            "nature": nature.lower(),
            "ability": ability.lower(),
            "ivs": ivs
        }
        await save_active_encounter(member.id, json.dumps(encounter_data))

        file = None
        if img_path.exists():
            file = discord.File(img_path, filename="revomon.png")
            embed.set_image(url="attachment://revomon.png")
        else:
            embed.description = (embed.description or "") + "\n*(Image sprite not found)*"

        # We need the embed without the expiration timer for the broadcast
        broadcast_embed = embed.copy()
        broadcast_embed.set_footer(text=None)

        event_msg_id = await broadcast_encounter(
            self.bot, member, name, str(chosen.get("mon_id", chosen.get("idRevomon"))), rarity, is_shiny, broadcast_embed
        )

        view = WildSpawnView(chosen, is_shiny, member.id, event_msg_id)
        if file:
            await interaction.edit_original_response(embed=embed, view=view, attachments=[file])
        else:
            await interaction.edit_original_response(embed=embed, view=view, attachments=[])

    @tasks.loop(minutes=5)
    async def cleanup_encounters(self) -> None:
        """Periodically scan for expired wild encounter messages."""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    # Only check the last few messages to avoid excessive API calls
                    async for msg in channel.history(limit=20):
                        if msg.components:
                            for component in msg.components:
                                children = getattr(component, "children", getattr(component, "items", []))
                                for item in children:
                                    custom_id = getattr(item, "custom_id", None)
                                    if isinstance(custom_id, str) and custom_id.startswith(
                                        "spawn_"
                                    ):
                                        parts = custom_id.split(":")
                                        if len(parts) >= 5:
                                            timestamp = int(parts[4])
                                            if time.time() - timestamp > 300:
                                                await msg.delete()
                                                break
                except Exception as e:
                    logger.error(
                        "Error during encounter cleanup in channel %s: %s",
                        channel,
                        e,
                    )

async def initial_wilds_spawn(bot: commands.Bot, guild: discord.Guild) -> None:
    """Trigger the initial wild spawns after setup."""
    wilds_loop_cog = bot.get_cog("WildsLoopCog")
    if not wilds_loop_cog:
        return
    from scripts.gradexDB import get_guild_spawn_config
    config = await get_guild_spawn_config(guild.id)
    limit = config["max_spawn_limit"]
    spawn_count = limit // 3
    for _ in range(spawn_count):
        try:
            await wilds_loop_cog._do_spawn(guild)
            await asyncio.sleep(0.5)  # Rate limiting safety
        except Exception as e:
            logger.error(f"Error doing initial spawn: {e}")

async def setup(bot: commands.Bot) -> None:
    """Add the HuntingCog to the bot."""
    await bot.add_cog(HuntingCog(bot))
