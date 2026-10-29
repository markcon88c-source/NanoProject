# AirPowerNano.py

class AirPowerNano:
    """
    Tiny air‑power brain:
    - tags HQs with an 'air' status (GREEN/YELLOW/RED)
    - can later be extended to spawn air units, sorties, etc.
    """

    def __init__(self, world):
        self.world = world

    def _evaluate_corps_air(self, hq):
        """
        Simple heuristic:
        - if hinge is very offensive → air GREEN
        - if hinge is logistical / stabilizing → air YELLOW
        - if hinge is delay / under pressure → air RED
        """
        hinge = getattr(hq, "hinge", None)

        if hinge in ("Commit_Main_Effort", "Probe_Enemy_Lines"):
            return "GREEN"
        elif hinge in ("Secure_Supply_Lines", "Stabilize_Command", "Shift_Air_Sorties"):
            return "YELLOW"
        elif hinge in ("Delay_Action",):
            return "RED"
        else:
            return None

    def update_air(self, world):
        """
        Called each tick from NanoRunner:
        - sets hq.air
        - can later drive actual air units / missions
        """
        # front‑level air (placeholder)
        if hasattr(world, "front"):
            # you can make this depend on enemy strength, weather, etc.
            world.front.air = "GREEN"

        for hq in world.hqs:
            if hq.level == 3:  # Corps HQs are the air mission controllers
                hq.air = self._evaluate_corps_air(hq)
            else:
                # non‑corps HQs may have no direct air control
                hq.air = getattr(hq, "air", None)
