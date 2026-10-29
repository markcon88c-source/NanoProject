class SentenceOrgan:
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

    def score(self, a, b):
        return (
            self.chain.get_strength(a, b)
            + self.heart.similarity(a, b)
            + (0.1 if self.tie(a) and self.tie(b) and self.tie(a) < self.tie(b) else 0)
        )

    def build(self, tokens):
        ordered = sorted(tokens, key=lambda t: sum(self.score(t, o) for o in tokens if o != t), reverse=True)
        out = []
        for t in ordered:
            tw = self.tie(t)
            if tw:
                out.append(tw)
            out.append(t)
        return " ".join(out)
