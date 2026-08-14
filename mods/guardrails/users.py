"""Gradex Tool Guardrails for managing users."""

import logging

from discord import Interaction, Member, Message, app_commands, utils
from discord.ext import commands

from configs import GRA_GUILD_ID
from utils.helpers import user_check

logger = logging.getLogger(__name__)


class UsersGuardrail(commands.Cog):
    """Users guardrail for managing users."""

    def __init__(self, gradex_tool: commands.Bot) -> None:
        """Initialize the UsersGuardrail.

        Args:
            gradex_tool: The GradexTool bot instance.
        """
        self.gradex_tool = gradex_tool
        self.cog_name = "UsersGuardrail"

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"{self.cog_name} is ready!")
        logger.info("-" * 50)

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Called when a message is sent.

        Args:
            message: The message that was sent.
        """
        # Ignore messages from bots (including self)
        if message.author.bot:
            return
        try:
            logger.info(f"Running user check for {message.author}")
            await user_check(gradex_tool=self.gradex_tool, user=message.author)  # type: ignore[arg-type]
        except Exception as e:
            logger.error(f"An error occurred during main(on_message): {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Called when a member joins a guild.

        Args:
            member: The member that joined.
        """
        logger.info(f"User {member.name} joined the {member.guild.name} server!")
        logger.info("-" * 50)
        if GRA_GUILD_ID is None:
            logger.error("GRA_GUILD_ID not found in environment variables!")
            return
        if member.guild.id == GRA_GUILD_ID:
            role_name = "Fresh Spawn"
            role = utils.get(member.guild.roles, name=role_name)
            if role:
                await member.add_roles(role)
                logger.info(f"Added role {role_name} to {member.name}!")
            else:
                logger.warning(f"Role {role_name} not found!")

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: Interaction,
        command: app_commands.Command,  # type: ignore[type-arg]
    ) -> None:
        """Called when an app command is completed.

        Args:
            interaction: The interaction that triggered the command.
            command: The command that was executed.
        """
        logger.info(
            f"Command '{command.name}' was executed by {interaction.user.name} in {interaction.guild.name} (ID: {interaction.guild.id})"  # type: ignore[union-attr]
        )
        try:
            await user_check(gradex_tool=interaction.client, user=interaction.user)  # type: ignore[arg-type]
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
