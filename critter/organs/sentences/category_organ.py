class CategoryOrgan:
    """
    CategoryOrgan with:
    - multi-category support
    - multi-word category detection
    - automatic category inheritance
    - prototype-based category propagation
    - hinge-neighbor category propagation
    - category families (lack-family)
    - conditional asking (only when edges are low)
    - automatic category creation
    - automatic definition guessing
    - category-driven edge reinforcement
    - category-driven edge weakening
    """

    def __init__(self, chain, heart, hinge):
        self.chain = chain
        self.heart = heart
        self.hinge = hinge

        self.prototypes = {}
        self.word_categories = {}

        self.multiword_categories = {
            "lack of": ["lack-family"],
            "absence of": ["lack-family"],
        }

        self.lack_family = [
            "lack", "lack of", "absence", "absence of",
            "nothingness", "slowness", "depreciation",
            "without", "void", "scarcity", "deprivation"
        ]

    def detect_multiword(self, tokens):
        joined = " ".join(tokens)
        return self.multiword_categories.get(joined, None)

    def detect_lack_family(self, word):
        for lf in self.lack_family:
            if lf in word:
                return "lack-family"
        return None

    def inherit_from_prototypes(self, word):
        inherited = []
        for cat, words in self.prototypes.items():
            for w in words:
                if w in word or word in w:
                    inherited.append(cat)
        return inherited

    def inherit_from_neighbors(self, word):
        inherited = []
        for (n, w, meta) in self.hinge.graph.neighbors(word):
            if n in self.word_categories:
                inherited.extend(self.word_categories[n])
        return inherited

    def learn(self, word, cat):
        self.word_categories.setdefault(word, []).append(cat)
        self.prototypes.setdefault(cat, []).append(word)

    def should_ask(self):
        edges = len(self.hinge.graph.edges)
        if edges < 10:
            return True
        if hasattr(self.chain, "proto_repetition") and self.chain.proto_repetition > 0.7:
            return True
        if hasattr(self.chain, "category_overlap") and self.chain.category_overlap < 0.2:
            return True
        if hasattr(self.chain, "definition_drift") and self.chain.definition_drift < 0.1:
            return True
        return False

    # ----------------------------------------------------------
    # NEW: guess definition + category when missing
    # ----------------------------------------------------------
    def guess_definition_and_category(self, word):
        cluster = self.chain.lexical_cluster(word)
        if cluster:
            cat = f"{cluster}_concept"
        else:
            cat = f"{word}_concept"

        nn = self.heart.closest(word)
        if nn:
            definition = (word, nn)
        else:
            definition = (word, word)

        self.word_categories[word] = [cat]
        self.prototypes.setdefault(cat, []).append(word)
        self.chain.definitions[word] = definition

        return cat, definition

    # ----------------------------------------------------------
    # Categorize tokens
    # ----------------------------------------------------------
    def categorize(self, tokens):
        out = {}

        mw = self.detect_multiword(tokens)
        if mw:
            for t in tokens:
                out[t] = mw
            return out

        for t in tokens:

            auto = self.detect_lack_family(t)
            if auto:
                out[t] = [auto]
                self.word_categories.setdefault(t, []).append(auto)
                continue

            if t in self.word_categories:
                out[t] = self.word_categories[t]
                continue

            proto_inherit = self.inherit_from_prototypes(t)
            if proto_inherit:
                out[t] = proto_inherit
                self.word_categories[t] = proto_inherit
                continue

            neighbor_inherit = self.inherit_from_neighbors(t)
            if neighbor_inherit:
                out[t] = neighbor_inherit
                self.word_categories[t] = neighbor_inherit
                continue

            if self.should_ask():
                out[t] = None
            else:
                inherited = self.word_categories.get(t, [])
                out[t] = inherited

            # NEW: guess category + definition if still empty
            if not out[t] and t not in self.chain.definitions:
                cat, definition = self.guess_definition_and_category(t)
                out[t] = [cat]
                continue

        for i in range(len(tokens) - 1):
            w1 = tokens[i]
            w2 = tokens[i + 1]

            cats1 = out.get(w1, [])
            cats2 = out.get(w2, [])

            if cats1 is None or cats2 is None:
                continue

            if set(cats1).intersection(cats2):
                for (n, w, meta) in self.hinge.graph.neighbors(w1):
                    self.hinge.graph.update_edge(w1, n, w * 1.2)
            else:
                for (n, w, meta) in self.hinge.graph.neighbors(w1):
                    self.hinge.graph.update_edge(w1, n, w * 0.8)

        return out
