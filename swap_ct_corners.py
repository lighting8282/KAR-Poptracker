"""
Pin four specific City Trial checks to the four corners of the checklist grid
by swapping positions with whatever currently occupies each corner.
"""

import json

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]
FILES = [r"\locations\City Trial.json", r"\locations\Stadium.json"]
MAP_NAME = "City Trial Checklist"

# (name_substring, target_corner_xy)
SWAPS = [
    ("Dragoon Parts A, B, and C",  (168,  35)),   # top-left
    ("Hydra Parts X, Y, and Z",    (498,  35)),   # top-right
    ("Fill in over 100 Checklist", (168, 358)),   # bottom-left
    ("KING DEDEDE KO King Dedede", (498, 358)),   # bottom-right
]


def find_ml(data, predicate):
    """Walk all checks; return first map_location dict matching predicate."""
    def walk(node):
        for ml in node.get("map_locations", []):
            if ml.get("map") == MAP_NAME and predicate(node, ml):
                return ml
        for c in node.get("children", []):
            r = walk(c)
            if r:
                return r
        return None
    for n in data:
        r = walk(n)
        if r:
            return r
    return None


def load_all():
    """Load both JSON files for each pack copy."""
    return [{"path": root + f, "data": json.load(open(root + f, encoding="utf-8"))}
            for root in PACKS for f in FILES]


def save_all(loaded):
    for item in loaded:
        with open(item["path"], "w", encoding="utf-8") as f:
            json.dump(item["data"], f, indent=4)


# Operate on a single pack copy at a time, then mirror to all
def apply_swaps(data_list):
    """data_list = list of root data arrays (one per file)."""
    for keyword, (cx, cy) in SWAPS:
        # Find the target check (by name keyword) across all files
        target_ml = None
        for data in data_list:
            target_ml = find_ml(data,
                lambda n, ml: keyword.lower() in n.get("name", "").lower())
            if target_ml:
                break
        if not target_ml:
            print(f"  ! could not find target check matching '{keyword}'")
            continue

        # Find whatever check currently occupies the corner
        corner_ml = None
        for data in data_list:
            corner_ml = find_ml(data,
                lambda n, ml: ml["x"] == cx and ml["y"] == cy)
            if corner_ml:
                break

        old_target = (target_ml["x"], target_ml["y"])
        if corner_ml is None:
            # Corner is empty; just move target there
            target_ml["x"], target_ml["y"] = cx, cy
            print(f"  '{keyword}' moved {old_target} -> ({cx},{cy}) (corner was empty)")
        else:
            # Swap
            ox, oy = corner_ml["x"], corner_ml["y"]
            corner_ml["x"], corner_ml["y"] = old_target
            target_ml["x"], target_ml["y"] = cx, cy
            print(f"  '{keyword}' {old_target} <-> corner ({ox},{oy})")


# ─── apply same edits to BOTH pack copies (they should be identical) ─────────
for root in PACKS:
    print(f"\nProcessing {root}")
    data_list = []
    paths = []
    for f in FILES:
        p = root + f
        with open(p, encoding="utf-8") as fp:
            data_list.append(json.load(fp))
        paths.append(p)
    apply_swaps(data_list)
    for p, d in zip(paths, data_list):
        with open(p, "w", encoding="utf-8") as fp:
            json.dump(d, fp, indent=4)

print("\nDone!")
