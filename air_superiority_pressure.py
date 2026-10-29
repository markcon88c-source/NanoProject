# air_superiority_pressure.py
# Computes air superiority pressure independently of bombing pressure

import math

class AirSuperiorityPressure:
    def __init__(self, world):
        self.world = world

    def compute(self):
        # Friendly interceptors / fighters
        friendly_fighters = []
        recon_units = []

        for u in self.world.units:
            utype = getattr(u, "utype", None) or getattr(u, "type", None)

            if utype in ("INTERCEPT", "FTR", "AIR"):
                friendly_fighters.append(u)

            if utype == "RECON":
                recon_units.append(u)

        # Enemy fighter density (world may override this)
        enemy_fighters = getattr(self.world, "enemy_air_density", 3)

        # Recon survivability bonus
        recon_bonus = len(recon_units) * 0.15

        # Escort ratio
        escort_ratio = len(friendly_fighters) / max(1, enemy_fighters)

        # Bombing pressure → escort mobilization → ASP boost
        bombing_state = getattr(self.world, "bombing_state", "GREEN")
        if bombing_state == "RED":
            escort_bonus = 0.3
        elif bombing_state == "YELLOW":
            escort_bonus = 0.15
        else:
            escort_bonus = 0.0

        # Final superiority score
        score = escort_ratio + recon_bonus + escort_bonus
        pressure = math.tanh(score * 0.7)

        if pressure > 0.75:
            state = "GREEN"
        elif pressure > 0.40:
            state = "YELLOW"
        else:
            state = "RED"

        return state, pressure
