# Regroups City Trial locations in location_mapping.lua into logical map sections

PATH = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\scripts\autotracking\location_mapping.lua"

# Map: location ID -> new path
REMAP = {
    # Milestones
    1:  "@City Trial/Milestones/race over 60 miles!",
    2:  "@City Trial/Milestones/pick up a total of over 1000 items!",
    3:  "@City Trial/Milestones/break more than 1000 boxes!",
    19: "@City Trial/Milestones/Get 10 items within the first 20 seconds of the match!",
    31: "@City Trial/Milestones/Race over 200 miles!",
    32: "@City Trial/Milestones/Pick up a total of over 3000 items!",
    49: "@City Trial/Milestones/Do damage to a rival within the first 10 seconds of a match!",
    61: "@City Trial/Milestones/Pick up a total of over 100 items!",
    79: "@City Trial/Milestones/Have all players simultaneously get off of their machines!",
    80: "@City Trial/Milestones/Enter a race with 3 CPU Players and do damage to all of them in the city!",
    91: "@City Trial/Milestones/pick up a total of over 500 items!",
    92: "@City Trial/Milestones/break more than 500 boxes!",
    104:"@City Trial/Milestones/Fill in over 100 Checklist blocks!",
    109:"@City Trial/Milestones/Let time run out while all players are off of their machines!",
    110:"@City Trial/Milestones/In one game, get 50 or more items!",

    # Volcano
    16: "@City Trial/Volcano/Open up all the holes around the base of the volcano!",
    17: "@City Trial/Volcano/During one game, go into the hole in the high plains 3 times or more!",
    47: "@City Trial/Volcano/During one game, break all of the volcano rocks and high plains rocks!",
    77: "@City Trial/Volcano/Use the grind rail to break into the crater!",

    # Forest
    48: "@City Trial/Forest/Knock down all of the trees in the forest!",
    106:"@City Trial/Forest/Open up the pitfall in the forest!",

    # Castle
    15: "@City Trial/Castle/Go into the castle chamber when it opens!",
    76: "@City Trial/Castle/Make your way to the garden in the sky!",

    # Events
    13: "@City Trial/Events/Do some damage to Dyna Blade!",
    43: "@City Trial/Events/Get trampled by Dyna Blade!",
    44: "@City Trial/Events/The meteor attacks the city 3 or more times!",
    14: "@City Trial/Events/Steal over 8 items from Tac by yourself!",
    25: "@City Trial/Events/Use Fireworks to KO rivals 10 times or more!",
    73: "@City Trial/Events/Break 5 or more of the huge pillars that appear!",
    103:"@City Trial/Events/Break a huge pillar within 40 seconds of the time it appears!",
    78: "@City Trial/Events/Get the Bomb ability from the Copy Chance Wheel!",
    108:"@City Trial/Events/Get the Sleep ability from the Copy Chance Wheel!",

    # City
    18: "@City Trial/City/Destroy all of the dilapidated houses!",
    20: "@City Trial/City/Let time run out while all players are on the rails!",
    45: "@City Trial/City/During one game, fly through the rings in the sky 5 times or more!",
    46: "@City Trial/City/Let the waterwheel carry you 10 times or more!",
    74: "@City Trial/City/Use up one of the restoration areas!",
    75: "@City Trial/City/Bust the star pole!",
    105:"@City Trial/City/Bust the star pole 10 times or more!",
    107:"@City Trial/City/Jump on top of the building 10 times or more using the super jump ramp!",
    28: "@City Trial/City/In one race, eat 3 or more Hot Dogs!",
    55: "@City Trial/City/In one game, eat 2 or more maxim tomatoes!",
    85: "@City Trial/City/In one game, drink 3 or more energy drinks!",
    117:"@City Trial/City/In one race, eat 3 or more plates of sushi!",

    # Machine Busting
    29: "@City Trial/Machine Busting/In the city, bust Wheelie Bike while riding on Warpstar!",
    30: "@City Trial/Machine Busting/In the city, bust Slick Star while riding on Formula Star!",
    59: "@City Trial/Machine Busting/In the city, bust Swerve Star while riding on Wheelie Bike!",
    60: "@City Trial/Machine Busting/In the city, bust Rocket Star while riding on Slick Star!",
    89: "@City Trial/Machine Busting/In the city, bust Warpstar while riding on Swerve Star!",
    90: "@City Trial/Machine Busting/In the city, bust Turbo Star while riding on Rocket Star!",
    118:"@City Trial/Machine Busting/In the city, bust Wheelie Scooter while riding Compact Star!",
    119:"@City Trial/Machine Busting/In the city, bust Formula Star while riding on Turbo Star!",
    50: "@City Trial/Machine Busting/Break a CPUs machine 5 times or more in the city!",
    84: "@City Trial/Machine Busting/Use Sensor Bombs to KO rivals 3 times or more!",
    114:"@City Trial/Machine Busting/Use Gold Spikes to KO rivals 3 times or more!",

    # Patches
    21: "@City Trial/Patches/In one game, get over 10 Boost Patches!",
    22: "@City Trial/Patches/In one game, get 10 or more Turn Patches!",
    23: "@City Trial/Patches/In one game, get 10 or more Weight Patches!",
    24: "@City Trial/Patches/In one game, get 10 or more Glide Patches!",
    54: "@City Trial/Patches/Get 30 or more Glide Patches!",
    81: "@City Trial/Patches/In one game, get 10 or more Top Speed Patches!",
    82: "@City Trial/Patches/In one game, get 10 or more Charge Patches!",
    83: "@City Trial/Patches/In one game, get 10 or more Defense Patches!",

    # Dragoon & Hydra
    58: "@City Trial/Dragoon and Hydra/Unlock Dragoon Parts A, B, and C on the Checklist!",
    88: "@City Trial/Dragoon and Hydra/Unlock Hydra Parts X, Y, and Z on the Checklist!",
    120:"@City Trial/Dragoon and Hydra/In one match, complete both Dragoon and Hydra!",

    # Free Run (unchanged)
    33: "@City Trial/Free Run/Drive for a total of 10 minutes or more!",
    62: "@City Trial/Free Run/Change Air Ride Machines 10 times or more!",
    63: "@City Trial/Free Run/Drive for a total of 30 minutes or more!",
    93: "@City Trial/Free Run/Drive for a total of 2 hours or more!",
}

with open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    replaced = False
    for loc_id, new_path in REMAP.items():
        prefix = f"\t[{loc_id}] = "
        if line.strip().startswith(f"[{loc_id}] = "):
            new_lines.append(f'\t[{loc_id}] = {{"{new_path}"}},\n')
            replaced = True
            break
    if not replaced:
        new_lines.append(line)

with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Done! City Trial locations regrouped.")
