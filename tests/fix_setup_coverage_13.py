
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

bad_block = """def mock_create_text_channel(**kwargs):
            if kwargs.get("name") == "portal":
                return None
            channel = MagicMock(spec=discord.TextChannel)
            channel.name = kwargs.get("name")
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)"""

good_block = """        def mock_create_text_channel(**kwargs):
            if kwargs.get("name") == "portal":
                return None
            channel = MagicMock(spec=discord.TextChannel)
            channel.name = kwargs.get("name")
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)"""

text = text.replace(bad_block, good_block)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
