"""Utility for broadcasting notable events to the public event board."""

import logging
import time

import discord
from discord.ext import commands

from data import EventBoardLogsTable

logger = logging.getLogger("discord_bot")


async def broadcast_encounter(
    bot: commands.Bot,
    user: discord.Member,
    mon_name: str,
    mon_id: str,
    rarity: str,
    is_shiny: bool,
    embed: discord.Embed,
) -> int:
    """Broadcasts a notable encounter to the #event-board.

    Returns the message_id of the broadcasted event, or 0 if failed/skipped.
    """
    # 1. Check if rarity meets threshold
    notable_rarities = ["Rare", "Epic", "Legendary", "Shiny"]

    if rarity not in notable_rarities and not is_shiny:
        return 0

    # 2. Find the #event-board channel
    event_board = discord.utils.get(user.guild.channels, name="event-board")
    if not event_board or not isinstance(event_board, discord.TextChannel):
        logger.warning("Event board channel not found during broadcast.")
        return 0

    try:
        # Create a broadcast embed wrapping the encounter
        shiny_tag = "✨ SHINY " if is_shiny else ""
        broadcast_embed = discord.Embed(
            title="🚨 WILD ENCOUNTER ALARM!",
            description=f"**{user.display_name}** has just encountered a wild {shiny_tag}**{mon_name.title()}**!",
            color=0xFFAA00 if is_shiny else 0xFF0000,
        )
        broadcast_embed.set_thumbnail(url=user.display_avatar.url)

        # Extract attributes from the passed-in encounter card
        for field in embed.fields:
            if field.name in ["Ability", "Nature", "IVs"]:
                broadcast_embed.add_field(
                    name=field.name, value=field.value, inline=field.inline
                )

        # Extract RC-ID from the footer
        footer_text = embed.footer.text if embed.footer and embed.footer.text else ""
        if footer_text:
            broadcast_embed.set_footer(text=footer_text)

        msg = await event_board.send(embed=broadcast_embed)

        # 3. Log to database
        db_table = EventBoardLogsTable()
        async with db_table._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                INSERT INTO event_board_logs (message_id, user_id, revomon_id, is_shiny, outcome, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    msg.id,
                    user.id,
                    int(mon_id),
                    1 if is_shiny else 0,
                    "Battling",
                    int(time.time()),
                ),
            )
            await conn.commit()

        return msg.id

    except Exception as e:
        logger.error(f"Failed to broadcast encounter: {e}", exc_info=True)
        return 0


async def update_encounter_broadcast(
    guild: discord.Guild, event_msg_id: int, outcome: str, color: int
) -> None:
    """Updates the public event board message with the outcome (Caught/Fled/Ran)."""
    if not event_msg_id:
        return

    event_board = discord.utils.get(guild.channels, name="event-board")
    if not event_board or not isinstance(event_board, discord.TextChannel):
        return

    try:
        msg = await event_board.fetch_message(event_msg_id)
        if not msg or not msg.embeds:
            return

        embed = msg.embeds[0]
        # Update embed to reflect outcome
        embed.title = "📢 ENCOUNTER RESOLVED"

        desc = embed.description or ""
        if outcome == "Caught":
            embed.description = desc + "\n\n✅ **OUTCOME:** Captured successfully!"
        elif outcome == "Fled":
            embed.description = (
                desc + "\n\n💨 **OUTCOME:** The Revomon broke free and fled!"
            )
        elif outcome == "Ran":
            embed.description = desc + "\n\n🏃 **OUTCOME:** The trainer ran away!"

        embed.color = color

        await msg.edit(embed=embed)

        # Update database
        db_table = EventBoardLogsTable()
        async with db_table._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "UPDATE event_board_logs SET outcome = ? WHERE message_id = ?",
                (outcome, event_msg_id),
            )
            await conn.commit()

    except discord.NotFound:
        pass
    except Exception as e:
        logger.error(f"Failed to update broadcast encounter {event_msg_id}: {e}")
