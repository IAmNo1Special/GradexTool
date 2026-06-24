from typing import Any
import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# I will replace `setup_command.callback` with `execute_setup` in the specific test functions that need it.
def replace_in_test(test_name: Any, old: Any, new: Any, content: Any) -> str:
    pattern = rf"(def {test_name}\(.*?\):.*?)({re.escape(old)})"
    return re.sub(pattern, r"\1" + new, content, flags=re.DOTALL)

tests_to_fix = [
    "test_setup_full_creation",
    "test_setup_existing_sync",
    "test_setup_fetch_fallback",
    "test_forbidden_exception",
    "test_generic_exception",
    "test_setup_portal_fail"
]

for test_name in tests_to_fix:
    text = replace_in_test(
        test_name,
        "await setup_cog.setup_command.callback(setup_cog, mock_interaction)",
        "await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)",
        text
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
