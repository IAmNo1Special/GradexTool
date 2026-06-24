path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

test = """
    def test_wilds_interact_view_init_event_zero(self) -> None:
        view = WildsInteractView(1, 2, 0, 1000, 0)
        assert len(view.children) == 4
"""

text = text.replace(
    "class TestWildsInteractView:", "class TestWildsInteractView:\n" + test
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
