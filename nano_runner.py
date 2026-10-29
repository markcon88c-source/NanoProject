# nano_runner.py
import math
from dataclasses import dataclass
from typing import List, Dict, Any


# ------------------------------
# Decision Tokens + Chains
# ------------------------------
@dataclass
class DecisionToken:
    actor: str
    verb: str
    log_prob: float


@dataclass
class DecisionChain:
    actor: str
    tokens: List[DecisionToken]


# ------------------------------
# Chain Scorer
# ------------------------------
class ChainScorer:
    def __init__(self, alpha: float = 0.7, tau: float = 1.0):
        self.alpha = alpha
        self.tau = tau

    def score_chain(self, chain: DecisionChain) -> float:
        N = max(len(chain.tokens), 1)
        s = sum(tok.log_prob for tok in chain.tokens)
        return (1.0 / (N ** self.alpha)) * math.exp((1.0 / self.tau) * s)


# ------------------------------
# Edge Graph
# ------------------------------
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
        self.edges.append(Edge(u, v, w, meta))

    def adj(self, u: str):
        return [(e.v, e.w, e.meta) for e in self.edges if e.u == u]


# ------------------------------
# Neural Heart (nano)
# ------------------------------
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

    def h_u(self, u: str, verb_u: str, chain_score_u: float, graph: EdgeGraph) -> float:
        node_emb = self.phi(verb_u)

        ctx_sum = 0.0
        for v, w, meta in graph.adj(u):
            ctx_sum += w * (self.phi(v) + self.psi(meta))

        chain_term = math.log(max(chain_score_u, 1e-8))

        raw = (
            self.W_node * node_emb +
            self.W_ctx * ctx_sum +
            self.W_chain * chain_term +
            self.b
        )

        return math.tanh(raw)


# ------------------------------
# Real Units
# ------------------------------
@dataclass
class RealUnit:
    name: str
    actor: str
    type: str
    lat: float
    lon: float


# ------------------------------
# Action Organ
# ------------------------------
class ActionOrgan:
    def apply(self, units: List[RealUnit], hinge: str):
        for u in units:
            if hinge == "Commit_Main_Effort" and u.type == "Armor":
                u.lat += 0.05
                u.lon += 0.07
            elif hinge == "Probe_Enemy" and u.type == "Infantry":
                u.lat += 0.02
                u.lon += 0.03
            elif hinge == "Delay_Action":
                u.lat -= 0.01
                u.lon -= 0.01


# ------------------------------
# HQ Runner (Nano Integration)
# ------------------------------
class NanoHQRunner:
    def __init__(self):
        self.scorer = ChainScorer()
        self.graph = EdgeGraph()
        self.heart = NeuralHeartNano()
        self.action = ActionOrgan()

    def run(self, chain: DecisionChain, units: List[RealUnit]):
        # Build edges from chain
        for i in range(len(chain.tokens) - 1):
            u = chain.tokens[i].verb
            v = chain.tokens[i + 1].verb
            self.graph.add_edge(u, v, 1.0, {"importance": 1.0})

        # Score chain
        score = self.scorer.score_chain(chain)

        # Compute hinge scores
        hinge_scores = {}
        for tok in chain.tokens:
            hinge_scores[tok.verb] = self.heart.h_u(tok.verb, tok.verb, score, self.graph)

        # Pick hinge
        hinge = max(hinge_scores, key=hinge_scores.get)

        # Apply hinge to units
        self.action.apply(units, hinge)

        # HQ Output
        return f"{chain.actor} HQ selects hinge '{hinge}' and orders units accordingly."


# ------------------------------
# Example Run
# ------------------------------
if __name__ == "__main__":
    chain = DecisionChain(
        actor="GER",
        tokens=[
            DecisionToken("GER", "Probe_Enemy", -0.2),
            DecisionToken("GER", "Commit_Main_Effort", -0.1),
            DecisionToken("GER", "Reinforce_Front", -0.3),
        ]
    )

    units = [
        RealUnit("1st Panzer", "GER", "Armor", 50.064, 19.945),
        RealUnit("3rd Infantry", "GER", "Infantry", 50.064, 19.945),
    ]

    runner = NanoHQRunner()
    print(runner.run(chain, units))

    for u in units:
        print(u)
