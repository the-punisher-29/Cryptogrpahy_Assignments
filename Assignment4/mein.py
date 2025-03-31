import numpy as np
import sympy
from math import sqrt

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83]
ct = 1350995397927355657956786955603012410260017344805998076702828160316695004588429433

# Use dtype=object to handle large integers
M = np.zeros((len(PRIMES) + 1, len(PRIMES) + 2), dtype=object)

M[0, 0], M[0, 1] = ct, 1
for i in range(len(PRIMES)):
    M[i+1, 0] = round(2**256 * sqrt(PRIMES[i]))
    M[i+1, i+2] = 1

# Convert to sympy Matrix for LLL reduction
M_sympy = sympy.Matrix(M)
lll_reduced = M_sympy.lll()

# Ensure values are within the valid range for chr()
decoded_chars = []
for c in lll_reduced[0, 2:]:
    char_code = -c  # Negate as in the original logic
    if 0 <= char_code < 0x110000:
        decoded_chars.append(chr(char_code))
    else:
        decoded_chars.append("?")  # Replace invalid characters with '?'

decoded_message = "".join(decoded_chars)

print(decoded_message)
