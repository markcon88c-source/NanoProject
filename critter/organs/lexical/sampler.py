import random
import time

class LexicalSampler:
    def __init__(self, clusters, freq):
        self.clusters = clusters
        self.freq = freq

    def sample(self):
        # pick a cluster
        cluster = random.choice(list(self.clusters.keys()))
        words = self.clusters[cluster]

        # pick a word
        word = random.choice(words)

        # frequency fallback
        f = self.freq.get(word, 1)

        packet = {
            "type": "lexical",
            "word": word,
            "cluster": cluster,
            "frequency": f,
            "pressure": random.random(),
            "timestamp": int(time.time())
        }

        return packet
