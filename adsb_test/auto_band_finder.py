import wave
import struct
import math
from fft_utils import fft_iter

def load_wav_iq(filename):
    w = wave.open(filename, 'rb')
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

    samples = struct.unpack('<' + 'h' * (n_frames * 2), raw)
    I = samples[0::2]
    Q = samples[1::2]

    iq = [complex(I[i] / 32768.0, Q[i] / 32768.0) for i in range(n_frames)]
    return iq, w.getframerate()

def find_energy_clusters(iq, sample_rate, fft_size=4096, clusters=5):
    frame = iq[:fft_size]
    spectrum = fft_iter(frame)
    mag = [abs(v) for v in spectrum]

    # Sort bins by magnitude
    sorted_bins = sorted(range(len(mag)), key=lambda i: mag[i], reverse=True)

    center_bin = fft_size // 2
    bin_width = sample_rate / fft_size

    results = []

    for b in sorted_bins[:clusters]:
        offset_bins = b - center_bin
        freq_offset_hz = offset_bins * bin_width

        results.append({
            "bin": b,
            "magnitude": mag[b],
            "offset_bins": offset_bins,
            "offset_hz": freq_offset_hz
        })

    return results

def main():
    iq, sample_rate = load_wav_iq("radar.wav")

    print(f"Sample rate: {sample_rate} Hz")
    print("Scanning for strongest energy clusters...\n")

    clusters = find_energy_clusters(iq, sample_rate)

    print("Top energy clusters:")
    for c in clusters:
        print(f"Bin {c['bin']:4d} | Mag {c['magnitude']:.4f} | "
              f"Offset {c['offset_hz']/1000:.2f} kHz")

    print("\nSuggested scan bands:")
    for c in clusters:
        # ±10 kHz around each cluster
        low = c["offset_hz"] - 10000
        high = c["offset_hz"] + 10000
        print(f"Band: {low/1000:.2f} kHz to {high/1000:.2f} kHz offset from center")

if __name__ == "__main__":
    main()
