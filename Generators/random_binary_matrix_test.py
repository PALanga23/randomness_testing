import math

"""Simulate a linear congruential generator"""
def flawed_bits(n_matrices=100, seed=42):

    state = seed & 0xFFFFFFFF
    bits = []

    for _ in range(n_matrices):
        rows = []
        
        for _ in range(16):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            row.append(state)

            for i in range(16):
                rows.append(rows[i] ^ rows[(i + 1) % 16])

                for row in rows:
                    for shift in range(31, -1, 0):
                        bits.append((row >> shift) & 1)


    return bits

bits = flawed_bits()