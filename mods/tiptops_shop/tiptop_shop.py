from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class tiptop_shop(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def tiptop_shop_intro_embed(self) -> Any:
        embed = discord.Embed(
            title="Tip: Welcome to Tiptop's Top-up Shop.",
            description="I have lots of  items in stock. Which one are you interested in today?",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(
            url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
        )
        embed.set_author(name="Tiptop's Top-up Shop")
        embed.set_footer(text="Global Revomon Association")
        return embed

    class tiptop_shop_intro_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="NFT Items",
            style=discord.ButtonStyle.green,
            custom_id="Nft Items",
        )
        async def tiptop_nft_items(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Only the best items for the best Tamers.",
                description="Let me know if you see an NFT item that interests you.",
                color=discord.Color.red(),
                url="https://lifty.io/@GlobalRevomonAssociation?tab=NFTs",
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            buttons = tiptop_shop.tiptop_shop_nft_items_buttons()
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, view=buttons, ephemeral=True)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    class tiptop_shop_nft_items_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Gradex Tool(Pro+)",
            style=discord.ButtonStyle.green,
            custom_id="Tiptop Gradex Tool",
        )
        async def tiptop_gradex_tool(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Interested in the Gradex Tool(Pro+) are ya?",
                description="",
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://media.discordapp.net/attachments/983557860803874826/1076037071539544124/grade-x_tool.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            # buttons =
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="6,000 IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="6000 IGC NFT",
        )
        async def tiptop_6000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Would you like to buy or redeem a 6,000 IGC NFT?",
                description="__**PRICE**__\n- 10.3 REVO\n- 6,600 IGC\n\nA - Click 'REDEEM YOUR IGC' to redeem your 6,000 IGC NFT(s) for the equivalent in-game IGC\n\nB - Click 'BUY WITH REVO' to buy the 6,000 IGC NFT(s) with REVO token\n\nC- Click 'BUY WITH IGC' to buy the 6,000 IGC NFT(s) with your In-Game Currency",
                color=discord.Color.red(),
            )

            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657181376055x123899512123595730/6%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            buttons = tiptop_shop.igc_6000_nft_buttons()
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, view=buttons, ephemeral=True)

        @discord.ui.button(
            label="60,000 IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="60000 IGC NFT",
        )
        async def tiptop_60000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Would you like to buy or redeem a 60,000 IGC NFT?",
                description="__**PRICE**__\n- 103 REVO\n- 66,000 IGC\n\nA - Click 'REDEEM YOUR IGC' to redeem your 60,000 IGC NFT(s) for the equivalent in-game IGC\n\nB - Click 'BUY WITH REVO' to buy the 60,000 IGC NFT(s) with REVO token\n\nC- Click 'BUY WITH IGC' to buy the 60,000 IGC NFT(s) with your In-Game Currency",
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182769924x799549239436221600/60%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            buttons = tiptop_shop.igc_60000_nft_buttons()
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, view=buttons, ephemeral=True)

        @discord.ui.button(
            label="120,000 IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="120000 IGC NFT",
        )
        async def tiptop_120000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Would you like to buy or redeem a 120,000 IGC NFT?",
                description="__**PRICE**__\n- 206 REVO\n- 132,000 IGC\n\nA - Click 'REDEEM YOUR IGC' to redeem your 120,000 IGC NFT(s) for the equivalent in-game IGC\n\nB - Click 'BUY WITH REVO' to buy the 120,000 IGC NFT(s) with REVO token\n\nC- Click 'BUY WITH IGC' to buy the 120,000 IGC NFT(s) with your In-Game Currency",
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182784991x177167826442251600/120%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            buttons = tiptop_shop.igc_120000_nft_buttons()
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, view=buttons, ephemeral=True)

    class igc_6000_nft_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Redeem your IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="Redeem 6000 IGC NFT",
        )
        async def redeem_6000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Either for one thing or another, you'll always need IGC.",
                description="One of my {^TipTop's Helper} will DM you to complete your order to redeem your 6,000 IGC NFT.",
                color=discord.Color.red(),
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657181376055x123899512123595730/6%2C000%20%24IGC%20NFT.png"
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with REVO",
            style=discord.ButtonStyle.green,
            custom_id="Buy 6000 IGC NFT With REVO",
        )
        async def buy_6000_igc_revo(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Click here to buy a 6,000 IGC NFT for REVO",
                description="- 10.3 REVO = 6,000 IGC NFT",
                color=discord.Color.red(),
                url="https://lifty.io/bsc/0xEd840De2c93BA3BfaF3d9aa79BfcDC869B77De09/3851545",
            )

            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657181376055x123899512123595730/6%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with IGC",
            style=discord.ButtonStyle.green,
            custom_id="Buy 6000 IGC NFT With IGC",
        )
        async def buy_6000_igc_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: I keep telling people, NFTs are the future!",
                description="One of my {^TipTop's Helper} will DM you to complete your order for a 6,000 IGC NFT with 6,600 in-game IGC.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657181376055x123899512123595730/6%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

    class igc_60000_nft_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Redeem your IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="Redeem 60000 IGC NFT",
        )
        async def redeem_60000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Either for one thing or another, you'll always need IGC.",
                description="One of my {^TipTop's Helper} will DM you to complete your order to redeem your 60,000 IGC NFT.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182769924x799549239436221600/60%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with REVO",
            style=discord.ButtonStyle.green,
            custom_id="Buy 60000 IGC NFT With REVO",
        )
        async def buy_60000_igc_revo(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Click here to buy a 60,000 IGC NFT for REVO",
                description="- 103 REVO = 60,000 IGC NFT",
                color=discord.Color.red(),
                url="https://lifty.io/bsc/0xEd840De2c93BA3BfaF3d9aa79BfcDC869B77De09/8870473",
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182769924x799549239436221600/60%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with IGC",
            style=discord.ButtonStyle.green,
            custom_id="Buy 60000 IGC NFT With IGC",
        )
        async def buy_60000_igc_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: I keep telling people, NFTs are the future!",
                description="One of my {^TipTop's Helper} will DM you to complete your order for a 60,000 IGC NFT with 66,000 in-game IGC.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182769924x799549239436221600/60%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

    class igc_120000_nft_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Redeem your IGC NFT",
            style=discord.ButtonStyle.green,
            custom_id="Redeem 120000 IGC NFT",
        )
        async def redeem_120000_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: Either for one thing or another, you'll always need IGC.",
                description="One of my {^TipTop's Helper} will DM you to complete your order to redeem your 120,000 IGC NFT.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182784991x177167826442251600/120%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with REVO",
            style=discord.ButtonStyle.green,
            custom_id="Buy 120000 IGC NFT With REVO",
        )
        async def buy_120000_igc_revo(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Click here to buy a 120,000 IGC NFT for REVO",
                description="- 206 REVO = 120,000 IGC NFT",
                color=discord.Color.red(),
                url="https://lifty.io/bsc/0xEd840De2c93BA3BfaF3d9aa79BfcDC869B77De09/2201662",
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182784991x177167826442251600/120%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

        @discord.ui.button(
            label="Buy with IGC",
            style=discord.ButtonStyle.green,
            custom_id="Buy 120000 IGC NFT With IGC",
        )
        async def buy_120000_igc_igc(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            embed = discord.Embed(
                title="Tip: I keep telling people, NFTs are the future!",
                description="One of my {^TipTop's Helper} will DM you to complete your order for a 120,000 IGC NFT with 132,000 in-game IGC.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://s3.amazonaws.com/appforest_uf/f1657410637472x122090386899320620/TIPTOP.png"
            )
            embed.set_image(
                url="https://s3.amazonaws.com/appforest_uf/f1657182784991x177167826442251600/120%2C000%20%24IGC%20NFT.png"
            )
            embed.set_author(name="Tiptop's Top-up Shop")
            embed.set_footer(text="Global Revomon Association")
            await interaction.response.defer()
            await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Revomon Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            # Save User's Cleaned Input As The Search Prompt
            prompt = message.content.lower().strip()
            # Check if User's Prompt is "Tiptop" or "Tip Top"
            if prompt == "tiptop" or prompt == "tip top":
                embed = self.tiptop_shop_intro_embed()
                buttons = self.tiptop_shop_intro_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during tiptop_shop on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(tiptop_shop(gradex))
