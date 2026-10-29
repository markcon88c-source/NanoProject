# nano_diag.py
# Diagnostic organ to show hinge, pressure, HQ load, and unit states each tick.

def diag_tick(world):
    print("--------------------------------------------------")
    print(f"[TICK] {world.time}")

    # Front pressures
    for front in world.fronts:
        print(f"[FRONT] {front.id} pressure={front.pressure}")

    # HQ loads + hinge
    for hq in world.hqs:
        hinge = getattr(hq, "hinge", None)
        print(f"[HQ] {hq.id} lvl={hq.level} load={len(hq.units)} hinge={hinge}")

    # Units + echelons
    for u in world.units:
        try:
            print(f"[UNIT] {u.name} type={u.role if hasattr(u,'role') else 'UNK'} "
                  f"hq={u.hq.id if u.hq else 'NONE'} echelon={getattr(u,'echelon','NONE')}")
        except Exception as e:
            print(f"[UNIT] ERROR reading unit: {e}")

    print("--------------------------------------------------")
