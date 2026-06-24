import re
from typing import Any

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()


# 1. Restore `response.send_message` in all these tests
def restore_send_message(test_names: Any, t: Any) -> Any:
    for name in test_names:
        pattern = (
            r"(async def "
            + name
            + r"\(.*?\):[\s\S]*?)mock_interaction\.edit_original_response\.assert_called_once\(\)"
        )
        t = re.sub(
            pattern, r"\1mock_interaction.response.send_message.assert_called_once()", t
        )

        pattern2 = (
            r"(async def "
            + name
            + r"\(.*?\):[\s\S]*?)mock_interaction\.edit_original_response\.call_args"
        )
        t = re.sub(pattern2, r"\1mock_interaction.response.send_message.call_args", t)
    return t


tests_send_message = [
    "test_wrong_user",
    "test_spawn_fight",
    "test_spawn_catch_menu_no_orbs",
    "test_spawn_catch_menu_with_orbs",
    "test_spawn_throw_orb_no_msg_id",
    "test_spawn_throw_orb_fetch_msg_error",
    "test_spawn_throw_orb_no_embeds",
    "test_spawn_throw_orb_insufficient_orbs",
    "test_spawn_throw_orb_not_found",
    "test_spawn_throw_orb_fail_flee",
    "test_spawn_throw_orb_fail_no_flee",
    "test_spawn_throw_orb_success",
    "test_expired_throw_orb_msg",
    "test_spawn_run_delete_error",
]
text = restore_send_message(tests_send_message, text)


# 2. Restore `followup.send` in these tests
def restore_followup_send(test_names: Any, t: Any) -> Any:
    for name in test_names:
        pattern = (
            r"(async def "
            + name
            + r"\(.*?\):[\s\S]*?)mock_interaction\.edit_original_response\.assert_called_once\(\)"
        )
        t = re.sub(pattern, r"\1mock_interaction.followup.send.assert_called_once()", t)

        pattern2 = (
            r"(async def "
            + name
            + r"\(.*?\):[\s\S]*?)mock_interaction\.edit_original_response\.call_args"
        )
        t = re.sub(pattern2, r"\1mock_interaction.followup.send.call_args", t)
    return t


tests_followup_send = ["test_no_database", "test_no_eligible"]
text = restore_followup_send(tests_followup_send, text)

# 3. Fix type1 in test_spawn_success_shiny_file_exists
text = text.replace('"type1": "Grass", "type2": "Poison"', '"type1": "neutral"')

# 4. Check for test_spawn_success_shiny_file_exists assert
text = text.replace(
    'assert "embed" in kwargs\n        assert "file" in kwargs',
    'assert kwargs.get("embed")\n        assert kwargs.get("attachments")',
)

# test_spawn_success_not_shiny_no_file
text = text.replace(
    'assert "file" not in kwargs', 'assert not kwargs.get("attachments")'
)
text = text.replace('kwargs["embed"].description', 'kwargs["embed"].description')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
