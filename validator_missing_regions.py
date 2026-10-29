import re

defined = set()
referenced = set()

with open("geo_hinge_graph.py") as f:
    text = f.read()

# Find all defined regions: g["NAME"] = Region(
for name in re.findall(r'g\["([^"]+)"\]\s*=\s*Region', text):
    defined.add(name)

# Find all referenced regions in link("A","B")
for a, b in re.findall(r'link\("([^"]+)",\s*"([^"]+)"\)', text):
    referenced.add(a)
    referenced.add(b)

missing = referenced - defined

print("Defined regions:", len(defined))
print("Referenced regions:", len(referenced))
print("Missing regions:", len(missing))

if missing:
    print("\nMissing region names:")
    for m in sorted(missing):
        print(" -", m)
else:
    print("\nNo missing regions.")
