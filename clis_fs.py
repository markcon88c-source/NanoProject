#!/usr/bin/env python3
"""
CLIS File System Diagnostic

Scans the project directory, reads Python files, parses them with AST,
and looks for patterns related to corridor chain inheritance, adjacency
propagation, and BFS corridor generation.

You can extend the detectors as your ecosystem grows.
"""

import os
import ast
import traceback


# ============================================================
# PROJECT SCANNING
# ============================================================

def scan_project(root):
    """
    Yield absolute paths to all .py files under the given root.
    """
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)


def read_file(path):
    """
    Read a file and return its contents as a string.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def parse_python(source, path="<unknown>"):
    """
    Parse Python source into an AST. Return None on failure.
    """
    try:
        return ast.parse(source, filename=path)
    except Exception:
        return None


# ============================================================
# PATTERN DETECTORS
# ============================================================

def detect_stage11_chain_bug(tree):
    """
    Heuristic: look for assignments to u.vision_chain that only take
    a single element from parent.vision_chain (e.g. parent.vision_chain[0]).
    """
    if tree is None:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # target: u.vision_chain or self.vision_chain
            target = node.targets[0]
            if isinstance(target, ast.Attribute):
                if target.attr == "vision_chain":
                    # value: [parent.vision_chain[0]] or similar
                    if isinstance(node.value, ast.List) and node.value.elts:
                        elt = node.value.elts[0]
                        if isinstance(elt, ast.Subscript):
                            if isinstance(elt.value, ast.Attribute):
                                if elt.value.attr == "vision_chain":
                                    # u.vision_chain = [parent.vision_chain[0]]
                                    return True
    return False


def detect_full_chain_copy(tree):
    """
    Heuristic: look for u.vision_chain = list(parent.vision_chain)
    or u.vision_chain = parent.vision_chain[:]
    """
    if tree is None:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            if isinstance(target, ast.Attribute) and target.attr == "vision_chain":
                # list(parent.vision_chain)
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Name) and func.id == "list":
                        if node.value.args and isinstance(node.value.args[0], ast.Attribute):
                            if node.value.args[0].attr == "vision_chain":
                                return True
                # parent.vision_chain[:]
                if isinstance(node.value, ast.Subscript):
                    if isinstance(node.value.value, ast.Attribute):
                        if node.value.value.attr == "vision_chain":
                            if isinstance(node.value.slice, ast.Slice):
                                return True
    return False


def detect_adjacency_propagation(tree):
    """
    Heuristic: look for assignments like u.corridor_adj = parent.corridor_adj
    or hq.corridor_adj = something derived from hinge_graph.
    """
    if tree is None:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            if isinstance(target, ast.Attribute) and target.attr == "corridor_adj":
                # u.corridor_adj = parent.corridor_adj
                if isinstance(node.value, ast.Attribute) and node.value.attr == "corridor_adj":
                    return True
                # hq.corridor_adj = <something>
                if not isinstance(node.value, ast.Constant):
                    return True
    return False


def detect_bfs_chain_generation(tree):
    """
    Heuristic: look for functions that appear to generate a corridor chain
    using BFS or pathfinding (e.g. bfs_path, build_corridor_chain).
    """
    if tree is None:
        return False

    for node in ast.walk(tree):
        # Look for function calls with BFS-ish names
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                if func.id.lower() in ("bfs_path", "bfs", "build_corridor_chain", "compute_chain"):
                    return True
        # Or function definitions with corridor-related names
        if isinstance(node, ast.FunctionDef):
            name = node.name.lower()
            if any(key in name for key in ("corridor", "chain", "path")):
                return True
    return False


# ============================================================
# FILE SYSTEM DIAGNOSTIC ENTRYPOINT
# ============================================================

def clis_fs_diagnostic(world):
    """
    Run a project-wide diagnostic over the file system.

    This does NOT mutate the world; it only inspects source files
    and reports structural issues and likely causes.
    """
    print("\n==================== CLIS FILE SYSTEM DIAGNOSTIC ====================\n")

    try:
        root = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        root = "."

    for path in scan_project(root):
        source = read_file(path)
        if not source:
            continue

        tree = parse_python(source, path)
        if tree is None:
            print(f"[FILE] {path}")
            print("  ERROR: Could not parse Python source.\n")
            continue

        print(f"[FILE] {path}")

        # Stage 11 chain bug
        if detect_stage11_chain_bug(tree) and not detect_full_chain_copy(tree):
            print("  ISSUE: Detected assignment to vision_chain that likely copies only the first element.")
            print("  CAUSE: Units inherit only parent.vision_chain[0], rest becomes NONE.")
            print("  FIX: Replace with full copy: u.vision_chain = list(parent.vision_chain) or parent.vision_chain[:].\n")

        # Adjacency propagation
        if not detect_adjacency_propagation(tree):
            print("  WARNING: No clear adjacency propagation detected in this file.")
            print("  NOTE: Ensure hq.corridor_adj and u.corridor_adj are populated from hinge_graph or parent HQ.\n")

        # BFS corridor generation
        if not detect_bfs_chain_generation(tree):
            print("  WARNING: No obvious BFS/path-based corridor generation detected in this file.")
            print("  NOTE: Ensure a corridor chain is built via BFS or pathfinding from goal to long-range.\n")

        print("")  # spacing between files

    print("================ END FILE SYSTEM DIAGNOSTIC ====================\n")


# ============================================================
# STANDALONE TEST HOOK
# ============================================================

if __name__ == "__main__":
    # Minimal standalone run: no world, just scan the project.
    try:
        clis_fs_diagnostic(world=None)
    except Exception as e:
        print("CLIS FS standalone run failed:")
        print(e)
        traceback.print_exc()
