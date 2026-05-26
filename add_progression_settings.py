"""
Implements YAML-based progression visibility in PopTracker.
- Adds setting toggle items to items.json
- Adds a setting_grid layout to layouts/items.json
- Adds access_rules to location JSON files
- Updates autotracking lua for slot data
Syncs both source and packs folders.
"""
import json, os, shutil

ROOTS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# ── Setting definitions ────────────────────────────────────────────────────────
SETTINGS = [
    # code                                    label                               default
    ("air_ride_progression_time_attack",      "Air Ride: Time Attack checks",     False),
    ("air_ride_progression_free_run",         "Air Ride: Free Run checks",        False),
    ("air_ride_progression_high_effort",      "Air Ride: High Effort checks",     False),
    ("city_trial_progression_free_run",       "City Trial: Free Run checks",      False),
    ("city_trial_progression_multiplayer",    "City Trial: Multiplayer checks",   False),
    ("city_trial_progression_rng",            "City Trial: RNG checks",           False),
    ("city_trial_progression_bust_vehicles",  "City Trial: Bust Vehicle checks",  False),
    ("city_trial_progression_high_effort",    "City Trial: High Effort checks",   False),
    ("top_ride_progression_time_attack",      "Top Ride: Time Attack checks",     False),
    ("top_ride_progression_free_run",         "Top Ride: Free Run checks",        False),
    ("top_ride_progression_high_effort",      "Top Ride: High Effort checks",     False),
    ("top_ride_progression_multiplayer",      "Top Ride: Multiplayer checks",     False),
]

# ── Section-level access rules (section name → setting code) ──────────────────
# These are sections NOT covered by a named child-node rule.
# Section name = AP location name minus the mode prefix ("Air Ride: ", etc.)

AIR_RIDE_HIGH_EFFORT_SECTIONS = {
    "Defeat 100 or more enemies with exhaled stars!",
    "Glide for more than 1 hour!",
    "Swallow 200 or more enemies!",
    "Glide for more than 30 minutes!",
    "Defeat over 1,000 of your enemies!",
    "Race over 300 laps!",
    "Fill in over 100 Checklist blocks!",
    "Defeat over 300 of your enemies!",
    "Race over 100 laps!",
}

CITY_TRIAL_MULTIPLAYER_SECTIONS = {
    "Let time run out while all players are on the rails!",
    "Have all players simultaneously get off of their machines!",
    "Let time run out while all players are off of their machines!",
}

CITY_TRIAL_RNG_SECTIONS = {
    "In one race, eat 3 or more plates of sushi!",
    "In one race, eat 3 or more Hot Dogs!",
    "In one game, eat 2 or more maxim tomatoes!",
    "In one game, drink 3 or more energy drinks!",
    "Get the Bomb ability from the Copy Chance Wheel!",
    "Get the Sleep ability from the Copy Chance Wheel!",
}

CITY_TRIAL_HIGH_EFFORT_SECTIONS = {
    "break more than 500 boxes!",
    "break more than 1000 boxes!",
    "pick up a total of over 1000 items!",
    "Pick up a total of over 3000 items!",
    "In one match, complete both Dragoon and Hydra!",
    "Fill in over 100 Checklist blocks!",
    "Get 10 items within the first 20 seconds of the match!",
    "In one game, get 50 or more items!",
    "Race over 200 miles!",
}

TOP_RIDE_HIGH_EFFORT_SECTIONS = {
    "Fill in over 100 Checklist blocks!",
    "Collect 500 items or more!",
    "SAND Drop into Ant Doom 50 times or more!",
    "LIGHT Ride the grind rail 50 times or more!",
    "Get over 18 different types of items!",
    "Race over 300 laps!",
    # "Race more than 100 laps!" appears per-course — handled via SAND/WATER etc. children
}

TOP_RIDE_MULTIPLAYER_SECTIONS = {
    "Compete in more than 50 multiplayer races!",
    "Compete in more than 10 multiplayer races!",
}

# child-node name → setting code (applied to all sections inside that child)
CHILD_NODE_RULES = {
    "Air Ride.json": {
        "Time Attack": "air_ride_progression_time_attack",
        "Free Run":    "air_ride_progression_free_run",
    },
    "City Trial.json": {
        "Free Run":         "city_trial_progression_free_run",
        "Machine Busting":  "city_trial_progression_bust_vehicles",
    },
    "Top Ride.json": {
        "Time Attack": "top_ride_progression_time_attack",
        "Free Run":    "top_ride_progression_free_run",
    },
}

# section name → setting code (for scattered sections not under a named child)
SECTION_RULES = {
    "Air Ride.json":    {s: "air_ride_progression_high_effort"     for s in AIR_RIDE_HIGH_EFFORT_SECTIONS},
    "City Trial.json":  {**{s: "city_trial_progression_multiplayer" for s in CITY_TRIAL_MULTIPLAYER_SECTIONS},
                         **{s: "city_trial_progression_rng"         for s in CITY_TRIAL_RNG_SECTIONS},
                         **{s: "city_trial_progression_high_effort" for s in CITY_TRIAL_HIGH_EFFORT_SECTIONS}},
    "Top Ride.json":    {**{s: "top_ride_progression_high_effort"   for s in TOP_RIDE_HIGH_EFFORT_SECTIONS},
                         **{s: "top_ride_progression_multiplayer"   for s in TOP_RIDE_MULTIPLAYER_SECTIONS}},
}


# ── Helpers ────────────────────────────────────────────────────────────────────
def add_access_rule(node: dict, rule: str):
    """Add an access rule to a node if not already present."""
    rules = node.setdefault("access_rules", [])
    if rule not in rules:
        rules.append(rule)

def apply_rules_to_tree(nodes: list, child_rules: dict, section_rules: dict):
    """Recursively apply access rules to location tree."""
    for node in nodes:
        name = node.get("name", "")

        # Child-node level rule
        if name in child_rules:
            add_access_rule(node, child_rules[name])

        # Section level rules
        for section in node.get("sections", []):
            sec_name = section.get("name", "")
            if sec_name in section_rules:
                add_access_rule(section, section_rules[sec_name])

        # Recurse into children
        if "children" in node:
            apply_rules_to_tree(node["children"], child_rules, section_rules)


# ── Apply to location JSONs ────────────────────────────────────────────────────
def process_location_json(path: str, filename: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    child_rules = CHILD_NODE_RULES.get(filename, {})
    sec_rules   = SECTION_RULES.get(filename, {})

    apply_rules_to_tree(data, child_rules, sec_rules)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"  Updated {filename}")


# ── Setting items ──────────────────────────────────────────────────────────────
def build_setting_items():
    items = []
    for code, label, default in SETTINGS:
        items.append({
            "name": code,
            "type": "toggle",
            "img": "images/items/checkbox_filler_city.png",  # reuse checkbox icon
            "initial_active_state": default,
            "overlay_align": "right",
            "codes": code
        })
    return items


# ── Settings grid layout ───────────────────────────────────────────────────────
def build_setting_grid():
    rows = []
    for code, label, _ in SETTINGS:
        rows.append({
            "type": "array",
            "orientation": "horizontal",
            "margin": "0, 2",
            "content": [
                {"type": "item",   "item": code, "width": 24, "height": 24},
                {"type": "label",  "text": label}
            ]
        })
    return {
        "setting_grid": {
            "type": "array",
            "orientation": "vertical",
            "margin": "4, 4",
            "content": rows
        }
    }


# ── Autotracking lua ───────────────────────────────────────────────────────────
SLOT_DATA_LUA = """
-- Progression settings from slot data
function applyProgressionSettings(slot_data)
    local settings = {
        "air_ride_progression_time_attack",
        "air_ride_progression_free_run",
        "air_ride_progression_high_effort",
        "city_trial_progression_free_run",
        "city_trial_progression_multiplayer",
        "city_trial_progression_rng",
        "city_trial_progression_bust_vehicles",
        "city_trial_progression_high_effort",
        "top_ride_progression_time_attack",
        "top_ride_progression_free_run",
        "top_ride_progression_high_effort",
        "top_ride_progression_multiplayer",
    }
    for _, code in ipairs(settings) do
        local item = Tracker:FindObjectForCode(code)
        if item then
            local val = slot_data[code]
            if val ~= nil then
                item.Active = (val == 1)
            end
        end
    end
end

-- Hook into slot data received
if SLOT_DATA ~= nil then
    applyProgressionSettings(SLOT_DATA)
end
"""

# ── Main ───────────────────────────────────────────────────────────────────────
src_root = ROOTS[0]
setting_items = build_setting_items()
setting_layout = build_setting_grid()

for root in ROOTS:
    print(f"\nProcessing: {root}")

    # 1. Location JSONs
    for fname in ["Air Ride.json", "City Trial.json", "Top Ride.json"]:
        fpath = os.path.join(root, "locations", fname)
        if os.path.exists(fpath):
            process_location_json(fpath, fname)

    # 2. Add setting items to items.json
    items_path = os.path.join(root, "items", "items.json")
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)
    # Remove old setting items if present
    existing_codes = {s[0] for s in SETTINGS}
    items = [i for i in items if i.get("codes") not in existing_codes]
    items.extend(setting_items)
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)
    print(f"  Updated items.json")

    # 3. Add setting_grid to layouts/items.json
    layout_path = os.path.join(root, "layouts", "items.json")
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)
    layout.update(setting_layout)
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"  Updated layouts/items.json")

    # 4. Append slot data handler to archipelago.lua
    lua_path = os.path.join(root, "scripts", "autotracking", "archipelago.lua")
    with open(lua_path, encoding="utf-8") as f:
        lua = f.read()
    if "applyProgressionSettings" not in lua:
        with open(lua_path, "a", encoding="utf-8") as f:
            f.write(SLOT_DATA_LUA)
        print(f"  Updated archipelago.lua")
    else:
        print(f"  archipelago.lua already updated")

print("\nDone!")
