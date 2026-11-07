import math

"""25-bit XOR LFSR inspired by Analog Device's MAX7651/52 XOR LFSR"""
def flawed_bits(n_bits=1_000_000, seed=1):

    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")
    if not 0 < seed < (1 << 25):
        raise ValueErorr("Seed must be a nonzero 25-bit integer")

    state = seed
    mask = (1 << 25) - 1
    bits = []

    #Fibonacci XOR LFSR
    for _ in range(n_bits):
        bits.append(str((state >> 24) & 1))
        feedback = ((state >> 7) ^ (state >> 24)) & 1
        state = ((state << 1) & mask) | feedback

    return "".join(bits)

bits = flawed_bits()