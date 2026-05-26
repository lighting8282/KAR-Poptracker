import json

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# Image bounds for each map
BOUNDS = {
    "Top Ride":   (640, 511),
    "Air Ride":   (9999, 9999),  # skip air ride for now
    "City Trial": (9999, 9999),
}

def fix_node(node, bounds):
    """Remove out-of-bounds map_locations from a node."""
    if "map_locations" in node:
        valid = []
        for ml in node["map_locations"]:
            x, y = ml.get("x", 0), ml.get("y", 0)
            w, h = bounds.get(ml.get("map", ""), (9999, 9999))
            if x <= w and y <= h and x >= 0 and y >= 0:
                valid.append(ml)
            else:
                print("  Removed out-of-bounds marker: " + node["name"] + " x=" + str(x) + " y=" + str(y))
        node["map_locations"] = valid
    for child in node.get("children", []):
        fix_node(child, bounds)

for root in PACKS:
    path = root + r"\locations\Top Ride.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for node in data:
        fix_node(node, BOUNDS)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("Fixed " + path)

print("Done!")
