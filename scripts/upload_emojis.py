"""Script to compress and upload Revomon assets as Discord Application Emojis."""

import asyncio
import json
import logging
import os
import sys
from io import BytesIO

import discord
from dotenv import load_dotenv
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Setup basic logging for the script
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("upload_emojis")

class EmojiUploaderClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}!")
        try:
            await self.process_emojis()
        except Exception as e:
            logger.error(f"Error during emoji processing: {e}")
        finally:
            await self.close()

    async def process_emojis(self):
        # 1. Fetch existing application emojis to avoid duplicates
        logger.info("Fetching existing application emojis...")
        existing_emojis = await self.fetch_application_emojis()
        existing_names = {emoji.name for emoji in existing_emojis}
        logger.info(f"Found {len(existing_names)} existing application emojis.")

        # 2. Load the revomon JSON database to map dex_id -> name
        json_path = os.path.join("data", "revomon.json")
        if not os.path.exists(json_path):
            logger.error(f"Database not found at {json_path}")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            revomon_db = json.load(f)

        # Build mapping: dex_id -> safe_name
        # The TV UI sanitizes names by replacing spaces and hyphens with underscores
        dex_map = {}
        for mon in revomon_db:
            dex_id = str(mon.get("dex_id"))
            name = mon.get("name", "unknown").lower().replace(" ", "_").replace("-", "_")
            dex_map[dex_id] = name

        raw_dir = os.path.join("data", "assets", "revomon", "raw")
        if not os.path.exists(raw_dir):
            logger.error(f"Raw image directory not found at {raw_dir}")
            return

        # 3. Process each image
        files = os.listdir(raw_dir)
        upload_count = 0

        for filename in files:
            if not filename.endswith(".png"):
                continue

            # Parse the filename (e.g., '1.png' or '1_shiny.png')
            base_name = filename[:-4]
            is_shiny = "_shiny" in base_name
            
            # Extract just the ID number
            dex_id_str = base_name.replace("_shiny", "")
            
            if dex_id_str not in dex_map:
                logger.warning(f"Unrecognized dex ID '{dex_id_str}' in file '{filename}'. Skipping.")
                continue
                
            revomon_name = dex_map[dex_id_str]
            emoji_name = f"{revomon_name}_shiny" if is_shiny else revomon_name

            if emoji_name in existing_names:
                # Already uploaded
                continue

            # Load and resize the image
            filepath = os.path.join(raw_dir, filename)
            try:
                img = Image.open(filepath)
                # Resize down to 128x128 for Discord emojis (<= 256kb)
                img.thumbnail((128, 128))
                
                b = BytesIO()
                img.save(b, format="PNG")
                image_bytes = b.getvalue()
                
                # Double check size just in case, though 128x128 PNG is practically guaranteed to be < 256kb
                if len(image_bytes) > 256 * 1024:
                    logger.warning(f"Image {filename} is still too large after resize ({len(image_bytes)} bytes)! Skipping.")
                    continue

                # 4. Upload Application Emoji
                logger.info(f"Uploading emoji: {emoji_name} (from {filename})...")
                await self.create_application_emoji(name=emoji_name, image=image_bytes)
                upload_count += 1
                
                # Add to set so we don't accidentally upload duplicates if the folder has duplicates
                existing_names.add(emoji_name)

                # Discord Application Emoji limit is 2000.
                if len(existing_names) >= 2000:
                    logger.warning("Reached the absolute maximum limit of 2,000 Application Emojis!")
                    break

                # Sleep to prevent HTTP 429 Rate Limiting from Discord API
                await asyncio.sleep(2.0)

            except discord.HTTPException as e:
                logger.error(f"Discord HTTP Exception while uploading {emoji_name}: {e}")
                if e.status == 429:
                    logger.warning("Hit hard rate limit. Sleeping for 15 seconds...")
                    await asyncio.sleep(15.0)
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}")

        logger.info(f"Finished uploading {upload_count} new emojis! Total app emojis: {len(existing_names)}.")

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("No DISCORD_BOT_TOKEN found in environment variables!")
        sys.exit(1)

    intents = discord.Intents.default()
    client = EmojiUploaderClient(intents=intents)
    client.run(token)
