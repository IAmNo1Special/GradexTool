from typing import Any
from io import BytesIO

import aiohttp
import discord
from discord import ui
from discord.ext import commands

from utils.helpers import respond
from utils.revomon_utils import appraise_revomon, create_graded_mon_img

# Define the URL for the Revomon API
REVO_API_URL = "https://api.revomon.io/revomon"


class Grade(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex

    class MonManager:
        def __init__(self) -> None:
            self.mon_info: dict[int, dict[str, Any]] = {}

    mon_manager = MonManager()

    @staticmethod
    def grade_embed() -> Any:
        embed = discord.Embed(
            title="(Eazy) : What do you need?",
            description="I have things to get done, let's make this quick.",
            color=discord.Color.from_str("#2e03fc"),
        )
        embed.set_thumbnail(
            url="https://s3.amazonaws.com/appforest_uf/f1674291486599x648341738902608500/EAZY.png"
        )
        embed.set_footer(text="Grappraisal · Global Revomon Association")
        return embed

    @staticmethod
    def mon_info_embed1(user_id: Any) -> Any:
        mon = Grade.mon_manager.mon_info[user_id]
        embed = discord.Embed(
            title=f"Revomon: {mon['mon_name'].title()}",
            description=f"**Nature:** {mon['mon_nature'].title()}\n**Ability:** {mon['mon_ability'].title()}",
            color=discord.Color.from_str("#2e03fc"),
            url=f"https://revomon.online/revodex/revomon/{mon['mon_name']}/",
        )
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text="Grappraisal · Global Revomon Association")
        return embed

    @staticmethod
    def graded_mon_embed(user_id: Any) -> Any:
        mon = Grade.mon_manager.mon_info[user_id]
        grade_image = create_graded_mon_img(mon, mon.get("grade_percent"))
        # Convert the PIL Image object to a BytesIO object
        image_bytes = BytesIO()
        grade_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        Grade.mon_manager.mon_info[user_id]["image_bytes"] = image_bytes

        embed = discord.Embed(
            title=f"Grade: {mon.get('grade_letter', '?')} ({mon.get('grade_percent', 0)}%)",
            description=f"**Role:** {mon.get('role', 'Unknown')}\n**Nature Quality:** {mon.get('nature_quality', 'Unknown')}",
            color=(
                discord.Color.green()
                if mon.get("grade_percent", 0) >= 80
                else discord.Color.orange()
            ),
            url=f"https://revomon.online/revodex/revomon/{mon['mon_name']}/",
        )

        # Breakdown of weights
        weights = mon.get("stat_weights", {})
        weight_desc = ""
        for stat, w in weights.items():
            if w >= 1.5:
                weight_desc += f"**{stat.upper()}** "
            elif w <= 0.5:
                weight_desc += f"~~{stat.upper()}~~ "
            else:
                weight_desc += f"{stat.upper()} "

        embed.add_field(name="Stat Focus", value=weight_desc, inline=False)
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text="Competitive Grade v2.0 · Global Revomon Association")
        return embed

    @staticmethod
    def grade_breakdown_embed(user_id: Any) -> Any:
        mon = Grade.mon_manager.mon_info[user_id]

        embed = discord.Embed(
            title=f"Breakdown: {mon['mon_name'].title()}",
            description=f"Analysis for **{mon.get('role', 'Unknown')}** role.",
            color=discord.Color.blue(),
            url=f"https://revomon.online/revodex/revomon/{mon['mon_name']}/",
        )

        weights = mon.get("stat_weights", {})
        ivs = {
            "HP": mon.get("hp_iv", 0),
            "ATK": mon.get("atk_iv", 0),
            "DEF": mon.get("def_iv", 0),
            "SPA": mon.get("spa_iv", 0),
            "SPD": mon.get("spd_iv", 0),
            "SPE": mon.get("spe_iv", 0),
        }

        breakdown_text = ""
        for stat, weight in weights.items():
            s_name = stat.upper()
            iv_val = ivs.get(s_name, 0)

            importance = "Average"
            if weight >= 2.0:
                importance = "**CRITICAL**"
            elif weight >= 1.5:
                importance = "High"
            elif weight <= 0.1:
                importance = "~~Ignored~~"
            elif weight <= 0.5:
                importance = "Low"

            # Special logic display
            val_str = f"{iv_val}/31"
            if s_name == "ATK" and "Special Attacker" in mon.get("role", ""):
                if iv_val <= 5:
                    val_str = f"**{iv_val} (Perfect 0-IV)**"
                else:
                    val_str = f"{iv_val} (Penalized)"

            breakdown_text += f"**{s_name}**: {val_str} — Weight: {importance}\n"

        embed.add_field(name="Stat Calculations", value=breakdown_text, inline=False)

        # Nature impact
        nq = mon.get("nature_quality", "Neutral")
        nature_text = f"Nature: **{mon['mon_nature'].title()}**\nQuality: **{nq}**"
        if nq == "Perfect":
            nature_text += "\n*+5% Bonus applied (Optimal boost/drop)*"
        elif nq == "Good":
            nature_text += "\n*+2.5% Bonus applied (Relevant boost)*"
        elif nq == "Poor":
            nature_text += "\n*-5% Penalty applied (Negative boost)*"

        embed.add_field(name="Nature Assessment", value=nature_text, inline=False)

        embed.add_field(
            name="Formula",
            value="(Sum(Transformed_IV * Weight) / Max) + Nature_Bonus",
            inline=False,
        )
        return embed

    class GradeButton(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Grade My Revomon",
            style=discord.ButtonStyle.green,
            custom_id="Grade Revomon1",
        )
        async def grade(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            try:
                await interaction.response.send_modal(Grade.MonInfoModal())
            except Exception as e:
                print(
                    f"An error occurred trying to submit the 'GradeButton[Grade My Revomon]' Button from the Grade Keyword script: {e}"
                )

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, button: discord.ui.Button[Any]
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    class MonInfoButtons1(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Grade", style=discord.ButtonStyle.green, custom_id="Grade"
        )
        async def grade(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                appr = await appraise_revomon(Grade.mon_manager.mon_info[user_id])
                if appr:
                    Grade.mon_manager.mon_info[user_id].update(appr)

                embed = Grade.graded_mon_embed(user_id=user_id)
                await interaction.response.edit_message(
                    attachments=[
                        discord.File(
                            Grade.mon_manager.mon_info[user_id]["image_bytes"],
                            filename="image.png",
                        )
                    ],
                    embed=embed,
                    view=Grade.MonInfoButtons6(),
                )
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons1[Grade]' Button from the Grade Keyword script: {e}"
                )

    class MonInfoButtons6(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Save", style=discord.ButtonStyle.green, custom_id="Save"
        )
        async def save_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                embed = Grade.graded_mon_embed(user_id=user_id)
                if interaction.guild:
                    await interaction.response.edit_message(
                        content=f"{interaction.user.mention} Your Revomon has been saved!\nCheck your DMs.",
                        view=None,
                    )
                    await interaction.user.send(
                        files=[
                            discord.File(
                                Grade.mon_manager.mon_info[user_id]["image_bytes"],
                                filename="image.png",
                            )
                        ],
                        embed=embed,
                        view=Grade.MonInfoButtons7(),
                    )
                else:
                    await interaction.response.send_message(
                        files=[
                            discord.File(
                                Grade.mon_manager.mon_info[user_id]["image_bytes"],
                                filename="image.png",
                            )
                        ],
                        embed=embed,
                        view=Grade.MonInfoButtons7(),
                    )
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons6[Save]' Button from the Grade Keyword script: {e}"
                )

        @ui.button(
            label="Flex this Revomon",
            style=discord.ButtonStyle.green,
            custom_id="Flex",
        )
        async def flex(self, interaction: discord.Interaction, Button: ui.Button[Any]) -> None:
            try:
                user_id = interaction.user.id
                await interaction.response.defer()
                embed = Grade.graded_mon_embed(user_id=user_id)
                await interaction.followup.send(
                    files=[
                        discord.File(
                            Grade.mon_manager.mon_info[user_id]["image_bytes"],
                            filename="image.png",
                        )
                    ],
                    embed=embed,
                )
                await interaction.followup.send(
                    content=f"{interaction.user.mention} Your Revomon has been flexed!",
                    ephemeral=True,
                )

            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons6[Flex This  Revomon]' Button from the grade_command script: {e}"
                )

        @ui.button(
            label="Why this grade?",
            style=discord.ButtonStyle.blurple,
            custom_id="why_this_grade",
        )
        async def why_this_grade(
            self, interaction: discord.Interaction, Button: ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                embed = Grade.grade_breakdown_embed(user_id=user_id)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons6[Why this grade?]' Button: {e}"
                )

    class MonInfoButtons7(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    class MonInfoModal(ui.Modal, title="Revomon Basic Info"):
        mon_catch_id: ui.TextInput[Any] = ui.TextInput(
            label="Revomon Catch ID",
            placeholder="1234",
            style=discord.TextStyle.short,
        )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            try:
                await interaction.response.defer(ephemeral=True, thinking=True)
                current_mon_attribs_url = f"{REVO_API_URL}/{self.mon_catch_id}"
                print(current_mon_attribs_url)
                async with aiohttp.ClientSession() as session:
                    async with session.get(current_mon_attribs_url) as response:
                        response = await response.json()
                        if response["data"] is None:
                            await interaction.followup.send(
                                "Invalid Revomon ID. Please try again.",
                                ephemeral=True,
                            )
                            return
                user_id = interaction.user.id
                Grade.mon_manager.mon_info[user_id] = {
                    "catch_id": int(str(self.mon_catch_id.value)),
                    "mon_name": str(response["data"]["catchedRevomon"]["name"]).lower(),
                    "mon_nature": str(
                        response["data"]["catchedRevomon"]["nature"]
                    ).lower(),
                    "mon_ability": str(
                        response["data"]["catchedRevomon"]["ability"]
                    ).lower(),
                    "shiny": response["data"]["catchedRevomon"]["shiny"],
                    "hp_iv": int(str(response["data"]["catchedRevomon"]["ivhp"])),
                    "atk_iv": int(str(response["data"]["catchedRevomon"]["ivatk"])),
                    "def_iv": int(str(response["data"]["catchedRevomon"]["ivdef"])),
                    "spa_iv": int(str(response["data"]["catchedRevomon"]["ivspa"])),
                    "spd_iv": int(str(response["data"]["catchedRevomon"]["ivspd"])),
                    "spe_iv": int(str(response["data"]["catchedRevomon"]["ivspe"])),
                    "hp_ev": 0,
                    "atk_ev": 0,
                    "def_ev": 0,
                    "spa_ev": 0,
                    "spd_ev": 0,
                    "spe_ev": 0,
                }

                grade_image = create_graded_mon_img(
                    Grade.mon_manager.mon_info[user_id], score_percentage=None
                )
                # Convert the PIL Image object to a BytesIO object
                image_bytes = BytesIO()
                grade_image.save(image_bytes, format="PNG")
                image_bytes.seek(0)
                Grade.mon_manager.mon_info[user_id]["image_bytes"] = image_bytes

                await interaction.response.send_message(
                    files=[
                        discord.File(
                            Grade.mon_manager.mon_info[user_id]["image_bytes"],
                            filename="image.png",
                        )
                    ],
                    embed=Grade.mon_info_embed1(user_id=user_id),
                    view=Grade.MonInfoButtons1(),
                    ephemeral=True,
                )
            except Exception as e:
                print(
                    f"An error occurred trying to submit the 'MonInfoModal' from the Grade Keyword script: {e}"
                )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        buttons = [
            self.GradeButton(),
            self.MonInfoButtons1(),
            self.MonInfoButtons6(),
            self.MonInfoButtons7(),
        ]
        for button in buttons:
            self.gradex.add_view(button)
        print("Grappraisal Mod(Grade Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if (
                prompt == "grade"
                or prompt == "appraise"
                or prompt == "admin grade"
                or prompt == "admin appraise"
            ):
                embed = Grade.grade_embed()
                buttons = self.GradeButton()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )

        except Exception as e:
            print(f"An error occurred during Grade Keyword on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Grade(gradex))
