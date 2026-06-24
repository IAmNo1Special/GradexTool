from typing import Any

"""Cog for managing interactive thread activities and persistent views."""

import logging  # noqa: E402

import discord  # noqa: E402
from discord import ui  # noqa: E402
from discord.ext import commands  # noqa: E402

from mods.revocord.shared import get_or_create_account, update_account  # noqa: E402

logger = logging.getLogger("discord_bot")


class TravelButtonView(ui.View):
    """Persistent view for the Travel and Hunt buttons in Wilds threads."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @ui.button(
        label="Hunt Wild Revomon",
        style=discord.ButtonStyle.success,
        emoji="🌿",
        custom_id="persistent_hunt_button",
    )
    async def hunt(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        """Hunt a wild Revomon in the current city wilds."""
        await interaction.response.defer()

        client: Any = interaction.client
        cog = client.get_cog("HuntingCog")
        if not cog:
            await interaction.followup.send(
                "❌ Hunting system is currently unavailable. Try again later.",
                ephemeral=True,
            )
            return

        await cog.spawn_wild_revomon(interaction)




class ShopSelect(ui.Select[Any]):
    """Dropdown for purchasing Orbs in the RevoCenter."""

    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Red Orb",
                value="159",
                description="Catch multiplier: 1.0x (Cost: 200 RevoCoins)",
                emoji="🔴",
            ),
            discord.SelectOption(
                label="Blue Orb",
                value="4",
                description="Catch multiplier: 1.5x (Cost: 600 RevoCoins)",
                emoji="🔵",
            ),
            discord.SelectOption(
                label="Green Orb",
                value="31",
                description="Catch multiplier: 2.0x (Cost: 800 RevoCoins)",
                emoji="🟢",
            ),
        ]
        super().__init__(
            placeholder="Select an Orb to buy...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Handle the orb purchase selection."""
        await interaction.response.defer(ephemeral=True)
        orb_id = self.values[0]
        member = interaction.user

        # Get orb details
        orb_details = {
            "159": {"name": "Red Orb", "cost": 200},
            "4": {"name": "Blue Orb", "cost": 600},
            "31": {"name": "Green Orb", "cost": 800},
        }
        details = orb_details.get(orb_id)
        if not details:
            await interaction.followup.send("❌ Invalid selection.", ephemeral=True)
            return

        cost = details["cost"]
        name = details["name"]

        account = await get_or_create_account(member.id)
        coins = account.get("coins", 0)

        if coins < cost:
            await interaction.followup.send(
                f"❌ You do not have enough RevoCoins to buy a **{name}**!\n"
                f"Required: `{cost}` | Current: `{coins}`",
                ephemeral=True,
            )
            return

        # Deduct coins and update inventory
        new_coins = coins - cost
        inventory = account.get("inventory", {})
        inventory[orb_id] = inventory.get(orb_id, 0) + 1

        await update_account(member.id, coins=new_coins, inventory=inventory)

        await interaction.followup.send(
            f"🛒 Success! Purchased 1x **{name}** for `{cost}` RevoCoins!\n"
            f"Remaining balance: `{new_coins}` RevoCoins.",
            ephemeral=True,
        )


class ShopSelectView(ui.View):
    """View wrapping the ShopSelect dropdown menu."""

    def __init__(self) -> None:
        super().__init__(timeout=180)
        self.add_item(ShopSelect())


class RestButtonView(ui.View):
    """Persistent view for RevoCenter. Contains Rest and Buy Orbs buttons."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @ui.button(
        label="Rest",
        style=discord.ButtonStyle.success,
        emoji="💤",
        custom_id="persistent_rest_button",
    )
    async def rest(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        """Fully restore the player's energy."""
        await interaction.response.defer(ephemeral=True)
        member = interaction.user
        account = await get_or_create_account(member.id)

        max_energy = account.get("max_energy", 100)
        current_energy = account.get("energy", 100)

        if current_energy >= max_energy:
            await interaction.followup.send(
                "You are already fully rested!", ephemeral=True
            )
            return

        await update_account(member.id, energy=max_energy)
        await interaction.followup.send(
            f"💤 You rested and restored your energy to **{max_energy}**!",
            ephemeral=True,
        )

    @ui.button(
        label="Buy Orbs",
        style=discord.ButtonStyle.primary,
        emoji="🛒",
        custom_id="persistent_shop_button",
    )
    async def shop(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        """Open the RevoCenter Orb shop."""
        member = interaction.user
        account = await get_or_create_account(member.id)
        coins = account.get("coins", 0)

        embed = discord.Embed(
            title="🛒 RevoCenter Shop - Purchase Orbs",
            description=(
                f"Welcome to the RevoCenter shop, **{member.display_name}**!\n"
                f"Spend your RevoCoins on Orbs to catch wild Revomon.\n\n"
                f"🪙 **Your Balance:** `{coins}` RevoCoins\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x1ABC9C,
        )

        view = ShopSelectView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class RouteAITrainerView(ui.View):
    """Persistent view for AI Trainers on Routes. Contains Battle and Travel buttons."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @ui.button(
        label="Battle",
        style=discord.ButtonStyle.danger,
        emoji="⚔️",
        custom_id="persistent_battle_button",
    )
    async def battle(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        """Handle the AI trainer battle click."""
        await interaction.response.send_message(
            "The Battle system is not yet implemented! 🚧", ephemeral=True
        )




class ActivityCog(commands.Cog):
    """Cog for managing interactive thread panels and views."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the ActivityCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot

    async def cog_load(self) -> None:
        """Register persistent views."""
        self.bot.add_view(TravelButtonView())
        self.bot.add_view(RestButtonView())
        self.bot.add_view(RouteAITrainerView())


async def setup(bot: commands.Bot) -> None:
    """Add the ActivityCog to the bot."""
    await bot.add_cog(ActivityCog(bot))
