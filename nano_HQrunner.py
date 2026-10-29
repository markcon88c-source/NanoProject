# nano_HQrunner.py
import math
from dataclasses import dataclass
from typing import List, Dict, Any


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class DecisionToken:
    actor: str
    verb: str
    log_prob: float
    meta: Dict[str, Any]


@dataclass
class DecisionChain:
    actor: str
    tokens: List[DecisionToken]


@dataclass
class RealUnit:
    name: str
    actor: str
    type: str
    lat: float
    lon: float
    echelon: str  # Division / Corps / Army / Theater


# ============================================================
# CHAIN SCORER
# ============================================================

class ChainScorer:
    def __init__(self, alpha: float = 0.7, tau: float = 1.0):
        self.alpha = alpha
        self.tau = tau

    def score_chain(self, chain: DecisionChain) -> float:
        N = max(len(chain.tokens), 1)
        s = sum(tok.log_prob for tok in chain.tokens)
        score = (1.0 / (N ** self.alpha)) * math.exp((1.0 / self.tau) * s)
        print(f"[HQ] Chain score = {score:.4f} (N={N})")
        return score


# ============================================================
# EDGE GRAPH
# ============================================================

@dataclass
class Edge:
    u: str
    v: str
    w: float
    meta: Dict[str, Any]


class EdgeGraph:
    def __init__(self):
        self.edges: List[Edge] = []

    def add_edge(self, u: str, v: str, w: float, meta: Dict[str, Any]):
        print(f"[HQ] Edge added: {u} -> {v} (w={w}, meta={meta})")
        self.edges.append(Edge(u, v, w, meta))

    def adj(self, u: str):
        return [(e.v, e.w, e.meta) for e in self.edges if e.u == u]


# ============================================================
# NEURAL HEART (NANO)
# ============================================================

class NeuralHeartNano:
    def __init__(self):
        self.W_node = 0.8
        self.W_ctx = 0.6
        self.W_chain = 0.9
        self.b = 0.1

    def phi(self, verb: str) -> float:
        table = {
            "Probe_Enemy": 0.6,
            "Commit_Main_Effort": 1.0,
            "Reinforce_Front": 0.5,
            "Delay_Action": 0.3,
            "Shift_Air_Sorties": 0.7,
            "Secure_Supply_Lines": 0.4,
        }
        return table.get(verb, 0.2)

    def psi(self, meta: Dict[str, Any]) -> float:
        return float(meta.get("importance", 1.0))

    def h_u(self, verb_u: str, chain_score: float, graph: EdgeGraph) -> float:
        node_emb = self.phi(verb_u)

        ctx_sum = 0.0
        for v, w, meta in graph.adj(verb_u):
            ctx_sum += w * (self.phi(v) + self.psi(meta))

        chain_term = math.log(max(chain_score, 1e-8))

        raw = (
            self.W_node * node_emb +
            self.W_ctx * ctx_sum +
            self.W_chain * chain_term +
            self.b
        )

        h = math.tanh(raw)
        print(f"[HQ] h({verb_u}) = {h:.4f}")
        return h


# ============================================================
# ACTION ORGAN (MOVEMENT)
# ============================================================

class ActionOrgan:
    def apply(self, units: List[RealUnit], hinge: str):
        print(f"[HQ] Movement for hinge '{hinge}'")
        for u in units:
            before = (u.lat, u.lon)

            if hinge == "Commit_Main_Effort" and u.type == "Armor":
                u.lat += 0.05
                u.lon += 0.07

            elif hinge == "Probe_Enemy" and u.type == "Infantry":
                u.lat += 0.02
                u.lon += 0.03

            elif hinge == "Delay_Action":
                u.lat -= 0.01
                u.lon -= 0.01

            after = (u.lat, u.lon)
            if before != after:
                print(f"  - {u.name} moved from {before} to {after}")


# ============================================================
# CALL-UP ORGAN (HQ HIERARCHY)
# ============================================================

class CallUpOrganNano:
    def call_up(self, units: List[RealUnit], hinge: str):
        print(f"[HQ] Call-up / send-down for hinge '{hinge}'")
        moved = []

        for u in units:
            if hinge == "Commit_Main_Effort" and u.type == "Armor":
                if u.echelon == "Division":
                    print(f"  - {u.name}: Division → Corps")
                    u.echelon = "Corps"
                    moved.append((u.name, "Division → Corps"))

            elif hinge == "Shift_Air_Sorties" and u.type == "Air":
                if u.echelon == "Corps":
                    print(f"  - {u.name}: Corps → Army")
                    u.echelon = "Army"
                    moved.append((u.name, "Corps → Army"))

            elif hinge == "Secure_Supply_Lines" and u.type == "Infantry":
                if u.echelon == "Army":
                    print(f"  - {u.name}: Army → Division")
                    u.echelon = "Division"
                    moved.append((u.name, "Army → Division"))

            elif hinge == "Delay_Action":
                if u.echelon != "Theater":
                    old = u.echelon
                    print(f"  - {u.name}: {old} → Theater")
                    u.echelon = "Theater"
                    moved.append((u.name, f"{old} → Theater"))

        return moved


# ============================================================
# NANO HQ RUNNER (FULL)
# ============================================================

class NanoHQRunner:
    def __init__(self):
        self.scorer = ChainScorer()
        self.graph = EdgeGraph()
        self.heart = NeuralHeartNano()
        self.action = ActionOrgan()
        self.callup = CallUpOrganNano()

    def run(self, chain: DecisionChain, units: List[RealUnit]):
        print(f"[HQ] Running HQ for actor {chain.actor}")
        print("[HQ] Building edges...")

        for i in range(len(chain.tokens) - 1):
            u = chain.tokens[i].verb
            v = chain.tokens[i + 1].verb
            self.graph.add_edge(u, v, 1.0, {"importance": 1.0})

        score = self.scorer.score_chain(chain)

        print("[HQ] Computing hinge scores...")
        hinge_scores = {}
        for tok in chain.tokens:
            hinge_scores[tok.verb] = self.heart.h_u(tok.verb, score, self.graph)

        hinge = max(hinge_scores, key=hinge_scores.get)
        print(f"[HQ] Selected hinge: '{hinge}'")

        self.action.apply(units, hinge)
        callup_moves = self.callup.call_up(units, hinge)

        print("[HQ] Summary:")
        print(f"  Hinge: {hinge}")
        for name, move in callup_moves:
            print(f"  Reassignment: {name} -> {move}")

        return f"[HQ] Completed hinge '{hinge}'"


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    chain = DecisionChain(
        actor="GER",
        tokens=[
            DecisionToken("GER", "Probe_Enemy", -0.3, {}),
            DecisionToken("GER", "Commit_Main_Effort", -0.1, {}),
            DecisionToken("GER", "Reinforce_Front", -0.2, {}),
        ]
    )

    units = [
        RealUnit("1st Panzer", "GER", "Armor", 50.064, 19.945, "Division"),
        RealUnit("3rd Infantry", "GER", "Infantry", 50.064, 19.945, "Division"),
    ]

    hq = NanoHQRunner()
    result = hq.run(chain, units)

    print("\n[HQ] Units after execution:")
    for u in units:
        print(" ", u)
