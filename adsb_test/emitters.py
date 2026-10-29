# emitters.py
import math

class CelestialEmitter:
    def __init__(self, name, rest_freq_hz, drift_hz_s):
        self.name = name
        self.rest = rest_freq_hz
        self.drift = drift_hz_s

    def expected_freq(self, t):
        # simple linear Doppler model
        return self.rest + self.drift * t

    def expected_waveform(self, sample_rate, duration_s, t):
        f = self.expected_freq(t)
        n = int(sample_rate * duration_s)
        return [math.sin(2 * math.pi * f * (i / sample_rate)) for i in range(n)]

EMITTERS = [
    CelestialEmitter("Pulsar_J0437_demo", 142.000e6, -0.3),   # demo drift
    CelestialEmitter("Solar_radio_line", 141.900e6, 0.0),
    CelestialEmitter("GRAVES_nominal", 143.050e6, 0.0),
]
