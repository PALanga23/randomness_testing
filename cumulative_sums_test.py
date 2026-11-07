import math


#Mirsenne primes
P = (1 << 521) - 1
Q = (1 << 607) - 1
MODULUS = P * Q
E = 13
N = MODULUS.bit_length()
K = N * (E - 2) // E 
R = N - K
SEED = (1 << (R - 1)) | 0x123456789ABCDEF0123456789ABCDEF


"""Micali-Schnoor-inspired but flawed RNG generator"""
def flawed_bits(n_bits=1_000_000, seed=SEED):

    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")
    if not  < seed < (1 << R):
        raise ValueError(f"Seed must be a nonzero {R}-bit integer")
    if math.gcd(E, (P-1) * (Q-1)) != 1 or 80 * E >= N:
        raise ValueError("Invalid demonstration parameters")

    state = seed
    chunks = []

    for _ in range((n_bits + K - 1) // K):
        y = pow(state, E, MODULUS)
        state = y >> K
        output = state
        chunks.append(format(output, f"0{K}b"))

    return "".join(chunks)[:n_bits]



bits = flawed_bits()


