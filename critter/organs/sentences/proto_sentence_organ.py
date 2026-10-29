import random

class ProtoSentenceOrgan:
    def __init__(self, lexical, heart, graph, chain):
        self.lexical = lexical
        self.heart = heart
        self.graph = graph
        self.chain = chain

    def choose_start(self):
        sources = [src for (src, _, _, _) in self.graph.edges]
        return random.choice(sources) if sources else self.lexical.emit()["word"]

    def choose_next(self, current):
        neighbors = self.graph.neighbors(current)
        if not neighbors:
            return None

        neighbors = sorted(neighbors, key=lambda x: x[1], reverse=True)

        scored = []
        for (v, hinge_w, meta) in neighbors:
            chain_s = self.chain.score_chain([current, v])
            heart_s = self.heart.score_node(current, self.graph, chain_s, [current, v])
            score = hinge_w * 3 + chain_s + heart_s
            scored.append((v, score))

        total = sum(s for (_, s) in scored)
        r = random.random() * total
        acc = 0.0
        for (v, s) in scored:
            acc += s
            if acc >= r:
                return v
        return scored[-1][0]

    def build_sentence(self, min_len=2, max_len=7):
        first = self.choose_start()
        tokens = [first]
        current = first

        for _ in range(max_len - 1):
            nxt = self.choose_next(current)
            if nxt is None:
                break
            tokens.append(nxt)
            current = nxt

        while len(tokens) < min_len:
            tokens.append(self.lexical.emit()["word"])

        return {
            "tokens": tokens,
            "text": " ".join(tokens),
            "length": len(tokens)
        }
