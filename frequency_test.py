import math

"""Simulate two-state Markov chain RNG"""
def flawed_bits(n, seed=0):
    state = 0
    choice_state = seed & 0xFFFFFFFF

    for _ in range(n):
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


bit = list(markov_bits(100_000))
