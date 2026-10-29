# nano_callup.py
# Call-up and send-down organ for emergent HQ reorganization.

class CallUpOrganNano:

    def __init__(self):
        pass

    # ------------------------------------------------------------
    # CALL-UP / SEND-DOWN LOGIC
    # ------------------------------------------------------------
    def call_up(self, units, hinge, feedback=0):
        """
        units: list of unit objects
        hinge: HQ hinge (Commit_Main_Effort, Delay_Action, etc.)
        feedback: edge feedback score from world.edge_feedback

        Returns list of (unit_name, old_echelon, new_echelon, reason)
        """

        moved = []

        # ------------------------------------------------------------
        # FEEDBACK THRESHOLDS
        # ------------------------------------------------------------
        high_feedback = feedback > 20      # strong momentum
        low_feedback  = feedback < -10     # collapse / stagnation

        # ------------------------------------------------------------
        # HINGE-BASED CALL-UP PRIORITY
        # ------------------------------------------------------------
        hinge_aggressive = hinge in [
            "Commit_Main_Effort",
            "Shift_Air_Sorties"
        ]

        hinge_defensive = hinge in [
            "Delay_Action",
            "Stabilize_Command"
        ]

        hinge_probe = hinge == "Probe_Enemy_Lines"

        # ------------------------------------------------------------
        # PROCESS EACH UNIT
        # ------------------------------------------------------------
        for u in units:

            old = u.echelon

            # ========================================================
            # CALL-UP LOGIC (UPWARD MOVEMENT)
            # ========================================================
            if hinge_aggressive or high_feedback:

                # Armor → Corps
                if u.utype == "ARM" and u.echelon == "Division":
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "CALL-UP (ARM, AGGRESSIVE/FEEDBACK)"))
                    continue

                # Motorized → Corps
                if u.utype == "MOT" and u.echelon == "Division":
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "CALL-UP (MOT, AGGRESSIVE/FEEDBACK)"))
                    continue

                # Infantry → Corps (only if feedback very high)
                if u.utype == "INF" and u.echelon == "Division" and feedback > 40:
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "CALL-UP (INF, HIGH FEEDBACK)"))
                    continue

            # ========================================================
            # PROBE LOGIC (LIGHT CALL-UP)
            # ========================================================
            if hinge_probe:

                # Only move recon-capable units upward
                if u.utype in ["MOT", "ARM"] and u.echelon == "Division":
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "CALL-UP (PROBE)"))
                    continue

            # ========================================================
            # SEND-DOWN LOGIC (DOWNWARD MOVEMENT)
            # ========================================================
            if hinge_defensive or low_feedback:

                # Corps → Division
                if u.echelon == "Corps":
                    u.echelon = "Division"
                    moved.append((u.name, old, u.echelon,
                        "SEND-DOWN (DEFENSIVE/FEEDBACK)"))
                    continue

                # Army → Corps (collapse)
                if u.echelon == "Army" and low_feedback:
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "SEND-DOWN (COLLAPSE)"))
                    continue

            # ========================================================
            # STABILIZE COMMAND (HINGE)
            # ========================================================
            if hinge == "Stabilize_Command":

                # Everything collapses downward one level
                if u.echelon == "Army":
                    u.echelon = "Corps"
                    moved.append((u.name, old, u.echelon,
                        "SEND-DOWN (STABILIZE)"))
                    continue

                if u.echelon == "Corps":
                    u.echelon = "Division"
                    moved.append((u.name, old, u.echelon,
                        "SEND-DOWN (STABILIZE)"))
                    continue

        return moved
