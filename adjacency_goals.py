# adjacency_goals.py
# Assigns per-HQ goals based on hinge-graph adjacency and hinge state.

import random

def choose_next_region(region, world, hq):
    """
    Simple adjacency-based goal selection:
      - if no adjacents: stay in place
      - otherwise: pick one adjacent region
      - later: can be made hinge/pressure-aware
    """
    if not region.adjacent:
        return region

    # For now, just pick a random adjacent region to avoid lockstep
    next_name = random.choice(region.adjacent)
    return world.hinge_graph[next_name]


def update_hq_goals(world):
    """
    For each HQ:
      - ensure it has a region
      - choose a next region via adjacency
      - assign that as its goal_region
    """

    if world.hinge_graph is None:
        return

    for hq in world.hqs:
        region = hq.region
        if region is None:
            # Try to assign a region if missing
            region = world._nearest(hq.pos)
            hq.region = region

        if region is None:
            continue

        next_region = choose_next_region(region, world, hq)
        hq.goal_region = next_region
