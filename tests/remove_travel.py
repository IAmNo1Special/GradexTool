from typing import Any


def delete_blocks(path: Any, blocks: Any) -> None:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    for block in blocks:
        text = text.replace(block, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

act_path = r"f:\projects\Revomon\GradexTool\mods\revocord\activity.py"
test_act_path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_activity.py"

act_block1 = """    @ui.button(
        label="Travel",
        style=discord.ButtonStyle.primary,
        emoji="🗺️",
        custom_id="persistent_travel_button",
    )
    async def travel(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        \"\"\"Open the travel destination select menu.\"\"\"
        from mods.revocord.travel import (
            TRAVEL_COST,
            TRAVEL_TIME_SECONDS,
            TravelSelectView,
        )

        member = interaction.user
        account = await get_or_create_account(member.id)
        current_city = account.get("current_city", "drassius city")

        await interaction.response.send_message(
            f"Where would you like to travel to from **{current_city.title()}**?\\n"
            f"(Cost: {TRAVEL_COST} Energy, Time: {TRAVEL_TIME_SECONDS}s)",
            view=TravelSelectView(current_city),
            ephemeral=True,
        )"""

act_block2 = """    @ui.button(
        label="Travel",
        style=discord.ButtonStyle.primary,
        emoji="🗺️",
        custom_id="persistent_route_travel_button",
    )
    async def travel(self, interaction: discord.Interaction, button: ui.Button[Any]) -> None:
        \"\"\"Open the travel destination select menu.\"\"\"
        from mods.revocord.travel import (
            TRAVEL_COST,
            TRAVEL_TIME_SECONDS,
            TravelSelectView,
        )

        member = interaction.user
        account = await get_or_create_account(member.id)
        current_city = account.get("current_city", "drassius city")

        await interaction.response.send_message(
            f"Where would you like to travel to from **{current_city.title()}**?\\n"
            f"(Cost: {TRAVEL_COST} Energy, Time: {TRAVEL_TIME_SECONDS}s)",
            view=TravelSelectView(current_city),
            ephemeral=True,
        )"""

test_block1 = """    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    async def test_travel_button(self, mock_get_account: Any, mock_interaction: Any) -> None:
        mock_get_account.return_value = {"current_city": "test city"}
        view = TravelButtonView()

        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_travel_button"][0]

        with patch("mods.revocord.travel.TravelSelectView") as mock_travel_view:
            mock_travel_view.return_value = MagicMock()
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()
            args, kwargs = mock_interaction.response.send_message.call_args
            assert "test city" in args[0].lower()
            assert kwargs["ephemeral"] is True"""

test_block2 = """    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    async def test_travel_button(self, mock_get_account: Any, mock_interaction: Any) -> None:
        view = RouteAITrainerView()
        mock_get_account.return_value = {"current_city": "route 1"}

        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_route_travel_button"][0]

        with patch("mods.revocord.travel.TravelSelectView") as mock_travel_view:
            mock_travel_view.return_value = MagicMock()
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()
            args, kwargs = mock_interaction.response.send_message.call_args
            assert "route 1" in args[0].lower()"""

delete_blocks(act_path, [act_block1, act_block2])
delete_blocks(test_act_path, [test_block1, test_block2])
print("Done")
