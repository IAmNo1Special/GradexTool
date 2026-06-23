import math
import discord
from discord import ui
from utils.revomon_utils import get_attributes

def build_tv_embed(member: discord.Member, total_caught: int, current_page: int, total_pages: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"📺 {member.display_name.upper()}'S TV",
        description=f"Browsing **{total_caught}** caught Revomon in storage.\n━━━━━━━━━━━━━━━━━━━━",
        color=0x3498db
    )
    embed.set_footer(text=f"Page {current_page + 1} of {max(1, total_pages)}")
    return embed

async def build_stat_embed(mon: dict, attrs: dict | None) -> discord.Embed:
    name = mon.get("name", "Unknown").title()
    is_shiny = mon.get("is_shiny", False)
    level = mon.get("level", 1)
    xp = mon.get("xp", 0)
    nature = mon.get("nature", "Hardy").title()
    ability = mon.get("ability", "Unknown").title()
    ivs = mon.get("ivs", {})
    iv_pct = mon.get("iv_percent", 0.0)
    rc_id = mon.get("rc_id", "???")
    
    shiny_str = "✨ SHINY " if is_shiny else ""
    
    embed = discord.Embed(
        title=f"{shiny_str}{name} (Lv. {level})",
        color=0xF1C40F if is_shiny else 0x3498db
    )
    
    embed.add_field(name="Experience", value=f"{xp} XP", inline=True)
    embed.add_field(name="Nature", value=nature, inline=True)
    embed.add_field(name="Ability", value=ability, inline=True)
    
    ivs_table = (
        f"```yaml\n"
        f"HP : {ivs.get('hp', 0):<2} | SPA: {ivs.get('spa', 0):<2}\n"
        f"ATK: {ivs.get('atk', 0):<2} | SPD: {ivs.get('spd', 0):<2}\n"
        f"DEF: {ivs.get('def', 0):<2} | SPE: {ivs.get('spe', 0):<2}\n\n"
        f"Total: {sum(ivs.values())}/186 ({iv_pct}%)\n"
        f"```"
    )
    embed.add_field(name=" ", value=ivs_table, inline=False)
    embed.set_footer(text=f"RC-ID: #{rc_id}")
    
    if attrs:
        dex_id = attrs.get("num")
        if dex_id:
            img_url = f"https://nft.revomon.io/image/raw/revomon/{dex_id}_shiny.png" if is_shiny else f"https://nft.revomon.io/image/raw/revomon/{dex_id}.png"
            embed.set_thumbnail(url=img_url)
            
    return embed

class TVStatView(ui.View):
    def __init__(self, spawner_id: int, caught_list: list, current_page: int):
        super().__init__(timeout=None)
        self.spawner_id = spawner_id
        self.caught_list = caught_list
        self.current_page = current_page

    @ui.button(label="Back to TV", style=discord.ButtonStyle.primary, emoji="📺", custom_id="tv_back")
    async def back_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        if interaction.user.id != self.spawner_id:
            await interaction.response.send_message("❌ This is not your TV!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        total_caught = len(self.caught_list)
        total_pages = math.ceil(total_caught / 20)
        
        embed = build_tv_embed(interaction.user, total_caught, self.current_page, total_pages)
        view = TVView(interaction.client, self.spawner_id, self.caught_list, self.current_page)
        await view.build_buttons()
        await interaction.edit_original_response(embed=embed, view=view, attachments=[])

class TVView(ui.View):
    def __init__(self, bot: discord.Client, spawner_id: int, caught_list: list, current_page: int = 0):
        super().__init__(timeout=None)
        self.bot = bot
        self.spawner_id = spawner_id
        self.caught_list = caught_list
        self.current_page = current_page
        
    async def build_buttons(self):
        # Sort newest first as requested (chronological by captured_at descending)
        sorted_list = sorted(self.caught_list, key=lambda x: x.get("captured_at", 0), reverse=True)
        
        start_idx = self.current_page * 20
        page_items = sorted_list[start_idx:start_idx + 20]
        
        if not hasattr(self.bot, "_app_emojis_cache"):
            self.bot._app_emojis_cache = await self.bot.fetch_application_emojis()
            
        app_emojis = self.bot._app_emojis_cache
        
        for i, mon in enumerate(page_items):
            name = mon.get("name", "unknown").replace(" ", "_").replace("-", "_")
            is_shiny = mon.get("is_shiny", False)
            
            emoji_name = f"{name}_shiny" if is_shiny else name
            
            # Scrape live emoji cache directly from Discord Client and Application Emojis
            emoji_obj = discord.utils.get(app_emojis, name=emoji_name) or discord.utils.get(self.bot.emojis, name=emoji_name)
            
            self.add_item(RevomonTVButton(self.bot, self.spawner_id, self.caught_list, self.current_page, mon, i, emoji_obj))
            
        self.add_item(TVNavButton("first", "⏮️", "First", self.bot, self.spawner_id, sorted_list, self.current_page))
        self.add_item(TVNavButton("prev", "⏪", "Prev", self.bot, self.spawner_id, sorted_list, self.current_page))
        self.add_item(TVNavButton("close", "❌", "Close", self.bot, self.spawner_id, sorted_list, self.current_page))
        self.add_item(TVNavButton("next", "⏩", "Next", self.bot, self.spawner_id, sorted_list, self.current_page))
        self.add_item(TVNavButton("last", "⏭️", "Last", self.bot, self.spawner_id, sorted_list, self.current_page))

class RevomonTVButton(ui.Button):
    def __init__(self, bot: discord.Client, spawner_id: int, caught_list: list, current_page: int, mon: dict, index: int, emoji_obj: discord.Emoji | None):
        self.bot = bot
        self.spawner_id = spawner_id
        self.caught_list = caught_list
        self.current_page = current_page
        self.mon = mon
        
        rc_id = mon.get("rc_id", 0)
        label = f"#{rc_id}"
        
        super().__init__(
            style=discord.ButtonStyle.secondary, 
            label=label,
            emoji=emoji_obj if emoji_obj else ("✨" if mon.get("is_shiny") else "🐉"),
            custom_id=f"tv_mon_{current_page}_{index}"
        )
        
    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.spawner_id:
            await interaction.response.send_message("❌ This is not your TV!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        name = self.mon.get("name", "unknown")
        try:
            attrs = await get_attributes(name)
        except Exception:
            attrs = None
            
        embed = await build_stat_embed(self.mon, attrs)
        view = TVStatView(self.spawner_id, self.caught_list, self.current_page)
            
        await interaction.edit_original_response(embed=embed, view=view, attachments=[])

class TVNavButton(ui.Button):
    def __init__(self, action: str, emoji: str, label: str, bot: discord.Client, spawner_id: int, sorted_list: list, current_page: int):
        self.action = action
        self.bot = bot
        self.spawner_id = spawner_id
        self.sorted_list = sorted_list
        self.current_page = current_page
        
        super().__init__(
            style=discord.ButtonStyle.danger if action == "close" else discord.ButtonStyle.primary,
            label=label,
            emoji=emoji,
            row=4,
            custom_id=f"tv_nav_{action}"
        )
        
    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.spawner_id:
            await interaction.response.send_message("❌ This is not your TV!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        total_pages = max(1, math.ceil(len(self.sorted_list) / 20))
        new_page = self.current_page
        
        if self.action == "close":
            from mods.revocord.shared import get_or_create_account
            from mods.revocord.portal import build_console_embed, GameConsoleView
            account = await get_or_create_account(self.spawner_id)
            embed = await build_console_embed(account, interaction.user)
            await interaction.edit_original_response(embed=embed, view=GameConsoleView(self.spawner_id), attachments=[])
            return
            
        elif self.action == "first":
            new_page = 0
        elif self.action == "last":
            new_page = max(0, total_pages - 1)
        elif self.action == "next":
            new_page = min(total_pages - 1, self.current_page + 1)
        elif self.action == "prev":
            new_page = max(0, self.current_page - 1)
            
        if new_page != self.current_page:
            embed = build_tv_embed(interaction.user, len(self.sorted_list), new_page, total_pages)
            view = TVView(self.bot, self.spawner_id, self.sorted_list, new_page)
            await view.build_buttons()
            await interaction.edit_original_response(embed=embed, view=view, attachments=[])
