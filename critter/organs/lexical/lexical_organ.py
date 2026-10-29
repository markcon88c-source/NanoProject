from organs.lexical.loader import LexicalLoader
from organs.lexical.sampler import LexicalSampler
from organs.mathblocks.mathblock_organ import MathBlockOrgan

class LexicalOrgan:
    def __init__(self):
        loader = LexicalLoader()
        clusters = loader.load_clusters()
        freq = loader.load_frequency_list()

        self.sampler = LexicalSampler(clusters, freq)
        self.mathblocks = MathBlockOrgan()

    def emit(self):
        packet = self.sampler.sample()
        packet = self.mathblocks.assign(packet)
        return packet
