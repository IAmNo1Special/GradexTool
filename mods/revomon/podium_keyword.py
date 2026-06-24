import asyncio
import datetime
import random
from io import BytesIO
from typing import Any

import discord
import requests
from discord.embeds import Embed
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.helpers import respond


class Podium(commands.Cog):
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

    def get_weekly_podium_data(self) -> dict[str, dict[str, str]]:
        weekly_podium_url = "https://api.revomon.io/leaderboard/weekly_podium"
        response = requests.get(weekly_podium_url)
        response = response.json()
        first_user = response["data"]["weeklyPodium"][0]["username"]
        first_img = response["data"]["weeklyPodium"][0]["profilePicture"]
        first_time_seconds = response["data"]["weeklyPodium"][0]["times"]
        first_time = self.convert_time(first_time_seconds)
        self.rankings["first"] = {
            "user": first_user,
            "img": first_img,
            "time": first_time,
        }
        second_user = response["data"]["weeklyPodium"][1]["username"]
        second_img = response["data"]["weeklyPodium"][1]["profilePicture"]
        second_time_seconds = response["data"]["weeklyPodium"][1]["times"]
        second_time = self.convert_time(second_time_seconds)
        self.rankings["second"] = {
            "user": second_user,
            "img": second_img,
            "time": second_time,
        }
        third_user = response["data"]["weeklyPodium"][2]["username"]
        third_img = response["data"]["weeklyPodium"][2]["profilePicture"]
        third_time_seconds = response["data"]["weeklyPodium"][2]["times"]
        third_time = self.convert_time(third_time_seconds)
        self.rankings["third"] = {
            "user": third_user,
            "img": third_img,
            "time": third_time,
        }
        return self.rankings

    def get_current_podium_data(self) -> dict[str, dict[str, str]]:
        current_podium_url = "https://api.revomon.io/leaderboard/current_podium"
        response = requests.get(current_podium_url)
        response = response.json()
        first_user = response["data"]["currentPodium"][0]["username"]
        first_img = response["data"]["currentPodium"][0]["profilePicture"]
        self.rankings["first"] = {"user": first_user, "img": first_img}
        second_user = response["data"]["currentPodium"][1]["username"]
        second_img = response["data"]["currentPodium"][1]["profilePicture"]
        self.rankings["second"] = {"user": second_user, "img": second_img}
        third_user = response["data"]["currentPodium"][2]["username"]
        third_img = response["data"]["currentPodium"][2]["profilePicture"]
        self.rankings["third"] = {"user": third_user, "img": third_img}
        return self.rankings

    def get_text_size(self, draw: Any, text: str, font: Any) -> tuple[int, int]:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def podium_img(self, podium_type: str) -> None:
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
            rankings = self.get_weekly_podium_data()
            times = [
                rankings["second"]["time"],
                rankings["first"]["time"],
                rankings["third"]["time"],
            ]  # Text to display under usernames
        else:
            rankings = self.get_current_podium_data()
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

    def current_podium_embed(self) -> Embed:
        self.podium_img(podium_type="current")
        embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.from_str("#2e03fc"),
            timestamp=datetime.datetime.now(),
        )
        embed.set_image(url="attachment://current_image.png")
        embed.set_footer(text="Global Revomon Association")
        return embed

    def weekly_podium_embed(self) -> Embed:
        self.podium_img(podium_type="weekly")
        embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.from_str("#2e03fc"),
            timestamp=datetime.datetime.now(),
        )
        embed.set_image(url="attachment://weekly_image.png")
        embed.set_footer(text="Global Revomon Association")
        return embed

    async def update_rankings(self) -> None:
        try:
            podium_channel = await self.gradex.fetch_channel(1251022667935387740)
            if not isinstance(podium_channel, discord.TextChannel):
                return
            old_leaderboards = [
                message async for message in podium_channel.history(limit=2)
            ]
            for old_leaderboard in old_leaderboards:
                await old_leaderboard.delete()
            current_leaderboard = await podium_channel.send(content="Loading...")
            weekly_leaderboard = await podium_channel.send(content="Loading...")
            while True:
                self.podium_img(podium_type="current")
                await current_leaderboard.edit(
                    content=None,
                    attachments=[
                        discord.File(
                            self.current_podium_img["image_bytes"],
                            filename="current_image.png",
                        )
                    ],
                    embed=self.current_podium_embed(),
                )
                self.podium_img(podium_type="weekly")
                await weekly_leaderboard.edit(
                    content=None,
                    attachments=[
                        discord.File(
                            self.weekly_podium_img["image_bytes"],
                            filename="weekly_image.png",
                        )
                    ],
                    embed=self.weekly_podium_embed(),
                )
                await asyncio.sleep(random.randint(600, 900))
        except Exception as e:
            print(f"Podium Tracker Error: {e}")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # buttons = []
        # for button in buttons:
        #     self.gradex.add_view(button)
        print("Revomon Mod(Podium Leaderboard Tracker) is ready!")
        print("---------------------------")
        await self.update_rankings()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "podium":
                embed = self.current_podium_embed()
                await respond(self.gradex, message=message, embed=embed, buttons=None)
                embed = self.weekly_podium_embed()
                await respond(self.gradex, message=message, embed=embed, buttons=None)
        except Exception as e:
            print(f"An error occurred during Podium Keyword on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Podium(gradex))
