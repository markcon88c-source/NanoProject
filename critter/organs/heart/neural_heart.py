import math
import random


class NeuralHeart:
    """
    h_u = σ( W_node·φ(u) + W_ctx·Σ w·(φ(v)⊕ψ(meta)) + W_chain·log(Score_chain(s_u)) + b )
    """

    def __init__(self, embed_dim=64, ctx_dim=64):
        self.embed_dim = embed_dim
        self.ctx_dim = ctx_dim

        # Random init for W_* and b (placeholder; real version would be learned)
        self.W_node = [random.uniform(-0.1, 0.1) for _ in range(embed_dim)]
        self.W_ctx = [random.uniform(-0.1, 0.1) for _ in range(embed_dim + ctx_dim)]
        self.W_chain = random.uniform(-0.1, 0.1)
        self.b = random.uniform(-0.1, 0.1)

        # dynamic vocab support
        self.graph = None  # will be set by hinge organ

    def sigma(self, x):
        # clip to avoid overflow in exp
        if x > 50.0:
            x = 50.0
        elif x < -50.0:
            x = -50.0
        return 1.0 / (1.0 + math.exp(-x))

    def phi(self, node):
        # node embedding placeholder
        return [hash(node) % 997 / 997.0 for _ in range(self.embed_dim)]

    def psi(self, meta):
        # meta/context embedding placeholder
        return [hash(str(meta)) % 997 / 997.0 for _ in range(self.ctx_dim)]

    # ----------------------------------------------------------
    # embed() method required by CLIS, CategoryOrgan, Proto, etc.
    # ----------------------------------------------------------
    def embed(self, word):
        try:
            return self.phi(word)
        except Exception as e:
            print("NEURALHEART INTERNAL ERROR:", e)
            return None

    # ----------------------------------------------------------
    # NEW: closest() — nearest neighbor by cosine similarity
    # ----------------------------------------------------------
    def closest(self, word):
        """
        Find nearest neighbor to `word` using cosine similarity.
        Uses hinge graph nodes as dynamic vocab.
        """
        v1 = self.embed(word)
        if v1 is None:
            return None

        best = None
        best_score = -1.0

        # dynamic vocab from hinge graph
        vocab = []
        if self.graph is not None:
            try:
                vocab = list(self.graph.nodes())
            except:
                vocab = []

        for w in vocab:
            if w == word:
                continue

            v2 = self.embed(w)
            if v2 is None:
                continue

            dot = sum(a * b for a, b in zip(v1, v2))
            norm = (sum(a * a for a in v1) ** 0.5) * (sum(b * b for b in v2) ** 0.5)
            score = dot / norm if norm != 0 else 0.0

            if score > best_score:
                best_score = score
                best = w

        return best

    def score_node(self, u, graph, chain_score, hinge_sentence):
        # φ(u)
        node_emb = self.phi(u)

        # Σ w·(φ(v) ⊕ ψ(meta))
        agg = [0.0] * (self.embed_dim + self.ctx_dim)
        for (v, w, meta) in graph.neighbors(u):
            v_emb = self.phi(v)
            m_emb = self.psi(meta)
            concat = v_emb + m_emb
            for i in range(len(agg)):
                agg[i] += w * concat[i]

        # W_node·φ(u)
        node_term = sum(w * e for w, e in zip(self.W_node, node_emb))

        # W_ctx·agg
        ctx_term = sum(w * e for w, e in zip(self.W_ctx, agg))

        # W_chain·log(Score_chain(s_u))
        chain_term = self.W_chain * math.log(chain_score + 1e-9)

        h_raw = node_term + ctx_term + chain_term + self.b
        return self.sigma(h_raw)
