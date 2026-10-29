#!/usr/bin/env python3
import os
import re
import json

ROOT = os.path.join(os.getcwd(), "organs")

organ_map = {}

class_pattern = re.compile(r"class\s+([A-Za-z0-9_]+Organ)\s*[:\(]")

for root, dirs, files in os.walk(ROOT):
    for f in files:
        if not f.endswith(".py"):
            continue

        full = os.path.join(root, f)
        rel = os.path.relpath(full, os.getcwd())
        module = rel.replace("/", ".").replace(".py", "")

        with open(full, "r", encoding="utf-8") as fh:
            text = fh.read()

        for match in class_pattern.findall(text):
            organ_map[match] = module

print("\n=== ORGAN → MODULE MAP ===\n")
for organ, module in organ_map.items():
    print(f"{organ:30}  from {module} import {organ}")

print("\n=== JSON OUTPUT (module_map.json) ===\n")
with open("module_map.json", "w", encoding="utf-8") as out:
    json.dump(organ_map, out, indent=4)

print("Wrote module_map.json")
