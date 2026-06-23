import re

path = r"f:\projects\Revomon\GradexTool\mods\revocord\hunting.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# I will replace the except (ValueError, IndexError): return with a catch-all that logs everything
text = text.replace(
    '        except (ValueError, IndexError):\n            return',
    '        except Exception as e:\n            logger.error(f"EXCEPTION IN ON_INTERACTION: {e}", exc_info=True)\n            return'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
