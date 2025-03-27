# Extended Euclidean Algorithm to find gcd and modular inverses
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

# Function to compute modular inverse using Extended Euclidean algorithm
def modinv(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('Inverse does not exist')
    else:
        return x % m

# Chinese Remainder Theorem (CRT) implementation
def chinese_remainder(n_list, a_list):
    total = 0  # Initialize result
    prod = 1   # Product of all moduli

    # Compute product of all moduli (N = n1 * n2 * n3 ...)
    for n in n_list:
        prod *= n

    # Combine each congruence into single solution modulo prod(N)
    for n_i, a_i in zip(n_list, a_list):
        p = prod // n_i               # Partial product N/n_i
        inv_p = modinv(p, n_i)        # Modular inverse of partial product modulo current modulus n_i
        total += a_i * inv_p * p      # Add contribution from current congruence to total

    return total % prod               # Final solution modulo N

# Given congruences explicitly:
# x ≡ 2 mod 5
# x ≡ 3 mod 11
# x ≡ 5 mod 17

n_list = [5, 11, 17]
a_list = [2, 3, 5]

# Compute the solution using CRT and print it clearly:
result = chinese_remainder(n_list, a_list)

print(f"The integer satisfying all congruences modulo {5*11*17} is: {result}")
