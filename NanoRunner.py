cat NanoRunner.py
# NanoRunner.py
# Main runner for the modular NanoRunner ecosystem

from init_world import init_world
from air import AirPowerNano
from callup_flexible import CallUpFlexible
from MobilizationOrgan import MobilizationOrgan
from aviation_mobilization import AviationMobilizationOrgan
from air_superiority_pressure import AirSuperiorityPressure
from bombing_pressure import BombingPressure

from movement import move_hqs, move_units, update_hq_distances
from friction import compute_edge_feedback, update_friction
from environment import update_supply, update_leadership, update_terrain, maybe_crash

from messages import (
    hq_status_messages,
    unit_status_messages,
    air_pressure_messages,
    callup_senddown_messages,
    unit_reattach_messages,
)

from DynamicHingeNano import DynamicHingeNano
from geo_hinge_graph import build_hinge_graph
from AlwaysThinkingHQ import always_thinking
from combat import update_combat

import math

# ------------------------------------------------------------
# REAL DISTANCE FUNCTION (Region-aware)
# ------------------------------------------------------------
def compute_distance(a, b):
    ax, ay = a
    bx, by = b.pos
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

# ------------------------------------------------------------
# DOWNSTREAM EFFECTS
# ------------------------------------------------------------
def send_downstream(world):
    effects = []
    for u in world.units:
        echelon = getattr(u, "echelon", None)
        if echelon == "Army":
            effects.append(3.0)
        elif echelon == "Corps":
            effects.append(2.0)
        else:
            effects.append(1.0)
    return effects

# ------------------------------------------------------------
# RUN SIMULATION
# ------------------------------------------------------------
def run_simulation(ticks=20):

    # WORLD INIT
    world = init_world()

    # BUILD HINGE GRAPH
    world.hinge_graph = build_hinge_graph()

    # FIRST: THINK — build full HQ hierarchy + unit propagation
    ctx = always_thinking(world)

    # CREATE HINGE ENGINE
    hinge_engine = DynamicHingeNano(world)

    # AIR SYSTEMS
    air = AirPowerNano(world)
    air_superiority = AirSuperiorityPressure(world)
    bombing_pressure = BombingPressure(world)
    aviation_mob = AviationMobilizationOrgan(world)

    # GROUND SYSTEMS
    callup = CallUpFlexible(world)
    mobilization = MobilizationOrgan(world, ctx)

    # Initial region assignment + distance update
    update_hq_distances(world)

    # MAIN LOOP
    for _ in range(ticks):

        # CALL-UP ORGAN
        moved = callup.run()
        callup_senddown_messages(world)

        # MOBILIZATION ORGAN
        mobilization.run()

        # AIR PRESSURES
        sup_state, sup_value = air_superiority.compute()
        bomb_state, bomb_value = bombing_pressure.compute()

        world.air_superiority_state = sup_state
        world.bombing_state = bomb_state
        world.bombing_pressure = bomb_value

        air_pressure_messages(world)

        # AVIATION MOBILIZATION
        air_events = aviation_mob.tick()

        # FULL HQ BRAIN — must run BEFORE printing statuses
        ctx = always_thinking(world)

        # UPDATE HQ GOALS VIA ADJACENCY
        for hq in world.hqs:
            goal_region = getattr(hq, "goal_region", None)
            if goal_region is not None:
                hq.distance_to_goal = compute_distance(hq.pos, goal_region)
            else:
                region = getattr(hq, "region", None)
                if region:
                    hq.distance_to_goal = compute_distance(hq.pos, region)

        # DOWNSTREAM EFFECTS
        effects = send_downstream(world)

        # EDGE FEEDBACK + ENVIRONMENT
        compute_edge_feedback(world, effects)
        update_supply(world)
        update_leadership(world)
        update_terrain(world)

        # AIR + FRICTION + CRASH
        air.update_air()
        update_friction(world)
        maybe_crash(world)

        # MOVEMENT (hinge-aware)
        move_hqs(world)
        move_units(world)
        update_hq_distances(world)

        # COMBAT ENGINE
        update_combat(world)

        # DIAGNOSTICS + NARRATIVE
        hq_status_messages(world)
        unit_status_messages(world)
        unit_reattach_messages(world)

        world.time += 1

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    run_simulation()
~ $
