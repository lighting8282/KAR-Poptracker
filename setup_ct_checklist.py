"""
Full City Trial checklist pipeline:
1. Add City Trial Checklist map to maps.json
2. Add it as a second layer on the City Trial tab in tabs.json
3. Restructure City Trial.json + Stadium.json:
   - Add child nodes with checklist map_locations for every section
   - Restore parent sections so map dots stay visible
4. Fix position collisions (same name used in multiple nodes)
5. Update location_mapping.lua with dual paths (parent + child)
"""

import json, zipfile, re, shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
SOURCE = PACKS[0]
APWORLD = r"A:\Archipelago\custom_worlds\kirby_air_ride.apworld"

# Grid computed from original 1536x1024 image, scaled to 640x511
COL_CENTERS = [168, 198, 228, 258, 288, 318, 348, 378, 408, 438, 467, 498]
ROW_CENTERS = [35,  71, 107, 143, 179, 215, 251, 286, 322, 358]
CHECKLIST_MAP = "City Trial Checklist"

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_code_to_offset():
    with zipfile.ZipFile(APWORLD) as z:
        content = z.read('kirby_air_ride/KARLocations.py').decode('utf-8')
    pattern = re.compile(
        r'"(?:City Trial|Stadium)[^"]+\":\s*KARLocationData\(\s*(\d+),\s*'
        r'"[^"]*",\s*"[^"]*",\s*KARLocationType\.\w+,\s*'
        r'MemoryAddress\.\w+\.value\s*(?:\+\s*([\d\s\+]+))?\s*,', re.DOTALL)
    result = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        expr = m.group(2)
        offset = 0 if not expr else sum(int(x.strip()) for x in expr.split('+'))
        result[code] = offset
    return result

def parse_lua():
    with open(SOURCE + r"\scripts\autotracking\location_mapping.lua", encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}')
    result = {}
    for m in pattern.finditer(content):
        code = int(m.group(1))
        result[code] = re.findall(r'"([^"]+)"', m.group(2))
    return result

def build_path_to_code(lua_mapping, code_range):
    """full section path -> code"""
    result = {}
    for code in code_range:
        for p in lua_mapping.get(code, []):
            result[p] = code
    return result

# ── step 1: maps.json ────────────────────────────────────────────────────────

def update_maps_json(root):
    path = root + r"\maps\maps.json"
    with open(path, encoding='utf-8') as f:
        maps = json.load(f)
    if not any(m['name'] == CHECKLIST_MAP for m in maps):
        maps.append({
            "name": CHECKLIST_MAP,
            "location_size": 16,
            "location_border_thickness": 2,
            "img": "images/maps/City Trial Checklist.png"
        })
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(maps, f, indent=4)
        print(f"  maps.json updated")
    else:
        print(f"  maps.json already has City Trial Checklist")

# ── step 2: tabs.json ────────────────────────────────────────────────────────

def update_tabs_json(root):
    path = root + r"\layouts\tabs.json"
    with open(path, encoding='utf-8') as f:
        tabs = json.load(f)
    changed = False
    for key in tabs:
        for tab in tabs[key].get('tabs', []):
            if tab.get('title') == 'City Trial':
                maps_list = tab['content'].get('maps', [])
                if CHECKLIST_MAP not in maps_list:
                    maps_list.append(CHECKLIST_MAP)
                    tab['content']['maps'] = maps_list
                    changed = True
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(tabs, f, indent=4)
        print(f"  tabs.json updated")
    else:
        print(f"  tabs.json already updated")

# ── step 3: restructure location file ───────────────────────────────────────

def make_child_node(section, x, y):
    child = {
        "name": section["name"],
        "chest_unopened_img": "/images/items/close.png",
        "chest_opened_img": "/images/items/open.png",
        "overlay_background": "#000000",
        "access_rules": section.get("access_rules", []),
        "map_locations": [{"map": CHECKLIST_MAP, "x": x, "y": y}],
        "sections": [{
            "name": section["name"],
            "access_rules": section.get("access_rules", []),
            "visibility_rules": section.get("visibility_rules", []),
            "item_count": section.get("item_count", 1)
        }]
    }
    if section.get("visibility_rules"):
        child["visibility_rules"] = section["visibility_rules"]
    return child

def restructure_node(node, path_to_code, code_to_offset, added, skipped, node_path=''):
    cur_path = (node_path + '/' + node.get('name','')) if node_path else node.get('name','')
    existing_children = list(node.get('children', []))
    for child in existing_children:
        restructure_node(child, path_to_code, code_to_offset, added, skipped, cur_path)

    if node.get('sections'):
        new_children = []
        remaining = []
        for sec in node['sections']:
            sname = sec['name']
            sec.pop('map_locations', None)
            # Build the full section path as it appears in lua
            full_path = '@' + cur_path + '/' + sname
            code = path_to_code.get(full_path)
            if code is not None and code in code_to_offset:
                offset = code_to_offset[code]
                col = offset % 12
                row = offset // 12
                x, y = COL_CENTERS[col], ROW_CENTERS[row]
                new_children.append(make_child_node(sec, x, y))
                added.append(full_path)
            else:
                remaining.append(sec)
                skipped.append(full_path)

        if new_children:
            node['children'] = new_children + existing_children
            node['sections'] = remaining if remaining else node.get('sections', [])
            if not remaining:
                node.pop('sections', None)

def restructure_file(json_path, path_to_code, code_to_offset):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    added, skipped = [], []
    for node in data:
        restructure_node(node, path_to_code, code_to_offset, added, skipped)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return added, skipped

# ── step 4: fix duplicate-name position collisions ───────────────────────────

def fix_positions(json_path, path_to_code, code_to_offset, node_path=''):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    fixed = [0]
    def fix_node(node, cur_path):
        if node.get('sections'):
            sec_name = node['sections'][0]['name']
            full_path = '@' + cur_path + '/' + sec_name
            code = path_to_code.get(full_path)
            if code and code in code_to_offset:
                offset = code_to_offset[code]
                col, row = offset % 12, offset // 12
                x, y = COL_CENTERS[col], ROW_CENTERS[row]
                for ml in node.get('map_locations', []):
                    if CHECKLIST_MAP in ml.get('map',''):
                        if ml['x'] != x or ml['y'] != y:
                            ml['x'], ml['y'] = x, y
                            fixed[0] += 1
        np = cur_path + '/' + node.get('name','')
        for child in node.get('children', []):
            fix_node(child, np)

    for node in data:
        fix_node(node, node.get('name',''))

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return fixed[0]

# ── step 5: restore parent sections ─────────────────────────────────────────

def restore_parent_sections(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    count = [0]
    def restore(node):
        has_map = any(ml.get('map') not in (CHECKLIST_MAP, '') and 'Checklist' not in ml.get('map','')
                      for ml in node.get('map_locations', []))
        if has_map and not node.get('sections'):
            new_secs = []
            for child in node.get('children', []):
                if any(CHECKLIST_MAP in ml.get('map','') for ml in child.get('map_locations',[])):
                    for sec in child.get('sections', []):
                        new_secs.append(dict(sec))
            if new_secs:
                node['sections'] = new_secs
                count[0] += len(new_secs)
        for child in node.get('children', []):
            restore(child)
    for node in data:
        restore(node)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return count[0]

# ── step 6: dual paths in lua ────────────────────────────────────────────────

def update_lua_dual(lua_path, code_range):
    with open(lua_path, encoding='utf-8') as f:
        content = f.read()
    code_set = set(code_range)
    def replace(m):
        code = int(m.group(1))
        if code not in code_set:
            return m.group(0)
        paths = re.findall(r'"([^"]+)"', m.group(2))
        new_paths = list(paths)
        for p in paths:
            parts = p.split('/')
            if len(parts) >= 2 and parts[-1] == parts[-2]:
                parent = '/'.join(parts[:-1])
                if parent not in new_paths:
                    new_paths.append(parent)
        return f"[{code}] = {{" + ", ".join(f'"{p}"' for p in new_paths) + "}"
    updated = re.sub(r'\[(\d+)\]\s*=\s*\{("(?:[^"]+)"(?:,\s*"(?:[^"]+)")*)\}', replace, content)
    with open(lua_path, 'w', encoding='utf-8') as f:
        f.write(updated)

# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Building lookup tables...")
    code_to_offset = parse_code_to_offset()
    lua_mapping = parse_lua()
    path_to_code = build_path_to_code(lua_mapping, range(1, 121))
    print(f"  City Trial offsets: {len(code_to_offset)}, lua paths: {len(path_to_code)}")

    for root in PACKS:
        print(f"\n-- {root}")
        update_maps_json(root)
        update_tabs_json(root)

        for fname, label in [(r"\locations\City Trial.json", "City Trial"),
                              (r"\locations\Stadium.json",    "Stadium")]:
            fpath = root + fname
            added, skipped = restructure_file(fpath, path_to_code, code_to_offset)
            print(f"  {label}: {len(added)} nodes created, {len(skipped)} skipped")
            if skipped: print(f"    skipped: {skipped[:3]}")

            fixed = fix_positions(fpath, path_to_code, code_to_offset)
            if fixed: print(f"  {label}: {fixed} positions corrected")

            n = restore_parent_sections(fpath)
            print(f"  {label}: {n} parent sections restored")

    print("\nUpdating location_mapping.lua...")
    lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
    update_lua_dual(lua_path, range(1, 121))
    shutil.copy2(lua_path, PACKS[1] + r"\scripts\autotracking\location_mapping.lua")

    # Verify a couple entries
    with open(lua_path, encoding='utf-8') as f:
        lua = f.read()
    for code in [1, 5, 41]:
        m = re.search(rf'\[{code}\] = \{{([^}}]+)\}}', lua)
        if m: print(f"  [{code}]: {m.group(0)}")

    print("\nDone!")
