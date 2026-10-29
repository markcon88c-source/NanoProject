class ECNOrderingOrgan:
    """
    Orders words using ECN:
    - hinge strength (edges)
    - chain continuity (multi-hop)
    - neural heart relevance
    - memory adjacency reinforcement
    """

    def __init__(self, graph, chain, heart, memory):
        self.graph = graph
        self.chain = chain
        self.heart = heart
        self.memory = memory

    def score_word(self, word):
        # hinge score = total outgoing weight
        hinge_score = sum(w for (src, dst, w, meta) in self.graph.edges if src == word)

        # chain score = multi-hop continuity
        chain_score = 0.0
        neighbors = self.graph.neighbors(word)
        if neighbors:
            chain_score = sum(
                self.chain.score_chain([word, v])
                for (v, w, meta) in neighbors
            ) / len(neighbors)

        # heart score = relevance pressure
        heart_score = self.heart.score_node(word, self.graph, chain_score, [word])

        # memory score = adjacency reinforcement
        mem_score = self.memory.count(word) * 0.1

        return hinge_score * 3 + chain_score + heart_score + mem_score

    def order_words(self):
        words = set(src for (src, _, _, _) in self.graph.edges)
        scored = [(w, self.score_word(w)) for w in words]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
