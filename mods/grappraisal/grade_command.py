from io import BytesIO
from typing import Any

import aiohttp
from discord import (
    ButtonStyle,
    Color,
    Embed,
    File,
    Interaction,
    app_commands,
    ui,
)
from discord.ext import commands

from utils.revomon_utils import appraise_revomon, create_graded_mon_img

# Define the URL for the Revomon API
REVO_API_URL = "https://api.revomon.io/revomon"


class GradeCommand(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex

    class MonManager:
        def __init__(self) -> None:
            self.mon_info: dict[str | int, Any] = {}

    mon_manager = MonManager()

    def mon_info_embed1(self, user_id: Any) -> Any:
        mon = GradeCommand.mon_manager.mon_info[user_id]
        embed = Embed(
            title=f"Revomon: {mon['mon_name'].title()}",
            description=f"**Nature:** {mon['mon_nature'].title()}\n**Ability:** {mon['mon_ability'].title()}",
            color=Color.from_str("#2e03fc"),
            url=f"https://revomon.online/revodex/revomon/{mon['mon_name']}/",
        )
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text="Grappraisal · Global Revomon Association")
        return embed

    def graded_mon_embed(self, user_id: Any) -> Any:
        mon = GradeCommand.mon_manager.mon_info[user_id]
        grade_image = create_graded_mon_img(mon, mon["grade_percent"])
        # Convert the PIL Image object to a BytesIO object
        image_bytes = BytesIO()
        grade_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        GradeCommand.mon_manager.mon_info[user_id]["image_bytes"] = image_bytes

        embed = Embed(
            title=f"Grade: {mon['grade_letter']} ({mon['grade_percent']}%)",
            description=f"**Role:** {mon['role']}\n**Nature Quality:** {mon['nature_quality']}",
            color=Color.green() if mon["grade_percent"] >= 80 else Color.orange(),
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

    def grade_breakdown_embed(self, user_id: Any) -> Any:
        mon = GradeCommand.mon_manager.mon_info[user_id]

        embed = Embed(
            title=f"Breakdown: {mon['mon_name'].title()}",
            description=f"Analysis for **{mon['role']}** role.",
            color=Color.blue(),
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
            if s_name == "ATK" and "Special Attacker" in mon["role"]:
                if iv_val <= 5:
                    val_str = f"**{iv_val} (Perfect 0-IV)**"
                else:
                    val_str = f"{iv_val} (Penalized)"

            breakdown_text += f"**{s_name}**: {val_str} — Weight: {importance}\n"

        embed.add_field(name="Stat Calculations", value=breakdown_text, inline=False)

        # Nature impact
        nature_text = f"Nature: **{mon['mon_nature'].title()}**\nQuality: **{mon['nature_quality']}**"
        if mon["nature_quality"] == "Perfect":
            nature_text += "\n*+5% Bonus applied (Optimal boost/drop)*"
        elif mon["nature_quality"] == "Good":
            nature_text += "\n*+2.5% Bonus applied (Relevant boost)*"
        elif mon["nature_quality"] == "Poor":
            nature_text += "\n*-5% Penalty applied (Negative boost)*"

        embed.add_field(name="Nature Assessment", value=nature_text, inline=False)

        embed.add_field(
            name="Formula",
            value="(Sum(Transformed_IV * Weight) / Max) + Nature_Bonus",
            inline=False,
        )
        return embed

    class MonInfoButtons1(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @ui.button(label="Grade", style=ButtonStyle.green, custom_id="grade_button")
        async def grade_button(
            self, interaction: Interaction, button: ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                message_id = interaction.message.id  # type: ignore[union-attr]
                await interaction.response.defer()
                await interaction.followup.edit_message(
                    message_id=message_id,
                    content="Grading your Revomon...",
                    embed=None,
                    attachments=[],
                    view=None,
                )
                appr = await appraise_revomon(
                    GradeCommand.mon_manager.mon_info[user_id]
                )
                if appr:
                    GradeCommand.mon_manager.mon_info[user_id].update(appr)

                embed = GradeCommand.graded_mon_embed(self, user_id=user_id)  # type: ignore[arg-type]
                await interaction.followup.edit_message(
                    message_id=message_id,
                    content=None,
                    attachments=[
                        File(
                            GradeCommand.mon_manager.mon_info[user_id]["image_bytes"],
                            filename="image.png",
                        )
                    ],
                    embed=embed,
                    view=GradeCommand.MonInfoButtons6(),
                )
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons1[Grade]' Button from the grade_command script: {e}"
                )

    class ExitMessageButton(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @ui.button(label="❌", style=ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: Interaction, button: ui.Button[Any]
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    class MonInfoButtons6(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @ui.button(label="Save", style=ButtonStyle.green, custom_id="Save")
        async def save_embed(
            self, interaction: Interaction, button: ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                await interaction.response.defer()
                embed = GradeCommand.graded_mon_embed(self, user_id=user_id)  # type: ignore[arg-type]
                if interaction.guild:
                    await interaction.followup.send(
                        content=f"{interaction.user.mention} Your Revomon has been saved!\nCheck your DMs.",
                        ephemeral=True,
                    )
                    await interaction.user.send(
                        files=[
                            File(
                                GradeCommand.mon_manager.mon_info[user_id][
                                    "image_bytes"
                                ],
                                filename="image.png",
                            )
                        ],
                        embed=embed,
                        view=GradeCommand.ExitMessageButton(),
                    )
                else:
                    await interaction.followup.send(
                        files=[
                            File(
                                GradeCommand.mon_manager.mon_info[user_id][
                                    "image_bytes"
                                ],
                                filename="image.png",
                            )
                        ],
                        embed=embed,
                        view=GradeCommand.ExitMessageButton(),
                    )
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons6[Save]' Button from the grade_command script: {e}"
                )

        @ui.button(label="Flex this Revomon", style=ButtonStyle.green, custom_id="Flex")
        async def flex(self, interaction: Interaction, button: ui.Button[Any]) -> None:
            try:
                user_id = interaction.user.id
                await interaction.response.defer()
                embed = GradeCommand.graded_mon_embed(self, user_id=user_id)  # type: ignore[arg-type]
                await interaction.followup.send(
                    files=[
                        File(
                            GradeCommand.mon_manager.mon_info[user_id]["image_bytes"],
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
            style=ButtonStyle.blurple,
            custom_id="why_this_grade",
        )
        async def why_this_grade(
            self, interaction: Interaction, button: ui.Button[Any]
        ) -> None:
            try:
                user_id = interaction.user.id
                embed = GradeCommand.grade_breakdown_embed(self, user_id=user_id)  # type: ignore[arg-type]
                # Respond with a new ephemeral message instead of editing
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'MonInfoButtons6[Why this grade?]' Button: {e}"
                )

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        buttons = [
            self.MonInfoButtons1(),
            self.MonInfoButtons6(),
            self.ExitMessageButton(),
        ]
        for button in buttons:
            self.gradex.add_view(button)
        print("Grappraisal Mod(Grade Command) is ready!")
        print("---------------------------")

    @app_commands.command(name="grade", description="Grade a Revomon")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(catch_id="The Catch ID of the Revomon")
    async def grade(self, interaction: Interaction, catch_id: int) -> None:
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            current_mon_attribs_url = f"{REVO_API_URL}/{catch_id}"
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
                    GradeCommand.mon_manager.mon_info[user_id] = {
                        "catch_id": int(catch_id),
                        "mon_name": str(
                            response["data"]["catchedRevomon"]["name"]
                        ).lower(),
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
                GradeCommand.mon_manager.mon_info[user_id],
                score_percentage=None,
            )
            # Convert the PIL Image object to a BytesIO object
            image_bytes = BytesIO()
            grade_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)
            GradeCommand.mon_manager.mon_info[user_id]["image_bytes"] = image_bytes

            await interaction.followup.send(
                files=[File(image_bytes, filename="image.png")],
                embed=GradeCommand.mon_info_embed1(self, user_id=user_id),
                view=GradeCommand.MonInfoButtons1(),
                ephemeral=True,
            )
        except Exception as e:
            print(
                f"An error occurred trying to submit the 'grade' command from the grade_command script: {e}"
            )


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(GradeCommand(gradex))
