import json

PACKS = [
    r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride",
    r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride"
]

# ── Per-mode settings ──────────────────────────────────────────────────────────
MODE_SETTINGS = {
    "air_ride_settings": [
        ("air_ride_progression_time_attack",  "Time Attack checks are progression"),
        ("air_ride_progression_free_run",     "Free Run checks are progression"),
        ("air_ride_progression_high_effort",  "High Effort checks are progression"),
    ],
    "city_trial_settings": [
        ("city_trial_progression_free_run",      "Free Run checks are progression"),
        ("city_trial_progression_multiplayer",   "Multiplayer checks are progression"),
        ("city_trial_progression_rng",           "RNG checks are progression"),
        ("city_trial_progression_bust_vehicles", "Bust Vehicle checks are progression"),
        ("city_trial_progression_high_effort",   "High Effort checks are progression"),
    ],
    "top_ride_settings": [
        ("top_ride_progression_time_attack",  "Time Attack checks are progression"),
        ("top_ride_progression_free_run",     "Free Run checks are progression"),
        ("top_ride_progression_high_effort",  "High Effort checks are progression"),
        ("top_ride_progression_multiplayer",  "Multiplayer checks are progression"),
    ],
}

def make_settings_grid(settings_list):
    rows = []
    for code, label in settings_list:
        rows.append({
            "type": "array",
            "orientation": "horizontal",
            "margin": "0, 3",
            "content": [
                {"type": "item",  "item": code, "width": 20, "height": 20},
                {"type": "label", "text": label, "margin": "4, 0"}
            ]
        })
    return {
        "type": "array",
        "orientation": "vertical",
        "margin": "4, 4",
        "content": rows
    }

for root in PACKS:
    # 1. Update layouts/items.json — add 3 mode-specific setting grids
    layout_path = root + r"\layouts\items.json"
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    # Remove old setting_grid if present
    layout.pop("setting_grid", None)

    # Add 3 mode grids
    for key, settings_list in MODE_SETTINGS.items():
        layout[key] = make_settings_grid(settings_list)

    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=4)
    print(f"Updated layouts/items.json in {root}")

    # 2. Update tracker.json — replace "Settings" group with 3 mode-specific groups
    tracker_path = root + r"\layouts\tracker.json"
    with open(tracker_path, encoding="utf-8") as f:
        tracker = json.load(f)

    mode_groups_vertical = [
        {
            "type": "group",
            "header": "Air Ride ⚙",
            "dock": "top",
            "content": {"type": "layout", "key": "air_ride_settings"}
        },
        {
            "type": "group",
            "header": "City Trial ⚙",
            "dock": "top",
            "content": {"type": "layout", "key": "city_trial_settings"}
        },
        {
            "type": "group",
            "header": "Top Ride ⚙",
            "dock": "top",
            "content": {"type": "layout", "key": "top_ride_settings"}
        }
    ]

    mode_groups_horizontal = [
        {
            "type": "group",
            "header": "Air Ride ⚙",
            "dock": "left",
            "margin": "0,0,3,0",
            "content": {"type": "layout", "key": "air_ride_settings"}
        },
        {
            "type": "group",
            "header": "City Trial ⚙",
            "dock": "left",
            "margin": "0,0,3,0",
            "content": {"type": "layout", "key": "city_trial_settings"}
        },
        {
            "type": "group",
            "header": "Top Ride ⚙",
            "dock": "left",
            "margin": "0,0,3,0",
            "content": {"type": "layout", "key": "top_ride_settings"}
        }
    ]

    for variant in tracker:
        dock = tracker[variant]["content"]["content"]
        for section in dock:
            content = section.get("content", [])
            if not isinstance(content, list):
                continue
            new_content = []
            for group in content:
                if group.get("header") == "Settings":
                    # Replace with 3 mode groups
                    if section.get("dock") == "bottom":
                        new_content.extend(mode_groups_horizontal)
                    else:
                        new_content.extend(mode_groups_vertical)
                else:
                    new_content.append(group)
            section["content"] = new_content

    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=4)
    print(f"Updated layouts/tracker.json in {root}")

print("\nDone!")
