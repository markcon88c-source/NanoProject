# HQ.py
# Universal HQ object for Theater, Army Group, Army, Corps
# Fully compatible with AlwaysThinkingHQ, MobilizationOrgan,
# MovementOrgan, CLIS diagnostics, hinge‑graph world models,
# and the combat engine.

class HQ:
    def __init__(self, id, pos=None, level=0):
        """
        HQ levels:
            0 = Theater
            1 = Army Group
            2 = Army
            3 = Corps
        """

        # Identity
        self.id = id
        self.pos = pos
        self.level = level

        # Command hierarchy
        self.units = []          # units directly under this HQ
        self.children = []       # subordinate HQs
        self.parent = None       # parent HQ

        # Region + hinge-graph integration
        self.region = None
        self.goal_region = None
        self.future_goal_region = None
        self.long_range_goal_region = None
        self.vision_chain = []

        # Nation (France, Germany, UK, USSR, USA)
        self.nation = None

        # Air wing creation counter (used by air mobilization)
        self.air_wing_counter = 0

        # Air activity (used by messages/diagnostics)
        self.air_sorties = 0

        # Doctrine + drive (AlwaysThinkingHQ)
        self.drive = None
        self.doctrine = None

        # Pressure / feedback (callup_flexible + friction)
        self.hinge = None
        self.pressure = "GREEN"      # combat engine uses this
        self.edge_feedback = 0.0

        # Required by friction.py
        self.distance_to_goal = 0.0

        # ------------------------------------------------------------
        # Combat engine integration
        # ------------------------------------------------------------

        # Officer model (affects ORG recovery + reinforcement)
        self.officer_skill = 0.5
        self.officer_recovery = 0.5
        self.officer_aggression = 0.5

        # Movement + hinge-graph combat integration
        self.path = []               # planned movement path
        self.next_region = None      # next hinge-graph region

        # MobilizationOrgan compatibility
        self.reattached_to = None

    # ------------------------------------------------------------
    # HQ hierarchy helpers
    # ------------------------------------------------------------
    def add_child(self, child_hq):
        """Attach a subordinate HQ."""
        child_hq.parent = self
        self.children.append(child_hq)

    def add_unit(self, unit):
        """Attach a unit to this HQ."""
        self.units.append(unit)
        unit.parent = self
        if self.region:
            unit.region = self.region

    # ------------------------------------------------------------
    # Movement helpers
    # ------------------------------------------------------------
    def set_position(self, pos):
        self.pos = pos

    def set_region(self, region):
        self.region = region

    # ------------------------------------------------------------
    # Goal + friction helpers
    # ------------------------------------------------------------
    def set_goal_region(self, region):
        self.goal_region = region

    def compute_distance_to_goal(self):
        """
        Computes distance to goal region for friction/edge feedback.
        Safe even if region or goal is missing.
        """
        if not self.pos or not self.goal_region or not self.goal_region.pos:
            self.distance_to_goal = 0.0
            return self.distance_to_goal

        dx = self.goal_region.pos[0] - self.pos[0]
        dy = self.goal_region.pos[1] - self.pos[1]
        self.distance_to_goal = (dx*dx + dy*dy) ** 0.5
        return self.distance_to_goal

    # ------------------------------------------------------------
    # Pressure helper (combat engine)
    # ------------------------------------------------------------
    def set_pressure(self, state):
        """
        Valid states: GREEN, YELLOW, RED
        """
        if state in ("GREEN", "YELLOW", "RED"):
            self.pressure = state
