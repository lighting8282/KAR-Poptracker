import json

POWERUP_ROWS = [
    ["boost_up_perm", "charge_up_perm", "defense_up_perm", "glide_up_perm", "hp_up_perm"],
    ["offense_up_perm", "top_speed_up_perm", "turn_up_perm", "weight_up_perm"],
    ["hp_up", "all_up", "patch_cap_increase", "update"],
]

STADIUM_ROWS = [
    ["stadium_drag_race_1", "stadium_drag_race_2", "stadium_drag_race_3", "stadium_drag_race_4"],
    ["stadium_destruction_derby_1", "stadium_destruction_derby_2", "stadium_destruction_derby_3", "stadium_destruction_derby_4", "stadium_destruction_derby_5"],
    ["stadium_kirby_melee_1", "stadium_kirby_melee_2"],
    ["stadium_single_race_1", "stadium_single_race_2", "stadium_single_race_3", "stadium_single_race_4", "stadium_single_race_5"],
    ["stadium_single_race_6", "stadium_single_race_7", "stadium_single_race_8", "stadium_single_race_9"],
    ["stadium_high_jump", "stadium_target_flight", "stadium_air_glider", "stadium_vs_king_dedede"],
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

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

for root in PACKS:
    # 1. Fix items.json layout — power ups only
    layout_path = root + r"\layouts\items.json"
    layout = {
        "shared_item_grid_horizontal": {
            "type": "array",
            "orientation": "vertical",
            "margin": "0,0",
            "content": [make_grid(POWERUP_ROWS)]
        },
        "shared_item_grid_vertical": {
            "type": "array",
            "orientation": "vertical",
            "margin": "0,0",
            "content": [make_grid(POWERUP_ROWS)]
        },
        "stadium_grid": {
            "type": "array",
            "orientation": "vertical",
            "margin": "0,0",
            "content": [make_grid(STADIUM_ROWS)]
        }
    }
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"Updated layouts/items.json in {root}")

    # 2. Fix tracker.json — add Stadiums tab between Items and Settings
    tracker_path = root + r"\layouts\tracker.json"
    with open(tracker_path, encoding="utf-8") as f:
        tracker = json.load(f)

    for variant in tracker:
        dock = tracker[variant]["content"]["content"]
        for section in dock:
            if section.get("dock") in ["left", "bottom"]:
                content = section["content"]
                # Find the Items group and add Stadiums after it
                new_content = []
                for group in content:
                    new_content.append(group)
                    if group.get("header") == "Items":
                        new_content.append({
                            "type": "group",
                            "header": "Stadiums",
                            "dock": group.get("dock", "left"),
                            "margin": group.get("margin", "0,0,3,0"),
                            "content": {
                                "type": "layout",
                                "key": "stadium_grid"
                            }
                        })
                section["content"] = new_content

    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=4)
    print(f"Updated layouts/tracker.json in {root}")

print("\nDone!")
