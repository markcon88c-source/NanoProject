# nano_unite_organ.py
from dataclasses import dataclass
from typing import List, Dict, Any
import math

@dataclass
class DecisionToken:
    actor: str
    verb: str
    pressure: float

@dataclass
class DecisionChain:
    actor: str
    tokens: List[DecisionToken]
    log_probs: List[float]

class NanoUniteOrgan:
    def __init__(self, alpha: float = 0.7, tau: float = 1.0):
        self.alpha = alpha
        self.tau = tau

    def score_chain(self, chain: DecisionChain) -> float:
        N = max(len(chain.tokens), 1)
        s = sum(chain.log_probs)
        return (1.0 / (N ** self.alpha)) * math.exp((1.0 / self.tau) * s)

    def edge_weight_aggregate(self, chain: DecisionChain) -> float:
        total = 0.0
        for tok in chain.tokens:
            total += tok.pressure
        return total

    def unified_tension(self, german_chain: DecisionChain, british_chain: DecisionChain) -> float:
        s_ger = self.score_chain(german_chain)
        s_uk  = self.score_chain(british_chain)

        w_ger = self.edge_weight_aggregate(german_chain)
        w_uk  = self.edge_weight_aggregate(british_chain)

        pressure_ger = s_ger * w_ger
        pressure_uk  = s_uk  * w_uk

        return pressure_ger - pressure_uk
