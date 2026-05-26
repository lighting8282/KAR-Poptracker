"""
Restructure Air Ride.json and Top Ride.json so each check is a child location
node (with map_locations on the checklist map) rather than a bare section.

PopTracker only respects map_locations on location nodes, not on sections.

Before:
  "MAGMA FLOWS" node  (map_locations: Air Ride course map)
    sections: [check_a, check_b, ...]

After:
  "MAGMA FLOWS" node  (map_locations: Air Ride course map)
    children:
      "check_a" node  (map_locations: Air Ride Checklist pos)
        sections: [check_a]
      "check_b" node  (map_locations: Air Ride Checklist pos)
        sections: [check_b]

Also updates location_mapping.lua paths from:
  @Air Ride/MAGMA FLOWS/check_a
to:
  @Air Ride/MAGMA FLOWS/check_a/check_a
"""

import json
import zipfile
import re

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
SOURCE = PACKS[0]
APWORLD = r"A:\Archipelago\custom_worlds\kirby_air_ride.apworld"

# Checklist grid cell centers  (12 cols x 10 rows)
COL_CENTERS = [168, 198, 228, 258, 288, 318, 348, 377, 407, 437, 467, 497]
ROW_CENTERS = [71, 101, 131, 161, 191, 221, 250, 280, 311, 341]


def parse_code_to_offset():
    """code -> relative memory offset for Air Ride (121-240) and Top Ride (241-360)."""
    with zipfile.ZipFile(APWORLD) as z:
        content = z.read('kirby_air_ride/KARLocations.py').decode('utf-8')
    pattern = re.compile(
        r'"(?:Air Ride|Top Ride)[^"]+\":\s*KARLocationData\(\s*(\d+),\s*'
        r'"[^"]*",\s*"[^"]*",\s*KARLocationType\.\w+,\s*'
        r'MemoryAddress\.\w+\.value\s*(?:\+\s*([\d\s\+]+))?\s*,',
        re.DOTALL
    )
    result = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        expr = m.group(2)
        offset = 0 if not expr else sum(int(x.strip()) for x in expr.split('+'))
        result[code] = offset
    return result


def parse_lua_mapping():
    """Parse location_mapping.lua: code -> section_path."""
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}')
    result = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        paths = re.findall(r'"([^"]+)"', m.group(2))
        result[code] = paths
    return result


def section_name_to_code(lua_mapping, mode_prefix, code_range):
    """Build section_name -> code for a mode using the lua mapping."""
    result = {}
    for code in code_range:
        if code not in lua_mapping:
            continue
        for path in lua_mapping[code]:
            # path like "@Air Ride/MAGMA FLOWS/Race over 4,800 feet in 2 minutes!"
            if path.startswith(mode_prefix):
                section_name = path.rsplit('/', 1)[-1]
                result[section_name] = code
    return result


def offset_for_section(section_name, name_to_code, code_to_offset):
    code = name_to_code.get(section_name)
    if code is None:
        return None
    return code_to_offset.get(code)


def make_child_node(section, checklist_map_name, x, y):
    """Convert a section dict into a child location node."""
    # Build the child node - replicate access/visibility from the section
    child = {
        "name": section["name"],
        "chest_unopened_img": "/images/items/close.png",
        "chest_opened_img": "/images/items/open.png",
        "overlay_background": "#000000",
        "access_rules": section.get("access_rules", []),
        "map_locations": [
            {"map": checklist_map_name, "x": x, "y": y}
        ],
        "sections": [
            {
                "name": section["name"],
                "access_rules": section.get("access_rules", []),
                "visibility_rules": section.get("visibility_rules", []),
                "item_count": section.get("item_count", 1)
            }
        ]
    }
    # Keep visibility_rules if present
    if section.get("visibility_rules"):
        child["visibility_rules"] = section["visibility_rules"]
    return child


def restructure_node(node, name_to_code, code_to_offset, checklist_map, added, skipped):
    """
    Recursively restructure: convert sections to children with checklist map_locations.
    Also removes any stale map_locations from sections (cleanup from failed first attempt).
    """
    # Recurse into EXISTING children FIRST (before we add new ones)
    existing_children = list(node.get('children', []))
    for child in existing_children:
        restructure_node(child, name_to_code, code_to_offset, checklist_map, added, skipped)

    if 'sections' in node and node['sections']:
        new_children = []
        remaining_sections = []
        for section in node['sections']:
            sname = section['name']
            # Remove map_locations from sections (cleanup from failed first attempt)
            section.pop('map_locations', None)
            offset = offset_for_section(sname, name_to_code, code_to_offset)
            if offset is not None:
                col = offset % 12
                row = offset // 12
                x = COL_CENTERS[col]
                y = ROW_CENTERS[row]
                new_children.append(make_child_node(section, checklist_map, x, y))
                added.append(sname)
            else:
                remaining_sections.append(section)
                skipped.append(sname)

        # Replace sections with new child nodes; keep any unmatched sections as-is
        if new_children:
            node['children'] = new_children + existing_children
            if remaining_sections:
                node['sections'] = remaining_sections
            else:
                node.pop('sections', None)


def restructure_file(json_path, name_to_code, code_to_offset, checklist_map):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    added = []
    skipped = []
    for node in data:
        restructure_node(node, name_to_code, code_to_offset, checklist_map, added, skipped)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return added, skipped


def update_lua_mapping(lua_path, code_range, lua_mapping, name_to_code):
    """Update location_mapping.lua: deepen Air Ride / Top Ride paths by one level."""
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()

    # Build reverse: section_name -> code for the relevant range
    code_set = set(code_range)

    def replace_entry(m):
        code = int(m.group(1))
        if code not in code_set:
            return m.group(0)  # leave non-Air/Top-Ride entries unchanged
        paths_str = m.group(2)
        old_paths = re.findall(r'"([^"]+)"', paths_str)
        new_paths = []
        for p in old_paths:
            # Only deepen paths that don't already have the deeper form
            # Path format: @Mode/Group/SectionName
            # Deeper:      @Mode/Group/SectionName/SectionName
            parts = p.split('/')
            # If the path already ends in /SectionName/SectionName, skip
            if len(parts) >= 2 and parts[-1] == parts[-2]:
                new_paths.append(p)
            else:
                # Deepen: append section_name again
                section_name = parts[-1]
                new_paths.append(p + '/' + section_name)
        paths_joined = ', '.join(f'"{p}"' for p in new_paths)
        return f'[{code}] = {{{paths_joined}}}'

    # Match lines like: [code] = {"path1", "path2"},
    updated = re.sub(
        r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}',
        replace_entry,
        content
    )

    with open(lua_path, 'w', encoding='utf-8') as f:
        f.write(updated)


if __name__ == '__main__':
    print("Parsing data sources...")
    code_to_offset = parse_code_to_offset()
    lua_mapping = parse_lua_mapping()

    # Build name->code for Air Ride and Top Ride
    air_name_to_code = section_name_to_code(lua_mapping, "@Air Ride/", range(121, 241))
    top_name_to_code = section_name_to_code(lua_mapping, "@Top Ride/", range(241, 361))
    print(f"  Air Ride name->code: {len(air_name_to_code)}")
    print(f"  Top Ride name->code: {len(top_name_to_code)}")

    for root in PACKS:
        print(f"\nProcessing {root}...")

        ar_path = root + r"\locations\Air Ride.json"
        added, skipped = restructure_file(
            ar_path, air_name_to_code, code_to_offset, "Air Ride Checklist")
        print(f"  Air Ride: {len(added)} nodes created, {len(skipped)} skipped")
        if skipped:
            print(f"    Skipped: {skipped[:3]}")

        tr_path = root + r"\locations\Top Ride.json"
        added, skipped = restructure_file(
            tr_path, top_name_to_code, code_to_offset, "Top Ride Checklist")
        print(f"  Top Ride: {len(added)} nodes created, {len(skipped)} skipped")
        if skipped:
            print(f"    Skipped: {skipped[:3]}")

    # Update location_mapping.lua (only once, in source)
    print("\nUpdating location_mapping.lua...")
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    update_lua_mapping(lua_path, range(121, 361), lua_mapping, None)

    # Copy lua to packs folder
    import shutil
    dest_lua = PACKS[1] + r"\scripts\autotracking\location_mapping.lua"
    shutil.copy2(lua_path, dest_lua)
    print("  Copied location_mapping.lua to packs folder")

    # Verify
    print("\nVerifying...")
    with open(lua_path, encoding='utf-8') as f:
        lua_content = f.read()
    sample = re.search(r'\[124\] = \{([^}]+)\}', lua_content)
    if sample:
        print(f"  Code 124 entry: {sample.group(0)}")

    print("\nDone!")
