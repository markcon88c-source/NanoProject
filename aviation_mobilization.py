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

        air_armies = [h for h in self.world.hqs if h.level == 10]
        if len(air_armies) == 0:
            new_air_army = HQ(
                id="AIR_ARMY_1",
                pos=theater.pos,
                level=10
            )
            self._ensure_hq_counters(new_air_army)
            new_air_army.parent = theater
            self.world.hqs.append(new_air_army)

            events.append(
                f"[AIR MOBILIZATION] Theater {theater.id} raises new Air Army {new_air_army.id}"
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
                new_wing = HQ(
                    id=f"{air_army.id}_WING_{air_army.air_wing_counter}",
                    pos=air_army.pos,
                    level=11
                )
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
                if getattr(u, "echelon", None) == "Air Squadron"
                and getattr(u, "reattached_to", None) is wing
            ]

            if len(current_squadrons) < self.max_squadrons_per_wing:

                hinge = getattr(wing, "hinge", None)
                asp = getattr(self.world, "air_superiority_state", "GREEN")
                bp = getattr(self.world, "bombing_state", "GREEN")

                if asp == "RED":
                    atype = "INTERCEPT"
                elif bp == "RED":
                    atype = "RECON"
                elif hinge == "Commit_Main_Effort":
                    atype = "STRIKE"
                elif hinge == "Probe_Enemy_Lines":
                    atype = "RECON"
                else:
                    atype = "SUPPORT"

                display_name = generate_air_name(atype)

                wing.air_squadron_counter += 1
                internal_name = f"{wing.id}_SQ_{wing.air_squadron_counter}"

                pos = wing.pos

                # Use new Unit signature: Unit(id, name, pos, utype)
                new_sq = Unit(internal_name, display_name, pos, atype)

                # Set echelon + hierarchy + nation
                new_sq.echelon = "Air Squadron"
                new_sq.parent = wing
                new_sq.reattached_to = wing
                new_sq.assigned = True
                new_sq.nation = getattr(wing, "nation", None)

                # Region inheritance
                new_sq.region = getattr(wing, "region", None)
                if new_sq.region is not None:
                    new_sq.pos = new_sq.region.pos

                # Add to world + wing
                wing.units.append(new_sq)
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
