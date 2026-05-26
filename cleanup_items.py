import json

REMOVE = {
    # Regular Up patches (fake)
    "boost_up", "charge_up", "defense_up", "glide_up",
    "offense_up", "top_speed_up", "turn_up", "weight_up",
    # All Down patches
    "boost_down", "charge_down", "defense_down", "glide_down",
    "offense_down", "top_speed_down", "turn_down", "weight_down",
    "hp_down", "all_down"
}

NEW_SIZE = 48

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

for root in PACKS:
    # 1. Clean items.json
    items_path = root + r"\items\items.json"
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)
    items = [i for i in items if i["codes"] not in REMOVE]
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)
    print(f"Updated items.json in {root}")

    # 2. Clean layout + resize
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    for grid_key in layout:
        for content in layout[grid_key]["content"]:
            for inner in content["content"]:
                # Bump size
                inner["item_height"] = NEW_SIZE
                inner["item_width"] = NEW_SIZE
                # Remove unwanted items from rows, drop empty rows
                new_rows = []
                for row in inner["rows"]:
                    new_row = [item for item in row if item not in REMOVE]
                    if new_row:
                        new_rows.append(new_row)
                inner["rows"] = new_rows

    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"Updated layouts/items.json in {root}")

print("\nDone!")
