import re
import time

# Load hinge graph file
with open("geo_hinge_graph.py") as f:
    hinge = f.read()

# Load init_world file
with open("init_world.py") as f:
    initw = f.read()

# Extract defined hinge regions
defined = set(re.findall(r'g\["([^"]+)"\]\s*=\s*Region', hinge))

# Extract referenced regions in init_world
referenced = set(re.findall(r'hinge_graph\["([^"]+)"\]', initw))

missing = referenced - defined

# Delay to ensure runner spam finishes
time.sleep(1)

print("\n\n============================================================")
print("                 MISSING INIT_WORLD REGIONS")
print("============================================================\n")

if missing:
    for m in sorted(missing):
        print(" >>> MISSING REGION:", m)
else:
    print(" >>> NO MISSING REGIONS FOUND")

print("\n============================================================\n")
