# WanderOrgan_v2.py
# Purposeful wandering based on loci goals, hinge adjacency,
# future axes, bombing pressure, supply, friction, and hinge mood.

import random
from geo_hinge_graph import path_distance

class WanderOrganV2:
    def __init__(self, world):
        self.world = world

    def tick(self):
        events = []

        bombing = getattr(self.world, "bombing_pressure", 0.0)
        friction = getattr(self.world, "friction", 0.0)

        for u in self.world.units:
            parent = getattr(u, "parent", None)
            if parent is None:
                continue

            # 1. Determine loci goals
            current_goal = getattr(parent, "goal_region", None)
            future_goal = getattr(parent, "future_goal_region", None)
            long_goal = getattr(parent, "long_range_goal_region", None)

            if current_goal is None:
                continue

            # 2. Get hinge adjacency
            region = getattr(u, "region", None)
            if region is None:
                continue

            adj = getattr(region, "adjacent", [])

            # 3. Filter adjacency by loci goal direction
            candidates = []
            for r in adj:
                d_current = path_distance(r, current_goal)
                d_here = path_distance(region, current_goal)
                if d_current is not None and d_here is not None:
                    if d_current < d_here:
                        candidates.append(r)

            # 4. Future goal alignment
            if future_goal:
                aligned = []
                for r in candidates:
                    d_future = path_distance(r, future_goal)
                    d_here_future = path_distance(region, future_goal)
                    if d_future is not None and d_here_future is not None:
                        if d_future <= d_here_future:
                            aligned.append(r)
                if aligned:
                    candidates = aligned

            # 5. Long-range axis alignment (soft bias)
            if long_goal:
                candidates.sort(
                    key=lambda r: path_distance(r, long_goal) or 9999
                )

            # 6. Wander radius
            max_wander = 1.0
            filtered = []
            for r in candidates:
                dx = r.pos[0] - region.pos[0]
                dy = r.pos[1] - region.pos[1]
                if (dx*dx + dy*dy)**0.5 <= max_wander:
                    filtered.append(r)

            if not filtered:
                continue

            # 7. Pressure-aware filtering
            pressure_filtered = []

            for r in filtered:
                # Avoid bombing pressure
                local_bomb = getattr(self.world.region_pulse, r.name, 0.0)
                if local_bomb > bombing * 1.2:
                    continue

                # Seek supply
                local_supply = getattr(self.world.supply_map, r.name, 1.0)
                if local_supply < 0.3:
                    continue

                pressure_filtered.append(r)

            if not pressure_filtered:
                pressure_filtered = filtered

            # 8. Friction slowdown
            friction_factor = max(0.1, 1.0 - friction)

            # 9. Choose a wander target
            target = random.choice(pressure_filtered)

            # 10. Move unit toward target (small step)
            base_step = 0.05
            step = base_step * friction_factor

            dx = target.pos[0] - u.pos[0]
            dy = target.pos[1] - u.pos[1]
            dist = (dx*dx + dy*dy)**0.5

            if dist > 0.01:
                u.pos = (
                    u.pos[0] + (dx / dist) * step,
                    u.pos[1] + (dy / dist) * step
                )
                u.region = target
                events.append(f"{u.id} wanders toward {target.name}")

        return events
