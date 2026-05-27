"""
Merge the split 'TARGET FLIGHT perfect score' check into one clean name:
   'TARGET FLIGHT Get a perfect score (200 points)!'

Renames the parent node, child node, and both sections to the new name,
then updates location_mapping.lua so autotracking still works.
"""

import json, re, shutil

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

OLD_PARENT_NAME = "TARGET FLIGHT In one game, get a perfect score"
OLD_SECTION_NAME = "200 points!"
NEW_NAME = "TARGET FLIGHT Get a perfect score (200 points)!"


def rename_in_node(node):
    """Recursively rename matching node names and section names."""
    if node.get("name") == OLD_PARENT_NAME:
        node["name"] = NEW_NAME
        # Rename children with old section name
        for c in node.get("children", []):
            if c.get("name") == OLD_SECTION_NAME:
                c["name"] = NEW_NAME
                for sec in c.get("sections", []):
                    if sec.get("name") == OLD_SECTION_NAME:
                        sec["name"] = NEW_NAME
        # Rename own sections
        for sec in node.get("sections", []):
            if sec.get("name") == OLD_SECTION_NAME:
                sec["name"] = NEW_NAME
    for c in node.get("children", []):
        rename_in_node(c)


for root in PACKS:
    path = root + r"\locations\Stadium.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for n in data:
        rename_in_node(n)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"  Renamed in {path}")

# Now update location_mapping.lua paths
SOURCE = PACKS[0]
lua_path = SOURCE + r"\scripts\autotracking\location_mapping.lua"
with open(lua_path, encoding="utf-8") as f:
    content = f.read()

old_shallow = f"@Stadium/{OLD_PARENT_NAME}/{OLD_SECTION_NAME}"
old_deep    = f"@Stadium/{OLD_PARENT_NAME}/{OLD_SECTION_NAME}/{OLD_SECTION_NAME}"
new_shallow = f"@Stadium/{NEW_NAME}/{NEW_NAME}"
new_deep    = f"@Stadium/{NEW_NAME}/{NEW_NAME}/{NEW_NAME}"

# Replace longest first to avoid partial matches
content = content.replace(old_deep, new_deep)
content = content.replace(old_shallow, new_shallow)

with open(lua_path, "w", encoding="utf-8") as f:
    f.write(content)

shutil.copy2(lua_path, PACKS[1] + r"\scripts\autotracking\location_mapping.lua")
print("  Updated location_mapping.lua paths")

# Verify
with open(lua_path) as f:
    c = f.read()
m = re.search(r"\[97\]\s*=\s*\{[^}]*\}", c)
if m:
    print(f"\n[97] = {m.group(0)}")

print("Done!")
