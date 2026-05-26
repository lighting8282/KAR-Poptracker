from PIL import Image
import shutil
import os

dump = r"C:\Users\turtl\AppData\Roaming\Dolphin Emulator\Dump\Textures\GKYE01"
out = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images"

# one_hp and full_heal -> use the hp_up heart icon
shutil.copy(os.path.join(out, "hp_up.png"), os.path.join(out, "one_hp.png"))
shutil.copy(os.path.join(out, "hp_up.png"), os.path.join(out, "full_heal.png"))
print("Saved one_hp.png and full_heal.png")

# checkbox fillers -> use the checkbox icon from dump
checkbox_src = os.path.join(dump, "tex1_128x120_a0539f59ee1e54ff_0.png")
shutil.copy(checkbox_src, os.path.join(out, "checkbox_filler_city.png"))
shutil.copy(checkbox_src, os.path.join(out, "checkbox_filler_air.png"))
shutil.copy(checkbox_src, os.path.join(out, "checkbox_filler_top.png"))
print("Saved checkbox_filler_city/air/top.png")

# filler -> crop pink Kirby circle from Kirby sheet
kirby_sheet = Image.open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - Miscellaneous - Kirby.png")
# Sheet is 424x456, pink Kirby circle is in row 3
kirby_circle = kirby_sheet.crop((55, 291, 122, 358))
kirby_circle = kirby_circle.resize((64, 64), Image.LANCZOS)
kirby_circle.save(os.path.join(out, "filler.png"))
print("Saved filler.png")

# patch_cap_increase -> use the weight bag icon (weight_up)
shutil.copy(os.path.join(out, "weight_up.png"), os.path.join(out, "patch_cap_increase.png"))
print("Saved patch_cap_increase.png")

print("\nDone!")
