class SoftDefinitionOrgan:
    """
    Full soft-definition organ.
    Phrases define words based on hinge edges, chain strength, heart cosine,
    and definition memory. Definitions drift and decay over time.
    """

    def __init__(self, chain, heart, hinge):
        self.chain = chain
        self.heart = heart
        self.hinge = hinge

        # {(word, phrase_tuple): weight}
        self.def_weights = {}
        self.decay_rate = 0.98
        self.reinforce_rate = 1.05

    # --- hinge weight (MathblockHinge compatible) ---
    def hinge_weight(self, a, b):
        """
        MathblockHinge stores hinge forces in HINGE_FORCES.
        Keys may be tuples or strings depending on version.
        We support both.
        """
        try:
            # tuple key
            if (a, b) in self.hinge.HINGE_FORCES:
                return self.hinge.HINGE_FORCES.get((a, b), 0.0)

            # string key
            key = f"{a} -> {b}"
            return self.hinge.HINGE_FORCES.get(key, 0.0)

        except:
            return 0.0

    # --- cosine similarity ---
    def cosine(self, a, b):
        try:
            va = self.heart.embed(a)
            vb = self.heart.embed(b)
            dot = sum(x*y for x, y in zip(va, vb))
            norm = (sum(x*x for x in va)**0.5) * (sum(y*y for y in vb)**0.5)
            return dot / norm if norm != 0 else 0.0
        except:
            return 0.0

    # --- phrase strength ---
    def phrase_strength(self, a, b):
        return (
            self.hinge_weight(a, b)
            + self.chain.score_chain([a, b])
            + self.cosine(a, b)
        )

    # --- reinforcement ---
    def reinforce(self, word, phrase):
        key = (word, phrase)
        old = self.def_weights.get(key, 0.1)
        self.def_weights[key] = old * self.reinforce_rate

    # --- decay ---
    def decay(self):
        for key in list(self.def_weights.keys()):
            self.def_weights[key] *= self.decay_rate
            if self.def_weights[key] < 0.01:
                del self.def_weights[key]

    # --- main definition builder ---
    def define(self, phrases):
        """
        phrases: list containing tokens and tuples
        returns: dict {word: (a,b)}
        """
        out = {}

        for item in phrases:
            # Only accept 2-element tuples as definitional phrases
            if not isinstance(item, tuple) or len(item) != 2:
                continue

            a, b = item
            strength = self.phrase_strength(a, b)

            # threshold is intentionally low to allow emergent meaning
            if strength > 0.25:
                out[a] = (a, b)
                self.reinforce(a, (a, b))

            if strength > 0.25:
                out[b] = (a, b)
                self.reinforce(b, (a, b))

        self.decay()
        return out
