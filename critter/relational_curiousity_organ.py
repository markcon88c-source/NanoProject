# ~/critter/organs/relations/relational_curiosity_organ.py

class RelationalCuriosityOrgan:
    """
    Nano:
    - If two items share a category, create a soft relation.
    - If they don't, create a curiosity edge (weak).
    - No correctness required.
    """

    def __init__(self, hinge, category):
        self.hinge = hinge
        self.category = category
        self.same_cat_weight = 0.3
        self.diff_cat_weight = 0.05

    def relate(self, tokens):
        if len(tokens) < 2:
            return

        a, b = tokens[0], tokens[1]

        cats_a = self.category.categories.get(a, [])
        cats_b = self.category.categories.get(b, [])

        # same category → stronger relation
        if any(c in cats_b for c in cats_a):
            self.hinge.observe({"u": a, "v": b, "weight": self.same_cat_weight})
        else:
            # different categories → curiosity relation
            self.hinge.observe({"u": a, "v": b, "weight": self.diff_cat_weight})
