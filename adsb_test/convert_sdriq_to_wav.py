import wave
import struct
import os

# Input raw IQ file
infile = "radar.2021-01-30T19_30_43_722.sdriq"

# Output WAV file
outfile = "radar.wav"

# SDRangel sample rate (most examples use 2.4 MHz)
SAMPLE_RATE = 2400000

# Read raw IQ
size = os.path.getsize(infile)
print(f"[+] Raw IQ size: {size} bytes")

with open(infile, "rb") as f:
    raw = f.read()

# Convert raw bytes → 16-bit signed integers
samples = struct.unpack("<" + "h" * (len(raw)//2), raw)

# WAV expects stereo: left = I, right = Q
I = samples[0::2]
Q = samples[1::2]

print(f"[+] Samples loaded: {len(I)} IQ pairs")

# Write WAV
w = wave.open(outfile, "wb")
w.setnchannels(2)          # I/Q stereo
w.setsampwidth(2)          # 16-bit
w.setframerate(SAMPLE_RATE)

# Interleave I and Q for WAV
interleaved = []
for i, q in zip(I, Q):
    interleaved.append(i)
    interleaved.append(q)

# Pack into bytes
wav_bytes = struct.pack("<" + "h" * len(interleaved), *interleaved)

w.writeframes(wav_bytes)
w.close()

print(f"[+] Wrote WAV: {outfile}")
