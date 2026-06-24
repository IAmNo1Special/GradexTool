path = r"f:\projects\Revomon\GradexTool\mods\revocord\hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Add debug
text = text.replace(
    '        elif action == "spawn_catch_menu":\n            account = await get_or_create_account(spawner_id)\n            inventory = account.get("inventory", {})\n\n            red_count = inventory.get(ORB_CONFIG["RED"]["id"], 0)',
    '        elif action == "spawn_catch_menu":\n            account = await get_or_create_account(spawner_id)\n            inventory = account.get("inventory", {})\n            logger.error(f"DEBUG: account={account}, inventory={inventory}")\n\n            red_count = inventory.get(ORB_CONFIG["RED"]["id"], 0)',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
