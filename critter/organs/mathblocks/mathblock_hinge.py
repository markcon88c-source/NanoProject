import math

class MathblockHinge:
    """
    Full hinge system:
    - Accepts lexical packets (word + mathblock)
    - Accepts synthetic u→v packets (word pairs)
    - Computes mathblock similarity
    - Creates edges
    - Reinforces edges
    - Decays edges
    - Never crashes
    """

    def __init__(self, graph, threshold=0.1, decay=0.98, reinforce=1.05):
        self.graph = graph
        self.threshold = threshold
        self.decay_rate = decay
        self.reinforce_rate = reinforce
        self.last_packet = None

    # ----------------------------------------------------------
    # Mathblock similarity (robust)
    # ----------------------------------------------------------
    def similarity(self, a, b):
        """
        Robust similarity:
        - compares character sets (not positions)
        - works with random mathblocks
        """
        if a is None or b is None:
            return 0.0

        set_a = set(a)
        set_b = set(b)

        inter = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        if union == 0:
            return 0.0

        return inter / union

    # ----------------------------------------------------------
    # Observe packets
    # ----------------------------------------------------------
    def observe(self, packet):
        """
        Packet may be:
        - lexical packet: {"word": "...", "mathblock": "..."}
        - synthetic packet: {"u": "...", "v": "...", "mathblock": "..."}
        """

        # ------------------------------------------------------
        # Synthetic u→v packet
        # ------------------------------------------------------
        if "u" in packet and "v" in packet:
            u = packet["u"]
            v = packet["v"]
            mb = packet.get("mathblock", None)

            # similarity of mathblock to itself (neutral)
            sim = self.similarity(mb, mb)

            # add edge
            self.graph.add_edge(u, v, sim, {"src": "synthetic", "mathblock": mb})

            # reinforce neighbors
            for (n, w, meta) in self.graph.neighbors(u):
                new_w = w * self.reinforce_rate
                self.graph.update_edge(u, n, new_w)

            # decay all edges
            for (a, b, w, meta) in list(self.graph.edges):
                new_w = w * self.decay_rate
                self.graph.update_edge(a, b, new_w)

            return

        # ------------------------------------------------------
        # Lexical packet
        # ------------------------------------------------------
        if "word" in packet and "mathblock" in packet:
            if self.last_packet is None:
                self.last_packet = packet
                return

            prev = self.last_packet
            curr = packet

            sim = self.similarity(prev["mathblock"], curr["mathblock"])

            if sim >= self.threshold:
                self.graph.add_edge(
                    prev["word"],
                    curr["word"],
                    sim,
                    {"src": "mathblock", "sim": sim}
                )

            # update last packet
            self.last_packet = curr
            return

        # ------------------------------------------------------
        # Unknown packet type
        # ------------------------------------------------------
        return
