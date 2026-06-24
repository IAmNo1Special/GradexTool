import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. test_on_timeout_success & test_on_timeout_exception
text = text.replace(
    "        view.message = mock_message\n        \n        await view.on_timeout()",
    "        view.message = mock_message\n        mock_message.embeds = [MagicMock()]\n        await view.on_timeout()",
)
text = text.replace(
    "        view.message = mock_message\n        await view.on_timeout()",
    "        view.message = mock_message\n        mock_message.embeds = [MagicMock()]\n        await view.on_timeout()",
)

# 2. test_spawn_catch_menu_with_orbs
text = text.replace(
    "        mock_interaction.message.id = 100\n        await cog.on_interaction(mock_interaction)",
    '        mock_interaction.message.id = 100\n        mock_interaction.message.embeds = [MagicMock()]\n        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]\n        await cog.on_interaction(mock_interaction)',
)

# 3. test_handle_wilds_claim
text = text.replace(
    "    async def test_handle_wilds_claim(self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any) -> None:",
    '    @patch("mods.revocord.hunting.save_active_encounter", new_callable=AsyncMock)\n    async def test_handle_wilds_claim(self, mock_save: Any, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any) -> None:',
)

# 4. test_no_eligible
text = text.replace(
    '    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)\n    async def test_no_eligible(self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any) -> None:',
    '    @patch("mods.revocord.hunting.get_guild_biome", return_value="Plains")\n    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)\n    async def test_no_eligible(self, mock_get_account: Any, mock_biome: Any, cog: HuntingCog, mock_interaction: Any) -> None:',
)

# 5. test_cleanup_encounters
cleanup_fix = """    @pytest.mark.asyncio
    async def test_cleanup_encounters(self, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        mock_msg = MagicMock()
        mock_msg.delete = AsyncMock()

        mock_item = MagicMock()
        mock_item.custom_id = f"spawn_fight:123:1:0:{int(time.time() - 400)}"

        mock_component = MagicMock()
        mock_component.children = [mock_item]
        mock_msg.components = [mock_component]

        mock_channel = MagicMock()

        async def mock_history(*args, **kwargs):
            yield mock_msg

        mock_channel.history = mock_history
        mock_guild = MagicMock()
        mock_guild.text_channels = [mock_channel]
        mock_bot.guilds = [mock_guild]

        await cog.cleanup_encounters()
        mock_msg.delete.assert_called_once()
"""
text = re.sub(
    r"    @pytest\.mark\.asyncio\n    async def test_cleanup_encounters\(self.*?\):[\s\S]*",
    cleanup_fix,
    text,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
