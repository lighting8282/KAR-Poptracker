import json
import zipfile
import re

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

APWORLD = r"A:\Archipelago\custom_worlds\kirby_air_ride.apworld"
SOURCE = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride"

# Grid layout: 12 columns x 10 rows = 120 cells
# Both Air Ride and Top Ride checklists use the same pixel layout
COL_CENTERS = [168, 198, 228, 258, 288, 318, 348, 377, 407, 437, 467, 497]
ROW_CENTERS = [71, 101, 131, 161, 191, 221, 250, 280, 311, 341]

# Visual position formula (memory offset -> visual cell):
#   visual_col = offset % 12
#   visual_row = offset // 12


def parse_code_to_offset():
    """Extract code -> relative_offset from KARLocations.py for Air Ride and Top Ride."""
    with zipfile.ZipFile(APWORLD) as z:
        content = z.read('kirby_air_ride/KARLocations.py').decode('utf-8')

    pattern = re.compile(
        r'"(?:Air Ride|Top Ride)[^"]+\":\s*KARLocationData\(\s*'
        r'(\d+),\s*'           # code
        r'"[^"]*",\s*'         # region
        r'"[^"]*",\s*'         # reward
        r'KARLocationType\.\w+,\s*'  # type
        r'MemoryAddress\.\w+\.value\s*(?:\+\s*([\d\s\+]+))?\s*,',
        re.DOTALL
    )

    code_to_offset = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        offset_expr = m.group(2)
        if offset_expr is None:
            offset = 0
        else:
            offset = sum(int(x.strip()) for x in offset_expr.split('+'))
        code_to_offset[code] = offset

    return code_to_offset


def parse_location_mapping_lua():
    """Parse location_mapping.lua: code -> section_name (last path component)."""
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()

    # Match: [code] = {"@Mode/.../SectionName"},
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{"([^"]+)"\}')
    code_to_section = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        path = m.group(2)
        # Section name is the last component of the path
        section_name = path.rsplit('/', 1)[-1]
        code_to_section[code] = section_name

    return code_to_section


def build_name_to_offset(mode_prefix, code_range_start, code_range_end,
                          code_to_offset, code_to_section):
    """Build section_name -> visual_offset for a given mode."""
    name_to_offset = {}
    for code in range(code_range_start, code_range_end + 1):
        if code not in code_to_offset:
            continue
        if code not in code_to_section:
            continue
        section_name = code_to_section[code]
        name_to_offset[section_name] = code_to_offset[code]
    return name_to_offset


def add_map_location(section, map_name, x, y):
    """Add a map_location entry to a section node (skip if already present)."""
    if 'map_locations' not in section:
        section['map_locations'] = []
    for ml in section['map_locations']:
        if ml.get('map') == map_name:
            return False
    section['map_locations'].append({"map": map_name, "x": x, "y": y})
    return True


def process_nodes(nodes, name_to_offset, map_name, added, missing):
    """Recursively walk location nodes and add map_locations to sections."""
    for node in nodes:
        for section in node.get('sections', []):
            sname = section['name']
            if sname in name_to_offset:
                offset = name_to_offset[sname]
                visual_col = offset % 12
                visual_row = offset // 12
                x = COL_CENTERS[visual_col]
                y = ROW_CENTERS[visual_row]
                if add_map_location(section, map_name, x, y):
                    added.append(sname)
            else:
                missing.append(sname)

        if 'children' in node:
            process_nodes(node['children'], name_to_offset, map_name, added, missing)


def process_file(json_path, name_to_offset, map_name):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    added = []
    missing = []
    process_nodes(data, name_to_offset, map_name, added, missing)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return added, missing


if __name__ == '__main__':
    print("Building location mappings...")
    code_to_offset = parse_code_to_offset()
    code_to_section = parse_location_mapping_lua()

    print(f"  Codes with offsets: {len(code_to_offset)}")
    print(f"  Codes with section names: {len(code_to_section)}")

    # Air Ride: codes 121-240
    air_name_to_offset = build_name_to_offset(
        "Air Ride", 121, 240, code_to_offset, code_to_section)
    # Top Ride: codes 241-360
    top_name_to_offset = build_name_to_offset(
        "Top Ride", 241, 360, code_to_offset, code_to_section)

    print(f"  Air Ride name->offset entries: {len(air_name_to_offset)}")
    print(f"  Top Ride name->offset entries: {len(top_name_to_offset)}")

    for root in PACKS:
        print(f"\nProcessing {root}")

        ar_path = root + r"\locations\Air Ride.json"
        added, missing = process_file(ar_path, air_name_to_offset, "Air Ride Checklist")
        print(f"  Air Ride: added {len(added)} markers, {len(missing)} unmatched")
        if missing:
            print(f"    UNMATCHED: {missing[:5]}")

        tr_path = root + r"\locations\Top Ride.json"
        added, missing = process_file(tr_path, top_name_to_offset, "Top Ride Checklist")
        print(f"  Top Ride: added {len(added)} markers, {len(missing)} unmatched")
        if missing:
            print(f"    UNMATCHED: {missing[:5]}")

    print("\nDone!")
