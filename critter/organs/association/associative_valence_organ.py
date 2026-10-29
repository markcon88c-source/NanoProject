import math
from collections import defaultdict

class AssociativeValenceOrgan:
    """
    AssociativeValenceOrgan (full):

    Purpose:
    - Give the critter a way to *care* about certain concepts/composites.
    - Use semantic rivers (hinge, definitions, categories) to spread valence.
    - Allow emergent preferences like: "I want the blue ball because of the color."

    Interfaces:
    - hinge: graph-like organ with neighbors(word) -> [(nbr, weight, meta), ...]
    - category: organ with categories[word] -> [category_labels]
    - definitions: dict-like: word -> (head, tail) conceptual pair
    - heart: NeuralHeart-like organ with embed(word) for semantic similarity.

    Core ideas:
    - valence[word]: scalar liking/disliking.
    - composites: "blue_ball", "red_ball", etc.
    - propagation: valence flows along rivers, decays, and blends.
    """

    def __init__(self,
                 hinge=None,
                 category=None,
                 definitions=None,
                 heart=None):
        # External organs
        self.hinge = hinge
        self.category = category
        self.definitions = definitions or {}
        self.heart = heart

        # Valence memory
        self.valence = defaultdict(float)   # word/composite -> scalar

        # Dynamics
        self.decay_rate = 0.995
        self.propagation_factor = 0.12
        self.definition_factor = 0.08
        self.category_factor = 0.06
        self.semantic_factor = 0.05

        # Optional: track composite usage
        self.composite_usage = defaultdict(int)

    # ----------------------------------------------------------------------
    # Direct valence manipulation
    # ----------------------------------------------------------------------

    def like(self, word, amount=1.0):
        """Increase valence for a word or composite."""
        self.valence[word] += amount

    def dislike(self, word, amount=1.0):
        """Decrease valence for a word or composite."""
        self.valence[word] -= amount

    def set_valence(self, word, value):
        """Explicitly set valence."""
        self.valence[word] = float(value)

    # ----------------------------------------------------------------------
    # Composite formation: "blue_ball"
    # ----------------------------------------------------------------------

    def associate(self, a, b):
        """
        Form a composite concept a_b and assign blended valence.
        This is the core of 'I like the blue ball'.
        """
        composite = f"{a}_{b}"
        va = self.valence[a]
        vb = self.valence[b]
        # blend with a slight bias toward the more strongly valenced term
        if abs(va) > abs(vb):
            blend = 0.6 * va + 0.4 * vb
        else:
            blend = 0.4 * va + 0.6 * vb
        self.valence[composite] = blend
        self.composite_usage[composite] += 1
        return composite

    # ----------------------------------------------------------------------
    # Rivers: hinge, definitions, categories, semantic similarity
    # ----------------------------------------------------------------------

    def _propagate_hinge(self, word, base_v):
        if self.hinge is None or not hasattr(self.hinge, "neighbors"):
            return
        for (nbr, w, meta) in self.hinge.neighbors(word):
            self.valence[nbr] += base_v * self.propagation_factor * w

    def _propagate_definitions(self, word, base_v):
        if word not in self.definitions:
            return
        head, tail = self.definitions[word]
        self.valence[head] += base_v * self.definition_factor
        self.valence[tail] += base_v * self.definition_factor

    def _propagate_categories(self, word, base_v):
        if self.category is None or not hasattr(self.category, "categories"):
            return
        if word not in self.category.categories:
            return
        for cat in self.category.categories[word]:
            self.valence[cat] += base_v * self.category_factor

    def _propagate_semantic(self, word, base_v, top_k=5):
        """
        Optional: use NeuralHeart embeddings to push valence to semantically
        close neighbors (if heart + hinge can provide them).
        """
        if self.heart is None or self.hinge is None:
            return
        if not hasattr(self.heart, "embed"):
            return

        try:
            w_emb = self.heart.embed(word)
        except Exception:
            return

        if w_emb is None:
            return

        # crude semantic neighbor search via hinge neighbors + embedding
        neighbors = []
        if hasattr(self.hinge, "neighbors"):
            for (nbr, w, meta) in self.hinge.neighbors(word):
                try:
                    n_emb = self.heart.embed(nbr)
                    if n_emb is None:
                        continue
                    # cosine-ish similarity
                    sim = self._cosine_like(w_emb, n_emb)
                    neighbors.append((nbr, sim))
                except Exception:
                    continue

        neighbors.sort(key=lambda x: x[1], reverse=True)
        for nbr, sim in neighbors[:top_k]:
            self.valence[nbr] += base_v * self.semantic_factor * sim

    def _cosine_like(self, a, b):
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return dot / (na * nb)

    # ----------------------------------------------------------------------
    # Tick: decay + propagate from active words
    # ----------------------------------------------------------------------

    def tick(self, active_words):
        """
        One tick of valence dynamics:
        - decay all valence
        - propagate from active words along all rivers
        """
        # decay
        for k in list(self.valence.keys()):
            self.valence[k] *= self.decay_rate

        # propagate
        for w in active_words:
            base_v = self.valence[w]
            if base_v == 0.0:
                continue
            self._propagate_hinge(w, base_v)
            self._propagate_definitions(w, base_v)
            self._propagate_categories(w, base_v)
            self._propagate_semantic(w, base_v)

    # ----------------------------------------------------------------------
    # Preference queries
    # ----------------------------------------------------------------------

    def prefer_between(self, options):
        """
        Given a list of words/composites, return the one with highest valence.
        This is where 'I want the blue ball' emerges.
        """
        if not options:
            return None
        return max(options, key=lambda x: self.valence[x])

    def ranked_preferences(self, options):
        """
        Return options sorted by valence, highest first.
        """
        return sorted(options, key=lambda x: self.valence[x], reverse=True)

    # ----------------------------------------------------------------------
    # Introspection / debugging
    # ----------------------------------------------------------------------

    def top_valenced(self, n=20):
        """
        Return the top-n most positively valenced concepts/composites.
        """
        items = [(k, v) for k, v in self.valence.items()]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:n]

    def bottom_valenced(self, n=20):
        """
        Return the top-n most negatively valenced concepts/composites.
        """
        items = [(k, v) for k, v in self.valence.items()]
        items.sort(key=lambda x: x[1])
        return items[:n]
