
"""Flawed RNG mimicking IBM's RANDU generator"""
def flawed_bits(n_bits=1_000_000):
    state = 1
    chunks = []

    for _ in range((n_bits + 7) // 8):
        state = (65539 * state) & 0x7FFFFFFF
        chunks.append(format(state & 0xFF, "08b"))

    return "".join(chunks)[:n_bits]

bits = flawed_bits()