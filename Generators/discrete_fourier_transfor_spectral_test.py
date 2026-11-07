import math

def flawed_bits(n=1_000_000, seed=42):
    if n < 1024 or n % 64:
        raise ValueError("n must be a multiple of 64 and at least 1024")

    state = seed & 0xFFFFFFFF
    block = []

    #Create block using LCG
    for _ in range(64):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        block.append((state >> 31) & 1)

    bits = ''.join(map(str, block * (n // 64)))

    return bits[:n]


bits = flawed_bits()
