import math
import time

class CuriosityOrgan:
    """
    Curiosity Organ:
    - Operates on Recursion Layer 3 (conceptual brane)
    - Time-aware curiosity (decay + revival)
    - Category-aware curiosity (concept density)
    - Definition-aware curiosity (semantic overlap)
    - Heart-aware curiosity (activation)
    - History-aware curiosity (long-term fascinations)
    """

    def __init__(self, hinge, heart, category, definitions):
        self.hinge = hinge
        self.heart = heart
        self.category = category
        self.definitions = definitions

        # curiosity memory
        self.history = {}

        # parameters
        self.lambda_ = 0.05   # decay rate
        self.mu = 0.4         # revival strength
        self.gamma = 0.3      # category activation strength
        self.delta = 0.25     # definition activation strength
        self.beta = 0.2       # history reinforcement

        # timestamps
        self.last_seen = {}

    # ----------------------------------------------------------
    # Utility: compute age of a concept
    # ----------------------------------------------------------
    def age(self, c):
        if c not in self.last_seen:
            return 0.0
        return time.time() - self.last_seen[c]

    # ----------------------------------------------------------
    # Utility: compute novelty (difference from past context)
    # ----------------------------------------------------------
    def novelty(self, c, layer):
        # novelty = number of neighbors not seen before
        neighbors = self.hinge.graph.neighbors(c)
        seen = self.history.get(c, [])
        new = [n for (n, w, m) in neighbors if n not in seen]
        return len(new)

    # ----------------------------------------------------------
    # Utility: category density
    # ----------------------------------------------------------
    def category_density(self, c):
        cats = self.category.categorize([c])
        if c in cats:
            return len(cats[c])
        return 0

    # ----------------------------------------------------------
    # Utility: definition overlap
    # ----------------------------------------------------------
    def definition_overlap(self, c, layer):
        defs = self.definitions.define([(c, None)])
        overlap = 0
        for k, (a, b) in defs.items():
            if a[0] in layer or b[0] in layer:
                overlap += 1
        return overlap

    # ----------------------------------------------------------
    # Compute curiosity for each concept in layer 3
    # ----------------------------------------------------------
    def compute(self, layer):
        curiosity_map = {}

        for c in layer:
            if c is None:
                continue

            # base curiosity: inverse edge strength * heart activation * definition spread
            edge_strength = sum(w for (_, w, _) in self.hinge.graph.neighbors(c)) or 1.0
            heart_activation = sum(abs(x) for x in self.heart.embed(c)) or 1.0
            definition_spread = self.definition_overlap(c, layer) or 1.0

            base = (1.0 / (1.0 + edge_strength)) * heart_activation * definition_spread

            # time decay
            D = math.exp(-self.lambda_ * self.age(c))

            # revival
            R = self.mu * self.novelty(c, layer) * heart_activation

            # category activation
            C = 1 + self.gamma * self.category_density(c)

            # definition activation
            S = 1 + self.delta * self.definition_overlap(c, layer)

            # history reinforcement
            H = self.beta * self.history.get(c, 0.0)

            curiosity_map[c] = (base * D + R) * C * S + H

            # update memory
            self.history[c] = curiosity_map[c]
            self.last_seen[c] = time.time()

        return curiosity_map

    # ----------------------------------------------------------
    # Choose the most curious concept
    # ----------------------------------------------------------
    def choose(self, layer):
        curiosity_map = self.compute(layer)
        if not curiosity_map:
            return None
        return max(curiosity_map.items(), key=lambda kv: kv[1])[0]
