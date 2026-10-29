# bombing_pressure.py
# Computes bombing pressure independently of air superiority

import math

class BombingPressure:
    def __init__(self, world):
        self.world = world

    def compute(self):
        strike_units = []
        recon_units = []
        support_units = []

        for u in self.world.units:
            # Accept both new and legacy unit attribute names
            utype = getattr(u, "utype", None) or getattr(u, "type", None)

            if utype in ("STRIKE", "CAS", "TAC"):
                strike_units.append(u)

            if utype == "RECON":
                recon_units.append(u)

            if utype == "SUPPORT":
                support_units.append(u)

        enemy_ground_density = getattr(self.world, "enemy_ground_density", 5)

        recon_bonus = len(recon_units) * 0.10
        support_bonus = len(support_units) * 0.05

        strike_ratio = len(strike_units) / max(1, enemy_ground_density)

        score = strike_ratio + recon_bonus + support_bonus
        pressure = math.tanh(score * 0.8)

        if pressure > 0.75:
            state = "GREEN"
        elif pressure > 0.40:
            state = "YELLOW"
        else:
            state = "RED"

        return state, pressure
