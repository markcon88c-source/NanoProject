#!/usr/bin/env python3
import os
import ast
import traceback

print("CLIS STARTED")

# ============================================================
# SAFE IMPORTS
# ============================================================

def safe_import(module_name, attr=None):
    try:
        module = __import__(module_name)
        print(f"IMPORT OK: {module_name}")
        return getattr(module, attr) if attr else module
    except Exception as e:
        print(f"\nIMPORT ERROR: {module_name}")
        print(e)
        traceback.print_exc()
        raise SystemExit(1)

init_world = safe_import("init_world", "init_world")
AlwaysThinkingHQ = safe_import("AlwaysThinkingHQ")
always_thinking = getattr(AlwaysThinkingHQ, "always_thinking")

messages = safe_import("messages")
hq_status_messages = getattr(messages, "hq_status_messages")
unit_status_messages = getattr(messages, "unit_status_messages")
unit_reattach_messages = getattr(messages, "unit_reattach_messages")
france_thought_messages = getattr(messages, "france_thought_messages")
unit_assignment_messages = getattr(messages, "unit_assignment_messages")
air_pressure_messages = getattr(messages, "air_pressure_messages")
callup_senddown_messages = getattr(messages, "callup_senddown_messages")
neural_shockwave_messages = getattr(messages, "neural_shockwave_messages")
shockwave_impact_messages = getattr(messages, "shockwave_impact_messages")

# ⭐ NEW: Germany thoughts
germany_thought_messages = getattr(messages, "germany_thought_messages")

# ============================================================
# FUTURE PLANNING DECISIONS (WHAT HQs DECIDED VS. PLANNED)
# ============================================================
def future_planning_messages(world):
    print("[FUTURE PLANNING DECISIONS]")

    for hq in world.hqs:
        original_future = getattr(hq, "future_goal_region", None)
        original_future_name = original_future.name if original_future else "NONE"

        original_long = getattr(hq, "long_range_goal_region", None)
        original_long_name = original_long.name if original_long else "NONE"

        final_goal = getattr(hq, "goal_region", None)
        final_goal_name = final_goal.name if final_goal else "NONE"

        changed = (original_future_name != final_goal_name)

        print(f"- {hq.id} (lvl={hq.level}, nation={hq.nation})")
        print(f"    original future goal: {original_future_name}")
        print(f"    original long-range:  {original_long_name}")
        print(f"    final goal:           {final_goal_name}")
        print(f"    decision changed:     {changed}")

        if changed:
            print("    reason: future planning or thought-pressure replaced the goal")
        else:
            print("    reason: no change (HQ kept its planned future goal)")

        print("")

# ============================================================
# SAFE CALL WRAPPER
# ============================================================

def safe_call(name, fn, world):
    print(f"\n--- RUNNING {name} ---")
    try:
        fn(world)
        print(f"--- {name} OK ---")
    except Exception as e:
        print(f"\nERROR IN {name}: {e}")
        traceback.print_exc()
        print(f"--- {name} FAILED ---")

# ============================================================
# CLIS CORE DIAGNOSTICS
# ============================================================

def clis(world):
    print("\n==================== CLIS ====================\n")

    try:
        for hq in world.hqs:
            print(f"[HQ {hq.id}] lvl={hq.level} nation={hq.nation}")
            print(f"  assigned:    {hq.assigned}")
            print(f"  goal:        {getattr(hq.goal_region,'name','NONE')}")
            print(f"  future:      {getattr(hq.future_goal_region,'name','NONE')}")
            print(f"  long-range:  {getattr(hq.long_range_goal_region,'name','NONE')}")
            print(f"  corridor:    {[getattr(r,'name','NONE') for r in hq.vision_chain]}")
            print(f"  adjacencies: {[getattr(r,'name','NONE') for r in hq.corridor_adj]}")
            print("")

        for u in world.units:
            parent = getattr(u,"reattached_to",None) or getattr(u,"parent",None)
            parent_id = parent.id if parent else "NONE"

            print(f"[UNIT {u.id}] echelon={u.echelon} type={getattr(u,'utype',None)} nation={u.nation}")
            print(f"  parent:      {parent_id}")
            print(f"  assigned:    {u.assigned}")
            print(f"  goal:        {getattr(u.goal_region,'name','NONE')}")
            print(f"  future:      {getattr(u.future_goal_region,'name','NONE')}")
            print(f"  long-range:  {getattr(u.long_range_goal_region,'name','NONE')}")
            print(f"  pos:         {u.pos}")
            print(f"  adjacencies: {[getattr(r,'name','NONE') for r in u.corridor_adj]}")
            print(f"  corridor:    {[getattr(r,'name','NONE') for r in u.vision_chain]}")
            print("")

    except Exception as e:
        print("\nCLIS ERROR:")
        print(e)
        traceback.print_exc()

    print("================== END CLIS ==================\n")

# ============================================================
# STRICT ASSIGNMENT CHECK
# ============================================================

def clis_assignment_check(world):
    print("\n==================== CLIS ASSIGNMENT CHECK ====================\n")

    bad = 0

    try:
        for hq in world.hqs:
            assigned_valid = hq.assigned not in (None,"NONE",False)
            goal_valid = hq.goal_region is not None
            adj_valid = hq.corridor_adj != [] and all(getattr(r,"name",None) not in ("NONE",None) for r in hq.corridor_adj)
            chain_valid = hq.vision_chain != []

            if not (assigned_valid and goal_valid and adj_valid and chain_valid):
                bad += 1
                print(f"[BAD] HQ {hq.id}")

        for u in world.units:
            assigned_valid = u.assigned not in (None,"NONE",False)
            goal_valid = u.goal_region is not None
            adj_valid = u.corridor_adj != [] and all(getattr(r,"name",None) not in ("NONE",None) for r in u.corridor_adj)
            chain_valid = u.vision_chain != []

            parent = getattr(u,"reattached_to",None) or getattr(u,"parent",None)
            parent_id = parent.id if parent else "NONE"

            if not (assigned_valid and goal_valid and adj_valid and chain_valid):
                bad += 1
                print(f"[BAD] UNIT {u.id} → {parent_id}")

    except Exception as e:
        print("\nASSIGNMENT CHECK ERROR:")
        print(e)
        traceback.print_exc()

    if bad == 0:
        print("\n[CLIS] All HQs and units have valid assignment + goals + edges + chains.\n")
    else:
        print(f"\n[CLIS] Structural problems detected: {bad} entities.\n")

    print("\n================ END ASSIGNMENT CHECK =================\n")

# ============================================================
# CHAIN NONE DIAGNOSTIC
# ============================================================

def clis_chain_none_diagnostic(world):
    print("\n==================== CLIS CHAIN NONE DIAGNOSTIC ====================\n")

    for u in world.units:
        chain = u.vision_chain
        chain_names = [getattr(r,"name",None) for r in chain]

        if any(name == "NONE" for name in chain_names):
            parent = getattr(u,"reattached_to",None) or getattr(u,"parent",None)
            parent_chain = getattr(parent,"vision_chain",[]) if parent else []
            parent_names = [getattr(r,"name",None) for r in parent_chain]

            print(f"[UNIT {u.id}] corridor contains NONE → {chain_names}")

            if parent is None:
                print("  CAUSE: Unit has no parent HQ.")
                print("  FIX: Reattachment logic must assign a parent HQ.\n")
                continue

            if len(parent_chain) > len(chain):
                print("  CAUSE: Unit inherited only the first region of parent chain.")
                print(f"  PARENT CHAIN: {parent_names}")
                print("  FIX: Stage 11 must copy FULL parent.vision_chain.\n")
                continue

            if any(name == "NONE" for name in parent_names):
                print("  CAUSE: Parent HQ chain contains NONE.")
                print("  FIX: Stage 3 BFS corridor generation must produce full chain.\n")
                continue

            print("  CAUSE: Unknown — chain has NONE but parent chain is valid.")
            print("  FIX: Review Stage 11 chain inheritance.\n")

    print("================ END CHAIN NONE DIAGNOSTIC ====================\n")

# ============================================================
# ROOT CAUSE
# ============================================================

def clis_root_cause(world):
    print("\n==================== CLIS ROOT CAUSE ====================\n")

    try:
        print("[CHECK HQ STRUCTURE]")
        for hq in world.hqs:
            if hq.assigned in (None,"NONE",False):
                print(f"[HQ ERROR] {hq.id} missing assignment")
            if hq.goal_region is None:
                print(f"[HQ ERROR] {hq.id} missing goal_region")
            if hq.corridor_adj == []:
                print(f"[HQ ERROR] {hq.id} missing adjacency")
            if hq.vision_chain == []:
                print(f"[HQ ERROR] {hq.id} missing corridor chain")

        print("[CHECK UNIT STRUCTURE]")
        for u in world.units:
            parent = getattr(u,"reattached_to",None) or getattr(u,"parent",None)
            if parent is None:
                print(f"[UNIT ERROR] {u.id} missing parent HQ")
            if u.assigned in (None,"NONE",False):
                print(f"[UNIT ERROR] {u.id} missing assignment")
            if u.goal_region is None:
                print(f"[UNIT ERROR] {u.id} missing goal_region")
            if u.corridor_adj == []:
                print(f"[UNIT ERROR] {u.id} missing adjacency")
            if u.vision_chain == []:
                print(f"[UNIT ERROR] {u.id} missing corridor chain")

    except Exception as e:
        print("\nROOT CAUSE ERROR:")
        print(e)
        traceback.print_exc()

    print("================ END CLIS ROOT CAUSE ====================\n")

# ============================================================
# FILE SYSTEM DIAGNOSTIC
# ============================================================

def scan_project(root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)

def read_file(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def parse_python(source,path):
    try:
        return ast.parse(source,filename=path)
    except:
        return None

def detect_stage11_chain_bug(tree):
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            target=node.targets[0]
            if isinstance(target,ast.Attribute) and target.attr=="vision_chain":
                if isinstance(node.value,ast.List) and node.value.elts:
                    elt=node.value.elts[0]
                    if isinstance(elt,ast.Subscript):
                        if isinstance(elt.value,ast.Attribute):
                            if elt.value.attr=="vision_chain":
                                return True
    return False

def detect_full_chain_copy(tree):
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            target=node.targets[0]
            if isinstance(target,ast.Attribute) and target.attr=="vision_chain":
                if isinstance(node.value,ast.Call):
                    func=node.value.func
                    if isinstance(func,ast.Name) and func.id=="list":
                        return True
                if isinstance(node.value,ast.Subscript):
                    if isinstance(node.value.value,ast.Attribute):
                        if node.value.value.attr=="vision_chain":
                            if isinstance(node.value.slice,ast.Slice):
                                return True
    return False

def detect_adjacency_propagation(tree):
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            target=node.targets[0]
            if isinstance(target,ast.Attribute) and target.attr=="corridor_adj":
                return True
    return False

def detect_bfs_chain_generation(tree):
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            func=node.func
            if isinstance(func,ast.Name):
                if func.id.lower() in ("bfs_path","bfs","build_corridor_chain"):
                    return True
    return False

def clis_fs_diagnostic(world):
    print("\n==================== CLIS FILE SYSTEM DIAGNOSTIC ====================\n")

    root=os.path.dirname(os.path.abspath(__file__))

    for path in scan_project(root):
        source=read_file(path)
        tree=parse_python(source,path)

        print(f"[FILE] {path}")

        if detect_stage11_chain_bug(tree) and not detect_full_chain_copy(tree):
            print("  ISSUE: Stage 11 chain inheritance copies only first element.")
            print("  FIX: Use full copy: u.vision_chain = list(parent.vision_chain)\n")

        if not detect_adjacency_propagation(tree):
            print("  WARNING: No adjacency propagation detected.\n")

        if not detect_bfs_chain_generation(tree):
            print("  WARNING: No BFS corridor generation detected.\n")

        print("")

    print("================ END FILE SYSTEM DIAGNOSTIC ====================\n")

# ============================================================
# MAIN
# ============================================================

def main():
    print("WORLD INIT...")
    try:
        world=init_world()
        print("WORLD INIT OK")
    except Exception as e:
        print("WORLD INIT FAILED:")
        print(e)
        traceback.print_exc()
        return

    print("RUNNING ALWAYS THINKING...")
    try:
        ctx=always_thinking(world)
        world.ctx=ctx
        print("ALWAYS THINKING OK")
    except Exception as e:
        print("ALWAYS THINKING FAILED:")
        print(e)
        traceback.print_exc()
        return

    safe_call("CLIS",clis,world)
    safe_call("CLIS ASSIGNMENT CHECK",clis_assignment_check,world)
    safe_call("CLIS CHAIN NONE DIAGNOSTIC",clis_chain_none_diagnostic,world)
    safe_call("CLIS ROOT CAUSE",clis_root_cause,world)
    safe_call("CLIS FILE SYSTEM DIAGNOSTIC",clis_fs_diagnostic,world)

    safe_call("AIR PRESSURE",air_pressure_messages,world)
    safe_call("HQ STATUS",hq_status_messages,world)
    safe_call("UNIT STATUS",unit_status_messages,world)
    safe_call("UNIT REATTACHMENTS",unit_reattach_messages,world)

    safe_call("FRANCE THOUGHTS",france_thought_messages,world)
    safe_call("GERMANY THOUGHTS",germany_thought_messages,world)

    # ⭐ NEW: Future planning decisions
    safe_call("FUTURE PLANNING DECISIONS", future_planning_messages, world)

    safe_call("UNIT ASSIGNMENTS",unit_assignment_messages,world)
    safe_call("CALLUP SENDDOWN",callup_senddown_messages,world)
    safe_call("NEURAL SHOCKWAVE", neural_shockwave_messages, world)
    safe_call("SHOCKWAVE IMPACT", shockwave_impact_messages, world)
    print("\nCLIS COMPLETE\n")

if __name__=="__main__":
    main()
