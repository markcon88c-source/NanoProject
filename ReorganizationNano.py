import random

def apply_reorganization(world):
    r = random.random()

    if r < 0.15:
        world.leadership_level += 0.05
        world.edge_feedback -= 5.0
        world.terrain_level += 0.02
        print("[REORG] HQs reorganized effectively.")

    elif r < 0.45:
        world.leadership_level -= 0.08
        world.edge_feedback += 8.0
        world.terrain_level -= 0.03
        print("[REORG] HQs reorganized poorly.")

    else:
        world.leadership_level -= 0.15
        world.edge_feedback += 15.0
        world.terrain_level -= 0.05
        print("[REORG] HQs reorganized chaotically!")

    world.leadership_level = max(0.3, min(1.0, world.leadership_level))
    world.terrain_level = max(0.5, min(1.0, world.terrain_level))
