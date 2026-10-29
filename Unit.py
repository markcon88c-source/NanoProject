# unit.py
# Defines the Unit object with all fields required by CLIS, init_world, and AlwaysThinkingHQ

class Unit:
    def __init__(self, id, name, pos, utype):
        self.id = id
        self.name = name
        self.pos = pos              # (lat, lon)
        self.type = utype           # INF, MOT, MECH, ARM, AIR, etc.

        # Structural hierarchy
        self.reattached_to = None   # Parent HQ
        self.nation = None          # Set when attached to HQ

        # Assignment flag
        self.assigned = True        # Units start active

        # Region + movement
        self.region = None
        self.goal_region = None

        # Echelon (Division, Brigade, Squadron)
        self.echelon = "Division"

    def attach_to(self, hq):
        self.reattached_to = hq
        self.assigned = True
        if hq.nation:
            self.nation = hq.nation
        hq.units.append(self)
