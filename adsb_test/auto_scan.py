import wave
import struct
from fft_utils import fft_iter
from nano_test_pure import run_nano_test_pure

# ---------------------------------------------------------
# Load stereo IQ WAV (Drake format)
# ---------------------------------------------------------
def load_wav_iq(filename):
    w = wave.open(filename, 'rb')
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

    samples = struct.unpack('<' + 'h' * (n_frames * 2), raw)
    I = samples[0::2]
    Q = samples[1::2]

    iq = [complex(I[i] / 32768.0, Q[i] / 32768.0) for i in range(n_frames)]
    return iq, w.getframerate()

# ---------------------------------------------------------
# Find strongest FFT bins
# ---------------------------------------------------------
def find_clusters(iq, sample_rate, fft_size=4096, top_n=5):
    frame = iq[:fft_size]
    spectrum = fft_iter(frame)
    mag = [abs(v) for v in spectrum]

    sorted_bins = sorted(range(len(mag)), key=lambda i: mag[i], reverse=True)
    center_bin = fft_size // 2
    bin_width = sample_rate / fft_size

    clusters = []
    for b in sorted_bins[:top_n]:
        offset_bins = b - center_bin
        offset_hz = offset_bins * bin_width
        clusters.append((b, mag[b], offset_hz))

    return clusters

# ---------------------------------------------------------
# Auto-scan each cluster band with nano test
# ---------------------------------------------------------
def auto_scan(iq, sample_rate, clusters):
    print("\n=== AUTO SCAN RESULTS ===\n")

    for (bin_idx, mag, offset_hz) in clusters:
        band_min = offset_hz - 10000   # ±10 kHz around cluster
        band_max = offset_hz + 10000

        print(f"Cluster bin {bin_idx} | offset {offset_hz/1000:.2f} kHz")
        print(f"Scanning band {band_min/1000:.2f} kHz → {band_max/1000:.2f} kHz")

        nano = run_nano_test_pure(
            iq_samples=iq,
            sample_rate=sample_rate,
            center_freq=0,          # we scan offsets, not RF
            band_min=band_min,
            band_max=band_max,
            num_random_frames=5
        )

        print("  snr_mean:", nano["snr_mean"])
        print("  frames:", nano["frames"])
        print("  drift:", nano["drift_series"])
        print("")

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    iq, sample_rate = load_wav_iq("radar.wav")

    print(f"Loaded radar.wav | sample rate {sample_rate} Hz")

    clusters = find_clusters(iq, sample_rate)
    print("\nTop clusters:")
    for b, m, off in clusters:
        print(f"  bin {b} | mag {m:.4f} | offset {off/1000:.2f} kHz")

    auto_scan(iq, sample_rate, clusters)

if __name__ == "__main__":
    main()
