"""Utility functions for the Gradex Tool."""

import discord
from discord.ext import commands

from configs import GRA_GUILD_ID, PRO_TAMER_ROLE_IDS
from data.gradexDB import UsersTable


def is_pro_tamer(gradex_tool: commands.Bot, user: discord.Member):
    gra_guild = gradex_tool.get_guild(GRA_GUILD_ID)
    if gra_guild is None:
        return False
    gra_member = gra_guild.get_member(user.id)
    if gra_member is None:
        return False
    user_roles = [role.id for role in gra_member.roles]
    return any(role in PRO_TAMER_ROLE_IDS for role in user_roles)


async def user_check(gradex_tool: commands.Bot, user: discord.Member):
    # If message is from an existing user, check if their membership status needs to be updated
    users_data = UsersTable()
    current_user = users_data.get_user(user_id=user.id)
    is_pro_status = 1 if is_pro_tamer(gradex_tool=gradex_tool, user=user) else 0
    if current_user:
        if current_user[4] != is_pro_status:
            # update existing user's membership status
            users_data.update_user(user_id=current_user[0], is_pro=is_pro_status)
            print("Existing User Updated!")
            return
    else:
        # Otherwise, set the new user's membership status and add them to the Gradex Tool members db.
        users_data.add_user(
            user_id=user.id,
            username=user.name,
            wallet_connected=0,
            wallet_address=None,
            is_pro=is_pro_status,
            is_certified=0,
            experience_points=0,
            battle_points=0,
            victory_points=0,
            wins=0,
            losses=0,
            draws=0,
        )
        print("New User Added!")


async def respond(
    gradex_tool: commands.Bot,
    message: discord.Message = None,
    embed: discord.Embed = None,
    buttons: discord.ui.View = None,
    file=None,
):
    if not message.guild:
        if is_pro_tamer(gradex_tool=gradex_tool, user=message.author):
            await message.author.send(embed=embed, view=buttons, file=file)
        else:
            reply_message = f"{message.author.mention}\nYou must be a Pro or Pro+ Tamer to use your Gradex Tool from your DMs"
            reply_message = await message.author.send(content=reply_message)
            await reply_message.delete(delay=10)
    elif message.guild:
        await message.delete()
        await message.author.send(embed=embed, view=buttons, file=file)
