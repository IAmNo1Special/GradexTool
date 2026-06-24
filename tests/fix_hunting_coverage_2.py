path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

test = """
    @patch("mods.revocord.hunting.Path.exists", return_value=True)
    @patch("mods.revocord.hunting.json.load")
    @patch("builtins.open")
    def test_hunting_cog_init_dict_data(self, mock_open, mock_json_load, mock_exists, mock_bot: Any) -> None:
        mock_json_load.side_effect = [{"to": "Pikachu"}, {"revomons": [{"name": "Pikachu"}]}, [{"name": "Hardy"}]]
        cog = HuntingCog(mock_bot)
        assert len(cog.revomons) == 1

    @patch("mods.revocord.hunting.Path.exists", return_value=True)
    @patch("builtins.open", side_effect=Exception("File Error"))
    def test_hunting_cog_init_exceptions(self, mock_open, mock_exists, mock_bot: Any) -> None:
        with patch("mods.revocord.hunting.logger") as mock_logger:
            cog = HuntingCog(mock_bot)
            assert mock_logger.error.call_count == 3
"""

text = text.replace(
    "class TestHuntingCogInitialization:",
    "class TestHuntingCogInitialization:\n" + test,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
