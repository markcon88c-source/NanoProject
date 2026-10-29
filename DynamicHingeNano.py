# DynamicHingeNano.py
# Adjacency-aware hinge engine for NanoRunner
# Uses full geo hinge graph to choose next operational region.

from geo_hinge_graph import build_hinge_graph

class DynamicHingeNano:

    def __init__(self, world):
        """
        Hinge engine now receives the world so it can access:
        - world.hinge_graph (full region graph)
        - world._nearest() (region lookup)
        """
        self.world = world

        # Build hinge graph once
        if not hasattr(world, "hinge_graph"):
            world.hinge_graph = build_hinge_graph()

    def generate(self, hq):
        """
        Generate hinge decision AND adjacency-based next-region movement.
        """

        # ------------------------------------------------------------
        # PRESSURE → hinge mood (HOI3-style)
        # ------------------------------------------------------------
        pressure = getattr(hq, "pressure", "GREEN")

        if pressure == "GREEN":
            hinge_mood = "Commit_Main_Effort" if hq.level < 3 else "Probe_Enemy_Lines"

        elif pressure == "YELLOW":
            hinge_mood = "Secure_Supply_Lines" if hq.level < 3 else "Stabilize_Command"

        elif pressure == "RED":
            hinge_mood = "Delay_Action"

        elif pressure == "NEW_HQ":
            hinge_mood = "Stabilize_Command"

        else:
            hinge_mood = "Probe_Enemy_Lines"

        # Store hinge mood
        hq.hinge = hinge_mood

        # ------------------------------------------------------------
        # ADJACENCY-AWARE REGION SELECTION
        # ------------------------------------------------------------
        # Determine current region
        region = getattr(hq, "region", None)
        if region is None:
            # fallback: nearest region
            region = self.world._nearest(hq.pos)
            hq.region = region

        # If region has adjacency, choose next region
        if region.adjacent:
            import random
            next_name = random.choice(region.adjacent)
            next_region = self.world.hinge_graph[next_name]

            # Assign adjacency goal
            hq.goal_region = next_region
            return next_region

        # ------------------------------------------------------------
        # FALLBACK: no adjacency → stay in current region
        # ------------------------------------------------------------
        hq.goal_region = region
        return region
