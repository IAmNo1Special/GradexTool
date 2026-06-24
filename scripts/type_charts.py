import asyncio
import json
import logging
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from configs import (
    BASE_TYPES_FILE,
    BASE_TYPES_IMAGES_DIR,
    MISSING_TYPE_CHARTS_FILE,
    REVOMON_FILE,
    TYPE_CHART_IMAGES_DIR,
    TYPE_CHARTS_FILE,
)

logger = logging.getLogger(__name__)


# Canvas Settings
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 600
BG_COLOR = (0, 0, 0)  # Black
TEXT_COLOR = (255, 255, 255)  # White
ACCENT_COLOR = (150, 0, 255)  # Purple line color

# Layout Settings
SIDEBAR_WIDTH = 120
MARGIN = 40
LABEL_HEIGHT = 60
ROW_SPACING = 40
ICON_HEIGHT = 40  # Fixed height, width will be calculated based on aspect ratio

# Base effectiveness for the 18 types
BASE_TYPE_MULTIPLIERS: dict[str, dict[str, float]] = {}

REVOMON_TO_POKEMON_TYPE = {
    "neutral": "normal",
    "battle": "fighting",
    "sky": "flying",
    "toxic": "poison",
    "earth": "ground",
    "stone": "rock",
    "bug": "bug",
    "phantom": "ghost",
    "metal": "steel",
    "fire": "fire",
    "water": "water",
    "forest": "grass",
    "electric": "electric",
    "time": "psychic",
    "ice": "ice",
    "draconic": "dragon",
    "twilight": "dark",
    "spirit": "fairy",
}

POKEMON_TO_REVOMON_TYPE = {v: k for k, v in REVOMON_TO_POKEMON_TYPE.items()}


async def fetch_single_type(client: httpx.AsyncClient, rtype: str, ptype: str) -> None:
    url = f"https://pokeapi.co/api/v2/type/{ptype}/"
    resp = await client.get(url, timeout=15.0)
    resp.raise_for_status()
    data = resp.json()
    relations = data["damage_relations"]

    for entry in relations["double_damage_from"]:
        attacker_ptype = entry["name"]
        if attacker_ptype in POKEMON_TO_REVOMON_TYPE:
            BASE_TYPE_MULTIPLIERS[rtype][POKEMON_TO_REVOMON_TYPE[attacker_ptype]] = 2.0

    for entry in relations["half_damage_from"]:
        attacker_ptype = entry["name"]
        if attacker_ptype in POKEMON_TO_REVOMON_TYPE:
            BASE_TYPE_MULTIPLIERS[rtype][POKEMON_TO_REVOMON_TYPE[attacker_ptype]] = 0.5

    for entry in relations["no_damage_from"]:
        attacker_ptype = entry["name"]
        if attacker_ptype in POKEMON_TO_REVOMON_TYPE:
            BASE_TYPE_MULTIPLIERS[rtype][POKEMON_TO_REVOMON_TYPE[attacker_ptype]] = 0.0


async def fetch_base_type_multipliers() -> None:
    """Fetch type effectiveness from PokeAPI and populate BASE_TYPE_MULTIPLIERS dynamically."""
    logger.info("Fetching type effectiveness from PokeAPI...")
    global BASE_TYPE_MULTIPLIERS

    # Initialize dictionary
    BASE_TYPE_MULTIPLIERS = {rtype: {} for rtype in REVOMON_TO_POKEMON_TYPE.keys()}
    for rtype in BASE_TYPE_MULTIPLIERS:
        for rtype_attacker in REVOMON_TO_POKEMON_TYPE.keys():
            BASE_TYPE_MULTIPLIERS[rtype][rtype_attacker] = 1.0  # Default neutral

    async with httpx.AsyncClient() as client:
        tasks = []
        for rtype, ptype in REVOMON_TO_POKEMON_TYPE.items():
            tasks.append(fetch_single_type(client, rtype, ptype))
        await asyncio.gather(*tasks)


def get_font(size: int) -> Any:
    """Load a system font or fallback to default."""
    fonts_to_try = [
        "arial.ttf",
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf",
        "Arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_name in fonts_to_try:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def calculate_section_height(
    max_width: int | float, targets: list[Any | str], type_images: dict[str, Any]
) -> int:
    """Calculate the height required for a section based on target icons and wrapping."""
    if not targets:
        return 0

    height = LABEL_HEIGHT
    curr_x = 0
    icons_count = 0

    for t in targets:
        if t in type_images:
            original_img = type_images[t]
            aspect_ratio = original_img.width / original_img.height
            width = int(ICON_HEIGHT * aspect_ratio)

            if curr_x + width > max_width:
                curr_x = 0
                height += ICON_HEIGHT + 10

            curr_x += width + 15
            icons_count += 1

    if icons_count > 0:
        height += ICON_HEIGHT + ROW_SPACING

    return height


def draw_icon_section(
    img: Any,
    draw: Any,
    x_start: int,
    y_start: int,
    max_width: int | float,
    label: str,
    targets: list[Any | str],
    type_images: dict[str, Any],
    font: Any,
) -> int:
    """Draw a category label and its corresponding type icons with wrapping, centered."""
    if not targets:
        return y_start

    # Center the text label
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = int(x_start + (max_width - text_width) // 2)
    draw.text((text_x, y_start), label, font=font, fill=TEXT_COLOR)

    y = int(y_start + LABEL_HEIGHT)

    # Pre-calculate rows for centering
    rows = []
    current_row: list[tuple[Any, int]] = []
    current_row_width = 0

    for t in targets:
        if t in type_images:
            original_img = type_images[t]
            aspect_ratio = original_img.width / original_img.height
            width = int(ICON_HEIGHT * aspect_ratio)

            # Wrap if needed
            if current_row and current_row_width + width > max_width:
                # subtract the trailing 15 gap
                rows.append((current_row, current_row_width - 15))
                current_row = []
                current_row_width = 0

            current_row.append((original_img, width))
            current_row_width += width + 15

    if current_row:
        rows.append((current_row, current_row_width - 15))

    # Draw rows centered
    for row_icons, row_width in rows:
        curr_x = int(x_start + (max_width - row_width) // 2)
        for original_img, width in row_icons:
            icon = original_img.resize((width, ICON_HEIGHT))
            img.paste(icon, (curr_x, y), icon)
            curr_x += width + 15
        y += int(ICON_HEIGHT + 10)  # gap for next row

    # subtract the 10 gap from the last row and add ROW_SPACING
    return y - 10 + ROW_SPACING


def save_type_chart_images(
    types_dict: dict[str, dict[str, Any]],
    base_type_names: list[str],
    type_images: dict[str, Any],
) -> None:
    """Generate and save type chart images using Pillow."""
    TYPE_CHART_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    font_medium = get_font(30)

    for types_str, data in types_dict.items():
        # 1. Prepare Sidebar Icons
        t1 = data["type1"]
        t2 = data["type2"]

        sidebar_icons = []
        total_sidebar_height = 0

        for t in [t1, t2]:
            if t and t in type_images:
                orig = type_images[t]
                rotated = orig.rotate(90, expand=True)
                rot_w, rot_h = rotated.size
                scale = 70 / rot_w
                icon_w = 70
                icon_h = int(rot_h * scale)
                resized = rotated.resize((icon_w, icon_h))
                sidebar_icons.append(resized)
                total_sidebar_height += icon_h

        if len(sidebar_icons) > 1:
            total_sidebar_height += 20  # Spacing between icons

        # 2. Content Layout Calculation
        half_width = (CANVAS_WIDTH - SIDEBAR_WIDTH) // 2
        content_max_width = half_width - MARGIN * 1.5
        is_dual_type = t2 is not None

        # Offensive height (only for single type)
        y_off_needed = 0
        off_categories = [
            ("4x DAMAGE TO", 4.0),
            ("2x DAMAGE TO", 2.0),
            ("1/2 DAMAGE TO", 0.5),
            ("1/4 DAMAGE TO", 0.25),
            ("CAN'T DAMAGE", 0.0),
        ]
        if not is_dual_type:
            for _, val in off_categories:
                targets = [
                    bt
                    for bt in base_type_names
                    if (BASE_TYPE_MULTIPLIERS.get(bt, {}).get(t1, 1.0) if t1 else 1.0)
                    * (BASE_TYPE_MULTIPLIERS.get(bt, {}).get(t2, 1.0) if t2 else 1.0)
                    == val
                ]
                y_off_needed += calculate_section_height(
                    content_max_width, targets, type_images
                )

        # Defensive height
        y_def_needed = 0
        def_categories = [
            ("4x DAMAGE FROM", 4.0),
            ("2x DAMAGE FROM", 2.0),
            ("1/2 DAMAGE FROM", 0.5),
            ("1/4 DAMAGE FROM", 0.25),
            ("IMMUNE TO", 0.0),
        ]
        for _, val in def_categories:
            def_targets = [
                t for t, v in data.items() if t in base_type_names and v == val
            ]
            y_def_needed += calculate_section_height(
                content_max_width
                if not is_dual_type
                else (CANVAS_WIDTH - SIDEBAR_WIDTH - MARGIN * 2),
                def_targets,
                type_images,
            )

        content_height = max(y_off_needed, y_def_needed)
        actual_height = max(CANVAS_HEIGHT, content_height + (MARGIN * 2))
        img = Image.new("RGB", (CANVAS_WIDTH, actual_height), BG_COLOR)
        draw = ImageDraw.Draw(img)

        vertical_offset = (actual_height - content_height) // 2

        # 3. Draw Offensive Section (Left)
        y_off = vertical_offset
        if not is_dual_type:
            off_x = SIDEBAR_WIDTH + MARGIN
            for label, val in off_categories:
                targets = [
                    bt
                    for bt in base_type_names
                    if (BASE_TYPE_MULTIPLIERS.get(bt, {}).get(t1, 1.0) if t1 else 1.0)
                    * (BASE_TYPE_MULTIPLIERS.get(bt, {}).get(t2, 1.0) if t2 else 1.0)
                    == val
                ]
                y_off = draw_icon_section(
                    img,
                    draw,
                    off_x,
                    y_off,
                    content_max_width,
                    label,
                    targets,
                    type_images,
                    font_medium,
                )

        # 4. Draw Defensive Section (Right)
        y_def = vertical_offset
        def_x = SIDEBAR_WIDTH + (half_width if not is_dual_type else MARGIN)
        def_max_width = (
            content_max_width
            if not is_dual_type
            else (CANVAS_WIDTH - SIDEBAR_WIDTH - MARGIN * 2)
        )
        for label, val in def_categories:
            def_targets = [
                t for t, v in data.items() if t in base_type_names and v == val
            ]
            y_def = draw_icon_section(
                img,
                draw,
                def_x,
                y_def,
                def_max_width,
                label,
                def_targets,
                type_images,
                font_medium,
            )

        # 5. Finalize Sidebar
        draw.rectangle(
            [0, 0, SIDEBAR_WIDTH, actual_height], outline=ACCENT_COLOR, width=3
        )
        curr_sidebar_y = (actual_height - total_sidebar_height) // 2
        for icon in sidebar_icons:
            icon_w, icon_h = icon.size
            x_pos = (SIDEBAR_WIDTH - icon_w) // 2
            img.paste(icon, (x_pos, curr_sidebar_y), icon)
            curr_sidebar_y += icon_h + 20

        img.save(TYPE_CHART_IMAGES_DIR / f"{types_str}.png")
        logger.info(f"Generated chart for {types_str}")


async def get_type_charts(generate_images: bool = False) -> None:
    await fetch_base_type_multipliers()
    # Load required data
    with open(BASE_TYPES_FILE, encoding="utf-8") as f:
        base_type_names = json.load(f)

    with open(REVOMON_FILE, encoding="utf-8") as f:
        revomons = json.load(f)

    # Identify all unique type combinations present in the game
    unique_combinations: set[tuple[str | None, str | None]] = set()

    # 1. Ensure all 18 base types are included as single-type entries
    for bt in base_type_names:
        unique_combinations.add((bt.lower(), None))

    # 2. Add dual-type combinations from the revomon list
    for r in revomons:
        t1 = r.get("type1").lower() if r.get("type1") else None
        t2 = r.get("type2").lower() if r.get("type2") else None
        if t1 and t2:
            combo = tuple(sorted([t1, t2]))
            unique_combinations.add(combo)
        elif t1:
            unique_combinations.add((t1, None))

    types_list = []
    for t1, t2 in unique_combinations:
        # Build the underscore formatted types_str
        types_str = str(t1) + (f"_{t2}" if t2 else "")

        # Initialize entry
        type_entry: dict[str, Any] = {
            "types_str": types_str,
            "type1": t1,
            "type2": t2,
        }

        # Calculate effectiveness multipliers
        for target_type in base_type_names:
            m1 = BASE_TYPE_MULTIPLIERS.get(t1, {}).get(target_type, 1.0) if t1 else 1.0
            m2 = BASE_TYPE_MULTIPLIERS.get(t2, {}).get(target_type, 1.0) if t2 else 1.0
            type_entry[target_type] = m1 * m2

        types_list.append(type_entry)

    # Sort alphabetically by types_str
    types_list.sort(key=lambda x: str(x["types_str"]))

    # Assign sequential IDs and build dict
    types_dict: dict[str, dict[str, Any]] = {}
    for i, type_entry in enumerate(types_list, start=1):
        type_entry["idType"] = i
        types_dict[type_entry["types_str"]] = type_entry

    logger.info(f"Saving {len(types_dict)} types to {TYPE_CHARTS_FILE}...")
    TYPE_CHARTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TYPE_CHARTS_FILE, "w", encoding="utf-8") as f:
        json.dump(types_dict, f, indent=2, ensure_ascii=False)

    # Generate images if requested
    if generate_images:
        logger.info(f"\nGenerating type images for {len(types_dict)} types...")
        # Load base type images
        type_images = {}
        for img_file in BASE_TYPES_IMAGES_DIR.glob("*.png"):
            type_name = img_file.stem.lower()
            try:
                type_images[type_name] = Image.open(img_file).convert("RGBA")
            except (OSError, UnidentifiedImageError) as e:
                logger.error(f"Failed to load image {img_file}: {e}")

        save_type_chart_images(types_dict, base_type_names, type_images)

    # After generation, check which files are missing on disk
    missing_files: list[str] = []
    for types_str in types_dict.keys():
        if not (TYPE_CHART_IMAGES_DIR / f"{types_str}.png").exists():
            missing_files.append(str(types_str))

    # Save missing files list
    if missing_files:
        logger.info(
            f"Saving {len(missing_files)} missing images to {MISSING_TYPE_CHARTS_FILE}..."
        )
        with open(MISSING_TYPE_CHARTS_FILE, "w", encoding="utf-8") as f:
            json.dump(missing_files, f, indent=2, ensure_ascii=False)
    else:
        logger.info("No missing images found on disk.")
        if MISSING_TYPE_CHARTS_FILE.exists():
            MISSING_TYPE_CHARTS_FILE.unlink()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_type_charts(generate_images=True))
