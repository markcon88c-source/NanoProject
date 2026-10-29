class SentenceOrgan:
    """
    Light structuring organ.
    Uses:
    - chain.score_chain([a,b]) as emergent pair strength
    - cosine similarity from NeuralHeart embeddings
    - tie-word nudges
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

    def cosine(self, a, b):
        try:
            va = self.heart.embed(a)
            vb = self.heart.embed(b)
            dot = sum(x*y for x, y in zip(va, vb))
            norm = (sum(x*x for x in va)**0.5) * (sum(y*y for y in vb)**0.5)
            return dot / norm if norm != 0 else 0.0
        except:
            return 0.0

    def score(self, a, b):
        chain_s = self.chain.score_chain([a, b])
        heart_s = self.cosine(a, b)

        tie_a = self.tie(a)
        tie_b = self.tie(b)
        tie_bonus = 0.1 if tie_a and tie_b and tie_a < tie_b else 0.0

        return chain_s + heart_s + tie_bonus

    def build(self, tokens):
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
