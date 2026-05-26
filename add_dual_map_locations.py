"""
Add course-map map_location entries to each individual check node so checks
appear on BOTH the course select map AND the checklist grid.

Each child check node currently only has a checklist map_location.
This script copies the parent course node's map_location (e.g. "Air Ride")
down to every child, so each check shows on both layers.
"""

import json
import shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

COURSE_MAPS = {"Air Ride", "Top Ride"}


def propagate_map_locations(node, inherited_course_locs, added_count):
    """
    Walk the tree. When we reach a node that has course map_locations,
    pass them down. For leaf check nodes (those with only checklist map_locations),
    prepend the inherited course location so the check appears on both maps.
    """
    # Collect any course map_locations THIS node owns
    own_course_locs = [
        ml for ml in node.get("map_locations", [])
        if ml.get("map") in COURSE_MAPS
    ]

    # The course locations to pass to children = own course locs (if any) else inherited
    course_locs_for_children = own_course_locs if own_course_locs else inherited_course_locs

    children = node.get("children", [])

    for child in children:
        # Check if this child is a "leaf check node":
        # it has sections AND its map_locations only contain checklist entries
        child_maplocs = child.get("map_locations", [])
        child_has_checklist = any(
            "Checklist" in ml.get("map", "") for ml in child_maplocs
        )
        child_has_course = any(
            ml.get("map") in COURSE_MAPS for ml in child_maplocs
        )

        if child_has_checklist and not child_has_course and course_locs_for_children:
            # Prepend the course map_locations so the check appears on the course map too
            child["map_locations"] = course_locs_for_children + child_maplocs
            added_count[0] += 1

        # Recurse into this child's children
        propagate_map_locations(child, course_locs_for_children, added_count)


def process_file(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    added_count = [0]
    for node in data:
        propagate_map_locations(node, [], added_count)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return added_count[0]


if __name__ == "__main__":
    for root in PACKS:
        print(f"Processing {root}")

        ar_path = root + r"\locations\Air Ride.json"
        n = process_file(ar_path)
        print(f"  Air Ride.json: {n} check nodes updated with course map_location")

        tr_path = root + r"\locations\Top Ride.json"
        n = process_file(tr_path)
        print(f"  Top Ride.json: {n} check nodes updated with course map_location")

    print("\nDone!")
