#!/usr/bin/env python3
# filepath: /home/soumen/Dev/Cryptogrpahy_Assignments/Assignment4/solve.py
from decimal import Decimal, getcontext
import math

# Use high precision: note that 16^64 is huge so we need plenty of digits.
getcontext().prec = 200

# Data from the challenge
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103]

# The secret FLAG is of the form "crypto{???????????????}"
# Based on the code, FLAG is 23 characters long:
# prefix = "crypto{" (positions 0..6)
# unknown positions: indices 7 .. 21 (15 characters)
# suffix = "}" at position 22
FLAG_prefix = "crypto{"
FLAG_suffix = "}"

# Given ciphertext from the script:
ciphertext = 1350995397927355657956786955603012410260017344805998076702828160316695004588429433

# Recover approximate h: we know ciphertext = floor(h * 16^64)
h_approx = Decimal(ciphertext) / (Decimal(16) ** 64)

# Compute the contribution of the known letters.
known_sum = Decimal(0)
# indices 0 to 6 from prefix:
for i, ch in enumerate(FLAG_prefix):
    known_sum += Decimal(ord(ch)) * Decimal(PRIMES[i]).sqrt()
# position 22 (last char) from suffix:
known_sum += Decimal(ord(FLAG_suffix)) * Decimal(PRIMES[22]).sqrt()

# Target for unknown positions (indices 7 .. 21)
target_unknown = h_approx - known_sum

# The unknown positions are indices 7 to 21 (15 letters)
unknown_indices = list(range(7, 22))
# Precompute Decimal sqrt values for these indices.
sqrt_vals = {}
for i in unknown_indices:
    sqrt_vals[i] = Decimal(PRIMES[i]).sqrt()

min_ascii = 32  # space (adjust if you know more about the charset)
max_ascii = 126 # tilde
# Tolerance: note that 1/16^64 ~ 1e-77, so a tolerance of 1e-80 is safe.
tol = Decimal("1e-80")

results = []

def dfs(pos, current_sum, current_chars):
    # pos indexes into unknown_indices.
    if pos == len(unknown_indices):
        if abs(current_sum - target_unknown) < tol:
            results.append("".join(current_chars))
        return
    # For pruning: compute minimal and maximal remaining contribution.
    rem_indices = unknown_indices[pos:]
    min_remaining = sum(Decimal(min_ascii) * sqrt_vals[j] for j in rem_indices)
    max_remaining = sum(Decimal(max_ascii) * sqrt_vals[j] for j in rem_indices)
    # Prune if even using minimal or maximal values we cannot reach target.
    if current_sum + min_remaining - target_unknown > tol:
        return
    if target_unknown - (current_sum + max_remaining) > tol:
        return
    # Try possible ascii codes.
    for a in range(min_ascii, max_ascii + 1):
        dfs(pos + 1, current_sum + Decimal(a) * sqrt_vals[unknown_indices[pos]], current_chars + [chr(a)])

# Run DFS
dfs(0, Decimal(0), [])

if results:
    flag = FLAG_prefix + results[0] + FLAG_suffix
    print("FLAG:", flag)
else:
    print("FLAG not found")