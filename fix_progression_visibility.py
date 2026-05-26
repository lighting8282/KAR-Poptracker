"""
Move progression setting rules from access_rules -> visibility_rules.

access_rules failing  = RED  (inaccessible but in logic)
visibility_rules failing = GRAY (hidden / out of logic)

With "Show unreachable locations" enabled in PopTracker, gray dots appear
for checks whose visibility_rules fail, which is the desired behavior.
"""

import json, shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

PROGRESSION_RULES = {
    "air_ride_progression_time_attack",
    "air_ride_progression_free_run",
    "air_ride_progression_high_effort",
    "city_trial_progression_free_run",
    "city_trial_progression_multiplayer",
    "city_trial_progression_rng",
    "city_trial_progression_bust_vehicles",
    "city_trial_progression_high_effort",
    "top_ride_progression_time_attack",
    "top_ride_progression_free_run",
    "top_ride_progression_high_effort",
    "top_ride_progression_multiplayer",
}


def fix_rules(obj, moved):
    """
    On any dict that has access_rules:
    - Pull out any progression rules and put them in visibility_rules instead.
    - Leave non-progression access rules (and the space placeholder) alone.
    """
    access = obj.get("access_rules", [])
    vis = list(obj.get("visibility_rules", []))

    prog_rules = [r for r in access if r in PROGRESSION_RULES]
    other_rules = [r for r in access if r not in PROGRESSION_RULES]

    if prog_rules:
        for r in prog_rules:
            if r not in vis:
                vis.append(r)
        obj["access_rules"] = other_rules if other_rules else []
        obj["visibility_rules"] = vis
        moved[0] += len(prog_rules)


def walk(node, moved):
    fix_rules(node, moved)
    for sec in node.get("sections", []):
        fix_rules(sec, moved)
    for child in node.get("children", []):
        walk(child, moved)


FILES = [
    r"\locations\Air Ride.json",
    r"\locations\Top Ride.json",
    r"\locations\City Trial.json",
    r"\locations\Stadium.json",
]

for root in PACKS:
    print(f"Processing {root}")
    for fname in FILES:
        path = root + fname
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        moved = [0]
        for node in data:
            walk(node, moved)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        if moved[0]:
            print(f"  {fname.split(chr(92))[-1]}: {moved[0]} rules moved to visibility_rules")

print("\nDone!")
