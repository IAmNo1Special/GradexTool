import os
from io import BytesIO

import aiohttp
from dotenv import load_dotenv
from PIL import Image

from data.gradexDB import OwnedLandsTable, RevomonTable
from utils.revomon_utils import get_attributes

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")


async def img_url_to_emoji_size(img_url: str):
    # URL of the image
    image_url = img_url

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                # Download the image
                content = await response.read()
                img = Image.open(BytesIO(content))
                # Get the size of the image
                width, height = img.size
                # Get the resize ratio
                ratio = int(min(width / 128, height / 128))

                # Resize the image to 128 pixels
                img = img.resize(
                    (int(width / ratio), int(height / ratio)),
                    Image.Resampling.LANCZOS,
                )

                # Save the resized image to a BytesIO object
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format="PNG")
                img_byte_arr.seek(0)
                return img_byte_arr.getvalue()
            else:
                print(
                    f"Failed to fetch image: {response.status} - {await response.text()}"
                )


async def create_application_emoji(image_data, emoji_name):
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/emojis"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",  # Ensure the correct Content-Type
    }

    # Encode the image data as base64
    import base64

    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Prepare the payload
    payload = {
        "name": emoji_name,
        "image": f"data:image/png;base64,{image_base64}",  # Use base64-encoded image
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 201:
                emoji = await response.json()
                print(f"Emoji created: {emoji['name']} (ID: {emoji['id']})")
                return {"name": emoji["name"], "id": emoji["id"]}
            else:
                print(
                    f"Failed to create emoji: {response.status} - {await response.text()}"
                )


async def list_application_emojis():
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/emojis"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    app_emojis = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                emojis = await response.json()
                for emoji in emojis["items"]:
                    app_emojis.append(
                        {"name": emoji["name"], "id": emoji["id"]}
                    )
            else:
                print(
                    f"Failed to fetch emojis: {response.status} - {await response.text()}"
                )

    return app_emojis


async def get_application_emoji(emoji_id):
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/emojis/{emoji_id}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                emoji = await response.json()
                print(f"Emoji Name: {emoji['name']}, Emoji ID: {emoji['id']}")
            else:
                print(
                    f"Failed to fetch emoji: {response.status} - {await response.text()}"
                )


async def modify_application_emoji(emoji_id, new_name):
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/emojis/{emoji_id}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"name": new_name}

    async with aiohttp.ClientSession() as session:
        async with session.patch(
            url, headers=headers, json=payload
        ) as response:
            if response.status == 200:
                emoji = await response.json()
                print(f"Emoji modified: {emoji['name']} (ID: {emoji['id']})")
            else:
                print(
                    f"Failed to modify emoji: {response.status} - {await response.text()}"
                )


async def delete_application_emoji(emoji_id):
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/emojis/{emoji_id}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            if response.status == 204:
                print(f"Emoji with ID {emoji_id} deleted successfully.")
            else:
                print(
                    f"Failed to delete emoji: {response.status} - {await response.text()} - {response}"
                )


async def create_emoji_from_url(img_url: str, emoji_name: str):
    image_data = await img_url_to_emoji_size(img_url)
    emoji_obj = await create_application_emoji(
        image_data, emoji_name=emoji_name
    )
    return emoji_obj


async def create_revomon_emojis():
    emoji_list = await list_application_emojis()
    for mon_name in RevomonTable().get_names():
        if "-" in mon_name:
            emoji_mon_name: str = mon_name.replace("-", "_")
        else:
            emoji_mon_name: str = mon_name
        try:
            if emoji_mon_name in [emoji["name"] for emoji in emoji_list]:
                continue
            else:
                attributes = get_attributes(mon_name)
                mon_img_url = attributes["profile_img"]
                emoji_obj = await create_emoji_from_url(
                    mon_img_url, emoji_name=emoji_mon_name
                )
                emoji_list.append(emoji_obj)
            if f"{emoji_mon_name}_shiny" in [
                emoji["name"] for emoji in emoji_list
            ]:
                continue
            else:
                attributes = get_attributes(mon_name)
                shiny_mon_img_url = attributes["shiny_profile_img"]
                emoji_obj = await create_emoji_from_url(
                    shiny_mon_img_url, emoji_name=f"{emoji_mon_name}_shiny"
                )
                emoji_list.append(emoji_obj)
        except Exception as e:
            print(f"Failed to create emoji for {mon_name}: {e}")

    emoji_list = await list_application_emojis()
    return emoji_list


async def create_land_emojis():
    emoji_list = await list_application_emojis()
    lands_table = OwnedLandsTable()
    for land_id in lands_table.get_ids():
        land_info = OwnedLandsTable().get_info(token_id=land_id)[0]
        emoji_name = f"{land_info[3]}_{land_info[4]}".replace(" ", "_")
        print("Attempting to create emoji for land: ", emoji_name)
        if emoji_name in [emoji["name"] for emoji in emoji_list]:
            print(f"Emoji {emoji_name} already exists")
            continue
        else:
            land_img_url = land_info[7]
            emoji_obj = await create_emoji_from_url(
                land_img_url, emoji_name=emoji_name
            )
            emoji_list.append(emoji_obj)
            print(land_img_url)
    return emoji_list


if __name__ == "__main__":
    pass
