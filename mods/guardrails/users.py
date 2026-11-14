"""Gradex Tool Guardrails for managing users."""

import logging
from typing import Any, cast

from discord import Interaction, Member, app_commands, utils
from discord.ext import commands, tasks

from configs import GRA_GUILD_ID
from utils.helpers import user_check

logger = logging.getLogger(__name__)

FRESH_SPAWN_ROLE_NAME = "Fresh Spawn"
# How often the Fresh Spawn sweep runs. New members wait at most this long
# for the role when the on_member_join event cannot fire.
FRESH_SPAWN_SWEEP_MINUTES = 30


class UsersGuardrail(commands.Cog):
    """Users guardrail for managing users."""

    def __init__(self, gradex_tool: commands.Bot) -> None:
        """Initialize the UsersGuardrail.

        Args:
            gradex_tool: The GradexTool bot instance.
        """
        self.gradex_tool = gradex_tool
        self.cog_name = "UsersGuardrail"

    async def cog_load(self) -> None:
        """Start the Fresh Spawn sweep once the bot is ready."""
        self.fresh_spawn_sweep.start()

    async def cog_unload(self) -> None:
        """Stop the Fresh Spawn sweep."""
        self.fresh_spawn_sweep.cancel()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"{self.cog_name} is ready!")
        logger.info("-" * 50)

    # NOTE (2026-10-11): the on_message user_check was removed with the
    # message_content intent. Guardrail coverage is preserved: every slash
    # command now triggers on_app_command_completion -> user_check below.

    async def _assign_fresh_spawn(self, member: Member) -> bool:
        """Give one member the Fresh Spawn role if they do not have it yet.

        Args:
            member: The member to give the role to.

        Returns:
            True if the role was assigned, False otherwise.
        """
        role = utils.get(member.guild.roles, name=FRESH_SPAWN_ROLE_NAME)
        if role is None:
            logger.warning(f"Role {FRESH_SPAWN_ROLE_NAME} not found!")
            return False
        if role in member.roles:
            return False
        await member.add_roles(role)
        logger.info(f"Added role {FRESH_SPAWN_ROLE_NAME} to {member.name}!")
        return True

    @tasks.loop(minutes=FRESH_SPAWN_SWEEP_MINUTES)
    async def fresh_spawn_sweep(self) -> None:
        """Assign the Fresh Spawn role to members who are missing it.

        This is the backfill for on_member_join, which cannot fire while the
        bot runs without the privileged `members` intent (removed 2026-10-09).
        It uses the REST member list, so it works on default intents. Members
        who joined while the event was dead get the role here instead, at
        most one sweep interval after joining.
        """
        if GRA_GUILD_ID is None:
            logger.error("GRA_GUILD_ID not found in environment variables!")
            return
        guild = self.gradex_tool.get_guild(GRA_GUILD_ID)
        if guild is None:
            try:
                guild = await self.gradex_tool.fetch_guild(GRA_GUILD_ID)
            except Exception as e:
                logger.error(
                    f"Could not fetch guild {GRA_GUILD_ID} for Fresh Spawn sweep: {e}"
                )
                return
        role = utils.get(guild.roles, name=FRESH_SPAWN_ROLE_NAME)
        if role is None:
            logger.warning(f"Role {FRESH_SPAWN_ROLE_NAME} not found!")
            return
        assigned = 0
        try:
            async for member in guild.fetch_members(limit=None):
                if member.bot or role in member.roles:
                    continue
                try:
                    await member.add_roles(role)
                    assigned += 1
                except Exception as e:
                    logger.error(
                        f"Failed to add Fresh Spawn role to {member.name}: {e}"
                    )
        except Exception as e:
            logger.error(f"Fresh Spawn sweep failed: {e}")
            return
        if assigned:
            logger.info(f"Fresh Spawn sweep assigned the role to {assigned} member(s).")

    @fresh_spawn_sweep.before_loop
    async def before_fresh_spawn_sweep(self) -> None:
        await self.gradex_tool.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Called when a member joins a guild.

        Args:
            member: The member that joined.
        """
        # NOTE (2026-10-11): INERT while the bot runs without the privileged
        # `members` intent, which Discord removed on 2026-10-09 (missed review
        # window). It will NOT fire until the intent is re-approved in the
        # Developer Portal. Kept as the fast path for when that happens; the
        # fresh_spawn_sweep above covers every join until then.
        logger.info(f"User {member.name} joined the {member.guild.name} server!")
        logger.info("-" * 50)
        if GRA_GUILD_ID is None:
            logger.error("GRA_GUILD_ID not found in environment variables!")
            return
        if member.guild.id == GRA_GUILD_ID:
            await self._assign_fresh_spawn(member)

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: Interaction,
        command: app_commands.Command[Any, Any, Any],
    ) -> None:
        """Called when an app command is completed.

        Args:
            interaction: The interaction that triggered the command.
            command: The command that was executed.
        """
        guild = interaction.guild
        if guild is None:
            logger.info(
                f"Command '{command.name}' was executed by {interaction.user.name} in DMs"
            )
        else:
            logger.info(
                f"Command '{command.name}' was executed by {interaction.user.name} in {guild.name} (ID: {guild.id})"
            )
        try:
            await user_check(
                gradex_tool=cast(commands.Bot, interaction.client),
                user=cast(Member, interaction.user),
            )
        except Exception as e:
            logger.error(
                f"An error occurred during {self.cog_name}(on_app_command_completion): {e}"
            )


async def setup(gradex_tool: commands.Bot) -> None:
    """Set up the UsersGuardrail cog.

    Args:
        gradex_tool: The GradexTool bot instance.
    """
    cog = UsersGuardrail(gradex_tool)
    logger.info(f"Loading {cog.cog_name} Cog...")
    try:
        await gradex_tool.add_cog(cog)
        logger.info(f"Successfully loaded {cog.cog_name}")
    except Exception as e:
        logger.error(f"Error loading {cog.cog_name}: {e}")
