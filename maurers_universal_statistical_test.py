

def flawed_bits(n_bits=1_000_000, seed=1):

    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")

    state = seed & 0xFFFFFFFF
    bits = []

    for _ in range(n_bits):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        bits.append(str(state & 1))

        return "".join(bits)

bits = flawed_bits(100_000)