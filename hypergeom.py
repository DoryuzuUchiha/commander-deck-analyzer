from math import comb

def at_least(k_min, N, K, n):
    total = 0
    for k in range(k_min, min(K, n) + 1):
        total += comb(K, k) * comb(N - K, n - k)
    return total / comb(N, n)

def at_least_one(N, K, n):
    return 1 - comb(N - K, n) / comb(N, n)
