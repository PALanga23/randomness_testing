
"""32-bit XORshift PRNG"""
def flawed_bits(n_bits=1_000_000, seed=1):

    if n_bits < 0 or n_bits % 2:
        raise ValueError("Number of bits must be a nonnegative even integer")
    if not 0 < seed < (1 << 32):
        raise ValueError("Seed must be a nonzero 32-bit integer")

    state = seed
    pairs = []

    for _ in range(n_bits // 2):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        pairs.append("10" if state & 1 else "01")

    return "".join(pairs)


bits = flawed_bits()