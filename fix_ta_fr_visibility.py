"""
Add visibility_rules to Time Attack and Free Run checks that were missed.
Identifies them by their 'TA:' or 'FR:' name prefix.
Applies to both the child check nodes AND the parent sections.
"""

import json, shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# name prefix -> visibility rule to add
PREFIX_RULES = {
    "TA:": None,   # filled per-mode below
    "FR:": None,
}

def add_visibility_rule(obj, rule):
    vis = obj.get("visibility_rules", [])
    if rule not in vis:
        vis.append(rule)
        obj["visibility_rules"] = vis
        return True
    return False


def walk(node, ta_rule, fr_rule, added):
    name = node.get("name", "")

    # If this node itself is a TA/FR check node, add rule to the node
    if ta_rule and name.startswith("TA:"):
        if add_visibility_rule(node, ta_rule):
            added[0] += 1
    elif fr_rule and name.startswith("FR:"):
        if add_visibility_rule(node, fr_rule):
            added[0] += 1

    # Also check sections directly on this node
    for sec in node.get("sections", []):
        sname = sec.get("name", "")
        if ta_rule and sname.startswith("TA:"):
            if add_visibility_rule(sec, ta_rule):
                added[0] += 1
        elif fr_rule and sname.startswith("FR:"):
            if add_visibility_rule(sec, fr_rule):
                added[0] += 1

    for child in node.get("children", []):
        walk(child, ta_rule, fr_rule, added)


CONFIGS = [
    (r"\locations\Air Ride.json",
     "air_ride_progression_time_attack",
     "air_ride_progression_free_run"),
    (r"\locations\Top Ride.json",
     "top_ride_progression_time_attack",
     "top_ride_progression_free_run"),
]

for root in PACKS:
    print(f"Processing {root}")
    for fname, ta_rule, fr_rule in CONFIGS:
        path = root + fname
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        added = [0]
        for node in data:
            walk(node, ta_rule, fr_rule, added)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"  {fname.split(chr(92))[-1]}: {added[0]} visibility rules added")

print("\nDone!")
