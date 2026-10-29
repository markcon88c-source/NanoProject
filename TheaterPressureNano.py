# TheaterPressureNano.py
# Dynamic theater pressure evolution organ

import random

PRESSURE_LEVELS = ["GREEN", "YELLOW", "RED"]

class TheaterPressureNano:
    def __init__(self):
        self.tick_counter = 0

    def update(self, world):
        self.tick_counter += 1

        for front in world.fronts:
            # Random pressure evolution every few ticks
            if self.tick_counter % 3 == 0:
                front.pressure = random.choice(PRESSURE_LEVELS)

            # Pressure propagation to HQ chain
            owner = front.owner_hq
            owner.pressure = front.pressure

            # Propagate upward
            parent = owner.parent
            while parent:
                parent.pressure = front.pressure
                parent = parent.parent
