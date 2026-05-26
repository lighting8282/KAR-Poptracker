"""
Clean up City Trial checklist screenshot:
1. Detect the grid area
2. Replace all colored cells (green / red / orange / purple) with base grey
3. Fill the description text bar at the bottom
4. Crop to just the frame (matching Air Ride / Top Ride checklist style)
5. Resize to 640x511 and save as City Trial Checklist.png
"""

from PIL import Image
import numpy as np

SOURCE = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\city trial checklist raw.png"
DEST   = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\maps\City Trial Checklist.png"
DEST2  = r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride\images\maps\City Trial Checklist.png"
TARGET_SIZE = (640, 511)

img = Image.open(SOURCE).convert("RGB")
arr = np.array(img, dtype=np.int32)
h, w = arr.shape[:2]
print(f"Source size: {w}x{h}")

# ── 1. Detect the base "cell grey" colour ────────────────────────────────────
# Sample the interior of a clearly grey cell (approx centre of grid)
sample_y, sample_x = h // 2, w // 2
cell_grey = tuple(arr[sample_y, sample_x, :3].tolist())
print(f"Sampled cell grey: {cell_grey}")

# ── 2. Replace every non-grey coloured pixel inside the grid with cell_grey ──
# A pixel is "coloured" if it has a high saturation (r,g,b clearly not equal).
# We'll use a simple heuristic: max(r,g,b) - min(r,g,b) > threshold  = coloured
threshold = 30   # pixels with channel spread > this are non-grey

r = arr[:, :, 0]
g = arr[:, :, 1]
b = arr[:, :, 2]
spread = (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b))
coloured_mask = spread > threshold

# Only replace pixels roughly inside the grid region
# (avoid touching the outer frame / icons)
grid_top    = int(h * 0.07)
grid_bottom = int(h * 0.77)
grid_left   = int(w * 0.13)
grid_right  = int(w * 0.87)

mask = np.zeros((h, w), dtype=bool)
mask[grid_top:grid_bottom, grid_left:grid_right] = True
replace_mask = coloured_mask & mask

arr[replace_mask, 0] = cell_grey[0]
arr[replace_mask, 1] = cell_grey[1]
arr[replace_mask, 2] = cell_grey[2]

print(f"Replaced {replace_mask.sum()} coloured pixels with cell grey")

# ── 3. Fill the description bar at the bottom (below the grid) ───────────────
# Find the background colour by sampling near the bottom-left corner
bar_colour = tuple(arr[h - 20, 10, :3].tolist())
print(f"Bar fill colour: {bar_colour}")
arr[grid_bottom:, :] = bar_colour

# ── 4. Rebuild image and resize to 640x511 ───────────────────────────────────
clean = Image.fromarray(arr.astype(np.uint8))
final = clean.resize(TARGET_SIZE, Image.LANCZOS)
final.save(DEST)
final.save(DEST2)
print(f"Saved to {DEST}")
print(f"Saved to {DEST2}")
print("Done!")
