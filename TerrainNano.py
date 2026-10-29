# TerrainNano.py
# Models terrain friction based on HQ position.

import math

class TerrainNano:

    def __init__(self):
        pass

    def terrain_at(self, x, y):
        """
        Simple terrain classifier based on coordinates.
        Replace with real map later.
        """

        # Forest band
        if 48 < x < 50 and 3 < y < 6:
            return "FOREST"

        # Hills
        if 50 < x < 52 and 4 < y < 7:
            return "HILLS"

        # Urban (Amsterdam region)
        if 52.0 < x < 52.5 and 4.7 < y < 5.2:
            return "URBAN"

        return "PLAINS"

    def terrain_friction(self, terrain):
        if terrain == "PLAINS":
            return 1.0
        if terrain == "FOREST":
            return 0.7
        if terrain == "HILLS":
            return 0.5
        if terrain == "URBAN":
            return 0.4
        return 1.0

    def update_terrain(self, world):
        """
        Computes average terrain friction for all HQs.
        """

        frictions = []
        for hq in world.hqs:
            x, y = hq.pos
            t = self.terrain_at(x, y)
            f = self.terrain_friction(t)
            frictions.append(f)

        world.terrain_level = sum(frictions) / len(frictions)
