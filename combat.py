# combat.py
# Multi-tick combat engine with organization, officers, reinforcements,
# and friction hooks.

import random
import math

# -------------------------------------------------------------------
# Battle object: persists across ticks
# -------------------------------------------------------------------

class Battle:
    def __init__(self, region, attackers, defenders):
        self.region = region
        self.attackers = attackers[:]   # list[Unit]
        self.defenders = defenders[:]   # list[Unit]

        self.duration = 0              # ticks
        self.intensity = 0.0           # 0..1
        self.supply_drain = 0.0
        self.friction_gain = 0.0

        self.is_active = True

    def tick(self, world):
        """
        Advance battle by one tick:
        - compute intensity
        - drain ORG
        - apply bombing pressure
        - call friction hooks
        - maybe trigger reinforcements
        - maybe end battle
        """

        if not self.is_active:
            return

        self.duration += 1

        # -----------------------------
        # 1. Compute base intensity
        # -----------------------------
        atk_count = len(self.attackers)
        def_count = len(self.defenders)
        if atk_count == 0 or def_count == 0:
            self.is_active = False
            return

        # Simple intensity: more units → more intensity
        self.intensity = min(1.0, 0.1 + 0.02 * (atk_count + def_count))

        # -----------------------------
        # 2. Bombing pressure modifier
        # -----------------------------
        # Assume world has bombing_pressure in [0, 1]
        bombing_pressure = getattr(world, "bombing_pressure", 0.0)

        # RED bombing → more ORG loss
        org_multiplier = 1.0 + bombing_pressure * 0.5

        # -----------------------------
        # 3. Drain ORG for attackers/defenders
        # -----------------------------
        org_loss_base = int(50_000 * self.intensity)

        for u in self.attackers:
            if getattr(u, "org", None) is None:
                continue
            loss = int(org_loss_base * org_multiplier)
            u.org = max(0, u.org - loss)

        for u in self.defenders:
            if getattr(u, "org", None) is None:
                continue
            loss = int(org_loss_base)
            u.org = max(0, u.org - loss)

        # -----------------------------
        # 4. Officer effects (HQ-level)
        # -----------------------------
        def officer_bonus(hq):
            if hq is None:
                return 1.0
            skill = getattr(hq, "officer_skill", 0.5)
            recovery = getattr(hq, "officer_recovery", 0.5)
            return 0.5 + 0.5 * (skill + recovery) / 2.0

        # Attackers: use parent HQ of first attacker
        atk_hq = self.attackers[0].parent if self.attackers[0].parent else None
        def_hq = self.defenders[0].parent if self.defenders[0].parent else None

        atk_officer = officer_bonus(atk_hq)
        def_officer = officer_bonus(def_hq)

        # Small ORG recovery each tick (rest between volleys)
        for u in self.attackers:
            if getattr(u, "org", None) is None:
                continue
            gain = int(20_000 * atk_officer * (1.0 - bombing_pressure))
            u.org = min(u.max_org, u.org + gain)

        for u in self.defenders:
            if getattr(u, "org", None) is None:
                continue
            gain = int(25_000 * def_officer * (1.0 - bombing_pressure))
            u.org = min(u.max_org, u.org + gain)

        # -----------------------------
        # 5. Supply + friction hooks
        # -----------------------------
        # Supply drain proportional to intensity and unit count
        self.supply_drain = (atk_count + def_count) * self.intensity * 1000
        world.supply_level = max(0.0, world.supply_level - self.supply_drain)

        # Friction gain: battles grind the system
        self.friction_gain = self.intensity * (1.0 + bombing_pressure)
        world.friction += self.friction_gain

        # Hook: dispersion / reorg factor
        # (friction.py can read world.dispersion / prev_dispersion)
        world.prev_dispersion = world.dispersion
        world.dispersion += self.friction_gain * 0.1

        # -----------------------------
        # 6. Reinforcements
        # -----------------------------
        self._maybe_reinforce(world, atk_hq, def_hq)

        # -----------------------------
        # 7. Check for collapse / retreat
        # -----------------------------
        self._check_retreat(world)

    def _maybe_reinforce(self, world, atk_hq, def_hq):
        """
        Simple reinforcement logic:
        - chance based on HQ pressure and officer aggression
        - pulls nearby units into battle
        """

        def reinforcement_chance(hq):
            if hq is None:
                return 0.0
            pressure = getattr(hq, "pressure", "GREEN")
            aggression = getattr(hq, "officer_aggression", 0.5)

            base = 0.05
            if pressure == "YELLOW":
                base = 0.15
            elif pressure == "RED":
                base = 0.35

            return base + 0.10 * aggression

        atk_chance = reinforcement_chance(atk_hq)
        def_chance = reinforcement_chance(def_hq)

        # Attackers reinforcement
        if random.random() < atk_chance:
            u = _find_reinforcement_unit(world, atk_hq, self.region)
            if u is not None:
                self.attackers.append(u)
                # small ORG boost on arrival
                u.org = min(u.max_org, u.org + 100_000)

        # Defenders reinforcement
        if random.random() < def_chance:
            u = _find_reinforcement_unit(world, def_hq, self.region)
            if u is not None:
                self.defenders.append(u)
                u.org = min(u.max_org, u.org + 120_000)

    def _check_retreat(self, world):
        """
        End battle when one side's average ORG collapses.
        """

        def avg_org(units):
            total = 0
            count = 0
            for u in units:
                if getattr(u, "org", None) is None:
                    continue
                total += u.org
                count += 1
            return total / count if count > 0 else 0

        atk_avg = avg_org(self.attackers)
        def_avg = avg_org(self.defenders)

        atk_threshold = 0.2 * (self.attackers[0].max_org if self.attackers else 1_000_000)
        def_threshold = 0.2 * (self.defenders[0].max_org if self.defenders else 1_000_000)

        # Bombing pressure makes collapse earlier
        bombing_pressure = getattr(world, "bombing_pressure", 0.0)
        atk_threshold *= (1.0 + bombing_pressure * 0.5)
        def_threshold *= (1.0 + bombing_pressure * 0.3)

        if atk_avg < atk_threshold or def_avg < def_threshold:
            # Mark retreating units
            side = "attackers" if atk_avg < atk_threshold else "defenders"
            for u in (self.attackers if side == "attackers" else self.defenders):
                setattr(u, "retreating", True)

            # Extra friction spike on collapse
            world.friction += 0.5 * self.intensity
            world.dispersion += 0.2 * self.intensity

            self.is_active = False


# -------------------------------------------------------------------
# Helper: find reinforcement unit
# -------------------------------------------------------------------

def _find_reinforcement_unit(world, hq, region):
    """
    Find a unit near the battle region that is not already in battle
    and has some ORG left.
    """
    if hq is None:
        return None

    candidates = []
    for u in world.units:
        if getattr(u, "org", None) is None:
            continue
        if getattr(u, "in_battle", False):
            continue
        if u.parent != hq:
            continue
        if u.region != region:
            continue
        if u.org < 0.3 * u.max_org:
            continue
        candidates.append(u)

    if not candidates:
        return None

    u = random.choice(candidates)
    u.in_battle = True
    return u


# -------------------------------------------------------------------
# Top-level: update_combat(world)
# -------------------------------------------------------------------

def update_combat(world):
    """
    Main combat loop called from NanoRunner.run_simulation().

    - Detect contact in regions
    - Create battles
    - Advance existing battles
    - Integrate with friction, supply, bombing pressure
    """

    # Initialize battle list on world if not present
    if not hasattr(world, "battles"):
        world.battles = []

    # 1. Advance existing battles
    for battle in list(world.battles):
        battle.tick(world)
        if not battle.is_active:
            world.battles.remove(battle)

    # 2. Detect new contacts and start battles
    # Simple rule: if multiple nations share a region, start a battle.
    region_map = {}
    for u in world.units:
        if u.region is None:
            continue
        key = u.region
        if key not in region_map:
            region_map[key] = []
        region_map[key].append(u)

    for region, units in region_map.items():
        nations = {}
        for u in units:
            nation = getattr(u, "nation", None) or getattr(u.parent, "nation", None)
            if nation is None:
                continue
            nations.setdefault(nation, []).append(u)

        if len(nations) < 2:
            continue

        # Pick two sides (e.g., first two nations)
        nation_list = list(nations.keys())
        attackers = nations[nation_list[0]]
        defenders = nations[nation_list[1]]

        # Avoid duplicating battles in same region
        already = False
        for b in world.battles:
            if b.region == region:
                already = True
                break
        if already:
            continue

        # Initialize ORG if missing
        for u in attackers + defenders:
            if getattr(u, "org", None) is None:
                u.org = 1_000_000
                u.max_org = 1_000_000
            u.in_battle = True

        battle = Battle(region, attackers, defenders)
        world.battles.append(battle)

        # Optional: log creation via world.messages
        world.send_message(
            src="COMBAT",
            to=f"REGION_{getattr(region, 'name', 'UNKNOWN')}",
            msg=f"Battle begins in {getattr(region, 'name', 'UNKNOWN')} with {len(attackers)} attackers and {len(defenders)} defenders.",
            kind="battle-start"
        )
