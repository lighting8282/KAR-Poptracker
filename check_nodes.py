import json

with open(r"A:\Archipelago\Games\Kirby Air Ride\Pop-Tracker- Kirby Air Ride\locations\Top Ride.json") as f:
    data = json.load(f)

def check_node(node):
    name = node["name"]
    for ml in node.get("map_locations", []):
        x, y = ml.get("x", 0), ml.get("y", 0)
        out_of_bounds = x > 640 or y > 511 or x < 0 or y < 0
        flag = " *** OUT OF BOUNDS" if out_of_bounds else ""
        print(name + " -> x=" + str(x) + " y=" + str(y) + flag)
    for child in node.get("children", []):
        check_node(child)

for n in data:
    check_node(n)
