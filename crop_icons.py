from PIL import Image
import os

sheet = Image.open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - City Trial - Power Up Patches.png")
out = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images"
os.makedirs(out, exist_ok=True)

# Sheet is 1185x755
# 9 columns: Boost, Charge, Defense, Glide, HP, Offense, TopSpeed, Turn, Weight
# Row 1 = Up (colored), Row 2 = Up Permanent (lighter), Row 3 = Down (grey)
# Bottom center = All Up / All Down

col_names = ["boost", "charge", "defense", "glide", "hp", "offense", "top_speed", "turn", "weight"]

# Approximate column x-starts (left edge of each icon)
col_x = [10, 141, 272, 403, 524, 655, 786, 917, 1048]
icon_w = 120
icon_h = 130

# Row y-starts
row1_y = 15   # Up (colored)
row2_y = 160  # Up Permanent (lighter)
row3_y = 305  # Down (grey)

# Crop Up patches
for i, name in enumerate(col_names):
    x = col_x[i]
    icon = sheet.crop((x, row1_y, x + icon_w, row1_y + icon_h))
    icon.save(os.path.join(out, f"{name}_up.png"))
    print(f"Saved {name}_up.png")

# Crop Up Permanent patches (lighter row)
for i, name in enumerate(col_names):
    x = col_x[i]
    icon = sheet.crop((x, row2_y, x + icon_w, row2_y + icon_h))
    icon.save(os.path.join(out, f"{name}_up_perm.png"))
    print(f"Saved {name}_up_perm.png")

# Crop Down patches
for i, name in enumerate(col_names):
    x = col_x[i]
    icon = sheet.crop((x, row3_y, x + icon_w, row3_y + icon_h))
    icon.save(os.path.join(out, f"{name}_down.png"))
    print(f"Saved {name}_down.png")

# All Up / All Down — centered at bottom of sheet
all_x = 490
all_y = 500
all_w = 200
all_h = 200
all_icon = sheet.crop((all_x, all_y, all_x + all_w, all_y + all_h))
all_icon.save(os.path.join(out, "all_up.png"))
all_icon.save(os.path.join(out, "all_down.png"))
print("Saved all_up.png and all_down.png")

print("\nDone! Check the images/ folder.")
