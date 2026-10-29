# celestial_models.py
import math

class CelestialEmitter:
    def __init__(self, name, kind, rest_freq_hz):
        self.name = name
        self.kind = kind      # "pulsar", "sun", "planet", "satellite"
        self.rest = rest_freq_hz

    def expected_freq(self, t, ra=None, dec=None, tle=None):
        # t = time (seconds or frame index proxy)
        # ra/dec for pulsars/planets, tle for satellites
        # TODO: replace with real Doppler model
        return self.rest

    def describe(self):
        return f"{self.name} ({self.kind}) rest={self.rest/1e6:.6f} MHz"


EMITTERS = [
    CelestialEmitter("Solar_radio_line_141.9", "sun", 141.900e6),
    CelestialEmitter("Pulsar_J0437_demo", "pulsar", 142.000e6),
    CelestialEmitter("GRAVES_nominal", "radar", 143.050e6),
]
