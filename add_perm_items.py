import json, shutil, os

PERM_ITEMS = [
    ("boost_up_perm",     "boost"),
    ("charge_up_perm",    "charge"),
    ("defense_up_perm",   "defense"),
    ("glide_up_perm",     "glide"),
    ("hp_up_perm",        "hp"),
    ("offense_up_perm",   "offense"),
    ("top_speed_up_perm", "top_speed"),
    ("turn_up_perm",      "turn"),
    ("weight_up_perm",    "weight"),
]

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

src_images = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\items"

# Build new item entries
new_items = []
for code, base in PERM_ITEMS:
    new_items.append({
        "name": code,
        "type": "consumable",
        "img": f"images/items/{base}_up_active.png",
        "img_inactive": f"images/items/{base}_up_inactive.png",
        "initial_active_state": False,
        "max_quantity": 99,
        "overlay_align": "right",
        "codes": code
    })

for root in PACKS:
    # Copy images to packs folder if needed
    items_img_dir = root + r"\images\items"
    os.makedirs(items_img_dir, exist_ok=True)
    for code, base in PERM_ITEMS:
        for suffix in ["active", "inactive"]:
            fname = f"{base}_up_{suffix}.png"
            src = os.path.join(src_images, fname)
            dst = os.path.join(items_img_dir, fname)
            if os.path.abspath(src) != os.path.abspath(dst):
                shutil.copy(src, dst)

    # Add to items.json
    items_path = root + r"\items\items.json"
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)
    # Remove any existing perm entries first to avoid dupes
    existing_codes = {i["codes"] for i in new_items}
    items = [i for i in items if i["codes"] not in existing_codes]
    items.extend(new_items)
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)
    print(f"Updated items.json in {root}")

    # Add to layout — insert perm items as their own rows
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    perm_row1 = ["boost_up_perm", "charge_up_perm", "defense_up_perm", "glide_up_perm", "hp_up_perm"]
    perm_row2 = ["offense_up_perm", "top_speed_up_perm", "turn_up_perm", "weight_up_perm"]

    for grid_key in layout:
        for content in layout[grid_key]["content"]:
            for inner in content["content"]:
                # Remove existing perm entries first
                inner["rows"] = [
                    [item for item in row if item not in existing_codes]
                    for row in inner["rows"]
                ]
                inner["rows"] = [r for r in inner["rows"] if r]
                # Add perm rows at the top
                inner["rows"] = [perm_row1, perm_row2] + inner["rows"]

    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"Updated layouts/items.json in {root}")

print("\nDone!")
