"""
Add text labels to the patch icons.
Draws a small label at the bottom of each icon with a semi-transparent
dark bar behind it so it reads cleanly on any background.
"""

from PIL import Image, ImageDraw, ImageFont
import os

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"
ICON_SIZE  = 64
FONT_SIZE  = 11
BAR_HEIGHT = 14   # height of the label bar at the bottom

LABELS = {
    "boost_up":     "Boost",
    "charge_up":    "Charge",
    "defense_up":   "Defense",
    "glide_up":     "Glide",
    "hp_up":        "HP",
    "offense_up":   "Offense",
    "top_speed_up": "Top Spd",
    "turn_up":      "Turn",
    "weight_up":    "Weight",
    "all_up":       "All Up",
}

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def add_label(img: Image.Image, text: str) -> Image.Image:
    """Draw a small label bar at the bottom of a 64x64 RGBA icon."""
    out = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(out)

    # Semi-transparent dark bar at the bottom
    bar_y = ICON_SIZE - BAR_HEIGHT
    bar = Image.new("RGBA", (ICON_SIZE, BAR_HEIGHT), (0, 0, 0, 160))
    out.alpha_composite(bar, (0, bar_y))

    # Measure text and center it
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (ICON_SIZE - tw) // 2
    ty = bar_y + (BAR_HEIGHT - th) // 2 - bbox[1]  # adjust for font baseline

    # White text with a 1px dark outline for clarity
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        draw.text((tx+dx, ty+dy), text, font=font, fill=(0, 0, 0, 200))
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    return out


saved = 0
for base_name, label in LABELS.items():
    for suffix in ("active", "inactive"):
        fname = f"{base_name}_{suffix}.png"
        src_path = PACKS[0] + r"\images\items\\" + fname
        if not os.path.exists(src_path):
            print(f"  MISSING: {fname}")
            continue
        img = Image.open(src_path).convert("RGBA")
        out = add_label(img, label)
        for root in PACKS:
            out.save(os.path.join(root, "images", "items", fname))
        saved += 1

print(f"Labelled {saved} icons.")
print("Done!")
