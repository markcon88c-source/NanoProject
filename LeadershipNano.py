# LeadershipNano.py
# Models leadership quality friction.

class LeadershipNano:

    def __init__(self):
        # 1.0 = perfect leadership
        # 0.0 = catastrophic leadership
        self.quality = 0.85

    def update_leadership(self, world):
        """
        Leadership degrades slightly over time,
        improves when close to objective,
        worsens when pressure is high.
        """

        # degrade slowly each tick
        self.quality -= 0.005

        # improve when close to objective
        avg_dist = sum(getattr(hq, "distance_to_goal", 0) for hq in world.hqs) / len(world.hqs)
        if avg_dist < 5.0:
            self.quality += 0.02

        # worsen if many HQs are RED
        red_count = sum(1 for hq in world.hqs if getattr(hq, "pressure", None) == "RED")
        if red_count > 0:
            self.quality -= red_count * 0.03

        # clamp
        if self.quality < 0.1:
            self.quality = 0.1
        if self.quality > 1.0:
            self.quality = 1.0

        world.leadership_level = self.quality
