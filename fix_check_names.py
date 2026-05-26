"""
Fix check display names in Air Ride.json, Top Ride.json, and location_mapping.lua:

1. Restore time format: "010700" -> "01:07:00"
2. Add "TA: " prefix for Time Attack checks
3. Add "FR: " prefix for Free Run checks

Uses KARLocations.py as the authoritative source to determine check type.
"""

import json
import re
import zipfile
import shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
SOURCE = PACKS[0]
APWORLD = r"A:\Archipelago\custom_worlds\kirby_air_ride.apworld"


def fix_time_format(name):
    """Convert 6-digit time strings like '010700' -> '01:07:00'."""
    return re.sub(r'(?<!\d)(\d{2})(\d{2})(\d{2})(?!\d)', r'\1:\2:\3', name)


def parse_code_to_fullname():
    """code -> full name string from KARLocations.py."""
    with zipfile.ZipFile(APWORLD) as z:
        content = z.read('kirby_air_ride/KARLocations.py').decode('utf-8')
    pattern = re.compile(r'"((?:Air Ride|Top Ride)[^"]+)":\s*KARLocationData\(\s*(\d+),')
    result = {}
    for m in pattern.finditer(content):
        result[int(m.group(2))] = m.group(1)
    return result


def parse_lua():
    """code -> list of section paths from location_mapping.lua."""
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


def get_check_type(full_name):
    """Return 'TA', 'FR', or '' based on the full KAR location name."""
    # Strip "Air Ride: " or "Top Ride: " prefix
    for prefix in ('Air Ride: ', 'Top Ride: '):
        if full_name.startswith(prefix):
            rest = full_name[len(prefix):]
            if rest.startswith('Time Attack:'):
                return 'TA'
            if rest.startswith('Free Run:'):
                return 'FR'
    return ''


def make_new_name(current_name, check_type):
    """
    Given the current (possibly broken) section name:
    1. Fix time format
    2. Add TA:/FR: prefix if missing
    """
    new_name = fix_time_format(current_name)

    if check_type == 'TA' and not new_name.startswith('TA:'):
        new_name = 'TA: ' + new_name
    elif check_type == 'FR' and not new_name.startswith('FR:'):
        new_name = 'FR: ' + new_name

    return new_name


def rename_in_node(node, old_to_new, path, renames_done):
    """Recursively rename nodes and sections matching old_to_new."""
    node_name = node.get('name', '')

    if node_name in old_to_new:
        new_name = old_to_new[node_name]
        node['name'] = new_name
        renames_done[node_name] = new_name

    # Also fix section names
    for sec in node.get('sections', []):
        sname = sec.get('name', '')
        if sname in old_to_new:
            new_sname = old_to_new[sname]
            sec['name'] = new_sname

    for child in node.get('children', []):
        rename_in_node(child, old_to_new, path + '/' + node_name, renames_done)


def update_lua(lua_path, old_to_new):
    """Update section paths in location_mapping.lua."""
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()

    for old, new in old_to_new.items():
        # The path ends with /OldName/OldName — replace both occurrences
        old_escaped = re.escape(old)
        # Replace path component: /OldName/OldName -> /NewName/NewName
        content = re.sub(
            r'/' + old_escaped + r'/' + old_escaped,
            '/' + new + '/' + new,
            content
        )
        # Also replace single occurrence (e.g. /OldName at end of a path)
        content = re.sub(
            r'/' + old_escaped + r'(?=["/])',
            '/' + new,
            content
        )

    with open(lua_path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    print("Building rename map...")
    code_to_name = parse_code_to_fullname()
    lua_mapping = parse_lua()

    # Build: current_section_name -> new_display_name
    old_to_new = {}
    for code in range(121, 361):
        if code not in code_to_name or code not in lua_mapping:
            continue
        full_name = code_to_name[code]
        check_type = get_check_type(full_name)

        for path in lua_mapping[code]:
            current_name = path.rsplit('/', 1)[-1]
            new_name = make_new_name(current_name, check_type)
            if new_name != current_name:
                old_to_new[current_name] = new_name

    print(f"  {len(old_to_new)} names to update")
    # Show a sample
    for old, new in list(old_to_new.items())[:8]:
        print(f"  '{old}' -> '{new}'")
    print("  ...")

    for root in PACKS:
        print(f"\nProcessing {root}")

        for mode_file in [r'\locations\Air Ride.json', r'\locations\Top Ride.json']:
            fpath = root + mode_file
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)

            renames_done = {}
            for node in data:
                rename_in_node(node, old_to_new, '', renames_done)

            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"  {mode_file}: {len(renames_done)} nodes renamed")

    # Update location_mapping.lua (once in source, then copy)
    print("\nUpdating location_mapping.lua...")
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    update_lua(lua_path, old_to_new)
    dest_lua = PACKS[1] + r"\scripts\autotracking\location_mapping.lua"
    shutil.copy2(lua_path, dest_lua)
    print("  Copied to packs folder")

    # Verify a few entries
    with open(lua_path, encoding='utf-8') as f:
        lua_content = f.read()
    for code in [134, 136, 139, 264]:
        m = re.search(rf'\[{code}\] = \{{([^}}]+)\}}', lua_content)
        if m:
            print(f"  [{code}]: {m.group(0)}")

    print("\nDone!")
