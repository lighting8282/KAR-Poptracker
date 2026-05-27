"""
Add stadium-unlock access_rules to every Stadium check.

When city_trial_progressive_stadiums is enabled, each stadium-specific check
should require the corresponding stadium unlock item.

For specific stadiums (e.g. "DRAG RACE 1"), the check needs that stadium's item.
For "(All)" variant checks (e.g. "DESTRUCTION DERBY (All)"), the check needs
ANY of the variants of that stadium.
"""

import json, re

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# Map (parent_name, section_name) patterns to item codes
# Returns a list of item codes (multiple = OR'd in PopTracker)
def items_for_check(parent_name: str, name: str) -> list[str]:
    full = f"{parent_name}/{name}".upper()
    # Check parent name first for "(All)" variants
    if "(ALL)" in parent_name.upper() or "(ALL)" in name.upper():
        if "DESTRUCTION DERBY" in full:
            return [f"stadium_destruction_derby_{i}" for i in range(1, 6)]
        if "KIRBY MELEE" in full:
            return [f"stadium_kirby_melee_{i}" for i in range(1, 3)]

    # Specific stadium patterns
    # Order matters: check more specific patterns first
    patterns = [
        (r"DRAG RACE\s*4\b",            ["stadium_drag_race_4"]),
        (r"DRAG RACE\s*3\b",            ["stadium_drag_race_3"]),
        (r"DRAG RACE\s*2\b",            ["stadium_drag_race_2"]),
        (r"DRAG RACE\s*1\b",            ["stadium_drag_race_1"]),
        (r"DESTRUCTION DERBY\s*5\b",    ["stadium_destruction_derby_5"]),
        (r"DESTRUCTION DERBY\s*4\b",    ["stadium_destruction_derby_4"]),
        (r"DESTRUCTION DERBY\s*3\b",    ["stadium_destruction_derby_3"]),
        (r"DESTRUCTION DERBY\s*2\b",    ["stadium_destruction_derby_2"]),
        (r"DESTRUCTION DERBY\s*1\b",    ["stadium_destruction_derby_1"]),
        (r"KIRBY MELEE\s*2\b",          ["stadium_kirby_melee_2"]),
        (r"KIRBY MELEE\s*1\b",          ["stadium_kirby_melee_1"]),
        (r"\bHIGH JUMP\b",              ["stadium_high_jump"]),
        (r"\bTARGET FLIGHT\b",          ["stadium_target_flight"]),
        (r"\bAIR GLIDER\b",             ["stadium_air_glider"]),
        (r"VS\.\s*KING DEDEDE",         ["stadium_vs_king_dedede"]),
    ]
    for pat, items in patterns:
        if re.search(pat, full):
            return items
    return []  # not stadium-gated


def merge_access_rule(existing: list[str], new_items: list[str]) -> list[str]:
    """
    Combine existing access_rules with the new stadium item requirement.

    PopTracker access_rules semantics:
      - List entries are OR'd together (any one satisfies)
      - Comma-separated items within an entry are AND'd (all required)

    For (All) variants with multiple new_items, ANY one of them satisfies (OR).
    For specific stadiums with one new_item, that exact item is required.

    Result expresses: (existing) AND (any of new_items)
    Expanded to OR-of-AND form: for each old rule × each new item, "old,new".
    """
    if not new_items:
        return existing

    # Clean existing list
    if not existing or all(not e.strip() for e in existing):
        # No real existing rules — each new_item becomes its own OR alternative
        return list(new_items)

    # Has existing rules — combine each old rule with each new item via AND,
    # and emit all combinations as OR alternatives
    result = []
    for old in existing:
        old = old.strip()
        for new in new_items:
            if old:
                result.append(f"{old},{new}")
            else:
                result.append(new)
    return result


def walk_node(node, parent_name, count):
    name = node.get("name", "")
    items = items_for_check(parent_name, name)

    if items:
        # Add to this node's access_rules
        existing = node.get("access_rules", [])
        merged = merge_access_rule(existing, items)
        if merged != existing:
            node["access_rules"] = merged
            count[0] += 1
        # Also add to sections within this node
        for sec in node.get("sections", []):
            sec_items = items_for_check(parent_name, sec.get("name", name))
            if sec_items:
                ex = sec.get("access_rules", [])
                m = merge_access_rule(ex, sec_items)
                if m != ex:
                    sec["access_rules"] = m
                    count[0] += 1
    else:
        # Even without node-level match, check sections by name
        for sec in node.get("sections", []):
            sec_items = items_for_check(name, sec.get("name", ""))
            if sec_items:
                ex = sec.get("access_rules", [])
                m = merge_access_rule(ex, sec_items)
                if m != ex:
                    sec["access_rules"] = m
                    count[0] += 1

    # Recurse into children
    for child in node.get("children", []):
        walk_node(child, name, count)


def process_file(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    count = [0]
    for node in data:
        walk_node(node, "", count)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return count[0]


if __name__ == "__main__":
    for root in PACKS:
        print(f"\nProcessing {root}")
        for fname in [r"\locations\Stadium.json", r"\locations\City Trial.json"]:
            path = root + fname
            n = process_file(path)
            print(f"  {fname.split(chr(92))[-1]}: added stadium rule to {n} nodes/sections")
    print("\nDone!")
