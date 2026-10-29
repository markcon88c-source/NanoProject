# init_world.py

from world_state import WorldState, HQ, Unit, Front
from creation import (
    create_theater_hq,
    create_army_group_hq,
    create_army_hq,
    create_corps_hq,
    create_inf_div,
    create_mot_div,
    create_mech_div,
    create_arm_div,
    create_panzer_div,
    create_support_brigade,
    create_recon_brigade,
    create_artillery_brigade,
    create_engineer_brigade,
)

from geo_hinge_graph import build_hinge_graph, bfs_path


# ------------------------------------------------------------
# HQ DEFAULT INITIALIZATION
# ------------------------------------------------------------

def initialize_hq_defaults(hq):
    """
    Ensures every HQ has the fields AlwaysThinkingHQ expects.
    Prevents crashes when dynamic theaters spawn.
    Also ensures assignment is never None at creation.
    """
    hq.pressure = "YELLOW"
    hq.pressure_value = 0.0

    hq.goal_region = None
    hq.future_goal_region = None
    hq.long_range_goal_region = None

    hq.vision_chain = []
    hq.distance_to_goal = 9999

    # NEW: assignment + structural defaults
    hq.assigned = True          # HQ exists and is active
    if not hasattr(hq, "nation"):
        hq.nation = None
    if not hasattr(hq, "parent"):
        hq.parent = None
    if not hasattr(hq, "units"):
        hq.units = []


# ------------------------------------------------------------
# INIT WORLD
# ------------------------------------------------------------

def init_world():
    world = WorldState()

    # Build hinge graph
    world.hinge_graph = build_hinge_graph()
    world.regions = world.hinge_graph

    # --------------------------------------------------------
    # HQ hierarchy
    # --------------------------------------------------------

    # Base Western theater chain (Paris-centric)
    theater = create_theater_hq("THEATER_WEST", (48.85, 2.35))
    initialize_hq_defaults(theater)
    theater.nation = "FRANCE"
    theater.region = world.hinge_graph["PARIS"]

    ag = create_army_group_hq("AG_NORTH", (50.63, 3.06), theater)
    initialize_hq_defaults(ag)
    ag.nation = "FRANCE"
    ag.parent = theater
    ag.region = theater.region

    army = create_army_hq("ARMY_1", (49.0, 3.0), ag)
    initialize_hq_defaults(army)
    army.nation = "FRANCE"
    army.parent = ag
    army.region = theater.region

    corps = create_corps_hq("CORPS_A", (49.5, 2.5), army)
    initialize_hq_defaults(corps)
    corps.nation = "FRANCE"
    corps.parent = army
    corps.region = theater.region

    world.hqs.extend([theater, ag, army, corps])

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    units = [
        create_inf_div("1ID", "1st Infantry", (49.2, 2.8)),
        create_inf_div("2ID", "2nd Infantry", (49.3, 2.9)),
        create_inf_div("3ID", "3rd Infantry", (49.4, 3.0)),
        create_mot_div("5MD", "5th Motorized", (49.6, 3.1)),
        create_mech_div("7MECH", "7th Mechanized", (49.7, 3.2)),
        create_arm_div("8AD", "8th Armored", (49.8, 3.3)),
        create_panzer_div("9PD", "9th Panzer", (49.9, 3.4)),
        create_support_brigade("10SUP", "10th Support", (49.2, 3.5)),
        create_recon_brigade("11REC", "11th Recon", (49.3, 3.6)),
        create_artillery_brigade("12ART", "12th Artillery", (49.4, 3.7)),
        create_engineer_brigade("13ENG", "13th Engineers", (49.5, 3.8)),
    ]

    for u in units:
        # Attach to CORPS_A structurally
        corps.add_unit(u)

        # NEW: assignment + parent linkage
        u.assigned = True
        u.reattached_to = corps
        if not hasattr(u, "nation"):
            u.nation = corps.nation

    world.units.extend(units)

    # --------------------------------------------------------
    # Region assignment
    # --------------------------------------------------------

    world.assign_regions()

    # --------------------------------------------------------
    # HQ goals (ALL FROM GEO LIST)
    # --------------------------------------------------------

    # Theater strategic chain
    theater.goal_region = world.hinge_graph["PARIS"]
    theater.future_goal_region = world.hinge_graph["LONDON"]
    theater.long_range_goal_region = world.hinge_graph["AMERICA"]

    # Army Group strategic chain
    ag.goal_region = world.hinge_graph["LILLE"]
    ag.future_goal_region = world.hinge_graph["HAMBURG"]
    ag.long_range_goal_region = world.hinge_graph["MOSCOW"]

    # Army strategic chain
    army.goal_region = world.hinge_graph["AMIENS"]
    army.future_goal_region = world.hinge_graph["GHENT"]
    army.long_range_goal_region = world.hinge_graph["BERLIN"]

    # Corps strategic chain
    corps.goal_region = world.hinge_graph["COMPIEGNE"]
    corps.future_goal_region = world.hinge_graph["REIMS"]
    corps.long_range_goal_region = world.hinge_graph["METZ"]

    # Movement organ global goals
    world.theater_goal = theater.goal_region
    world.army_group_goal = ag.goal_region
    world.army_goal = army.goal_region
    world.corps_goal = corps.goal_region

    # --------------------------------------------------------
    # Front creation (hinge-graph BFS)
    # --------------------------------------------------------

    start = corps.region
    goal = corps.goal_region
    path = bfs_path(start, goal)

    front_line = [(r.pos[0], r.pos[1]) for r in path]
    world.fronts.append(Front("FRANCE_FRONT", front_line, corps))

    return world
