"""Cog for enforcing workspace layouts and preventing channel tampering."""

import logging

import discord
from discord.ext import commands

logger = logging.getLogger("discord_bot")


class EnforcementCog(commands.Cog):
    """Cog to automatically snap channels back into their designated categories."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the EnforcementCog.

        Args:
            bot: The Discord bot instance.
        """
        from mods.revocord.shared import normalize_channel_name

        self.bot = bot
        self.category_name = "RevoCord"

        # Build protected channels and track their expected position
        self.protected_channels: dict[str, type[discord.abc.GuildChannel]] = {}
        self.expected_positions: dict[str, int] = {}

        core_channels = ["news", "event-board", "portal", "wilds"]
        for index, name in enumerate(core_channels):
            safe_name = normalize_channel_name(name)
            self.expected_positions[safe_name] = index
            self.protected_channels[safe_name] = discord.TextChannel

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Automatically delete system 'pin' notifications sent by the bot."""
        # Check if the message is a system "pinned" notification
        if message.type == discord.MessageType.pins_add:
            if not (
                hasattr(message.channel, "category")
                and message.channel.category
                and message.channel.category.name == self.category_name
            ):
                return
            try:
                await message.delete()
                logger.info("Deleted pin notification.")
            except discord.Forbidden:
                logger.error(
                    "Permissions failure: Cannot delete pin notification. Bot needs 'Manage Channels'."
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error during pin notification deletion: {e}",
                    exc_info=True,
                )

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        """Monitor channel updates and enforce category confinement."""
        # Fast-fail if the channel name isn't one we are actively protecting
        if after.name not in self.protected_channels:
            return

        # Verify the channel type matches our protection profile
        expected_type = self.protected_channels[after.name]
        if not isinstance(after, expected_type):
            return

        # Attempt to locate the anchor category in the server cache
        protected_category = discord.utils.get(
            after.guild.categories, name=self.category_name
        )
        if not protected_category:
            # If the category is gone, we can't enforce confinement.
            # We don't log a warning here to avoid spamming when the category is intentionally deleted.
            return

        # If the channel's parent category ID has drifted, drag it back
        expected_pos = self.expected_positions.get(after.name, 0)
        if after.category_id != protected_category.id:
            try:
                await after.edit(  # type: ignore[attr-defined]
                    category=protected_category,
                    position=expected_pos,
                    sync_permissions=False,
                    reason="RevoCord Enforcement: Channel movement restricted.",
                )
                logger.info(
                    f"Enforced layout restriction: Relocated '{after.name}' back under '{self.category_name}' at position {expected_pos}."
                )
            except discord.Forbidden:
                logger.error(
                    f"Permissions failure: Cannot lock '{after.name}'. Bot needs 'Manage Channels'."
                )
            except discord.HTTPException as e:
                if e.code == 50035 and "parent_id: Category does not exist" in str(e):
                    # Ignore this error during category deletion race conditions
                    pass
                else:
                    logger.error(f"HTTP error during channel enforcement: {e}")
            except Exception as e:
                logger.error(
                    f"Unexpected error during channel enforcement: {e}",
                    exc_info=True,
                )

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        """Monitor for the deletion of the protected category and clean up sub-channels."""
        # We only care if the channel being deleted is our specific category
        if not isinstance(channel, discord.CategoryChannel):
            return

        if channel.name != self.category_name:
            return

        logger.info(
            f"Protected category '{self.category_name}' was deleted. Cleaning up orphaned channels..."
        )

        # When a category is deleted, children are orphaned (category is None).
        # We iterate through the guild's channels and delete any protected channel that is now orphaned.
        for guild_channel in channel.guild.channels:
            # Only target channels that are in our protected list
            if guild_channel.name in self.protected_channels:
                # If the channel is now orphaned, it should be deleted
                if guild_channel.category_id is None:
                    try:
                        await guild_channel.delete(
                            reason="RevoCord Cleanup: Category was deleted."
                        )
                        logger.info(f"Deleted orphaned channel: {guild_channel.name}")
                    except discord.Forbidden:
                        logger.error(
                            f"Failed to delete {guild_channel.name}: Missing 'Manage Channels' permission."
                        )
                    except discord.HTTPException as e:
                        logger.error(f"Error deleting {guild_channel.name}: {e}")

        # Wipe out guild configurations from DB to avoid tracking ghost data
        try:
            from scripts.gradexDB import delete_guild_data

            await delete_guild_data(channel.guild.id)
            logger.info(
                f"Wiped guild data for {channel.guild.id} after category deletion."
            )
        except Exception as e:
            logger.error(f"Error wiping guild data on category delete: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Triggered when the bot leaves or is kicked from a server."""
        try:
            from scripts.gradexDB import delete_guild_data

            await delete_guild_data(guild.id)
            logger.info(
                f"Wiped guild data for {guild.id} after bot was removed from server."
            )
        except Exception as e:
            logger.error(f"Error wiping guild data on guild remove: {e}")


async def setup(bot: commands.Bot) -> None:
    """Set up the EnforcementCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(EnforcementCog(bot))
        logger.info("EnforcementCog loaded successfully.")
    except Exception as e:
        logger.error('ERROR in EnforcementCog "setup" function: %s', e)
