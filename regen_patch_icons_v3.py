"""
Rebuild patch icons:
  - Symbol:  cropped from sprite sheet (row 1 = colored, row 3 = grey)
  - Label:   drawn fresh with PIL (Arial Black, colored + black outline)
             matching the game's style
Final output: 128x128 RGBA (higher source res = sharper when PopTracker scales)
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

SRC = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - City Trial - Power Up Patches.png"
PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

ICON_W     = 128
SYMBOL_H   = 96    # top portion
LABEL_H    = 32    # bottom strip
ICON_H     = SYMBOL_H + LABEL_H   # = 128
FONT_SIZE  = 18
OUTLINE    = 2

FONT = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", FONT_SIZE)

# ── Label text and colour per stat ───────────────────────────────────────────
LABELS = {
    "boost_up":     ("Boost",     (255,  50, 220)),
    "charge_up":    ("Charge",    (255, 210,   0)),
    "defense_up":   ("Defense",   ( 80, 110, 255)),
    "glide_up":     ("Glide",     (200, 240, 180)),
    "hp_up":        ("HP",        (255,  50,  50)),
    "offense_up":   ("Offense",   (255, 130,  30)),
    "top_speed_up": ("Top Speed", (  0, 210, 255)),
    "turn_up":      ("Turn",      ( 50, 220,  50)),
    "weight_up":    ("Weight",    (210, 160,  60)),
    "all_up":       ("All Up",    (255, 255, 255)),
}

# ── Symbol column bounds ─────────────────────────────────────────────────────
COLS = {
    "boost_up":     (13,   127),
    "charge_up":    (130,  253),
    "defense_up":   (255,  395),
    "glide_up":     (396,  530),
    "hp_up":        (527,  657),
    "offense_up":   (650,  793),
    "top_speed_up": (790,  920),
    "turn_up":      (918, 1048),
    "weight_up":    (1046,1175),
    "all_up":       (490,  670),
}

ROW_COLORED = (35,  157)
ROW_GREY    = (297, 418)
ALL_ROW     = (505, 665)


def trim_and_fit(arr, x0, x1, y0, y1, w, h):
    """Crop, trim transparent border, scale to fit w×h centred."""
    region = arr[y0:y1, x0:x1]
    alpha = region[:, :, 3]
    rows = np.where(np.any(alpha > 15, axis=1))[0]
    cols_ = np.where(np.any(alpha > 15, axis=0))[0]
    if not len(rows) or not len(cols_):
        return Image.new("RGBA", (w, h), (0,0,0,0))
    r0,r1 = rows[0], rows[-1]+1
    c0,c1 = cols_[0], cols_[-1]+1
    piece = Image.fromarray(region[r0:r1, c0:c1])
    iw, ih = piece.size
    scale = min(w/iw, h/ih) * 0.92      # slight padding
    nw, nh = max(1,int(iw*scale)), max(1,int(ih*scale))
    resized = piece.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0,0,0,0))
    canvas.alpha_composite(resized, ((w-nw)//2, (h-nh)//2))
    return canvas


def draw_label(text, color, w, h, arrow):
    """Draw text with thick black outline, centred in w×h."""
    # Render at 3× then scale down for crisp sub-pixel antialiasing
    scale = 3
    big_font = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", FONT_SIZE * scale)
    bw, bh = w * scale, h * scale
    big = Image.new("RGBA", (bw, bh), (0,0,0,0))
    draw = ImageDraw.Draw(big)
    full_text = f"{text}{arrow}"
    bbox = draw.textbbox((0,0), full_text, font=big_font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    tx = (bw - tw) // 2 - bbox[0]
    ty = (bh - th) // 2 - bbox[1]
    out = OUTLINE * scale
    for dx in range(-out, out+1):
        for dy in range(-out, out+1):
            if dx*dx + dy*dy <= out*out:
                draw.text((tx+dx, ty+dy), full_text, font=big_font, fill=(0,0,0,255))
    draw.text((tx, ty), full_text, font=big_font, fill=(*color, 255))
    return big.resize((w, h), Image.LANCZOS)


img = Image.open(SRC).convert("RGBA")
arr = np.array(img)
saved = 0

for base_name, (label_text, color) in LABELS.items():
    col = COLS[base_name]
    sym_row = ALL_ROW if base_name == "all_up" else ROW_COLORED
    grey_row = ALL_ROW if base_name == "all_up" else ROW_GREY

    for suffix, row, arrow in [("active", sym_row, "↑"), ("inactive", grey_row, "↓")]:
        sym = trim_and_fit(arr, *col, *row, ICON_W, SYMBOL_H)
        # HP and all_up have no grey row — desaturate instead
        if suffix == "inactive" and base_name in ("hp_up", "all_up"):
            sym = sym.convert("LA").convert("RGBA")
            txt_color = (160, 160, 160)
        elif suffix == "inactive":
            txt_color = (160, 160, 160)
        else:
            txt_color = color

        lbl = draw_label(label_text, txt_color, ICON_W, LABEL_H, arrow)

        canvas = Image.new("RGBA", (ICON_W, ICON_H), (0,0,0,0))
        canvas.alpha_composite(sym, (0, 0))
        canvas.alpha_composite(lbl, (0, SYMBOL_H))

        fname = f"{base_name}_{suffix}.png"
        for root in PACKS:
            canvas.save(os.path.join(root, "images", "items", fname))
        saved += 1

print(f"Saved {saved} icons.")
