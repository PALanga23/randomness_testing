import math

"""Simulate 32-bit XORshift"""
def flawed_bits(n, seed=42):

    bits = []

    for _ in range(n // 2):

        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF

        first = state & 1

        bits.extend([first, 1 - first])


bits = flawed_bits(10_000)
