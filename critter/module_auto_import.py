import json
import importlib

with open("module_map.json", "r") as fh:
    organ_map = json.load(fh)

loaded = {}

for organ_name, module_path in organ_map.items():
    module = importlib.import_module(module_path)
    cls = getattr(module, organ_name)
    loaded[organ_name] = cls
