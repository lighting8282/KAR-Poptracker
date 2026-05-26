import json

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

SIZE = 36

def make_grid(rows):
    return {
        "type": "itemgrid",
        "item_margin": "2, 2",
        "h_alignment": "left",
        "item_h_alignment": "center",
        "item_v_alignment": "center",
        "item_height": SIZE,
        "item_width": SIZE,
        "rows": rows
    }

STADIUM_SECTIONS = [
    ("Drag Race", [
        ["stadium_drag_race_1", "stadium_drag_race_2", "stadium_drag_race_3", "stadium_drag_race_4"]
    ]),
    ("Destruction Derby", [
        ["stadium_destruction_derby_1", "stadium_destruction_derby_2", "stadium_destruction_derby_3", "stadium_destruction_derby_4", "stadium_destruction_derby_5"]
    ]),
    ("Kirby Melee", [
        ["stadium_kirby_melee_1", "stadium_kirby_melee_2"]
    ]),
    ("Single Race", [
        ["stadium_single_race_1", "stadium_single_race_2", "stadium_single_race_3", "stadium_single_race_4", "stadium_single_race_5", "stadium_single_race_6", "stadium_single_race_7", "stadium_single_race_8", "stadium_single_race_9"]
    ]),
    ("Other", [
        ["stadium_high_jump", "stadium_target_flight", "stadium_air_glider", "stadium_vs_king_dedede"]
    ]),
]

# Build labeled sections using groups (guaranteed header support in PopTracker)
content = []
for label_text, rows in STADIUM_SECTIONS:
    content.append({
        "type": "group",
        "header": label_text,
        "content": make_grid(rows)
    })

stadium_grid = {
    "type": "array",
    "orientation": "vertical",
    "margin": "2, 2",
    "content": content
}

for root in PACKS:
    path = root + r"\layouts\items.json"
    with open(path, encoding="utf-8") as f:
        layout = json.load(f)
    layout["stadium_grid"] = stadium_grid
    with open(path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print("Updated " + path)

print("Done!")
