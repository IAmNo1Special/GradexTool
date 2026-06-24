import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

debug_mock = '''
        async def mock_create_text_channel(name, **kwargs):
            print(f"CALLED MOCK CREATE TEXT CHANNEL FOR {name}")
            if name == "portal":
                raise Exception("Portal channel failed to generate.")
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)
'''

text = re.sub(
    r'        async def mock_create_text_channel.*?mock_guild\.create_text_channel = mock_create_text_channel',
    debug_mock.strip(),
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
