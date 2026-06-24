import datetime
from io import BytesIO
from typing import Any

import discord.embeds
import requests
from discord import Color, Embed, File, Interaction, app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class PvpLeaderboard2(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.rankings: list[dict[str, str | int]] | None = None
        self.pvp_img: dict[str, Any] = {}

    def get_current_pvp_data(self) -> None:
        ranks = [
            "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "sixth",
            "seventh",
            "eighth",
            "ninth",
            "tenth",
            "eleventh",
            "twelfth",
            "thirteenth",
            "fourteenth",
            "fifteenth",
        ]
        current_pvp_url = "https://api.revomon.io/leaderboard/pvp_top_fifteen"
        response = requests.get(current_pvp_url)
        response = response.json()
        pvp_top_fifteen = response["data"]["pvpTopFifteen"]
        if not pvp_top_fifteen:
            self.rankings = None
            return

        rankings_data = []
        for count, _rank in enumerate(ranks):
            if pvp_top_fifteen[count] == {}:
                break
            user = pvp_top_fifteen[count]["username"]
            pvp_top_fifteen[count]["profilePicture"]
            amount = pvp_top_fifteen[count]["amount"]
            elo = pvp_top_fifteen[count]["elo"]
            current_rank = pvp_top_fifteen[count]["rank"]
            lose_count = pvp_top_fifteen[count]["loseCount"]
            win_count = pvp_top_fifteen[count]["winCount"]
            winning_percentage = (win_count / (win_count + lose_count)) * 100
            rankings_data.append(
                {
                    "Rank": current_rank,
                    "Name": user,
                    "Elo": elo,
                    "Wins": win_count,
                    "Losses": lose_count,
                    "Winning": f"{winning_percentage:.2f}%",
                    "Reward": f"{amount} REVO",
                }
            )

        self.rankings = rankings_data

    def update_pvp_image(self, data: list[dict[str, str | int]] | None, output_path: None=None) -> None:
        img_width, cell_height = 1050, 50
        header_height = 40
        total_height = header_height + 15 * cell_height
        img = Image.new("RGB", (img_width, total_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        try:
            font: Any = ImageFont.truetype("data/fonts/Cabal.ttf", 16)
        except Exception as e:
            print(f"Error loading font during update_pvp_image: {e}")
            font = ImageFont.load_default()

        headers = ["Rank", "Name", "Elo", "Wins", "Losses", "Winning", "Reward"]
        draw.rectangle([0, 0, img_width, header_height], fill=(0, 0, 0))
        for i, header in enumerate(headers):
            draw.text(
                (i * img_width // len(headers) + 10, 10),
                header,
                font=font,
                fill=(255, 255, 255),
            )

        if data is None:
            no_data_font = ImageFont.truetype("data/fonts/Cabal.ttf", 16)
            message = "The ranking is not available at the moment, it will be available when more PvP games have been played."
            bbox = draw.textbbox((0, 0), message, font=no_data_font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                (
                    (img_width - text_width) / 2,
                    (total_height - text_height) / 2,
                ),
                message,
                font=no_data_font,
                fill=(255, 255, 255),
            )
        else:
            colors = {
                1: (214, 178, 36),
                2: (192, 192, 192),
                3: (205, 127, 50),
                "default": (60, 60, 60),
            }

            for idx, row in enumerate(data):
                y0 = header_height + idx * cell_height
                y1 = y0 + cell_height
                rank = row["Rank"]

                bg_color = colors.get(rank, colors["default"])
                draw.rectangle([0, y0, img_width, y1], fill=bg_color)

                for i, col in enumerate(headers):
                    draw.text(
                        (i * img_width // len(headers) + 10, y0 + 10),
                        str(row[col]),
                        font=font,
                        fill=(255, 255, 255),
                    )

        try:
            self.pvp_img["image_bytes"] = BytesIO()
            img.save(self.pvp_img["image_bytes"], format="PNG")
            self.pvp_img["image_bytes"].seek(0)
            self.pvp_img["image_bytes"].name = "current_pvp_image.png"
        except Exception as e:
            print(f"Error converting PIL image during update_pvp_image: {e}")

    def current_pvp_embed(self) -> discord.embeds.Embed:
        embed = Embed(
            title=None,
            description=None,
            color=Color.from_str("#2e03fc"),
            timestamp=datetime.datetime.now(),
        )
        embed.set_image(url="attachment://current_pvp_image.png")
        embed.set_footer(text="Global Revomon Association")
        return embed

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # buttons = []
        # for button in buttons:
        #     self.gradex.add_view(button)
        print("Revomon Mod(PvP Leaderboard Command) is ready!")
        print("---------------------------")

    @app_commands.command(name="pvp", description="Display the Podium leaderboards.")
    @app_commands.allowed_installs(guilds=True, users=True)
    async def pvp(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            self.get_current_pvp_data()
        except Exception as e:
            print(f"Error during pvp_command(get_current_pvp_data): {e}")
        try:
            self.update_pvp_image(self.rankings)
        except Exception as e:
            print(f"Error during pvp_command(update_pvp_image): {e}")
        try:
            curr_pvp_embed = self.current_pvp_embed()
        except Exception as e:
            print(f"Error during pvp_command(current_pvp_embed): {e}")

        file = File(self.pvp_img["image_bytes"], filename="current_pvp_image.png")
        await interaction.followup.send(embed=curr_pvp_embed, file=file, ephemeral=True)

        # Close the BytesIO object after sending
        self.pvp_img["image_bytes"].close()
        del self.pvp_img["image_bytes"]


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(PvpLeaderboard2(gradex))
