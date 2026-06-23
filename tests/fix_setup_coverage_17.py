import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

bad_indentation = """async def mock_create_text_channel(name, **kwargs):
            if name == "portal":
                raise Exception("Portal channel failed to generate.")
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel
            
        mock_guild.create_text_channel = mock_create_text_channel"""

good_indentation = """        async def mock_create_text_channel(name, **kwargs):
            if name == "portal":
                raise Exception("Portal channel failed to generate.")
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel
            
        mock_guild.create_text_channel = mock_create_text_channel"""

text = text.replace(bad_indentation, good_indentation)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
