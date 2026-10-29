class MicroPhraseOrgan:
    """
    Nano micro-phrase organ.
    Forms tiny proto-phrases only when the critter's edges say it likes them.
    """

    def __init__(self, chain, heart, hinge):
        self.chain = chain
        self.heart = heart
        self.hinge = hinge

    def hinge_weight(self, a, b):
        try:
            return self.hinge.edges.get((a, b), 0.0)
        except:
            return 0.0

    def cosine(self, a, b):
        try:
            va = self.heart.embed(a)
            vb = self.heart.embed(b)
            dot = sum(x*y for x, y in zip(va, vb))
            norm = (sum(x*x for x in va)**0.5) * (sum(y*y for y in vb)**0.5)
            return dot / norm if norm != 0 else 0.0
        except:
            return 0.0

    def pair_score(self, a, b):
        hinge_s = self.hinge_weight(a, b)
        chain_s = self.chain.score_chain([a, b])
        heart_s = self.cosine(a, b)
        return hinge_s + chain_s + heart_s

    def build(self, tokens, threshold=0.25):
        out = []
        skip = False

        for i in range(len(tokens) - 1):
            if skip:
                skip = False
                continue

            a = tokens[i]
            b = tokens[i+1]

            score = self.pair_score(a, b)

            if score >= threshold:
                out.append((a, b))
                skip = True
            else:
                out.append(a)

        if not skip:
            out.append(tokens[-1])

        return out
