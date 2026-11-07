

def flawed_bits(n, seed=1):
    state = seed & 0xFFFFFFFF
    bits = []

    for _ in range(n):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        bits.append(str(state & 1))

        return "".join(bits)

bits = flawed_bits(100_000)