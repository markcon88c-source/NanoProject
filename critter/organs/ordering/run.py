from organs.lexical.lexical_organ import LexicalOrgan
from organs.graph.hinge_graph import HingeGraph
from organs.mathblocks.mathblock_hinge import MathblockHinge
from organs.chains.chain_organ import ChainOrgan
from organs.heart.neural_heart import NeuralHeart
from organs.sentences.proto_sentence_organ import ProtoSentenceOrgan
from organs.tick.tick_organ import TickOrgan
from organs.ordering.ecn_ordering_organ import ECNOrderingOrgan

# ---------------------------------------------------------
# BUILD CORE ORGANS
# ---------------------------------------------------------

lex = LexicalOrgan()
graph = HingeGraph()
chain = ChainOrgan()
heart = NeuralHeart()
hinge = MathblockHinge(graph, threshold=0.02)

# ---------------------------------------------------------
# BUILD TICK ORGAN (metabolism)
# ---------------------------------------------------------

tick = TickOrgan(lex, hinge, graph)

# ---------------------------------------------------------
# RUN METABOLISM
# ---------------------------------------------------------

for _ in range(200):
    tick.tick()

# ---------------------------------------------------------
# BUILD A PROTO-SENTENCE
# ---------------------------------------------------------

proto = ProtoSentenceOrgan(lex, heart, graph, chain)
sentence = proto.build_sentence()
print("PROTO SENTENCE:", sentence)

# ---------------------------------------------------------
# ORDER WORDS USING ECN
# ---------------------------------------------------------

ordering = ECNOrderingOrgan(graph, chain, heart, tick.memory)
ranked = ordering.order_words()

print("\nECN ORDERED WORDS (top 20):")
for w, s in ranked[:20]:
    print(f"{w}: {s:.4f}")
