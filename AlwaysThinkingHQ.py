# AlwaysThinkingHQ.py
# Strategic brain for the organism — with assignment + hierarchy propagation fixed

from geo_hinge_graph import bfs_path, path_distance
from MobilizationOrgan import MobilizationOrgan
from world_state import HQ, Unit

# ============================================================
# SAFE REGION RESOLVER
# ============================================================

def safe_region(world, key):
    """Return a real hinge-graph region or None."""
    return world.hinge_graph.get(key, None)

# ============================================================
# CONTEXT INITIALIZATION
# ============================================================

def init_ctx():
    return {
        "nations_created": set(),
        "hq_data": {},
    }

# ============================================================
# STAGE 0 — CREATE FRANCE
# ============================================================

def stage_0_nano_create_france(world, ctx):
    if "FRANCE" in ctx["nations_created"]:
        return ctx

    paris = safe_region(world, "PARIS")
    reims = safe_region(world, "REIMS")
    metz = safe_region(world, "METZ")

    if not (paris and reims and metz):
        return ctx

    fr = HQ("THEATER_FRANCE", paris.pos, 0)
    fr.region = paris
    fr.goal_region = paris
    fr.future_goal_region = reims
    fr.long_range_goal_region = metz
    fr.nation = "FRANCE"
    fr.units = []
    fr.assigned = True
    world.hqs.append(fr)

    ag_north = HQ("AG_FRANCE_NORTH", fr.pos, 1)
    ag_north.parent = fr
    ag_north.region = fr.region
    ag_north.goal_region = reims
    ag_north.nation = "FRANCE"
    ag_north.units = []
    ag_north.assigned = True
    world.hqs.append(ag_north)

    ag_south = HQ("AG_FRANCE_SOUTH", fr.pos, 1)
    ag_south.parent = fr
    ag_south.region = fr.region
    ag_south.goal_region = reims
    ag_south.nation = "FRANCE"
    ag_south.units = []
    ag_south.assigned = True
    world.hqs.append(ag_south)

    army_1 = HQ("ARMY_FR_1", fr.pos, 2)
    army_1.parent = ag_north
    army_1.region = fr.region
    army_1.goal_region = paris
    army_1.nation = "FRANCE"
    army_1.units = []
    army_1.assigned = True
    world.hqs.append(army_1)

    army_2 = HQ("ARMY_FR_2", fr.pos, 2)
    army_2.parent = ag_south
    army_2.region = fr.region
    army_2.goal_region = paris
    army_2.nation = "FRANCE"
    army_2.units = []
    army_2.assigned = True
    world.hqs.append(army_2)

    corps_a = HQ("CORPS_FR_A", fr.pos, 3)
    corps_a.parent = army_1
    corps_a.region = fr.region
    corps_a.goal_region = paris
    corps_a.nation = "FRANCE"
    corps_a.units = []
    corps_a.assigned = True
    world.hqs.append(corps_a)

    corps_b = HQ("CORPS_FR_B", fr.pos, 3)
    corps_b.parent = army_2
    corps_b.region = fr.region
    corps_b.goal_region = paris
    corps_b.nation = "FRANCE"
    corps_b.units = []
    corps_b.assigned = True
    world.hqs.append(corps_b)

    # Spawn French divisions and air wings
    u1 = world.spawn_unit("FR_1st_Infantry", fr.region.pos, "INF", corps_a)
    u2 = world.spawn_unit("FR_2nd_Infantry", fr.region.pos, "INF", corps_a)
    u3 = world.spawn_unit("FR_3rd_Infantry", fr.region.pos, "INF", corps_b)
    u4 = world.spawn_unit("FR_4th_Armored", fr.region.pos, "ARM", corps_b)
    a1 = world.spawn_unit("FR_1st_AirWing", fr.region.pos, "AIR", fr)
    a2 = world.spawn_unit("FR_2nd_AirWing", fr.region.pos, "AIR", fr)

    for u in [u1, u2, u3, u4, a1, a2]:
        u.assigned = True
        u.reattached_to = u.parent
        u.nation = "FRANCE"

    ctx["nations_created"].add("FRANCE")
    return ctx

# ============================================================
# STAGE 0 — CREATE GERMANY
# ============================================================

def stage_0_nano_create_germany(world, ctx):
    if "GERMANY" in ctx["nations_created"]:
        return ctx

    frankfurt = safe_region(world, "FRANKFURT")
    leipzig = safe_region(world, "LEIPZIG")
    moscow = safe_region(world, "MOSCOW")

    if not (frankfurt and leipzig and moscow):
        return ctx

    de = HQ("THEATER_WEST", frankfurt.pos, 0)
    de.region = frankfurt
    de.goal_region = frankfurt
    de.future_goal_region = leipzig
    de.long_range_goal_region = moscow
    de.nation = "GERMANY"
    de.units = []
    de.assigned = True
    world.hqs.append(de)

    ag_north = HQ("AG_GER_NORTH", de.pos, 1)
    ag_north.parent = de
    ag_north.region = de.region
    ag_north.goal_region = de.goal_region
    ag_north.nation = "GERMANY"
    ag_north.units = []
    ag_north.assigned = True
    world.hqs.append(ag_north)

    army_1 = HQ("ARMY_GER_1", de.pos, 2)
    army_1.parent = ag_north
    army_1.region = de.region
    army_1.goal_region = de.goal_region
    army_1.nation = "GERMANY"
    army_1.units = []
    army_1.assigned = True
    world.hqs.append(army_1)

    corps_a = HQ("CORPS_A", de.pos, 3)
    corps_a.parent = army_1
    corps_a.region = de.region
    corps_a.goal_region = de.goal_region
    corps_a.nation = "GERMANY"
    corps_a.units = []
    corps_a.assigned = True
    world.hqs.append(corps_a)

    g1 = world.spawn_unit("DE_1st_Infantry", de.region.pos, "INF", corps_a)
    g2 = world.spawn_unit("DE_2nd_Infantry", de.region.pos, "INF", corps_a)
    g3 = world.spawn_unit("DE_1st_AirWing", de.region.pos, "AIR", de)

    for u in [g1, g2, g3]:
        u.assigned = True
        u.reattached_to = u.parent
        u.nation = "GERMANY"

    ctx["nations_created"].add("GERMANY")
    return ctx

# ============================================================
# STAGE 1 — SENSE
# ============================================================

def stage_1_sense(world, ctx):
    for hq in world.hqs:
        if hq.goal_region and hq.region:
            d = path_distance(hq.region, hq.goal_region)
            dist = d if d is not None else 9999
        else:
            dist = 9999

        ctx["hq_data"][hq.id] = {
            "distance": dist,
            "vision_chain": getattr(hq, "vision_chain", []),
            "future_goal": getattr(hq, "future_goal_region", None),
        }
    return ctx

# ============================================================
# STAGE 2 — FORECAST
# ============================================================

def stage_2_forecast(world, ctx):
    # 1) Attach adjacency edges from hinge-graph Regions to every HQ
    for hq in world.hqs:
        region = getattr(hq, "region", None)
        if region is None:
            hq.corridor_adj = []
            continue

        hq.corridor_adj = list(getattr(region, "adj", []))

    # 2) Theater-level forecasting
    for hq in world.hqs:
        if hq.level != 0:
            continue

        current = hq.goal_region

        if hq.id == "THEATER_WEST":
            hq.future_goal_region = safe_region(world, "LEIPZIG")
            hq.long_range_goal_region = safe_region(world, "MOSCOW")

        elif hq.id == "THEATER_FRANCE":
            hq.future_goal_region = safe_region(world, "REIMS")
            hq.long_range_goal_region = safe_region(world, "METZ")

        if current and hq.long_range_goal_region:
            hq.vision_chain = bfs_path(current, hq.long_range_goal_region)
        else:
            hq.vision_chain = []

        hq.future_use_flag = True

    return ctx
# ============================================================
# STAGE 3 — AXIS + CHAIN GENERATION FOR ALL HQs
# ============================================================

def stage_3_axis(world, ctx):

    if "hq_data" not in ctx:
        ctx["hq_data"] = {}
    hq_data = ctx["hq_data"]

    for hq in world.hqs:
        region = getattr(hq, "region", None)
        goal   = getattr(hq, "goal_region", None)

        if region is None or goal is None:
            hq.vision_chain = []
            hq.corridor = []
        else:
            if not getattr(hq, "vision_chain", []):
                hq.vision_chain = bfs_path(region, goal)

            hq.corridor = [r.name for r in hq.vision_chain]

        if hq.id not in hq_data:
            hq_data[hq.id] = {}

        hq_data[hq.id]["vision_chain"] = hq.vision_chain
        hq_data[hq.id]["corridor"]     = hq.corridor
        hq_data[hq.id]["distance"]     = len(hq.vision_chain) - 1

    for hq in world.hqs:
        if hq.level != 0:
            continue

        data  = hq_data.get(hq.id, {})
        dist  = data.get("distance", 9999)
        chain = data.get("vision_chain", [])

        if dist < 2 and len(chain) > 1:
            next_step = chain[1]
            if next_step != hq.goal_region:
                hq.goal_region = next_step
                hq.region      = next_step
                hq.pos         = next_step.pos
                hq.assigned    = True

                hq_data[hq.id]["goal_region"] = hq.goal_region
                hq_data[hq.id]["region"]      = hq.region
                hq_data[hq.id]["pos"]         = hq.pos

    return ctx

# ============================================================
# STAGE 3b — AXIS PROPAGATION
# ============================================================

def stage_3b_axis_propagation(world, ctx):
    for hq in world.hqs:
        parent = getattr(hq, "parent", None)
        if not parent:
            continue

        if getattr(parent, "nation", None) != getattr(hq, "nation", None):
            continue

        if not getattr(parent, "goal_region", None):
            continue

        if parent.level >= hq.level:
            continue

        hq.goal_region = parent.goal_region
        hq.region = parent.region
        hq.pos = parent.region.pos
        hq.assigned = True

    return ctx
# ============================================================
# STAGE 3c — HIERARCHICAL AXIS SLICING + ADJACENCY GOALING
# ============================================================
# This stage transforms the theater-level strategic corridor
# (vision_chain) into echelon-specific sub‑chains. Each HQ receives
# a unique goal and a unique corridor slice based on its level:
#
#   Theater (0) → chain[0]      (full chain)
#   Army Group (1) → chain[1:]
#   Army (2) → chain[2:]
#   Corps (3) → chain[3:] or fallback to chain[2:]
#
# If the parent chain is too short, adjacency-based goal assignment
# is used: a child HQ may inherit any region that lies inside the
# parent’s adjacency envelope (corridor_adj). This allows lateral
# maneuvering and prevents chain collapse.
#
# Result:
#   • HQs receive differentiated goals
#   • HQs follow unique axis segments
#   • Units and squadrons inherit unique movement paths
#   • The organism gains true multi‑echelon strategic behavior
#
# This stage must run AFTER Stage 3b and Stage P, and BEFORE Stage 11.
# ============================================================
def stage_3c_hierarchy_chains(world, ctx):
    """
    Slice parent vision_chain by echelon so each HQ gets a unique goal.
    If the chain is too short, allow adjacency-based goal inheritance.
    """

    for hq in world.hqs:
        parent = getattr(hq, "parent", None)
        if not parent:
            continue

        parent_chain = getattr(parent, "vision_chain", [])
        parent_adj   = getattr(parent, "corridor_adj", [])
        lvl = getattr(hq, "level", None)

        # If parent has no chain, skip
        if not parent_chain:
            continue

        # === Determine chain slice by echelon ===
        if lvl == 0:
            # Theater keeps full chain
            sub = parent_chain

        elif lvl == 1:
            # Army Group gets chain[1:]
            sub = parent_chain[1:] if len(parent_chain) > 1 else parent_chain

        elif lvl == 2:
            # Army gets chain[2:]
            if len(parent_chain) > 2:
                sub = parent_chain[2:]
            else:
                sub = parent_chain[1:]

        elif lvl == 3:
            # Corps gets chain[3:] or fallback to chain[2:]
            if len(parent_chain) > 3:
                sub = parent_chain[3:]
            elif len(parent_chain) > 2:
                sub = parent_chain[2:]
            else:
                sub = parent_chain[1:]

        else:
            # Unknown level → inherit parent chain
            sub = parent_chain

        # === Assign chain + corridor ===
        hq.vision_chain = sub
        hq.corridor = [r.name for r in sub]

        # === Primary goal: first region in sub-chain ===
        if sub:
            hq.goal_region = sub[0]
            hq.region = sub[0]
            hq.pos = sub[0].pos
            hq.assigned = True

        # === Secondary goal: adjacency-based goal inheritance ===
        # If the chain slice is too short, allow parent to give a goal
        # from its adjacency envelope.
        if len(sub) < 2 and parent_adj:
            # Pick the adjacency closest to parent's goal
            # (you can tune this selection logic)
            adj_goal = parent_adj[0]
            hq.goal_region = adj_goal
            hq.region = adj_goal
            hq.pos = adj_goal.pos
            hq.assigned = True

        # === Propagate adjacency envelope ===
        hq.corridor_adj = list(parent_adj)

    return ctx
# ============================================================
# STAGE P — PREPARATION CORRIDORS
# ============================================================

def stage_p_preparation_corridors(world, ctx):
    for hq in world.hqs:
        nation = getattr(hq, "nation", None)
        level = getattr(hq, "level", None)
        parent = getattr(hq, "parent", None)

        if nation not in ("GERMANY", "FRANCE"):
            continue
        if level not in (1, 2, 3):
            continue
        if not parent:
            continue

        chain = getattr(parent, "vision_chain", [])
        if chain and len(chain) > 1:
            corridor = chain[1]
        else:
            corridor = getattr(parent, "future_goal_region", None) or \
                       getattr(parent, "long_range_goal_region", None)

        if corridor:
            hq.goal_region = corridor
            hq.region = corridor
            hq.pos = corridor.pos
            hq.assigned = True

    return ctx

# ============================================================
# STAGE 11 — UNIT PROPAGATION
# ============================================================

def stage_11_unit_propagation(world, ctx):

    hq_by_id = {hq.id: hq for hq in world.hqs}

    if "unit_data" not in ctx:
        ctx["unit_data"] = {}
    unit_data = ctx["unit_data"]

    for u in world.units:

        parent = getattr(u, "reattached_to", None)
        if parent is None:
            parent = getattr(u, "parent", None)

        if parent is None:
            continue

        if isinstance(parent, str):
            parent_hq = hq_by_id.get(parent)
        else:
            parent_hq = parent

        if parent_hq is None:
            continue

        u.assigned = True

        u.goal_region        = getattr(parent_hq, "goal_region", None)
        u.future_goal_region = getattr(parent_hq, "future_goal_region", None)
        u.long_range_goal_region = getattr(parent_hq, "long_range_goal_region", None)

        if getattr(parent_hq, "region", None):
            u.region = parent_hq.region
            u.pos    = parent_hq.region.pos

        u.nation = getattr(parent_hq, "nation", None)

        parent_adj = getattr(parent_hq, "corridor_adj", [])
        u.corridor_adj = list(parent_adj)
        u.adjacencies  = [r.name for r in parent_adj]

        parent_chain = getattr(parent_hq, "corridor", [])
        u.corridor = list(parent_chain)

        parent_vchain = getattr(parent_hq, "vision_chain", [])
        u.vision_chain = list(parent_vchain)

        import random
        if parent_adj:
            for _ in range(random.randint(1, 3)):
                branch = random.choice(parent_adj)
                u.vision_chain.append(branch.name)

        data = unit_data.get(u.id, {})
        data["parent_hq"]     = parent_hq.id
        data["goal_region"]   = u.goal_region
        data["region"]        = u.region
        data["pos"]           = u.pos
        data["corridor"]      = u.corridor
        data["adjacencies"]   = u.adjacencies
        data["corridor_adj"]  = u.corridor_adj
        data["vision_chain"]  = u.vision_chain

        unit_data[u.id] = data

    ctx["unit_data"] = unit_data
    return ctx

# ============================================================
# STAGE 12 — UNIT SEMANTIC ASSIGNMENT
# ============================================================

def stage_12_unit_assignment(world, ctx):

    for u in world.units:

        u.thought_flag = "NONE"

        parent = getattr(u, "parent", None)
        if parent is None:
            continue

        chain = getattr(u, "vision_chain", None)
        adj   = getattr(u, "corridor_adj", None)

        if chain and adj:
            lvl = getattr(parent, "level", None)

            if lvl == 3:
                u.thought_flag = f"CORPS_{parent.id}"
            elif lvl == 2:
                u.thought_flag = f"ARMY_{parent.id}"
            elif lvl == 1:
                u.thought_flag = f"AG_{parent.id}"
            elif lvl == 0:
                u.thought_flag = f"THEATER_{parent.id}"
            else:
                u.thought_flag = f"PARENT_{parent.id}"

        elif chain:
            u.thought_flag = f"CHAIN_{parent.id}"

        elif adj:
            u.thought_flag = f"ADJ_{parent.id}"

    return ctx

# ============================================================
# ALWAYS THINKING — MAIN ORCHESTRATOR
# ============================================================

def always_thinking(world):
    ctx = init_ctx()

    ctx = stage_0_nano_create_france(world, ctx)
    ctx = stage_0_nano_create_germany(world, ctx)

    ctx = stage_1_sense(world, ctx)
    ctx = stage_2_forecast(world, ctx)
    ctx = stage_3_axis(world, ctx)
    ctx = stage_3b_axis_propagation(world, ctx)
    ctx = stage_p_preparation_corridors(world, ctx)

    # ⭐ FIX ADDED HERE ⭐
    ctx = stage_11_unit_propagation(world, ctx)
    ctx = stage_12_unit_assignment(world, ctx)
# ============================================================
# DOWNSTREAM STRATEGIC ORGANS
# ============================================================

    ctx = stage_13_thought_goal_adjustment(world, ctx)
    ctx = stage_17_event_neural_shockwave(world, ctx)
    ctx = stage_18_england_special(world, ctx)
    ctx = stage_19_future_goal_selection(world, ctx)
    ctx = stage_20_movement_intent(world, ctx)
    ctx = stage_21_neural_heart(world, ctx)
    mob = MobilizationOrgan(world, ctx)
    mob.run()

    return ctx
# ============================================================
# STAGE 13 — STRATEGIC THOUGHT → GOAL ADJUSTMENT (DOWNSTREAM)
# ============================================================
# This stage is intentionally placed AFTER Stage 12 so that it
# does not interfere with the existing, stable pipeline:
#
#   • Stage 2: Theater forecasting (future + long-range)
#   • Stage 3: Corridor + chain generation
#   • Stage 3b: Axis propagation
#   • Stage P: Preparation corridors
#   • Stage 3c: Hierarchical chain slicing
#   • Stage 11: Full unit propagation
#   • Stage 12: Semantic assignment (CORPS_*, ARMY_*, etc.)
#
# Stage 13 reads the strategic “thought maps” produced by
# france_thought_messages() and germany_thought_messages().
# These maps represent the organism’s offensive/defensive
# interest in every hinge-graph region, weighted by distance.
#
# Instead of replacing or rewriting any upstream logic,
# Stage 13 gently nudges HQ goal_region based on these thoughts.
#
# Rules:
#   • Thoughts must be adjacency-valid (reachable).
#   • Thoughts must not break existing corridor chains.
#   • Thoughts only adjust goals; Stage 3/11/12 handle propagation.
#
# Result:
#   • HQs drift toward interesting loci (offensive or defensive).
#   • Army Groups, Armies, and Corps inherit these nudges naturally.
#   • Units and squadrons move in unique, emergent ways.
#   • No upstream logic is broken; the organism remains stable.
#
# This is the safest way to evolve strategic behavior without
# destabilizing the working architecture.
# ============================================================
def stage_13_thought_goal_adjustment(world, ctx):
    """
    Downstream strategic adjustment.
    Uses thought maps (France/Germany) to gently nudge HQ goals
    WITHOUT breaking the existing chain system.
    """

    for hq in world.hqs:
        nation = getattr(hq, "nation", None)
        region = getattr(hq, "region", None)
        if region is None:
            continue

        # Build thought list for this HQ
        thoughts = []
        for name, r in world.hinge_graph.items():
            d = path_distance(region, r)
            if d is not None:
                thoughts.append((d, r))

        # Sort by distance (closest = defensive, farthest = offensive)
        thoughts.sort(key=lambda x: x[0])

        # Pick a “strategic interest” region
        # Example: pick the 5th closest (tunable)
        if len(thoughts) > 5:
            _, target = thoughts[5]
        else:
            continue

        # Validate adjacency: target must be reachable
        if target not in getattr(hq, "corridor_adj", []):
            continue

        # Nudge HQ goal
        hq.goal_region = target
        hq.region = target
        hq.pos = target.pos

        # Rebuild chain
        hq.vision_chain = bfs_path(target, getattr(hq, "long_range_goal_region", target))
        hq.corridor = [r.name for r in hq.vision_chain]

        hq.assigned = True

    return ctx
def stage_14_future_planning_recorder(world, ctx):
    """
    Records how future planning affected HQ decisions.
    Non-intrusive: does not modify HQs or units.
    """

    log = []

    for hq in world.hqs:
        entry = {}

        entry["id"] = hq.id
        entry["nation"] = getattr(hq, "nation", None)
        entry["level"] = getattr(hq, "level", None)

        # What Stage 2 originally planned
        entry["original_future_goal"] = getattr(hq, "future_goal_region", None)
        entry["original_future_goal_name"] = getattr(hq.future_goal_region, "name", "NONE")

        entry["original_long_range_goal"] = getattr(hq, "long_range_goal_region", None)
        entry["original_long_range_goal_name"] = getattr(hq.long_range_goal_region, "name", "NONE")

        # What Stage 3c sliced for this HQ
        entry["original_chain_slice"] = [
            getattr(r, "name", "NONE") for r in getattr(hq, "vision_chain", [])
        ]

        # What Stage 13 changed (if anything)
        entry["final_goal"] = getattr(hq.goal_region, None)
        entry["final_goal_name"] = getattr(hq.goal_region, "name", "NONE")

        # Detect replacement
        if entry["original_future_goal_name"] != entry["final_goal_name"]:
            entry["decision_changed"] = True
            entry["reason"] = "Thought-driven nudge or adjacency constraint"
        else:
            entry["decision_changed"] = False
            entry["reason"] = "No change"

        log.append(entry)

    ctx["future_planning_decisions"] = log
    return ctx
# ============================================================
# STAGE 17 — EVENT NEURAL SHOCKWAVE (FULL)
# ============================================================

def stage_17_event_neural_shockwave(world, ctx):
    events = getattr(world, "pending_events", [])
    if not events:
        return ctx

    for event in events:
        if event == "REOCCUPY_RHINELAND":
            apply_rhineland_reoccupation(world)

        # Future: add more events here
        # FALL_OF_PARIS
        # BATTLE_OF_CAEN
        # EVACUATION_TO_ENGLAND
        # BARBAROSSA_EARLY
        # etc.

    recompute_after_event(world)
    return ctx


# ------------------------------------------------------------
# APPLY EVENT: REOCCUPATION OF THE RHINELAND
# ------------------------------------------------------------
def apply_rhineland_reoccupation(world):
    corridor_edges = [
        ("METZ", "SAARBRUCKEN"),
        ("SAARBRUCKEN", "KAISERSLAUTERN"),
        ("KAISERSLAUTERN", "MANNHEIM"),
    ]

    for a, b in corridor_edges:
        world.edge_control[(a, b)] = "GERMANY"
        world.edge_control[(b, a)] = "GERMANY"

        world.hinge_graph[a].control = "GERMANY"
        world.hinge_graph[b].control = "GERMANY"

    world.event_log.append("Germany reoccupies the Rhineland.")


# ------------------------------------------------------------
# RECOMPUTE EVERYTHING AFTER EVENT
# ------------------------------------------------------------
def recompute_after_event(world):

    # 1. Recompute corridors
    for hq in world.hqs:
        hq.vision_chain = world.compute_corridor(hq.region, hq.goal_region)
        hq.corridor_adj = hq.region.adj

    # 2. Recompute thought maps
    world.thought_maps = world.compute_thought_maps()

    # 3. Recompute future goals
    for hq in world.hqs:
        future = getattr(hq, "future_goal_region", None)
        if future and not world.is_corridor_valid(hq.region, future):
            hq.future_goal_region = world.pick_next_valid_future_goal(hq)

        long = getattr(hq, "long_range_goal_region", None)
        if long and not world.is_corridor_valid(hq.region, long):
            hq.long_range_goal_region = world.pick_next_valid_long_range_goal(hq)

    # 4. Recompute deltas
    world.delta_maps = world.compute_delta_maps()

    # 5. Recompute movement intent
    world.movement_intent = world.compute_movement_intent()

    # 6. Fire neural-heart impulses
    world.neural_heart_pulse()

    # 7. Update unit movement
    world.update_unit_movement()

    # 8. Update air pressure and bombing targets
    world.update_air_pressure()
    world.update_bombing_targets()

    # 9. Update mobilization
    world.update_mobilization()

    # 10. Log shockwave
    world.event_log.append("Event shockwave propagated.")
# ============================================================
# STAGE 18 — ENGLAND SPECIAL REGION ORGAN (NANO)
# ============================================================

def stage_18_england_special(world, ctx):
    for hq in world.hqs:
        region = getattr(hq, "region", None)
        future = getattr(hq, "future_goal_region", None)
        long = getattr(hq, "long_range_goal_region", None)

        # Special weighting for London
        if future and future.name == "LONDON":
            hq.future_goal_weight = getattr(hq, "future_goal_weight", 1.0) + 5.0

        if long and long.name == "LONDON":
            hq.long_range_goal_weight = getattr(hq, "long_range_goal_weight", 1.0) + 10.0

        # Offshore adjacency weighting
        if region and getattr(region, "offshore", False):
            hq.offshore_weight = getattr(hq, "offshore_weight", 1.0) + 3.0

    return ctx
# ============================================================
# STAGE 19 — FUTURE GOAL SELECTION (NANO)
# ============================================================

def stage_19_future_goal_selection(world, ctx):
    for hq in world.hqs:
        # Collect candidate goals
        candidates = []

        # Current future goal
        fg = getattr(hq, "future_goal_region", None)
        if fg:
            candidates.append(fg)

        # Current long-range goal
        lg = getattr(hq, "long_range_goal_region", None)
        if lg:
            candidates.append(lg)

        # Parent adjacency (fallback)
        adj = getattr(hq, "corridor_adj", [])
        for r in adj:
            candidates.append(r)

        # Weighting
        best = None
        best_score = -9999

        for r in candidates:
            score = 0.0

            # London special weighting
            if r.name == "LONDON":
                score += 10.0

            # Offshore weighting
            if getattr(r, "offshore", False):
                score += 5.0

            # Distance weighting
            dist = path_distance(hq.region, r)
            if dist is not None:
                score -= dist

            if score > best_score:
                best_score = score
                best = r

        if best:
            hq.future_goal_region = best

    return ctx
# ============================================================
# STAGE 20 — MOVEMENT INTENT (FULL)
# ============================================================

def stage_20_movement_intent(world, ctx):
    """
    Compute movement intent for each HQ based on its region and future goal.
    Produces:
        - delta vector
        - urgency
        - pivot (change from previous goal)
        - corridor context
    """

    for hq in world.hqs:
        region = getattr(hq, "region", None)
        future = getattr(hq, "future_goal_region", None)

        if not region or not future:
            continue

        # --- Delta vector ---
        dx = future.pos[0] - region.pos[0]
        dy = future.pos[1] - region.pos[1]
        delta = (dx, dy)

        # --- Urgency (distance-based) ---
        dist = path_distance(region, future)
        if dist is None:
            urgency = 0.0
        else:
            urgency = max(0.01, 1.0 / (dist + 1))

        # --- Pivot (change from previous goal) ---
        prev = getattr(hq, "goal_region", None)
        if prev:
            px = future.pos[0] - prev.pos[0]
            py = future.pos[1] - prev.pos[1]
            pivot = (px, py)
        else:
            pivot = (0.0, 0.0)

        # --- Corridor context ---
        corridor = getattr(hq, "vision_chain", [])

        # --- Store movement intent ---
        hq.movement_intent = {
            "vector": delta,
            "urgency": urgency,
            "pivot": pivot,
            "corridor": corridor
        }

    return ctx
# ============================================================
# STAGE 21 — NEURAL HEART PULSE (FULL)
# ============================================================

def stage_21_neural_heart(world, ctx):
    """
    Neural Heart Pulse:
    Amplifies movement intent based on urgency and corridor pressure.
    Produces:
        - neural_heart_vector
        - neural_heart_urgency
        - neural_heart_impulse (qualitative)
    """

    for hq in world.hqs:
        intent = getattr(hq, "movement_intent", None)
        if not intent:
            continue

        vector = intent.get("vector", (0.0, 0.0))
        urgency = intent.get("urgency", 0.0)
        pivot = intent.get("pivot", (0.0, 0.0))
        corridor = intent.get("corridor", [])

        # --- Amplification factor ---
        amp = 1.0 + urgency

        # --- Amplified delta ---
        nh_vector = (vector[0] * amp, vector[1] * amp)

        # --- Amplified urgency ---
        nh_urgency = urgency * amp

        # --- Impulse classification ---
        if nh_urgency > 0.5:
            impulse = "SURGE"
        elif nh_urgency > 0.2:
            impulse = "PRESSURE"
        elif nh_urgency > 0.05:
            impulse = "TENSION"
        else:
            impulse = "CALM"

        # --- Store neural-heart output ---
        hq.neural_heart_vector = nh_vector
        hq.neural_heart_urgency = nh_urgency
        hq.neural_heart_impulse = impulse

    return ctx
