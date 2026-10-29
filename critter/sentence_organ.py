class SentenceOrgan:
    """
    SentenceOrgan with:
    - static ties (original)
    - auto-growing self-ties from categories
    - ganglia-like conceptual reinforcement
    """

    def __init__(self, chain, heart):
        self.chain = chain
        self.heart = heart

        self.ties = {
            "energy": "is",
            "energy's": "is",
            "loneliness": "feels",
            "positivity": "brings",
            "magic": "has",
            "unaware": "seems"
        }

    def tie(self, t):
        return self.ties.get(t)

    # ----------------------------------------------------------
    # NEW: grow self-ties from categories (ganglia)
    # ----------------------------------------------------------
    def grow_self_ties(self, word, categories):
        cats = categories.get(word, [])
        for c in cats:
            if c not in self.ties:
                self.ties[c] = word

    def score(self, a, b):
        return (
            self.chain.get_strength(a, b)
            + self.heart.similarity(a, b)
            + (0.1 if self.tie(a) and self.tie(b) and self.tie(a) < self.tie(b) else 0)
        )

    def build(self, tokens):
        # grow ganglia before scoring
        for t in tokens:
            self.grow_self_ties(t, self.chain.categories)

        ordered = sorted(
            tokens,
            key=lambda t: sum(self.score(t, o) for o in tokens if o != t),
            reverse=True
        )

        out = []
        for t in ordered:
            tw = self.tie(t)
            if tw:
                out.append(tw)
            out.append(t)

        return " ".join(out)
