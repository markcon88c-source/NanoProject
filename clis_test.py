# clis_test.py
# Concept Logic Isolation Script v3 (Crash-proof)

from world_state import WorldState
from AlwaysThinkingHQ import always_thinking

def safe(obj, attr, default=None):
    """Safe attribute getter."""
    return getattr(obj, attr, default)

def clis_print(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def clis_test():
    world = WorldState()

    # Try running the pipeline, but catch hinge-graph errors
    try:
        always_thinking(world)
    except Exception as e:
        print("[WARNING] Pipeline crashed:", e)
        print("[INFO] Continuing CLIS test with partial world state.\n")

    # ------------------------------------------------------------
    # HQ LOGIC ISOLATION
    # ------------------------------------------------------------
    clis_print("HQ LOGIC (France vs Germany)")

    for hq in world.hqs:
        nation = safe(hq, "nation", None)
        region = safe(hq, "region", None)
        region_name = safe(region, "name", None)
        goal = safe(hq, "goal_region", None)
        goal_name = safe(goal, "name", None)
        assigned = safe(hq, "assigned", None)
        thought = safe(hq, "thought_flag", None)
        parent = safe(hq, "parent", None)
        parent_id = safe(parent, "id", None)

        print(f"{hq.id}:")
        print(f"  nation={nation}")
        print(f"  parent={parent_id}")
        print(f"  region={region_name}")
        print(f"  goal_region={goal_name}")
        print(f"  assigned={assigned}")
        print(f"  thought_flag={thought}")
        print()

    # ------------------------------------------------------------
    # UNIT LOGIC ISOLATION
    # ------------------------------------------------------------
    clis_print("UNIT LOGIC (France vs Germany)")

    for u in world.units:
        hq = safe(u, "hq", None)
        hq_id = safe(hq, "id", None)
        nation = safe(hq, "nation", None)
        assigned = safe(u, "assigned", None)
        thought = safe(u, "thought_flag", None)

        print(f"{u.id}:")
        print(f"  hq={hq_id}")
        print(f"  nation={nation}")
        print(f"  assigned={assigned}")
        print(f"  thought_flag={thought}")
        print()

    # ------------------------------------------------------------
    # STAGE 3b PROPAGATION CHECK
    # ------------------------------------------------------------
    clis_print("STAGE 3b PROPAGATION CHECK")

    for hq in world.hqs:
        parent = safe(hq, "parent", None)
        parent_nation = safe(parent, "nation", None)
        hq_nation = safe(hq, "nation", None)
        same = (parent_nation == hq_nation) if parent else None

        print(f"{hq.id}: parent={safe(parent, 'id', None)}, same_nation={same}")

if __name__ == "__main__":
    clis_test()
