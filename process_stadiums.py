from PIL import Image
import os, shutil

src = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\Stadiums"
dst_src = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\items"
dst_pack = r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride\images\items"

# Map source filename (no extension) to item code
mapping = {
    "air glider":          "stadium_air_glider",
    "destruction derby 1": "stadium_destruction_derby_1",
    "destruction derby 2": "stadium_destruction_derby_2",
    "destruction derby 3": "stadium_destruction_derby_3",
    "destruction derby 4": "stadium_destruction_derby_4",
    "destruction derby 5": "stadium_destruction_derby_5",
    "drag race 1":         "stadium_drag_race_1",
    "drag race 2":         "stadium_drag_race_2",
    "drag race 3":         "stadium_drag_race_3",
    "drag race 4":         "stadium_drag_race_4",
    "high jump":           "stadium_high_jump",
    "kirby melee 1":       "stadium_kirby_melee_1",
    "kirby melee 2":       "stadium_kirby_melee_2",
    "single race":         "stadium_single_race_1",
    "single race 2":       "stadium_single_race_2",
    "single race 3":       "stadium_single_race_3",
    "single race 4":       "stadium_single_race_4",
    "single race 5":       "stadium_single_race_5",
    "single race 6":       "stadium_single_race_6",
    "single race 7":       "stadium_single_race_7",
    "single race 8":       "stadium_single_race_8",
    "single race 9":       "stadium_single_race_9",
    "target flight":       "stadium_target_flight",
    "vs king dedede":      "stadium_vs_king_dedede",
}

TARGET_SIZE = (128, 96)  # 4:3 ratio, good icon size

for filename in os.listdir(src):
    name, ext = os.path.splitext(filename)
    name_lower = name.lower()

    if name_lower not in mapping:
        print(f"SKIPPED (no mapping): {filename}")
        continue

    code = mapping[name_lower]
    img = Image.open(os.path.join(src, filename)).convert("RGB")
    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    out_name = code + ".png"
    img.save(os.path.join(dst_src, out_name))
    shutil.copy(os.path.join(dst_src, out_name), os.path.join(dst_pack, out_name))
    print(f"Saved {out_name}")

print("\nDone!")
