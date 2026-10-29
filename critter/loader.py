import json
from pathlib import Path
from wordfreq import top_n_list

class LexicalLoader:
    def __init__(self):
        # Use path relative to this file
        self.base = Path(__file__).parent

    def load_clusters(self):
        clusters = {}
        cluster_dir = self.base / "clusters"

        for f in cluster_dir.glob("*.txt"):
            with open(f, "r") as fp:
                words = [w.strip() for w in fp.readlines() if w.strip()]
                clusters[f.stem] = words

        return clusters

    def load_frequency_list(self, limit=50000):
        words = top_n_list("en", limit)
        freq = {w: (limit - i) for i, w in enumerate(words)}
        return freq
