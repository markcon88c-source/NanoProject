import cmath
import math

def fft_iter(x):
    N = len(x)
    if N <= 1:
        return x

    even = fft_iter(x[0::2])
    odd  = fft_iter(x[1::2])

    out = [0] * N
    for k in range(N // 2):
        t = cmath.exp(-2j * math.pi * k / N) * odd[k]
        out[k] = even[k] + t
        out[k + N//2] = even[k] - t

    return out
