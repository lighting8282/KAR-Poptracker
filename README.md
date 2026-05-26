# Kirby Air Ride – PopTracker Pack

A [PopTracker](https://github.com/black-sliver/PopTracker) pack for
**Kirby Air Ride (GameCube, NTSC)** with full [Archipelago](https://archipelago.gg) autotracking
support.

Tracks every check, every received item, and every progression setting from your AP YAML —
all three modes (Air Ride, Top Ride, City Trial) plus the Stadium checks.

## Features

- **All 360 checks tracked**: 120 Air Ride, 120 Top Ride, 120 City Trial (incl. Stadium checks)
- **Dual map views per mode** — clickable course/category map dots *and* the in-game 12×10 checklist grid
- **Autotracking** of received items: permanent stat patches, stadium unlocks, HP, etc.
- **Progression filters** auto-applied from your YAML's slot data — checks turn gray if you
  excluded their category (Time Attack, Free Run, High Effort, Multiplayer, RNG, etc.)
- **Stadium icons** showing the title-card art for each stadium unlock
- **In-game style item icons** with colored labels matching the original sprite art

## Installation

1. Download the latest release ZIP from the [Releases page](https://github.com/lighting8282/KAR-Poptracker/releases)
2. Extract it into your PopTracker `packs/` folder, e.g.
   `…/poptracker/packs/Pop-Tracker- Kirby Air Ride/`
3. Open PopTracker — the Kirby Air Ride pack should appear in the pack list

## Usage

### Standalone (manual tracking)
1. Load the pack in PopTracker
2. Click checks as you complete them in-game

### With Archipelago autotracking
1. Start your Archipelago server and game as normal
2. In PopTracker, click the **AP** button → connect with your host, slot, and password
3. Items and locations will populate automatically
4. Progression categories (TA/FR/etc.) auto-toggle based on your YAML options

## Requirements

- **PopTracker** 0.25+ (tested on 0.33.0)
- **Kirby Air Ride** GameCube ROM (NTSC version)
- The [Kirby Air Ride Archipelago world](https://github.com/Decompacted/kirby-air-ride-archipelago) installed in your AP setup
- Dolphin emulator + the AP Dolphin client (for autotracking)

## Layout

The tracker is divided into:

**Bottom bar**
- **Items** — permanent stat patches with active/inactive states
- **Stadiums** (×2) — stadium unlock icons grouped by category

**Map area** (three tabs)
- **Air Ride** — course select map + checklist grid layer
- **City Trial** — overworld map + checklist grid layer
- **Top Ride** — course select map + checklist grid layer

Each tab has two map layers: switch with the arrow controls or by clicking the layer icon.

## Notes

- The 12×10 checklist grid positions are derived from in-game memory offsets.
  In the original game these positions are randomized per save file, so the grid layout in
  the tracker won't necessarily match what you see in-game — but every check is uniquely
  represented and autotracking works correctly regardless.
- Four "key" City Trial checks are pinned to the grid corners for visibility:
  Dragoon completion, Hydra completion, Fill 100 boxes, and the VS King Dedede check.

## Credits

- **PopTracker** by [black-sliver](https://github.com/black-sliver/PopTracker)
- **Kirby Air Ride Archipelago** by the AP community
- Sprite art ripped from Kirby Air Ride (Nintendo / HAL Laboratory, 2003) — used for
  non-commercial fan tracking purposes

## License

Pack contents are released for community use alongside the Kirby Air Ride Archipelago world.
Game-original art and audio remain property of Nintendo / HAL Laboratory.
