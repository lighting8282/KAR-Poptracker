"""
Remove course map_locations from individual check child nodes.
They should only have the checklist map_location.
The parent course node (MAGMA FLOWS, etc.) retains its course map_location
and PopTracker aggregates all children under it — so clicking the course dot
still shows all checks for that course, and completion state is shared.
"""

import json

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

COURSE_MAPS = {"Air Ride", "Top Ride"}


def strip_course_locs_from_check_nodes(node, removed_count):
    """
    For any node that has sections (a leaf check node), remove any course map_locations.
    Keep only checklist map_locations on those nodes.
    Recurse into children.
    """
    if node.get("sections"):
        original = node.get("map_locations", [])
        filtered = [ml for ml in original if ml.get("map") not in COURSE_MAPS]
        if len(filtered) != len(original):
            removed_count[0] += len(original) - len(filtered)
            node["map_locations"] = filtered

    for child in node.get("children", []):
        strip_course_locs_from_check_nodes(child, removed_count)


def process_file(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    removed_count = [0]
    for node in data:
        strip_course_locs_from_check_nodes(node, removed_count)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return removed_count[0]


if __name__ == "__main__":
    for root in PACKS:
        print(f"Processing {root}")
        n = process_file(root + r"\locations\Air Ride.json")
        print(f"  Air Ride.json: removed {n} course map_locations from check nodes")
        n = process_file(root + r"\locations\Top Ride.json")
        print(f"  Top Ride.json: removed {n} course map_locations from check nodes")
    print("Done!")
