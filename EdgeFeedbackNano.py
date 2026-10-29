# EdgeFeedbackNano.py
# Converts downstream effects into edge feedback score.

def edge_feedback(effects):
    """
    Converts downstream effects into a single feedback score
    that can be fed back into edges.
    """

    score = 0.0

    # Distance: closer = stronger edges
    score += (100 - effects["avg_distance"]) * 0.1

    # Pressure: more GREEN = stronger edges
    score += effects["avg_pressure_green"] * 2.0

    # Air pressure: more GREEN = stronger edges
    score += effects["air_pressure_green"] * 3.0

    # Movement energy: more movement = stronger edges
    score += effects["movement_energy"] * 5.0

    # Hinges
    hinge_counts = effects["hinge_counts"]

    # Offensive hinge strengthens edges
    if "Commit_Main_Effort" in hinge_counts:
        score += hinge_counts["Commit_Main_Effort"] * 4.0

    # Defensive hinge weakens edges
    if "Delay_Action" in hinge_counts:
        score -= hinge_counts["Delay_Action"] * 3.0

    return score
