import shutil
import os

dump = r"C:\Users\turtl\AppData\Roaming\Dolphin Emulator\Dump\Textures\GKYE01"
out = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images"

# Stadium icons from 128x120 dump textures
stadium_map = {
    "tex1_128x120_3199bcbe1f889850_0.png": "stadium_drag_race",       # steering wheel
    "tex1_128x120_3db3e63b4136c979_0.png": "stadium_air_glider",      # wing
    "tex1_128x120_58db3e4adb1ab5d9_0.png": "stadium_destruction_derby", # bomb
    "tex1_128x120_85c9fee59ed51f04_0.png": "stadium_target_flight",   # targeting circle
    "tex1_128x120_982cdf46bc9c877a_0.png": "stadium_kirby_melee",     # circular arrows
    "tex1_128x120_f252eea0a4457a1a_0.png": "stadium_high_jump",       # jumping figure
    "tex1_128x120_fee328920e041eeb_0.png": "stadium_vs_king_dedede",  # GC controller
}

# Warpstar from 64x64 for Single Race
single_race_src = "tex1_64x64_30783a2c3912c150_14.png"  # Warpstar

for src_file, base_name in stadium_map.items():
    src = os.path.join(dump, src_file)
    dst = os.path.join(out, base_name + ".png")
    shutil.copy(src, dst)
    print(f"Copied {base_name}.png")

# Multi-variant stadiums reuse the same icon
variants = {
    "stadium_drag_race": range(1, 5),        # 1-4
    "stadium_destruction_derby": range(1, 6), # 1-5
    "stadium_kirby_melee": range(1, 3),       # 1-2
}
for base, rng in variants.items():
    src = os.path.join(out, base + ".png")
    for n in rng:
        dst = os.path.join(out, f"{base}_{n}.png")
        shutil.copy(src, dst)
        print(f"Copied {base}_{n}.png")

# Single race 1-9 uses Warpstar
shutil.copy(os.path.join(dump, single_race_src), os.path.join(out, "stadium_single_race.png"))
for n in range(1, 10):
    shutil.copy(os.path.join(out, "stadium_single_race.png"), os.path.join(out, f"stadium_single_race_{n}.png"))
    print(f"Copied stadium_single_race_{n}.png")

# Single unlocks
shutil.copy(os.path.join(dump, "tex1_128x120_85c9fee59ed51f04_0.png"), os.path.join(out, "stadium_target_flight.png"))
shutil.copy(os.path.join(dump, "tex1_128x120_3db3e63b4136c979_0.png"), os.path.join(out, "stadium_air_glider.png"))
shutil.copy(os.path.join(dump, "tex1_128x120_f252eea0a4457a1a_0.png"), os.path.join(out, "stadium_high_jump.png"))
shutil.copy(os.path.join(dump, "tex1_128x120_fee328920e041eeb_0.png"), os.path.join(out, "stadium_vs_king_dedede.png"))

print("\nDone!")
