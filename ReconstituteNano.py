# ReconstituteNano.py
# Rebuild units after collapse

class ReconstituteNano:
    def update(self, world):
        for hq in world.hqs:
            # Only rebuild when pressure is GREEN
            if getattr(hq, "pressure", None) != "GREEN":
                continue

            for u in hq.units:
                # If unit collapsed to Theater, rebuild it
                if u.echelon == "Theater":
                    old = u.echelon
                    u.echelon = "Division"

                    # Log rebuild
                    if not hasattr(world, "callup_log"):
                        world.callup_log = []
                    world.callup_log.append(
                        (u.name, old, u.echelon, "RECONSTITUTE")
                    )
