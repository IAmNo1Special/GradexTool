path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_activity.py"

with open(path, encoding="utf-8") as f:
    text = f.read()

# Delete test_travel_button_exists in TestTravelButtonViewButtons
block1 = """    def test_travel_button_exists(self) -> None:
        \"\"\"Test that travel button exists in the view.\"\"\"
        view = TravelButtonView()

        travel_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'travel' in child.custom_id:
                travel_button = child
                break

        assert travel_button is not None"""
text = text.replace(block1, "")

# Delete test_travel_button_exists in TestRouteAITrainerViewButtons
block2 = """    def test_travel_button_exists(self) -> None:
        \"\"\"Test that travel button exists in the view.\"\"\"
        view = RouteAITrainerView()

        travel_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'travel' in child.custom_id:
                travel_button = child
                break

        assert travel_button is not None"""
text = text.replace(block2, "")

# Update expected children
text = text.replace("(TravelButtonView(), 2),", "(TravelButtonView(), 1),")
text = text.replace("(RouteAITrainerView(), 2),", "(RouteAITrainerView(), 1),")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
