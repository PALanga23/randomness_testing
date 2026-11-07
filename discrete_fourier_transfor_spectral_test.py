import math
import numpy as numpy


def flawed_bits(n=16_384, seed=42):
    if n < 1024 or n % 64:
        raise ValueError("n must be a multiple of 64 and at least 1024")

    state = seed & 0xFFFFFFFF
    block = []

    #Create block using LCG
    for _ in range(64):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        block.append((state >> 31) & 1)

    return block * (n // 64)

bits = flawed_bits()
