from typing import Any

"""Setup cog for configuring the RevoCord workspace."""

import asyncio  # noqa: E402
import logging  # noqa: E402

import discord  # noqa: E402
from discord import app_commands  # noqa: E402
from discord.ext import commands  # noqa: E402

from mods.revocord.portal import PortalLoginView  # noqa: E402
from mods.revocord.shared import (  # noqa: E402
    build_text_view,
    is_server_owner,
    normalize_channel_name,
)
from scripts.gradexDB import set_guild_biome  # noqa: E402

logger = logging.getLogger("discord_bot")

class BiomeSelect(discord.ui.Select):
    def __init__(self, setup_cog: "SetupCog", user: discord.Member, guild: discord.Guild):
        self.setup_cog = setup_cog
        self.user = user
        self.guild = guild
        options = [
            discord.SelectOption(label="Forest", description="Bug, Grass, Neutral", emoji="🌳"),
            discord.SelectOption(label="Jungle", description="Forest, Bug, Toxic", emoji="🌴"),
            discord.SelectOption(label="Plains", description="Neutral, Battle, Sky", emoji="🌾"),
            discord.SelectOption(label="Tundra", description="Ice, Spirit", emoji="❄️"),
            discord.SelectOption(label="Caves", description="Stone, Earth, Metal", emoji="🪨"),
            discord.SelectOption(label="Beach", description="Water, Sky", emoji="🏖️"),
            discord.SelectOption(label="Crater", description="Fire, Stone, Draconic", emoji="🌋"),
            discord.SelectOption(label="Swamp", description="Toxic, Phantom, Water", emoji="🐊"),
            discord.SelectOption(label="Desert", description="Earth, Fire, Time", emoji="🏜️"),
            discord.SelectOption(label="Urban", description="Electric, Metal, Twilight", emoji="🏙️"),
            discord.SelectOption(label="Underwater", description="Water, Ice", emoji="🌊"),
        ]
        super().__init__(placeholder="Select the Biome for your Server...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        biome = self.values[0]
        await set_guild_biome(self.guild.id, biome)
        await interaction.edit_original_response(content=f"🌍 Server Biome locked to **{biome}**! Building RevoCord...", view=None)
        await self.setup_cog.execute_setup(interaction, self.user, self.guild)

class BiomeSelectView(discord.ui.View):
    def __init__(self, setup_cog: "SetupCog", user: discord.Member, guild: discord.Guild):
        super().__init__(timeout=300)
        self.add_item(BiomeSelect(setup_cog, user, guild))


class SetupCog(commands.Cog):
    """Cog for setting up the bot workspace."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the SetupCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot

    @app_commands.command(name="setup", description="Set up the bot's workspace.")
    @is_server_owner()
    async def setup_command(self, interaction: discord.Interaction) -> Any:
        """Create or locate the revocord category and channels.

        Args:
            interaction: The Discord interaction.
        """
        await interaction.response.defer(ephemeral=True)

        bot_permissions = interaction.app_permissions
        missing_permissions = False
        if not bot_permissions.manage_roles:
            await interaction.followup.send(
                f"❌ API Error: My global permissions are missing the 'Manage Roles' permission. "
                f"Current: Roles={bot_permissions.manage_roles}",
                ephemeral=True,
            )
            missing_permissions = True
        if not bot_permissions.manage_channels:
            await interaction.followup.send(
                f"❌ API Error: My global permissions are missing the 'Manage Channels' permission. "
                f"Current: Channels={bot_permissions.manage_channels}",
                ephemeral=True,
            )
            missing_permissions = True
        if not bot_permissions.manage_messages:
            await interaction.followup.send(
                f"❌ API Error: My global permissions are missing the 'Manage Messages' permission. "
                f"Current: Messages={bot_permissions.manage_messages}",
                ephemeral=True,
            )
            missing_permissions = True
        if missing_permissions:
            return

        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.followup.send("This command must be used by a server member.", ephemeral=True)
            return

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command must be used in a server.")
            return

        view = BiomeSelectView(self, user, guild)
        await interaction.followup.send("Please select a Biome for this server:", view=view, ephemeral=True)

    async def execute_setup(self, interaction: discord.Interaction, user: discord.Member, guild: discord.Guild) -> None:
        permission_overwrites: dict[discord.Role | discord.Member | discord.Object, discord.PermissionOverwrite] = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=True,
                view_channel=True,
                send_messages=False,
                add_reactions=False,
            ),
            user: discord.PermissionOverwrite(
                read_messages=True,
                view_channel=True,
                send_messages=False,
                add_reactions=False,
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                view_channel=True,
                send_messages=True,
                embed_links=True,
                attach_files=True,
                manage_messages=True,  # Needed for pinning
            ),
        }

        try:
            # 1. Check if the category already exists (Check cache first)
            category_name = "RevoCord"
            revocord_category = discord.utils.get(guild.categories, name=category_name)

            # API Fallback: If cache hasn't updated yet, fetch all channels directly
            if not revocord_category:
                all_channels = await guild.fetch_channels()
                for channel in all_channels:
                    # Categories are fetched as CategoryChannel objects
                    if (
                        isinstance(channel, discord.CategoryChannel)
                        and channel.name == category_name
                    ):
                        revocord_category = channel
                        logger.info(
                            f"Found existing category via active fetch: {category_name}"
                        )
                        break

            # Create it only if it TRULY doesn't exist anywhere
            if not revocord_category:
                revocord_category = await guild.create_category(
                    name=category_name, overwrites=permission_overwrites
                )
                logger.info(f"Created brand new category: {category_name}")
            else:
                # Sync privacy constraints if the category already existed
                await revocord_category.edit(overwrites=permission_overwrites)
                logger.info(f"Category located: {category_name}")

            # 2. Ensure Core Channels (News, Event Board, Portal, Wilds)
            core_channels = ["news", "event-board", "portal", "wilds"]

            async def ensure_text_channel(name: str, position: int) -> tuple[Any, bool]:
                normalized_name = normalize_channel_name(name)
                text_channel = discord.utils.get(guild.channels, name=normalized_name)
                is_new = False
                if not text_channel:
                    all_channels = await guild.fetch_channels()
                    for channel in all_channels:
                        if isinstance(channel, discord.TextChannel) and channel.name == normalized_name:
                            text_channel = channel
                            break
                if not text_channel:
                    text_channel = await guild.create_text_channel(
                        name=name,
                        category=revocord_category,
                        overwrites=permission_overwrites,
                        position=position,
                    )
                    is_new = True
                    await asyncio.sleep(0.25)
                    logger.info(f"Created brand new core channel: {name}")
                else:
                    if text_channel.position != position:
                        await text_channel.edit(position=position)
                    await text_channel.edit(category=revocord_category)
                    for target, overwrite in permission_overwrites.items():
                        await text_channel.set_permissions(target, overwrite=overwrite)
                    logger.info(f"Core channel synced: {normalized_name}")
                return text_channel, is_new

            # Create the 4 core channels
            portal_channel = None
            wilds_channel_new = False
            for idx, ch_name in enumerate(core_channels):
                ch, is_new = await ensure_text_channel(ch_name, idx)
                if ch_name == "portal":
                    portal_channel = ch
                elif ch_name == "wilds":
                    wilds_channel_new = is_new

            trigger_initial_spawn = wilds_channel_new
            if not trigger_initial_spawn:
                from scripts.gradexDB import active_spawns_table
                current_spawns = await active_spawns_table.count_guild_spawns(guild.id)
                if current_spawns == 0:
                    trigger_initial_spawn = True

            if trigger_initial_spawn:
                try:
                    from mods.revocord.hunting import initial_wilds_spawn
                    self.bot.loop.create_task(initial_wilds_spawn(self.bot, guild))
                except Exception as e:
                    logger.error(f"Failed to run initial wilds spawn: {e}")

            if not portal_channel:
                raise Exception("Portal channel failed to generate.")

            # 3. Handle Portal Message dispatching
            portal_message = None
            async for message in portal_channel.history(limit=10, oldest_first=True):
                if message.author == self.bot.user:
                    portal_message = message
                    break

            if not portal_message:
                portal_view = PortalLoginView()
                portal_message = await portal_channel.send(
                    content="# 🎮 RevoCord Portal\nClick the button below to summon your personal Ephemeral Game Console and begin your adventure!",
                    view=portal_view,
                )
                await portal_message.pin()
                logger.info("Dispatched and pinned permanent portal login button.")
            else:
                logger.info("Portal login message already exists.")

            # Ensure portal is visible to @everyone so they can click the button
            portal_overwrites = discord.PermissionOverwrite(
                view_channel=True, send_messages=False
            )
            await portal_channel.set_permissions(
                guild.default_role, overwrite=portal_overwrites
            )
            logger.info("Set portal channel to be visible to @everyone.")

            response_view = build_text_view(f"RevoCord System fully deployed! Portal is at <#{portal_channel.id}>")
            await interaction.followup.send(view=response_view, ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have the required permissions to manage channels or permissions.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error("Error during setup: %s", e, exc_info=True)
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    @setup_command.error
    async def setup_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Catch permission errors if a non-owner attempts execution."""
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ Only the absolute server owner can run this application setup utility.",
                ephemeral=True,
            )
        else:
            logger.error(f"Unhandled error in setup command: {error}", exc_info=True)


async def setup(bot: commands.Bot) -> None:
    """Set up the SetupCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(SetupCog(bot))
        logger.info("SetupCog loaded successfully.")
    except Exception as e:
        logger.error('ERROR in SetupCog "setup" function: %s', e)
