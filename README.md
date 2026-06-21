# Kirby Air Ride – PopTracker Pack

**SIDENOTE#:** For any issues, suggestions,etc with the tracker please open up an issues request here on github or feel free to ping me in the KAR channel in the Archipelago Discord!

A [PopTracker](https://github.com/black-sliver/PopTracker) pack for
**Kirby Air Ride (GameCube, NTSC)** with full [Archipelago](https://archipelago.gg) autotracking
support.

Tracks every check, every received item, and every progression setting from your AP YAML —
all three modes (Air Ride, Top Ride, City Trial) plus the Stadium checks. (More to come in a near future update)

## Features

- **All 360 checks tracked**: 120 Air Ride, 120 Top Ride, 120 City Trial (incl. Stadium checks)
- **Dual map views per mode** — clickable course/category map dots *and* the in-game 12×10 checklist grid
- **Autotracking** of received items: permanent stat patches, stadium unlocks, HP, etc.
- **In-game style item icons** with colored labels matching the original sprite art

## Installation

1. Download the latest release ZIP from the [Releases page](https://github.com/lighting8282/KAR-Poptracker/releases)
2. Extract it into your PopTracker `packs/` folder, e.g.
   `…/poptracker/packs/Pop-Tracker- Kirby Air Ride/`
3. Open PopTracker — the Kirby Air Ride pack should appear in the pack list

## Usage

### With Archipelago autotracking
1. Start your Archipelago server and game as normal
2. In PopTracker, click the **AP** button → connect with your host, slot, and password
3. Items and locations will populate automatically
4. Certain options like Deathlink, Trap link, energy link, etc will automatically turn on based on YAML options.

## Requirements

- **PopTracker** 0.25+ (tested on 0.33.0)
- **Kirby Air Ride** GameCube ROM (NTSC version) (Legal ROM needed)
- The [Kirby Air Ride Archipelago world][https://github.com/DeDeDeK/KARchipelago/releases/tag/v0.6.0] installed in your AP setup
- Dolphin emulator + the AP Dolphin client (for autotracking)

## Layout

The tracker is divided into:

**Bottom bar**
- **Patches** - Permament patches that stick throughout all modes
- **Patches Unlock** - Unlocks the aiblity to start stacking permament patches
- **Stadiums** (×2) — stadium unlock icons grouped by category
- **Boxes** — stadium unlock icons grouped by category
- **Special Offense** - Unique and special offense items
- **Machines** - Generic machiens
- **CT Vehicles** - Vehciles only available in CT (City Trial)
- **Characater Unlock** - Unique characteres you can unlock
- **Kirby Colors** - Kirb colors you can unlock
- **Copy Abilities** - Copy abilities
- **City Trial Events** - Events that happen randomly in CT mode (City Trial)
- **Utility** - List settings such as deathlink, traplink, energylink and so on
- **Top Ride Items Only** - Items only found in top ride mode
- **Top Ride Maps** - Maps just in TR mode. (Top Ride)
- **Top Ride Machines** - Machines only in TR. (Top Ride)
- **Air Ride Maps** - Maps just in AR mode. (Air Ride
- **Seed Settings** - Based on gating options in user YAML
- **Legendary Parts** - Pieces of the legendary Dragoon and Hydra

**Map area** (three tabs)
- **Air Ride** — course select map + checklist grid layer
- **City Trial** — overworld map + checklist grid layer
- **Top Ride** — course select map + checklist grid layer

Each tab has two map layers: switch by clicking the layer icon.

**City Trial Screenshot:**
<img width="2563" height="866" alt="image" src="https://github.com/user-attachments/assets/15fc8794-b98d-44e9-a11a-01b4a204c271" />


**Air Ride Screenshot:**
<img width="2568" height="533" alt="image" src="https://github.com/user-attachments/assets/eac42703-2f07-449b-a8dc-cbc3be2a94a5" />



## Notes

- The 12×10 checklist grid positions are derived from in-game memory offsets.
  In the original game these positions are randomized per save file, so the grid layout in
  the tracker won't necessarily match what you see in-game — but every check is uniquely
  represented and autotracking works correctly regardless.
- Four "key" City Trial checks are pinned to the grid corners for visibility:
  Dragoon completion, Hydra completion, Fill 100 boxes, and the VS King Dedede check.

## Credits

- **PopTracker** by [black-sliver](https://github.com/black-sliver/PopTracker)
- **Kirby Air Ride Archipelago** by https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md#items-file and the AP community.
- Sprite art ripped from Kirby Air Ride (Nintendo / HAL Laboratory, 2003) — used for
  non-commercial fan tracking purposes

## License

Pack contents are released for community use alongside the Kirby Air Ride Archipelago world.
Game-original art and audio remain property of Nintendo / HAL Laboratory.
