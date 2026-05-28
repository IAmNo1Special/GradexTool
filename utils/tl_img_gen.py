from PIL import Image, ImageDraw, ImageFont

from data.gradexDB import RevomonTable
from utils.revomon_utils import get_attributes


def create_base_tier_list(
    width,
    height,
    row_gap=10,
    font_path="data/fonts/CabalBold.ttf",
    font_size=20,
    image_paths=None,
):
    """Creates the base tier list image with colored headers and black rows.

    Args:
        width: Width of the base image.
        height: Height of the base image.
        row_gap: Size of the gap between rows (default: 10).
        font_path: Path to the font file for tier labels (default: "CabalBold.ttf").
        font_size: Size of the font for tier labels (default: 20).
        image_paths: Dictionary with tier labels as keys and lists of image paths as values.

    Returns:
        An Image object representing the base tier list image.
    """
    if image_paths is None:
        image_paths = {"S": [], "A": [], "B": [], "C": [], "D": []}

    # Create an empty image with a white background
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Define colors for each tier
    tiers = [
        ("S", (255, 105, 97)),
        ("A", (255, 179, 71)),
        ("B", (253, 253, 150)),
        ("C", (255, 255, 204)),
        ("D", (119, 221, 119)),
    ]

    image_size = 100  # Adjust the size of the image as needed
    max_images_per_row = (width - 100) // (
        image_size + 10
    )  # Calculate max images per row based on width

    total_height = 0
    tier_heights = []

    # Calculate the height needed for each tier based on the number of images
    for label, _ in tiers:
        num_images = len(image_paths[label])
        rows_needed = (
            num_images + max_images_per_row - 1
        ) // max_images_per_row  # Calculate rows needed
        tier_height = (
            rows_needed * (image_size + 10) + row_gap
        )  # Calculate tier height
        tier_heights.append(tier_height)
        total_height += tier_height

    # Draw the rectangles and text for each tier
    y_offset = 0
    for idx, (label, color) in enumerate(tiers):
        tier_height = tier_heights[idx]
        y_start = y_offset + row_gap
        y_end = y_start + tier_height - row_gap
        draw.rectangle([0, y_start, 100, y_end], fill=color)
        text_position = (50, (y_start + y_end) // 2)
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(
            (
                text_position[0] - text_width // 2,
                text_position[1] - text_height // 2,
            ),
            label,
            fill="black",
            font=font,
        )

        row_width = (max_images_per_row * (image_size + 10)) + 100
        draw.rectangle(
            [100, y_start, min(row_width, width - row_gap), y_end], fill="black"
        )
        y_offset += tier_height

    return image


def create_tier_list_with_images(
    width,
    height,
    image_paths,
    row_gap=10,
    font_path="data/fonts/CabalBold.ttf",
    font_size=20,
):
    """Creates a tier list image with the given Revomon images in their correct tiers.

    Args:
        width: Width of the base image.
        height: Height of the base image.
        image_paths: Dictionary with tier labels as keys and lists of image paths as values.
        row_gap: Size of the gap between rows (default: 10).
        font_path: Path to the font file for tier labels (default: "CabalBold.ttf").
        font_size: Size of the font for tier labels (default: 20).

    Returns:
        An Image object representing the tier list with the Revomon images.

    Example:
    image_paths = {
        "S": [],
        "A": [],
        "B": [],
        "C": [],
        "D": []
    }

    for name in RevomonTable().get_names():
        attribs = get_attributes(name)
        if attribs["evolution"] == "None":
            img_path = f"data/Images/Revomon/{name}.png"

            tier = attribs["cdex_tier"]
            if tier == "S":
                image_paths["S"].append(img_path)
            elif tier == "A":
                image_paths["A"].append(img_path)
            elif tier == "B":
                image_paths["B"].append(img_path)
            elif tier == "C":
                image_paths["C"].append(img_path)
            elif tier == "D":
                image_paths["D"].append(img_path)

    tier_list_image = create_tier_list_with_images(1800, 900, image_paths)
    tier_list_image.show()
    tier_list_image.save("tier_list.png")
    """
    # Create the base tier list
    base_image = create_base_tier_list(
        width, height, row_gap, font_path, font_size, image_paths
    )
    ImageDraw.Draw(base_image)

    # Define the positions for each tier
    tier_positions = {
        "S": (0, row_gap, 100, 0),
        "A": (0, 0, 100, 0),
        "B": (0, 0, 100, 0),
        "C": (0, 0, 100, 0),
        "D": (0, 0, 100, 0),
    }

    image_size = 100  # Adjust the size of the image as needed
    max_images_per_row = (width - 100) // (
        image_size + 10
    )  # Calculate max images per row based on width

    y_offset = 0

    # Draw the images in their reective tiers
    for tier, paths in image_paths.items():
        num_images = len(paths)
        rows_needed = (
            num_images + max_images_per_row - 1
        ) // max_images_per_row
        tier_height = rows_needed * (image_size + 10) + row_gap
        tier_positions[tier] = (
            0,
            y_offset + row_gap,
            100,
            y_offset + tier_height - row_gap,
        )

        x_offset = 110  # Start placing images to the right of the colored tier label boxes
        y_start = tier_positions[tier][1]
        # y_end = tier_positions[tier][3]
        # y_start_row = y_start

        for img_path in paths:
            try:
                revomon_img = Image.open(img_path).convert("RGBA")
                revomon_img = revomon_img.resize(
                    (image_size, image_size), Image.Resampling.LANCZOS
                )
                base_image.paste(revomon_img, (x_offset, y_start), revomon_img)
                x_offset += image_size + 10  # Add space between images
                if (
                    x_offset + image_size > width
                ):  # If the row is full, move to the next row
                    x_offset = 110
                    y_start += image_size + 10
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

        y_offset += tier_height

    return base_image


# Example usage
if __name__ == "__main__":
    image_paths = {"S": [], "A": [], "B": [], "C": [], "D": []}

    for name in RevomonTable().get_names():
        attribs = get_attributes(name)
        if attribs["evolution"] == "None":
            img_path = f"data/Images/Revomon/{name}.png"

            tier = attribs["cdex_tier"]
            if tier == "S":
                image_paths["S"].append(img_path)
            elif tier == "A":
                image_paths["A"].append(img_path)
            elif tier == "B":
                image_paths["B"].append(img_path)
            elif tier == "C":
                image_paths["C"].append(img_path)
            elif tier == "D":
                image_paths["D"].append(img_path)

    tier_list_image = create_tier_list_with_images(1800, 900, image_paths)
    tier_list_image.show()
    tier_list_image.save("tier_list.png")
