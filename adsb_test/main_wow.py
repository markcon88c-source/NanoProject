import wave
import struct
from nano_test_pure import run_nano_test_pure

def load_wav_iq(filename):
    w = wave.open(filename, 'rb')
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

    samples = struct.unpack('<' + 'h' * (n_frames * 2), raw)
    I = samples[0::2]
    Q = samples[1::2]

    iq = [complex(I[i] / 32768.0, Q[i] / 32768.0) for i in range(n_frames)]
    return iq, w.getframerate()

def main():
    print("Running WOW infinite frame-by-frame test...")

    iq, sample_rate = load_wav_iq("radar.wav")

    band_min = 523790   # 523.79 kHz offset
    band_max = 543790   # 543.79 kHz offset

    print(f"Band: {band_min/1000:.2f} → {band_max/1000:.2f} kHz offset")

    frame_index = 1

    while True:
        result = run_nano_test_pure(
            iq_samples=iq,
            sample_rate=sample_rate,
            center_freq=0,
            band_min=band_min,
            band_max=band_max,
            num_random_frames=1
        )

        print(f"\nFrame {frame_index}:")
        print(f"  snr: {result['snr_mean']}")
        print(f"  drift: {result['drift_series']}")
        print(f"  frames: {result['frames']}")

        frame_index += 1

if __name__ == "__main__":
    main()
