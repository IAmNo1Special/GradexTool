path = r"f:\projects\Revomon\GradexTool\mods\revocord\hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. on_timeout exception log
text = text.replace(
    "            except Exception:\n                pass",
    '            except Exception as e:\n                import logging\n                logging.error(f"on_timeout EXCEPTION: {e}", exc_info=True)\n                pass',
)

# 2. spawn_catch_menu debug
text = text.replace(
    '            await interaction.response.send_message("Choose an Orb to throw:", view=view, ephemeral=True)',
    '            import logging\n            logging.error(f"ABOUT TO SEND MESSAGE! {total_orbs}")\n            await interaction.response.send_message("Choose an Orb to throw:", view=view, ephemeral=True)',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
