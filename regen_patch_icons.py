"""
Re-crop patch icons from the original sprite sheet, removing all text labels.
Row 1 (colored) = active  (player has the buff)
Row 3 (grey)    = inactive (player hasn't gotten it yet)
"""

from PIL import Image, ImageEnhance
import numpy as np
import shutil, os

SRC   = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - City Trial - Power Up Patches.png"
PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
OUTPUT_SIZE = 64  # final icon size in px

# ── Column bounds (x_start, x_end) per stat ─────────────────────────────────
# Derived from grey row column detection; HP only appears in colored rows.
COLS = {
    "boost":     (13,   114),
    "charge":    (142,  240),
    "defense":   (258,  393),
    "glide":     (398,  521),
    "hp":        (529,  646),
    "offense":   (652,  789),
    "top_speed": (792,  917),
    "turn":      (919, 1045),
    "weight":   (1048, 1171),
}

# ── Row bounds (y_start, y_end) for each sprite row ──────────────────────────
ROW_COLORED = (35,  157)   # row 1 – fully colored symbols
ROW_GREY    = (297, 418)   # row 3 – grey/inactive symbols

# ── File name mapping ─────────────────────────────────────────────────────────
ITEMS = {
    "boost":     "boost_up",
    "charge":    "charge_up",
    "defense":   "defense_up",
    "glide":     "glide_up",
    "hp":        "hp_up",
    "offense":   "offense_up",
    "top_speed": "top_speed_up",
    "turn":      "turn_up",
    "weight":    "weight_up",
}

def crop_symbol(img, col_bounds, row_bounds):
    """Crop a symbol, trim transparent padding, then resize to OUTPUT_SIZE."""
    x0, x1 = col_bounds
    y0, y1 = row_bounds
    cropped = img.crop((x0, y0, x1, y1))
    # Trim transparent border
    arr = np.array(cropped)
    alpha = arr[:, :, 3]
    rows = np.where(np.any(alpha > 20, axis=1))[0]
    cols = np.where(np.any(alpha > 20, axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    r0, r1 = rows[0], rows[-1] + 1
    c0, c1 = cols[0], cols[-1] + 1
    trimmed = cropped.crop((c0, r0, c1, r1))
    # Make square, centred on transparent bg
    side = max(trimmed.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox = (side - trimmed.width) // 2
    oy = (side - trimmed.height) // 2
    square.paste(trimmed, (ox, oy))
    return square.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)


def to_grey(img):
    """Convert a colored icon to greyscale (for hp inactive fallback)."""
    grey = img.convert("LA").convert("RGBA")
    return grey


img = Image.open(SRC).convert("RGBA")
print(f"Sprite sheet: {img.size}")

saved = []
for stat, base_name in ITEMS.items():
    col = COLS[stat]

    # Active (colored)
    active = crop_symbol(img, col, ROW_COLORED)
    if active:
        for root in PACKS:
            p = os.path.join(root, "images", "items", f"{base_name}_active.png")
            active.save(p)
        saved.append(f"{base_name}_active.png")

    # Inactive (grey) — HP has no grey row sprite, so desaturate colored
    if stat == "hp":
        inactive = to_grey(active) if active else None
    else:
        inactive = crop_symbol(img, col, ROW_GREY)

    if inactive:
        for root in PACKS:
            p = os.path.join(root, "images", "items", f"{base_name}_inactive.png")
            inactive.save(p)
        saved.append(f"{base_name}_inactive.png")

# ── all_up: big circle at bottom of sheet ────────────────────────────────────
# Centered around x=528-660, y=505-665
all_active   = crop_symbol(img, (510, 670), (505, 668))
all_inactive = to_grey(all_active) if all_active else None
for suffix, icon in [("active", all_active), ("inactive", all_inactive)]:
    if icon:
        for root in PACKS:
            p = os.path.join(root, "images", "items", f"all_up_{suffix}.png")
            icon.save(p)
        saved.append(f"all_up_{suffix}.png")

print(f"Saved {len(saved)} icons:")
for s in saved:
    print(f"  {s}")
print("Done!")
