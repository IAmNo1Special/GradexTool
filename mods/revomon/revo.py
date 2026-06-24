import requests
from discord.ext import commands, tasks


class PriceTracker(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.revo_url = "https://api.coingecko.com/api/v3/coins/revomon-2?localization=false&tickers=false&market_data=true&community_data=false&sparkline=false&developer_data=false"
        self.price_channel_id = 1254142506178838558  # Replace with your channel ID
        self.update_price.start()

    def get_revo_price(self) -> float | None:
        response = requests.get(self.revo_url)
        if response.status_code == 200:
            data = response.json()
            price = data["market_data"]["current_price"]["usd"]
            return float(price)
        return None

    @tasks.loop(minutes=3)
    async def update_price(self) -> None:
        price = await self.gradex.loop.run_in_executor(None, self.get_revo_price)
        if price is not None:
            channel = self.gradex.get_channel(self.price_channel_id)
            if channel is not None:
                new_name = f"Revo: ${price:.5f}"
                await channel.edit(name=new_name)  # type: ignore
        else:
            print("Failed to fetch the price data.")

    @update_price.before_loop
    async def before_update_price(self) -> None:
        await self.gradex.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Revomon Mod(REVO Price Tracker) is ready!")
        print("---------------------------")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(PriceTracker(gradex))
