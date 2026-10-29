# friction.py
# Dispersion, reorganization factor, edge feedback, and friction engine.

import math
import random


# ------------------------------------------------------------
# DISPERSION
# ------------------------------------------------------------
def compute_dispersion(world):
    """
    Measures how spread out HQs are around their centroid.
    Higher dispersion → more command friction.
    """
    xs = [hq.pos[0] for hq in world.hqs]
    ys = [hq.pos[1] for hq in world.hqs]

    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    return sum(
        math.sqrt((x - cx)**2 + (y - cy)**2)
        for x, y in zip(xs, ys)
    )


# ------------------------------------------------------------
# REORGANIZATION FACTOR
# ------------------------------------------------------------
def compute_reorg_factor(world):
    """
    Measures how much HQ dispersion changed since last tick.
    Positive delta → HQs converged → lower friction.
    Negative delta → HQs scattered → higher friction.
    """
    prev = world.prev_dispersion
    curr = compute_dispersion(world)
    world.prev_dispersion = curr

    if prev is None:
        return 0.0

    delta = prev - curr
    return max(-1.0, min(1.0, delta * 0.3))


# ------------------------------------------------------------
# EDGE FEEDBACK
# ------------------------------------------------------------
def compute_edge_feedback(world, effects=None):
    """
    Edge feedback is the organism’s “stress signal.”
    It increases when:
      - HQs are far from the goal
      - HQs are unevenly spread
      - Downstream effects are weak
    """
    if effects:
        base_effect = sum(effects) / len(effects)
    else:
        dists = [hq.distance_to_goal for hq in world.hqs]
        if not dists:
            world.edge_feedback = 0.0
            return
        base_effect = sum(dists) / len(dists)

    dists = [hq.distance_to_goal for hq in world.hqs]
    spread = (max(dists) - min(dists)) if dists else 0.0

    base = base_effect * 8.0 + spread * 12.0
    noise = random.uniform(-3.0, 3.0)

    world.edge_feedback = max(0.0, base + noise)


# ------------------------------------------------------------
# FRICTION ENGINE
# ------------------------------------------------------------
def update_friction(world):
    """
    Friction is the organism’s “command difficulty” score.
    It rises when:
      - HQs are far from the goal
      - Edge feedback is high
      - Terrain is bad
      - Leadership is low
      - Supply is low
      - Reorganization is chaotic
    """

    dists = [hq.distance_to_goal for hq in world.hqs]
    avg_dist = sum(dists) / len(dists) if dists else 0.0
    world.avg_hq_distance = avg_dist

    # Normalize distance → D
    D = max(0.0, min(1.0, (avg_dist - 2.0) / 6.0))

    # Normalize edge feedback → E
    E = max(0.0, min(1.0, world.edge_feedback / 50.0))

    L = world.leadership_level
    S = world.supply_level
    T = world.terrain_level
    R = compute_reorg_factor(world)

    # Weighted friction target
    F_target = (
        0.25 * D +
        0.20 * E +
        0.20 * (1.0 - T) +
        0.20 * (1.0 - L) +
        0.10 * (1.0 - S) +
        0.15 * R
    )

    beta = 0.15
    noise = random.uniform(-0.03, 0.03)

    world.friction = max(
        0.0,
        min(1.0, (1 - beta) * world.friction + beta * F_target + noise)
    )
