from typing import Any

"""Cog for Player Dashboard and character profile interface."""

import logging  # noqa: E402

import discord  # noqa: E402
from discord import ui  # noqa: E402
from discord.ext import commands  # noqa: E402

from mods.revocord.shared import (  # noqa: E402
    build_text_view,
    get_or_create_account,
    update_account,
)

logger = logging.getLogger("discord_bot")


class DashboardView(ui.View):
    """View for the dashboard text channel. Contains Profile and Logout buttons."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @ui.button(
        label="Character Profile",
        style=discord.ButtonStyle.primary,
        custom_id="persistent_dashboard_profile",
        emoji="👤",
    )
    async def profile(
        self, interaction: discord.Interaction, button: ui.Button[Any]
    ) -> None:
        """Display the user's character profile."""
        await interaction.response.defer(ephemeral=True)
        member = interaction.user

        try:
            account = await get_or_create_account(member.id)

            # Format the profile card beautifully
            level = account.get("trainer_level", 1)
            xp = account.get("trainer_xp", 25)
            coins = account.get("coins", 500)
            rank = account.get("rank", "Rookie")
            energy = account.get("energy", 100)
            max_energy = account.get("max_energy", 100)
            city = account.get("current_city", "drassius city").title()
            location = account.get("current_location", "revocenter").title()
            won = account.get("battles_won", 0)
            lost = account.get("battles_lost", 0)

            # Visual XP Bar
            xp_percent = min(100, max(0, xp))
            filled_blocks = int(xp_percent / 10)
            xp_bar = "█" * filled_blocks + "░" * (10 - filled_blocks)

            # Visual Energy Bar
            energy_percent = min(100, max(0, int((energy / max_energy) * 100)))
            filled_energy = int(energy_percent / 10)
            energy_bar = "█" * filled_energy + "░" * (10 - filled_energy)

            # Format Inventory
            inventory = account.get("inventory", {})
            red_count = inventory.get("159", 0)
            blue_count = inventory.get("4", 0)
            green_count = inventory.get("31", 0)

            inventory_parts = []
            if red_count > 0:
                inventory_parts.append(f"🔴 Red x{red_count}")
            if blue_count > 0:
                inventory_parts.append(f"🔵 Blue x{blue_count}")
            if green_count > 0:
                inventory_parts.append(f"🟢 Green x{green_count}")

            if inventory_parts:
                inventory_str = ", ".join(inventory_parts)
            else:
                inventory_str = "*No Orbs owned*"

            # Format Caught Roster
            caught = account.get("caught_revomon", [])
            roster_lines = []
            for c in caught[:6]:  # Limit to 6 for clean visual size
                c_name = c.get("name", "Unknown").title()
                c_level = c.get("level", 1)
                shiny_pref = "✨ " if c.get("is_shiny") else ""
                roster_lines.append(f"- {shiny_pref}{c_name} (Lv. {c_level})")

            if len(caught) > 6:
                roster_lines.append(f"*...and {len(caught) - 6} more*")

            if roster_lines:
                roster_str = "\n".join(roster_lines)
            else:
                roster_str = "*No captured Revomon yet*"

            profile_text = (
                f"### 👤 **TRAINER PROFILE: {member.display_name.upper()}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏅 **Rank:** `{rank}`\n"
                f"⭐️ **Level:** `{level}` | **XP:** `[{xp_bar}] {xp_percent}%`\n"
                f"🪙 **Coins:** `{coins}` RevoCoins\n"
                f"⚡ **Energy:** `[{energy_bar}] {energy}/{max_energy}`\n"
                f"🎒 **Orbs:** {inventory_str}\n"
                f"⚔️ **Battle Record:** `{won}` Won / `{lost}` Lost\n"
                f"📍 **Current Location:** `{city}` ({location})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🐉 **CAUGHT REVOMON ROSTER:**\n"
                f"{roster_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            view = build_text_view(profile_text, accent_color=0x3498DB)
            await interaction.followup.send(view=view, ephemeral=True)

        except Exception as e:
            logger.error(f"Error showing character profile: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ An error occurred loading your profile: {e}",
                ephemeral=True,
            )

    @ui.button(
        label="Log Out",
        style=discord.ButtonStyle.danger,
        custom_id="persistent_dashboard_logout",
        emoji="🚪",
    )
    async def logout(
        self, interaction: discord.Interaction, button: ui.Button[Any]
    ) -> None:
        """Handle the dashboard logout button click."""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        member = interaction.user

        if (
            not isinstance(member, discord.Member)
            or not isinstance(channel, discord.abc.GuildChannel)
            or not channel.category
        ):
            await interaction.followup.send(
                "❌ Error: Workspace structure not found.", ephemeral=True
            )
            return

        try:
            # Update state
            await update_account(member.id, is_logged_in=False)

            category = channel.category

            # Adjust permissions
            portal_name = "portal"
            for chan in category.channels:
                if chan.name == portal_name:
                    # Show portal
                    await chan.set_permissions(member, overwrite=None)
                else:
                    # Hide all other channels (cities AND dashboard)
                    await chan.set_permissions(member, overwrite=None)

            await interaction.followup.send(
                "✅ You have successfully logged out. You can return via the portal.",
                ephemeral=True,
            )
            logger.info(f"User {member.name} logged out of RevoCord.")

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Error: I don't have permissions to update your access.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error during dashboard logout: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ An unexpected error occurred: {e}", ephemeral=True
            )


class DashboardCog(commands.Cog):
    """Cog for managing dashboard views."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize DashboardCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot

    async def cog_load(self) -> None:
        """Register persistent views."""
        self.bot.add_view(DashboardView())


async def setup(bot: commands.Bot) -> None:
    """Set up the DashboardCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(DashboardCog(bot))
        logger.info("DashboardCog loaded successfully.")
    except Exception as e:
        logger.error('ERROR in DashboardCog "setup" function: %s', e)
