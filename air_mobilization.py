# aviation_mobilization.py
# Airpower mobilization organ (HQ creates air armies, wings, squadrons, flights)
# Personality-based naming for air units

import math
import random
from world_state import HQ, Unit

# ------------------------------------------------------------
# PERSONALITY NAMES FOR AIR UNITS
# ------------------------------------------------------------

AIR_NUMBERS = [
    "1st", "2nd", "3rd", "5th", "7th", "9th",
    "12th", "21st", "44th", "88th", "101st"
]

AIR_NAMES = [
    "Himmeljäger", "Sturmfalke", "Drachenflug",
    "Eisenwing", "Wolkenhammer", "Nachtvogel",
    "Schattenflug", "Morgenfalke"
]

AIR_TYPES = {
    "RECON": "Recon Squadron",
    "INTERCEPT": "Interceptor Squadron",
    "STRIKE": "Strike Squadron",
    "SUPPORT": "Support Squadron"
}

def generate_air_name(atype):
    num = random.choice(AIR_NUMBERS)
    root = random.choice(AIR_NAMES)
    suffix = AIR_TYPES.get(atype, "Air Squadron")
    return f"{num} {root} {suffix}"


# ------------------------------------------------------------
# AVIATION MOBILIZATION ORGAN
# ------------------------------------------------------------

class AviationMobilizationOrgan:
    def __init__(self, world):
        self.world = world
        self.max_air_wings = 6
        self.max_squadrons_per_wing = 4

    # Safety: ensure counters exist
    def _ensure_hq_counters(self, hq):
        if not hasattr(hq, "air_wing_counter"):
            hq.air_wing_counter = 0
        if not hasattr(hq, "air_squadron_counter"):
            hq.air_squadron_counter = 0

    def tick(self):
        events = []
        events += self._mobilize_air_army()
        events += self._mobilize_air_wings()
        events += self._mobilize_squadrons()
        return events

    # ------------------------------------------------------------
    # THEATER → AIR ARMY
    # ------------------------------------------------------------
    def _mobilize_air_army(self):
        events = []
        theater = self._hq(0)
        if not theater:
            return events

        self._ensure_hq_counters(theater)

        # Shortage: no air army
        air_armies = [h for h in self.world.hqs if h.level == 10]  # Air Army level = 10
        if len(air_armies) == 0:
            new_air_army = HQ(level=10)
            new_air_army.id = "AIR_ARMY_1"
            new_air_army.pos = theater.pos
            self._ensure_hq_counters(new_air_army)
            self.world.hqs.append(new_air_army)

            events.append(
                f"[AIR MOBILIZATION] Theater {theater.id} raises new Air Army AIR_ARMY_1"
            )

        return events

    # ------------------------------------------------------------
    # AIR ARMY → AIR WINGS
    # ------------------------------------------------------------
    def _mobilize_air_wings(self):
        events = []
        air_armies = [h for h in self.world.hqs if h.level == 10]

        for air_army in air_armies:
            self._ensure_hq_counters(air_army)

            current_wings = [
                h for h in self.world.hqs
                if h.level == 11 and getattr(h, "parent", None) is air_army
            ]

            if len(current_wings) < self.max_air_wings:
                air_army.air_wing_counter += 1
                new_wing = HQ(level=11)
                new_wing.id = f"{air_army.id}_WING_{air_army.air_wing_counter}"
                new_wing.pos = air_army.pos
                new_wing.parent = air_army
                self._ensure_hq_counters(new_wing)
                self.world.hqs.append(new_wing)

                events.append(
                    f"[AIR MOBILIZATION] Air Army {air_army.id} forms new Air Wing {new_wing.id}"
                )

        return events

    # ------------------------------------------------------------
    # AIR WING → SQUADRONS
    # ------------------------------------------------------------
    def _mobilize_squadrons(self):
        events = []
        wings = [h for h in self.world.hqs if h.level == 11]

        for wing in wings:
            self._ensure_hq_counters(wing)

            current_squadrons = [
                u for u in self.world.units
                if u.echelon == "Air Squadron" and u.reattached_to is wing
            ]

            if len(current_squadrons) < self.max_squadrons_per_wing:

                # Determine squadron type based on hinge
                hinge = wing.hinge
                if hinge == "Probe_Enemy_Lines":
                    atype = "RECON"
                elif hinge == "Commit_Main_Effort":
                    atype = "STRIKE"
                elif hinge == "Stabilize_Command":
                    atype = "INTERCEPT"
                else:
                    atype = "SUPPORT"

                # Personality name
                display_name = generate_air_name(atype)

                # Internal ID
                wing.air_squadron_counter += 1
                internal_name = f"{wing.id}_SQ_{wing.air_squadron_counter}"

                pos = wing.pos
                new_sq = Unit(
                    name=display_name,
                    utype=atype,
                    echelon="Air Squadron",
                    pos=pos
                )
                new_sq.internal_id = internal_name
                new_sq.reattached_to = wing

                self.world.units.append(new_sq)

                events.append(
                    f"[AIR MOBILIZATION] Wing {wing.id} raises new {display_name} (ID={internal_name})"
                )

        return events

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _hq(self, level):
        for h in self.world.hqs:
            if h.level == level:
                return h
        return None
