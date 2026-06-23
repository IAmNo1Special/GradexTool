"""Cog for Portal session gateway login and ephemeral console deployment."""

import logging
import discord
from discord import ui
from discord.ext import commands

from mods.revocord.shared import (
    get_or_create_account,
    update_account,
)

logger = logging.getLogger("discord_bot")

async def build_console_embed(account: dict, member: discord.Member) -> discord.Embed:
    """Builds the ephemeral dashboard UI based on player data."""
    level = account.get("trainer_level", 1)
    xp = account.get("trainer_xp", 25)
    coins = account.get("coins", 500)
    rank = account.get("rank", "Rookie")
    energy = account.get("energy", 100)
    max_energy = account.get("max_energy", 100)
    city = account.get("current_city", "drassius city").title()

    # Visual XP Bar
    xp_percent = min(100, max(0, xp))
    filled_blocks = int(xp_percent / 10)
    xp_bar = "█" * filled_blocks + "░" * (10 - filled_blocks)

    # Visual Energy Bar
    energy_percent = min(100, max(0, int((energy / max_energy) * 100)))
    filled_energy = int(energy_percent / 10)
    energy_bar = "█" * filled_energy + "░" * (10 - filled_energy)

    embed = discord.Embed(
        title=f"🎮 {member.display_name.upper()}'S CONSOLE",
        description=f"**📍 Location:** {city}\n━━━━━━━━━━━━━━━━━━━━",
        color=0x2b2d31,
    )
    embed.add_field(name="Level & Rank", value=f"🏅 {rank} (Lv. {level})", inline=True)
    embed.add_field(name="Wealth", value=f"🪙 {coins} Coins", inline=True)
    embed.add_field(
        name="Stats",
        value=f"**XP:** {xp_bar} {xp_percent}%\n**NRG:** {energy_bar} {energy}/{max_energy}",
        inline=False,
    )
    
    # Inventory quick look
    inventory = account.get("inventory", {})
    red_count = inventory.get("159", 0)
    blue_count = inventory.get("4", 0)
    green_count = inventory.get("31", 0)
    
    inventory_parts = []
    if red_count > 0: inventory_parts.append(f"🔴 Red x{red_count}")
    if blue_count > 0: inventory_parts.append(f"🔵 Blue x{blue_count}")
    if green_count > 0: inventory_parts.append(f"🟢 Green x{green_count}")
    
    inventory_str = ", ".join(inventory_parts) if inventory_parts else "*No Orbs owned*"
    embed.add_field(name="Bag (Quick Look)", value=inventory_str, inline=False)
    
    return embed


class GameConsoleView(ui.View):
    """The interactive buttons attached to the ephemeral game console."""
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(label="Bag", style=discord.ButtonStyle.secondary, emoji="🎒", custom_id="console_bag")
    async def bag(self, interaction: discord.Interaction, button: ui.Button) -> None:
        await interaction.response.defer()

    @ui.button(label="Heal", style=discord.ButtonStyle.danger, emoji="🏥", custom_id="console_heal")
    async def heal(self, interaction: discord.Interaction, button: ui.Button) -> None:
        await interaction.response.defer()

    @ui.button(label="TV", style=discord.ButtonStyle.primary, emoji="📺", custom_id="console_tv")
    async def tv(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You cannot access someone else's Console!", ephemeral=True)
            return
            
        await interaction.response.defer()
        from mods.revocord.shared import get_or_create_account
        from mods.revocord.tv import TVView, build_tv_embed
        import math
        
        account = await get_or_create_account(self.user_id)
        caught_list = account.get("caught_revomon", [])
        
        total_caught = len(caught_list)
        total_pages = max(1, math.ceil(total_caught / 20))
        
        embed = build_tv_embed(interaction.user, total_caught, 0, total_pages)
        view = TVView(interaction.client, self.user_id, caught_list, 0)
        await view.build_buttons()
        await interaction.edit_original_response(embed=embed, view=view, attachments=[])


class PortalLoginView(ui.View):
    """View for the persistent portal login button."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @ui.button(
        label="Log In",
        style=discord.ButtonStyle.success,
        custom_id="persistent_portal_login",
        emoji="🎮"
    )
    async def login(self, interaction: discord.Interaction, button: ui.Button) -> None:
        """Handle the login button click."""
        await interaction.response.defer(ephemeral=True)

        member = interaction.user
        if not isinstance(member, discord.Member):
            return

        try:
            account = await get_or_create_account(member.id)
            # Mark them as logged in
            account = await update_account(member.id, is_logged_in=True)

            embed = await build_console_embed(account, member)
            view = GameConsoleView(member.id)

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            logger.info(f"Deployed ephemeral console for {member.name}")

        except Exception as e:
            logger.error(f"Error deploying console: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error initializing console: {e}", ephemeral=True)


class PortalCog(commands.Cog):
    """Cog for managing portal session gateway views."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        """Register persistent views."""
        self.bot.add_view(PortalLoginView())

async def setup(bot: commands.Bot) -> None:
    try:
        await bot.add_cog(PortalCog(bot))
        logger.info("PortalCog loaded successfully.")
    except Exception as e:
        logger.error('ERROR in PortalCog "setup" function: %s', e)
