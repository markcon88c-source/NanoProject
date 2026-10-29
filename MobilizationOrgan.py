# MobilizationOrgan.py
# Corrected to match AlwaysThinkingHQ and new Unit/HQ classes

import math
import random
from HQ import HQ
from Unit import Unit

# ------------------------------------------------------------
# PERSONALITY-DRIVEN DIVISION NAMING
# ------------------------------------------------------------

DIV_NUMBERS = [
    "1st", "2nd", "3rd", "4th", "5th", "7th", "9th",
    "12th", "14th", "17th", "21st", "44th", "101st"
]

DIV_NAMES = [
    "Korbenhuber", "Eisenwald", "Falkensturm", "Drachenfeld",
    "Steinhammer", "Wolfsjäger", "Morgenlicht", "Schwarzberg"
]

DIV_TYPES = {
    "INF": "Infantry Division",
    "MOT": "Motorized Division",
    "ARM": "Panzer Division",
}

def generate_division_name(utype):
    num = random.choice(DIV_NUMBERS)
    root = random.choice(DIV_NAMES)
    suffix = DIV_TYPES.get(utype, "Division")
    return f"{num} {root} {suffix}"

# ------------------------------------------------------------
# MOBILIZATION ORGAN
# ------------------------------------------------------------

class MobilizationOrgan:
    def __init__(self, world, ctx):
        self.world = world
        self.ctx = ctx
        self.max_armies = 4
        self.max_corps_per_army = 3
        self.max_divs_per_corps = 4

    def run(self):
        events = self.tick()
        for e in events:
            self.world.send_message("MOBILIZATION", "SYSTEM", e, kind="mobilization")
        return self.ctx

    def tick(self):
        events = []
        events += self._mobilize_theater()
        events += self._mobilize_armies()
        events += self._mobilize_corps()
        return events

    def _ensure_hq_counters(self, hq):
        if not hasattr(hq, "div_counter"):
            hq.div_counter = 0
        if not hasattr(hq, "corps_counter"):
            hq.corps_counter = 0
        if not hasattr(hq, "army_counter"):
            hq.army_counter = 0

    def _hq(self, level):
        for h in self.world.hqs:
            if h.level == level:
                return h
        return None

    def _mobilize_theater(self):
        events = []
        theater = self._hq(0)
        if not theater:
            return events

        self._ensure_hq_counters(theater)

        need_armies = self._compute_army_shortage(theater)
        pressure = self._needheart_theater(need_armies)

        current_armies = sum(1 for h in self.world.hqs if h.level == 2)

        if pressure > 0.85 and current_armies < self.max_armies and need_armies > 0:
            new_id = f"{theater.id}_ARMY_{current_armies+1}"
            new_hq = HQ(new_id, theater.pos, 2)
            new_hq.parent = theater
            new_hq.region = theater.region
            new_hq.goal_region = theater.goal_region
            new_hq.nation = theater.nation
            new_hq.assigned = True

            self.world.hqs.append(new_hq)

            events.append(
                f"[MOBILIZATION] Theater {theater.id} raises new Army {new_hq.id} (pressure={pressure:.2f})"
            )

        return events

    def _mobilize_armies(self):
        events = []
        for army in [h for h in self.world.hqs if h.level == 2]:
            self._ensure_hq_counters(army)

            need_corps = self._compute_corps_shortage(army)
            pressure = self._needheart_army(need_corps)

            current_corps = sum(
                1 for h in self.world.hqs
                if h.level == 3 and getattr(h, "parent", None) is army
            )

            if pressure > 0.80 and current_corps < self.max_corps_per_army and need_corps > 0:
                new_id = f"{army.id}_CORPS_{current_corps+1}"
                new_corps = HQ(new_id, army.pos, 3)
                new_corps.parent = army
                new_corps.region = army.region
                new_corps.goal_region = army.goal_region
                new_corps.nation = army.nation
                new_corps.assigned = True

                self.world.hqs.append(new_corps)

                events.append(
                    f"[MOBILIZATION] Army {army.id} forms new Corps {new_corps.id} (pressure={pressure:.2f})"
                )

        return events

    def _mobilize_corps(self):
        events = []
        for corps in [h for h in self.world.hqs if h.level == 3]:
            self._ensure_hq_counters(corps)

            need_divs = self._compute_div_shortage(corps)
            pressure = self._needheart_corps(need_divs)

            current_divs = sum(
                1 for u in self.world.units
                if getattr(u, "echelon", None) == "Division"
                and getattr(u, "reattached_to", None) is corps
            )

            if pressure > 0.75 and current_divs < self.max_divs_per_corps and need_divs > 0:
                utype = self._choose_div_type(getattr(corps, "hinge", None))

                display_name = generate_division_name(utype)

                corps.div_counter += 1
                internal_id = f"{corps.id}_DIV_{corps.div_counter}"

                new_div = Unit(internal_id, display_name, corps.pos, utype)
                new_div.echelon = "Division"
                new_div.reattached_to = corps
                new_div.region = corps.region
                new_div.goal_region = corps.goal_region
                new_div.nation = corps.nation
                new_div.assigned = True

                self.world.units.append(new_div)
                corps.units.append(new_div)

                events.append(
                    f"[MOBILIZATION] Corps {corps.id} raises new {display_name} "
                    f"(ID={internal_id}, pressure={pressure:.2f})"
                )

        return events

    def _compute_army_shortage(self, theater):
        required = 2 if getattr(theater, "hinge", None) == "Commit_Main_Effort" else 1
        current = sum(1 for h in self.world.hqs if h.level == 2)
        return max(0, required - current)

    def _compute_corps_shortage(self, army):
        current = sum(
            1 for h in self.world.hqs
            if h.level == 3 and getattr(h, "parent", None) is army
        )
        required = 1
        return max(0, required - current)

    def _compute_div_shortage(self, corps):
        current = sum(
            1 for u in self.world.units
            if getattr(u, "echelon", None) == "Division"
            and getattr(u, "reattached_to", None) is corps
        )
        required = 3
        return max(0, required - current)

    def _needheart_theater(self, need_armies):
        return math.tanh(0.7 * need_armies)

    def _needheart_army(self, need_corps):
        return math.tanh(0.6 * need_corps)

    def _needheart_corps(self, need_divs):
        return math.tanh(0.5 * need_divs)

    def _choose_div_type(self, hinge):
        if hinge == "Commit_Main_Effort":
            return "ARM"
        elif hinge == "Probe_Enemy_Lines":
            return "INF"
        else:
            return "MOT"
