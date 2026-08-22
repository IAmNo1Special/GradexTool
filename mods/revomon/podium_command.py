import datetime
from io import BytesIO
from typing import Any

import discord.embeds
from discord import Color, Embed, File, Interaction, app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.http import fetch_json


class Podium2(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.rankings: dict[str, dict[str, str]] = {}
        self.weekly_podium_img: dict[str, Any] = {}
        self.current_podium_img: dict[str, Any] = {}

    def convert_time(self, total_seconds: int) -> str:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        return formatted_time

    async def get_weekly_podium_data(self) -> dict[str, dict[str, str]]:
        weekly_podium_url = "https://api.revomon.io/leaderboard/weekly_podium"
        response = await fetch_json(weekly_podium_url)
        if not response:
            raise ValueError("Weekly podium leaderboard unavailable")
        weekly_podium = response["data"]["weeklyPodium"]
        if len(weekly_podium) < 3:
            self.rankings = {}
            return self.rankings

        def entry(idx: int) -> dict[str, str]:
            slot = weekly_podium[idx]
            return {
                "user": slot["username"],
                "img": slot["profilePicture"],
                "time": self.convert_time(slot["times"]),
            }

        self.rankings = {
            "first": entry(0),
            "second": entry(1),
            "third": entry(2),
        }
        return self.rankings

    async def get_current_podium_data(self) -> dict[str, dict[str, str]]:
        current_podium_url = "https://api.revomon.io/leaderboard/current_podium"
        response = await fetch_json(current_podium_url)
        if not response:
            raise ValueError("Current podium leaderboard unavailable")
        current_podium = response["data"]["currentPodium"]
        if len(current_podium) < 3:
            self.rankings = {}
            return self.rankings

        def entry(idx: int) -> dict[str, str]:
            slot = current_podium[idx]
            return {
                "user": slot["username"],
                "img": slot["profilePicture"],
            }

        self.rankings = {
            "first": entry(0),
            "second": entry(1),
            "third": entry(2),
        }
        return self.rankings

    def get_text_size(self, draw: Any, text: str, font: Any) -> tuple[int, int]:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    async def podium_img(self, podium_type: str) -> None:
        # Define the image size and background color
        image_width, image_height = 800, 450
        background_color = (36, 36, 36)  # Dark background

        # Define positions, sizes, and colors for the podium
        header_height = 25
        positions = [
            (image_width // 4 - 50, image_height // 2 + header_height // 2),
            (image_width // 2, image_height // 3 + header_height // 2),
            (3 * image_width // 4 + 50, image_height // 2 + header_height // 2),
        ]
        circle_radius = 100
        circle_colors = ["grey", "grey", "grey"]  # Colors for 1st, 2nd, 3rd
        text_colors = ["#ffffff", "#ffffff", "#ffffff"]  # Text colors for names
        if podium_type == "weekly":
            rankings = await self.get_weekly_podium_data()
            times = [
                rankings["second"]["time"],
                rankings["first"]["time"],
                rankings["third"]["time"],
            ]  # Text to display under usernames
        else:
            rankings = await self.get_current_podium_data()
        podium_ranks = ["2", "1", "3"]
        usernames = [
            rankings["second"]["user"],
            rankings["first"]["user"],
            rankings["third"]["user"],
        ]

        # Load fonts
        font_path = "data/fonts/Cabal.ttf"  # Ensure this font file is in the same directory or provide the correct path
        font_large = ImageFont.truetype(font_path, 24)
        font_small = ImageFont.truetype(font_path, 18)
        font_header = ImageFont.truetype(font_path, 20)

        # Create a new image
        new_image = Image.new("RGB", (image_width, image_height), background_color)
        draw = ImageDraw.Draw(new_image)

        # Draw the header text
        header_text = "In-Game Podium" if podium_type == "current" else "Weekly Podium"
        header_width, header_height = self.get_text_size(draw, header_text, font_header)
        header_x = (image_width - header_width) // 16
        header_y = 5  # Padding from the top
        draw.text((header_x, header_y), header_text, font=font_header, fill="#ffffff")

        # Draw a line below the header text
        line_y = header_y + header_height + 20
        draw.line((0, line_y, image_width, line_y), fill="#ffffff", width=2)

        # Draw circles and text for each podium position
        for i, pos in enumerate(positions):
            # Draw the circle
            draw.ellipse(
                (
                    pos[0] - circle_radius,
                    pos[1] - circle_radius + line_y,
                    pos[0] + circle_radius,
                    pos[1] + circle_radius + line_y,
                ),
                fill=circle_colors[i],
            )

            # Draw the rank number inside the circle
            rank_text = podium_ranks[i]
            rank_width, rank_height = self.get_text_size(draw, rank_text, font_large)
            rank_x = pos[0] - rank_width // 2
            rank_y = pos[1] - rank_height // 2 + line_y
            draw.text(
                (rank_x, rank_y),
                rank_text,
                font=font_large,
                fill=text_colors[i],
            )

            # Draw the username below the circle
            username = usernames[i]
            username_width, username_height = self.get_text_size(
                draw, username, font_small
            )
            username_x = pos[0] - username_width // 2
            username_y = pos[1] + circle_radius + 10 + line_y
            draw.text(
                (username_x, username_y),
                username,
                font=font_small,
                fill=text_colors[i],
            )

            if podium_type == "weekly":
                # Draw additional text below the username
                time_width, time_height = self.get_text_size(draw, times[i], font_small)
                time_x = pos[0] - time_width // 2
                time_y = username_y + username_height + 5
                draw.text((time_x, time_y), times[i], font=font_small, fill="#cccccc")

        if podium_type == "weekly":
            # Convert the PIL Image object to a BytesIO object
            self.weekly_podium_img["image_bytes"] = BytesIO()
            new_image.save(self.weekly_podium_img["image_bytes"], format="PNG")
            self.weekly_podium_img["image_bytes"].seek(0)
        elif podium_type == "current":
            # Convert the PIL Image object to a BytesIO object
            self.current_podium_img["image_bytes"] = BytesIO()
            new_image.save(self.current_podium_img["image_bytes"], format="PNG")
            self.current_podium_img["image_bytes"].seek(0)

    async def current_podium_embed(self) -> discord.embeds.Embed:
        await self.podium_img(podium_type="current")
        embed = Embed(
            title=None,
            description=None,
            color=Color.from_str("#2e03fc"),
            timestamp=datetime.datetime.now(),
        )
        embed.set_image(url="attachment://current_podium_image.png")
        embed.set_footer(text="Global Revomon Association")
        return embed

    async def weekly_podium_embed(self) -> discord.embeds.Embed:
        await self.podium_img(podium_type="weekly")
        embed = Embed(
            title=None,
            description=None,
            color=Color.from_str("#2e03fc"),
            timestamp=datetime.datetime.now(),
        )
        embed.set_image(url="attachment://weekly_podium_image.png")
        embed.set_footer(text="Global Revomon Association")
        return embed

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # buttons = []
        # for button in buttons:
        #   self.gradex.add_view(button)
        print("Revomon Mod(Podium Leaderboard Command) is ready!")
        print("---------------------------")

    @app_commands.command(name="podium", description="Display the Podium leaderboards.")
    @app_commands.allowed_installs(guilds=True, users=True)
    async def podium(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        self.weekly_podium_img = {}
        self.current_podium_img = {}
        try:
            curr_podium_embed = await self.current_podium_embed()
            file = File(
                self.current_podium_img["image_bytes"],
                filename="current_podium_image.png",
            )
            await interaction.followup.send(
                embed=curr_podium_embed, file=file, ephemeral=True
            )

            # Close the BytesIO object after sending
            self.current_podium_img["image_bytes"].close()
            del self.current_podium_img["image_bytes"]

            week_podium_embed = await self.weekly_podium_embed()
            file = File(
                self.weekly_podium_img["image_bytes"],
                filename="weekly_podium_image.png",
            )
            await interaction.followup.send(
                embed=week_podium_embed, file=file, ephemeral=True
            )

            # Close the BytesIO object after sending
            self.weekly_podium_img["image_bytes"].close()
            del self.weekly_podium_img["image_bytes"]

        except Exception as e:
            print(f"AN ERROR OCCURRED -> podium_command(Podium2.podium): {e}")
            try:
                await interaction.followup.send(
                    "Podium leaderboard data is unavailable right now. Please try again later.",
                    ephemeral=True,
                )
            except Exception:
                pass


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Podium2(gradex))
