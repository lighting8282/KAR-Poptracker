import json

STADIUM_ITEMS = [
    ["stadium_drag_race_1", "stadium_drag_race_2", "stadium_drag_race_3", "stadium_drag_race_4"],
    ["stadium_destruction_derby_1", "stadium_destruction_derby_2", "stadium_destruction_derby_3", "stadium_destruction_derby_4", "stadium_destruction_derby_5"],
    ["stadium_kirby_melee_1", "stadium_kirby_melee_2"],
    ["stadium_single_race_1", "stadium_single_race_2", "stadium_single_race_3", "stadium_single_race_4", "stadium_single_race_5"],
    ["stadium_single_race_6", "stadium_single_race_7", "stadium_single_race_8", "stadium_single_race_9"],
    ["stadium_high_jump", "stadium_target_flight", "stadium_air_glider", "stadium_vs_king_dedede"],
]

STADIUM_CODES = {item for row in STADIUM_ITEMS for item in row}

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

def make_grid(rows, size=48):
    return {
        "type": "itemgrid",
        "item_margin": "2, 2",
        "h_alignment": "left",
        "item_h_alignment": "center",
        "item_v_alignment": "center",
        "item_height": size,
        "item_width": size,
        "rows": rows
    }

def make_label(text):
    return {
        "type": "label",
        "text": text,
        "margin": "0, 4, 0, 2"
    }

for root in PACKS:
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    for grid_key in layout:
        # Collect all current rows and strip stadium items
        all_rows = []
        for content in layout[grid_key]["content"]:
            for inner in content["content"]:
                if isinstance(inner, dict) and "rows" in inner:
                    all_rows = inner["rows"]

        powerup_rows = [
            [item for item in row if item not in STADIUM_CODES]
            for row in all_rows
        ]
        powerup_rows = [r for r in powerup_rows if r]

        # Side-by-side layout: power ups on left, stadiums on right
        layout[grid_key]["content"] = [
            {
                "type": "array",
                "orientation": "horizontal",
                "margin": "0,0",
                "content": [
                    {
                        "type": "array",
                        "orientation": "vertical",
                        "margin": "0, 0, 8, 0",
                        "content": [
                            make_label("Power Ups"),
                            make_grid(powerup_rows)
                        ]
                    },
                    {
                        "type": "array",
                        "orientation": "vertical",
                        "margin": "0,0",
                        "content": [
                            make_label("Stadiums"),
                            make_grid(STADIUM_ITEMS)
                        ]
                    }
                ]
            }
        ]

    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"Updated layout in {root}")

print("\nDone!")
