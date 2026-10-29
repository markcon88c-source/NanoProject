# DownstreamNano.py
# Collects downstream effects from HQs and units.

import math

def collect_downstream(world):
    """
    Collects downstream effects from HQs and units.
    Returns a dict of causal signals for edge feedback.
    """

    effects = {
        "avg_distance": 0.0,
        "avg_pressure_green": 0,
        "hinge_counts": {},
        "air_pressure_green": 0,
        "movement_energy": 0.0,
        "hq_count": len(world.hqs)
    }

    # HQ effects
    for hq in world.hqs:

        # distance
        d = getattr(hq, "distance_to_goal", None)
        if d is not None:
            effects["avg_distance"] += d

        # pressure
        if getattr(hq, "pressure", None) == "GREEN":
            effects["avg_pressure_green"] += 1

        # hinge
        hinge = getattr(hq, "hinge", None)
        if hinge:
            effects["hinge_counts"][hinge] = effects["hinge_counts"].get(hinge, 0) + 1

        # movement energy
        if hasattr(hq, "pos") and hasattr(hq, "last_pos"):
            x, y = hq.pos
            lx, ly = hq.last_pos
            dx = x - lx
            dy = y - ly
            effects["movement_energy"] += math.sqrt(dx*dx + dy*dy)

        # update last_pos
        hq.last_pos = hq.pos

    # Air pressure
    for hq in world.hqs:
        if getattr(hq, "air", None) == "GREEN":
            effects["air_pressure_green"] += 1

    # Normalize distance
    if effects["hq_count"] > 0:
        effects["avg_distance"] /= effects["hq_count"]

    return effects
