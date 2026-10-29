import re

with open("init_world.py") as f:
    text = f.read()

# Find the line where CORPS_A gets its goal
matches = re.findall(r'CORPS_A.*?goal_region\s*=\s*world\.hinge_graph\["([^"]+)"\]', text)

print("\n=== CORPS_A GOAL REGION ===\n")

if matches:
    print("CORPS_A is assigned to region:", matches[0])
else:
    print("CORPS_A goal region not found in init_world.py")
