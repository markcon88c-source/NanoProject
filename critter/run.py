#!/usr/bin/env python3
import sys
import json
import importlib
import inspect
import time

# ------------------------------------------------------
# Load organ → module map
# ------------------------------------------------------
with open("module_map.json", "r") as fh:
    organ_map = json.load(fh)

# ------------------------------------------------------
# Dynamically import all organ classes
# ------------------------------------------------------
loaded = {}
for organ_name, module_path in organ_map.items():
    module = importlib.import_module(module_path)
    loaded[organ_name] = getattr(module, organ_name)

# ------------------------------------------------------
# Dynamic role detection
# ------------------------------------------------------
def find_role(name_substring):
    for organ_name in loaded:
        if name_substring.lower() in organ_name.lower():
            return organ_name
    return None

# ------------------------------------------------------
# Fallback Graph / Weighted Drift Hinge / Heart
# ------------------------------------------------------
class FallbackGraph:
    def __init__(self):
        self.edges = {}

    def add_edge(self, u, v, weight=1.0):
        self.edges.setdefault(u, {})
        old = self.edges[u].get(v, (0.0, {}))
        self.edges[u][v] = (old[0] + weight, old[1])

    def update_edge(self, u, v, weight):
        self.edges.setdefault(u, {})
        old = self.edges[u].get(v, (0.0, {}))
        self.edges[u][v] = (old[0] + weight, old[1])

    def neighbors(self, word):
        if word not in self.edges:
            return []
        return [(v, w_meta[0], w_meta[1]) for v, w_meta in self.edges[word].items()]


class FallbackHinge:
    def __init__(self, graph):
        self.graph = graph
        self.decay = 0.92

    def observe(self, event):
        u = event["u"]
        v = event["v"]
        w = float(event["weight"])

        self.graph.edges.setdefault(u, {})
        old = self.graph.edges[u].get(v, (0.0, {}))
        self.graph.edges[u][v] = (old[0] + w, old[1])

        self.graph.edges.setdefault(v, {})
        old_back = self.graph.edges[v].get(u, (0.0, {}))
        self.graph.edges[v][u] = (old_back[0] + (w * self.decay), old_back[1])

    def choose_weighted(self, word):
        if word not in self.graph.edges:
            return None
        neighbors = self.graph.edges[word]
        if not neighbors:
            return None
        (v, (weight, meta)) = max(neighbors.items(), key=lambda kv: kv[1][0])
        return (v, weight, meta)


class FallbackHeart:
    def closest(self, word):
        return word

    def embed(self, word):
        return [hash(word) % 997]

    def score_node(self, current, graph, chain_s, path):
        neighbors = graph.neighbors(current) if hasattr(graph, "neighbors") else []
        return len(path) + len(neighbors)

# ------------------------------------------------------
# Pre-create core positional dependencies
# ------------------------------------------------------
available = {}

chain_name = find_role("chain")
available["chain"] = loaded[chain_name]() if chain_name else None

graph_name = find_role("graph")
available["graph"] = loaded[graph_name]() if graph_name else FallbackGraph()

hinge_name = find_role("hinge")
available["hinge"] = loaded[hinge_name](available["graph"]) if hinge_name else FallbackHinge(available["graph"])

heart_name = find_role("heart")
available["heart"] = loaded[heart_name]() if heart_name else FallbackHeart()

relations_name = find_role("relat")
available["relations"] = loaded[relations_name]() if relations_name else None

# ------------------------------------------------------
# Dependency resolver
# ------------------------------------------------------
def resolve_dependencies(cls, available):
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]

    deps = {}
    for p in params:
        name = p.name

        if name in available:
            deps[name] = available[name]
            continue

        if name == "graph":
            deps[name] = available["graph"]
            continue

        if name == "memory":
            deps[name] = available[name] = {}
            continue

        if p.default is inspect._empty:
            raise TypeError(f"{cls.__name__} requires '{name}'")

    return deps

# ------------------------------------------------------
# Dynamic constructor
# ------------------------------------------------------
def construct(cls, available):
    deps = resolve_dependencies(cls, available)
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]

    args = []
    kwargs = {}

    for p in params:
        name = p.name
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
            args.append(deps[name])
        else:
            kwargs[name] = deps[name]

    return cls(*args, **kwargs)

# ------------------------------------------------------
# Build organs
# ------------------------------------------------------
available["lexical"] = construct(loaded["LexicalOrgan"], available)
available["category"] = construct(loaded["CategoryOrgan"], available)
available["definitions"] = construct(loaded["SoftDefinitionOrgan"], available)
available["micro"] = construct(loaded["MicroPhraseOrgan"], available)
available["proto"] = construct(loaded["ProtoSentenceOrgan"], available)
available["sentencer"] = construct(loaded["SentenceOrgan"], available)
available["valence"] = construct(loaded["AssociativeValenceOrgan"], available)
available["curiosity"] = construct(loaded["CuriosityOrgan"], available)
available["recursor"] = construct(loaded["RecursionOrgan"], available)

# ------------------------------------------------------
# EmergenceOrgan (direct construction — FIXED)
# ------------------------------------------------------
emergence_name = find_role("emergence")
if emergence_name:
    available["emergence"] = loaded["EmergenceOrgan"]()
else:
    available["emergence"] = None

if relations_name:
    available["relations"] = construct(loaded[relations_name], available)
    available["recursor"].relations = available["relations"]

print("CRITTER READY (continuous organism, mathblock-aware)\n")

# ------------------------------------------------------
# Continuous organism loop
# ------------------------------------------------------
while True:
    packet = available["lexical"].emit()
    print("TICK EMIT:", packet)

    token = (packet["word"], packet["mathblock"])
    proto_tokens = [token]
    current_word = packet["word"]

    for _ in range(2):
        neighbors = available["graph"].neighbors(current_word)
        if neighbors:
            nxt_word, hinge_w, meta = neighbors[0]
        else:
            nxt_word = current_word
        nxt_token = (nxt_word, packet["mathblock"])
        proto_tokens.append(nxt_token)
        current_word = nxt_word

    print("PROTO:", [w for (w, mb) in proto_tokens])

    sentence_input = [w for (w, mb) in proto_tokens]
    sentence_words = available["sentencer"].build(sentence_input)

    if isinstance(sentence_words, str):
        sentence_words = sentence_words.split()

    sentence_tokens = [(w, None) for w in sentence_words]
    print("SENTENCE:", [w for (w, mb) in sentence_tokens])

    phrases = available["micro"].build(sentence_tokens)
    print("PHRASES:", phrases)

    sentence_words_only = [w for (w, mb) in sentence_tokens]
    cats = available["category"].categorize(sentence_words_only)
    print("CATEGORIES:", cats)

    defs = available["definitions"].define(phrases)
    print("DEFINITIONS:", defs)

    if available["relations"]:
        available["relations"].relate(sentence_tokens)

    layers = available["recursor"].recurse(sentence_tokens)

    for i, layer in enumerate(layers):
        if layer and isinstance(layer[0], tuple):
            display = [w for (w, mb) in layer]
        else:
            display = layer
        print(f"RECURSION LAYER {i}:", display)

    # ------------------------------------------------------
    # EmergenceOrgan observation + EIX printing (colored)
    # ------------------------------------------------------
    if available.get("emergence") is not None:
        layer3 = layers[-1]
        if layer3 and isinstance(layer3[0], tuple):
            layer3_words = [w for (w, mb) in layer3]
        else:
            layer3_words = layer3

        heart_scores = []
        for w in layer3_words:
            try:
                score = available["heart"].score_node(w, available["graph"], 1.0, [w])
            except:
                score = 0.0
            heart_scores.append(score)

        available["emergence"].observe_tick(
            layer3_words,
            packet,
            heart_scores
        )

        eix = available["emergence"].compute_EIX()

        if eix < 0.01:
            color = "\033[92m"
        elif eix < 0.1:
            color = "\033[93m"
        else:
            color = "\033[91m"

        reset = "\033[0m"
        print(f"EIX: {color}{eix}{reset}")

    print("=== TICK ===")
    time.sleep(0.2)
