# nano_unit_organ.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Unit:
    name: str
    actor: str
    type: str
    strength: float
    org: float
    supply: float
    meta: Dict[str, Any]

class NanoUnitOrgan:
    def unit_decision(self, unit: Unit) -> str:
        if unit.supply < 0.3:
            return "Secure_Supply_Lines"
        if unit.org < 0.4:
            return "Delay_Action"
        if unit.type == "Armor":
            return "Probe_Enemy"
        if unit.type == "Air":
            return "Shift_Air_Sorties"
        if unit.strength > 0.7 and unit.org > 0.7:
            return "Commit_Main_Effort"
        return "Reinforce_Front"

    def unit_pressure(self, unit: Unit) -> float:
        if unit.type == "Armor":
            base = 1.3
        elif unit.type == "Air":
            base = 1.1
        else:
            base = 1.0

        base *= (0.8 + unit.strength * 0.4)
        base *= (0.8 + unit.org * 0.4)

        if unit.supply < 0.3:
            base *= 0.7

        return base

    def emit(self, unit: Unit):
        return {
            "actor": unit.actor,
            "verb": self.unit_decision(unit),
            "pressure": self.unit_pressure(unit)
        }
