import math

"""RNG based on NIST's MODEXPG"""
P = int(
    "987b6a6bf2c56a97291c445409920032499f9ee7ad128301b5d0254aa1a9633fdbd378"
    "d40149f1e23a13849f3d45992f5c4c6b7104099bc301f6005f9d8115e1", 16
)
G = int(
    "3844506a9456c564b8b8538e0cc15aff46c95e69600f084f0657c2401b3c244734b62ea"
    "9bb95be4923b9b7e84eeaf1a224894ef0328d44bc3eb3e983644da3f5", 16
)
SEED = int("7AB36982CE1ADF832019CDFEB2393CABDF0214EC", 16)

def flawed_bits(n_bits=1_000_000, seed=SEED):

    if n_bits < 0:
        raise ValueError("Number of bits must be non-negative")
    if not 0 < seed < (1 << 160):
        raise ValueError("Seed must be a nonzero 160-bit integer")

    exponent = seed 
    chunks = []

    for _ in range((n_bits + 511) // 512):
        x = pow(G, exponent, P)
        chunks.append(format(x, "0512b"))
        exponent = x & 1

    return "".join(chunks)[:n_bits]


bits = flawed_bits()   