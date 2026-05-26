"""
Fix checklist grid positions for check nodes that have duplicate section names.

The original restructure built a (section_name -> offset) lookup, which
collapsed duplicate names (e.g. 'Race more than 100 laps!' x8 in Top Ride)
to one offset. This script uses the FULL PopTracker path to identify each check
uniquely and corrects the grid positions.

Full path format after restructure:
  @Air Ride/COURSE/Check Name/Check Name
  ^--- this is what location_mapping.lua now stores

We invert location_mapping.lua to get (full_path -> code),
then use KARLocations.py offsets to place each dot correctly.
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

COL_CENTERS = [168, 198, 228, 258, 288, 318, 348, 377, 407, 437, 467, 497]
ROW_CENTERS = [71, 101, 131, 161, 191, 221, 250, 280, 311, 341]


def parse_code_to_offset():
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


def parse_path_to_code():
    """Build full_section_path -> code from location_mapping.lua."""
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}')
    path_to_code = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        paths = re.findall(r'"([^"]+)"', m.group(2))
        for p in paths:
            path_to_code[p] = code
    return path_to_code


def fix_node(node, path_to_code, code_to_offset, node_path, fixed, not_found):
    """
    Traverse the tree. For every leaf check node (has sections + checklist map_loc),
    compute its full PopTracker section path and look up the correct grid offset.
    """
    node_name = node.get('name', '')
    current_path = node_path + '/' + node_name if node_path else node_name

    if node.get('sections'):
        # This is a leaf check node created during restructuring.
        # Its section name equals its node name.
        section_name = node['sections'][0]['name']
        # Full section path as stored in location_mapping.lua:
        #   @Air Ride/COURSE/Check Name/Check Name
        full_path = '@' + current_path + '/' + section_name

        if full_path in path_to_code:
            code = path_to_code[full_path]
            if code in code_to_offset:
                offset = code_to_offset[code]
                col = offset % 12
                row = offset // 12
                x = COL_CENTERS[col]
                y = ROW_CENTERS[row]
                # Update checklist map_location
                for ml in node.get('map_locations', []):
                    if 'Checklist' in ml.get('map', ''):
                        if ml['x'] != x or ml['y'] != y:
                            ml['x'] = x
                            ml['y'] = y
                            fixed.append(full_path)
        else:
            not_found.append(full_path)

    for child in node.get('children', []):
        fix_node(child, path_to_code, code_to_offset, current_path, fixed, not_found)


def process_file(json_path, path_to_code, code_to_offset):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    fixed = []
    not_found = []
    for node in data:
        fix_node(node, path_to_code, code_to_offset, '', fixed, not_found)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return fixed, not_found


if __name__ == '__main__':
    print("Building lookup tables...")
    code_to_offset = parse_code_to_offset()
    path_to_code = parse_path_to_code()
    print(f"  {len(path_to_code)} section paths in location_mapping.lua")
    print(f"  {len(code_to_offset)} Air/Top Ride offsets from KARLocations.py")

    for root in PACKS:
        print(f"\nProcessing {root}")

        ar_path = root + r"\locations\Air Ride.json"
        fixed, not_found = process_file(ar_path, path_to_code, code_to_offset)
        print(f"  Air Ride: {len(fixed)} positions corrected, {len(not_found)} paths not found")
        if not_found:
            print(f"    Not found: {not_found[:5]}")

        tr_path = root + r"\locations\Top Ride.json"
        fixed, not_found = process_file(tr_path, path_to_code, code_to_offset)
        print(f"  Top Ride: {len(fixed)} positions corrected, {len(not_found)} paths not found")
        if not_found:
            print(f"    Not found: {not_found[:5]}")

    print("\nDone!")
