"""
Restore sections on parent course nodes so their dots appear on the course map.

After restructuring, parent nodes (MAGMA FLOWS etc.) have only children and no
direct sections. PopTracker won't render a map dot for a node with no sections.

Fix:
  1. Copy each child's section back onto the parent node as a direct section.
  2. Update location_mapping.lua to track BOTH paths for each check:
       - Parent section:  @Air Ride/MAGMA FLOWS/CheckName
       - Child section:   @Air Ride/MAGMA FLOWS/CheckName/CheckName
     Both get marked when the AP item is received, keeping both views in sync.
"""

import json
import re
import shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
SOURCE = PACKS[0]

COURSE_MAPS = {"Air Ride", "Top Ride"}


def has_course_maploc(node):
    return any(ml.get("map") in COURSE_MAPS for ml in node.get("map_locations", []))


def has_checklist_maploc(node):
    return any("Checklist" in ml.get("map", "") for ml in node.get("map_locations", []))


def restore_sections(node, restored_count):
    """
    For any node that:
      - Has a course map_location (Air Ride or Top Ride)
      - Has children with checklist map_locations and sections
      - Has NO direct sections of its own
    -> Copy each child's section onto this node as a direct section.
    """
    if has_course_maploc(node) and not node.get("sections"):
        # Collect sections from direct children that are checklist check nodes
        new_sections = []
        for child in node.get("children", []):
            if has_checklist_maploc(child) and child.get("sections"):
                for sec in child["sections"]:
                    # Copy the section (same name, rules, count)
                    new_sections.append(dict(sec))

        if new_sections:
            node["sections"] = new_sections
            restored_count[0] += len(new_sections)

    # Recurse
    for child in node.get("children", []):
        restore_sections(child, restored_count)


def process_file(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    count = [0]
    for node in data:
        restore_sections(node, count)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return count[0]


def update_lua_dual_paths(lua_path, code_range_start, code_range_end):
    """
    For each Air Ride / Top Ride code, add the parent section path alongside
    the child section path so both get marked by the autotracker.

    Current:  [124] = {"@Air Ride/MAGMA FLOWS/CheckName/CheckName"}
    After:    [124] = {"@Air Ride/MAGMA FLOWS/CheckName/CheckName",
                       "@Air Ride/MAGMA FLOWS/CheckName"}
    """
    with open(lua_path, encoding="utf-8") as f:
        content = f.read()

    code_set = set(range(code_range_start, code_range_end + 1))

    def replace_entry(m):
        code = int(m.group(1))
        if code not in code_set:
            return m.group(0)

        paths = re.findall(r'"([^"]+)"', m.group(2))
        new_paths = list(paths)  # start with existing paths

        for p in paths:
            parts = p.split("/")
            # If this is already the deep path (last two parts are the same),
            # add the shallow parent path if not already present
            if len(parts) >= 2 and parts[-1] == parts[-2]:
                parent_path = "/".join(parts[:-1])
                if parent_path not in new_paths:
                    new_paths.append(parent_path)

        paths_joined = ", ".join(f'"{p}"' for p in new_paths)
        return f"[{code}] = {{{paths_joined}}}"

    updated = re.sub(
        r"\[(\d+)\]\s*=\s*\{(\"(?:[^\"]+)\"(?:,\s*\"(?:[^\"]+)\")*)\}",
        replace_entry,
        content,
    )

    with open(lua_path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    for root in PACKS:
        print(f"Processing {root}")

        n = process_file(root + r"\locations\Air Ride.json")
        print(f"  Air Ride.json: {n} sections restored to parent nodes")

        n = process_file(root + r"\locations\Top Ride.json")
        print(f"  Top Ride.json: {n} sections restored to parent nodes")

    print("\nUpdating location_mapping.lua with dual paths...")
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    update_lua_dual_paths(lua_path, 121, 360)
    shutil.copy2(lua_path, PACKS[1] + r"\scripts\autotracking\location_mapping.lua")

    # Verify
    with open(lua_path, encoding="utf-8") as f:
        lua_content = f.read()
    for code in [124, 136, 264]:
        m = re.search(rf"\[{code}\] = \{{([^}}]+)\}}", lua_content)
        if m:
            print(f"  [{code}]: {m.group(0)}")

    print("\nDone!")
