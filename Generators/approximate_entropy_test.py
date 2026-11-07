import hashlib
import math

"""RNG based on two-state Markov bit generator"""
def flawed_bits(n_bits=1_000_000, seed=b"markov-demo-1"):
    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")
    if not isinstance(seed, bytes):
        raise TypeError("Seed must be in byte")

    choices = hashlib.shake_256(seed).digest(n_bits + 1)
    state = choices[0] & 1
    bits = []

    for choice in choices[1:]:
        bits.append(str(state))
        if choice < 16:
            state ^= 1

    return "".join(bits)


bits = flawed_bits()

with open("bitstream_01.txt", "w", encoding="utf-8") as file:
    file.write(bits)