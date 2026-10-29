# hq.py
# Defines the HQ object with all fields required by CLIS, init_world, and AlwaysThinkingHQ

class HQ:
    def __init__(self, id, pos, level):
        self.id = id
        self.pos = pos              # (lat, lon)
        self.level = level          # 0=Theater, 1=AG, 2=Army, 3=Corps

        # Structural hierarchy
        self.parent = None
        self.units = []

        # Region + movement
        self.region = None
        self.goal_region = None
        self.future_goal_region = None
        self.long_range_goal_region = None

        # Corridor / vision chain
        self.vision_chain = []
        self.corridor_adj = []
        self.corridor_depth = None

        # Assignment + nation
        self.assigned = True        # HQ is active by default
        self.nation = None          # Set in init_world or AlwaysThinkingHQ

        # Pressure fields (air, bombing, etc.)
        self.pressure = "YELLOW"
        self.pressure_value = 0.0

        # Distance to goal (computed in Stage 1)
        self.distance_to_goal = 9999

    def add_unit(self, unit):
        self.units.append(unit)
        unit.reattached_to = self
        unit.assigned = True
        if self.nation:
            unit.nation = self.nation
