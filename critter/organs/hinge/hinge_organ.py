class HingeOrgan:
    """
    Weighted drift hinge:
    - observe({u, v, weight}) adds weighted edges
    - edges propagate drift
    - supports proto chaining
    - supports recursion drift
    - HARD CRASH if graph or weights fail
    """

    def __init__(self, graph):
        self.graph = graph
        self.decay = 0.92  # drift decay factor

    # ----------------------------------------------------------
    # HARD CRASH CHECKS
    # ----------------------------------------------------------

    def assert_graph(self):
        if not hasattr(self.graph, "edges"):
            raise RuntimeError("HingeOrgan ERROR: graph has no edges attribute")

    def assert_edge(self, u, v):
        if u not in self.graph.edges:
            raise RuntimeError(f"HingeOrgan ERROR: no edges for {u}")
        if v not in self.graph.edges[u]:
            raise RuntimeError(f"HingeOrgan ERROR: edge {u}->{v} missing")

    # ----------------------------------------------------------
    # Weighted edge propagation
    # ----------------------------------------------------------

    def observe(self, event):
        """
        event = { "u": wordA, "v": wordB, "weight": float }
        """

        self.assert_graph()

        u = event["u"]
        v = event["v"]
        w = float(event["weight"])

        # forward edge
        self.graph.edges.setdefault(u, {})
        self.graph.edges[u][v] = self.graph.edges[u].get(v, 0.0) + w

        # backward drift edge
        self.graph.edges.setdefault(v, {})
        self.graph.edges[v][u] = self.graph.edges[v].get(u, 0.0) + (w * self.decay)

        # HARD CRASH if edges didn't propagate
        self.assert_edge(u, v)
        self.assert_edge(v, u)

    # ----------------------------------------------------------
    # Weighted neighbor selection
    # ----------------------------------------------------------

    def choose_weighted(self, word):
        """
        Returns the highest-weight neighbor.
        """
        if word not in self.graph.edges:
            return None

        neighbors = self.graph.edges[word]
        if not neighbors:
            return None

        # pick highest-weight drift
        return max(neighbors.items(), key=lambda kv: kv[1])[0]
