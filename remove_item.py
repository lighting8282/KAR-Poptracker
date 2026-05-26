import json

REMOVE = {"all_up"}

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

for root in PACKS:
    # Remove from items.json
    items_path = root + r"\items\items.json"
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)
    items = [i for i in items if i["codes"] not in REMOVE]
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)

    # Remove from layout
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)
    for key in layout:
        for section in layout[key]["content"]:
            if "rows" in section:
                section["rows"] = [[i for i in row if i not in REMOVE] for row in section["rows"]]
                section["rows"] = [r for r in section["rows"] if r]
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)

    print(f"Done: {root}")

print("Complete!")
