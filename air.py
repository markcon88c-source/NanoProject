# air.py
# AirPowerNano: air sortie intensity and HQ air-state updates.

class AirPowerNano:
    """
    Airpower organ for the NanoRunner ecosystem.
    Sortie intensity increases with friction:
        friction low  → light sorties
        friction high → heavy sorties
    Each HQ receives an air-state string like: SORTIES_0.63
    """

    def __init__(self, world):
        self.world = world
        self.sortie_intensity = 0.5  # baseline

    def update_air(self):
        """
        Update sortie intensity based on world friction.
        Friction ∈ [0,1] → sortie_intensity ∈ [0.3,1.0]
        """
        F = self.world.friction

        # Linear scaling: 0.3 + 0.7*F
        self.sortie_intensity = max(0.0, min(1.0, 0.3 + 0.7 * F))

        # Assign air-state to each HQ
        for hq in self.world.hqs:
            hq.air = f"SORTIES_{self.sortie_intensity:.2f}"
