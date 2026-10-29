# callup_flexible.py
# Hinge-aware, adjacency-aware, type-aware call-up organ

import math
from geo_hinge_graph import bfs_path, path_distance

class CallUpFlexible:
    def __init__(self, world):
        self.world = world

        # Core command echelons
        self.valid_echelons = {
            "Division", "Brigade", "Corps", "Army",
            "ArmyGroup", "Theater", "Squadron", "Flotilla"
        }

    # ------------------------------------------------------------
    # NEURAL HEART — HQ shortage → scalar need signal
    # ------------------------------------------------------------
    def compute_needheart(self):
        w = self.world

        need_armies = 0
        need_corps = 0
        need_divs = 0

        theater = self._hq(0)
        if theater:
            hinge = getattr(theater, "hinge", "Commit_Main_Effort")
            required = 2 if hinge == "Commit_Main_Effort" else 1
            current = sum(1 for u in w.units if getattr(u, "echelon", None) == "Army")
            need_armies = max(0, required - current)

        army = self._hq(2)
        if army:
            current_corps = sum(1 for u in w.units if getattr(u, "echelon", None) == "Corps")
            current_divs = sum(1 for u in w.units if getattr(u, "echelon", None) == "Division")
            need_corps = max(0, 1 - current_corps)
            need_divs = max(0, 3 - current_divs)

        β1, β2, β3 = 0.6, 0.3, 0.2
        need_raw = β1 * need_armies + β2 * need_corps + β3 * need_divs

        return math.tanh(need_raw)

    # ------------------------------------------------------------
    # COMMAND QUALITY SCORE (CQS)
    # ------------------------------------------------------------
    def compute_cqs(self):
        w = self.world

        eff = 0
        for u in w.units:
            echelon = getattr(u, "echelon", None)
            parent = getattr(u, "parent", None)
            parent_level = getattr(parent, "level", None)

            if echelon == "Division" and parent_level == 3:
                eff += 1
            elif echelon == "Corps" and parent_level == 2:
                eff += 1
            elif echelon == "Army" and parent_level == 1:
                eff += 1
            elif echelon == "ArmyGroup" and parent_level == 0:
                eff += 1

        eff /= max(1, len(w.units))

        friction_penalty = 1.0 - w.friction
        dist_penalty = 1.0 - (getattr(w, "avg_hq_distance", 0.0) / 10.0)

        hinge = getattr(w.hqs[0], "hinge", "Commit_Main_Effort") if w.hqs else "Commit_Main_Effort"

        if hinge == "Commit_Main_Effort":
            pressure_align = 1.0 if eff > 0.6 else 0.3
        elif hinge == "Probe_Enemy_Lines":
            pressure_align = 1.0 if eff < 0.4 else 0.3
        else:
            pressure_align = 0.5

        stability = 1.0 - min(1.0, abs(w.edge_feedback) / 20.0)
        needheart = self.compute_needheart()

        cqs = (
            0.25 * eff +
            0.20 * friction_penalty +
            0.20 * dist_penalty +
            0.20 * pressure_align +
            0.10 * stability +
            0.15 * needheart
        )

        return max(0.0, min(1.0, cqs))

    # ------------------------------------------------------------
    # MAIN CALL-UP ORGAN
    # ------------------------------------------------------------
    def run(self):
        w = self.world
        moved = []

        theater = self._hq(0)
        ag = self._hq(1)
        army = self._hq(2)
        corps = self._hq(3)
        air_hq = self._hq(10)
        naval_hq = self._hq(20)

        cqs = self.compute_cqs()
        needheart = self.compute_needheart()

        # Integrate new units in a hinge-aware, type-aware way
        self._integrate_new_units(corps, air_hq, naval_hq, moved)

        # --------------------------------------------------------
        # DYNAMIC UPWARD MOVEMENT (hinge-aware)
        # --------------------------------------------------------
        if cqs < 0.55 and needheart < 0.5:
            for u in w.units:
                if not self._hinge_ok(u):
                    continue

                if u.echelon == "Division":
                    self._move(u, "Corps", corps, "DYN DIV→CORPS", moved)

                elif u.echelon == "Corps" and w.edge_feedback > 5.0:
                    self._move(u, "Army", army, "DYN CORPS→ARMY", moved)

                elif u.echelon == "Army" and w.edge_feedback > 8.0:
                    self._move(u, "ArmyGroup", ag, "DYN ARMY→AG", moved)

                elif u.echelon == "ArmyGroup" and w.edge_feedback > 12.0:
                    self._move(u, "Theater", theater, "DYN AG→THEATER", moved)

        # --------------------------------------------------------
        # DYNAMIC DOWNWARD MOVEMENT (hinge-aware)
        # --------------------------------------------------------
        if cqs > 0.75 or needheart > 0.7:
            for u in w.units:
                if not self._hinge_ok(u):
                    continue

                if u.echelon == "ArmyGroup":
                    self._move(u, "Army", army, "DYN AG→ARMY", moved)

                elif u.echelon == "Army":
                    self._move(u, "Corps", corps, "DYN ARMY→CORPS", moved)

                elif u.echelon == "Corps":
                    self._move(u, "Division", corps, "DYN CORPS→DIV", moved)

        # --------------------------------------------------------
        # DYNAMIC REORGANIZATION (hinge-aware)
        # --------------------------------------------------------
        if 0.55 <= cqs <= 0.75:
            for u in w.units:
                if not self._hinge_ok(u):
                    continue

                if u.echelon == "Division" and corps:
                    self._move(u, "Corps", corps, "DYN REORG DIV→CORPS", moved)

                if u.echelon == "Corps" and army:
                    self._move(u, "Army", army, "DYN REORG CORPS→ARMY", moved)

        self._theater_shortage(theater)
        self._army_shortage(army)

        return moved

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _hq(self, level):
        for h in self.world.hqs:
            if getattr(h, "level", None) == level:
                return h
        return None

    def _hinge_ok(self, unit):
        """Check hinge adjacency between unit.region and HQ.region."""
        parent = getattr(unit, "parent", None)
        if not parent:
            return True

        if not unit.region or not parent.region:
            return True

        d = path_distance(unit.region, parent.region)
        return d is not None and d <= 3

    def _move(self, unit, new_echelon, hq, reason, moved):
        old = getattr(unit, "echelon", None)

        # Prevent upward collapse
        if unit.parent and unit.parent.level <= hq.level:
            return

        # Apply echelon change
        unit.echelon = new_echelon
        unit.parent = hq
        unit.reattached_to = hq

        # NEW: inherit HQ goal after reattachment
        unit.goal_region = getattr(hq, "goal_region", None)

        # NEW: inherit HQ region
        unit.region = getattr(hq, "region", unit.region)

        moved.append((unit.name, old, new_echelon, reason))

    def _integrate_new_units(self, corps_hq, air_hq, naval_hq, moved):
        """
        Type-aware integration:
        - Land combat → Division under Corps
        - Support → Brigade under Corps
        - Air → Squadron under Air HQ
        - Naval → Flotilla under Naval HQ
        - Existing valid echelons are left untouched.
        """
        w = self.world

        for u in w.units:
            echelon = getattr(u, "echelon", None)
            if echelon in self.valid_echelons:
                continue

            utype = getattr(u, "type", None)

            if utype in ("INF", "MOT", "MECH", "ARM", "PANZER"):
                self._move(u, "Division", corps_hq, "NEW LAND UNIT", moved)

            elif utype in ("SUPPORT", "RECON", "ARTY", "ENG"):
                self._move(u, "Brigade", corps_hq, "NEW SUPPORT UNIT", moved)

            elif utype in ("AIR", "FTR", "INTERCEPT", "CAS", "BOMBER"):
                self._move(u, "Squadron", air_hq, "NEW AIR UNIT", moved)

            elif utype in ("NAVAL", "DESTROYER", "SUB", "CRUISER"):
                self._move(u, "Flotilla", naval_hq, "NEW NAVAL UNIT", moved)

    def _theater_shortage(self, theater):
        if not theater:
            return
        armies = sum(1 for u in self.world.units if getattr(u, "echelon", None) == "Army")
        hinge = getattr(theater, "hinge", "Commit_Main_Effort")
        required = 2 if hinge == "Commit_Main_Effort" else 1
        if armies < required:
            print(f"[THEATER SHORTAGE] {theater.id} requires {required} armies but has {armies}.")

    def _army_shortage(self, army):
        if not army:
            return
        corps = sum(1 for u in self.world.units if getattr(u, "echelon", None) == "Corps")
        divs = sum(1 for u in self.world.units if getattr(u, "echelon", None) == "Division")
        if corps < 1:
            print(f"[ARMY SHORTAGE] {army.id} requires 1 corps but has {corps}.")
        if divs < 3:
            print(f"[ARMY SHORTAGE] {army.id} requires 3 divisions but has {divs}.")
