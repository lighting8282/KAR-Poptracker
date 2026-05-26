import json

REMOVE = {
    "filler", "one_hp", "full_heal",
    "checkbox_filler_city", "checkbox_filler_air", "checkbox_filler_top"
}

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

for root in PACKS:
    # Clean items.json
    items_path = root + r"\items\items.json"
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)
    items = [i for i in items if i["codes"] not in REMOVE]
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)
    print(f"Updated items.json in {root}")

    # Clean layout
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    for grid_key in layout:
        for content in layout[grid_key]["content"]:
            for inner in content["content"]:
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
