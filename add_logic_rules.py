"""
Add access_rules to gated checks based on the AP world's KARRules.py logic.

A check that requires another check to be reachable gets access_rules that reference
those prerequisite sections. PopTracker will mark such checks as RED (inaccessible but
in logic) when prerequisites aren't met, and GREEN once they are.
"""

import json, re
import os

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# Build code → all section paths from location_mapping.lua
def parse_lua_mapping(root):
    with open(root + r"\scripts\autotracking\location_mapping.lua", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}')
    result = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        paths = re.findall(r'"([^"]+)"', m.group(2))
        result[code] = paths
    return result

# Build AP location name → code from KARLocations.py (via apworld)
import zipfile
def parse_apworld_locations():
    with zipfile.ZipFile(r"A:\Archipelago\custom_worlds\kirby_air_ride.apworld") as z:
        content = z.read("kirby_air_ride/KARLocations.py").decode("utf-8")
    pattern = re.compile(r'"((?:Air Ride|Top Ride|City Trial|Stadium)[^"]+)":\s*KARLocationData\(\s*(\d+),')
    return {m.group(1): int(m.group(2)) for m in pattern.finditer(content)}

# ── The logic rules from KARRules.py ─────────────────────────────────────────
# (gated_check_name, [prerequisite_check_names])
LOGIC_RULES = [
    # City Trial
    ("City Trial: Unlock Hydra Parts X, Y, and Z on the Checklist!",
     ["City Trial: Destroy all of the dilapidated houses!",
      "Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!",
      "Stadium: KIRBY MELEE (All) KO over 1,500 enemies!"]),
    ("City Trial: Unlock Dragoon Parts A, B, and C on the Checklist!",
     ["Stadium: HIGH JUMP Jump higher than 1,000 feet!",
      "Stadium: DESTRUCTION DERBY (All) KO enemies over 150 times!",
      "Stadium: KIRBY MELEE (All) KO over 1,500 enemies!"]),

    # Air Ride machine-gated checks
    ("Air Ride: Time Attack: MAGMA FLOWS Finish in under 03:15:00 on Shadow Star!",
     ["Air Ride: Defeat 10 or more enemies using the Quick Spin!"]),
    ("Air Ride: Time Attack: SKY SANDS Finish in under 02:40:00 on Wagon Star!",
     ["Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!"]),
    ("Air Ride: Free Run: FANTASY MEADOWS Do 1 lap under 00:23:00 on Wagon Star!",
     ["Air Ride: In any mode other than Free Run, reach the goal a total of 3 times!"]),
    ("Air Ride: Free Run: FROZEN HILLSIDE Do 1 lap under 01:10:00 on Formula Star!",
     ["Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:14:00!"]),
    ("Air Ride: Free Run: CELESTIAL VALLEY Do 1 lap under 01:02:00 on Slick Star!",
     ["Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!"]),
    ("Air Ride: Time Attack: FANTASY MEADOWS Finish in under 01:05:00 on Slick Star!",
     ["Air Ride: CHECKER KNIGHTS Finish 2 laps in under 03:05:00!"]),
    ("Air Ride: Free Run: MAGMA FLOWS Do 1 lap under 01:02:00 on Turbo Star!",
     ["Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!"]),
    ("Air Ride: Time Attack: FROZEN HILLSIDE Finish in under 03:10:00 on Turbo Star!",
     ["Air Ride: MAGMA FLOWS: Use all the volcano rails and finish in 1st place!"]),
    ("Air Ride: Time Attack: BEANSTALK PARK Finish in under 03:00:00 on Rocket Star!",
     ["Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!"]),
    ("Air Ride: Free Run: CHECKER KNIGHTS Do 1 lap under 01:25:00 on Rocket Star!",
     ["Air Ride: Free Run: MACHINE PASSAGE Finish 1 lap in under 01:05:00!"]),
    ("Air Ride: Free Run: BEANSTALK PARK Do 1 lap under 00:58:00 on Winged Star!",
     ["Air Ride: Finish in 1st place while flying through the air!"]),
    ("Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 02:58:00 on Jet Star!",
     ["Air Ride: MACHINE PASSAGE Race over 4,500 feet in 2 minutes!"]),
    ("Air Ride: Free Run: SKY SANDS Do 1 lap under 01:05:00 on Bulk Star!",
     ["Air Ride: Time Attack: CELESTIAL VALLEY Finish in under 03:20:00!"]),
    ("Air Ride: Free Run: MACHINE PASSAGE Do 1 lap under 00:57:00 on Swerve Star!",
     ["Air Ride: SKY SANDS Finish 2 laps in under 02:05:00!"]),
]


def find_section_in_json(data, target_path, set_rules):
    """Walk all nodes and sections; if a section/node path matches target_path,
    set its access_rules to set_rules."""
    updated = [0]
    def walk(node, cur_path):
        node_name = node.get("name", "")
        np = cur_path + "/" + node_name if cur_path else node_name
        if "@" + np == target_path:
            # Set on the node itself
            node["access_rules"] = set_rules
            updated[0] += 1
        for sec in node.get("sections", []):
            spath = "@" + np + "/" + sec.get("name", "")
            if spath == target_path:
                sec["access_rules"] = set_rules
                updated[0] += 1
        for c in node.get("children", []):
            walk(c, np)
    for n in data:
        walk(n, "")
    return updated[0]


def apply_rules_to_file(json_path, rules_for_paths):
    """rules_for_paths: dict of target_path -> [list of prerequisite section paths]"""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    total = 0
    for target_path, prereq_paths in rules_for_paths.items():
        # Build the rule: require ALL prerequisites (AND), using @path syntax
        rule = list(prereq_paths)
        n = find_section_in_json(data, target_path, rule)
        total += n
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return total


if __name__ == "__main__":
    ap_locs = parse_apworld_locations()
    # Use one pack copy's lua mapping (they should be identical)
    lua_map = parse_lua_mapping(PACKS[0])

    print(f"Loaded {len(ap_locs)} AP location names, {len(lua_map)} lua mappings")

    # Build target -> [prereq paths] map
    # Group by which file the target lives in
    file_rules = {
        r"\locations\Air Ride.json":   {},
        r"\locations\Top Ride.json":   {},
        r"\locations\City Trial.json": {},
        r"\locations\Stadium.json":    {},
    }

    def pick_file(ap_name):
        # Choose the JSON file based on the prefix in the AP location name
        if ap_name.startswith("Air Ride:"):   return r"\locations\Air Ride.json"
        if ap_name.startswith("Top Ride:"):   return r"\locations\Top Ride.json"
        if ap_name.startswith("Stadium:"):    return r"\locations\Stadium.json"
        return r"\locations\City Trial.json"

    skipped = []
    for target_name, prereq_names in LOGIC_RULES:
        target_code = ap_locs.get(target_name)
        if target_code is None:
            skipped.append(("missing target", target_name))
            continue
        # Look up section paths via lua mapping
        target_paths = lua_map.get(target_code, [])
        # Pick the SHALLOW path (parent section, not the child node path)
        # The lua entries have both deep and shallow forms after our restructure;
        # the shallow one (parent section) is the one with fewer slashes.
        target_paths_sorted = sorted(target_paths, key=lambda p: p.count("/"))
        if not target_paths_sorted:
            skipped.append(("no paths for target", target_name))
            continue
        target_path = target_paths_sorted[0]  # shallowest

        prereq_paths = []
        ok = True
        for prereq_name in prereq_names:
            pc = ap_locs.get(prereq_name)
            if pc is None:
                skipped.append(("missing prereq", prereq_name))
                ok = False
                break
            pp = lua_map.get(pc, [])
            pp_sorted = sorted(pp, key=lambda p: p.count("/"))
            if not pp_sorted:
                skipped.append(("no paths for prereq", prereq_name))
                ok = False
                break
            prereq_paths.append(pp_sorted[0])
        if not ok:
            continue

        f = pick_file(target_name)
        file_rules[f][target_path] = prereq_paths

    print(f"\nRules built per file:")
    for f, rules in file_rules.items():
        print(f"  {f}: {len(rules)} rules")

    if skipped:
        print(f"\nSkipped {len(skipped)} entries:")
        for reason, name in skipped[:10]:
            print(f"  {reason}: {name}")

    for root in PACKS:
        print(f"\n-- {root}")
        for fname, rules in file_rules.items():
            if not rules:
                continue
            n = apply_rules_to_file(root + fname, rules)
            print(f"  {fname}: applied to {n} nodes/sections")

    print("\nDone!")
