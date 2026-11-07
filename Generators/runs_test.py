import math

"""Simulate 32-bit XORshift"""
def flawed_bits(n_bits=1_000_000, seed=42):

    if n_bits < 100 or n_bits % 2:
        raise ValueError("Number of bits must be an even integer greater than 100")

    state = seed & 0xFFFFFFFF
    if state == 0:
        raise ValueError("Seed must be nonzero after masking to 32 bits")

    bits = []

    for _ in range(n_bits // 2):

        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF

        first = state & 1

        bits.extend([str(first), str(1 - first)])

    return "".join(bits)


bits = flawed_bits()