# movement.py
# Dynamic movement organ for NanoRunner
# HQs and units move using assignment + future goals + long-range goals.

from geo_hinge_graph import path_distance

# ------------------------------------------------------------
# HQ DISTANCE CALCULATION
# ------------------------------------------------------------
def update_hq_distances(world):
    distances = []
    for hq in world.hqs:
        goal = getattr(hq, "goal_region", None)
        region = getattr(hq, "region", None)

        if goal is None or region is None:
            hq.distance_to_goal = 0.0
            continue

        hops = path_distance(region, goal)
        if hops is None:
            hops = 0

        radius = getattr(region, "radius_km", 50.0)
        hq.distance_to_goal = hops * radius
        distances.append(hq.distance_to_goal)

    world.avg_hq_distance = sum(distances) / len(distances) if distances else 0.0


# ------------------------------------------------------------
# HQ MOVEMENT — dynamic, future-weighted
# ------------------------------------------------------------
def move_hqs(world):
    for hq in world.hqs:
        region = getattr(hq, "region", None)
        if region is None:
            region = world._nearest(hq.pos)
            hq.region = region

        # Thought-driven assignment
        goal = getattr(hq, "goal_region", None)
        if goal is None:
            goal = region

        # Weighted movement vector
        fx = fy = 0.0

        # Assignment (strong)
        gx, gy = goal.pos
        fx += gx * 0.60
        fy += gy * 0.60

        # Future goal (medium)
        future = getattr(hq, "future_goal_region", None)
        if future:
            fx += future.pos[0] * 0.25
            fy += future.pos[1] * 0.25

        # Long-range goal (light)
        long = getattr(hq, "long_range_goal_region", None)
        if long:
            fx += long.pos[0] * 0.15
            fy += long.pos[1] * 0.15

        target = (fx, fy)

        # Hinge mood → speed
        hinge = getattr(hq, "hinge", "Probe_Enemy_Lines")

        if hinge == "Commit_Main_Effort":
            speed = 0.12
        elif hinge == "Probe_Enemy_Lines":
            speed = 0.08
        elif hinge == "Secure_Supply_Lines":
            speed = 0.05
        elif hinge == "Stabilize_Command":
            speed = 0.03
        elif hinge == "Delay_Action":
            speed = 0.02
        else:
            speed = 0.06

        # Move toward target
        hx, hy = hq.pos
        tx, ty = target

        dx = tx - hx
        dy = ty - hy
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 0:
            hq.pos = (
                hx + (dx / dist) * speed,
                hy + (dy / dist) * speed,
            )

        # Update region
        hq.region = world._nearest(hq.pos)


# ------------------------------------------------------------
# UNIT MOVEMENT — dynamic, follows HQ
# ------------------------------------------------------------
def move_units(world):
    for u in world.units:
        hq = getattr(u, "reattached_to", None)
        if hq is None:
            hq = getattr(u, "hq", None)

        if hq is None:
            continue

        ux, uy = u.pos
        hx, hy = hq.pos

        dx = hx - ux
        dy = hy - uy
        dist = (dx * dx + dy * dy) ** 0.5

        speed = 0.03

        if dist > 0:
            u.pos = (
                ux + (dx / dist) * speed,
                uy + (dy / dist) * speed,
            )
