# world_state.py
# Core world container for HQs, Units, Regions, Fronts, and messaging

from HQ import HQ
from Unit import Unit

class WorldState:
    def __init__(self):
        # Stage 13 neural heart requirement
        self.avg_hq_distance = 0.0

        # Command hierarchy
        self.hqs = []          # all HQs in the world
        self.units = []        # all units in the world

        # Front system
        self.fronts = []

        # Messaging
        self.messages = []

        # Hinge-graph world model
        self.hinge_graph = {}      # loaded externally
        self.region_pulse = {}     # pulse map
        self.global_pulse = 0.0
        self.friction = 0.0

        # Edge feedback
        self.edge_feedback = 0.0

        # Simulation time
        self.time = 0.0

        # Supply system
        self.supply_level = 0.0
        self.max_supply = 100.0

        # Leadership system
        self.leadership_level = 0.0
        self.max_leadership = 100.0

        # Terrain system
        self.terrain_level = 0.0
        self.max_terrain = 100.0

        # Dispersion / reorganization
        self.dispersion = 0.0
        self.prev_dispersion = 0.0

        # Crash simulation
        self.crash_ticks = 0

        # Combat engine integration
        self.bombing_pressure = 0.0
        self.battles = []

    # ============================================================
    # MESSAGE SYSTEM
    # ============================================================
    def send_message(self, src, to, msg, kind="info"):
        self.messages.append({
            "src": src,
            "to": to,
            "msg": msg,
            "kind": kind
        })

    # ============================================================
    # UNIVERSAL HQ CREATION ORGAN
    # ============================================================
    def create_hq(self, level, pos=None, parent=None, region=None, nation=None):
        """
        Creates an HQ of any level (0=Theater, 1=AG, 2=Army, 3=Corps).
        """
        hq_id = f"HQ_{level}_{len(self.hqs)+1}"
        hq = HQ(hq_id, pos, level)

        hq.parent = parent
        hq.region = region
        hq.nation = nation
        hq.assigned = True

        self.hqs.append(hq)

        self.send_message(
            src="SYSTEM",
            to=hq.id,
            msg=f"{hq.id} created at level {level}.",
            kind="hq-create"
        )

        return hq

    # ============================================================
    # MODERN UNIT CREATION ORGAN (FIXED)
    # ============================================================
    def spawn_unit(self, name, pos, utype, parent_hq):
        """
        Modern unit creation API.
        Creates a unit and attaches it to an HQ.
        Updated to match Unit(id, name, pos, utype).
        """

        unit_id = name  # ID = name for spawned units

        # Create unit with new signature
        u = Unit(unit_id, name, pos, utype)

        # Attach to HQ
        u.reattached_to = parent_hq
        u.parent = parent_hq          # ⭐ REQUIRED FIX
        u.assigned = True
        u.nation = getattr(parent_hq, "nation", None)

        # Region inheritance
        if parent_hq and parent_hq.region:
            u.region = parent_hq.region
            u.pos = parent_hq.region.pos

        # Goal inheritance
        u.goal_region = getattr(parent_hq, "goal_region", None)

        # Add to HQ + world
        parent_hq.units.append(u)
        self.units.append(u)

        # message
        self.send_message(
            src=parent_hq.id,
            to=name,
            msg=f"{name} mobilizes under {parent_hq.id}.",
            kind="unit-create"
        )

        return u

    # ============================================================
    # LEGACY UNIT CREATION ORGAN (FIXED)
    # ============================================================
    def create_unit(self, name, utype, echelon, pos, parent_hq=None):
        """
        Legacy API used by MobilizationOrgan:
            create_unit(name, utype, echelon, pos)
        Updated to match Unit(id, name, pos, utype).
        """

        unit_id = name

        u = Unit(unit_id, name, pos, utype)
        u.echelon = echelon
        u.assigned = True

        # Attach to HQ if provided
        if parent_hq is not None:
            u.reattached_to = parent_hq
            u.parent = parent_hq
            parent_hq.units.append(u)

            if parent_hq.region:
                u.region = parent_hq.region
                u.pos = parent_hq.region.pos

            u.nation = getattr(parent_hq, "nation", None)

        # Add to world
        self.units.append(u)

        # Optional message
        self.send_message(
            src=parent_hq.id if parent_hq else "SYSTEM",
            to=name,
            msg=f"{name} created as {echelon} ({utype}).",
            kind="unit-create-legacy"
        )

        return u

    # ============================================================
    # REGION ASSIGNMENT ORGAN
    # ============================================================
    def assign_regions(self):
        """
        Assign each HQ and Unit to the nearest hinge-graph region.
        Required for movement, fronts, pulse, and init_world.py.
        """
        if not self.hinge_graph:
            return

        regions = list(self.hinge_graph.values())

        def nearest_region(pos):
            best = None
            best_d = 999999
            for r in regions:
                dx = r.pos[0] - pos[0]
                dy = r.pos[1] - pos[1]
                d = dx*dx + dy*dy
                if d < best_d:
                    best_d = d
                    best = r
            return best

        # Assign HQs
        for hq in self.hqs:
            if hq.pos:
                hq.region = nearest_region(hq.pos)

        # Assign Units
        for u in self.units:
            if u.pos:
                u.region = nearest_region(u.pos)

    # ============================================================
    # Legacy nearest-region helper
    # ============================================================
    def _nearest(self, pos):
        if not self.hinge_graph or pos is None:
            return None

        regions = list(self.hinge_graph.values())
        best = None
        best_d = 999999

        for r in regions:
            dx = r.pos[0] - pos[0]
            dy = r.pos[1] - pos[1]
            d = dx*dx + dy*dy
            if d < best_d:
                best_d = d
                best = r

        return best

    # ============================================================
    # NATION-AWARE NAME GENERATOR
    # ============================================================
    def generate_unit_name(self, nation, role):
        count = len(self.units) + 1

        if nation == "FRANCE":
            return f"{role} Regiment {count}"
        if nation == "GERMANY":
            return f"{count}th {role} Division"
        if nation == "UK":
            return f"{role} Brigade {count}"
        if nation == "USSR":
            return f"{role} Rifle Division {count}"
        if nation == "USA":
            return f"{role} Battalion {count}"

        return f"{role}_{count}"


# ============================================================
# FRONT OBJECT
# ============================================================
class Front:
    def __init__(self, name, regions=None, corps=None):
        self.name = name
        self.regions = regions or []
        self.corps = corps or []

    def add_region(self, region):
        self.regions.append(region)

    def add_corps(self, corps_hq):
        self.corps.append(corps_hq)
