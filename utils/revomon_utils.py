import io
from typing import Any

import plotly.graph_objects as go
import requests
from PIL import Image, ImageDraw, ImageFont

from data import (
    CounterdexTable,
    NaturesTable,
    OwnedLandsTable,
    RevomonMovesTable,
    RevomonTable,
    TypesTable,
)

max_iv_total = 186
max_ev_total = 510


async def get_attributes(revomon_name: str) -> dict[str, str | int | list[str] | None]:
    revomon_name = revomon_name.lower()
    revomon_table = RevomonTable()
    TypesTable()
    mon_info = (await revomon_table.get_info(revomon_name=revomon_name))[0]
    ev_rewards = dict(
        zip(
            [
                "Hit Points",
                "Attack",
                "Defense ",
                "Special Attack",
                "Special Defense",
                "Speed",
            ],
            [
                mon_info[23],
                mon_info[24],
                mon_info[25],
                mon_info[26],
                mon_info[27],
                mon_info[28],
            ],
            strict=True,
        )
    )
    ev_rewards_list = [
        f"+ {boost} {stat_name}" for stat_name, boost in ev_rewards.items() if boost > 0
    ]
    attributes = {
        "name": mon_info[2],
        "num": mon_info[0],
        "profile_img": None,
        "shiny_profile_img": None,
        "nft_img": None,
        "shiny_nft_img": None,
        "shiny_emoji": None,
        "emoji": None,
        "main_description": mon_info[3],
        "type1": mon_info[4],
        "type1_img": None,
        "type2": mon_info[5],
        "type2_img": None,
        "type_chart_img": None,
        "rarity": mon_info[17],
        "ability1": mon_info[6],
        "ability2": mon_info[7],
        "abilityh": mon_info[8],
        "evolution": mon_info[15],
        "evolution_lvl": mon_info[16],
        "evolution_tree": None,
        "ev_gains1": ev_rewards_list[0] if len(ev_rewards_list) > 0 else None,
        "ev_gains2": ev_rewards_list[1] if len(ev_rewards_list) > 1 else None,
        "base_hp": mon_info[9],
        "base_atk": mon_info[10],
        "base_def": mon_info[11],
        "base_spa": mon_info[12],
        "base_spd": mon_info[13],
        "base_spe": mon_info[14],
        "total_stats": sum(
            filter(
                None,
                [
                    mon_info[9],
                    mon_info[10],
                    mon_info[11],
                    mon_info[12],
                    mon_info[13],
                    mon_info[14],
                ],
            )
        ),
        "spawn_loc1": None,
        "spawn_time1": None,
        "spawn_loc2": None,
        "spawn_time2": None,
        "spawn_loc3": None,
        "spawn_time3": None,
        "spawn_rate": None,
        "spawn_table": None,
        "move_list": [
            move_info[0]
            for move_info in await RevomonMovesTable().get_moves_for_revomon(
                mon_dex_id=mon_info[0]
            )
        ],
        "cdex_tier": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][4],
        "cdex_description": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][3],
        "weakness": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][9],
        "meta_build": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][6],
        "meta_moves": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][5],
        "tips": (await CounterdexTable().get_info(revomon_name=mon_info[2].lower()))[0][
            7
        ],
        "counters": (
            await CounterdexTable().get_info(revomon_name=mon_info[2].lower())
        )[0][8],
    }
    return attributes


async def save_mon_imgs() -> None:
    print("Getting names of all Revomon...")
    all_mons_names = await RevomonTable().get_names()
    print("Got names of all Revomon")
    for mon_name in all_mons_names:
        print(f"Getting attribs for {mon_name}...")
        mon_attr = await get_attributes(mon_name)
        print(f"Got attribs for {mon_name}")

        try:
            # Check if the Profile image is already saved to data.Images
            with open(f"./data/Images/Revomon/{mon_name.title()}.png", "rb") as file:
                print(f"{mon_name} Profile image already exists")
        except FileNotFoundError:
            print(f"Getting profile image for {mon_name}...")
            mon_img_url = str(mon_attr["profile_img"])
            mon_img = requests.get(mon_img_url)
            # Check if the request was successful
            if mon_img.status_code == 200:
                # Open a local file in binary write mode
                with open(
                    f"./data/Images/Revomon/{mon_name.title()}.png", "wb"
                ) as file:
                    file.write(mon_img.content)
                print(f"Saved profile image for {mon_name}")

        try:
            # Check if the Shiny Profile image is already saved to data.Images
            with open(
                f"./data/Images/Revomon/shiny-{mon_name.title()}.png", "rb"
            ) as file:
                print(f"{mon_name} Shiny Profile image already exists")
        except FileNotFoundError:
            print(f"Getting shiny profile image for {mon_name}...")
            mon_shiny_img_url = str(mon_attr["shiny_profile_img"])
            mon_shiny_img = requests.get(mon_shiny_img_url)
            # Check if the request was successful
            if mon_shiny_img.status_code == 200:
                # Open a local file in binary write mode
                with open(
                    f"./data/Images/Revomon/shiny-{mon_name.title()}.png", "wb"
                ) as file:
                    file.write(mon_shiny_img.content)
                print(f"Saved shiny profile image for {mon_name}")

        try:
            # Check if the NFT Profile image is already saved to data.Images
            with open(
                f"./data/Images/Revomon/{mon_name.title()}-nft.png", "rb"
            ) as file:
                print(f"{mon_name} NFT image already exists")
        except FileNotFoundError:
            print(f"Getting nft image for {mon_name}...")
            mon_nft_img_url = str(mon_attr["nft_img"])
            mon_nft_img = requests.get(mon_nft_img_url)
            # Check if the request was successful
            if mon_nft_img.status_code == 200:
                # Open a local file in binary write mode
                with open(
                    f"./data/Images/Revomon/{mon_name.title()}-nft.png", "wb"
                ) as file:
                    file.write(mon_nft_img.content)
                print(f"Saved nft image for {mon_name}")

        try:
            # Check if the Shiny NFT Profile image is already saved to data.Images
            with open(
                f"./data/Images/Revomon/shiny-{mon_name.title()}-nft.png", "rb"
            ) as file:
                print(f"{mon_name} Shiny Profile image already exists")
        except FileNotFoundError:
            print(f"Getting shiny nft image for {mon_name}...")
            mon_shiny_nft_img_url = str(mon_attr["shiny_nft_img"])
            mon_shiny_nft_img = requests.get(mon_shiny_nft_img_url)
            # Check if the request was successful
            if mon_shiny_nft_img.status_code == 200:
                # Open a local file in binary write mode
                with open(
                    f"./data/Images/Revomon/shiny-{mon_name.title()}-nft.png",
                    "wb",
                ) as file:
                    file.write(mon_shiny_nft_img.content)
                print(f"Saved shiny nft image for {mon_name}")
        print(f"Saved all images for {mon_name}")
    print("All Revomon images saved")


async def save_type_imgs() -> None:
    print("Getting names of all Types...")
    elements: list[str] = await TypesTable().get_mono_types()
    print("Got names of all Types")
    for element in elements:
        element = element.lower()
        try:
            # Check if the Profile image is already saved to data.Images
            with open(f"./data/Images/Types/{element}.png", "rb") as file:
                print(f"{element} Type image already exists")
        except FileNotFoundError:
            print(f"Getting Type image for {element}...")
            element_img_url = (
                f"https://app-v2.revomon.io/static/images/types/{element}.png"
            )
            element_img = requests.get(element_img_url)
            # Check if the request was successful
            if element_img.status_code == 200:
                # Open a local file in binary write mode
                with open(f"./data/Images/Types/{element}.png", "wb") as file:
                    file.write(element_img.content)
                print(f"Saved Type image for {element}")
    print("All Type images saved")


async def get_natures() -> Any:
    natures = await NaturesTable().get_names()
    return natures


def get_nature_mods(nature: str) -> dict[str, int | float]:
    nature_mods: dict[str, int | float] = {
        "hp": 1,
        "atk": 1,
        "def": 1,
        "spa": 1,
        "spd": 1,
        "spe": 1,
    }
    nature = nature.title()
    if (
        nature == "Adamant"
        or nature == "Brave"
        or nature == "Lonely"
        or nature == "Naughty"
    ):
        nature_mods["atk"] = 1.1
    elif (
        nature == "Bold" or nature == "Impish" or nature == "Lax" or nature == "Relaxed"
    ):
        nature_mods["def"] = 1.1
    elif (
        nature == "Modest" or nature == "Mild" or nature == "Quiet" or nature == "Rash"
    ):
        nature_mods["spa"] = 1.1
    elif (
        nature == "Calm"
        or nature == "Careful"
        or nature == "Gentle"
        or nature == "Sassy"
    ):
        nature_mods["spd"] = 1.1
    elif (
        nature == "Hasty" or nature == "Jolly" or nature == "Naive" or nature == "Timid"
    ):
        nature_mods["spe"] = 1.1
    if nature == "Bold" or nature == "Modest" or nature == "Calm" or nature == "Timid":
        nature_mods["atk"] = 0.9
    elif (
        nature == "Lonely"
        or nature == "Mild"
        or nature == "Gentle"
        or nature == "Hasty"
    ):
        nature_mods["def"] = 0.9
    elif (
        nature == "Adamant"
        or nature == "Impish"
        or nature == "Careful"
        or nature == "Jolly"
    ):
        nature_mods["spa"] = 0.9
    elif (
        nature == "Naughty" or nature == "Lax" or nature == "Rash" or nature == "Naive"
    ):
        nature_mods["spd"] = 0.9
    elif (
        nature == "Brave"
        or nature == "Relaxed"
        or nature == "Quiet"
        or nature == "Sassy"
    ):
        nature_mods["spe"] = 0.9
    return nature_mods


async def get_perferred_natures(revomon_name: str) -> list[str]:
    perferred_natures = []
    mon_attr = await get_attributes(revomon_name)
    natures = await get_natures()
    meta_build = mon_attr["meta_build"]
    for nature in natures:
        if meta_build and nature in meta_build:  # type: ignore
            perferred_natures.append(nature)
    return perferred_natures


def get_evo_trees() -> list[Any | str]:
    evo_trees = []
    evo_tree = ""
    # Fetch data from the Revomon API
    url = "https://api.revomon.io/revomon/revodex"
    payload: dict[str, Any] = {"idsCatchedRevomon": []}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()

        for revomon in sorted(data["data"]["revomons"], key=lambda x: x["idRevodex"]):
            evolution = (
                revomon["evolution"].lower() if revomon["evolution"] != "" else None
            )
            evo_lvl = (
                revomon["levelEvolution"] if revomon["levelEvolution"] != 0 else None
            )
            if evolution is not None:
                if evo_tree == "":
                    if revomon["name"].lower() == "vyphern":
                        evo_tree += f"| {revomon['name'].title()} -lvl {evo_lvl}-> Wyverdant |\n"
                        evo_trees.append(evo_tree)
                        evo_tree = ""
                        continue
                    evo_tree += f"| {revomon['name'].title()} -lvl {evo_lvl}-> "
                else:
                    evo_tree += f"{revomon['name'].title()} -lvl {evo_lvl}-> "
            elif evolution is None:
                if evo_tree == "":
                    if revomon["name"].lower() == "wyverdant":
                        continue
                    evo_tree += f"| {revomon['name'].title()} |\n"
                else:
                    evo_tree += f"{revomon['name'].title()} |\n"
                evo_trees.append(evo_tree)
                evo_tree = ""

    return evo_trees


async def get_book_of_mon_names() -> list[list[str]]:
    row = 0
    book = []
    pages = []
    names = await RevomonTable().get_names()
    for name in names:
        if name == "wyverdant":
            continue
        pages.append(name)
        if name == "vyphern":
            pages.append("wyverdant")
        if name == names[-1]:
            book.append(pages)
            return book
        if (await RevomonTable().get_info(name))[0][8] is None:
            row += 1
            if row == 4:
                book.append(pages)
                pages = []
                row = 0
            continue
    return book


async def get_book_of_land_ids(token_ids: list[Any] | None = None) -> list[list[int]]:
    row = 0
    book = []
    pages = []
    count = 0
    if token_ids is None:
        token_ids = await OwnedLandsTable().get_ids()
    for id in token_ids:
        pages.append(id)
        count += 1
        if id == token_ids[-1]:
            book.append(pages)
            return book
        if count == 3:
            row += 1
            count = 0
            if row == 4:
                book.append(pages)
                pages = []
                row = 0

            continue
    return book


def get_grade(grade_percent: float) -> str:
    grade_letter = ""
    if grade_percent >= 90.9:
        grade_letter = "A+"
    elif 80 <= grade_percent < 90.9:
        grade_letter = "A"
    elif 70 <= grade_percent <= 79.9:
        grade_letter = "B"
    elif 50 <= grade_percent < 70.9:
        grade_letter = "C"
    elif 40 <= grade_percent < 50.9:
        grade_letter = "D"
    elif 30 <= grade_percent < 40.9:
        grade_letter = "F"
    elif 0 <= grade_percent < 30.9:
        grade_letter = "F-"
    return grade_letter


def get_stat_weights(
    base_stats: dict[str, Any], mon_name: str = ""
) -> tuple[dict[str, float], str]:
    """Determine stat weights based on base stats and competitive roles."""
    weights = {
        "hp": 1.0,
        "atk": 1.0,
        "def": 1.0,
        "spa": 1.0,
        "spd": 1.0,
        "spe": 1.0,
    }

    # 1. Standardize base stats
    b = {
        "hp": base_stats.get("base_hp", 0),
        "atk": base_stats.get("base_atk", 0),
        "def": base_stats.get("base_def", 0),
        "spa": base_stats.get("base_spa", 0),
        "spd": base_stats.get("base_spd", 0),
        "spe": base_stats.get("base_spe", 0),
    }

    # 2. Identify Primary Role
    # Check for bias (e.g. Physical vs Special)
    role = "Balanced"

    # Offense Bias
    if b["atk"] > b["spa"] * 1.2:
        role = "Physical Attacker"
        weights["atk"] = 2.0
        weights["spa"] = 0.1  # Moot stat
    elif b["spa"] > b["atk"] * 1.2:
        role = "Special Attacker"
        weights["spa"] = 2.0
        weights["atk"] = 0.1  # Moot stat
    elif b["atk"] > 90 and b["spa"] > 90:
        role = "Mixed Attacker"
        weights["atk"] = 1.5
        weights["spa"] = 1.5

    # Speed Bias
    if b["spe"] >= 100:
        role = f"Fast {role}"
        weights["spe"] = 2.0
    elif b["spe"] <= 50:
        # Potential Trick Room Role
        role = f"Slow {role}"
        weights["spe"] = 0.5  # Spe matters less or we want 0 (handled in appraise)

    # Defensive Bias
    if b["def"] > 100 or b["spd"] > 100 or b["hp"] > 110:
        role = f"Defensive {role}"
        weights["hp"] = 1.5
        if b["def"] >= b["spd"]:
            weights["def"] = 1.8
            weights["spd"] = 1.2
        else:
            weights["spd"] = 1.8
            weights["def"] = 1.2

    return weights, role


def evaluate_stat_iv(stat_name: str, iv: int, weight: float, role: str) -> int:
    """Evaluate an IV based on its role and importance."""
    # Special Case: 0 Atk for Special Attackers
    if stat_name == "atk" and "Special Attacker" in role:
        if iv <= 5:
            return 31  # Treating 0-5 as 'perfect' 31
        return max(0, 31 - iv)  # Penalize higher Atk

    # Special Case: 0 Spe for Slow/Trick Room
    if stat_name == "spe" and "Slow" in role:
        # In Trick Room, 0 is perfect. We can't know for sure if they want TR,
        # but weighting it lower in get_stat_weights handles the 'meh' factor.
        # If we want to be NASA level, we'd check moves for Trick Room.
        pass

    return iv


async def appraise_revomon(
    mon_stats: dict[str, Any],
) -> dict[str, str | int | float | dict[str, float]] | None:
    try:
        mon_stats["lvl"] = 100
        mon_attrib = await get_attributes(mon_stats["mon_name"])

        # 1. Standard Ivy Totals
        iv_raw = {
            "hp": mon_stats["hp_iv"],
            "atk": mon_stats["atk_iv"],
            "def": mon_stats["def_iv"],
            "spa": mon_stats["spa_iv"],
            "spd": mon_stats["spd_iv"],
            "spe": mon_stats["spe_iv"],
        }
        iv_total = sum(iv_raw.values())

        # 2. Competitive Weighting logic
        weights, role = get_stat_weights(mon_attrib, mon_stats["mon_name"])

        # 3. Calculate Weighted Score
        weighted_iv_sum: float = 0.0
        max_weighted_iv_sum: float = 0.0

        for stat, iv in iv_raw.items():
            w = weights[stat]
            transformed_iv = evaluate_stat_iv(stat, iv, w, role)
            weighted_iv_sum += transformed_iv * w
            max_weighted_iv_sum += 31 * w

        grade_decimal = weighted_iv_sum / max_weighted_iv_sum
        grade_percent = round(grade_decimal * 100, 1)

        # 4. Nature Bonus
        nature_mods = get_nature_mods(mon_stats["mon_nature"])
        nature_quality = "Neutral"

        # Check if nature boosts a high-weight stat and drops a low-weight one
        boosted_stat = [s for s, m in nature_mods.items() if m > 1.0]
        dropped_stat = [s for s, m in nature_mods.items() if m < 1.0]

        if boosted_stat and dropped_stat:
            b_stat = boosted_stat[0]
            d_stat = dropped_stat[0]
            if weights[b_stat] >= 1.5 and weights[d_stat] <= 0.5:
                nature_quality = "Perfect"
                grade_percent = min(100.0, grade_percent + 5.0)
            elif weights[b_stat] < 1.0:
                nature_quality = "Poor"
                grade_percent = max(0.0, grade_percent - 5.0)
            elif weights[b_stat] >= 1.2:
                nature_quality = "Good"
                grade_percent = min(100.0, grade_percent + 2.5)

        grade_letter = get_grade(grade_percent)

        appraise_result = {
            "mon_name": mon_stats["mon_name"],
            "mon_nature": mon_stats["mon_nature"],
            "nature_quality": nature_quality,
            "mon_ability": mon_stats["mon_ability"],
            "role": role,
            "iv_total": iv_total,
            "grade_percent": grade_percent,
            "grade_letter": grade_letter,
            "stat_weights": weights,
        }

        print(
            f"Grading Done for {mon_stats['mon_name']}: {grade_letter} ({grade_percent}%) as {role}"
        )
        return appraise_result

    except Exception as e:
        print(f"An error occurred while running the 'appraise_revomon' function: {e}")
        import traceback

        traceback.print_exc()
        return None


def create_graded_mon_img(
    curr_stats: dict[str, Any],
    score_percentage: float | None = None,
    image_dir: str | None = None,
) -> Any:
    # Directory containing the images
    image_dir = "./data/Images/Revomon"
    iv_stats = {
        "HP": curr_stats["hp_iv"],
        "ATK": curr_stats["atk_iv"],
        "DEF": curr_stats["def_iv"],
        "SPA": curr_stats["spa_iv"],
        "SPD": curr_stats["spd_iv"],
        "SPE": curr_stats["spe_iv"],
    }

    # Image dimensions
    width = 750
    height = 1050  # Keeping the original height

    # Margins and spacings
    margin_left = 10
    margin_top = 20
    text_spacing = 10
    chart_spacing = 30

    # Create output buffer
    stats_buffer = io.BytesIO()

    # Create a new image with black background
    graded_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    draw = ImageDraw.Draw(graded_image)

    # Define fonts
    name_font: Any
    small_font: Any
    try:
        name_font = ImageFont.truetype("data/fonts/CabalBold.ttf", 60)
        small_font = ImageFont.truetype("data/fonts/Cabal.ttf", 25)
    except OSError:
        name_font = ImageFont.load_default(60)
        small_font = ImageFont.load_default(40)

    # Add name text to top left
    name_text = curr_stats["mon_name"]
    name_text_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    name_text_size = (
        name_text_bbox[2] - name_text_bbox[0],
        name_text_bbox[3] - name_text_bbox[1],
    )
    name_text_offset = (margin_left, margin_top)
    draw.text(name_text_offset, name_text, font=name_font, fill=(255, 255, 255, 255))

    # Add nature and ability text
    nature_ability_text = f"{curr_stats['mon_nature']} - {curr_stats['mon_ability']}"

    nature_ability_text_bbox = draw.textbbox(
        (0, 0), nature_ability_text, font=small_font
    )
    nature_ability_text_size = (
        nature_ability_text_bbox[2] - nature_ability_text_bbox[0],
        nature_ability_text_bbox[3] - nature_ability_text_bbox[1],
    )

    nature_ability_text_offset = (
        margin_left,
        (name_text_offset[1] + name_text_size[1] + text_spacing) + 20,
    )

    draw.text(
        nature_ability_text_offset,
        nature_ability_text,
        font=small_font,
        fill=(255, 255, 255, 255),
    )

    # Load the mon image
    if curr_stats["shiny"]:
        filename = f"shiny-{curr_stats['mon_name'].title()}.png"
    else:
        filename = f"{curr_stats['mon_name'].title()}.png"
    mon_image_path = f"{image_dir}/{filename}"
    # Calculate centered offset for mon image (default values if missing)
    mon_image_offset = (
        int((width - 400) / 2),
        int(nature_ability_text_offset[1] + nature_ability_text_size[1] + text_spacing),
    )
    mon_image_height = 400

    try:
        mon_image = Image.open(mon_image_path).convert("RGBA")

        # Resize the mon image to fit within a designated area
        mon_image.thumbnail((400, 400))

        # Calculate centered offset for mon image
        mon_image_offset = (
            int((width - mon_image.width) / 2),  # Center horizontally
            int(
                nature_ability_text_offset[1]
                + nature_ability_text_size[1]
                + text_spacing
            ),  # Position below text
        )
        graded_image.paste(mon_image, mon_image_offset, mon_image.convert("RGBA"))
        mon_image_height = mon_image.height
    except OSError:
        print(f"Image for {curr_stats['mon_name']} not found at {mon_image_path}")

    # Create stats bar chart and add it to the image
    stats_values = list(iv_stats.values())[::-1]
    stats_names = list(iv_stats.keys())[::-1]

    stats_fig = go.Figure(
        go.Bar(
            x=stats_values,
            y=stats_names,
            orientation="h",
            marker=dict(
                color="rgba(0, 0, 255, 0.6)",
                line=dict(color="rgba(0, 0, 255, 1.0)", width=2),
            ),
            text=[f"<b>{value}<b>" for value in stats_values],
            textposition=[
                "outside" if value < 10 else "inside" for value in stats_values
            ],
            textfont=dict(color="white", size=20, family="ARIAL"),
        )
    )
    stats_fig.update_layout(
        title=dict(
            text="<b>IV Stats<b>",
            y=1,
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(color="white", size=40, family="ARIAL"),
            automargin=True,
            yref="container",
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            zeroline=True,
            tickfont=dict(color="white", size=20, family="ARIAL"),
            domain=[0.15, 1],
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            showticklabels=True,
            zeroline=True,
            tickfont=dict(color="white", size=20, family="ARIAL"),
        ),
        barmode="stack",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=0, r=20, t=0, b=0),
        height=350,  # height of bar chart
        showlegend=False,
    )

    stats_fig.write_image(stats_buffer, format="png")
    stat_bar_chart_image = Image.open(stats_buffer)

    # Position the stat bar chart below the mon image, centered on the x-axis
    mon_image_bottom = int(mon_image_offset[1] + mon_image_height)
    stat_bar_position = (
        int((width - stat_bar_chart_image.width) // 2),  # Center horizontally
        int(mon_image_bottom + chart_spacing),  # Position below mon image with spacing
    )
    graded_image.paste(
        stat_bar_chart_image,
        (stat_bar_position[0], stat_bar_position[1]),
        stat_bar_chart_image.convert("RGBA"),
    )

    stats_buffer.close()

    if score_percentage is not None:
        # Create SCORE gauge indicator
        score_buffer = io.BytesIO()
        score_fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score_percentage,
                domain={"x": [0, 0], "y": [0, 0]},
                align="center",
                gauge={
                    "bar": {
                        "color": "rgba(0, 250, 125, 0.8)",
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.5,
                    },
                    "axis": {"range": [None, 100]},
                    "bgcolor": "rgba(0, 0, 0, 0)",
                    "steps": [
                        {
                            "range": [0, 30],
                            "color": "red",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [30, 40],
                            "color": "orangered",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [40, 50],
                            "color": "orange",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [50, 70],
                            "color": "yellow",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [70, 80],
                            "color": "springgreen",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [80, 90],
                            "color": "limegreen",
                            "line": {"color": "black", "width": 2},
                        },
                        {
                            "range": [90, 101],
                            "color": "green",
                            "line": {"color": "black", "width": 2},
                        },
                    ],
                },
                number={
                    "prefix": f"{curr_stats['grade_letter']}<br>",
                    "font": {
                        "size": 30,
                        "color": "white",
                    },
                    "suffix": "%",
                    "valueformat": ".1f",
                },
            )
        )

        score_fig.update_layout(
            paper_bgcolor="rgba(0, 0, 0, 0)",
            font={"color": "white", "family": "ARIAL"},
            height=275,
        )
        score_fig.write_image(score_buffer, format="png")
        score_gauge_image = Image.open(score_buffer)

        # Calculate top right corner position for score gauge
        image_width, image_height = graded_image.size
        score_gauge_position = (
            image_width
            - (score_gauge_image.width - (graded_image.width // 4))
            + 30,  # Right edge minus score gauge width and margin
            -60,  # Top margin
        )
        graded_image.paste(
            score_gauge_image,
            (score_gauge_position[0], score_gauge_position[1]),
            score_gauge_image.convert("RGBA"),
        )

        # Add underline for Name text
        grade = curr_stats["grade_letter"]
        if grade == "A+":
            underline_color = "green"  # Green underline
        elif grade == "A":
            underline_color = "limegreen"  # Light green underline
        elif grade == "B":
            underline_color = "springgreen"  # Orange underline
        elif grade == "C":
            underline_color = "yellow"  # Red underline
        elif grade == "D":
            underline_color = "orange"  # Dark red underline
        elif grade == "F":
            underline_color = "orangered"  # Black underline
        elif grade == "F-":
            underline_color = "red"  # White underline
        underline_thickness = 4

        underline_length = int(name_text_size[0])  # Underline slightly longer than text

        name_text_underline_image = Image.new(
            "RGBA", (underline_length, underline_thickness), (0, 0, 0, 0)
        )  # Transparent background
        name_text_underline_draw = ImageDraw.Draw(name_text_underline_image)
        name_text_underline_draw.line(
            [
                (0, underline_thickness // 2),
                (underline_length, underline_thickness // 2),
            ],
            fill=underline_color,
            width=underline_thickness,
        )

        name_text_underline_offset = (
            int(name_text_offset[0]),
            int(name_text_offset[1] + name_text_size[1] + 20),
        )  # Adjust y-offset based on preference
        graded_image.paste(
            name_text_underline_image,
            name_text_underline_offset,
            name_text_underline_image.convert("RGBA"),
        )

        # Add catch id text to bottom right corner
        catch_id_text = f"{curr_stats['catch_id']}"
        catch_id_font = ImageFont.truetype("data/fonts/Cabal.ttf", 20)
        catch_id_text_bbox = draw.textbbox((0, 0), catch_id_text, font=catch_id_font)
        catch_id_text_size = (
            catch_id_text_bbox[2] - catch_id_text_bbox[0],
            catch_id_text_bbox[3] - catch_id_text_bbox[1],
        )
        catch_id_text_position = (
            image_width
            - margin_left
            - catch_id_text_size[0]
            - 5,  # Right edge minus score gauge width and margin
            image_height - margin_top - catch_id_text_size[1],  # Top margin
        )
        draw = ImageDraw.Draw(graded_image)
        draw.rounded_rectangle(
            (
                catch_id_text_position[0] - 5,
                catch_id_text_position[1],
                catch_id_text_position[0] + catch_id_text_size[0] + 5,
                catch_id_text_position[1] + catch_id_text_size[1] + 5,
            ),
            fill="white",
            radius=5,
            width=3,
        )
        draw.text(
            catch_id_text_position,
            catch_id_text,
            fill="black",
            font=catch_id_font,
        )

        score_buffer.close()

    return graded_image
