"""
Rebuild patch icons by compositing:
  - Symbol from row 1 (colored) or row 3 (grey)
  - Text label cropped directly from the sprite sheet's label rows
    ("Boost↑" colored style for active, "Boost↓" grey style for inactive)
Output: 64×64 RGBA icons with symbol in upper ~48px and label in lower ~16px.
"""

from PIL import Image
import numpy as np
import os

SRC = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - City Trial - Power Up Patches.png"
PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
ICON_W      = 64
SYMBOL_H    = 48   # pixels allocated to symbol
LABEL_H     = 16   # pixels allocated to label
ICON_H      = SYMBOL_H + LABEL_H  # = 64

# Row bounds in sprite sheet
ROW_COLORED = (35,  157)   # fully colored symbols
ROW_GREY    = (297, 418)   # grey/inactive symbols
ROW_TXT_UP  = (419, 457)   # colored "Boost↑ Charge↑..." text
ROW_TXT_DN  = (457, 496)   # grey   "Boost↓ Charge↓..." text

# Symbol column bounds per stat (from symbol rows)
COLS = {
    "boost":     (13,   127),
    "charge":    (130,  253),
    "defense":   (255,  395),
    "glide":     (396,  530),
    "hp":        (527,  657),
    "offense":   (650,  793),
    "top_speed": (790,  920),
    "turn":      (918, 1048),
    "weight":    (1046,1175),
}

# Text label column bounds (may differ from symbol cols due to label widths)
TEXT_COLS = {
    "boost":     (10,   117),
    "charge":    (130,  257),
    "defense":   (263,  402),
    "glide":     (413,  510),
    "hp":        (535,  609),   # "HP" + "↑" are split groups — span both
    "offense":   (626,  766),
    "top_speed": (769,  934),   # "Top" + "Speed↑" are split — span both
    "turn":      (937, 1027),
    "weight":    (1050,1175),
}

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


def trim_crop(img_array, x0, x1, y0, y1):
    """Crop region and trim transparent padding, return PIL image."""
    region = img_array[y0:y1, x0:x1]
    alpha = region[:, :, 3]
    rows = np.where(np.any(alpha > 15, axis=1))[0]
    cols = np.where(np.any(alpha > 15, axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    r0, r1 = rows[0], rows[-1] + 1
    c0, c1 = cols[0], cols[-1] + 1
    return Image.fromarray(region[r0:r1, c0:c1])


def fit_into(img, w, h):
    """Resize image to fit in w×h, centred on transparent background."""
    iw, ih = img.size
    scale = min(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ox = (w - nw) // 2
    oy = (h - nh) // 2
    canvas.alpha_composite(resized, (ox, oy))
    return canvas


img = Image.open(SRC).convert("RGBA")
arr = np.array(img)

saved = 0
for stat, base_name in ITEMS.items():
    col = COLS[stat]

    # ── Active icon ───────────────────────────────────────────────────────────
    tcol = TEXT_COLS[stat]
    sym_active  = trim_crop(arr, *col,  *ROW_COLORED)
    txt_active  = trim_crop(arr, *tcol, *ROW_TXT_UP)

    if sym_active and txt_active:
        canvas = Image.new("RGBA", (ICON_W, ICON_H), (0, 0, 0, 0))
        canvas.alpha_composite(fit_into(sym_active, ICON_W, SYMBOL_H), (0, 0))
        canvas.alpha_composite(fit_into(txt_active, ICON_W, LABEL_H), (0, SYMBOL_H))
        for root in PACKS:
            canvas.save(os.path.join(root, "images", "items", f"{base_name}_active.png"))
        saved += 1

    # ── Inactive icon ─────────────────────────────────────────────────────────
    # HP has no grey symbol row — desaturate the colored symbol
    if stat == "hp":
        sym_inactive = sym_active.convert("LA").convert("RGBA") if sym_active else None
    else:
        sym_inactive = trim_crop(arr, *col, *ROW_GREY)

    txt_inactive = trim_crop(arr, *tcol, *ROW_TXT_DN)

    if sym_inactive and txt_inactive:
        canvas = Image.new("RGBA", (ICON_W, ICON_H), (0, 0, 0, 0))
        canvas.alpha_composite(fit_into(sym_inactive, ICON_W, SYMBOL_H), (0, 0))
        canvas.alpha_composite(fit_into(txt_inactive, ICON_W, LABEL_H), (0, SYMBOL_H))
        for root in PACKS:
            canvas.save(os.path.join(root, "images", "items", f"{base_name}_inactive.png"))
        saved += 1

# ── all_up: big circle + "All↑" / "All↓" labels ──────────────────────────────
all_sym_col   = (490, 670)
all_txt_up_y  = (660, 700)
all_txt_dn_y  = (700, 755)

sym_all = trim_crop(arr, *all_sym_col, 505, 665)
txt_all_up = trim_crop(arr, *all_sym_col, *all_txt_up_y)
txt_all_dn = trim_crop(arr, *all_sym_col, *all_txt_dn_y)

for suffix, sym, txt in [("active", sym_all, txt_all_up), ("inactive", sym_all, txt_all_dn)]:
    if sym and txt:
        if suffix == "inactive":
            sym = sym.convert("LA").convert("RGBA")
        canvas = Image.new("RGBA", (ICON_W, ICON_H), (0, 0, 0, 0))
        canvas.alpha_composite(fit_into(sym, ICON_W, SYMBOL_H), (0, 0))
        canvas.alpha_composite(fit_into(txt, ICON_W, LABEL_H), (0, SYMBOL_H))
        for root in PACKS:
            canvas.save(os.path.join(root, "images", "items", f"all_up_{suffix}.png"))
        saved += 1

print(f"Saved {saved} icons.")
