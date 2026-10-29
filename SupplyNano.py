# SupplyNano.py
# Models supply friction during long marches.

class SupplyNano:

    def __init__(self):
        self.base_supply = 1.0

    def update_supply(self, world):
        """
        Supply decreases with distance marched and time.
        Recovers slightly when close to objective.
        """

        # Degrade supply each tick
        self.base_supply -= 0.015

        # Recover when close to objective
        if world.theater_goal:
            name, gx, gy = world.theater_goal
            avg = sum(getattr(hq, "distance_to_goal", 0) for hq in world.hqs) / len(world.hqs)
            if avg < 5.0:
                self.base_supply += 0.02

        # Clamp
        if self.base_supply > 1.0:
            self.base_supply = 1.0
        if self.base_supply < 0.1:
            self.base_supply = 0.1

        world.supply_level = self.base_supply
