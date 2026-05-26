from PIL import Image

sheet = Image.open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - Miscellaneous - Kirby.png")
out = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\items"

# Row 4 circles (y~287-357), Row 5 circles (y~360-430)
# x positions spaced ~107px apart starting at ~51
circles = {
    "kirby_pink":   (13,  287, 93,  357),
    "kirby_yellow": (119, 287, 199, 357),
    "kirby_blue":   (225, 287, 305, 357),
    "kirby_red":    (331, 287, 411, 357),
    "kirby_green":  (13,  360, 93,  430),
    "kirby_purple": (119, 360, 199, 430),
    "kirby_brown":  (225, 360, 305, 430),
    "kirby_white":  (331, 360, 411, 430),
}

for name, (x1, y1, x2, y2) in circles.items():
    crop = sheet.crop((x1, y1, x2, y2)).resize((64, 64), Image.LANCZOS)
    crop.save(f"{out}\\sample_{name}.png")
    print(f"Saved sample_{name}.png")
