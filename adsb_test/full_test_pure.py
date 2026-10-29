from nano_test_pure import run_nano_test_pure

def run_full_test_pure(
    iq_samples,
    sample_rate,
    center_freq,
    band_min,
    band_max,
    frames_to_scan=20
):
    """
    FULL FRAME LOOP:
    - Loop through frames
    - Run nano test on each frame
    - Print results immediately
    - Return nothing (or return list if needed)
    """

    results = []

    for i in range(frames_to_scan):
        nano = run_nano_test_pure(
            iq_samples=iq_samples,
            sample_rate=sample_rate,
            center_freq=center_freq,
            band_min=band_min,
            band_max=band_max,
            num_random_frames=1
        )

        print(f"Frame {i+1}:")
        print(f"  snr_mean: {nano['snr_mean']}")
        print(f"  drift_series: {nano['drift_series']}")
        print(f"  frames: {nano['frames']}")
        print("")

        results.append(nano)

    return results
