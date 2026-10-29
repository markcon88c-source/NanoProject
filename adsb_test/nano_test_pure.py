import math
import random
from fft_utils import fft_iter

def hann_window(N):
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * n / (N - 1)) for n in range(N)]

def adaptive_threshold(values, sigma_factor=4.0):
    if not values:
        return 0.0
    mean_val = sum(values) / len(values)
    var = sum((v - mean_val)**2 for v in values) / len(values)
    std_val = math.sqrt(var)
    return mean_val + sigma_factor * std_val

def run_nano_test_pure(
    iq_samples,
    sample_rate,
    center_freq,
    band_min,
    band_max,
    fft_size=2048,
    num_random_frames=20,
):
    window = hann_window(fft_size)

    drift_series = []
    snr_series = []
    accumulated_spectrum = None

    bin_width = sample_rate / fft_size
    center_bin = fft_size // 2

    last_peak_bin = None

    if len(iq_samples) < fft_size:
        return {
            "band_min": band_min,
            "band_max": band_max,
            "snr_mean": 0.0,
            "drift_series": [],
            "avg_spectrum": [],
            "frames": 0,
        }

    for _ in range(num_random_frames):
        pos = random.randint(0, len(iq_samples) - fft_size)
        frame = iq_samples[pos:pos+fft_size]

        frame_win = [frame[i] * window[i] for i in range(fft_size)]

        spectrum = fft_iter(frame_win)
        mag = [abs(v) for v in spectrum]

        freqs = [
            center_freq + (i - center_bin) * bin_width
            for i in range(fft_size)
        ]

        band_bins = [
            i for i, f in enumerate(freqs)
            if band_min <= f <= band_max
        ]

        if not band_bins:
            continue

        band_mag = [mag[i] for i in band_bins]

        if accumulated_spectrum is None:
            accumulated_spectrum = band_mag[:]
        else:
            accumulated_spectrum = [
                accumulated_spectrum[i] + band_mag[i]
                for i in range(len(band_mag))
            ]

        peak_idx = max(range(len(band_mag)), key=lambda i: band_mag[i])
        peak_val = band_mag[peak_idx]

        mean_val = sum(band_mag) / len(band_mag)
        var = sum((v - mean_val)**2 for v in band_mag) / len(band_mag)
        std_val = math.sqrt(var)
        snr = (peak_val - mean_val) / (std_val + 1e-9)
        snr_series.append(snr)

        drift = 0 if last_peak_bin is None else peak_idx - last_peak_bin
        drift_series.append(drift)
        last_peak_bin = peak_idx

    if accumulated_spectrum:
        avg_spectrum = [
            v / len(drift_series) for v in accumulated_spectrum
        ]
    else:
        avg_spectrum = []

    return {
        "band_min": band_min,
        "band_max": band_max,
        "snr_mean": sum(snr_series)/len(snr_series) if snr_series else 0.0,
        "drift_series": drift_series,
        "avg_spectrum": avg_spectrum,
        "frames": len(drift_series),
    }
