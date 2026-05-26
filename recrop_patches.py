from PIL import Image
import os

sheet = Image.open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - City Trial - Power Up Patches.png")
out = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\items"

# Sheet is 1185x755
# Column order: Boost, Charge, Defense, Glide, HP, Offense, TopSpeed, Turn, Weight
col_names = ["boost", "charge", "defense", "glide", "hp", "offense", "top_speed", "turn", "weight"]
col_x     = [10, 141, 272, 403, 524, 655, 786, 917, 1048]
icon_w = 120
icon_h = 130

row_top_y    = 15   # Top row — colored (active)
row_bottom_y = 305  # Bottom row — grey (inactive)

# All icon (bottom center)
all_colored_x, all_colored_y = 490, 500
all_grey_x,    all_grey_y    = 490, 500  # same position, grey version is below colored
all_size = 200

for i, name in enumerate(col_names):
    x = col_x[i]

    # Colored (top row) — active state
    colored = sheet.crop((x, row_top_y, x + icon_w, row_top_y + icon_h))
    colored = colored.resize((64, 64), Image.LANCZOS)
    colored.save(os.path.join(out, f"{name}_up_active.png"))

    # Grey (bottom row) — inactive state
    grey = sheet.crop((x, row_bottom_y, x + icon_w, row_bottom_y + icon_h))
    grey = grey.resize((64, 64), Image.LANCZOS)
    grey.save(os.path.join(out, f"{name}_up_inactive.png"))

    print(f"Saved {name}_up_active.png and {name}_up_inactive.png")

# All Up — colored and grey
all_colored = sheet.crop((all_colored_x, all_colored_y, all_colored_x + all_size, all_colored_y + 150))
all_colored = all_colored.resize((64, 64), Image.LANCZOS)
all_colored.save(os.path.join(out, "all_up_active.png"))

all_grey = sheet.crop((all_grey_x, all_grey_y + 160, all_grey_x + all_size, all_grey_y + 310))
all_grey = all_grey.resize((64, 64), Image.LANCZOS)
all_grey.save(os.path.join(out, "all_up_inactive.png"))

print("Saved all_up_active.png and all_up_inactive.png")
print("\nDone!")
