from PIL import Image
import numpy as np

src = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\Stadiums\city trial map with numbers.png"
dst = r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\maps\City Trial.png"
dst_pack = r"A:\Archipelago\poptracker_0-33-0_win64\poptracker\packs\Pop-Tracker- Kirby Air Ride\images\maps\City Trial.png"

img = Image.open(src).convert("RGB")
arr = np.array(img, dtype=np.float32)

R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# Step 1: detect pink/magenta pixels
pink_mask = (R > 160) & (G < 100) & (B > 160)

# Step 2: dilate pink mask to capture nearby shadows
# Manual dilation — expand mask outward by radius px
radius = 12
from PIL import ImageFilter
pink_img = Image.fromarray(pink_mask.astype(np.uint8) * 255)
dilated = pink_img.filter(ImageFilter.MaxFilter(size=radius * 2 + 1))
dilated_mask = np.array(dilated) > 0

# Step 3: within dilated area, also catch dark shadow pixels
dark_pixels = (R < 80) & (G < 80) & (B < 80)
shadow_mask = dilated_mask & dark_pixels

# Step 4: combine pink + shadow into full removal mask
full_mask = pink_mask | shadow_mask
print(f"Removing {full_mask.sum()} pixels (pink + shadows)")

# Step 5: inpaint — replace masked pixels with avg of nearby unmasked pixels
result = arr.copy()
sample_radius = 10
ys, xs = np.where(full_mask)

for y, x in zip(ys, xs):
    y1, y2 = max(0, y - sample_radius), min(arr.shape[0], y + sample_radius)
    x1, x2 = max(0, x - sample_radius), min(arr.shape[1], x + sample_radius)
    patch = arr[y1:y2, x1:x2]
    patch_mask = full_mask[y1:y2, x1:x2]
    good_pixels = patch[~patch_mask]
    if len(good_pixels) > 0:
        result[y, x] = good_pixels.mean(axis=0)

out = Image.fromarray(result.astype(np.uint8))
out.save(dst)
out.save(dst_pack)
print("Done!")
