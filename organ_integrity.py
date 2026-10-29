# organ_integrity.py
# Drift-proof organ checker with GREP + constructor fingerprinting

import inspect
import re
import hashlib
import json
import os

FINGERPRINT_FILE = "organ_fingerprints.json"

REQUIRED_ORGANS = {
    # Core HQ ecosystem
    "HQ": "class",
    "Front": "class",
    "WorldState": "class",

    # Reorganization organ
    "apply_reorganization": "function",
    "compute_reorg_factor": "function",
    "compute_dispersion": "function",

    # Friction organ
    "update_friction": "function",
    "maybe_crash": "function",

    # Thinking organ
    "always_thinking": "function",

    # Supply organ
    "update_supply": "function",

    # Leadership organ
    "update_leadership": "function",

    # Terrain organ
    "update_terrain": "function",

    # Edge feedback organ
    "compute_edge_feedback": "function",

    # Downstream organ
    "send_downstream": "function",

    # Call-up organ
    "nano_callup": "function",

    # Air organ
    "AirPowerNano": "class",

    # HQ creation organ
    "create_theater_hq": "function",
    "create_army_group_hq": "function",
    "create_army_hq": "function",
    "create_corps_hq": "function",
}
def extract_useful_part(src):
    """Strip comments, whitespace, docstrings — keep only useful logic."""
    # Remove docstrings
    src = re.sub(r'"""(.*?)"""', '', src, flags=re.DOTALL)
    src = re.sub(r"'''(.*?)'''", '', src, flags=re.DOTALL)

    # Remove comments
    src = re.sub(r"#.*", "", src)

    # Remove blank lines
    lines = [line.strip() for line in src.split("\n") if line.strip()]

    return "\n".join(lines)


def fingerprint(src):
    """Hash the useful part of the organ."""
    useful = extract_useful_part(src)
    return hashlib.sha256(useful.encode()).hexdigest()


def load_fingerprints():
    if not os.path.exists(FINGERPRINT_FILE):
        return {}
    with open(FINGERPRINT_FILE, "r") as f:
        return json.load(f)


def save_fingerprints(fp):
    with open(FINGERPRINT_FILE, "w") as f:
        json.dump(fp, f, indent=4)


def verify_organs(modules, runner_source):
    fingerprints = load_fingerprints()

    missing = []
    broken = []
    unused = []
    import_missing = []
    drifted = []

    # ------------------------------------------------------------
    # 1. IMPORT CHECK
    # ------------------------------------------------------------
    for organ in REQUIRED_ORGANS:
        pattern = rf"import\s+.*{organ}"
        if not re.search(pattern, runner_source):
            import_missing.append(organ)

    # ------------------------------------------------------------
    # 2. DEFINITION + CONSTRUCTOR CHECK + FINGERPRINT
    # ------------------------------------------------------------
    for organ, organ_type in REQUIRED_ORGANS.items():
        found = False

        for m in modules:
            if hasattr(m, organ):
                found = True
                obj = getattr(m, organ)

                # Extract source
                try:
                    src = inspect.getsource(obj)
                except:
                    broken.append(organ)
                    break

                # Fingerprint
                fp = fingerprint(src)
                key = f"{m.__name__}.{organ}"

                if key in fingerprints:
                    if fingerprints[key] != fp:
                        drifted.append(organ)
                else:
                    fingerprints[key] = fp

                # Constructor check
                if organ_type == "class":
                    if not hasattr(obj, "__init__"):
                        broken.append(organ)

                break

        if not found:
            missing.append(organ)

    save_fingerprints(fingerprints)

    # ------------------------------------------------------------
    # 3. USAGE CHECK
    # ------------------------------------------------------------
    for organ in REQUIRED_ORGANS:
        if organ not in runner_source:
            unused.append(organ)

    # ------------------------------------------------------------
    # 4. CRASH IF ANYTHING WRONG
    # ------------------------------------------------------------
    if missing or broken or unused or import_missing or drifted:
        print("\n[ORGAN FAILURE] Organ integrity violation detected.")

        if import_missing:
            print("\nMissing imports:")
            for m in import_missing:
                print(f" - {m}")

        if missing:
            print("\nMissing definitions:")
            for m in missing:
                print(f" - {m}")

        if broken:
            print("\nBroken organs:")
            for b in broken:
                print(f" - {b}")

        if unused:
            print("\nUnused organs:")
            for u in unused:
                print(f" - {u}")

        if drifted:
            print("\nDrifted organs (fingerprint mismatch):")
            for d in drifted:
                print(f" - {d}")

        raise Exception("Organ integrity failure: rebuild required.")
