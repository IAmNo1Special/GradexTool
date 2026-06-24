import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. Remove all global `.start()` patches from the top of the file.
text = re.sub(r"patch\(.*?\.start\(\)\n", "", text)

# 2. Add an autouse fixture to patch database access globally for this file so we don't need .start()
fixture_code = """
@pytest.fixture(autouse=True)
def mock_db_and_broadcast():
    with patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock), \\
         patch("mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn", new_callable=AsyncMock), \\
         patch("mods.revocord.portal.build_console_embed", new_callable=AsyncMock), \\
         patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock, return_value={}), \\
         patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock):
        yield
"""
# Insert after imports
text = re.sub(r"(from unittest\.mock import .*?\n)", r"\1" + fixture_code, text)

# 3. Replace test_on_timeout_exception
text = re.sub(
    r"    @pytest\.mark\.asyncio\n    async def test_on_timeout_exception\(self.*?\):[\s\S]*?(?=    @pytest\.mark\.asyncio\n    async def test_on_timeout_success)",
    r"""    @pytest.mark.asyncio
    async def test_on_timeout_exception(self, mock_interaction: Any) -> None:
        chosen = {"name": "TestMon"}
        view = WildSpawnView(chosen, False, 123, 456)
        mock_message = MagicMock()
        mock_message.edit = AsyncMock(side_effect=Exception())
        view.message = mock_message
        await view.on_timeout()
        mock_message.edit.assert_called_once()
""",
    text,
)

# 4. Replace test_on_timeout_success
text = re.sub(
    r"    @pytest\.mark\.asyncio\n    async def test_on_timeout_success\(self.*?\):[\s\S]*?(?=class TestOnInteraction:)",
    r"""    @pytest.mark.asyncio
    async def test_on_timeout_success(self, mock_interaction: Any) -> None:
        chosen = {"name": "TestMon"}
        view = WildSpawnView(chosen, False, 123, 456)
        mock_message = MagicMock()
        embed = MagicMock()
        embed.description = "Original"
        mock_message.embeds = [embed]
        mock_message.edit = AsyncMock()
        view.message = mock_message

        with patch("scripts.gradexDB.active_spawns_table.remove_spawn", new_callable=AsyncMock) as mock_remove:
            await view.on_timeout()
            mock_message.edit.assert_called_once()
            mock_remove.assert_called_once_with(456)

""",
    text,
)

# 5. Replace test_expired to test_spawn_throw_orb_no_embeds inclusive!
# We'll just replace the whole block from test_expired down to test_spawn_throw_orb_insufficient_orbs
text = re.sub(
    r"    @pytest\.mark\.asyncio\n    async def test_expired\(self.*?\):[\s\S]*?(?=    @pytest\.mark\.asyncio\n    async def test_spawn_throw_orb_insufficient_orbs)",
    r"""    @pytest.mark.asyncio
    async def test_expired(self, cog: Any, mock_interaction: Any) -> None:
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time()) - 400
        mock_interaction.data = {"custom_id": f"spawn_fight:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.edit_original_response.assert_called_once()
        assert "expired" in mock_interaction.edit_original_response.call_args[1]["content"]

    @pytest.mark.asyncio
    async def test_spawn_run(self, cog: Any, mock_interaction: Any) -> None:
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_run:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        mock_interaction.response.defer = AsyncMock()
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_catch_menu_no_orbs(self, mock_get_account: Any, cog: Any, mock_interaction: Any) -> None:
        mock_get_account.return_value = {"inventory": {}}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_catch_menu:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert "not have any Orbs" in mock_interaction.response.send_message.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_catch_menu_with_orbs(self, mock_get_account: Any, cog: Any, mock_interaction: Any) -> None:
        mock_get_account.return_value = {"inventory": {"159": 1, "4": 2, "31": 3}}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_catch_menu:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        mock_interaction.message = MagicMock()
        mock_interaction.message.id = 100
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert "Choose an Orb" in mock_interaction.response.send_message.call_args[0][0]

    @pytest.mark.asyncio
    async def test_spawn_throw_orb_no_embeds(self, cog: Any, mock_interaction: Any) -> None:
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.user.id = 123
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = []
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert "invalid" in mock_interaction.response.send_message.call_args[0][0]

""",
    text,
)

# 6. We also need to fix `test_spawn_throw_orb_insufficient_orbs` and onwards because `get_or_create_account` needs `new_callable=AsyncMock`
text = re.sub(
    r'@patch\("mods\.revocord\.hunting\.get_or_create_account"\)',
    r'@patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)',
    text,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
