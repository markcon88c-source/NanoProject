# messages.py
# Logging and status reporting for NanoRunner

from geo_hinge_graph import path_distance

# ============================================================
# HQ STATUS
# ============================================================
def hq_status_messages(world):
    print("[HQ STATUS]")
    for hq in world.hqs:
        lvl = getattr(hq, "level", None)
        pos = getattr(hq, "pos", (0.0, 0.0))
        goal = getattr(hq, "goal_region", None)
        goal_name = goal.name if goal is not None else "NONE"
        print(f"- {hq.id} (level={lvl}) pos={pos} goal={goal_name}")


# ============================================================
# UNIT STATUS (NOW SHOWS ASSIGNMENT FLAG)
# ============================================================
def unit_status_messages(world):
    print("[UNIT STATUS]")
    for u in world.units:
        etype = getattr(u, "type", "UNKNOWN")
        echelon = getattr(u, "echelon", "UNKNOWN")
        pos = getattr(u, "pos", (0.0, 0.0))
        flag = getattr(u, "thought_flag", "NONE")
        print(f"- {u.id} ({etype}) echelon={echelon} pos={pos} assigned={flag}")


# ============================================================
# UNIT REATTACHMENTS (NOW SHOWS ASSIGNMENT FLAG)
# ============================================================
def unit_reattach_messages(world):
    print("[UNIT REATTACHMENTS]")
    for u in world.units:
        parent = getattr(u, "reattached_to", None)
        if parent is not None:
            flag = getattr(u, "thought_flag", "NONE")
            print(f"- {u.id} reattached to {parent.id} (assigned={flag})")


# ============================================================
# FRANCE STRATEGIC THOUGHTS
# ============================================================
def france_thought_messages(world):
    france = next((hq for hq in world.hqs if hq.id == "THEATER_FRANCE"), None)
    if france is None:
        return

    print("[FRANCE THOUGHTS]")
    for name, region in world.hinge_graph.items():
        dist = path_distance(france.region, region)
        if dist is None:
            continue
        print(f"- France considers {name} (distance={dist}) as a possible future locus.")


# ============================================================
# GERMANY STRATEGIC THOUGHTS
# ============================================================
def germany_thought_messages(world):
    germany = next((hq for hq in world.hqs
                    if hq.id == "THEATER_WEST"
                    and getattr(hq, "nation", None) == "GERMANY"), None)
    if germany is None:
        return

    print("[GERMANY THOUGHTS]")
    for name, region in world.hinge_graph.items():
        dist = path_distance(germany.region, region)
        if dist is None:
            continue
        print(f"- Germany considers {name} (distance={dist}) as a possible future locus.")


# ============================================================
# UNIT ASSIGNMENT REPORT
# ============================================================
def unit_assignment_messages(world):
    print("[UNIT ASSIGNMENTS]")
    for u in world.units:
        flag = getattr(u, "thought_flag", None)
        if flag:
            print(f"- {u.id} → {flag}")


# ============================================================
# AIR PRESSURE
# ============================================================
def air_pressure_messages(world):
    air_sup = getattr(world, "air_superiority", 0.0)
    bomb_press = getattr(world, "bombing_pressure", 0.0)
    print(f"[AIR SUPERIORITY] {'RED' if air_sup > 0.05 else 'GREEN'} (pressure={air_sup:.2f})")
    print(f"[BOMBING PRESSURE] {'RED' if bomb_press > 0.05 else 'GREEN'} (pressure={bomb_press:.2f})")


# ============================================================
# CALL-UP / SEND-DOWN REPORT
# ============================================================
def callup_senddown_messages(world):
    log = getattr(world, "mobilization_log", [])
    if not log:
        return

    print("[CALL-UP / SEND-DOWN REPORT]")
    for entry in log:
        print(f"- {entry}")


# ============================================================
# FUTURE PLANNING DECISIONS (WITH POSITION + DELTA)
# ============================================================
def future_planning_messages(world):
    print("[FUTURE PLANNING DECISIONS]")

    for hq in world.hqs:
        # Original future goal
        original_future = getattr(hq, "future_goal_region", None)
        original_future_name = original_future.name if original_future else "NONE"
        original_future_pos = getattr(original_future, "pos", None)

        # Original long-range goal
        original_long = getattr(hq, "long_range_goal_region", None)
        original_long_name = original_long.name if original_long else "NONE"

        # Final goal after thought-pressure
        final_goal = getattr(hq, "goal_region", None)
        final_goal_name = final_goal.name if final_goal else "NONE"
        final_goal_pos = getattr(final_goal, "pos", None)

        # Current HQ position
        hq_pos = getattr(hq, "pos", None)

        # Decision changed?
        changed = (original_future_name != final_goal_name)

        print(f"- {hq.id} (lvl={hq.level}, nation={hq.nation})")
        print(f"    original future goal: {original_future_name}")
        print(f"    original long-range:  {original_long_name}")
        print(f"    final goal:           {final_goal_name}")
        print(f"    decision changed:     {changed}")

        # Position reporting
        print(f"    HQ position:          {hq_pos}")
        print(f"    original future pos:  {original_future_pos}")
        print(f"    final goal pos:       {final_goal_pos}")

        # Delta vectors
        if hq_pos and original_future_pos:
            delta_original = (
                original_future_pos[0] - hq_pos[0],
                original_future_pos[1] - hq_pos[1]
            )
            print(f"    delta_original:       {delta_original}")

        if hq_pos and final_goal_pos:
            delta_final = (
                final_goal_pos[0] - hq_pos[0],
                final_goal_pos[1] - hq_pos[1]
            )
            print(f"    delta_final:          {delta_final}")

        if original_future_pos and final_goal_pos:
            delta_change = (
                final_goal_pos[0] - original_future_pos[0],
                final_goal_pos[1] - original_future_pos[1]
            )
            print(f"    delta_change:         {delta_change}")

        # Reasoning
        if changed:
            print("    reason: future planning or thought-pressure replaced the goal")
        else:
            print("    reason: no change (HQ kept its planned future goal)")

        print("")
# ============================================================
# NEURAL SHOCKWAVE EVENTS (COLORED + BOLD)
# ============================================================

# ANSI color codes
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def neural_shockwave_messages(world):
    events = getattr(world, "event_log", [])
    if not events:
        return

    print(f"{MAGENTA}{BOLD}[NEURAL SHOCKWAVE]{RESET}")

    for event in events:
        print(f"{YELLOW}{BOLD}⚡ EVENT:{RESET} {event}")

    print("")  # spacing


# ============================================================
# SHOCKWAVE IMPACT — DELTA / CORRIDOR / FUTURE GOALS
# ============================================================

def shockwave_impact_messages(world):
    print(f"{CYAN}{BOLD}[SHOCKWAVE IMPACT]{RESET}")

    for hq in world.hqs:
        print(f"{BOLD}- {hq.id}{RESET} ({hq.nation}, lvl={hq.level})")

        # Corridor impact
        corridor = getattr(hq, "vision_chain", None)
        if corridor:
            names = [r.name for r in corridor]
            print(f"    {BLUE}corridor:{RESET} {names}")

        # Delta impact
        intent = getattr(hq, "movement_intent", None)
        if intent:
            vec = intent.get("vector", None)
            urg = intent.get("urgency", None)
            pivot = intent.get("pivot", None)

            print(f"    {GREEN}delta_final:{RESET} {vec}")
            print(f"    {GREEN}delta_change:{RESET} {pivot}")
            print(f"    {GREEN}urgency:{RESET} {urg:.3f}")

        # Future goal impact
        future = getattr(hq, "future_goal_region", None)
        long = getattr(hq, "long_range_goal_region", None)

        future_name = future.name if future else "NONE"
        long_name = long.name if long else "NONE"

        print(f"    {MAGENTA}future goal:{RESET} {future_name}")
        print(f"    {MAGENTA}long-range goal:{RESET} {long_name}")

        print("")  # spacing
