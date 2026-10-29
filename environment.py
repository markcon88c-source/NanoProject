# environment.py
# Supply, leadership, terrain, and crash dynamics for the NanoRunner ecosystem.

import math
import random

def update_supply(world):
    """
    Supply behaves as a pulse organ:
      - Oscillates rhythmically
      - Amplitude increases with edge feedback
      - Decays under stress
      - Never stays flat
    """

    # Normalized stress
    E = max(0.0, min(1.0, world.edge_feedback / 50.0))

    # Pulse parameters
    omega = 0.35                     # frequency
    amplitude = 0.05 + 0.20 * E      # pulse grows with stress
    decay = 0.01 + 0.05 * E          # stress drains supply

    # Pulse update
    pulse = amplitude * math.sin(world.time * omega)

    world.supply_level += pulse
    world.supply_level -= decay

    # Clamp
    world.supply_level = max(0.2, min(1.0, world.supply_level))


def update_leadership(world):
    """
    Leadership decays under high edge feedback and recovers slowly otherwise.
    """
    E = max(0.0, min(1.0, world.edge_feedback / 50.0))

    world.leadership_level += 0.01      # slow natural recovery
    world.leadership_level -= 0.03 * E  # stress decay

    world.leadership_level = max(0.5, min(1.0, world.leadership_level))


def update_terrain(world):
    """
    Terrain effectiveness drifts randomly but decays under high edge feedback.
    """
    E = max(0.0, min(1.0, world.edge_feedback / 50.0))

    drift = random.uniform(-0.01, 0.01)
    world.terrain_level += drift
    world.terrain_level -= 0.02 * E

    world.terrain_level = max(0.6, min(1.0, world.terrain_level))


def maybe_crash(world):
    """
    Command crashes occur when friction is extremely high.
    Crash effects:
      - Leadership collapses
      - Edge feedback spikes
      - HQs scatter randomly for several ticks
    """
    # Trigger crash
    if world.friction > 0.85 and random.random() < 0.10:
        print("\n[CRASH] Command breakdown triggered!")
        world.leadership_level *= 0.4
        world.edge_feedback *= 1.5
        world.crash_ticks = 3

    # Crash effects persist for several ticks
    if world.crash_ticks > 0:
        world.crash_ticks -= 1
        for hq in world.hqs:
            x, y = hq.pos
            hq.pos = (
                x + random.uniform(-0.1, 0.1),
                y + random.uniform(-0.1, 0.1)
            )
