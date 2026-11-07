import math

"""Simulate two-state Markov chain RNG"""
def flawed_bits(n_bits=1_000_000, seed=0):

    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")

    state = 0
    choice_state = seed & 0xFFFFFFFF

    for _ in range(n_bits):
        #Pseudorandom driver that determines Markov state transitions
        choice_state = (
            1664525 * choice_state + 1013904223
        ) & 0xFFFFFFFF

        if state == 0:
            if choice_state < (1 << 30):
                state = 1
        else:
            if choice_state < (1 << 31):
                state = 0

        yield state


bit = list(flawed_bits())
