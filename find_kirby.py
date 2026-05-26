from PIL import Image
img = Image.open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\GameCube - Kirby Air Ride - Miscellaneous - Kirby.png")
# Save test crops at different y positions to find the circles
for y in [230, 260, 290, 310, 330]:
    crop = img.crop((50, y, 130, y + 70))
    crop.save(fr"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\images\test_y{y}.png")
    print(f"Saved test at y={y}")
