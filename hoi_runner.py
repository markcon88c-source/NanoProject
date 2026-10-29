# hoi_runner.py
from nano_unit_organ import NanoUnitOrgan, Unit
from nano_unite_organ import NanoUniteOrgan, DecisionChain, DecisionToken


class NanoRunner:
    def __init__(self):
        self.unit_organ = NanoUnitOrgan()
        self.unite = NanoUniteOrgan()

    def build_chain(self, actor: str, units: list) -> DecisionChain:
        tokens = []
        log_probs = []

        for u in units:
            if u.actor != actor:
                continue

            tok = self.unit_organ.emit(u)
            pressure = tok["pressure"]

            tokens.append(
                DecisionToken(
                    actor=tok["actor"],
                    verb=tok["verb"],
                    pressure=pressure
                )
            )

            log_probs.append(-0.2 + pressure * 0.1)

        return DecisionChain(actor=actor, tokens=tokens, log_probs=log_probs)

    def hq_output(self, tension):
        # Pick actor based on tension sign
        if tension > 0:
            actor = "German HQ"
            decision = "launches an attack"
        elif tension < 0:
            actor = "British HQ"
            decision = "fortifies the line"
        else:
            actor = "Both HQs"
            decision = "hold position"

        # Kraków base coordinates
        base_lat = 50.064
        base_lon = 19.945

        # tension influences offset
        lat = base_lat + (tension * 0.12)
        lon = base_lon + (tension * 0.18)

        # distance estimate
        distance = abs(tension) * 12 + 5

        return (
            f"{actor} {decision} near GPS "
            f"{lat:.3f}°N, {lon:.3f}°E, "
            f"approximately {distance:.1f} miles from Kraków."
        )

    def run(self, units: list):
        ger_chain = self.build_chain("GER", units)
        uk_chain  = self.build_chain("UK", units)

        tension = self.unite.unified_tension(ger_chain, uk_chain)

        return {
            "german_chain": ger_chain,
            "british_chain": uk_chain,
            "tension": tension
        }


if __name__ == "__main__":
    units = [
        Unit("GER_1st_Panzer", "GER", "Armor", 0.9, 0.8, 0.7, {}),
        Unit("GER_3rd_Infantry", "GER", "Infantry", 0.6, 0.5, 0.9, {}),
        Unit("UK_5th_Infantry", "UK", "Infantry", 0.7, 0.6, 0.8, {}),
        Unit("UK_RAF_Squadron", "UK", "Air", 0.8, 0.9, 0.7, {}),
    ]

    runner = NanoRunner()
    state = runner.run(units)

    print(runner.hq_output(state["tension"]))
