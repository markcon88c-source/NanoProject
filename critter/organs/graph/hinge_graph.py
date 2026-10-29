class GraphOrgan:
    """
    Dict-based graph compatible with hinge_organ.py and recursion_organ.py.
    Structure:
        edges = {
            u: {
                v: weight              # or (weight, meta)
            }
        }
    """

    def __init__(self):
        # u -> {v: weight or (weight, meta)}
        self.edges = {}

    # ----------------------------------------------------------
    # Add edge
    # ----------------------------------------------------------
    def add_edge(self, u, v, weight, meta=None):
        """
        Add or overwrite edge u → v.
        If meta is provided, store (weight, meta),
        otherwise store just weight.
        """
        self.edges.setdefault(u, {})
        if meta is None:
            self.edges[u][v] = weight
        else:
            self.edges[u][v] = (weight, meta)

    # ----------------------------------------------------------
    # Get neighbors
    # ----------------------------------------------------------
    def neighbors(self, u):
        """
        Returns list of (v, weight, meta) for edges u → v.
        If meta is not stored, meta is returned as None.
        """
        if u not in self.edges:
            return []
        out = []
        for v, val in self.edges[u].items():
            # val can be weight (float) or (weight, meta)
            if isinstance(val, tuple):
                weight, meta = val
            else:
                weight, meta = val, None
            out.append((v, weight, meta))
        return out

    # ----------------------------------------------------------
    # Update edge weight
    # ----------------------------------------------------------
    def update_edge(self, u, v, new_weight):
        """
        Update weight of edge u → v.
        Preserve meta if present.
        """
        if u in self.edges and v in self.edges[u]:
            val = self.edges[u][v]
            if isinstance(val, tuple):
                _, meta = val
                self.edges[u][v] = (new_weight, meta)
            else:
                self.edges[u][v] = new_weight

    # ----------------------------------------------------------
    # Prune weak edges
    # ----------------------------------------------------------
    def prune(self, min_weight=0.01):
        """
        Remove edges with weight < min_weight.
        Works whether edges store weight or (weight, meta).
        """
        to_delete = []
        for u, vmap in self.edges.items():
            newmap = {}
            for v, val in vmap.items():
                if isinstance(val, tuple):
                    w, meta = val
                else:
                    w, meta = val, None
                if w >= min_weight:
                    newmap[v] = (w, meta) if meta is not None else w
            if newmap:
                self.edges[u] = newmap
            else:
                to_delete.append(u)

        for u in to_delete:
            del self.edges[u]
