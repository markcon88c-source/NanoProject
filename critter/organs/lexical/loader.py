from pathlib import Path
from wordfreq import top_n_list

class LexicalLoader:
    def __init__(self):
        self.base = Path(__file__).parent

    def load_clusters(self):
        words = top_n_list("en", 50000)

        clusters = {
            "animals": [w for w in words if w.endswith("ion")],
            "verbs": [w for w in words if w.endswith("ing")],
            "emotions": [w for w in words if w.endswith("ness")],
            "physics": [w for w in words if "energy" in w],
            "military": [w for w in words if "war" in w],
            "fantasy": [w for w in words if "magic" in w],
            "tech": [w for w in words if "data" in w],
            "colors": [w for w in words if w in ["red","blue","green","yellow"]],
            "locations": [w for w in words if w.endswith("town")],
            "abstract": [w for w in words if w.endswith("ity")],
        }

        for k in clusters:
            if not clusters[k]:
                clusters[k] = ["placeholder"]

        return clusters

    def load_frequency_list(self, limit=50000):
        words = top_n_list("en", limit)
        freq = {w: (limit - i) for i, w in enumerate(words)}
        return freq
