import math

class ChainOrgan:
    """
    ChainOrgan:
    - proto chain scoring (your original)
    - definition storage
    - category storage
    - drift metrics for CategoryOrgan
    """

    def __init__(self, alpha=0.7, tau=1.0):
        self.alpha = alpha
        self.tau = tau

        # NEW: conceptual memory
        self.definitions = {}     # word → (word, guess)
        self.categories = {}      # word → [categories]

        # NEW: drift metrics
        self.definition_drift = 1.0
        self.category_overlap = 1.0
        self.proto_repetition = 0.0

    # NEW: safe placeholder for CategoryOrgan
    def lexical_cluster(self, word):
        """
        Placeholder cluster lookup.
        CategoryOrgan uses this to guess categories.
        """
        return None

    def conditional_logprob(self, token, history):
        # placeholder conditional probability
        return math.log(1.0 / (1 + len(history)))

    def score_chain(self, tokens):
        N = len(tokens)
        if N == 0:
            return 0.0

        log_sum = 0.0
        history = []
        for t in tokens:
            lp = self.conditional_logprob(t, history)
            log_sum += lp
            history.append(t)

        length_penalty = N ** self.alpha
        return (1.0 / length_penalty) * math.exp((1.0 / self.tau) * log_sum)
