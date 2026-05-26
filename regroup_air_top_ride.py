"""
Regroups Air Ride and Top Ride locations in location_mapping.lua:
- One marker per course, containing ALL tasks (races, Time Attack, Free Run)
- Non-course tasks grouped into categories
"""

PATH = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\scripts\autotracking\location_mapping.lua"

# ── Air Ride courses ───────────────────────────────────────────────────────────
AIR_RIDE_COURSES = [
    "MAGMA FLOWS",
    "FANTASY MEADOWS",
    "CHECKER KNIGHTS",
    "SKY SANDS",
    "FROZEN HILLSIDE",
    "MACHINE PASSAGE",
    "CELESTIAL VALLEY",
    "BEANSTALK PARK",
]

# Non-course Air Ride IDs → category
AIR_RIDE_OTHER = {
    # Swallow Challenges
    123: "@Air Ride/Swallow Challenges/Swallow Sword Knight 3 times and take 1st!",
    125: "@Air Ride/Swallow Challenges/Swallow 5 consecutive garbage enemies and take 1st!",
    153: "@Air Ride/Swallow Challenges/Swallow Wheelie 3 times and take 1st!",
    182: "@Air Ride/Swallow Challenges/Swallow Chilly 3 times and take 1st!",
    212: "@Air Ride/Swallow Challenges/Swallow Plasma Wisp 3 times and take 1st!",
    184: "@Air Ride/Swallow Challenges/Swallow 200 or more enemies!",

    # Ability Challenges
    128: "@Air Ride/Ability Challenges/Sword Challenge: swing sword 10 times and take 1st!",
    188: "@Air Ride/Ability Challenges/Tornado Challenge: defeat 15 enemies as Tornado Kirby!",
    144: "@Air Ride/Ability Challenges/Finish in 1st place with Wing ability!",
    173: "@Air Ride/Ability Challenges/Finish in 1st place with Sleep ability!",
    203: "@Air Ride/Ability Challenges/Finish in 1st place with Fire ability!",
    233: "@Air Ride/Ability Challenges/Finish in 1st place with Needle ability!",
    143: "@Air Ride/Ability Challenges/Finish in 1st place while flying through the air!",

    # High Effort
    121: "@Air Ride/High Effort/Race over 100 laps!",
    151: "@Air Ride/High Effort/Race over 300 laps!",
    122: "@Air Ride/High Effort/Defeat over 300 of your enemies!",
    152: "@Air Ride/High Effort/Defeat over 1,000 of your enemies!",
    214: "@Air Ride/High Effort/Defeat 100 or more enemies with exhaled stars!",
    181: "@Air Ride/High Effort/Glide for more than 30 minutes!",
    211: "@Air Ride/High Effort/Glide for more than 1 hour!",
    184: "@Air Ride/High Effort/Swallow 200 or more enemies!",
    127: "@Air Ride/High Effort/Fill in over 100 Checklist blocks!",

    # General
    129: "@Air Ride/General/Hit 20 or more rivals with your Quick Spin!",
    172: "@Air Ride/General/Start the final lap in 4th place and move to 1st to win!",
    142: "@Air Ride/General/Race all of the standard Air Ride courses!",
    183: "@Air Ride/General/In any mode other than Free Run, reach the goal 3 times!",
    202: "@Air Ride/General/Cross the finish line while spinning and take 1st place!",
    204: "@Air Ride/General/In one game, drop from the cliffs 3 times!",
    218: "@Air Ride/General/Defeat 10 or more enemies using the Quick Spin!",
    231: "@Air Ride/General/Make your lap times last two digits the same!",
    232: "@Air Ride/General/Finish in 1st place while taking damage!",
}

# ── Top Ride courses ───────────────────────────────────────────────────────────
TOP_RIDE_COURSES = ["GRASS", "SAND", "SKY", "FIRE", "WATER", "LIGHT", "METAL"]

# Non-course Top Ride IDs → category
TOP_RIDE_OTHER = {
    # General
    241: "@Top Ride/General/Cross the goal 20 or more times!",
    243: "@Top Ride/General/Do 20 or more Quick Spins in one lap and finish 1st!",
    244: "@Top Ride/General/Finish all courses without using Boost!",
    245: "@Top Ride/General/Take 1st place while holding the Hammer!",
    246: "@Top Ride/General/Get more than 20 Invincible Candy items!",
    247: "@Top Ride/General/In one game, hit enemies 3 times or more with Bomb items!",
    273: "@Top Ride/General/(No Zero Items rule) Complete all courses without using items!",
    274: "@Top Ride/General/Finish 1st on all courses without Boost!",
    275: "@Top Ride/General/Finish 1st with 1 lap between you and #2!",
    276: "@Top Ride/General/Get more than 20 Walky items!",
    277: "@Top Ride/General/Get over 18 different types of items!",
    301: "@Top Ride/General/Compete in more than 10 multiplayer races!",
    302: "@Top Ride/General/Take 1st place on all courses!",
    303: "@Top Ride/General/(No Zero Items rule) Finish 1st on all courses using no items!",
    304: "@Top Ride/General/Get the same item 3 times in one race!",
    305: "@Top Ride/General/Finish 1st with 2 laps between you and #2!",
    306: "@Top Ride/General/Torch 3 or more rivals using one Fire item!",
    334: "@Top Ride/General/Take 1st place while doing a Quick Spin!",
    335: "@Top Ride/General/Get more than 20 Spinner items!",
    336: "@Top Ride/General/Send 3 or more rivals sailing using one Buzz Saw item!",

    # High Effort
    271: "@Top Ride/High Effort/Race over 300 laps!",
    272: "@Top Ride/High Effort/Time Attack: Cross the goal 30 or more times!",
    333: "@Top Ride/High Effort/Collect 500 items or more!",
    360: "@Top Ride/High Effort/Fill in over 100 Checklist blocks!",

    # Multiplayer
    331: "@Top Ride/Multiplayer/Compete in more than 50 multiplayer races!",
    242: "@Top Ride/Free Run/Race more than 100 laps!",
}


def get_course_path(current_path: str, courses: list, mode: str) -> str | None:
    """
    If the path contains a course name, return the consolidated course path.
    Returns None if not a course-specific check.
    """
    path_upper = current_path.upper()
    for course in courses:
        if course in path_upper:
            # Extract the section name (last segment after the final /)
            parts = current_path.split("/")
            section = parts[-1]
            # Remove redundant course prefix from section name if present
            if section.upper().startswith(course):
                section = section[len(course):].lstrip(" :")
            if not section:
                section = parts[-1]
            return f"@{mode}/{course}/{section}"
    return None


with open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.strip()
    if not stripped.startswith("["):
        new_lines.append(line)
        continue

    # Parse: [ID] = {"@Mode/..."},
    try:
        bracket_end = stripped.index("]")
        loc_id = int(stripped[1:bracket_end])
        quote_start = stripped.index('"') + 1
        quote_end = stripped.rindex('"')
        current_path = stripped[quote_start:quote_end]
    except Exception:
        new_lines.append(line)
        continue

    new_path = None

    # Air Ride
    if current_path.startswith("@Air Ride"):
        if loc_id in AIR_RIDE_OTHER:
            new_path = AIR_RIDE_OTHER[loc_id]
        else:
            new_path = get_course_path(current_path, AIR_RIDE_COURSES, "Air Ride")

    # Top Ride
    elif current_path.startswith("@Top Ride"):
        if loc_id in TOP_RIDE_OTHER:
            new_path = TOP_RIDE_OTHER[loc_id]
        else:
            new_path = get_course_path(current_path, TOP_RIDE_COURSES, "Top Ride")

    if new_path:
        new_lines.append(f'\t[{loc_id}] = {{"{new_path}"}},\n')
    else:
        new_lines.append(line)

with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Done! Air Ride and Top Ride locations regrouped.")
