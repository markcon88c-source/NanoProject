# HQCreationNano.py
# Creates new HQs when load or pressure conditions demand it.

from HQTypesAndDivisions import (
    create_corps_hq,
    create_army_hq,
    create_army_group_hq
)

class HQCreationNano:

    def update(self, world):

        for hq in list(world.hqs):

            # Corps overloaded → create new Corps
            if hq.level == 2 and len(hq.units) > 10:
                new = create_corps_hq(f"CORPS_NEW_{world.time}", hq)
                new.pressure = "NEW_HQ"        # ⭐ REQUIRED FIX
                world.hqs.append(new)

                # Move half the units
                half = len(hq.units) // 2
                for u in hq.units[:half]:
                    hq.units.remove(u)
                    new.add_unit(u)

                print(f"[HQ-CREATE] Created {new.id} under {hq.id}")

            # Army overloaded → create new Army
            if hq.level == 1 and len(hq.units) > 20:
                new = create_army_hq(f"ARMY_NEW_{world.time}", hq)
                new.pressure = "NEW_HQ"        # ⭐ REQUIRED FIX
                world.hqs.append(new)

                print(f"[HQ-CREATE] Created {new.id} under {hq.id}")

            # Army Group overloaded → create new AG
            if hq.level == 0 and len(hq.units) > 30:
                new = create_army_group_hq(f"AG_NEW_{world.time}", hq)
                new.pressure = "NEW_HQ"        # ⭐ REQUIRED FIX
                world.hqs.append(new)

                print(f"[HQ-CREATE] Created {new.id} under {hq.id}")
