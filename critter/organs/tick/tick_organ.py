class TickOrgan:
    def __init__(self, lexical, hinge, graph):
        self.lexical = lexical
        self.hinge = hinge
        self.graph = graph
        self.memory = []
        self.max_memory = 12

    def tick(self):
        # 1. Emit lexical packet
        packet = self.lexical.emit()
        print(f"TICK EMIT: {packet['word']}  [{packet['mathblock']}]")

        # 2. Observe mathblock → hinge edges
        self.hinge.observe(packet)

        # 3. Working memory
        self.memory.append(packet["word"])
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)
        print(f"MEMORY: {self.memory}")

        # 4. Decay edges
        for i, (src, dst, w, meta) in enumerate(self.graph.edges):
            new_w = w * 0.999
            self.graph.edges[i] = (src, dst, new_w, meta)
        print(f"EDGES AFTER DECAY: {len(self.graph.edges)}")

        # 5. Reinforce edges between adjacent memory words
        for a, b in zip(self.memory[:-1], self.memory[1:]):
            for i, (src, dst, w, meta) in enumerate(self.graph.edges):
                if src == a and dst == b:
                    new_w = w * 1.05
                    self.graph.edges[i] = (src, dst, new_w, meta)
                    print(f"REINFORCE: {src} -> {dst}  new_w={new_w}")
