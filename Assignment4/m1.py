def legendre_symbol(x, p):
    """ Compute the Legendre symbol (x/p) using Euler's criterion. """
    return pow(x, (p - 1) // 2, p)

def find_square_root(x, p):
    """ Brute-force search for square roots of x mod p. """
    for a in range(1, p):  # Avoid a=0 since it's trivial
        if (a * a) % p == x:
            return a  # Return the smaller root

p = 29
ints = [14, 6, 11]

# Find the quadratic residue
for x in ints:
    if legendre_symbol(x, p) == 1:
        print(f"Quadratic residue found: {x}")
        root = find_square_root(x, p)
        print(f"Smallest square root: {root}")
        break  # Only one quadratic residue needed
