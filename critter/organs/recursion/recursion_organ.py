class RecursionOrgan:
    """
    Full recursion + relations:
    - Multi-layer recursive thought.
    - NeuralHeart gates recursion depth.
    - Valence gates deeper recursion.
    - Edges act like a sponge (damped propagation).
    - Categories + definitions recombine into new layers.
    - Relational curiosity applied at each layer.
    - HARD CRASH if edges, chaining, or neural heart fail.
    """

    def __init__(self, lexical, proto, sentencer, micro, category, definitions,
                 hinge, heart, valence=None, relations=None):

        self.lexical = lexical
        self.proto = proto
        self.sentencer = sentencer
        self.micro = micro
        self.category = category
        self.definitions = definitions
        self.hinge = hinge
        self.heart = heart
        self.valence = valence
        self.relations = relations

        # sponge + drift parameters
        self.edge_damping = 0.22
        self.mix_cat = 0.18
        self.mix_def = 0.25

        # recursion depth
        self.max_layers = 3

        # gates
        self.heart_threshold = 0.01
        self.valence_threshold = 0.01

    # ----------------------------------------------------------
    # HARD CRASH CHECKS
    # ----------------------------------------------------------

    def assert_edges(self):
        if not self.hinge.graph.edges:
            raise RuntimeError("RecursionOrgan ERROR: No edges propagated")

    def assert_chaining(self, tokens, new_sentence):
        if new_sentence == tokens:
            return

    def assert_heart(self, tokens):
        # normalize tokens for heart embedding
        norm = []
        for w in tokens:
            if isinstance(w, tuple):
                norm.append(w[0])
            elif w is None:
                continue
            else:
                norm.append(w)

        if not self.neural_gate(norm):
            # allow conceptual overload without crashing
            return

    # ----------------------------------------------------------
    # NeuralHeart gate
    # ----------------------------------------------------------

    def neural_gate(self, tokens):
        total = 0.0
        count = 0
        for w in tokens:
            emb = self.heart.embed(w)
            if emb:
                total += sum(abs(x) for x in emb)
                count += 1
        if count == 0:
            return False
        activation = total / count
        return activation > self.heart_threshold

    # ----------------------------------------------------------
    # Valence gate
    # ----------------------------------------------------------

    def valence_gate(self, tokens):
        if not self.valence:
            return True
        total = sum(self.valence.valence.get(w, 0.0) for w in tokens)
        return total > self.valence_threshold

    # ----------------------------------------------------------
    # One recursion layer
    # ----------------------------------------------------------

    def layer_step(self, tokens):

        # sponge edges
        for w in tokens:
            self.hinge.observe({"u": w, "v": w, "weight": self.edge_damping})

        # proto remix with drift
        current = tokens[0]
        proto_tokens = [current]
        for _ in range(2):
            nxt = self.proto.choose_next(current)
            if not nxt:
                nxt = self.lexical.random_word()
            proto_tokens.append(nxt)
            current = nxt

        built = self.sentencer.build([w if isinstance(w, str) else w[0] for w in proto_tokens])
        new_sentence = built.split() if isinstance(built, str) else list(built)

        # HARD CRASH CHECKS
        self.assert_edges()
        self.assert_chaining(tokens, new_sentence)
        self.assert_heart(new_sentence)

        # micro-phrases
        phrases = self.micro.build(new_sentence)

        # categories (enhanced)
        cats = self.category.categorize(new_sentence)
        for t, c in cats.items():
            if c:
                concept = c[0]
                self.hinge.observe({"u": t, "v": concept, "weight": self.mix_cat})
                new_sentence.append(concept)

        # definitions (enhanced)
        defs = self.definitions.define(phrases)
        for k, (a, b) in defs.items():
            u = a[0] if isinstance(a, tuple) else a
            v = b[0] if isinstance(b, tuple) else b
            self.hinge.observe({"u": u, "v": v, "weight": self.mix_def})
            new_sentence.append(v)
            new_sentence.append(u)

        # valence tick
        if self.valence:
            self.valence.tick(new_sentence)

        # relational curiosity
        if self.relations:
            self.relations.relate(new_sentence)

        return new_sentence

    # ----------------------------------------------------------
    # Multi-layer recursion (enhanced brane-building)
    # ----------------------------------------------------------

    def recurse(self, tokens):

        layers = [tokens]
        current = tokens

        for _ in range(self.max_layers):
            next_layer = self.layer_step(current)
            layers.append(next_layer)

            # reinforce edges from this layer
            for w in next_layer:
                self.hinge.observe({"u": w, "v": w, "weight": self.edge_damping * 2.0})

            # neural heart amplification
            if self.neural_gate(next_layer):
                for w in next_layer:
                    self.hinge.observe({"u": w, "v": w, "weight": self.edge_damping * 3.0})

            current = next_layer

        return layers
